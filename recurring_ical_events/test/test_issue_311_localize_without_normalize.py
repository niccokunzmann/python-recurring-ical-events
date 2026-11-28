"""A time zone with localize() but no normalize() is not a pytz time zone.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/311
"""

import datetime

import icalendar

import recurring_ical_events


class FixedOffset(datetime.tzinfo):
    """Like dateparser's StaticTzInfo: it has localize() but no normalize()."""

    def utcoffset(self, dt):
        return datetime.timedelta(hours=1)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "+01:00"

    def localize(self, dt, is_dst=False):
        return dt.replace(tzinfo=self)


CALENDAR = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:daily@example.com
DTSTART:20261101T050000Z
DURATION:PT1H
RRULE:FREQ=DAILY
END:VEVENT
END:VCALENDAR
"""


def test_query_between_dates_in_a_fixed_offset_time_zone():
    time_zone = FixedOffset()
    calendar = icalendar.Calendar.from_ical(CALENDAR)

    events = recurring_ical_events.of(calendar).between(
        datetime.datetime(2026, 11, 21, 5, tzinfo=time_zone),
        datetime.datetime(2026, 11, 21, 7, tzinfo=time_zone),
    )

    assert [event["DTSTART"].dt for event in events] == [
        datetime.datetime(2026, 11, 21, 5, tzinfo=datetime.timezone.utc)
    ]
