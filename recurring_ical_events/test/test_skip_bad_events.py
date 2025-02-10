from datetime import date

import pytest

from recurring_ical_events import of
from recurring_ical_events.errors import InvalidCalendar


@pytest.mark.parametrize(
    ("calendar_name", "start", "end"),
    [
        ("end_before_start_event", date(2019, 1, 1), date(2019, 12, 31)),
        ("bad_rrule_missing_until_event", date(2019, 3, 1), date(2019, 12, 31)),
    ],
)
def test_skip_bad_events(calendars, calendar_name, start, end):
    calendar = calendars.raw[calendar_name]
    with pytest.raises(InvalidCalendar):
        rcalendar = of(calendar, skip_bad_series=False)
        rcalendar.between(start, end)

    rcalendar = of(calendar, skip_bad_series=True)
    rcalendar.between(start, end)
