from recurring_ical_events.constants import DATE_MAX


def test_a_calendar_with_no_events_has_no_events(calendars):
    events = calendars.no_events.between((2000, 1, 1), DATE_MAX)
    assert not events


def test_a_calendar_with_one_event_has_one_event(calendars):
    events = calendars.one_event.between((2000, 1, 1), DATE_MAX)
    assert len(events) == 1


def test_event_is_not_included_if_it_is_later(calendars):
    events = calendars.one_event.between((2000, 1, 1), (2001, 1, 1))
    assert not events


def test_event_is_not_included_if_it_is_earlier(calendars):
    events = calendars.one_event.between((2030, 1, 1), DATE_MAX)
    assert not events


def test_all_events(calendars):
    assert len(list(calendars.one_event.all())) == 1
    assert len(list(calendars.no_events.all())) == 0
