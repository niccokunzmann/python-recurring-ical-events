"""
This file contains the test cases which test that the
event uses the right class: date or datetime.
See https://github.com/niccokunzmann/python-recurring-ical-events/issues/7
"""
import pytest
import datetime
from icalendar.prop import vDatetime, vDate
from icalendar import Event

def test_can_serialize(calendars):
    """Test that the event can be serialized."""
    events = calendars.one_day_event.all()
    assert events
    event = events[0]
    string = event.to_ical()
    assert isinstance(string, bytes)

@pytest.mark.parametrize("attribute,dt_type,event_name", [
        ("dtstart", datetime.date,  "one_day_event"),
        ("dtend", datetime.date, "one_day_event"),
        ("dtstart", datetime.datetime, "one_event"),
        ("dtend", datetime.datetime, "one_event"),
    ])
@pytest.mark.parametrize("dt_or_content", [False])
def test_is_date(calendars, attribute, dt_type, event_name, dt_or_content):
    """Check the type of the attributes"""
    calendar = calendars[event_name]
    events = calendar.all()
    assert len(events) == 1
    event = events[0]
    event = Event.from_ical(event.to_ical())
    dt = event[attribute]
    assert isinstance(dt.dt, dt_type), "content of ical should match"

