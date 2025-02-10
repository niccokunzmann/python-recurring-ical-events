import pytest

from recurring_ical_events.errors import BadRuleStringFormat


def test_bad_rrule_until_format(calendars):
    with pytest.raises(BadRuleStringFormat, match=r"UNTIL parameter is missing"):
        calendars.bad_rrule_missing_until_event.at(2019)
