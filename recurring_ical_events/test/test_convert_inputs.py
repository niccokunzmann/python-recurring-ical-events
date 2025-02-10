"""Test that different inputs are understood

Also see test_time_arguments.py
"""

import pytest


@pytest.mark.parametrize(
    ("start", "stop", "event_count"),
    [
        (2020, 2021, 366),
        ((2020,), (2021,), 366),
        ((2019, 2), (2020, 2), 334),
        ((2019, 2, 4), (2019, 5, 21), 78),
        ("20190204", "20190521", 78),
        ("20190204T000000Z", "20190521T235959Z", 79),  # 78 = that of the day
    ],
)
def test_calendar_between_allows_tuple(calendars, start, stop, event_count):
    events = calendars.one_day_event_repeat_every_day.between(start, stop)
    assert len(events) == event_count
