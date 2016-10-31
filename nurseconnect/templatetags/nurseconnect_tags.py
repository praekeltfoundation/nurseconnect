import calendar

from django.template import Library

from molo.core.templatetags.core_tags import load_sections

register = Library()


@register.inclusion_tag("core/tags/footerlink.html", takes_context=True)
def footer_link(context, id):
    request = context["request"]
    locale = context.get("locale_code")

    if request.site:
        pages = request.site.root_page.specific.footers()
        terms = pages.filter(title="Terms").first()
    else:
        terms = []

    return {
        "id": id,
        "terms": terms,
        "request": context["request"],
        "locale_code": locale,
    }


@register.inclusion_tag(
    "core/tags/section_listing_menu.html",
    takes_context=True
)
def section_listing_menu(context):
    locale_code = context.get("locale_code")

    return {
        "sections": load_sections(context),
        "request": context["request"],
        "locale_code": locale_code,
    }


@register.assignment_tag()
def convert_month(value):
    if value:
        return calendar.month_name[value]
    else:
        return ""
