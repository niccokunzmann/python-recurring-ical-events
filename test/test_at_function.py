import pytest
from datetime import date, datetime
from icalendar import Event


@pytest.mark.parametrize("a_date,count", [
    # Year
    (2018, 3), ((2018,), 3),
    # Month
    ((2018, 1), 3),
    # Day
    ((2018, 1, 11), 1), (date(2018, 1, 11), 1), ("20180111", 1),
    # Datetime
    (datetime(2018, 1, 11, 10, 0, 0), 0)
])
def test_at_input_arguments(a_date, count, calendars):
    events = calendars.duration.at(a_date)
    assert isinstance(events, list)
    for event in events:
        assert isinstance(event, Event)
    assert len(events) == count


@pytest.mark.parametrize("a_date,count", [
    (datetime(2018, 1, 15, 9, 59, 0), 0),
    (datetime(2018, 1, 15, 10, 0, 0), 1),
    (datetime(2018, 1, 15, 11, 0, 0), 1),
    (datetime(2018, 1, 15, 13, 0, 0), 0),
    (datetime(2018, 1, 15, 13, 1, 0), 0),
])
def test_at_datetime_input(a_date, count, calendars):
    events = calendars.duration.at(a_date)
    assert len(events) == count
