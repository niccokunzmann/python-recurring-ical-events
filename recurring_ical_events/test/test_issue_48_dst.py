"""
These are tests concerning issue 4
https://github.com/niccokunzmann/python-recurring-ical-events/issues/4

It seems the rrule until parameter includes the last date
https://dateutil.readthedocs.io/en/stable/rrule.html
"""

import datetime

import pytest
import pytz

chicago = pytz.timezone("America/Chicago")


@pytest.mark.parametrize(
    ("start_time", "end_time", "expected_count"),
    [
        # (
        #     chicago.localize(datetime.datetime(2020, 12, 11, 8)),
        #     chicago.localize(datetime.datetime(2020, 12, 11, 15)),
        #     4,
        # ),
        # (
        #     chicago.localize(datetime.datetime(2020, 12, 11, 9)),
        #     chicago.localize(datetime.datetime(2020, 12, 11, 15)),
        #     3,
        # ),
        (
            chicago.localize(datetime.datetime(2020, 12, 11, 10)),
            chicago.localize(datetime.datetime(2020, 12, 11, 15)),
            3,
        ),
    ],
)
def test_between(calendars, start_time, end_time, expected_count):
    events = calendars.issue_48_dst.between(start_time, end_time)
    assert len(events) == expected_count, (
        f"{expected_count} events expected between {start_time} and {end_time}"
    )
