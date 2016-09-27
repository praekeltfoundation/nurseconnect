from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.test.client import Client

from molo.core.tests.base import MoloTestCaseMixin

from nurseconnect import forms, views


class UserProfileTests(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.mk_main()

    def test_invalid_username_raises_error(self):
        # Username is expected to be a South African number,
        # normalised to +27 country code
        response = self.client.post(reverse("user_register"), {
            "username": "wrong username",
            "confirm_password": "1234"
        })
        self.assertFormError(
            response, "form", "username",
            [u"Please enter a valid South African cellphone number."]
        )

        # Invalid because 088 is not a valid SA cellphone code
        response = self.client.post(reverse("user_register"), {
            "username": "0881231234",
            "confirm_password": "1234"
        })
        self.assertFormError(
            response, "form", "username",
            [u"Please enter a valid South African cellphone number."]
        )

    def test_register_user_validation(self):
        # Passwords with non-alphanumeric characters raise errors
        response = self.client.post(reverse("user_register"), {
            "username": "0820000000",
            "password": "wrong$$$",
            "clinic_code": "000xx"
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

        # Clinic code must be six digits
        self.assertFormError(
            response, "form", "clinic_code",
            [u"Please enter your 6 digit clinic code"]
        )

        # Phone number starting with zero gives no errors
        response = self.client.post(
            reverse("user_register"),
            {
                "username": "0820000000",
                "clinic_code": "000000",
                "password": "1234",
                "confirm_password": "1234",
                "terms_and_conditions": True,
            },
            follow=True
        )
        self.assertRedirects(response, reverse("home"))

        # Phone number starting with +27 gives no errors
        response = self.client.post(
            reverse("user_register"),
            {
                "username": "+2782111111",
                "clinic_code": "000000",
                "password": "1234",
                "confirm_password": "1234",
                "terms_and_conditions": True,
            },
            follow=True
        )
        self.assertRedirects(response, reverse("home"))

        # User already exists
        User.objects.create_user(
            username="+27791234567",
            password="1234"
        )
        response = self.client.post(
            reverse("user_register"),
            {
                "username": "+27791234567",
                "password": "1234",
            }
        )
        self.assertFormError(
            response, "form", "username",
            [u"Username already exists."]
        )

    def test_login(self):
        pass

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
        user = User.objects.create_user("+27811231234", password="1234")
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

        # TOOD: verify that data has changed after edit
