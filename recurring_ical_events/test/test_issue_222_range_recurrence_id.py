"""Keep the original recurrence dates when a range of events moves."""

from datetime import timedelta

import pytest
from icalendar.prop import vDDDTypes

import recurring_ical_events


@pytest.mark.parametrize(
    "calendar_name",
    [
        "issue_222_range_date_backward",
        "issue_222_range_date_forward",
        "issue_222_range_floating_backward",
        "issue_222_range_floating_forward",
        "issue_222_range_utc_backward",
        "issue_222_range_utc_forward",
        "issue_222_range_berlin_backward",
        "issue_222_range_berlin_forward",
    ],
)
@pytest.mark.parametrize("keep_recurrence_attributes", [False, True])
def test_range_recurrence_ids(calendars, calendar_name, keep_recurrence_attributes):
    """Each expanded event keeps the date it had before the range moved."""
    calendar = calendars.raw[calendar_name]
    start = calendar.walk("VEVENT")[0]["DTSTART"].dt
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
        if expanded["RECURRENCE-ID"].dt != start:
            assert (
                "RANGE" in expanded["RECURRENCE-ID"].params
            ) == keep_recurrence_attributes
    assert calendar.to_ical() == original, (
        "Recurrence calculation must not change the calendar"
    )


def test_edit_one_event_after_range_move(calendars):
    """An exported occurrence can be edited without moving the whole range."""
    calendar = calendars.raw.issue_222_range_edit
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
