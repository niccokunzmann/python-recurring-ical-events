
from recurring_ical_events import of

def test_no_events_have_no_events(calendars):
    events = of(calendars.no_events).between((2000, 1, 1), (2099,1,1))
    assert not events
