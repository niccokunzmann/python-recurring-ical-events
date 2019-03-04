import datetime

def test_fablab_cottbus(calendars):
    """This calendar threw an exception.

        TypeError: can't compare offset-naive and offset-aware datetimes
    """
    today = datetime.datetime(2019, 3, 4, 16, 52, 10, 215209)
    one_year_ahead = today.replace(year=today.year + 1)
    one_year_before = today.replace(year=today.year - 1)
    events = calendars.fablab_cottbus.between(one_year_before, one_year_ahead)
