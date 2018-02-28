from freezegun import freeze_time

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguageRelation, Languages, Main

from molo.surveys.models import MoloSurveyPage, MoloSurveySubmission
from molo.surveys.tests.test_models import create_survey

from nurseconnect.utils import (
    get_period_date_format,
    convert_string_to_boolean_list,
    get_survey_results_for_user,
)


class UtilsTestCase(TestCase):

    @freeze_time("2018-02-01")
    def test_get_period_date_format_1(self):
        self.assertEqual(
            get_period_date_format(),
            "201802"
        )

    @freeze_time("2012-12-01")
    def test_get_period_date_format_2(self):
        self.assertEqual(
            get_period_date_format(),
            "201212"
        )

    def test_convert_string_to_boolean_list_1(self):
        self.assertEqual(
            convert_string_to_boolean_list("true"),
            [True]
        )

    def test_convert_string_to_boolean_list_2(self):
        self.assertEqual(
            convert_string_to_boolean_list("true,false"),
            [True, False]
        )

    def test_convert_string_to_boolean_list_3(self):
        self.assertEqual(
            convert_string_to_boolean_list(" true, false"),
            [True, False]
        )

    def test_convert_string_to_boolean_list_4(self):
        self.assertEqual(
            convert_string_to_boolean_list("TRUE,FalSE"),
            [True, False]
        )

    def test_convert_string_to_boolean_list_5(self):
        self.assertEqual(
            convert_string_to_boolean_list("true,BANANA,false"),
            [True, False]
        )

    def test_convert_string_to_boolean_list_6(self):
        self.assertEqual(
            convert_string_to_boolean_list("false    ,     True"),
            [False, True]
        )

    def test_convert_string_to_boolean_list_7(self):
        self.assertEqual(
            convert_string_to_boolean_list("false;true"),
            []
        )


class SurveyUtilsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')

    def test_get_survey_results_for_user_1(self):
        create_survey([
            {
                "question": "The sky is blue",
                "type": 'radio',
                "choices": ["true", "false"],
                "required": True,
                "page_break": False,
            }
        ])
        survey = MoloSurveyPage.objects.first()
        survey.thank_you_text = "true"
        survey.save()
        MoloSurveySubmission.objects.create(
            page=survey, user=self.user,
            form_data='{"the-sky-is-blue": "True"}')
        self.assertEqual(
            get_survey_results_for_user(survey, self.user),
            [{
                "question": "The sky is blue",
                "user_answer": True,
                "correct_answer": True,
            }]
        )

    def test_get_survey_results_for_user_2(self):
        create_survey([
            {
                "question": "The sky is blue",
                "type": 'radio',
                "choices": ["true", "false"],
                "required": True,
                "page_break": False,
            },
            {
                "question": "The grass is purple",
                "type": 'radio',
                "choices": ["true", "false"],
                "required": True,
                "page_break": False,
            }
        ])
        survey = MoloSurveyPage.objects.first()
        survey.thank_you_text = "true,false"
        survey.save()
        MoloSurveySubmission.objects.create(
            page=survey, user=self.user,
            form_data=('{"the-sky-is-blue": "True", '
                       '"the-grass-is-purple": "True"}'))
        self.assertEqual(
            get_survey_results_for_user(survey, self.user),
            [
                {
                    "question": "The sky is blue",
                    "user_answer": True,
                    "correct_answer": True,
                },
                {
                    "question": "The grass is purple",
                    "user_answer": True,
                    "correct_answer": False,
                },
            ]
        )
