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
