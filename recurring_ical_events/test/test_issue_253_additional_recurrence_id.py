"""A new sequence should override an older one."""

from datetime import date, datetime, timezone

import pytest

from recurring_ical_events.util import convert_to_date_range


def test_calendar_from_issue(calendars):
    """We have exactly two events in sequence 2.

    start 2024-07-01 duration 7 days, 0:00:00
    start 2024-07-15 duration 7 days, 0:00:00
    """
    events = list(calendars.issue_253_additional_recurrence_id.at((2024, 7)))
    for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        print(f"start {start} duration {duration}")

    assert len(events) == 2
    assert events[0].start == date(2024, 7, 1)
    assert events[1].start == date(2024, 7, 15)


def test_edge_case_1(calendars):
    """Modified edge case

    Although the old core has a recurrence id, it should not be returned.

    Dates stay the same.
    start 2024-07-01 duration 7 days, 0:00:00
    start 2024-07-15 duration 7 days, 0:00:00
    """
    events = sorted(
        calendars.issue_253_edge_case_1.at((2024, 7)), key=lambda e: e.start
    )
    for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        print(f"start {start} duration {duration} symmary: {event['SUMMARY']}")

    assert len(events) == 2
    assert events[0].start == date(2024, 7, 1)
    assert events[1].start == date(2024, 7, 29)

    assert events[0]["SUMMARY"] == "event 2"
    assert events[1]["SUMMARY"] == "event 1"


def test_edge_case_2(calendars):
    """Modified edge case

    > The first event should not be ignored if, for example, it had
    > RECURRENCE-ID;VALUE=DATE:20240715 or had not RECURRENCE-ID at all like in #164

    Dates differ
    start 2024-07-01 duration 7 days, 0:00:00
    start 2024-07-29 duration 7 days, 0:00:00
    """
    events = sorted(
        calendars.issue_253_edge_case_1.at((2024, 7)), key=lambda e: e.start
    )
    for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        print(f"start {start} duration {duration} symmary: {event['SUMMARY']}")

    assert len(events) == 2
    assert events[0].start == date(2024, 7, 1)
    assert events[1].start == date(2024, 7, 29)


@pytest.mark.parametrize(
    ("dt", "start", "stop"),
    [
        (datetime(2024, 1, 2, 3, 4), datetime(2024, 1, 2), datetime(2024, 1, 3)),
        (
            datetime(2025, 12, 31, 3, 4, tzinfo=timezone.utc),
            datetime(2025, 12, 31, tzinfo=timezone.utc),
            datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        ),
        (
            datetime(1990, 2, 1, 23, 59, 59),
            datetime(1990, 2, 1, 0, 0, 0),
            datetime(1990, 2, 2),
        ),
        (date(1993, 2, 23), date(1993, 2, 23), date(1993, 2, 24)),
    ],
)
def test_convert_to_date_range(dt, start, stop):
    """Test converting the date range."""
    date_range = convert_to_date_range(dt)
    assert date_range == (start, stop)
