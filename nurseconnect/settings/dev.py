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


CLINIC_CODE_API = environ.get("https://praekelt:IJGRu5gnCJeGfkd@npr-him.jembi.org:5000/ws/rest/v1/NCfacilityCheck")

# JEMBI configuration
JEMBI_URL = environ.get("JEMBI_URL")
JEMBI_USERNAME = environ.get("JEMBI_USERNAME")
JEMBI_PASSWORD = environ.get("JEMBI_PASSWORD")

try:
    from .local import *  # noqa
except ImportError:
    pass
