"""This tests the range parameter for ics file.

see https://github.com/niccokunzmann/python-recurring-ical-events/issues/75
"""

import pytest


@pytest.mark.parametrize(
    ("date", "summary"),
    [
        ("20240901", "ORGINAL EVENT"),
        ("20240911", "ORGINAL EVENT"),
        ("20240913", "MODIFIED EVENT"),
        ("20240915", "MODIFIED EVENT"),
        ("20240917", "MODIFIED EVENT"),
        ("20240919", "MODIFIED EVENT"),
        ("20240921", "MODIFIED EVENT"),
        ("20240923", "EDITED EVENT"),
        ("20240924", "EDITED EVENT"),  # RDATE
        ("20240925", "EDITED EVENT"),
    ],
)
def test_issue_75_RANGE_parameter(calendars, date, summary):
    events = calendars.issue_75_range_parameter.at(date)
    assert len(events) == 1, f"Expecting one event at {date}"
    event = events[0]
    assert event["SUMMARY"] == summary

# TODO: Test DTSTART and DTEND