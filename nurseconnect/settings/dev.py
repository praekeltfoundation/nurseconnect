from .base import *  # noqa


DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# WAGTAILSEARCH_BACKENDS = {
#     "default": {
#         "BACKEND": ("molo.core.wagtailsearch.backends.elasticsearch"),
#         "INDEX": "base",
#         "URLS": ["http://localhost:9200"],
#         "TIMEOUT": 5,
#     },
# }


CLINIC_CODE_API = environ.get("CLINIC_CODE_API")
FAKE_CLINIC_CODE_VALIDATION = True

# JEMBI configuration
JEMBI_URL = environ.get("JEMBI_URL")
JEMBI_USERNAME = environ.get("JEMBI_USERNAME")
JEMBI_PASSWORD = environ.get("JEMBI_PASSWORD")

ALLOWED_HOSTS = [
    'localhost',
    '.localhost',
    'site2',
    '127.0.0.1'
]

try:
    from .local import *  # noqa
except ImportError:
    pass
