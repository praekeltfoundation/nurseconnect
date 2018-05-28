from django.http import HttpResponse
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.models import UserProfile

from analytics.utils import *


class TestAnalyticsUtils(TestCase):
    def test_get_response_title(self):
        TITLE = "test title"
        response = HttpResponse(
            "<html><head><title>{}</title></head></html>".format(TITLE))
        self.assertEqual(
            get_response_title(response),
            TITLE.encode('utf-8')
        )

    def test_status_code_invalid(self):
        response = HttpResponse()
        response.status_code = 200
        self.assertFalse(status_code_invalid(response))
        response.status_code = 302
        self.assertFalse(status_code_invalid(response))
        response.status_code = 400
        self.assertTrue(status_code_invalid(response))

    def test_should_ignore_1(self):
        request = RequestFactory().get("/")
        self.assertFalse(should_ignore(request))

    @override_settings(ANALYTICS_IGNORE_PATH=["/admin"])
    def test_should_ignore_2(self):
        request = RequestFactory().get("/")
        self.assertFalse(should_ignore(request))

    @override_settings(ANALYTICS_IGNORE_PATH=["/admin"])
    def test_should_ignore_3(self):
        request = RequestFactory().get("/admin/")
        self.assertTrue(should_ignore(request))


class TestAnalyticsUserUtils(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

    def test_get_user_uuid_returns_none(self):
        request = RequestFactory().get("/")
        self.assertIsNone(get_user_uuid(request))

        request.user = AnonymousUser()
        self.assertIsNone(get_user_uuid(request))

    def test_get_user_uuid(self):
        request = RequestFactory().get("/")
        request.user = self.user
        self.assertEqual(
            get_user_uuid(request),
            self.user.profile.uuid
        )
