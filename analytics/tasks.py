from celery.task import task

from analytics.models import AnalyticsRecord
from analytics.utils import get_tracking_params


@task(ignore_result=True)
def record_behaviour(params):
    AnalyticsRecord.objects.create(**params)
