"""This tests generating the right sequence number for event editing.

A computed, recurring event of a UID taking an event with a higher sequence in account,
will be of that sequence.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/223
"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from icalendar import Event


def test_sequence_number_is_not_set_for_single_events(calendars):
    """If we have singe events, they should not need a sequence number."""
    assert "SEQUENCE" not in calendars.one_event.first


@pytest.mark.parametrize(("date", "sequence"), [("20190305", 1), ("20190304", 0)])
def test_sequence_is_not_deleted(calendars, date, sequence):
    """We do not delete the sequence if it is 0."""
    events: list[Event] = calendars.issue_223_one_event_with_sequence.at(date)
    assert len(events) == 1
    event = events[0]
    assert event["SEQUENCE"] == sequence, "sequence remains in here"


def test_sequence_number_is_not_set_for_recurrence(calendars):
    """If we do not use sequences at all, we should not set them."""
    events = calendars.one_day_event_repeat_every_day.at("20190308")
    assert len(events) == 1
    event = events[0]
    assert "SEQUENCE" not in event, "is not set if not needed"


def test_sequence_number_is_highest_for_edited_event(calendars):
    """If an event was edited, it uses this sequence number."""
    events: list[Event] = calendars.issue_223_thunderbird.at("20250424")
    assert len(events) == 1
    event = events[0]
    assert event["SEQUENCE"] == 3, "2 -> 3"


def test_sequence_number_is_highest_for_base_event(calendars):
    """The base event with no modification has the highest sequence number."""
    events: list[Event] = calendars.issue_223_thunderbird.at("20250423")
    assert len(events) == 1
    event = events[0]
    assert event["SEQUENCE"] == 3, "1 -> 3"


def test_sequence_number_is_highest_for_last_event(calendars):
    """The last edited event keeps its sequence number."""
    events: list[Event] = calendars.issue_223_thunderbird.at("20250425")
    assert len(events) == 1
    event = events[0]
    assert event["SEQUENCE"] == 3, "3 -> 3"
