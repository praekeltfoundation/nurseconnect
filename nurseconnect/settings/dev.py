from .base import *  # noqa


DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": ("molo.core.wagtailsearch.backends.elasticsearch"),
        "INDEX": "base",
        "URLS": ["http://localhost:80"],
        "TIMEOUT": 5,
    },
}

try:
    from .local import *  # noqa
except ImportError:
    pass
