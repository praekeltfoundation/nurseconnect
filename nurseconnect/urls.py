import os

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.views.generic import TemplateView

from molo.profiles import views as molo_profile_views
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

from nurseconnect import forms, views
from nurseconnect.forms import NurseconnectAuthenticationForm

from analytics.views import AnalyticsRedirectView

urlpatterns = []

# implement CAS URLs in a production setting
if settings.ENABLE_SSO:  # pragma: no cover
    urlpatterns += [
        url(r"^admin/login/", "django_cas_ng.views.login"),
        url(r"^admin/logout/", "django_cas_ng.views.logout"),
        url(r"^admin/callback/", "django_cas_ng.views.callback"),
    ]

urlpatterns += [
    url(r'^analytics/(?P<investigation_uuid>[^/]+)/(?P<redirect_path>.*)$',
        AnalyticsRedirectView.as_view(),
        name='analytics_redirect'),
    url(r"^django-admin/", include(admin.site.urls)),
    url(r"^admin/", include(wagtailadmin_urls)),
    url(r"^documents/", include(wagtaildocs_urls)),
    url(
        r"^search/$",
        views.SearchView.as_view(
            template_name="search/search.html"
        ),
        name="search"
    ),
    url(
        r"^search/results/$",
        views.search,
        name="search_query"
    ),
    url(
        r"^yourwords/",
        include("molo.yourwords.urls",
                namespace="molo.yourwords",
                app_name="molo.yourwords")
    ),
    url(
        r"^profiles/register/$",
        views.RegistrationView.as_view(),
        name="user_register"
    ),
    url(
        r"^profiles/register-msisdn/$",
        views.RegistrationMSISDNView.as_view(),
        name="user_register_msisdn"
    ),
    url(
        r"^profiles/register-security-questions/$",
        views.RegistrationSecurityQuestionsView.as_view(),
        name="user_register_security_questions"
    ),
    url(
        r"^profiles/register-clinic-code/$",
        views.RegistrationClinicCodeView.as_view(),
        name="user_register_clinic_code"
    ),
    url(
        r"^profiles/register-clinic-success/$",
        views.RegistrationClinicCodeSuccessView.as_view(),
        name="user_register_clinic_code_success"
    ),
    url(
        r"^profiles/register-complete/$",
        views.RegistrationCompleteView.as_view(),
        name="user_register_complete"
    ),
    url(
        r"^view/myprofile/$",
        login_required(views.MyProfileView.as_view(
            template_name="profiles/viewprofile.html"
        )),
        name="view_my_profile"
    ),
    url(
        r"^view/myprofile/(?P<edit>[\w-]+)/$",
        login_required(views.MyProfileView.as_view(
            template_name="profiles/viewprofile.html"
        )),
        name="edit_my_profile"
    ),
    url(
        r"^profiles/forgot-password/$",
        views.NCForgotPasswordView.as_view(
            form_class=forms.ForgotPasswordForm
        ),
        name="forgot_password"
    ),
    url(
        r"^profiles/reset-password/$",
        molo_profile_views.ResetPasswordView.as_view(
            form_class=forms.ResetPasswordForm
        ),
        name="reset_password"
    ),
    url(
        r"^profiles/reset-password-success/$",
        TemplateView.as_view(
            template_name="profiles/reset_password_success.html"
        ),
        name="reset_password_success"
    ),
    url(
        r"^surveys/(?P<slug>[\w-]+)/success/$",
        views.NCSurveySuccess.as_view(),
        name="success"
    ),
    url(
        r"^menu/$",
        login_required(views.MenuView.as_view()),
        name="menu"
    ),
    url(
        r"^$",
        views.HomePageView.as_view(
            template_name="core/main.html"
        ),
        name="home"
    ),
    url(
        r"^profiles/",
        include("molo.profiles.urls", namespace="molo.profiles")
    ),
    url(
        r"^login/$",
        login, {"authentication_form": NurseconnectAuthenticationForm},
        name="auth_login"
    ),

    url(r"^comments/", include("molo.commenting.urls")),
    url(r'^surveys/',
        include('molo.surveys.urls',
                namespace='molo.surveys',
                app_name='molo.surveys')),

    url(r'', include('django_comments.urls')),
    url(r"", include("molo.core.urls")),
    url(r"", include(wagtail_urls)),
]

if settings.DEBUG:  # pragma: no cover
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL + "images/",
        document_root=os.path.join(settings.MEDIA_ROOT, "images")
    )
    urlpatterns += \
        url(
            r"^styleguide/",
            include("styleguide.urls", namespace="styleguide")
        ),
