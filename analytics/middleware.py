import uuid

from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from analytics.models import AnalyticsRecord
from analytics.utils import (
    should_ignore,
    status_code_invalid,
    get_tracking_params,
)


class AnalyticsMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if should_ignore(request) or status_code_invalid(response):
            return response

        timestamp = timezone.now()

        if 'visitor_uuid' not in request.session:
            request.session['visitor_uuid'] = uuid.uuid4().hex
        visitor_uuid = request.session['visitor_uuid']

        params = get_tracking_params(
            request, response, timestamp, visitor_uuid)
        AnalyticsRecord.objects.create(**params)

        return response
