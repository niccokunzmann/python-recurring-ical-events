"""These are tests to make sure that the mixture of datetime and date works.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/201
"""

from datetime import date, datetime, timedelta

import pytest

from recurring_ical_events.types import Time
from recurring_ical_events.util import has_timezone, is_date, is_datetime


def test_can_calculate_times_of_issue_example(calendars, utc):
    """The example from the issue should work."""
    events = list(calendars.issue_201_mixed_datetime_and_date.all())
    assert len(events) == 1
    event = events[0]
    assert event.start == datetime(2023, 7, 24, 0, 0, tzinfo=utc)
    assert event.end == datetime(2023, 8, 17, 0, 0, tzinfo=utc)


def test_is_date(utc):
    """Identify dates."""
    assert is_date(date(2023, 7, 24))
    assert not is_date(datetime(2023, 7, 24, 0, 0, tzinfo=utc))
    assert not is_date(datetime(2023, 7, 24, 0, 0))


def test_is_datetime(utc):
    """Identify datetimes."""
    assert is_datetime(datetime(2023, 7, 24, 0, 0, tzinfo=utc))
    assert not is_datetime(date(2023, 7, 24))
    assert is_datetime(datetime(2023, 7, 24, 0, 0))


def test_has_timezone(utc):
    """Check if we have a timezone."""
    assert has_timezone(datetime(2023, 7, 24, 0, 0, tzinfo=utc))
    assert not has_timezone(datetime(2023, 7, 24, 0, 0))
    assert not has_timezone(date(2023, 7, 24))


@pytest.mark.parametrize("component", ["VEVENT", "VTODO"])
@pytest.mark.parametrize("start", ["DATE", "DATETIME", "UTC"])
@pytest.mark.parametrize("end", ["DATE", "DATETIME", "UTC", "DAYS", "HOURS"])
def test_all_possiblilities_are_considered(calendars, component, start, end):
    """All possibilities are present in the result."""
    calendars.components = [component]
    uids = {str(c["UID"]) for c in calendars.issue_201_test_matrix.all()}
    assert f"{component}-{start}-{end}" in uids


@pytest.mark.parametrize(
    ("end", "duration"),
    [
        ("DATE", timedelta(days=1)),
        ("DATETIME", timedelta(days=1, hours=4)),
        ("UTC", timedelta(days=2, hours=2)),
        ("DAYS", timedelta(days=3)),
        ("HOURS", timedelta(hours=10)),
    ],
)
def test_duration(calendars, end, duration):
    """Check the duration."""
    calendars.components = ["VEVENT", "VTODO"]
    components = [
        c for c in calendars.issue_201_test_matrix.all() if c["UID"].endswith(end)
    ]
    for component in components:
        uid = str(component["UID"])
        assert component.duration == duration, uid
        assert component.end - component.start == duration, uid


def is_datetime_without_timezone(dt: Time) -> bool:
    """Wether this has no timrzone."""
    return is_datetime(dt) and not has_timezone(dt)


def is_datetime_with_timezone(dt: Time) -> bool:
    """Wether this has no timrzone."""
    return is_datetime(dt) and has_timezone(dt)


def is_days(td: timedelta):
    """Wether this is only days, not hours."""
    return td.days != 0 and td.seconds == 0


def is_hours(td: timedelta):
    """Wether this is only days, not hours."""
    return td.seconds != 0


@pytest.mark.parametrize(
    ("uid", "check"),
    [
        ("DATE", is_date),
        ("DATETIME", is_datetime_without_timezone),
        ("UTC", is_datetime_with_timezone),
    ],
)
def test_start_is_correct(calendars, uid, check):
    """Check the start of the components."""
    components = calendars.raw.issue_201_test_matrix.walk(
        select=lambda c: c.get("UID", "--").split("-")[1] == uid
    )
    for component in components:
        assert check(component.DTSTART), f"{component['UID']}.DTSTART"


@pytest.mark.parametrize(
    ("uid", "check"),
    [
        ("DATE", is_date),
        ("DATETIME", is_datetime_without_timezone),
        ("UTC", is_datetime_with_timezone),
        ("DAYS", is_days),
        ("HOURS", is_hours),
    ],
)
def test_end_is_correct(calendars, uid, check):
    """Check the start of the components."""
    components = calendars.raw.issue_201_test_matrix.walk(
        select=lambda c: c.get("UID", "--").split("-")[2] == uid
    )
    for component in components:
        if uid in ("DAYS", "HOURS"):
            assert check(component.DURATION)
        elif component.name == "VEVENT":
            assert check(component.DTEND), f"{component['UID']}.DTEND"
        else:
            assert component.name == "VTODO"
            assert check(component.DUE), f"{component['UID']}.DUE"
