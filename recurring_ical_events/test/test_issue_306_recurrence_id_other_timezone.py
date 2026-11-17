"""An EXDATE or RECURRENCE-ID in another time zone must only match one occurrence.

The event repeats at 09:00 and 10:00 London time (BST, UTC+1).
20220610T090000Z is 10:00 BST, so it must not match the 09:00 BST occurrence.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/306
"""

import pytest


def starts(events):
    """The start times of the events as sorted strings."""
    return sorted(
        (event["DTSTART"].dt.strftime("%Y-%m-%d %H:%M"), str(event["SUMMARY"]))
        for event in events
    )


@pytest.mark.parametrize(
    "calendar_name",
    [
        "issue_306_exdate_utc",
        "issue_306_exdate_other_timezone",
    ],
)
def test_exdate_removes_only_one_occurrence(calendars, calendar_name):
    """The EXDATE is 10:00 BST, the 09:00 BST occurrence stays."""
    events = calendars[calendar_name].between((2022, 6, 10), (2022, 6, 12))
    assert starts(events) == [
        ("2022-06-10 09:00", "twice daily"),
        ("2022-06-11 09:00", "twice daily"),
        ("2022-06-11 10:00", "twice daily"),
    ]


def test_recurrence_id_replaces_only_one_occurrence(calendars):
    """The modification replaces 10:00 BST, the 09:00 BST occurrence stays."""
    events = calendars.issue_306_recurrence_id_utc.between((2022, 6, 10), (2022, 6, 12))
    assert starts(events) == [
        ("2022-06-10 09:00", "twice daily"),
        ("2022-06-10 11:30", "moved"),
        ("2022-06-11 09:00", "twice daily"),
        ("2022-06-11 10:00", "twice daily"),
    ]


def test_floating_exdate_matches_local_time(calendars):
    """A floating EXDATE means 08:00 London time, which is no occurrence.

    It must not match the occurrence at 08:00 UTC (09:00 BST).
    """
    events = calendars.issue_306_exdate_floating_utc_digits.between(
        (2022, 6, 10), (2022, 6, 12)
    )
    assert len(events) == 4
