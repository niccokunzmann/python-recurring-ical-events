"""Add the RECURRENCE-ID to all the resuts.

It is problematic to assume that recurrences are identified by their DTSTART.
This adds the recurrence id to the events.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/219
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest
from icalendar import Calendar, Event
from icalendar.timezone import tzp

import recurring_ical_events

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # noqa: F401, RUF100


def create_event_without_recurrence_id(
    start: date,
    rdate: timedelta | None = None,
    is_rdate: bool = False,  # noqa: FBT001
) -> Event:
    """Return"""
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


param_start = pytest.mark.parametrize(
    "start",
    [
        date(2019, 5, 15),
        datetime(2019, 5, 15),
        datetime(2019, 5, 15, 12),
        datetime(2021, 5, 15, 12, tzinfo=ZoneInfo("UTC")),
        datetime(2021, 5, 15, 12, tzinfo=ZoneInfo("Europe/Moscow")),
    ],
)


@param_start
@pytest.mark.parametrize(
    ("rdate", "is_rdate"),
    [
        (None, False),
        (timedelta(days=1), False),
        (timedelta(days=-2), True),
    ],
)
def test_recurrence_id_of_first_event(start, rdate, is_rdate):
    """Check the the events returned have the right recurrence id."""
    event = create_event_without_recurrence_id(start, rdate=rdate, is_rdate=is_rdate)
    assert get_recurrence_id_at(event, start) == start


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


def test_event_with_recurrence_id_keeps_it_in_series(calendars):
    """The event got moved."""
    events = calendars.recurring_events_moved.at("20190309")
    assert len(events) == 1
    event = events[0]
    # RECURRENCE-ID;TZID=Europe/Berlin:20190309T020000
    rid = tzp.localize(datetime(2019, 3, 9, 2), "Europe/Berlin")
    # DTSTART;TZID=Europe/Berlin:20190309T030000
    start = tzp.localize(datetime(2019, 3, 9, 3), "Europe/Berlin")
    print("start")
    print(start)
    print(event.start)
    print("rid")
    print(rid)
    print(event["RECURRENCE-ID"].dt)
    assert event.start == start
    assert event["RECURRENCE-ID"].dt == rid


def test_event_with_recurrence_id_keeps_it_standalone(calendars):
    """Test an event without rule, just recurrence id."""
    # UID:_6krj2dhl74q34b9j60sj4b9k8h238b9p6gok2ba68gojgchl6cpj0h1o88_R20231009T130000@google.com
    # RECURRENCE-ID;TZID=Europe/Paris:20240108T150000
    # DTSTART;TZID=Europe/Paris:20240108T170000
    uid = "_6krj2dhl74q34b9j60sj4b9k8h238b9p6gok2ba68gojgchl6cpj0h1o88_R20231009T130000@google.com"
    events = calendars.issue_173_only_modifications_error.at("20240108")
    event = next(event for event in events if event["UID"] == uid)
    expected = tzp.localize(datetime(2024, 1, 8, 15), "Europe/Paris")
    recid = event["RECURRENCE-ID"].dt
    print("expected", expected, "\n   start", event.start, "\n     rid", recid)
    assert recid == expected, "RECURRENCE-ID;TZID=Europe/Paris:20240108T150000"


def test_recurrence_id_defaults_to_start(calendars):
    """Test the we always have one so we can edits events."""
    event = calendars.one_event.first
    assert event.start == event["RECURRENCE-ID"].dt


def test_if_we_add_an_event_with_recurrence_id_we_edit_it(calendars):
    """Test the we always have one so we can edits events."""
    event = calendars.one_event.first
    modified = event.copy()
    del event["RECURRENCE-ID"]  # this looks like the base event
    modified["modified"] = True
    calendar = Calendar()
    calendar.add_component(event)
    calendar.add_component(modified)
    events = list(recurring_ical_events.of(calendar).all())
    print(calendar.to_ical().decode())
    assert len(events) == 1
    event = events[0]
    assert event["modified"]


def test_modify_event_with_sequence_number(calendars):
    """Test the we always have one so we can edits events."""
    calendar = calendars.raw.recurring_events_moved
    events = recurring_ical_events.of(calendar).at("20190309")
    assert len(events) == 1
    event = events[0]

    # This event happens on 2019-03-09
    assert event["SUMMARY"] == "New Event"
    assert event["SEQUENCE"]

    # The attributes can be set, just not mutated
    event["SEQUENCE"] = event.get("SEQUENCE", 0) + 1
    event["SUMMARY"] = "Modified Again!"

    # Add the modified event ot the calendar
    calendar.add_component(event)
    print(calendar.to_ical().decode())

    # Get the day again and see the modified event
    events = recurring_ical_events.of(calendar).at("20190309")
    assert len(events) == 1
    event = events[0]

    assert event["SUMMARY"] == "Modified Again!"


def test_alarm_has_no_recurrence_id(alarms):
    """Alarms usually do not have those ids."""
    a = alarms.alarm_absolute.at("20241003")
    assert len(a) == 1
    print(a[0].to_ical().decode())
    alarm = a[0].subcomponents[0]
    assert "RECURRENCE-ID" not in alarm
