from django.http import HttpResponse
from django.contrib.auth.models import User

from wagtailmodeladmin.views import IndexView

# Custom - specific to NurseConnect. Adpated from the one
# provided by molo.profiles
from nurseconnect.admin_import_export import FrontendUsersResource


class NurseConnectFrontendUsersAdminView(IndexView):
    def post(self, request, *args, **kwargs):
        drf__date_joined__gte = request.GET.get('drf__date_joined__gte')
        drf__date_joined__lte = request.GET.get('drf__date_joined__lte')
        is_active_exact = request.GET.get('is_active__exact')

        filter_list = {
            'date_joined__range': (drf__date_joined__gte,
                                   drf__date_joined__lte) if
            drf__date_joined__gte and drf__date_joined__lte else None,
            'is_active': is_active_exact
        }

        arguments = {}

        for key, value in filter_list.items():
            if value:
                arguments[key] = value

        dataset = FrontendUsersResource().export(
            User.objects.filter(is_staff=False, **arguments))

        response = HttpResponse(dataset.csv, content_type="text/csv")
        response['Content-Disposition'] = \
            'attachment;filename=frontend_users.csv'
        return response

    def get_template_names(self):
        return 'admin/frontend_users_admin_view.html'
