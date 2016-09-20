from molo.core.models import ArticlePage
from wagtailmodeladmin.options import ModelAdmin as WagtailModelAdmin


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
