import datetime

import pytest
from pytz import timezone

berlin = timezone("Europe/Berlin")


@pytest.mark.parametrize(
    ("date", "time"),
    [
        (
            (2019, 3, 20),
            berlin.localize(datetime.datetime(2019, 3, 20, 19)),
        ),  # winter time, UTC+1
        (
            (2019, 4, 24),
            berlin.localize(datetime.datetime(2019, 4, 24, 19)),
        ),  # summer time UTC+2
    ],
)
def test_daylight_saving_events(calendars, date, time):
    """Test the event 7uartkcnhf0elbvs8md0itrf6c@google.com."""
    event = calendars.daylight_saving_time.at(date)[0]
    expected_time = calendars.consistent_tz(time)
    print(event["UID"])
    print(event["DTEND"].dt)
    assert event["DTSTART"].dt == expected_time
