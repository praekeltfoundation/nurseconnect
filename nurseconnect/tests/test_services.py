import logging
import responses

from django.test import TestCase, override_settings

from nurseconnect.services import get_clinic_code

FAKE_URL = "https://username:password@external.api/"

FAKE_ENDPOINT_RESPONSE = {
    "title": "Facility Check Nurse Connect",
    "headers": [
        {
            "name": "value",
            "column": "value",
            "type": "java.lang.String",
            "hidden": False,
            "meta": False
        },
        {
            "name": "uid",
            "column": "uid",
            "type": "java.lang.String",
            "hidden": False,
            "meta": False
        },
        {
            "name": "name",
            "column": "name",
            "type": "java.lang.String",
            "hidden": False,
            "meta": False
        }
    ],
    "rows": [
        [
            "123456",
            "aTud78njasdf",
            "NC Test Clinic"
        ]
    ],
    "width": 3,
    "height": 1
}

FAKE_ENDPOINT_INVALID_PARAM_RESPONSE = {
    "title": "",
    "headers": [],
    "rows": [],
    "width": 0,
    "height": 0
}


@override_settings(CLINIC_CODE_API=FAKE_URL)
class ServicesTestCase(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.clinic_code = 123456
        self.complete_url = "{}?criteria=value:{}".format(FAKE_URL,
                                                          self.clinic_code)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @override_settings(FAKE_CLINIC_CODE_VALIDATION=True, DEBUG=True)
    def test_get_clinic_code_returns_fake_data(self):
        self.assertEqual(
            get_clinic_code(self.clinic_code),
            [0, 1, "fake_clinic_name"]
        )

    @responses.activate
    def test_get_clinic_code_returns_none_from_400(self):
        responses.add(responses.GET, self.complete_url, status=400)
        self.assertEqual(get_clinic_code(self.clinic_code), None)

    @responses.activate
    def test_get_clinic_code_returns_none_no_json(self):
        responses.add(responses.GET, self.complete_url, status=200)
        self.assertEqual(get_clinic_code(self.clinic_code), None)

    @responses.activate
    def test_get_clinic_code_returns_none_not_found(self):
        responses.add(responses.GET, self.complete_url,
                      json={'error': 'not found'}, status=200)
        self.assertEqual(get_clinic_code(self.clinic_code), None)

    @responses.activate
    def test_get_clinic_code_returns_none_invalid_response(self):
        responses.add(responses.GET, self.complete_url,
                      json=FAKE_ENDPOINT_INVALID_PARAM_RESPONSE,
                      status=200)
        self.assertEqual(get_clinic_code(self.clinic_code), None)

    @responses.activate
    def test_get_clinic_code_returns_values(self):
        responses.add(responses.GET, self.complete_url,
                      json=FAKE_ENDPOINT_RESPONSE, status=200)
        self.assertEqual(
            get_clinic_code(self.clinic_code),
            FAKE_ENDPOINT_RESPONSE["rows"][0])
