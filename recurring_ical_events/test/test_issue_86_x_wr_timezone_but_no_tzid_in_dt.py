"""
This tests the fix present in x-wr-timezone v0.0.4.
See https://github.com/niccokunzmann/python-recurring-ical-events/issues/86

"""


def test_event_can_be_retrieved(calendars):
    event = next(calendars.issue_86_x_wr_timezone_without_time_zone_in_dt.all())
    assert event["DTSTART"].dt.tzinfo is not None, "should be replaced"
    assert event["DTSTART"].dt.tzname() == "CEST"
    assert event["DTSTART"].dt.year == 2021
    assert event["DTSTART"].dt.month == 9
    assert event["DTSTART"].dt.day == 16
    assert event["DTSTART"].dt.hour == 21
    assert event["DTSTART"].dt.minute == 0
