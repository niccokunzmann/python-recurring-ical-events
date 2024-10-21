"""We want to check that even if the span falls into a day long event, the event is found."""

import pytest

@pytest.mark.parametrize(
    "dt", [
        (1997,11, 2, 0),
        (1997,11, 2, 1),
    ]
)
def test_event_occurs(calendars, dt):
    """The event should occur."""
    events = calendars.issue_179_example.at(dt)
    assert len(events) == 1
