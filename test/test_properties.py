"""Test the properties of events."""

import pytest


def test_event_has_summary(calendars):
    event = next(calendars.one_event.all())
    assert event["SUMMARY"] == "test1"


@pytest.mark.parametrize("attribute", ["DTSTART", "DTEND"])
def test_recurrent_events_change_start_and_end(calendars, attribute):
    events = calendars.three_events_one_edited.all()
    values = set(event[attribute] for event in events)
    assert len(values) == 3


@pytest.mark.parametrize("index", [1, 2])
def test_duration_stays_the_same(calendars, index):
    events = list(calendars.three_events_one_edited.all())
    duration1 = events[0]["DTEND"].dt - events[0]["DTSTART"].dt
    duration2 = events[index]["DTEND"].dt - events[index]["DTSTART"].dt
    assert duration1 == duration2


def test_attributes_are_created(calendars):
    """Some properties should be part of every event

    This is, even if they are not given in the event at the beginning."""
    events = calendars.discourse_no_dtend.at((2019, 1, 17))
    assert len(events) == 1
    event = events[0]
    assert "DTEND" in event
