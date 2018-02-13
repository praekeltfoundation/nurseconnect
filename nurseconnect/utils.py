import datetime


def get_period_date_format():
    """
    Returns the current year and month concatenated into a string

    e.g.
    datetime.date(2018, 2, 1) -> 201802
    datetime.date(2012, 11, 29) -> 201211
    """
    return datetime.date.today().strftime('%Y%m')
