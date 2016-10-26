"""
Tests for the registration process.

The registration process is broken down into three steps:
1) MSISDN: for userame and password
2) Security questions: getting answers to be used for password recovery
3) Clinic code: For obtaining the user's clinic codde
"""

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase, LiveServerTestCase
from django.test.client import Client

from molo.core.tests.base import MoloTestCaseMixin

from nurseconnect import forms


class PerfectRegistrationTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_it(self):
        # Phone number starting with zero gives no errors
        response = self.client.post(
            reverse("user_register_msisdn"),
            {
                "username": "0820000000",
                "password": "1234",
                "confirm_password": "1234",
                "terms_and_conditions": True,
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse("user_register_security_questions")
        )


class PerfectEditProfileTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()
        # self.user = User.objects.create_user("0811231234", password="1234")

    def test_edit_personal_details(self):
        User.objects.create_user("0811231234", password="1234")
        self.client.login(username="+27811231234", password="1234")
        response = self.client.get(
            reverse("edit_my_profile", kwargs={"edit": "edit-settings"})
        )

        # EditProfileForm fields should be editable
        self.assertEqual(
            response.context["settings_form"].fields[
                "first_name"].widget.attrs["readonly"],
            False
        )

        # For unspecified first and last names, show "Anonymous"
        self.assertEqual(
            response.context["settings_form"].fields[
                "first_name"].initial,
            ""
        )


class EditProfileTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(username="+27811231234", password="1234")
        self.client = Client()

    def test_redirect_to_log_in_if_user_not_logged_in(self):
        # Redirects to login page if user is not logged in
        response = self.client.get(reverse("view_my_profile"))
        redirect_url = reverse("auth_login") + "?next=/view/myprofile/"
        self.assertRedirects(response, redirect_url)

    def test_both_forms_are_displayed(self):
        # EditProfileForm and ProfilePasswordChangeForm should both be rendered
        self.client.login(username="+27811231234", password="1234")

        response = self.client.get(
            reverse("view_my_profile"),
        )
        self.assertIsInstance(
            response.context["settings_form"],
            forms.EditProfileForm
        )
        self.assertIsInstance(
            response.context["profile_password_change_form"],
            forms.ProfilePasswordChangeForm
        )

        # Fields in both forms should be read-only
        self.assertEqual(
            response.context["settings_form"].fields[
                "first_name"].widget.attrs["readonly"],
            True
        )
        self.assertEqual(
            response.context["profile_password_change_form"].fields[
                "old_password"].widget.attrs["readonly"],
            True
        )


class MSISDNTestCase(MoloTestCaseMixin, TestCase):
    """
    Verify the correct error messages for the
    MSISDN step
    """

    def setUp(self):
        self.client = Client()
        self.mk_main()
        self.user = User.objects.create_user(
            username="+270821231234",
            password="0000")
        self.user.save()

    def test_invalid_username_raisies_error(self):
        response = self.client.post(reverse("user_register_msisdn"), {
            "username": "+270821231234",
            "password": "0000",
            "confirm_password": "0000",
            "terms_and_conditions": True,
        })
        self.failUnless("Username already exists" in response.content)

    def test_invalid_username_raises_error(self):
        # Username is expected to be a South African number,
        # normalised to +27 country code
        response = self.client.post(reverse("user_register_msisdn"), {
            "username": "wrong username",
            "confirm_password": "1234"
        })
        self.assertFormError(
            response, "form", "username",
            [u"Please enter a valid South African cellphone number."]
        )

    def invalid_south_african_number_raises_erorr(self):
        # Invalid because 088 is not a valid SA cellphone code
        response = self.client.post(reverse("user_register_msisdn"), {
            "username": "0881231234",
        })
        self.assertFormError(
            response, "form", "username",
            [u"Please enter a valid South African cellphone number."]
        )

    def test_password_with_non_alphanumneric_chars_raise_error(self):
        response = self.client.post(reverse("user_register_msisdn"), {
            "password": "wrong$$$"
        })
        self.assertFormError(
            response, "form", "password",
            [u"Your password must contain any alphanumeric "
             u"combination of 4 or more characters."]
        )


class ClinicCodeTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_invalid_clinic_code_raises_error(self):
        # Clinic_code is expected to be 6 digits long
        response = self.client.post(reverse("user_register_clinic_code"), {
            "clinic_code": "111",
        })
        self.assertFormError(
            response, "form", "clinic_code",
            [u"Please enter your 6 digit clinic code"]
        )

        response = self.client.post(reverse("user_register_clinic_code"), {
            "clinic_code": "1111111",
        })
        self.assertFormError(
            response, "form", "clinic_code",
            [u"Please enter your 6 digit clinic code"]
        )

        response = self.client.post(reverse("user_register_clinic_code"), {
            "clinic_code": "asdfasdfasdf",
        })
        self.assertFormError(
            response, "form", "clinic_code",
            [u"Please enter your 6 digit clinic code"]
        )
