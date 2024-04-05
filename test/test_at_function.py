from datetime import date, datetime

import pytest


@pytest.mark.parametrize(
    ("a_date", "count"),
    [
        # Year
        (2018, 3),
        ((2018,), 3),
        # Month
        ((2018, 1), 3),
        # Day
        ((2018, 1, 11), 1),
        (date(2018, 1, 11), 1),
        ("20180111", 1),
        ((2018, 1, 9), 0),
        (date(2018, 1, 9), 0),
        ("20180109", 0),
        # Datetime
        (datetime(2018, 1, 11, 10, 0, 0), 1),
        (datetime(2018, 1, 9, 10, 0, 0), 0),
    ],
)
def test_at_input_arguments(a_date, count, calendars):
    events = calendars.duration.at(a_date)
    assert len(events) == count
