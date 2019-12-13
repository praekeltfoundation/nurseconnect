# -*- coding: utf-8 -*-
"""
Django settings for base nurseconnect.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from copy import copy
from os.path import abspath, dirname, join
from os import environ
import sys
import django.conf.locale
from django.conf import global_settings
from django.utils.translation import ugettext_lazy as _
import dj_database_url  # noqa
import djcelery
from celery.schedules import crontab

djcelery.setup_loader()

# Absolute filesystem path to the Django project directory:
PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "^ftq6@u6!86we(2_o#r)p)&)w!1*%!@spmpen**8$s!2sn1fop"

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = environ.get('ALLOWED_HOSTS', '').split(",")

# Base URL to use when referring to full URLs within the Wagtail admin
# backend - e.g. in notification emails. Don"t include "/admin" or
# a trailing slash
BASE_URL = "http://example.com"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_extensions",

    'taggit',
    "modelcluster",

    "nurseconnect",
    "molo.core",
    'google_analytics',
    "molo.surveys",
    "molo.profiles",
    "molo.yourwords",
    "django_comments",
    "molo.commenting",
    "wagtail_personalisation",

    'wagtail.wagtailcore',
    'wagtail.wagtailadmin',
    'wagtail.wagtaildocs',
    'wagtail.wagtailsnippets',
    'wagtail.wagtailusers',
    'wagtail.wagtailsites',
    'wagtail.wagtailimages',
    'wagtail.wagtailembeds',
    'wagtail.wagtailsearch',
    'wagtail.wagtailredirects',
    'wagtail.wagtailforms',
    'wagtailmedia',
    'wagtail.contrib.settings',
    'wagtail.contrib.modeladmin',
    'wagtailsurveys',
    'wagtail.contrib.wagtailsitemaps',

    "mptt",
    'raven.contrib.django.raven_compat',
    'djcelery',
    'django_cas_ng',
    'compressor',
    'el_pagination',
    'analytics',

    'storages',
]

COMMENTS_APP = "molo.commenting"
COMMENTS_FLAG_THRESHHOLD = 3
COMMENTS_HIDE_REMOVED = False

SITE_ID = 1

MIDDLEWARE_CLASSES = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    'molo.core.middleware.ForceDefaultLanguageMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    'molo.core.middleware.AdminLocaleMiddleware',
    'molo.core.middleware.NoScriptGASessionMiddleware',
    'molo.core.middleware.MoloGoogleAnalyticsMiddleware',
    'analytics.middleware.AnalyticsMiddleware',
    "wagtail.wagtailcore.middleware.SiteMiddleware",
    "wagtail.wagtailredirects.middleware.RedirectMiddleware",
    'molo.core.middleware.MultiSiteRedirectToHomepage',
]

GOOGLE_ANALYTICS = {}
GOOGLE_ANALYTICS_IGNORE_PATH = [
    # health check used by marathon
    '/health/',
    # admin interfaces for wagtail and django
    '/admin/', '/django-admin/',
    # Universal Core content import URL
    '/import/',
    # browser troll paths
    '/favicon.ico', '/robots.txt',
    # when using nginx, we handle statics and media
    # but including them here just incase
    '/media/', '/static/',
    # metrics URL used by promethius monitoring system
    '/metrics',
]
ANALYTICS_IGNORE_PATH = copy(GOOGLE_ANALYTICS_IGNORE_PATH) + [
    # nurseconnect makes AJAX calls to menu on every page load
    # for some reason request.is_ajax fails to pick this up
    '/menu/',
]

# Authentication backends
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)

ENV = 'dev'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "molo.core.context_processors.locale",
                'nurseconnect.context_processors.compress_settings',
            ],
        },
    },
]

ROOT_URLCONF = "nurseconnect.urls"
WSGI_APPLICATION = "nurseconnect.wsgi.application"

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# SQLite (simplest install)
DATABASES = {"default": dj_database_url.config(
    default="sqlite:///{}".format(join(PROJECT_ROOT, "db.sqlite3"),))}

# PostgreSQL (Recommended, but requires the psycopg2 library and Postgresql
#             development headers)
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": "nurseconnect",
#         "USER": "nurseconnect",
#         "PASSWORD": "nurseconnect",
#         "HOST": "localhost",  # Set to empty string for localhost.
#         "PORT": "",  # Set to empty string for default.
#         # number of seconds database connections should persist for
#         "CONN_MAX_AGE": 600,
#     }
# }

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ALWAYS_EAGER = False
CELERY_IMPORTS = ('molo.core.tasks', 'google_analytics.tasks')
BROKER_URL = environ.get("BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERYBEAT_SCHEDULE = {
    'rotate_content': {
        'task': 'molo.core.tasks.rotate_content',
        'schedule': crontab(minute=0),
    },
    'molo_consolidated_minute_task': {
        'task': 'molo.core.tasks.molo_consolidated_minute_task',
        'schedule': crontab(minute='*'),
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = "en"
TIME_ZONE = "Africa/Johannesburg"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Native South African languages are currently not included in the default
# list of languges in django
# https://github.com/django/django/blob/master/django/conf/global_settings.py#L50
LANGUAGES = global_settings.LANGUAGES + [
    ("zu", _("Zulu")),
    ("xh", _("Xhosa")),
    ("st", _("Sotho")),
    ("ve", _("Venda")),
    ("tn", _("Tswana")),
    ("ts", _("Tsonga")),
    ("ss", _("Swati")),
    ("nr", _("Ndebele")),
]

EXTRA_LANG_INFO = {
    "zu": {
        "bidi": False,
        "code": "zu",
        "name": "Zulu",
        "name_local": "isiZulu",
    },
    "xh": {
        "bidi": False,
        "code": "xh",
        "name": "Xhosa",
        "name_local": "isiXhosa",
    },
    "st": {
        "bidi": False,
        "code": "st",
        "name": "Sotho",
        "name_local": "seSotho",
    },
    "ve": {
        "bidi": False,
        "code": "ve",
        "name": "Venda",
        "name_local": u"tshiVenḓa",
    },
    "tn": {
        "bidi": False,
        "code": "tn",
        "name": "Tswana",
        "name_local": "Setswana",
    },
    "ts": {
        "bidi": False,
        "code": "ts",
        "name": "Tsonga",
        "name_local": "xiTsonga",
    },
    "ss": {
        "bidi": False,
        "code": "ss",
        "name": "Swati",
        "name_local": "siSwati",
    },
    "nr": {
        "bidi": False,
        "code": "nr",
        "name": "Ndebele",
        "name_local": "isiNdebele",
    }
}

django.conf.locale.LANG_INFO.update(EXTRA_LANG_INFO)

LOCALE_PATHS = [
    join(PROJECT_ROOT, "locale"),
]

# Region for phone number validation
PHONENUMBER_DEFAULT_REGION = 'ZA'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = join(PROJECT_ROOT, "static")
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    join(PROJECT_ROOT, "fed/dist"),
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

MEDIA_ROOT = join(PROJECT_ROOT, "media")
MEDIA_URL = "/media/"

# Django compressor settings
# http://django-compressor.readthedocs.org/en/latest/settings/

COMPRESS_PRECOMPILERS = [
    ("text/x-scss", "django_libsass.SassCompiler"),
]

WAGTAIL_SITE_NAME = "base"

SITE_NAME = environ.get("SITE_NAME", "nurseconnect")
WAGTAIL_SITE_NAME = SITE_NAME

# Whether to use face/feature detection to improve image
# cropping - requires OpenCV
WAGTAILIMAGES_FEATURE_DETECTION_ENABLED = False

ENABLE_SSO = False

UNICORE_DISTRIBUTE_API = "http://localhost:6543"

ADMIN_LANGUAGE_CODE = environ.get("ADMIN_LANGUAGE_CODE", "en")

FROM_EMAIL = environ.get("FROM_EMAIL", "support@moloproject.org")
CONTENT_IMPORT_SUBJECT = environ.get(
    "CONTENT_IMPORT_SUBJECT", "Molo Content Import")

# SMTP Settings
EMAIL_HOST = environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = environ.get("EMAIL_PORT", 25)
EMAIL_HOST_USER = environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = environ.get("EMAIL_HOST_PASSWORD", "")

# LOGIN URL used for restrcited views
LOGIN_URL = "auth_login"
WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_URL

# For QA and production
CLINIC_CODE_API = environ.get("CLINIC_CODE_API")
FAKE_CLINIC_CODE_VALIDATION = False

LOGIN_REDIRECT_URL = "/"

JEMBI = {
    "num_nurses": {
        "dataElement": "uaQ8nZ2z8sl",
    },
    "nurses_per_facility": {
        "dataElement": "BAolygGNLPC",
    }
}

LOGGING = {
    "version": 1,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"  # noqa
        },
    },
    "handlers": {
        "console": {
            "level": "WARN",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout
        },
    },
    "loggers": {
        "nurseconnect.services": {
            "level": "WARN",
        },
        "requests.packages.urllib3": {
            "level": "WARN",
            "formatter": "verbose",
            "stream": sys.stdout
        },
    }
}

# Use Elasticsearch as the search backend for extra performance and better
# search results:
# http://wagtail.readthedocs.org/en/latest/howto/performance.html#search
# http://wagtail.readthedocs.org/en/latest/core_components/
#     search/backends.html#elasticsearch-backend
#

ES_HOST = environ.get('ES_HOST')
ES_INDEX = environ.get('ES_INDEX')
ES_VERSION = int(environ.get('ES_VERSION', 2))

ES_BACKEND_V1 = 'nurseconnect.wagtailsearch.backends.elasticsearch'
ES_BACKEND_V2 = 'nurseconnect.wagtailsearch.backends.elasticsearch2'

if ES_VERSION == 2:
    SELECTED_ES_BACKEND = ES_BACKEND_V2
else:
    SELECTED_ES_BACKEND = ES_BACKEND_V1

ES_SELECTED_INDEX = ES_INDEX or environ.get('MARATHON_APP_ID', '')

if ES_HOST and ES_SELECTED_INDEX:
    WAGTAILSEARCH_BACKENDS = {
        'default': {
            'BACKEND': SELECTED_ES_BACKEND,
            'URLS': [ES_HOST],
            'INDEX': ES_SELECTED_INDEX.replace('/', '')
        },
    }

AWS_S3_FILE_OVERWRITE = False
AWS_STORAGE_BUCKET_NAME = environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)

if AWS_STORAGE_BUCKET_NAME and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    MEDIA_URL = "https://{}/".format(AWS_S3_CUSTOM_DOMAIN)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
