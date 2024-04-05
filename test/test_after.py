"""Test getting events in a specific order."""

import datetime

import pytest
import pytz


def test_a_calendar_with_no_event_has_no_events(calendars):
    """No event"""
    for _ in calendars.no_events.after(datetime.datetime(2024, 3, 30, 12, 0, 0)):
        assert False, "No event expected."


def test_a_calendar_with_events_before_has_no_events_later(calendars):
    """No event is found."""
    for _ in calendars.event_10_times.after(
        datetime.datetime(2024, 3, 30, 12, 0, 0),
    ):
        assert False, "No event expected."


def test_different_time_zones():
    """If events with different time zones are compared."""
    pytest.skip("TODO")


def test_no_event_is_returned_twice(calendars):
    """Long events should not be returned several times."""
    i = 1
    for event in calendars.after_many_events_in_order.after("20240324"):
        assert event["SUMMARY"] == f"event {i}"
        i += 1
    assert i == 8


def test_todo_with_no_dtstart():
    pytest.skip("TODO")


@pytest.mark.parametrize(
    ("date", "count"),
    [
        ("20200113", 10),
        ("20200114", 9),
        ("20200115", 8),
        ("20200116", 7),
        ("20200117", 6),
        ("20200118", 5),
        ("20200119", 4),
        ("20200120", 3),
        ("20200121", 2),
        ("20200122", 1),
        ("20200123", 0),
        (datetime.datetime(2020, 1, 19, 0, 0, 0, tzinfo=pytz.UTC), 4),
    ],
)
def test_get_events_in_series(calendars, date, count):
    """Get a few events in a series."""
    events = list(calendars.event_10_times.after(date))
    assert len(events) == count, f"{count} events expected"


def test_zero_size_event_is_included(calendars):
    """If a zero size event happens exactly at the earliest_end, then it is included."""
    event = list(calendars.zero_size_event.after("20190304T080000Z"))[0]
    assert event["DTSTART"].to_ical() == b"20190304T080000"


def test_zero_size_event_is_excluded_one_second_later(calendars):
    """If a zero size event happens exactly at the earliest_end, then it is included."""
    assert not list(calendars.zero_size_event.after("20190304T080001Z"))
