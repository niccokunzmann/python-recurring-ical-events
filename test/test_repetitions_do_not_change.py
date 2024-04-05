"""The objective of this test is to ensure that repeated events can be copied
into an ICAL calendar again without multiplying themselves to wrong dates.
"""

import recurring_ical_events


def assert_event_does_not_duplicate(event):
    for i, _ in enumerate(recurring_ical_events.of(event).all()):
        assert i <= 1, event


def assert_events_do_not_duplicate(events):
    assert events
    for event in events:
        assert_event_does_not_duplicate(event)


def test_simple_event(calendars):
    """An event with no repetitions."""
    assert_events_do_not_duplicate(calendars.duration.at(2018))


def test_rdate_event(calendars):
    """An event with rdate."""
    assert_events_do_not_duplicate(calendars.rdate_hackerpublicradio.all())


def test_rrule(calendars):
    """An event with rrule and a number of events."""
    assert_events_do_not_duplicate(calendars.event_10_times.at(2020))


def test_rrule_with_exdate(calendars):
    """An event with rrule and exrule."""
    assert_events_do_not_duplicate(calendars.each_week_but_two_deleted.at(2019))


def test_exdate_is_removed_because_it_is_not_needed(calendars):
    """A repeated event removed RDATE and RRULE and as such should
    also remove the EXDATE values."""
    for event in calendars.rdate.all():
        assert "EXDATE" not in event
