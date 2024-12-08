"""Test VALARM recurrence.

VALARM is specified in RFC 5545 and RFC 9074.
See also https://github.com/niccokunzmann/python-recurring-ical-events/issues/186
"""
from datetime import datetime, timedelta, timezone

import icalendar
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
        e :icalendar.Event = a[0]
        assert len(e.alarms.times) == 1
        t = e.alarms.times[0]
        assert t.trigger == datetime(2024,10,3,13,0,0, tzinfo=timezone.utc)

def test_edited_alarm_is_moved(alarms):
    """When an absolute alarm is edited, the old one does not occur."""
    assert len(alarms.alarm_absolute_edited.at("20241004")) == 1, "New alarm is found"
    assert len(alarms.alarm_absolute_edited.at("20241003")) == 0, "Old alarm is removed"




@pytest.mark.parametrize(
    ("when", "deltas"),
    [
        ("20241003", {0, 45, 90}),
        ((2024,10,3,13), {0, 45}),
        ((2024,10,3,13,0), {0}),
        ((2024,10,3,12), set()),
        ((2024,10,3,14), {90}),
    ]
)
def test_can_find_absolute_alarm_with_repeat(alarms, when, deltas):
    """This absolute alarm has 2 repetitions in 45 min later."""
    a = alarms.alarm_absolute_repeat.at(when)
    deltas = {timedelta(minutes=m) for m in deltas}
    e_deltas = set()
    for e in a:
        assert len(e.alarms.times) == 1
        t = e.alarms.times[0]
        e_deltas.add(t.trigger - datetime(2024,10,3,13,0,0, tzinfo=timezone.utc))
    assert e_deltas == deltas


def test_collect_alarms_from_todos():
    pytest.skip("TODO")
