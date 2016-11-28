from __future__ import absolute_import

import requests
from celery.schedules import crontab
from celery.task import periodic_task
from django.contrib.auth.models import User

from raven.utils import json


def nurses_registered():
    """Returns the number of nurses registered on the system."""
    return User.objects.all().count()


@periodic_task(
    run_every=crontab(),
    default_retry_delay=300,
    ignore_result=True
)
def send_data():
    url = "https://praekelt:praekelt@npr-staging.jembi.org:5000/ws/rest/v1/" \
          "nurseconnectdataset"

    data = {
      "dataValues": [
        {
          "dataElement": "CSv1k6HyWaX",
          "period": "201601",
          "orgUnit": "Fws0A9spb9F",
          "value": str(nurses_registered())
        },
      ]
    }
    headers = {'Content-type': 'application/json'}

    requests.post(url, data=json.dumps(data), headers=headers, verify=False)
