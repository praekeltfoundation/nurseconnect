import responses

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase

from molo.core.tests.base import MoloTestCaseMixin
from .constants import FACILITIES
from nurseconnect import tasks


class MetricsTaskTestCase(MoloTestCaseMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="user1",
            password="user1"
        )
        cls.user1.save()
        cls.user1.profile.save()
        cls.user1.profile.for_nurseconnect.clinic_code = "123456"
        cls.user1.profile.for_nurseconnect.save()

        cls.user2 = User.objects.create_user(
            username="user2",
            password="user2"
        )
        cls.user2.save()
        cls.user2.profile.save()
        cls.user2.profile.for_nurseconnect.clinic_code = "234567"
        cls.user2.profile.for_nurseconnect.save()

    def setUp(self):
        self.client = Client()
        self.mk_main()

    @responses.activate
    def test_num_nurses_sent_successfully(self):
        responses.add(responses.POST, settings.JEMBI_URL,
                      body="<Response [200]>", status=200,)

        tasks.nurses_registered()
        self.assertEqual(
            responses.calls[-1].request.body,
            '{"dataValues": [{"dataElement": '
            '"uaQ8nZ2z8sl", "period": "201601", "value": "2"}]}'
        )
        self.assertEqual(responses.calls[-1].response.status_code, 200)

    @responses.activate
    def test_nurses_per_facility(self):
        responses.add(responses.GET, settings.CLINIC_CODE_API,
                      json=FACILITIES, status=200)
        responses.add(responses.POST, settings.JEMBI_URL,
                      body="<Response [200]>", status=200, )
        tasks.nurses_registered_per_clinic()

        # Two requests are made per clinic code. One to obtain the
        # clinic code orgUnit and another to post the metric. There are two
        # clinic codes, so we expect 4 calls
        self.assertEqual(len(responses.calls), 4)
        self.assertEqual(
            responses.calls[-1].response.text,
            "<Response [200]>"
        )
        self.assertEqual(
            responses.calls[-2].response.json(),
            FACILITIES
        )
