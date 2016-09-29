import csv

from django.http import HttpResponse

from molo.core.models import ArticlePage
from molo.profiles.admin import FrontendUsersModelAdmin
from molo.yourwords.admin import (
    YourWordsCompetitionAdmin, YourWordsCompetitionEntryAdmin)
from molo.yourwords.models import (
    YourWordsCompetition, YourWordsCompetitionEntry)
from wagtailmodeladmin.options import ModelAdminGroup
from wagtailmodeladmin.options import ModelAdmin as WagtailModelAdmin

from nurseconnect.admin_views import NurseConnectFrontendUsersAdminView


class ArticlePageModelAdmin(WagtailModelAdmin):
    model = ArticlePage
    menu_label = "Topic of the Day"
    list_display = ("title", "promote_date", "demote_date")

    def get_queryset(self, request):
        # Return only  Topic of the day articles
        queryset = ArticlePage.objects.filter(
            feature_as_topic_of_the_day=True
        ).order_by("-promote_date")
        return queryset


class MoloYourWordsCompetitionModelAdmin(
        WagtailModelAdmin, YourWordsCompetitionAdmin):

    model = YourWordsCompetition

    list_display = ("entries", "start_date", "end_date", "status",
                    "number_of_entries")
    list_filter = ("title", "start_date", "end_date")
    search_fields = ("title", "content", "description")


class MoloYourWordsCompetitionEntryModelAdmin(
        WagtailModelAdmin, YourWordsCompetitionEntryAdmin):

    model = YourWordsCompetitionEntry
    list_display = ("story_name", "truncate_text", "user", "hide_real_name",
                    "submission_date", "is_read", "is_shortlisted",
                    "is_winner", "_convert")


class YourWordsModelAdminGroup(ModelAdminGroup):
    menu_label = "Your Words"
    menu_icon = "edit"
    menu_order = 300
    items = (MoloYourWordsCompetitionModelAdmin,
             MoloYourWordsCompetitionEntryModelAdmin)


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
