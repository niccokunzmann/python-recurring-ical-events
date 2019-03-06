from recurring_ical_events import time_span_contains_event
import pytest
from datetime import datetime, date
from pytz import timezone, utc

berlin = timezone("Europe/Berlin")

@pytest.mark.parametrize(
    "span_start,span_stop,event_start,event_stop,"
    "include_start,include_stop,result,message", [

    (0, 5, 1, 3, True, True, True, "event lies inside 1"),
    (0, 5, 1, 3, False, True, True, "event lies inside 2"),
    (0, 5, 1, 3, True, False, True, "event lies inside 3"),
    (0, 5, 1, 3, False, False, True,"event lies inside 4"),

    (0, 5, -3, -1, True, True, False, "event lies before 1"),
    (0, 5, -3, -1, False, True, False, "event lies before 2"),
    (0, 5, -3, -1, True, False, False, "event lies before 3"),
    (0, 5, -3, -1, False, False, False, "event lies before 4"),

    (0, 5, 34, 41, True, True, False, "event lies after 1"),
    (0, 5, 34, 41, False, True, False, "event lies after 2"),
    (0, 5, 34, 41, True, False, False, "event lies after 3"),
    (0, 5, 34, 41, False, False, False, "event lies after 4"),

    (0, 5, 4, 6, True, True, True, "event overlaps end 1"),
    (0, 5, 4, 6, False, True, True, "event overlaps end 2"),
    (0, 5, 4, 6, True, False, False, "event overlaps end 3"),
    (0, 5, 4, 6, False, False, False, "event overlaps end 4"),

    (0, 5, -1, 2, True, True, True, "event overlaps start 1"),
    (0, 5, -1, 2, False, True, False, "event overlaps start 2"),
    (0, 5, -1, 2, True, False, True, "event overlaps start 3"),
    (0, 5, -1, 2, False, False, False, "event overlaps start 4"),

    (0, 5, -1, 7, True, True, True, "event overlaps start and end 1"),
    (0, 5, -1, 7, False, True, False, "event overlaps start and end 2"),
    (0, 5, -1, 7, True, False, False, "event overlaps start and end 3"),
    (0, 5, -1, 7, False, False, False, "event overlaps start and end 4"),

    (0, 5, 0, 4, True, True, True, "event begins at start 1"),
    (0, 5, 0, 4, False, True, True, "event begins at start 2"),
    (0, 5, 0, 4, True, False, True, "event begins at start 3"),
    (0, 5, 0, 4, False, False, True, "event begins at start 4"),

    (0, 5, 1, 5, True, True, True, "event ends at end 1"),
    (0, 5, 1, 5, False, True, True, "event ends at end 2"),
    (0, 5, 1, 5, True, False, True, "event ends at end 3"),
    (0, 5, 1, 5, False, False, True, "event ends at end 4"),

    (datetime(2019, 1, 1, 1), datetime(2019, 1, 4, 1), date(2019, 1, 2), date(2019, 1, 3), True, True, True, "date is in datetime span 1"),
    (datetime(2019, 1, 1, 1), datetime(2019, 1, 4, 1), date(2019, 1, 2), date(2019, 1, 3), False, True, True, "date is in datetime span 2"),
    (datetime(2019, 1, 1, 1), datetime(2019, 1, 4, 1), date(2019, 1, 2), date(2019, 1, 3), True, False, True, "date is in datetime span 3"),
    (datetime(2019, 1, 1, 1), datetime(2019, 1, 4, 1), date(2019, 1, 2), date(2019, 1, 3), False, False, True, "date is in datetime span 4"),

    (date(2019, 1, 3), date(2019, 1, 4), date(2019, 1, 2), date(2019, 1, 3), True, True, True, "date is in span 1"),
    (date(2019, 1, 3), date(2019, 1, 4), date(2019, 1, 2), date(2019, 1, 3), False, True, False, "date is in span 2"),
    (date(2019, 1, 3), date(2019, 1, 4), date(2019, 1, 2), date(2019, 1, 3), True, False, True, "date is in span 3"),
    (date(2019, 1, 3), date(2019, 1, 4), date(2019, 1, 2), date(2019, 1, 3), False, False, False, "date is in span 4"),

    (date(2019, 1, 4), date(2019, 1, 4), datetime(2019, 1, 2, 1), datetime(2019, 1, 4), True, True, True, "datetime is in date span start 1"),
    (date(2019, 1, 4), date(2019, 1, 4), datetime(2019, 1, 2, 1), datetime(2019, 1, 4), False, True, False, "datetime is in date span start 2"),
    (date(2019, 1, 4), date(2019, 1, 4), datetime(2019, 1, 2, 1), datetime(2019, 1, 4), True, False, True, "datetime is in date span start 3"),
    (date(2019, 1, 4), date(2019, 1, 4), datetime(2019, 1, 2, 1), datetime(2019, 1, 4), False, False, False, "datetime is in date span start 4"),

    (date(2019, 1, 4), date(2019, 1, 5), datetime(2019, 1, 4, 1), datetime(2019, 1, 4, 2), True, True, True, "datetime is in date span end 1"),
    (date(2019, 1, 4), date(2019, 1, 5), datetime(2019, 1, 4, 1), datetime(2019, 1, 4, 2), False, True, True, "datetime is in date span end 2"),
    (date(2019, 1, 4), date(2019, 1, 5), datetime(2019, 1, 4, 1), datetime(2019, 1, 4, 2), True, False, True, "datetime is in date span end 3"),
    (date(2019, 1, 4), date(2019, 1, 5), datetime(2019, 1, 4, 1), datetime(2019, 1, 4, 2), False, False, True, "datetime is in date span end 4"),

    (datetime(2019, 1, 1, 1, tzinfo=berlin), datetime(2019, 1, 4, 2, tzinfo=berlin), datetime(2019, 1, 4, 1, 10), datetime(2019, 1, 4, 1, 20), True, True, True, "without time zone is put into time zone 1"),
    (datetime(2019, 1, 1, 1, tzinfo=berlin), datetime(2019, 1, 4, 2, tzinfo=berlin), datetime(2019, 1, 4, 3, 10), datetime(2019, 1, 4, 3, 20), True, True, False, "without time zone is put into time zone 2"),
    (datetime(2019, 1, 1, 1), datetime(2019, 1, 4, 2), datetime(2019, 1, 4, 1, 10, tzinfo=berlin), datetime(2019, 1, 4, 1, 20, tzinfo=berlin), True, True, True, "without time zone is put into time zone 3"),
    (datetime(2019, 1, 1, 1), datetime(2019, 1, 4, 2), datetime(2019, 1, 4, 3, 10, tzinfo=berlin), datetime(2019, 1, 4, 3, 20, tzinfo=berlin), True, True, False, "without time zone is put into time zone 4"),

    (datetime(2019, 1, 1, 1, tzinfo=berlin), datetime(2019, 1, 1, 2, tzinfo=berlin), datetime(2019, 1, 1, 0, tzinfo=utc), datetime(2019, 1, 1, 1, tzinfo=utc), True, True, True, "comparing times from different time zones 1"),
    (datetime(2019, 1, 1, 4, tzinfo=berlin), datetime(2019, 1, 1, 5, tzinfo=berlin), datetime(2019, 1, 1, 0, tzinfo=utc), datetime(2019, 1, 1, 1, tzinfo=utc), True, True, False, "comparing times from different time zones 2"),
])
def test_time_span_inclusion(
    span_start, span_stop, event_start, event_stop, include_start, include_stop,
    result, message):
    assert time_span_contains_event(
        span_start, span_stop, event_start, event_stop,
        include_start, include_stop
        ) == result, message

def test_end_time(todo):
    """The end of the VEVENT is exclusive, see RFC5545

    Note that the "DTEND" property is
        set to July 9th, 2007, since the "DTEND" property specifies the
        non-inclusive end of the event.

    Tests:
    - We should not include an event which ends at a requested start date.
    - We should include an event which ends at an end date but is included
      in the range.
    """
