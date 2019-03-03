
from recurring_ical_events import of

def test_a_calendar_with_no_events_has_no_events(calendars):
    events = of(calendars.no_events).between((2000, 1, 1), (2099,1,1))
    assert not events

def test_a_calendar_with_one_event_has_one_event(calendars):
    events = of(calendars.one_event).between((2000, 1, 1), (2099,1,1))
    assert len(events) == 1
