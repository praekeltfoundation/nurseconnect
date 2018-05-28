from django.utils.http import is_safe_url
from django.views.generic import View
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseBadRequest
)


class AnalyticsRedirectView(View):
    def get(self, request, investigation_uuid, redirect_path, *args, **kwargs):
        destination = request.build_absolute_uri('/{0}'.format(redirect_path))
        allowed_hosts = [request.get_host()]

        if is_safe_url(destination, allowed_hosts=allowed_hosts):
            response = HttpResponseRedirect(destination)
            response.set_cookie('investigation_uuid', investigation_uuid)
        else:
            response = HttpResponseBadRequest('Redirect URL is unsafe')

        return response
