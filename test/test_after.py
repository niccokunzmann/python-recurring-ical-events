"""Test getting events in a specific order."""
import datetime
import pytest


def test_a_calendar_with_no_event_has_no_events(calendars):
    """No event"""
    for event in calendars.no_events.after(datetime.datetime(2024, 3, 30, 12, 0, 0)):
        assert False, "No event expected."


def test_a_calendar_with_events_before_has_no_events_later(calendars):
    """No event is found."""
    for event in calendars.event_10_times.after(datetime.datetime(2024, 3, 30, 12, 0, 0)):
        assert False, "No event expected."


def test_different_time_zones():
    """If events with different time zones are compared."""
    pytest.skip("TODO")


def test_no_event_is_returned_twice():
    """Long events should not be returned several times."""
    pytest.skip("TODO")


def test_input_with_time_zone():
    """When the earlied_end has a time zone."""
    pytest.skip("TODO")
