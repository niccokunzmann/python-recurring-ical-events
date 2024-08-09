"""This tests if there is a difference between macOS and Linux

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/151
"""

from datetime import datetime, timezone


def test_count_events_from_issue(calendars):
    """The number of events seems to differ from OS to OS."""

    start_time = datetime.fromtimestamp(1722564000, timezone.utc)
    end_time = datetime.fromtimestamp(1722567600, timezone.utc)
    events = calendars.issue_151_macos_linux_difference.between(start_time, end_time)
    for event in events:
        print(event["UID"], event["DTSTART"], event["SUMMARY"])
    assert len(events) == 1
