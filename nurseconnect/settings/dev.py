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

JEMBI_URL = "http://example.com"
JEMBI_USERNAME = "user"
JEMBI_PASSWORD = "password"

try:
    from .local import *  # noqa
except ImportError:
    pass
