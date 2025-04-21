"""Imputs of different time zones should make a difference in the output"""

import datetime

import pytest
import pytz


@pytest.mark.parametrize(
    ("date", "hours", "timezone", "number_of_events", "calendar_name"),
    [
        # DTSTART;TZID=Europe/Berlin:20190304T000000
        # time zone offset 6:07:00 between Europe/Berlin and Asia/Ho_Chi_Minh
        ((2019, 3, 4), 24, "Europe/Berlin", 1, "three_events"),
        ((2019, 3, 4), 24, "America/Panama", 0, "three_events"),
        ((2019, 3, 4), 24, "Asia/Ho_Chi_Minh", 1, "three_events"),
        ((2019, 3, 4), 1, "Asia/Ho_Chi_Minh", 0, "three_events"),
        ((2019, 3, 4), 6, "Asia/Ho_Chi_Minh", 0, "three_events"),
        ((2019, 3, 4), 7, "Asia/Ho_Chi_Minh", 1, "three_events"),
        # events that have no time zone, New Year
        ((2019, 1, 1), 1, "Europe/Berlin", 1, "Germany"),
        ((2019, 1, 1), 1, "Asia/Ho_Chi_Minh", 1, "Germany"),
        ((2019, 1, 1), 1, "America/Panama", 1, "Germany"),
    ],
)
def test_include_events_if_the_time_zone_differs(
    calendars, date, hours, timezone, number_of_events, calendar_name
):
    """When the time zone is different, events can be included or
    excluded because they are in another time zone.
    """
    tzinfo = pytz.timezone(timezone)
    start = tzinfo.localize(datetime.datetime(*date))
    stop = start + datetime.timedelta(hours=hours)
    events = calendars[calendar_name].between(start, stop)
    assert len(events) == number_of_events, (
        f"in calendar {calendar_name} and {date} in {timezone}"
    )
