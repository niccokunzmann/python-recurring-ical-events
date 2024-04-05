"""This tests events of zero size.

In the specification, the DTSTART is the only mandatory attribute.
DTEND and DURATION are both optimal.
"""

import pytest


@pytest.mark.parametrize(
    ("date", "event_count"),
    [
        # DTSTART:20190304T080000
        ("20190303", 0),
        ("20190304", 1),
        ("20190305", 0),
        ((2019, 3, 4, 7), 0),
        ((2019, 3, 4, 8), 1),
        ((2019, 3, 4, 9), 0),
    ],
)
def test_zero_sized_events_at(calendars, date, event_count):
    events = calendars.zero_size_event.at(date)
    assert len(events) == event_count


@pytest.mark.parametrize(
    ("start", "stop", "event_count", "message"),
    [
        # DTSTART:20190304T080000
        ((2019, 3, 4, 7), (2019, 3, 4, 8), 0, "event is at end of span"),
        ((2019, 3, 4, 8), (2019, 3, 4, 9), 1, "event is at start of span"),
        ((2019, 3, 4, 8), (2019, 3, 4, 8), 1, "event is at the exact span"),
    ],
)
def test_zero_sized_events_at_2(calendars, start, stop, event_count, message):
    events = calendars.zero_size_event.between(start, stop)
    assert len(events) == event_count, message
