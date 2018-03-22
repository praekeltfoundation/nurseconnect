from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from molo.core.models import SiteLanguageRelation, Main, Languages
from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.models import (
    SecurityQuestion, UserProfilesSettings, SecurityQuestionIndexPage)

from nurseconnect import forms


class MenuTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()
        self.client = Client()

        # This  URL is decorated with @login_required
        self.user = User.objects.create_user("+27811231234", password="1234")
        self.client.login(username="+27811231234", password="1234")

    def test_menu_renders_correctly(self):
        # Content in this view is dependent on there being sections.
        # So we'll test that the view returns successfully and leave
        # it at that
        response = self.client.get(reverse("menu"))
        self.assertEqual(response.status_code, 200)


class RegistrationViewTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.main = Main.objects.first()
        profile_settings = UserProfilesSettings.for_site(self.main.get_site())
        profile_settings.show_security_question_fields = True
        profile_settings.security_questions_required = True
        profile_settings.save()

        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        self.question = SecurityQuestion(
            title="What is your name?",
            slug="what-is-your-name",
        )
        self.security_index.add_child(instance=self.question)
        self.question.save()

    def test_register_initial_view(self):
        response = self.client.get(reverse("user_register"))
        self.assertRedirects(
            response,
            "/profiles/register-msisdn/",
            status_code=302,
            target_status_code=200, host=None, msg_prefix="",
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


class ForgotPasswordViewTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()
        self.client = Client()

        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

        self.profile_settings = UserProfilesSettings.for_site(
            self.main.get_site())
        self.profile_settings.show_security_question_fields = True
        self.profile_settings.security_questions_required = True
        self.profile_settings.save()

        # security question
        self.security_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security_questions',
        )
        self.main.add_child(instance=self.security_index)
        self.security_index.save()
        # create a few security questions
        self.q1 = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
        )
        self.security_index.add_child(instance=self.q1)
        self.q1.save()

    def test_view_renders(self):
        response = self.client.get(
            reverse("forgot_password")
        )
        self.assertContains(response, "Password Reset")
