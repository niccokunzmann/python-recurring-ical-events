"""Duplicated instances of the same event are returned in v3.1.0. The bug is not present in v2.1.3.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/164
"""


def test_event_is_only_returned_once(calendars):
    """We should not see the same event twice!"""
    events = calendars.issue_164_duplicated_event.at([2024, 8])
    for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        print(f"start {start} duration {duration}")
        print(event.to_ical().decode())
    assert len(events) == 2
