"""Check icalendar's alarms interface.

We need to check if icalendar is doinng the right thing.
Also, recurring ical events now needs to consider alarms
in a different way.
"""

def test_an_event_has_subcomponents_even_if_it_has_an_alarm(calendars):
    """We want the events to have no alarms by default."""
    events = calendars.alarm_at_start_of_event.at("20241004")
    assert len(events) == 1
    event = events[0]
    assert event.subcomponents != []
