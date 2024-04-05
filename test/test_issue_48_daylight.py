"""These tests are for Issue 48
https://github.com/niccokunzmann/python-recurring-ical-events/issues/48

These were the events occurring when the issue was raised:
    EVENT2:
    start: 2020-11-02 11:30:00+00:00
    stop:  2020-11-02 13:00:00+00:00

March to October: UTC+1
October to March: UTC+0

"""

from datetime import datetime

import pytest
from pytz import timezone

TZ = timezone("Europe/Lisbon")


@pytest.mark.parametrize(
    ("date", "event_name"),
    [
        (datetime(2020, 11, 2, 11, 15, 0, 0), 0),
        (datetime(2020, 11, 2, 11, 31, 0, 0), "EVENT2"),
        (datetime(2020, 11, 2, 12, 0, 0, 0), "EVENT2"),
        (datetime(2020, 11, 2, 12, 1, 0, 0), "EVENT2"),
        (datetime(2020, 11, 2, 12, 59, 0, 0), "EVENT2"),
        (datetime(2020, 11, 2, 13, 1, 0, 0), 0),
    ],
)
def test_event_timing(calendars, date, event_name):
    date = TZ.localize(date)
    events = calendars.issue_48_daylight_aware_repeats.at(date)
    if event_name:
        assert len(events) == 1
        assert events[0]["UID"] == event_name
    else:
        assert not events, "no events expected"
