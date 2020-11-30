"""These tests are for Issue 48
https://github.com/niccokunzmann/python-recurring-ical-events/issues/48

"""

import pytest
from pytz import timezone
from datetime import datetime

TZ = timezone("Europe/Lisbon")
@pytest.mark.parametrize("date,result",
        [(datetime(2020,11,2,11,15,0,0,TZ),0),
        (datetime(2020,11,2,11,31,0,0,TZ),1),
        (datetime(2020,11,2,12,0,0,0,TZ),1),
        (datetime(2020,11,2,12,1,0,0,TZ),1),
        (datetime(2020,11,2,13,0,0,0,TZ),1),
        (datetime(2020,11,2,13,1,0,0,TZ),0)
        ])
def test_event_timing(calendars,date,result):
    events = calendars.issue_48_daylight_aware_repeats.at(date)
    assert len(events) == result
