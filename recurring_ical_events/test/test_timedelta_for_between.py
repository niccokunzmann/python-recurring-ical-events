"""This tests that a timedelta can be used as the second argument to between.

This is useful when you do not want to calculate this yourself.
"""

from datetime import timedelta

import pytest


@pytest.mark.parametrize(
    ("start", "delta", "count"),
    [
        ("20190301", timedelta(days=3), 0),
        ("20190301", timedelta(days=5), 1),
        ("20190301", timedelta(days=3, hours=8), 0),
        ("20190301", timedelta(days=3, hours=9), 1),
        ("20190301", timedelta(days=3, hours=8, seconds=1), 1),
        ("20190304", timedelta(days=1), 1),
        ("20190304", timedelta(hours=8), 0),
        ("20190304", timedelta(hours=9), 1),
    ],
)
def test_event_with_between_and_timedelta(calendars, start, delta, count):
    """The event starts at 20190304T080000 and ends at 20190304T080000"""
    events = calendars.one_event.between(start, delta)
    assert len(events) == count
