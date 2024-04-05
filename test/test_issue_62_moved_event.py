"""
This tests the move of a december event.

Issue: https://github.com/niccokunzmann/python-recurring-ical-events/issues/62
"""

import pytest


def test_event_is_absent(calendars):
    """RRULE:FREQ=MONTHLY;BYDAY=-1FR"""
    events = calendars.issue_62_moved_event.at("20211231")
    assert events == []


def test_event_has_moved(calendars):
    """DTSTART;TZID=Europe/Berlin:20211217T213000"""
    events = calendars.issue_62_moved_event.at("20211217")
    assert len(events) == 1


def test_there_is_only_one_event_in_december(calendars):
    """Maybe, if we get the whole December, there might be one event."""
    events = calendars.issue_62_moved_event.at((2021, 12))
    assert len(events) == 1


@pytest.mark.parametrize(
    ("date", "summary"),
    [
        ("20230810", "All Day"),
        ("20230816", "All Day"),
        ("20230824", "All Day"),
        ("20230808", "Datetime"),
        ("20230814", "Datetime"),
        ("20230822", "Datetime"),
    ],
)
def test_event_is_present(calendars, date, summary):
    """Test that the middle event has moved"""
    events = calendars.issue_62_moved_event_2.at(date)
    assert len(events) == 1
    event = events[0]
    assert event["SUMMARY"] == summary


@pytest.mark.parametrize("date", ["20230815", "20230817"])
def test_event_is_absent_2(calendars, date):
    """We make sure that the moved event is not there."""
    events = calendars.issue_62_moved_event_2.at(date)
    assert len(events) == 0


def test_total_amount_of_events(calendars):
    """There are only 6 events!"""
    events = calendars.issue_62_moved_event_2.at((2023, 8))
    assert len(events) == 6
