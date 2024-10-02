"""Test VALARM recurrence.

VALARM is specified in RFC 5545 and RFC 9074.
See also https://github.com/niccokunzmann/python-recurring-ical-events/issues/186
"""
from datetime import datetime, timedelta, timezone

from icalendar import vDatetime, vDuration


def utc(s_dt:str, tzid:str, delta:str) -> vDatetime:
    """Return the datetime of the trigger in UTC."""
    dt : datetime = vDatetime.from_ical(s_dt, tzid)
    _delta : timedelta = vDuration.from_ical(delta)
    return vDatetime(dt.astimezone(timezone.utc) - _delta)

def test_simple_alarm(alarms):
    """This alarm takes place 15 minutes before the event."""
    alarm = alarms.alarm_15_min_before_event_snoozed.first
    assert alarm["TRIGGER"] == utc("20241002T110000", "Europe/London", "-PT15M")

def test_alarm_snoozed(alarms):
    """The alarm is snoozed."""
    alarm = alarms.alarm_15_min_before_event_snoozed.first
    assert alarm["X-SNOOZED"]

def test_alarm_is_not_snoozed(alarms):
    """The alarm is snoozed."""
    alarm = alarms.alarm_at_start_of_event.first
    assert not alarm["X-SNOOZED"]

