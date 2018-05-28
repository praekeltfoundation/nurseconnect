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

        visitor_id = request.COOKIES.get('visitor_id', False)
        if not visitor_id:
            response.set_cookie('visitor_id', str(uuid.uuid4()))

        params = get_tracking_params(request, response, timestamp, visitor_id)
        AnalyticsRecord.objects.create(**params)

        return response
