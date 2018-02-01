from freezegun import freeze_time

from django.test import TestCase

from nurseconnect.utils import get_period_date_format


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
