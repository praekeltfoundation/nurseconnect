from bs4 import BeautifulSoup

from django.conf import settings
from django.utils import timezone

from google_analytics.utils import get_visitor_id


def should_ignore(request):
    if hasattr(settings, 'ANALYTICS_IGNORE_PATH'):
        exclude = [p for p in settings.ANALYTICS_IGNORE_PATH
                   if request.path.startswith(p)]
        return any(exclude)
    return False


def status_code_invalid(response):
    return not (response.status_code == 200 or response.status_code == 302)


def get_response_title(response):
    try:
        return BeautifulSoup(
            response.content, "html.parser"
        ).html.head.title.text.encode('utf-8')
    except Exception:
        return None


def get_user_uuid(request):
    if hasattr(request, 'user') and hasattr(request.user, 'profile')\
            and request.user.profile.uuid:
        return request.user.profile.uuid
    return None


def get_tracking_params(request, response, timestamp=None, visitor_uuid=None):
    '''
    Takes response and request objects
    Returns data necessary for tracking user journey
    '''
    return({
        "timestamp": timestamp or timezone.now(),
        "path": request.get_full_path() or '',
        "referer": request.META.get('HTTP_REFERER', request.GET.get('r', '')),
        "investigation_uuid": request.COOKIES.get('investigation_uuid', ''),
        "domain": request.META.get('HTTP_HOST', ''),
        "user_agent": request.META.get('HTTP_USER_AGENT', 'Unknown'),
        "title": get_response_title(response) or '',
        "user_profile_uuid": get_user_uuid(request) or '',
        "method": request.method or '',
        "visitor_uuid": visitor_uuid or ''
    })
