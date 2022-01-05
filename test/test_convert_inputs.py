'''Test that different inputs are understood'''
import pytest

@pytest.mark.parametrize("start,stop,event_count", [
  (2020, 2021, None)
])
def test_calendar_between_allows_tuple(calendars, start, stop, event_count):
    events = calendars.one_day_event_repeat_every_day.between(start, stop)
    assert len(events) == event_count
