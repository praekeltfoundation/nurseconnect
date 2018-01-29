from datetime import datetime

import json
import responses

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase

from molo.core.tests.base import MoloTestCaseMixin
from .constants import FACILITIES
from nurseconnect import tasks


class MetricsTaskTestCase(MoloTestCaseMixin, TestCase):
    def setUp(self):
        self.client = Client()
        self.mk_main()
        self.user1 = User.objects.create_user(
            username="user1",
            password="user1"
        )
        self.user1.save()
        self.user1.profile.save()
        self.user1.profile.for_nurseconnect.clinic_code = "123456"
        self.user1.profile.for_nurseconnect.save()

        self.user2 = User.objects.create_user(
            username="user2",
            password="user2"
        )
        self.user2.save()
        self.user2.profile.save()
        self.user2.profile.for_nurseconnect.clinic_code = "234567"
        self.user2.profile.for_nurseconnect.save()

    @responses.activate
    def test_num_nurses_sent_successfully(self):
        responses.add(responses.POST, settings.JEMBI_URL,
                      body="<Response [200]>", status=200,)

        tasks.nurses_registered()
        date = "{}{:02d}".format(str(datetime.now().year),
                                 datetime.now().month)

        expected_response_body = {
            "dataValues": [{
                "dataElement": "uaQ8nZ2z8sl",
                "period": date,
                "value": "2"
            }]
        }

        self.assertEqual(
            json.loads(responses.calls[-1].request.body),
            expected_response_body
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
