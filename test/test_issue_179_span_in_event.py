"""We want to check that even if the span falls into a day long event, the event is found.

RFC 5545:

    For cases where a "VEVENT" calendar component
    specifies a "DTSTART" property with a DATE value type but no
    "DTEND" nor "DURATION" property, the event's duration is taken to
    be one day.
"""

import pytest


@pytest.mark.parametrize(
    "dt",
    [
        (1997, 11, 2, 0),
        (1997, 11, 2, 1),
    ],
)
def test_event_occurs(calendars, dt):
    """The event should occur."""
    events = calendars.issue_179_example.at(dt)
    assert len(events) == 1
