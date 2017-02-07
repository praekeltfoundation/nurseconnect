from __future__ import absolute_import

import requests
from datetime import datetime
from collections import Counter

from celery.schedules import crontab
from celery.task import periodic_task

from django.contrib.auth.models import User

from nurseconnect.services import get_clinic_code
from nurseconnect.settings import (
    JEMBI_URL, JEMBI_USERNAME, JEMBI_PASSWORD, JEMBI)


class JembiMetricsPoster(object):
    """
    Send metrics to Jembi
    """
    def send_metric(self, data):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        requests.post(
            url=JEMBI_URL,
            headers=headers,
            json=data,
            auth=(JEMBI_USERNAME, JEMBI_PASSWORD),
            verify=False
        )


def nurses_registered():
    """Returns the number of nurses registered on the system."""
    num_nurses = User.objects.filter(is_staff=False).count()
    data = {
        "dataValues": [
            {
                "dataElement": JEMBI["num_nurses"]["dataElement"],
                "period":
                    str(datetime.now().year) + "%02d" % datetime.now().month,
                "value": str(num_nurses)
            },
        ]
    }

    JembiMetricsPoster().send_metric(data)


def nurses_registered_per_clinic():
    """ Returns the number of nurses registered per facility. """
    users = User.objects.filter(is_staff=False)

    clinic_codes = []
    for user in users:
        if hasattr(user.profile, "for_nurseconnect"):
            clinic_codes.append(user.profile.for_nurseconnect.clinic_code)
    nurses_per_facility = Counter(clinic_codes)
    metric_poster = JembiMetricsPoster()

    # nurses_per_facility = {"clinic_code": total} pairs
    for k, v in nurses_per_facility.items():
        if k:
            clinic = get_clinic_code(k)
            data = {
                "dataValues": [
                    {
                        "dataElement": JEMBI["nurses_per_facility"][
                            "dataElement"],
                        "period":
                            str(datetime.now().year) +
                            "%02d" % datetime.now().month,
                        "orgUnit": clinic[1],
                        "value": str(v)
                    },
                ]
            }
            metric_poster.send_metric(data)


@periodic_task(
    run_every=crontab(minute=0, hour=6),
    default_retry_delay=300,
    ignore_result=True
)
def send_data():
    nurses_registered()
    nurses_registered_per_clinic()
