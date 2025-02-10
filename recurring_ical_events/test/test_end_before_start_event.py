import pytest

from recurring_ical_events.errors import PeriodEndBeforeStart


def test_end_before_start_event(calendars):
    with pytest.raises(PeriodEndBeforeStart):
        calendars.end_before_start_event.at(2019)
