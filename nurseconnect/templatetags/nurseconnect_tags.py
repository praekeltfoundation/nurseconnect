import calendar

from django.template import Library

from molo.core.templatetags.core_tags import load_sections
from molo.profiles.models import UserProfilesSettings

from nurseconnect.utils import get_survey_results_for_user

register = Library()


@register.filter('fieldtype')
def fieldtype(field):
    return field.field.widget.__class__.__name__


@register.inclusion_tag("core/tags/footerlink.html", takes_context=True)
def footer_link(context, id):
    request = context["request"]
    locale = context.get("locale_code")

    terms = UserProfilesSettings.for_site(request.site).terms_and_conditions

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


@register.inclusion_tag("surveys/embedded_survey.html",
                        takes_context=True)
def embedded_survey_tag(context, page):
    '''
    Display the child survey of a page

    If a user has not submitted they will see the survey form
    If a user has already submitted an answer they see their results

    NOTE: This currently only works for Radio Buttons with True/False
    and uses a hack where data stored in the survey thank you text will
    store true, false string values seperated by commas. I apologise
    if you are responsible for maintaining this in the future.
    '''
    user = context['request'].user
    survey = page.get_children().first().specific

    survey_results = get_survey_results_for_user(survey, user)

    if survey_results:
        if page.get_next_sibling():
            next_article = page.get_next_sibling().specific
        else:
            next_article = None

        return {
            "survey_answered": True,
            "answers": survey_results,
            "next_article": next_article,
        }
    else:
        return {
            "survey_answered": False,
            "survey": survey
        }
