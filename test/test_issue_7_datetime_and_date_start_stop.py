"""
This file contains the test cases which test that the
event uses the right class: date or datetime.
See https://github.com/niccokunzmann/python-recurring-ical-events/issues/7
"""
import pytest
import datetime
from icalendar.prop import vDatetime, vDate

def test_can_serialize(calendars):
    """Test that the event can be serialized."""
    events = calendars.one_day_event.all()
    assert events
    event = events[0]
    string = event.to_ical()
    assert isinstance(string, bytes)

@pytest.mark.parametrize("attribute,dt_type,ical_type,event_name", [
        ("dtstart", datetime.date, vDate, "one_day_event"),
        ("dtend", datetime.date, vDate, "one_day_event"),
        ("dtstart", datetime.datetime, vDatetime, "one_event"),
        ("dtend", datetime.datetime, vDatetime, "one_event"),
    ])
@pytest.mark.parametrize("dt_or_content", [True, False])
def test_is_date(calendars, attribute, dt_type, ical_type,
        event_name, dt_or_content):
    """Check the type of the attributes"""
    calendar = calendars[event_name]
    events = calendar.all()
    assert len(events) == 1
    event = events[0]
    dt = event[attribute]
    if dt_or_content:
        assert isinstance(dt, ical_type), "ical type should match"
    else:
        assert isinstance(dt.dt, dt_type), "content of ical should match"

