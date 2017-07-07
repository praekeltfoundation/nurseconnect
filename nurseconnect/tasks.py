from __future__ import absolute_import

import requests
import logging
from datetime import datetime
from collections import Counter

from celery.schedules import crontab
from celery.task import periodic_task
from celery.signals import celeryd_init

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command

from nurseconnect.services import get_clinic_code

from wagtail.wagtailsearch.backends.db import DBSearch
from wagtail.wagtailsearch.backends import get_search_backend

logger = logging.getLogger("nurseconnect.services")


class JembiMetricsPoster(object):
    """
    Send metrics to Jembi
    """
    def send_metric(self, data):
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        if all([
            settings.JEMBI_URL, settings.JEMBI_USERNAME,
            settings.JEMBI_PASSWORD
        ]):
            result = requests.post(
                url=settings.JEMBI_URL,
                headers=headers,
                json=data,
                auth=(settings.JEMBI_USERNAME, settings.JEMBI_PASSWORD),
                verify=False
            )
            result.raise_for_status()
        else:
            logger.warn(
                "The JEMBI_URL, JEMBI_PASSWORD and/or JEMBI_USERNAME "
                "environment variables are not configured"
            )


def nurses_registered():
    """Returns the number of nurses registered on the system."""
    num_nurses = User.objects.filter(is_staff=False).count()
    data = {
        "dataValues": [
            {
                "dataElement": settings.JEMBI["num_nurses"]["dataElement"],
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
        clinic = get_clinic_code(k)
        if clinic is not None:
            data = {
                "dataValues": [
                    {
                        "dataElement": settings.JEMBI["nurses_per_facility"][
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


@celeryd_init.connect
def ensure_search_index_updated(sender, instance, **kwargs):
    '''
    Run update_index when celery starts
    '''
    if not isinstance(get_search_backend(), DBSearch):
        call_command('update_index')
