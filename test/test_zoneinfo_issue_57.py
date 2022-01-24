"""Test that zoneinfo timezones can be used.

See also Issue https://github.com/niccokunzmann/python-recurring-ical-events/issues/57
"""
from datetime import date, datetime, timedelta

from icalendar import Calendar, Event, vDDDTypes
import recurring_ical_events
import sys
from importlib.util import find_spec as module_exists


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


def test_zoneinfo_must_be_installed_if_it_is_possible():
    """Make sure that zoneinfo and tzdata are installed if possible."""
    python_version = sys.version_info[:2]
    if python_version < (3, 7):
        return # no zoneinfo
    if python_version <= (3, 8):
        assert module_exists("backports.zoneinfo"), "zoneinfo should be installed with pip install backports.zoneinfo"
    else:
        assert module_exists("zoneinfo"), "We assume that zoneinfo exists."
    assert module_exists("tzdata"), "tzdata is necessary to test current time zone understanding."
