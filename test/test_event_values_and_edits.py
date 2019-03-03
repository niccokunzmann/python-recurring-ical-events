"""This tests the values of the event even when edited."""

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
