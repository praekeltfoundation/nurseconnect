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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "nurseconnect",
        "USER": "nurseconnect",
        "PASSWORD": "nurseconnect",
        "HOST": "localhost",  # Set to empty string for localhost.
        "PORT": "",  # Set to empty string for default.
        # number of seconds database connections should persist for
        "CONN_MAX_AGE": 600,
    }
}

# For dev, REMOVE
CLINIC_CODE_API = "http://praekelt:praekelt@npr-staging.jembi.org:5001/ws/" \
                  "rest/v1/NCfacilityCheck?"

try:
    from .local import *  # noqa
except ImportError:
    pass
