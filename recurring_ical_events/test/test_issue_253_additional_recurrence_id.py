"""A new sequence should override an older one."""

from datetime import date


def test_recurrence_id_is_not_identical_to_dtstart(calendars):
    """We have exactly two events in sequence 2.

    start 2024-07-01 duration 7 days, 0:00:00
    start 2024-07-15 duration 7 days, 0:00:00
    """
    events = list(calendars.issue_253_additional_recurrence_id.all())
    for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        print(f"start {start} duration {duration}")

    assert len(events) == 2
    assert events[0].start == date(2024, 7, 1)
    assert events[1].start == date(2024, 7, 15)
