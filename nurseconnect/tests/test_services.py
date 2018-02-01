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

    @override_settings(FAKE_CLINIC_CODE_VALIDATION=True, DEBUG=True)
    def test_get_clinic_code_returns_fake_data(self):
        clinic_code = 123456

        self.assertEqual(
            get_clinic_code(clinic_code),
            [0, 1, "fake_clinic_name"]
        )

    @responses.activate
    def test_get_clinic_code_returns_none(self):
        clinic_code = 123456
        complete_url = "{}?criteria=value:{}".format(FAKE_URL, clinic_code)

        responses.add(responses.GET, FAKE_URL, status=400)
        self.assertEqual(get_clinic_code(clinic_code), None)

        responses.add(responses.GET, FAKE_URL, status=200)
        self.assertEqual(get_clinic_code(clinic_code), None)

        responses.add(responses.GET, complete_url,
                      json={'error': 'not found'}, status=200)
        self.assertEqual(get_clinic_code(clinic_code), None)

        responses.add(responses.GET, complete_url,
                      json=FAKE_ENDPOINT_INVALID_PARAM_RESPONSE,
                      status=200)
        self.assertEqual(get_clinic_code(clinic_code), None)

    @responses.activate
    def test_get_clinic_code_returns_values(self):
        clinic_code = 123456
        complete_url = "{}?criteria=value:{}".format(FAKE_URL, clinic_code)

        responses.add(responses.GET, complete_url,
                      json=FAKE_ENDPOINT_RESPONSE, status=200)
        self.assertEqual(
            get_clinic_code(clinic_code),
            FAKE_ENDPOINT_RESPONSE["rows"][0])
