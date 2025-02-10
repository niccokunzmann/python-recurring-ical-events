"""Test that some attributes of the calendar objects
are kept if required.

See Issue 23 https://github.com/niccokunzmann/python-recurring-ical-events/issues/23.
"""

import pytest

from recurring_ical_events import of

RRULE = b"FREQ=DAILY;UNTIL=20160320T030000Z"
RDATE = b"20150705T190000Z"
EXDATE = b"20150705T190000Z"


class Default:
    @staticmethod
    def to_ical():
        return None


@pytest.mark.parametrize(
    ("keywords", "rrule", "rdate", "exdate"),
    [
        ({}, None, None, None),
        ({"keep_recurrence_attributes": False}, None, None, None),
        ({"keep_recurrence_attributes": True}, RRULE, RDATE, EXDATE),
    ],
)
def test_keep_recurrence_attributes_default(calendars, keywords, rrule, rdate, exdate):
    calendar = calendars.raw.rdate2
    rcalendar = of(calendar, **keywords)
    events = rcalendar.at(2014)
    assert events
    for event in events:
        assert event.get("RRULE", Default).to_ical() == rrule
        assert event.get("RDATE", Default).to_ical() == rdate
        assert event.get("EXDATE", Default).to_ical() == exdate
