"""Keep the original recurrence dates when a range of events moves."""

from datetime import date, datetime, timedelta

import pytest
from icalendar import Calendar, Event
from icalendar.prop import vDDDTypes
from icalendar.timezone import tzp as timezone_provider

import recurring_ical_events


@pytest.mark.parametrize("kind", ["date", "floating", "UTC", "Europe/Berlin"])
@pytest.mark.parametrize("shift", [timedelta(days=-2), timedelta(days=2)])
@pytest.mark.parametrize("keep_recurrence_attributes", [False, True])
def test_range_recurrence_ids(tzp, kind, shift, keep_recurrence_attributes):
    """Each expanded event keeps the date it had before the range moved."""
    tzp()
    start = date(2026, 3, 27) if kind == "date" else datetime(2026, 3, 27, 10)
    if kind not in ("date", "floating"):
        start = timezone_provider.localize(start, kind)
    event = Event()
    event.add("UID", "range-recurrence-id")
    event.add("DTSTART", start)
    event.add("DURATION", timedelta(days=1))
    event.add("RRULE", {"FREQ": "DAILY", "COUNT": 4})
    override = Event()
    override.add("UID", event["UID"])
    override.add(
        "RECURRENCE-ID",
        start + timedelta(days=1),
        parameters={"RANGE": "THISANDFUTURE"},
    )
    override.add("DTSTART", start + timedelta(days=1) + shift)
    override.add("DURATION", timedelta(days=1))
    calendar = Calendar()
    calendar.add_component(event)
    calendar.add_component(override)
    original = calendar.to_ical()

    events = list(
        recurring_ical_events.of(
            calendar, keep_recurrence_attributes=keep_recurrence_attributes
        ).all()
    )
    assert len(events) == 4
    recurrence_ids = sorted(e["RECURRENCE-ID"].to_ical() for e in events)
    expected = sorted(
        vDDDTypes(start + timedelta(days=day)).to_ical() for day in range(4)
    )
    assert recurrence_ids == expected
    for expanded in events:
        if expanded["DTSTART"].dt != start:
            assert (
                "RANGE" in expanded["RECURRENCE-ID"].params
            ) == keep_recurrence_attributes
    assert calendar.to_ical() == original


def test_edit_one_event_after_range_move(tzp):
    """An exported occurrence can be edited without moving the whole range."""
    tzp()
    calendar = Calendar.from_ical("""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:range-edit
DTSTART:20260327T100000Z
DURATION:PT1H
RRULE:FREQ=DAILY;COUNT=4
SUMMARY:Original
END:VEVENT
BEGIN:VEVENT
UID:range-edit
RECURRENCE-ID;RANGE=THISANDFUTURE:20260328T100000Z
DTSTART:20260328T120000Z
DURATION:PT1H
SUMMARY:Moved range
END:VEVENT
END:VCALENDAR
""")
    event = recurring_ical_events.of(calendar).at("20260329")[0]
    event["SUMMARY"] = "Edited occurrence"
    event["SEQUENCE"] = 1
    calendar.add_component(event)

    events = list(recurring_ical_events.of(calendar).all())
    assert [str(e["SUMMARY"]) for e in events] == [
        "Original",
        "Moved range",
        "Edited occurrence",
        "Moved range",
    ]
    assert [e["RECURRENCE-ID"].to_ical() for e in events] == [
        b"20260327T100000Z",
        b"20260328T100000Z",
        b"20260329T100000Z",
        b"20260330T100000Z",
    ]
