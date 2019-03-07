"""This tests the values of the event even when edited."""
import pytest
import datetime

def test_two_events_have_the_same_values(calendars):
    events = calendars.three_events_one_edited.all()
    unedited_events = [event for event in events if event["SUMMARY"] == "test7"]
    assert len(unedited_events) == 2

def test_one_event_is_edited(calendars):
    events = calendars.three_events_one_edited.all()
    edited_events = [event for event in events if event["SUMMARY"] == "test7 - edited"]
    assert len(edited_events) == 1
    edited_event = edited_events[0]
    assert edited_event["LOCATION"] == "location"

def test_three_events_total(calendars):
    events = calendars.three_events_one_edited.all()
    assert len(events) == 3

def test_edited_event_as_part_of_exdate(todo):
    """What happens when an edited event is part of the exdate?"""

def test_edited_event_as_part_of_exrule(todo):
    """What happens when an edited event is part of the exrule?"""

@pytest.mark.parametrize("date,hour", [
    ((2019, 3, 7), 2),
    ((2019, 3, 8), 1),
    ((2019, 3, 9), 3),
    ((2019, 3, 10), 2),
])
def test_event_moved_in_time(calendars, date, hour):
    events = calendars.recurring_events_moved.at(date)
    assert len(events) == 1
    event = events[0]
    assert event["DTSTART"].dt.hour == hour

@pytest.mark.parametrize("date,duration", [
    ((2019, 3, 7), datetime.timedelta(hours=1)),
    ((2019, 3, 8), datetime.timedelta(hours=2)),
    ((2019, 3, 9), datetime.timedelta(minutes=30)),
    ((2019, 3, 10), datetime.timedelta(days=1)),
])
def test_event_moved_in_time(calendars, date, duration):
    events = calendars.recurring_events_changed_duration.at(date)
    assert len(events) == 1
    event = events[0]
    assert event["DTEND"].dt - event["DTSTART"].dt == duration
