import pytest
from datetime import date, datetime


@pytest.mark.parametrize("a_date", [
    # Year
    2019, (2019,),
    # Month
    (2019, 1),
    # Day
    (2019, 1, 1), date(2019, 1, 1), "20190101",
    # Datetime
    datetime(2019, 1, 1, 10, 0, 0)
])
def test_at_input_arguments(a_date, calendars):
    calendars.duration.at(a_date)
