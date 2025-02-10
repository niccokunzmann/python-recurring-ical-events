"""This file tests whether the time input is correctly converted.

Also see test_convert_inputs.py
"""

from datetime import datetime

import pytest
from pytz import utc

from recurring_ical_events.query import CalendarQuery


@pytest.mark.parametrize(
    ("input_date", "output_datetime"),
    [
        ((2019, 1, 1), datetime(2019, 1, 1)),
        ((2000, 12, 2), datetime(2000, 12, 2)),
        ((2000, 12, 2, 4), datetime(2000, 12, 2, 4)),
        ((2000, 12, 2, 4, 44), datetime(2000, 12, 2, 4, 44)),
        ((2000, 12, 2, 4, 44, 55), datetime(2000, 12, 2, 4, 44, 55)),
        (datetime(2001, 3, 12, tzinfo=utc), datetime(2001, 3, 12, tzinfo=utc)),
        ("20140511T000000Z", datetime(2014, 5, 11)),
        ("20150521", datetime(2015, 5, 21)),
    ],
)
def test_conversion(input_date, output_datetime):
    assert CalendarQuery.to_datetime(input_date) == output_datetime
