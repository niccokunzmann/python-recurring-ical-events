'''
This tests the move of a december event.

Issue: https://github.com/niccokunzmann/python-recurring-ical-events/issues/62
'''

def test_event_is_absent(calendars):
    '''RRULE:FREQ=MONTHLY;BYDAY=-1FR'''
    events = calendars.issue_62_moved_event.at("20211231")
    assert events == []

def test_event_has_moved(calendars):
    '''DTSTART;TZID=Europe/Berlin:20211217T213000'''
    events = calendars.issue_62_moved_event.at("20211217")
    assert len(events) == 1

def test_there_is_only_one_event_in_december(calendars):
    '''Maybe, if we get the whole December, there might be one event.'''
    events = calendars.issue_62_moved_event.at((2021, 12))
    assert len(events) == 1

    


