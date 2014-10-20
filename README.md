# Mutually Exclusive Form Fields

## Install
### PyPI
```
pip install django-xor-formfields
```

### Source
```
python setup.py install
```

## Example mutually exclusive form field (TextInput & Select):
```
MutuallyExclusiveValueField(
    fields=(forms.IntegerField(), forms.IntegerField()),
    widget=MutuallyExclusiveRadioWidget(widgets=[
            forms.Select(choices=[(1,1), (2,2)]),
            forms.TextInput(attrs={'placeholder': 'Enter a number'}),
        ]))
```

## Using FileOrUrlField
This library also includes a more complete field that inherits from
`MutuallyExclusiveValueField` that allows users to upload files via an URL or a
file upload. The field accepts a `to` parameter accepting the following values:
`None, 'url', 'file'`. This value causes the field to perform either no
normalization, normalizatoin to an url (by storing uploaded files as media) or
to a file (by downloading urls to an `InMemoryUploadedFile`).
### Example:
```
FileOrUrlField(None) # returns UploadedFile objects or URL based on user input
FileOrUrlField(to='file') # always validates to an UploadedFile
FileOrUrlField(to='url', upload_to='foobar') # always validates to an URL
```
#### AWS note:
The `FileOrUrlField` supports a they keyword argument `no_aws_qs` which
disables aws querystring authorization if using AWS via `django-storages`

## Tests & coverage!
to run the tests simply run:
```
DJANGO_SETTINGS_MODULE=xorformfields.test_settings django-admin.py test xorformfields
```

Coverage results are available here: https://dschep.github.io/django-xor-formfields/htmlcov/
