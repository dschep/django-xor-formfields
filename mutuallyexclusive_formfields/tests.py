import StringIO
import tempfile
import shutil
import urlparse

from django.test import TestCase
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from mutuallyexclusive_formfields.forms import (
        FileOrURLField, MutuallyExclusiveRadioWidget,
        MutuallyExclusiveValueField, FileOrURLWidget,
        )

class MutuallyExclusiveValueFieldTestCase(TestCase):
    def setUp(self):
        class TestForm(forms.Form):
            test_field = MutuallyExclusiveValueField(
                fields=(forms.IntegerField(), forms.IntegerField()),
                widget=MutuallyExclusiveRadioWidget(widgets=[
                        forms.Select(choices=[(1,1), (2,2)]),
                        forms.TextInput(attrs={'placeholder': 'Enter a number'}),
                    ]))
        self.form = TestForm

    def test_first_values(self):
        form = self.form({'test_field_0': 1})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['test_field'], 1)

    def test_second_values(self):
        form = self.form({'test_field_1': 1})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['test_field'], 1)

    def test_0_values(self):
        form = self.form({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'test_field': [forms.Field.default_error_messages['required']]})

    def test_2_values(self):
        form = self.form({'test_field_1': 1, 'test_field_0': 42})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'test_field':
            [MutuallyExclusiveValueField.too_many_values_error]})


class OptionalMutuallyExclusiveValueFieldTestCase(TestCase):
    def setUp(self):
        class TestForm(forms.Form):
            test_field = MutuallyExclusiveValueField(
                required=False,
                fields=(forms.IntegerField(), forms.IntegerField()),
                widget=MutuallyExclusiveRadioWidget(widgets=[
                        forms.Select(choices=[(1,1), (2,2)]),
                        forms.TextInput(attrs={'placeholder': 'Enter a number'}),
                    ]))
        self.form = TestForm

    def test_0_values(self):
        form = self.form({})
        self.assertTrue(form.is_valid())
        self.assertIs(form.cleaned_data['test_field'], None)


class FileOrURLTestCaseBase(TestCase):
    test_file = InMemoryUploadedFile(
            StringIO.StringIO(' '), None, 'file', 'text/plain', 1, None)
    test_url = 'http://example.com/'

    def setUp(self):
        class TestForm(forms.Form):
            test_field = FileOrURLField()
        self.form = TestForm


class OptionalFileOrURLTestCase(FileOrURLTestCaseBase):
    def setUp(self):
        class TestForm(forms.Form):
            test_field = FileOrURLField(required=False)
        self.form = TestForm

    def test_0_values(self):
        form = self.form({})
        self.assertTrue(form.is_valid())
        self.assertIs(form.cleaned_data['test_field'], None)


class FileOrURLTestZeroOrTwoValsMixin():
    def test_0_values(self):
        form = self.form({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'test_field': [forms.Field.default_error_messages['required']]})

    def test_2_values(self):
        form = self.form(
                {'test_field_1': self.test_url},
                {'test_field_0': self.test_file},
            )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'test_field':
            [MutuallyExclusiveValueField.too_many_values_error]})


class FileOrURLPassthrougFileTestCase(FileOrURLTestZeroOrTwoValsMixin, FileOrURLTestCaseBase):
    def test_validate_file_passthrough(self):
        form = self.form({}, {
            'test_field_0': self.test_file,
            })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['test_field'], self.test_file)


class FileOrURLPassthrougURLTestCase(FileOrURLTestZeroOrTwoValsMixin, FileOrURLTestCaseBase):
    def test_validate_url_passthrough(self):
        form = self.form({
            'test_field_1': self.test_url,
            })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['test_field'], self.test_url)



class FileOrURLToURLTestCase(FileOrURLPassthrougURLTestCase):
    def setUp(self):
        class TestForm(forms.Form):
            test_field = FileOrURLField(to='url', upload_to='TEST')
        self.form = TestForm

        settings._original_media_root = settings.MEDIA_ROOT
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media

    def tearDown(self):
        settings.MEDIA_ROOT = settings._original_media_root
        shutil.rmtree(self._temp_media, ignore_errors=True)

    def test_validate_file(self):
        form = self.form({}, {
            'test_field_0': self.test_file,
            })
        self.assertTrue(form.is_valid())
        self.assertEqual(
                form.cleaned_data['test_field'],
                urlparse.urljoin(settings.MEDIA_URL, 'TEST/file'))


