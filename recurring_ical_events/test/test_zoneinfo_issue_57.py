"""Test that zoneinfo timezones can be used.

See also Issue https://github.com/niccokunzmann/python-recurring-ical-events/issues/57
"""

import sys
from datetime import datetime, timedelta

import pytest
import pytz
from icalendar import Calendar, Event, vDDDTypes

import recurring_ical_events
import recurring_ical_events.util


def test_zoneinfo_example_yields_events(ZoneInfo):  # noqa: N803
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
        return  # no zoneinfo
    from importlib.util import find_spec as module_exists

    if python_version <= (3, 8):
        assert module_exists("backports.zoneinfo"), (
            "zoneinfo should be installed with pip install backports.zoneinfo"
        )
    else:
        assert module_exists("zoneinfo"), "We assume that zoneinfo exists."
    assert module_exists("tzdata"), (
        "tzdata is necessary to test current time zone understanding."
    )


@pytest.mark.parametrize(
    "dt1",
    [
        datetime(2019, 4, 24, 19),
        pytz.timezone("Europe/Berlin").localize(datetime(2019, 4, 24, 19)),
        pytz.timezone("America/New_York").localize(datetime(2019, 4, 24, 19)),
    ],
)
def test_zoneinfo_consistent_conversion(calendars, dt1):
    """Make sure that the conversion function actually works."""
    dt2 = calendars.consistent_tz(dt1)
    assert dt1.year == dt2.year
    assert dt1.month == dt2.month
    assert dt1.day == dt2.day
    assert dt1.hour == dt2.hour
    assert dt1.minute == dt2.minute
    assert dt1.second == dt2.second


ATTRS = ["year", "month", "day", "hour", "minute", "second"]


@pytest.mark.parametrize(
    ("dt", "tz", "times"),
    [
        (datetime(2019, 2, 22, 4, 30), "Europe/Berlin", (2019, 2, 22, 4, 30)),
        (datetime(2019, 2, 22, 4, 30), "UTC", (2019, 2, 22, 4, 30)),
    ],
)
def test_convert_to_date(dt, tz, times, ZoneInfo):  # noqa: N803
    """Check that a datetime conversion takes place properly."""
    new = recurring_ical_events.util.convert_to_datetime(dt, ZoneInfo(tz))
    converted = ()
    for attr, _ in zip(ATTRS, times):
        converted += (getattr(new, attr),)
    assert converted == times
