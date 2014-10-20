import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = ' '

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MIDDLEWARE_CLASSES = []

INSTALLED_APPS = ['xorformfields']
