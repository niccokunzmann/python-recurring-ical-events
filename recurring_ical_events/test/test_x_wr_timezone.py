"""These test the support of the non-standard X-WR-TIMEZONE attribute.

See Issue 71: https://github.com/niccokunzmann/python-recurring-ical-events/issues/71
"""

import datetime

import pytest
from pytz import UTC, timezone

from recurring_ical_events.util import timestamp

tz_london = timezone("Europe/London")

c1_t_utc = UTC.localize(datetime.datetime(2013, 8, 3, 19))
c1_t_london = tz_london.localize(datetime.datetime(2013, 8, 3, 20))

hour_1 = datetime.timedelta(hours=1)
hour_2 = hour_1 + hour_1


def test_dates_are_equal():
    """These dates need to be equal so that the next test 'test_events_with_x_wr_timezone_returned()' works."""
    t1 = timestamp(c1_t_utc)
    t2 = timestamp(c1_t_london)
    assert t1 == t2, f"time stamp should equal, delta {t1 - t2}"
    assert c1_t_utc == c1_t_london, "dates should equal"


c1 = "rdate_hackerpublicradio"
c2 = "x_wr_timezone_simple_events_issue_59"


@pytest.mark.parametrize(
    ("calendar_name", "a_date", "event_count", "message"),
    [
        # test c1
        #     Europe/London changes into summer time after March to October.
        #     We test with UTC as time zone
        (c1, c1_t_utc, 1, "(1) Exact start of the first event."),
        (c1, c1_t_utc + hour_1, 1, "(1) Middle of the first event."),
        (c1, c1_t_utc + hour_2, 0, "(1) Exact end of the first event."),
        #     Other time zone as argument
        (c1, c1_t_london, 1, "(2) Exact start of the first event. (London)"),
        (c1, c1_t_london + hour_1, 1, "(2) Middle of the first event. (London)"),
        (c1, c1_t_london + hour_2, 0, "(2) Exact end of the first event. (London)"),
        # test c2
        #     here, we have the dates and times of the events given
        #     test the first event
        (c2, (2021, 12, 22, 12, 0), 1, "(3) Exact start of the event. New York"),
        (c2, (2021, 12, 22, 11, 59), 0, "(3) Before the event. New York"),
        (c2, (2021, 12, 22, 12, 59), 1, "(3) Event almost over. New York"),
        (c2, (2021, 12, 22, 13, 0), 0, "(3) After the event. New York"),
        #    second event
        (c2, (2021, 12, 22, 21), 1, "(4) Exact start of the event. New York"),
        (c2, (2021, 12, 22, 20, 59), 0, "(4) Before the event. New York"),
        (c2, (2021, 12, 22, 21, 59), 1, "(4) Event almost over. New York"),
        (c2, (2021, 12, 22, 22), 0, "(4) After the event. New York"),
    ],
)
def test_events_with_x_wr_timezone_returned(
    calendars, calendar_name, a_date, event_count, message
):
    """Test that X-WR-TIMEZONE influences the event results."""
    calendar = calendars[calendar_name]
    for e in calendar.all():
        print(e.to_ical().decode("UTF-8"))
    events = calendar.at(a_date)
    assert len(events) == event_count, message
