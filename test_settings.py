yfrom nurseconnect.settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'nurseconnect_test.db',
    }
}

DEBUG = True
CELERY_ALWAYS_EAGER = True

CLINIC_CODE_API = "http://user:password@exmaple.com"
JEMBI_URL = "http://www.example.com"
JEMBI_USERNAME = "username"
JEMBI_PASSWORD = "password"
