"""These test the support of the non-standard X-WR-TIMEZONE attribute.

See Issue 71: https://github.com/niccokunzmann/python-recurring-ical-events/issues/71
"""
import datetime
from pytz import UTC, timezone
import pytest


tz_london = timezone("Europe/London")
@pytest.mark.parametrize("a_date,event_count,message", [
    (datetime.datetime(2013, 8, 3, 19, tzinfo=UTC), 1, "Exact start of the first event."),
    (datetime.datetime(2013, 8, 3, 20, tzinfo=UTC), 1, "Middle of the first event."),
    (datetime.datetime(2013, 8, 3, 21, tzinfo=UTC), 0, "Exact end of the first event."),
    # Other time zone
    (datetime.datetime(2013, 8, 3, 20, tzinfo=tz_london), 1, "Exact start of the first event. (London)"),
    (datetime.datetime(2013, 8, 3, 21, tzinfo=tz_london), 1, "Middle of the first event. (London)"),
    (datetime.datetime(2013, 8, 3, 22, tzinfo=tz_london), 0, "Exact end of the first event. (London)"),
])
def test_events_with_x_wr_timezone_returned(calendars, a_date, event_count, message):
    """Test that X-WR-TIMEZONE influences the event results.

    Europe/London changes into summer time after March to October.
    """
    events = calendars.rdate_hackerpublicradio.at(a_date)
    assert len(events) == event_count, message
