from wagtailmodeladmin.options import ModelAdminGroup
from wagtailmodeladmin.options import ModelAdmin as WagtailModelAdmin

from molo.core.models import ArticlePage
from molo.yourwords.admin import (
    YourWordsCompetitionAdmin, YourWordsCompetitionEntryAdmin)
from molo.yourwords.models import (
    YourWordsCompetition, YourWordsCompetitionEntry)


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

    list_display = ('entries', 'start_date', 'end_date', 'status',
                    'number_of_entries')
    list_filter = ('title', 'start_date', 'end_date')
    search_fields = ('title', 'content', 'description')


class MoloYourWordsCompetitionEntryModelAdmin(
        WagtailModelAdmin, YourWordsCompetitionEntryAdmin):

    model = YourWordsCompetitionEntry
    list_display = ('story_name', 'truncate_text', 'user', 'hide_real_name',
                    'submission_date', 'is_read', 'is_shortlisted',
                    'is_winner', '_convert')


class YourWordsModelAdminGroup(ModelAdminGroup):
    menu_label = 'Your Words'
    menu_icon = 'edit'
    menu_order = 300
    items = (MoloYourWordsCompetitionModelAdmin,
             MoloYourWordsCompetitionEntryModelAdmin)
