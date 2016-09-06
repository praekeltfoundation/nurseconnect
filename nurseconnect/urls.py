import os

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

from nurseconnect import views

# implement CAS URLs in a production setting
if settings.ENABLE_SSO:
    urlpatterns = patterns(
        "",
        url(r"^admin/login/", "django_cas_ng.views.login"),
        url(r"^admin/logout/", "django_cas_ng.views.logout"),
        url(r"^admin/callback/", "django_cas_ng.views.callback"),
    )
else:
    urlpatterns = patterns("", )

urlpatterns += patterns(
    "",
    url(r"^django-admin/", include(admin.site.urls)),
    url(r"^admin/", include(wagtailadmin_urls)),
    url(r"^documents/", include(wagtaildocs_urls)),
    url(r"search/$", views.search, name="search"),
    url(r"sections/$", include(wagtail_urls)),

    url(
        r"^profiles/",
        include("molo.profiles.urls", namespace="molo.profiles")
    ),
    url(r'^comments/', include('molo.commenting.urls')),

    url(r"^styleguide/", include("styleguide.urls", namespace="styleguide")),
    url(r"", include("molo.core.urls")),
    url("^", include("django.contrib.auth.urls")),
    url(r"", include(wagtail_urls)),
)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL + "images/",
        document_root=os.path.join(settings.MEDIA_ROOT, "images"))
