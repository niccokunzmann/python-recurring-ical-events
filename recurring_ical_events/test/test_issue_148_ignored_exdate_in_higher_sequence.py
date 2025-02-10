"""Events can be edited and a higher sequence number assigned.

In case the whole event is edited and receives a new sequence number,
the exdate should be considered.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/148
"""

from datetime import date

import pytest


def test_total_events(calendars):
    """We should remove the edited event."""
    events = list(calendars.issue_148_ignored_exdate.all())
    assert len(events) == 2


def test_the_exdate_is_not_available(calendars):
    """Make sure we do not get an event on the ecluded date."""
    events = calendars.issue_148_ignored_exdate.at("20240715")
    assert not events


@pytest.mark.parametrize(
    ("date", "summary"),
    [
        ("20240701", "test123 - edited"),
        ("20240729", "test123 - edited"),
    ],
)
def test_summary_is_modified(calendars, date, summary):
    """The summary of the edited event is used."""
    events = calendars.issue_148_ignored_exdate.at(date)
    assert events
    event = events[0]
    print(event)
    assert event["SUMMARY"] == summary


@pytest.mark.parametrize(
    ("date", "count", "message"),
    [
        ("20240701", 1, "The original event is present"),
        (
            "20240715",
            1,
            "The formerly excluded event is present after edit - EXDATE removed",
        ),
        (
            "20240717",
            0,
            "The formerly added event is removed after edit - RDATE removed",
        ),
        (
            "20240729",
            0,
            "The formerly present recurring event is now excluded - EXDATE added",
        ),
        ("20240730", 1, "Now, there is a new RDATE - RDATE added"),
    ],
)
def test_rdate_and_exdate_are_updated(calendars, date, count, message):
    """If we have RDATE and EXDATE present, we would like to update those and
    not use the old values."""
    events = calendars.issue_148_exdate_and_rdate_updated.at(date)
    print(events)
    assert len(events) == count, message


@pytest.mark.parametrize(
    ("date", "count", "message"),
    [
        ("20240701", 1, "The original event is present"),
        ("20240715", 0, "The formerly excluded event is absent"),
        ("20240717", 1, "The formerly added event is there"),
        ("20240729", 1, "The formerly present recurring event is there"),
        ("20240730", 0, "There is no RDATE, yet"),
    ],
)
def test_rdate_and_exdate_are_unedited(calendars, date, count, message):
    """If we have RDATE and EXDATE present, we would like to check the the
    value are used before edit."""
    events = calendars.issue_148_exdate_and_rdate_unedited.at(date)
    print(events)
    assert len(events) == count, message


def test_edge_case_1(calendars):
    """Check the edge case.

    Here, we do not have a modified event.
    See https://github.com/niccokunzmann/python-recurring-ical-events/issues/163#issuecomment-2301748873
    """
    events = list(calendars["issue_148_edge_case_1"].all())
    assert len(events) == 2
    starts = [event["DTSTART"].dt for event in events]
    assert date(2024, 7, 2) not in starts, "This event is not present in edge case 1"
    assert date(2024, 7, 1) in starts
    assert date(2024, 7, 29) in starts


def test_edge_case_2(calendars):
    """Check the edge case.

    This edge case shows that we have a modified event.
    See https://github.com/niccokunzmann/python-recurring-ical-events/issues/163#issuecomment-2301748873
    """
    events = list(calendars["issue_148_edge_case_2"].all())
    assert len(events) == 3
    starts = [event["DTSTART"].dt for event in events]
    assert date(2024, 7, 2) in starts
    assert date(2024, 7, 1) in starts
    assert date(2024, 7, 29) in starts
