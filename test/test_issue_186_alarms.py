"""Test VALARM recurrence.

VALARM is specified in RFC 5545 and RFC 9074.
See also https://github.com/niccokunzmann/python-recurring-ical-events/issues/186
"""
from datetime import datetime, timezone

import pytest


@pytest.mark.parametrize(
    ("when", "count"),
    [
        ("20241003", 1),
        ((2024,10,3,13), 1),
        ((2024,10,3,13,0), 1),
        ((2024,10,3,12), 0),
        ((2024,10,3,14), 0),
    ]
)
def test_can_find_absolute_alarm(alarms, when, count):
    """Find the absolute alarm."""
    a = alarms.alarm_absolute.at(when)
    assert len(a) == count
    if count == 1:
        e = alarms[0]
        assert len(e.alarms_in_query) == 1
        a = e.alarms_in_query
        assert a.trigger == datetime(2024, 10, 3, 13, tzinfo=timezone.utc)

