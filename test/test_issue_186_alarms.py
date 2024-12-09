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


def test_series_of_events_with_alarms_but_alarm_removed():
    pytest.skip("TODO")


def test_series_of_events_with_alarms_but_alarm_removed_relative_to_end():
    pytest.skip("TODO")


def test_series_of_events_with_alarms_but_alarm_edited():
    pytest.skip("TODO")


def test_series_of_events_with_alarms_but_alarm_edited_relative_to_end():
    pytest.skip("TODO")


def test_series_of_events_with_alarm_relative_to_end():
    pytest.skip("TODO")


@pytest.mark.parametrize(
    ("dt", "trigger"),
    
    [
        ("20241126", datetime(2024, 11, 26, 13, 0, 0)),
        ("20241127", datetime(2024, 11, 27, 13, 0, 0)),
        ("20241128", datetime(2024, 11, 28, 13, 0, 0)),
        ("20241129", datetime(2024, 11, 29, 13, 0, 0)),
        # narrow it down
        ((2024, 11, 28, 12), None),
        ((2024, 11, 28, 12, 30), None),
        ((2024, 11, 28, 13), datetime(2024, 11, 28, 13, 0, 0)),
        ((2024, 11, 28, 13, 0), datetime(2024, 11, 28, 13, 0, 0)),
        ((2024, 11, 28, 13, 0, 0), datetime(2024, 11, 28, 13, 0, 0)),
        ((2024, 11, 28, 13, 0, 1), None),
        ((2024, 11, 28, 14), None),
    ]
)
def test_series_of_event_with_alarm_relative_to_start(alarms, dt, trigger):
    """This series of events all are preceded by an alarm.

    The alarm occurs 1h before the event starts.
    In this test, we narrow down our query time to make sure we find it.
    """
    a = alarms.alarm_recurring_and_acknowledged_at_2024_11_27_16_27.at(dt)
    if trigger is None:
        assert len(a) == 0
        return
    assert len(a) == 1, f"{dt} has {len(a)} alarms"
    event = a[0]
    assert len(event.alarms.times) == 1
    only_trigger = event.alarms.times[0].trigger
    assert only_trigger.replace(tzinfo=None) == trigger
    assert icalendar.timezone.tzid_from_dt(only_trigger) == "Europe/London"


def test_find_alarm_that_is_a_week_before_the_event():
    pytest.skip("TODO")


def test_alarm_without_trigger_is_ignored_as_invalid():
    pytest.skip("TODO")


def test_event_is_not_modified_with_2_alarms(alarms):
    """The base event should not be modified."""
    q = alarms.alarm_1_week_before_event
    assert len(q.at("20241202")) == 1, "We find the alarm"
    assert len(q.at("20241202")) == 1, "We find the alarm again"
    assert len(q.at("20241207")) == 1, "We also find the other alarm"


def test_repeating_event_is_not_modified_with_repeating_alarm(alarms):
    """The base event should not be modified."""
    q = alarms.alarm_absolute_repeat
    assert len(list(q.all())) == 3, "We find the alarms"
    assert len(list(q.all())) == 3, "We find the alarm again"


def test_repeating_event_is_not_modified(alarms):
    """The base event should not be modified."""
    q = alarms.alarm_recurring_and_acknowledged_at_2024_11_27_16_27
    assert len(q.between("20241126", "20241130")) == 4, "We find the alarms"
    assert len(q.between("20241126", "20241130")) == 4, "We find the alarm again"
