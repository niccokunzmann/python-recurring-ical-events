"""
Test the DURATION property.

Not all events have an end.
Some events define no explicit end and some a DURATION.
RFC: https://www.kanzaki.com/docs/ical/duration.html

"""

import pytest


@pytest.mark.parametrize(
    ("date", "count"),
    [
        # event 3 days
        ("20180110", 1),
        ("20180111", 1),
        ("20180112", 1),
        ("20180109", 0),
        ("20180114", 0),
        # event 3 hours
        ((2018, 1, 15, 10), 1),
        ((2018, 1, 15, 11), 1),
        ((2018, 1, 15, 12), 1),
        ((2018, 1, 15, 9), 0),
        ((2018, 1, 15, 14), 0),
        # event with no duration nor end
        ((2018, 1, 20), 1),
        ((2018, 1, 19), 0),
        ((2018, 1, 21), 0),
    ],
)
def test_events_expected(date, count, calendars):
    events = calendars.duration.at(date)
    assert len(events) == count


@pytest.mark.parametrize(
    ("date", "summary", "expected_hours"),
    [
        ("20190318", "original event", 1),
        ("20190319", "edited duration", 3),
        ("20190320", "original event", 1),
    ],
)
def test_duration_is_edited(calendars, date, summary, expected_hours):
    """Test that the duration of an event can be edited."""
    events = calendars.duration_edited.at(date)
    assert len(events) == 1
    event = events[0]
    event_hours = (event["DTEND"].dt - event["DTSTART"].dt).total_seconds() / 3600
    assert summary == event["SUMMARY"], "we should have the correct event"
    assert event_hours == expected_hours, (
        "the duration is only edited in the edited event"
    )
