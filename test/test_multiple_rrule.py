from datetime import date


def test_multiple_rrule(calendars):
    events = calendars.multiple_rrule.at(2023)
    assert len(events) == 20 + 2
    event_dstarts = [event["DTSTART"].dt.date() for event in events]
    assert date(2023, 2, 9) in event_dstarts
    assert date(2023, 2, 13) in event_dstarts
    assert date(2023, 2, 16) in event_dstarts
    assert date(2023, 3, 13) in event_dstarts
