"""These are tests to make sure that the mixture of datetime and date works.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/201
"""

from datetime import datetime, timezone


def test_can_calculate_times_of_issue_example(calendars):
    """The example from the issue should work."""
    events = calendars.issue_201_mixed_datetime_and_date.all()
    assert len(events) == 1
    event = events[0]
    assert event.start == datetime(2023, 7, 24, 0, 0, tzinfo=timezone("UTC"))
    assert event.end == datetime(2023, 8, 17, 0, 0, tzinfo=timezone("UTC"))
