from __future__ import absolute_import

import json
import urllib

import requests

from celery.schedules import crontab
from celery.task import periodic_task
from django.contrib.auth.models import User


URL = "https://praekelt:praekelt@npr-staging.jembi.org:5000/ws/rest/v1/" \
          "nurseconnectdataset"


def nurses_registered():
    """Returns the number of nurses registered on the system."""
    nurses = User.objects.filter(is_staff=False).count()

    data = {
        "dataValues": [
            {
                "dataElement": "CSv1k6HyWaX",
                "period": "201601",
                "orgUnit": "Fws0A9spb9F",
                "value": str(nurses)
            },
        ]
    }
    headers = {'Content-type': 'application/json'}

    requests.post(URL, data=json.dumps(data), headers=headers, verify=False)


def nurses_registered_per_clinic():
    """Returns the number of nurses registered on the system."""
    json_data = open("nurseconnect/facility_codes.json")
    data = json.loads(json_data.read())
    users = User.objects.filter(is_staff=False)
    count = 0

    for clinic in data["rows"]:
        for user in users:
            if user.profile.for_nurseconnect.clinic_code == clinic[0]:
                count += 1
        if count > 0:
            data = {
                "dataValues": [
                    {
                        "dataElement": "CSv1k6HyWaX",
                        "period": "201601",
                        "orgUnit": clinic[1],
                        "value": "999"
                    },
                ]
            }
            headers = {'Content-type': 'application/json'}

            requests.post(URL, data=json.dumps(data), headers=headers,
                          verify=False)
            count = 0


def lookup_clinic_code_orgunit(clinic_code, data):
    for clinic in data["rows"]:
        if str(clinic_code) == clinic[0]:
            return clinic[1]

@periodic_task(
    run_every=crontab(),
    default_retry_delay=300,
    ignore_result=True
)
def send_data():
    nurses_registered()
    nurses_registered_per_clinic()
