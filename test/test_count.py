"""Create an test the count() method.

We want to be able to count the amount of events really fast.
"""

import pytest


@pytest.mark.parametrize(
    ("calendar", "count"),
    [
        ("issue_20_exdate_ignored", 7),
        ("issue_148_ignored_exdate", 2),
        ("issue_117_until_before_dtstart", 0),
    ],
)
def test_check_count_of_calendars(calendars, calendar, count):
    """We count the events."""
    assert calendars[calendar].count() == count
