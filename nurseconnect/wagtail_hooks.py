from nurseconnect.admin import (
    ArticlePageModelAdmin,
)
from nurseconnect.admin import NurseConnectEndUsersModelAdmin

from wagtailmodeladmin.options import wagtailmodeladmin_register
from wagtail.wagtailcore import hooks


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


wagtailmodeladmin_register(ArticlePageModelAdmin)
wagtailmodeladmin_register_without_menu(NurseConnectEndUsersModelAdmin)
