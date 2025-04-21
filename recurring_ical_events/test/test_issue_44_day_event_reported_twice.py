"""
It seems that the event is reported on its day and the next.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/44
"""

import pytest


def test_event_is_present_where_it_should_be(calendars):
    events = calendars.issue_44_double_event.at((2020, 8, 14))
    assert len(events) == 1
    event = events[0]
    assert event["SUMMARY"] == "test2"


def test_event_is_absent_on_the_next_day(calendars):
    events = calendars.issue_44_double_event.at((2020, 8, 15))
    assert events == [], "the issue is that an event could turn up here"


def test_event_is_absent_on_the_previous_day(calendars):
    events = calendars.issue_44_double_event.at((2020, 8, 13))
    assert events == [], "the issue is that an event could turn up here"


@pytest.mark.parametrize("offset", list(range(4)))
def test_event_of_recurrence_should_behave_the_same(calendars, offset):
    """we should check that a repeated event does not have the same problem."""
    events = calendars.one_day_event_repeat_every_day.at((2019, 3, 4 + offset))
    assert len(events) == 1, (
        "Events of the the day before and after should not be mentioned."
    )
