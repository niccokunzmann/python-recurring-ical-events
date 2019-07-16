"""
This file contains the test cases which test that the
event uses the right class: date or datetime.
See https://github.com/niccokunzmann/python-recurring-ical-events/issues/7
"""


def test_can_serialize(calendars):
    """Test that the event can be serialized."""
    events = calendars.one_day_event.all()
    assert events
    event = events[0]
    string = event.to_ical()
    assert isinstance(string, str)

