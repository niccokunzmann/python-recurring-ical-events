'''
It seems that the event is reported on its day and the next.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/44
'''

def test_event_is_present_where_it_should_be(calendars):
    events = calendars.issue_44_double_event.at((2020, 8, 14))
    assert len(events) == 1
    event = events[0]
    assert event["SUMMARY"] == "test2"


def test_event_is_absent_on_the_next_day(calendars):
    events = calendars.issue_44_double_event.at((2020, 8, 15))
    assert events == [], "the issue is that an event could turn up here"
