"""This file tests the issue 61.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/61

We expect DATE as the value.

    DTSTART;VALUE=DATE:20211215
    DTEND;VALUE=DATE:20211216

"""

import datetime

from pytz import timezone


def test_sequence_is_not_present(calendars):
    tz = str(calendars.raw.issue_61_time_zone_error.get("X-WR-TIMEZONE"))
    now = timezone(tz).localize(
        datetime.datetime(2021, 12, 15, 17, 41, 1, 446354)
    )  # datetime.datetime.now(timezone(tz)) # use fixed time
    events = calendars.issue_61_time_zone_error.at(now)
    assert len(events) == 1
    assert isinstance(events[0]["DTSTART"].dt, datetime.date)
