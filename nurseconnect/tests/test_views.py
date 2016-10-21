from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.models import SecurityQuestion

from nurseconnect import forms
from wagtail.contrib.settings.context_processors import SettingsProxy
from wagtail.wagtailcore.models import Site


class RegistrationViewTest(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_register_initial_view(self):
        response = self.client.get(reverse("user_register"))
        self.assertRedirects(
            response,
            "/profiles/register-msisdn/",
            status_code=302,
            target_status_code=200, host=None, msg_prefix='',
            fetch_redirect_response=True)

    def test_register_msisdn_view(self):
        response = self.client.get(reverse("user_register_msisdn"))
        self.assertTrue(isinstance(response.context["form"],
                                   forms.RegistrationMSISDNForm))

    def test_register_security_questions_view(self):
        response = self.client.get(reverse("user_register_security_questions"))
        self.assertTrue(isinstance(response.context["form"],
                                   forms.RegistrationSecurityQuestionsForm))

    def test_register_clinic_code_view(self):
        response = self.client.get(reverse("user_register_clinic_code"))
        self.assertTrue(isinstance(response.context["form"],
                                   forms.RegistrationClinicCodeForm))

    def test_register_msisdn_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse("user_register_msisdn"), {})
        self.assertFormError(
            response, "form", "username",
            [u"Please enter a valid South African cellphone number."])
        self.assertFormError(
            response, "form", "password", ["This field is required."])
        self.assertFormError(
            response, "form", "confirm_password", ["This field is required."])
        self.assertFormError(
            response, "form", "terms_and_conditions", [
                "This field is required."
            ])

    def test_security_questions(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)

        SecurityQuestion.objects.create(
            title="What is your name?",
            slug="what-is-your-name",
            path="0002",
            depth=1,
        )

        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.show_security_question_fields = True
        profile_settings.security_questions_required = True
        profile_settings.save()

        response = self.client.get(
              reverse('user_register_security_questions')
        )
        self.assertContains(response, "What is your name")

        # register with security questions
        response = self.client.post(
            reverse("user_register_security_questions"),
            {},
        )
        self.assertFormError(
            response, "form", "question_0",
            ["This field is required."])

    def test_register_clinic_code_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse("user_register_clinic_code"), {
        })
        self.assertFormError(
            response, "form", "clinic_code",
            ["This field is required."])
