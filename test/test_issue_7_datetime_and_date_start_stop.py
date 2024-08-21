"""
This file contains the test cases which test that the
event uses the right class: date or datetime.
See https://github.com/niccokunzmann/python-recurring-ical-events/issues/7
"""

import datetime

import pytest
from icalendar import Event


def test_can_serialize(calendars):
    """Test that the event can be serialized."""
    event = next(calendars.one_day_event.all())
    string = event.to_ical()
    assert isinstance(string, bytes)


@pytest.mark.parametrize(
    ("attribute", "dt_type", "event_name"),
    [
        ("dtstart", datetime.date, "one_day_event"),
        ("dtend", datetime.date, "one_day_event"),
        ("dtstart", datetime.datetime, "one_event"),
        ("dtend", datetime.datetime, "one_event"),
    ],
)
def test_is_date(calendars, attribute, dt_type, event_name):
    """Check the type of the attributes"""
    event = next(calendars[event_name].all())
    event = Event.from_ical(event.to_ical())
    dt = event[attribute]
    assert isinstance(dt.dt, dt_type), "content of ical should match"
