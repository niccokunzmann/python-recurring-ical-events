"""Imputs of different time zones should make a difference in the output"""
import pytest
import datetime
import pytz

@pytest.mark.parametrize("date,hours,timezone,number_of_events,calendar_name", [
# DTSTART;TZID=Europe/Berlin:20190304T000000
# time zone offset 6:07:00 between Europe/Berlin and Asia/Ho_Chi_Minh
    ((2019,3,4), 24, "Europe/Berlin", 1, "three_events"),
    ((2019,3,4), 24, "US/Eastern", 0, "three_events"),
    ((2019,3,4), 24, 'Asia/Ho_Chi_Minh', 1, "three_events"),
    ((2019,3,4), 1, 'Asia/Ho_Chi_Minh', 0, "three_events"),
    ((2019,3,4), 6, 'Asia/Ho_Chi_Minh', 0, "three_events"),
    ((2019,3,4), 7, 'Asia/Ho_Chi_Minh', 1, "three_events"),
# events that have no time zone, New Year
    ((2019,1,1), 1, 'Europe/Berlin', 1, "Germany"),
    ((2019,1,1), 1, 'Asia/Ho_Chi_Minh', 1, "Germany"),
    ((2019,1,1), 1, 'US/Eastern', 1, "Germany"),
])
def test_include_events_if_the_time_zone_differs(calendars, date, hours, timezone, number_of_events, calendar_name):
    """When the time zone is different, events can be included or
    excluded because they are in another time zone.
    """
    tzinfo = pytz.timezone(timezone)
    start = tzinfo.localize(datetime.datetime(*date))
    stop = start + datetime.timedelta(hours=hours)
    events = calendars[calendar_name].between(start, stop)
    if events:
        start = events[0]["DTSTART"].dt
        if isinstance(start, datetime.datetime):
            offset = start - start.replace(tzinfo=tzinfo)
            print("time zone offset {} between {} and {}".format(offset, start.tzinfo, tzinfo))
    assert len(events) == number_of_events, "in calendar {} and {} in {}".format(calendar_name, date, timezone)
