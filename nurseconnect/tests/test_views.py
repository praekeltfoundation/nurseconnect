from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from wagtail.wagtailcore.models import PageViewRestriction

from molo.core.models import SiteLanguageRelation, Main, Languages
from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.models import (
    SecurityQuestion, SecurityAnswer,
    UserProfilesSettings, SecurityQuestionIndexPage
)

from nurseconnect import forms


class MenuTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()
        self.client = Client()

    def test_menu_renders_correctly(self):
        # Content in this view is dependent on there being sections.
        # So we'll test that the view returns successfully and leave
        # it at that
        response = self.client.get(reverse("menu"))
        self.assertEqual(response.status_code, 200)


class MenuSearchCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()
        self.client = Client()

    def test_search_on_homepage(self):
        # Test that the search only occurs when the user clicks on t
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'What are you looking for?')
        self.assertContains(response, 'Search')

    def test_search_view(self):
        # Test that the search only occurs when the user clicks on t
        response = self.client.get(reverse("search"))
        self.assertNotContains(response, 'What are you looking for?')
        self.assertContains(response, 'Search')


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
        self.user = User.objects.create_user(
            username="+27791234567",
            password="1234"
        )
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
        self.q1_answer = SecurityAnswer.objects.create(
            user=self.user.profile, question=self.q1)
        self.user.profile.site = self.main.get_site()
        self.user.profile.save()

    def test_view_renders(self):
        response = self.client.get(reverse("forgot_password"))
        self.assertContains(response, "Password Reset")

    def test_forgot_password_with_security_questions(self):
        answer = '20'
        self.q1_answer.set_answer(answer)
        self.q1_answer.save()
        data = {
            'username': self.user.username,
            'question_0': answer
        }
        forgot_password = reverse("forgot_password")
        response = self.client.post(forgot_password, data=data)

        self.assertTrue(
            self.user.profile.security_question_answers.exists())
        reset_password = reverse("molo.profiles:reset_password")
        self.assertTrue(reset_password in response.url)

    def test_forgot_password_with_security_questions_fail(self):
        data = {
            'username': self.user.username,
            'question_0': 'randomanswer'
        }
        forgot_password = reverse("forgot_password")
        response = self.client.post(forgot_password, data=data)

        self.assertTrue(
            self.user.profile.security_question_answers.exists())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context_data.keys())
        self.assertEqual(
            response.context_data['form'].errors['__all__'][0],
            'The username and security question(s) combination do not match.'
        )

    def test_invalid_username_forgot_password(self):
        data = {'username': 'iamnotfromhere'}
        forgot_password = reverse("forgot_password")
        response = self.client.post(forgot_password, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context_data.keys())

    def test_too_many_attempts_forgot_password(self):
        answer = '20'
        forgot_password = reverse("forgot_password")
        self.q1_answer.set_answer(answer)
        self.q1_answer.save()

        session = self.client.session
        session['forgot_password_attempts'] = -10
        session.save()

        data = {
            'username': self.user.username,
            'question_0': answer
        }

        response = self.client.post(forgot_password, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data['form'].errors['__all__'][0],
            'Too many attempts. Please try again later.'
        )

    def test_inactive_user_forgot_password(self):
        forgot_password = reverse("forgot_password")
        data = {'username': self.user.username}
        self.user.is_active = False
        self.user.save()

        response = self.client.post(forgot_password, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context_data.keys())


class TestLoginRedirect(MoloTestCaseMixin, TestCase):
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
        self.section = self.mk_section(parent=self.section_index)
        self.article = self.mk_article(parent=self.section)

    def test_logged_out_redirect(self):
        PageViewRestriction.objects.create(
            page=self.main, restriction_type='login'
        )
        response = self.client.get(self.article.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.get('location'),
            '/login/?next={}'.format(self.article.url))


class TestAnalyticsRedirectView(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()

    def test_it_sets_cookie_for_analytics(self):
        response = self.client.get('/analytics/1234/')
        self.assertEqual(response.cookies['investigation_uuid'].value, '1234')

    def test_it_sets_cookie_for_analytics_1(self):
        UUID = '68fd1165-50b9-4188-b87b-695a0a6bd3a8'
        response = self.client.get('/analytics/{}/'.format(UUID))
        self.assertEqual(response.cookies['investigation_uuid'].value, UUID)

    def test_it_redirects_to_homepage(self):
        response = self.client.get('/analytics/1234/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'http://testserver/')

    def test_it_redirects_to_specified_location(self):
        response = self.client.get('/analytics/1234/section/one/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            'http://testserver/section/one/',
        )

    def test_it_returns_bad_request_if_url_unsafe_1(self):
        response = self.client.get('/analytics/http://evil.com/')
        self.assertEqual(response.status_code, 400)

    def test_it_returns_bad_request_if_url_unsafe_2(self):
        response = self.client.get('/analytics/1234//http://evil.com/')
        self.assertEqual(response.status_code, 400)

    def test_it_returns_bad_request_if_url_unsafe_3(self):
        response = self.client.get('/analytics/0//http://evil.com/')
        self.assertEqual(response.status_code, 400)
