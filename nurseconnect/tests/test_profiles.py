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

import mock

from molo.core.models import SiteLanguage
from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.models import SecurityQuestion
from wagtail.contrib.settings.context_processors import SettingsProxy
from wagtail.wagtailcore.models import Site

from nurseconnect import forms

import pytest


class PerfectRegistrationTestCase(TestCase, MoloTestCaseMixin):
    """
    Tests for the 3 step registration process.
    Successful flow through the steps is as follows
    MSISDN -> Security Questions -> Clinic code
    """
    def setUp(self):
        self.mk_main()
        self.client = Client()

        # site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(self.site)
        self.profile_settings = settings["profiles"]["UserProfilesSettings"]
        self.profile_settings.show_security_question_fields = True
        self.profile_settings.security_questions_required = True
        self.profile_settings.save()

        # security question
        # Creates Main language
        SiteLanguage.objects.create(locale='en')
        # create a few security questions
        self.q1 = SecurityQuestion(
            title="How old are you?",
            slug="how-old-are-you",
            path="0002",
            depth=1,
        )
        self.q1.save()

    def test_it(self):
        # post msisdn step
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

        # create security question
        self.client.get(reverse("user_register_security_questions"))
        response = self.client.post(
            reverse("user_register_security_questions"),
            {
                "question_0": "answer",
            },
            follow=True
        )
        self.assertRedirects(
            response, reverse("user_register_clinic_code")
        )


class MSISDNTestCase(MoloTestCaseMixin, TestCase):
    """
    Verify the correct error messages for the
    MSISDN step
    """

    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.user = User.objects.create_user(
            username="+27821231234",
            password="0000")

    def test_existing_username_raises_error(self):
        response = self.client.post(reverse("user_register_msisdn"), {
            "username": "+27821231234",
            "password": "0000",
            "confirm_password": "0000",
            "terms_and_conditions": True,
        })
        self.assertContains(response, "Username already exists")

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

    def invalid_south_african_number_raises_error(self):
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


# class PerfectEditProfileTestCase(MoloTestCaseMixin, TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.mk_main()
#         # self.user = User.objects.create_user("0811231234", password="1234")
#
#     def test_edit_personal_details(self):
#         User.objects.create_user("0811231234", password="1234")
#         self.client.login(username="+27811231234", password="1234")
#         response = self.client.get(
#             reverse("edit_my_profile", kwargs={"edit": "edit-settings"})
#         )
#
#         # EditProfileForm fields should be editable
#         self.assertEqual(
#             response.context["settings_form"].fields[
#                 "first_name"].widget.attrs["readonly"],
#             False
#         )
#
#         # For unspecified first and last names, show "Anonymous"
#         self.assertEqual(
#             response.context["settings_form"].fields[
#                 "first_name"].initial,
#             ""
#         )

class EditPersonalDetailsTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()
        self.user = User.objects.create_user("+27811231234", password="1234")
        self.client.login(username="+27811231234", password="1234")

    def test_personal_details_fields_are_editable(self):
        response = self.client.get(
            reverse("edit_my_profile", kwargs={"edit": "edit-settings"})
        )

        # EditProfileForm fields should be editable
        self.assertEqual(
            response.context["settings_form"].fields[
                "first_name"].widget.attrs["readonly"],
            False
        )

    @mock.patch("nurseconnect.views.get_clinic_code")
    def test_personal_details_can_be_changed(self, clinic_code_mock):
        clinic_code_mock.return_value = "388624","IKchmc9mrc6","kz Mshudu Clinic"
        response = self.client.post(
            reverse("edit_my_profile", kwargs={"edit": "edit-settings"}),
            {
                "settings_form-first_name": "First",
                "settings_form-last_name": "Last",
                "settings_form-username": "+27811231234",
            },
            follow=True
        )
        self.assertContains(response, "Profile successfully updated")

    @mock.patch("nurseconnect.views.get_clinic_code")
    def test_username_can_be_changed(self, clinic_code_mock):
        clinic_code_mock.return_value = "388624", "IKchmc9mrc6", "kz Mshudu Clinic"
        response = self.client.post(
            reverse("edit_my_profile", kwargs={"edit": "edit-settings"}),
            {
                "settings_form-username": "+27811231233",
            },
            follow=True
        )
        self.assertContains(response, "Username successfully updated")

    @mock.patch("nurseconnect.views.get_clinic_code")
    def test_invalid_username_raises_error(self, clinic_code_mock):
        clinic_code_mock.return_value = "388624", "IKchmc9mrc6", "kz Mshudu Clinic"
        response = self.client.post(
            reverse("edit_my_profile", kwargs={"edit": "edit-settings"}),
            {
                "settings_form-username": "39311231233",
            },
            follow=True
        )
        self.assertContains(response, "Please enter a valid South African cellphone number")

    @mock.patch("nurseconnect.views.get_clinic_code")
    def test_clinic_code_can_be_changed(self, clinic_code_mock):
        clinic_code_mock.return_value = "000111", "IKchmc9mrc6", "kz Mshudu Clinic"
        response = self.client.post(
            reverse("edit_my_profile", kwargs={"edit": "edit-settings"}),
            {
                "settings_form-username": "+27811231233",
                "settings_form-clinic_code": "000111"
            },
            follow=True
        )
        # TODO: save the changed clinic code

    @mock.patch("nurseconnect.views.get_clinic_code")
    def test_invalid_clinic_code_raises_error(self, clinic_code_mock):
        clinic_code_mock.return_value = None
        response = self.client.post(
            reverse("edit_my_profile", kwargs={"edit": "edit-settings"}),
            {
                "settings_form-username": "+27811231233",
                "settings_form-clinic_code": "000111"
            },
            follow=True
        )
        self.assertContains(response, "Clinic code does not exist")


class EditPasswordTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()
        self.user = User.objects.create_user("+27811231234", password="1234")
        self.client.login(username="+27811231234", password="1234")

    def test_password_fields_are_editable(self):
        response = self.client.get(
            reverse("edit_my_profile", kwargs={"edit": "edit-password"})
        )

        # ProfilePasswordChangeForm fields should be editable
        self.assertEqual(
            response.context["profile_password_change_form"].fields[
                "old_password"].widget.attrs["readonly"],
            False
        )

    def test_passwords_can_be_changed(self):
        self.client.get(
            reverse("edit_my_profile", kwargs={"edit": "edit-password"})
        )
        response = self.client.post(
            reverse("edit_my_profile", kwargs={"edit": "edit-password"}),
            {
                "profile_password_change_form-old_password": "1234",
                "profile_password_change_form-new_password": "0000",
                "profile_password_change_form-confirm_password": "0000"
            },
            follow=True
        )
        self.assertContains(response, "Password successfully changed!")

    def test_unmatching_passwords_raises_error(self):
        response = self.client.post(
            reverse("edit_my_profile", kwargs={"edit": "edit-password"}),
            {
                "profile_password_change_form-old_password": "1234",
                "profile_password_change_form-new_password": "0000",
                "profile_password_change_form-confirm_password": "0012"
            },
            follow=True
        )
        self.assertContains(response, "New passwords do not match.")

    def test_incoreect_old_password_raises_error(self):
        response = self.client.post(
            reverse("edit_my_profile", kwargs={"edit": "edit-password"}),
            {
                "profile_password_change_form-old_password": "0000",
                "profile_password_change_form-new_password": "0000",
                "profile_password_change_form-confirm_password": "0000"
            },
            follow=True
        )
        self.assertContains(response, "The old password is incorrect")


class ViewProfileTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_redirect_to_log_in_if_user_not_logged_in(self):
        # Redirects to login page if user is not logged in
        response = self.client.get(reverse("view_my_profile"))
        redirect_url = reverse("auth_login") + "?next=/view/myprofile/"
        self.assertRedirects(response, redirect_url)

    def test_both_forms_are_displayed(self):
        # EditProfileForm and ProfilePasswordChangeForm should both be rendered
        self.user = User.objects.create_user(username="+27811231234", password="1234")
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


# class ClinicCodeTestCase(MoloTestCaseMixin, TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.mk_main()
#
#     def test_invalid_clinic_code_raises_error(self):
#         # Clinic_code is expected to be 6 digits long
#         response = self.client.post(reverse("user_register_clinic_code"), {
#             "clinic_code": "111",
#         })
#         self.assertFormError(
#             response, "form", "clinic_code",
#             [u"Please enter your 6 digit clinic code"]
#         )
#
#         response = self.client.post(reverse("user_register_clinic_code"), {
#             "clinic_code": "1111111",
#         })
#         self.assertFormError(
#             response, "form", "clinic_code",
#             [u"Please enter your 6 digit clinic code"]
#         )
#
#         response = self.client.post(reverse("user_register_clinic_code"), {
#             "clinic_code": "asdfasdfasdf",
#         })
#         self.assertFormError(
#             response, "form", "clinic_code",
#             [u"Please enter your 6 digit clinic code"]
#         )
