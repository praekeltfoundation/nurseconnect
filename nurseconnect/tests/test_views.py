# from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from molo.core.tests.base import MoloTestCaseMixin

from nurseconnect import forms


class RegistrationViewTest(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()

    def test_register_view(self):
        response = self.client.get(reverse("user_register"))
        self.assertTrue(isinstance(response.context["form"],
                                   forms.RegistrationForm))

    def test_register_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse("user_register"), {
        })
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


# class ProfilePasswordChangeViewTest(MoloTestCaseMixin, TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             "+27811231234",
#             password="1234"
#         )
#         self.client = Client()
#         self.client.login(username="+27811231234", password="1234")
#
#     def test_view(self):
#         response = self.client.get(reverse("view_my_profile"))
#         form = response.context["form"]
#         self.assertTrue(isinstance(form, forms.ProfilePasswordChangeForm))
#
#     def test_update_invalid_old_password(self):
#         response = self.client.post(
#             reverse("edit_my_profile", kwargs={"edit": "edit-password"}), {
#                 "old_password": "0000",
#                 "new_password": "4567",
#                 "confirm_password": "4567",
#             })
#         self.assertFormError(
#             response, "form", "old_password", ["The old password is incorrect."])
#
#     def test_update_passwords_not_matching(self):
#         response = self.client.post(
#             reverse("edit_my_profile", kwargs={"edit": "edit-password"}), {
#                 "old_password": "1234",
#                 "new_password": "1234",
#                 "confirm_password": "4567",
#             })
#         form = response.context["form"]
#         [error] = form.non_field_errors().as_data()
#         self.assertEqual(error.message, "New passwords do not match.")
#
#     def test_update_passwords(self):
#         response = self.client.post(
#             reverse("edit_my_profile", kwargs={"edit": "edit-password"}), {
#                 "old_password": "1234",
#                 "new_password": "4567",
#                 "confirm_password": "4567",
#             })
#         self.assertRedirects(
#             response, reverse("view_my_profile"))
#         # Avoid cache by loading from db
#         user = User.objects.get(pk=self.user.pk)
#         self.assertTrue(user.check_password("4567"))
