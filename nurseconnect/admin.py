import csv

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.sites import NotRegistered
from django.http import HttpResponse

from molo.profiles.admin import FrontendUsersModelAdmin, ProfileUserAdmin
from nurseconnect.admin_views import NurseConnectFrontendUsersAdminView


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class NurseConnectProfileUserAdmin(ProfileUserAdmin):
    list_display = ProfileUserAdmin.list_display + (
        "_clinic_code",
    )

    def _clinic_code(self, obj, *args, **kwargs):
        if (
                hasattr(obj, "profile") and
                hasattr(obj.profile, "for_nurseconnect") and
                obj.profile.for_nurseconnect.clinic_code
        ):
            return obj.profile.for_nurseconnect.clinic_code
        return ""


def download_as_csv(NurseConnectEndUsersModelAdmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment;filename=export.csv"
    writer = csv.writer(response)
    field_names = NurseConnectEndUsersModelAdmin.list_display
    writer.writerow(field_names)
    for obj in queryset:
        obj.username = obj.username.encode("utf-8")
        obj.date_joined = obj.date_joined.strftime("%Y-%m-%d %H:%M")
        writer.writerow(
            [getattr(obj, field) for field in field_names]
        )
    return response


download_as_csv.short_description = "Download selected as csv"


class NurseConnectEndUsersModelAdmin(FrontendUsersModelAdmin):
    menu_label = "End Users"
    menu_icon = "user"
    menu_order = 600
    add_to_settings_menu = False
    index_view_class = NurseConnectFrontendUsersAdminView
    list_display = ("username", "first_name", "last_name", "_clinic_code")

    actions = [download_as_csv]

    def _clinic_code(self, obj, *args, **kwargs):
        if hasattr(obj.profile, "for_nurseconnect") and \
                obj.profile.for_nurseconnect.clinic_code:
            return obj.profile.for_nurseconnect.clinic_code
        return ""