class MutuallyExclusiveRadioWidgetTestCase(TestCase):
    def test_mutuallyexclusiveradiowidget(self):
        w = MutuallyExclusiveRadioWidget(widgets=[
                forms.Select(choices=[(1,1), (2,2)]),
                forms.TextInput(attrs={'placeholder': 'Enter a number'}),
                ])
        self.assertHTMLEqual(w.render('test', None),
                '<div id="test_container" class="mutually-exclusive-widget">'
                '<div><input checked="" name="test_radio" type="radio" />'
                '<select name="test_0"><option value="1">1</option>'
                '<option value="2">2</option></select></div>'
                '<div><input name="test_radio" type="radio" />'
                '<input name="test_1" placeholder="Enter a number" type="text" /></div></div>')
        self.assertHTMLEqual(w.render('test', ''),
                '<div id="test_container" class="mutually-exclusive-widget">'
                '<div><input checked="" name="test_radio" type="radio" />'
                '<select name="test_0"><option value="1">1</option>'
                '<option value="2">2</option></select></div>'
                '<div><input name="test_radio" type="radio" />'
                '<input name="test_1" placeholder="Enter a number" type="text" /></div></div>')
        self.assertHTMLEqual(w.render('test', '1'),
                '<div id="test_container" class="mutually-exclusive-widget">'
                '<div><input checked="" name="test_radio" type="radio" />'
                '<select name="test_0"><option value="1">1</option>'
                '<option value="2">2</option></select></div>'
                '<div><input name="test_radio" type="radio" />'
                '<input name="test_1" placeholder="Enter a number" type="text" /></div></div>')
        self.assertHTMLEqual(w.render('test', ['1', None]),
                '<div id="test_container" class="mutually-exclusive-widget">'
                '<div><input checked="" name="test_radio" type="radio" />'
                '<select name="test_0"><option value="1" selected="selected">1</option>'
                '<option value="2">2</option></select></div>'
                '<div><input name="test_radio" type="radio" />'
                '<input name="test_1" placeholder="Enter a number" type="text" /></div></div>')
        self.assertHTMLEqual(w.render('test', [None, '1']),
                '<div id="test_container" class="mutually-exclusive-widget">'
                '<div><input name="test_radio" type="radio" /><select name="test_0">'
                '<option value="1">1</option><option value="2">2</option>'
                '</select></div><div><input checked="" name="test_radio" type="radio" />'
                '<input name="test_1" placeholder="Enter a number" type="text" value="1" /></div></div>')


class FileOrURLWidgetTestCase(TestCase):
    def test_fileorurlwidget(self):
        w = FileOrURLWidget()
        self.assertHTMLEqual(w.render('test', None),
                '<div id="test_container" class="mutually-exclusive-widget">'
                '<div><input checked="" name="test_radio" type="radio" />'
                '<input name="test_0" type="file" /></div><div>'
                '<input name="test_radio" type="radio" />'
                '<input name="test_1" placeholder="Enter URL" type="url" />'
                '</div></div>')
        self.assertHTMLEqual(w.render('test', ''),
                '<div id="test_container" class="mutually-exclusive-widget">'
                '<div><input checked="" name="test_radio" type="radio" />'
                '<input name="test_0" type="file" /></div><div>'
                '<input name="test_radio" type="radio" />'
                '<input name="test_1" placeholder="Enter URL" type="url" />'
                '</div></div>')
        self.assertHTMLEqual(w.render('test', 'http://example.com'),
                '<div id="test_container" class="mutually-exclusive-widget">'
                '<div><input name="test_radio" type="radio" />'
                '<input name="test_0" type="file" /></div><div>'
                '<input checked="" name="test_radio" type="radio" />'
                '<input name="test_1" placeholder="Enter URL" type="url" value="http://example.com"/>'
                '</div></div>')
        self.assertHTMLEqual(w.render('test', [None, 'http://example.com']),
                '<div id="test_container" class="mutually-exclusive-widget">'
                '<div><input name="test_radio" type="radio" />'
                '<input name="test_0" type="file" /></div><div>'
                '<input checked="" name="test_radio" type="radio" />'
                '<input name="test_1" placeholder="Enter URL" type="url" '
                'value="http://example.com" />'
                '</div></div>')

