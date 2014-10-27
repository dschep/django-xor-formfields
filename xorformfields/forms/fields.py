try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
import posixpath
import os

from django.core.exceptions import ValidationError
from django.forms.fields import MultiValueField, FileField, URLField
from django.forms.util import ErrorList
from django.core.validators import EMPTY_VALUES
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

import requests

from .widgets import FileOrURLWidget


__all__ = ['MutuallyExclusiveValueField', 'FileOrURLField']


class MutuallyExclusiveValueField(MultiValueField):
    too_many_values_error = 'Exactly One field is required, no more'
    empty_values = EMPTY_VALUES

    def clean(self, value):
        """
        Validates every value in the given list. A value is validated against
        the corresponding Field in self.fields.

        Only allows for exactly 1 valid value to be submitted, this is what
        gets returned by compress.

        example to use directy (instead of using FileOrURLField):
            MutuallyExclusiveValueField(
                fields=(forms.IntegerField(), forms.IntegerField()),
                widget=MutuallyExclusiveRadioWidget(widgets=[
                        forms.Select(choices=[(1,1), (2,2)]),
                        forms.TextInput(attrs={'placeholder':
                                               'Enter a number'}),
                    ]))
        """
        clean_data = []
        errors = ErrorList()
        if not value or isinstance(value, (list, tuple)):
            if not value or not [
                    v for v in value if v not in self.empty_values]:
                if self.required:
                    raise ValidationError(
                        self.error_messages['required'], code='required')
                else:
                    return self.compress([])
        else:
            raise ValidationError(
                self.error_messages['invalid'], code='invalid')
        for i, field in enumerate(self.fields):
            try:
                field_value = value[i]
            except IndexError:
                field_value = None
            try:
                clean_data.append(field.clean(field_value))
            except ValidationError as e:
                # Collect all validation errors in a single list, which we'll
                # raise at the end of clean(), rather than raising a single
                # exception for the first error we encounter.
                errors.extend(e.messages)
        if errors:
            raise ValidationError(errors)

        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out

    def compress(self, data_list):
        """
        Returns a single value for the given list of values. The values can be
        assumed to be valid.

        For example, if this MultiValueField was instantiated with
        fields=(DateField(), TimeField()), this might return a datetime
        object created by combining the date and time in data_list.
        """

        non_empty_list = [d for d in data_list if d not in self.empty_values]

        if len(non_empty_list) == 0 and not self.required:
            return None
        elif len(non_empty_list) > 1:
            raise ValidationError(self.too_many_values_error)

        return non_empty_list[0]


class FileOrURLField(MutuallyExclusiveValueField):
    widget = FileOrURLWidget
    url_fetch_error = 'Failed to fetch URL specified'

    def __init__(self, to=None, *args, **kwargs):
        """
        Accepts EITHER a file or an URL.
        The `to` parameter accepts 3 values:
            None: default to_python, returns either url or file
            'file': if an url is submited, download it into an inmemory object
            'url': uploads the file to default storage and returns the URL
        The`upload_to` param must be set when to='url'
        if using AWS, set no_aws_qs to disable querystring auth
        """
        self.to = to
        self.no_aws_qs = kwargs.pop('no_aws_qs', False)
        if 'upload_to' in kwargs:
            self.upload_to = kwargs.pop('upload_to')
        elif self.to == 'url':
            raise RuntimeError('If normalizing to an URL `upload_to` '
                               'must be set')
        fields = (FileField(), URLField())
        super(FileOrURLField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        """ override just cause we want a to_python """
        value = super(FileOrURLField, self).compress(data_list)
        return self.to_python(value)

    def to_python(self, value):
        value = super(FileOrURLField, self).to_python(value)

        if self.to == None:
            return value
        elif self.to == 'file' and not isinstance(value, UploadedFile):
            try:
                resp = requests.get(value)
            except:
                raise ValidationError(self.url_fetch_error)
            if not (200 <= resp.status_code < 400):
                raise ValidationError(self.url_fetch_error)
            io = StringIO(unicode(resp.content))
            io.seek(0)
            io.seek(os.SEEK_END)
            size = io.tell()
            io.seek(0)
            return InMemoryUploadedFile(
                io, None,
                posixpath.basename(value),
                resp.headers['content-type'],
                size, None)
        elif self.to == 'url' and isinstance(value, UploadedFile):
            path = default_storage.save(
                posixpath.join(self.upload_to, value.name),
                ContentFile(value.read()))
            if self.no_aws_qs:
                default_storage.querystring_auth = False
            return default_storage.url(path)

        return value
