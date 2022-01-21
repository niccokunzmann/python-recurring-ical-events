"""Test that zoneinfo timezones can be used.

See also Issue https://github.com/niccokunzmann/python-recurring-ical-events/issues/57
"""
from datetime import date, datetime, timedelta

from icalendar import Calendar, Event, vDDDTypes
import recurring_ical_events


def test_zoneinfo_example_yields_events(ZoneInfo):
    """Test that there is no error.

    Source code is taken from Issue 57.
    """
    tz = ZoneInfo("Europe/London")

    cal = Calendar()
    event = Event()
    cal.add_component(event)

    dt = datetime(2021, 6, 24, 21, 15).astimezone().astimezone(tz)
    # datetime.datetime(2021, 6, 24, 21, 15, tzinfo=zoneinfo.ZoneInfo(key='Europe/London'))
    d = dt.date()

    event["dtstart"] = vDDDTypes(dt)

    events = recurring_ical_events.of(cal).between(d, d + timedelta(1))

    assert len(events) == 1, "The event was found."
