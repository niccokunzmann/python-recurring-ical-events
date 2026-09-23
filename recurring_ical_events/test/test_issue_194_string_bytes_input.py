"""Tests for Issue #194: Add string as input of of().

of() should accept str, bytes, and Path in addition to Calendar.
Inputs are parsed via icalendar.Calendar.from_ical().
"""

import datetime
from pathlib import Path

import icalendar
import pytest

import recurring_ical_events

SIMPLE_ICS = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "PRODID:-//Test//Test//EN\r\n"
    "BEGIN:VEVENT\r\n"
    "UID:test1@example.com\r\n"
    "DTSTART:20200101T100000Z\r\n"
    "DTEND:20200101T110000Z\r\n"
    "RRULE:FREQ=DAILY;COUNT=3\r\n"
    "SUMMARY:Test\r\n"
    "END:VEVENT\r\n"
    "END:VCALENDAR\r\n"
)

RECURRING_ICS = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "PRODID:-//Test//Test//EN\r\n"
    "BEGIN:VEVENT\r\n"
    "UID:recur@example.com\r\n"
    "DTSTART:20200301T090000Z\r\n"
    "DTEND:20200301T100000Z\r\n"
    "RRULE:FREQ=WEEKLY;COUNT=2\r\n"
    "SUMMARY:Weekly\r\n"
    "END:VEVENT\r\n"
    "END:VCALENDAR\r\n"
)


def _calendar():
    return icalendar.Calendar.from_ical(SIMPLE_ICS)


def test_of_accepts_string():
    events = list(recurring_ical_events.of(SIMPLE_ICS).all())
    assert len(events) == 3


def test_of_accepts_bytes():
    events = list(recurring_ical_events.of(SIMPLE_ICS.encode()).all())
    assert len(events) == 3


def test_of_accepts_calendar_still_works():
    cal = _calendar()
    events = list(recurring_ical_events.of(cal).all())
    assert len(events) == 3


def test_string_and_bytes_produce_same_results_as_calendar():
    cal = _calendar()
    from_cal = [e["UID"] for e in recurring_ical_events.of(cal).all()]
    from_str = [e["UID"] for e in recurring_ical_events.of(SIMPLE_ICS).all()]
    from_bytes = [e["UID"] for e in recurring_ical_events.of(SIMPLE_ICS.encode()).all()]
    assert from_cal == from_str == from_bytes
    # also check DTSTART values match
    dt_cal = [e["DTSTART"].dt for e in recurring_ical_events.of(cal).all()]
    dt_str = [e["DTSTART"].dt for e in recurring_ical_events.of(SIMPLE_ICS).all()]
    dt_bytes = [e["DTSTART"].dt for e in recurring_ical_events.of(SIMPLE_ICS.encode()).all()]
    assert dt_cal == dt_str == dt_bytes


def test_of_string_with_between():
    start = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
    end = datetime.datetime(2020, 1, 2, tzinfo=datetime.timezone.utc)
    events_str = list(recurring_ical_events.of(SIMPLE_ICS).between(start, end))
    events_cal = list(recurring_ical_events.of(_calendar()).between(start, end))
    assert len(events_str) == len(events_cal) == 1
    assert events_str[0]["DTSTART"].dt == events_cal[0]["DTSTART"].dt


def test_of_bytes_with_at():
    events = recurring_ical_events.of(SIMPLE_ICS.encode()).at("20200102")
    assert len(events) == 1
    events2 = recurring_ical_events.of(SIMPLE_ICS).at("20200102")
    assert len(events2) == 1
    assert events[0]["DTSTART"].dt == events2[0]["DTSTART"].dt


def test_of_string_forwards_keep_recurrence_attributes():
    cal_str_result = list(
        recurring_ical_events.of(SIMPLE_ICS, keep_recurrence_attributes=True).all()
    )
    assert len(cal_str_result) == 3
    # with keep_recurrence_attributes, RRULE should be preserved
    assert "RRULE" in cal_str_result[0]


def test_of_bytes_forwards_components():
    # Only VTODO should yield 0 for this VEVENT calendar
    events = list(recurring_ical_events.of(SIMPLE_ICS.encode(), components=["VTODO"]).all())
    assert len(events) == 0
    events2 = list(recurring_ical_events.of(SIMPLE_ICS, components=["VEVENT"]).all())
    assert len(events2) == 3


def test_of_string_forwards_skip_bad_series():
    # malformed but recoverable calendar – just verify the kwarg is forwarded without error
    events = list(recurring_ical_events.of(SIMPLE_ICS, skip_bad_series=True).all())
    assert len(events) == 3


def test_of_path(tmp_path):
    p = tmp_path / "cal.ics"
    p.write_text(SIMPLE_ICS)
    events = list(recurring_ical_events.of(p).all())
    assert len(events) == 3
    # Path result should match Calendar result
    assert [e["DTSTART"].dt for e in events] == [
        e["DTSTART"].dt for e in recurring_ical_events.of(_calendar()).all()
    ]


def test_of_invalid_string_raises():
    with pytest.raises(Exception):  # noqa: B017 - icalendar may raise various
        list(recurring_ical_events.of("NOT AN ICS FILE").all())


def test_of_invalid_bytes_raises():
    with pytest.raises(Exception):  # noqa: B017
        list(recurring_ical_events.of(b"NOT AN ICS FILE").all())


def test_of_empty_string_raises():
    with pytest.raises(Exception):  # noqa: B017
        list(recurring_ical_events.of("").all())


def test_stackoverflow_example_shorter():
    """Reproduce the StackOverflow pattern that motivated Issue #194.

    Previously users had to do:
        cal = Calendar.from_ical(ics_string)
        events = recurring_ical_events.of(cal).between(...)
    Now they can do:
        events = recurring_ical_events.of(ics_string).between(...)
    """
    ics = RECURRING_ICS
    start = datetime.datetime(2020, 3, 1, tzinfo=datetime.timezone.utc)
    end = datetime.datetime(2020, 3, 15, tzinfo=datetime.timezone.utc)
    # old way
    cal = icalendar.Calendar.from_ical(ics)
    old = list(recurring_ical_events.of(cal).between(start, end))
    # new way – string
    new_str = list(recurring_ical_events.of(ics).between(start, end))
    # new way – bytes
    new_bytes = list(recurring_ical_events.of(ics.encode()).between(start, end))
    assert len(old) == len(new_str) == len(new_bytes) == 2


def test_of_string_with_count():
    assert recurring_ical_events.of(SIMPLE_ICS).count() == 3
    assert recurring_ical_events.of(SIMPLE_ICS.encode()).count() == 3
