import calendar

from django.template import Library

from molo.core.templatetags.core_tags import load_sections
from molo.profiles.models import UserProfilesSettings

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


@register.inclusion_tag(
    "surveys/embedded_survey.html",
    takes_context=True
)
def embedded_survey_tag(context, page):
    # get the user
    user = context['request'].user
    survey = page.get_children().first().specific

    # get the submission
    submission = (survey.get_submission_class()
                        .objects.filter(page=survey, user=user))

    if submission:
        return {
            "survey_answered": True,
            "answers": [
                # their answer, if_correct
                {"question": "As nurses, we want children to not only survive, but thrive",
                 "user_answer": False,  "correct_answer": True},
                {"question": "As nurses, we want children to not only survive, but thrive",
                 "user_answer": True, "correct_answer": True},
            ],
            "next_article_link": "/",
        }
    else:
        return {
            "survey_answered": False,
            "survey": survey
        }
