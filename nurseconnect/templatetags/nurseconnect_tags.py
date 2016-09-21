import calendar

from django.template import Library
from molo.core.models import SiteLanguage, SiteSettings

register = Library()


def get_pages(context, qs, locale):
    language = SiteLanguage.objects.filter(locale=locale).first()
    request = context["request"]
    site_settings = SiteSettings.for_site(request.site)
    if site_settings.show_only_translated_pages:
        if language and language.is_main_language:
            return [a for a in qs.live()]
        else:
            pages = []
            for a in qs:
                translation = a.get_translation_for(locale)
                if translation:
                    pages.append(translation)
            return pages
    else:
        if language and language.is_main_language:
            return [a for a in qs.live()]
        else:
            pages = []
            for a in qs:
                translation = a.get_translation_for(locale)
                if translation:
                    pages.append(translation)
                elif a.live:
                    pages.append(a)
            return pages


@register.inclusion_tag("core/tags/footerlink.html", takes_context=True)
def footer_link(context):
    request = context["request"]
    locale = context.get("locale_code")

    if request.site:
        pages = request.site.root_page.specific.footers()
        terms = pages.filter(title="Terms").first()
    else:
        terms = []

    return {
        "terms": terms,
        "request": context["request"],
        "locale_code": locale,
    }


@register.assignment_tag(takes_context=True)
def load_sections(context):
    request = context["request"]
    locale = context.get("locale_code")

    if request.site:
        qs = request.site.root_page.specific.sections()
    else:
        qs = []

    return get_pages(context, qs, locale)


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
