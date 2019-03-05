"""Test the properties of events."""

import pytest

def test_event_has_summary(calendars):
    event = calendars.one_event.all()[0]
    assert event["SUMMARY"] == "test1"

@pytest.mark.parametrize("attribute", ["DTSTART", "DTEND"])
def test_recurrent_events_change_start_and_end(calendars, attribute):
    events = calendars.three_events_one_edited.all()
    print(events)
    values = set(event[attribute] for event in events)
    assert len(values) == 3

@pytest.mark.parametrize("index", [1, 2])
def test_duration_stays_the_same(calendars, index):
    events = calendars.three_events_one_edited.all()
    duration1 = events[0]["DTEND"].dt - events[0]["DTSTART"].dt
    duration2 = events[index]["DTEND"].dt - events[index]["DTSTART"].dt
    assert duration1 == duration2

def test_duration_is_edited(todo):
    """Test that the duration of an event can be edited."""

def test_attributes_are_not_copied(todo):
    """Some attributes should not be copied because they create a wrong meaning
    - rrule
    - exdate
    - rdate
    - dtend if not given
    """
