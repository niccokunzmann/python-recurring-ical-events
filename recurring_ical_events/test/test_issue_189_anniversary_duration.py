"""All-day events whose DURATION is given in days or weeks.

RFC 5545 lets an anniversary (a VEVENT with a DATE start) span several
days. Its DURATION must then be a dur-day or dur-week value.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/189
"""

from datetime import date

import pytest


@pytest.mark.parametrize(
    ("summary", "expected"),
    [
        (
            "three days",
            [
                (date(2020, 2, 27), date(2020, 3, 1)),  # leap year
                (date(2021, 2, 27), date(2021, 3, 2)),
                (date(2022, 2, 27), date(2022, 3, 2)),
                (date(2023, 2, 27), date(2023, 3, 2)),
            ],
        ),
        (
            "one week",
            [
                (date(2020, 12, 28), date(2021, 1, 4)),
                (date(2021, 12, 28), date(2022, 1, 4)),
                (date(2022, 12, 28), date(2023, 1, 4)),
            ],
        ),
    ],
)
def test_end_is_start_plus_duration(calendars, summary, expected):
    events = [
        event
        for event in calendars.issue_189_anniversary_duration.all()
        if event["SUMMARY"] == summary
    ]
    assert [(e["DTSTART"].dt, e["DTEND"].dt) for e in events] == expected


@pytest.mark.parametrize(
    ("day", "summaries"),
    [
        ("20210226", []),
        ("20210227", ["three days"]),
        ("20210301", ["three days"]),
        ("20210302", []),  # DTEND is exclusive
        ("20200229", ["three days"]),
        ("20200301", []),
        ("20201227", []),
        ("20201228", ["one week"]),
        ("20210103", ["one week"]),
        ("20210104", []),
        ("20240227", []),  # past COUNT
    ],
)
def test_occurrence_covers_every_day(calendars, day, summaries):
    events = calendars.issue_189_anniversary_duration.at(day)
    assert [event["SUMMARY"] for event in events] == summaries
