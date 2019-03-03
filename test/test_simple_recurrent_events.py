import pytest

def test_event_is_not_included_if_it_is_later(calendars):
    events = calendars.three_events.between((2000, 1, 1), (2001,1,1))
    assert not events

def test_event_is_not_included_if_it_is_earlier(calendars):
    events = calendars.three_events.between((2099, 1, 1), (2100,1,1))
    assert not events

def test_all_events_in_time_span(calendars):
    events = calendars.three_events.between((2000, 1, 1), (2100,1,1))
    assert len(events) == 3

@pytest.mark.parametrize("count,end",[
    (0, (2019, 3, 3)),
    (1, (2019, 3, 5)),
    (2, (2019, 3, 8)),
])
def test_events_occur_after_and_before_span_end(calendars, count, end):
    events = calendars.three_events.between((2000, 1, 1), end)
    assert len(events) == count

def test_include_events_if_the_time_zone_differs(todo):
    """When the time zone is different, events can be included or
    excluded because they are in another time zone.
    This may only be a problem for tests though because users will
    probably use time zones if it really makes a difference.
    """

@pytest.mark.parametrize("count,start",[
    (3, (2019, 3, 3)),
    (2, (2019, 3, 5)),
    (1, (2019, 3, 8)),
])
def test_events_occur_after_and_before_span_start(calendars, count, start):
    events = calendars.three_events.between(start, (2100, 1, 1))
    assert len(events) == count
