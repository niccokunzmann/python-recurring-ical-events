from pytz import timezone
import datetime
import pytest

berlin = timezone("Europe/Berlin")

@pytest.mark.parametrize("date,time", [
    ((2019,3,20), berlin.localize(datetime.datetime(2019, 3, 20, 19))),
    ((2019,4,24), berlin.localize(datetime.datetime(2019, 4, 24, 19))),
])
def test_daylight_saving_events(calendars, date, time):
    event = calendars.daylight_saving_time.at(date)[0]
    assert event["DTSTART"].dt == time
