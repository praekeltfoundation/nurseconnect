"""
Tests for the registration process.

The registration process is broken down into three steps:
1) MSISDN: for userame and password
2) Security questions: getting answers to be used for password recovery
3) Clinic code: For obtaining the user's clinic codde
"""

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client

from molo.core.tests.base import MoloTestCaseMixin

from nurseconnect import forms


class PerfectRegistrationTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_it(self):
        pass


class PerfectEditProfileTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_it(self):
        pass


class EditProfileTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_edit_user_profile(self):
        # Redirects to login page if user is not logged in
        response = self.client.get(reverse("view_my_profile"))
        redirect_url = reverse("auth_login") + "?next=/view/myprofile/"
        self.assertRedirects(response, redirect_url)

        # EditProfileForm and ProfilePasswordChangeForm should both be rendered
        User.objects.create_user("0811231234", password="1234")
        self.client.login(username="0811231234", password="1234")

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

    def test_edit_personal_details(self):
        User.objects.create_user("+27811231234", password="1234")
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


class MSISDNTestCase(MoloTestCaseMixin, TestCase):
    """
    Verify the correct error messages for the
    MSISDN step
    """

    def setUp(self):
        self.client = Client()
        self.mk_main()

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

        # Invalid because 088 is not a valid SA cellphone code
        response = self.client.post(reverse("user_register_msisdn"), {
            "username": "0881231234",
            "confirm_password": "1234"
        })
        self.assertFormError(
            response, "form", "username",
            [u"Please enter a valid South African cellphone number."]
        )




class ClinicCodeTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_register_user_validation(self):
        # Passwords with non-alphanumeric characters raise errors
        response = self.client.post(reverse("user_register_msisdn"), {
            "username": "0820000000",
            "password": "wrong$$$"
        })
        self.assertFormError(
            response, "form", "username",
            None
        )
        self.assertFormError(
            response, "form", "password",
            [u"Your password must contain any alphanumeric "
             u"combination of 4 or more characters."]
        )

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

        # Phone number starting with +27 gives no errors
        response = self.client.post(
            reverse("user_register_msisdn"),
            {
                "username": "+2782111111",
                "password": "1234",
                "confirm_password": "1234",
                "terms_and_conditions": True,
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse("user_register_security_questions")
        )

        # User already exists
        User.objects.create_user(
            username="+27791234567",
            password="1234"
        )
        response = self.client.post(
            reverse("user_register_msisdn"),
            {
                "username": "+27791234567",
                "password": "1234",
            }
        )
        self.assertFormError(
            response, "form", "username",
            [u"Username already exists."]
        )

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