"""Add the RECURRENCE-ID to all the resuts.

It is problematic to assume that recurrences are identified by their DTSTART.
This adds the recurrence id to the events.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/219
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest
from icalendar import Event

import recurring_ical_events

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # noqa: F401, RUF100

def create_event_without_recurrence_id(start:date, rdate:timedelta|None=None, is_rdate:bool=False) -> Event:  # noqa: FBT001
    """Return """
    delta = timedelta(days=10)
    event = Event()
    rdate = start + delta
    if is_rdate:
        rdate, start = start, rdate
    event.add("DTSTART", start)
    event.add("UID", "test")
    if rdate:
        event.add("RDATE", rdate)
        print("start", start, "rdate", rdate)
    else:
        print("start", start)
    print("--- calendar ---")
    print(event.to_ical().decode())
    return event

@pytest.mark.parametrize(
    "start",
    [
        date(2019, 5, 15),
        datetime(2019, 5, 15),
        datetime(2019, 5, 15, 12),
        datetime(2021, 5, 15, 12, tzinfo=ZoneInfo("UTC")),
        datetime(2021, 5, 15, 12, tzinfo=ZoneInfo("Europe/Moscow")),
    ]
)
@pytest.mark.parametrize(
    ("rdate", "is_rdate"), [
        (None, False),
        (timedelta(days=1), False),
        (timedelta(days=-2), True),
        ]
)
def test_recurrence_id_of_first_event(start, rdate, is_rdate):
    """Check the the events returned have the right recurrence id."""
    event = create_event_without_recurrence_id(start, rdate=rdate, is_rdate=is_rdate)
    assert  get_recurrence_id_at(event, start) == start


def get_recurrence_id_at(event: Event, start: date) -> datetime:
    """Return the recurrence id of the event at the start."""
    query = recurring_ical_events.of(event)
    events = list(query.between(start - timedelta(days=1), start + timedelta(days=1)))
    assert len(events) == 1
    event = events[0]
    print("looking at", start)
    print("--- result ---")
    print(event.to_ical().decode())
    return event["RECURRENCE-ID"].dt



def test_event_with_recurrence_id_keeps_it_in_series(todo):
    pass
    
def test_event_with_recurrence_id_keeps_it_standalone(todo):
    pass