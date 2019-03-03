"""This file tests whether the time input is correctly converted."""
import pytest
from recurring_ical_events import UnfoldableCalendar
from datetime import datetime
from pytz import utc

@pytest.mark.parametrize("input,output", [
    ((2019, 1, 1), datetime(2019, 1, 1, tzinfo=utc)),
    ((2000, 12, 2), datetime(2000, 12, 2, tzinfo=utc)),
    ((2000, 12, 2, 4), datetime(2000, 12, 2, 4, tzinfo=utc)),
    ((2000, 12, 2, 4, 44), datetime(2000, 12, 2, 4, 44, tzinfo=utc)),
    ((2000, 12, 2, 4, 44, 55), datetime(2000, 12, 2, 4, 44, 55, tzinfo=utc)),
    (datetime(2001, 3, 12, tzinfo=utc), datetime(2001, 3, 12, tzinfo=utc)),
    ("20140511T000000Z", datetime(2014, 5, 11, tzinfo=utc)),
    ("20150521", datetime(2015, 5, 21, tzinfo=utc)),
])
def test_conversion(input, output):
    assert UnfoldableCalendar.to_datetime(input) == output
