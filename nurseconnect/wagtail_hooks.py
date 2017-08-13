from nurseconnect.admin import NurseConnectEndUsersModelAdmin

from wagtail.wagtailcore import hooks
from wagtail.contrib.modeladmin.options import modeladmin_register
from molo.core.models import ArticlePage
from wagtail.contrib.modeladmin.options import ModelAdmin


def wagtailmodeladmin_register_without_menu(wagtailmodeladmin_class):
    """
    Based on wagtailmodeladmin_register which performs
    three functions to ModelAdmin. Main problem with the
    default behaviour is that
    """
    instance = wagtailmodeladmin_class()

    @hooks.register("register_permissions")
    def register_permissions():
        return instance.get_permissions_for_registration()

    @hooks.register("register_admin_urls")
    def register_admin_urls():
        return instance.get_admin_urls_for_registration()


class ArticlePageModelAdmin(ModelAdmin):
    model = ArticlePage
    menu_label = "Topic of the Day"
    list_display = ("title", "promote_date", "demote_date")

    def get_queryset(self, request):
        print 'in here'
        # Return only Topic of the day articles
        queryset = ArticlePage.objects.filter(
            feature_as_topic_of_the_day=True
        ).order_by("-promote_date")
        return queryset
modeladmin_register(ArticlePageModelAdmin)
wagtailmodeladmin_register_without_menu(NurseConnectEndUsersModelAdmin)


@hooks.register('construct_main_menu')
def hide_reaction_questions_menu_item(request, menu_items):
    menu_items[:] = [
        item for item in menu_items if item.name not in
        'reaction-question-summary']
