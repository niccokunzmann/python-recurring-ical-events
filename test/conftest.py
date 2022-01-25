import pytest
import os
import icalendar
import sys
import time
try:
    import zoneinfo as _zoneinfo
except ImportError:
    try:
        import backports.zoneinfo as _zoneinfo
    except ImportError:
        _zoneinfo = None
from x_wr_timezone import CalendarWalker


HERE = os.path.dirname(__file__)
REPO = os.path.dirname(HERE)

sys.path.append(REPO)

from recurring_ical_events import of

CALENDARS_FOLDER = os.path.join(HERE, "calendars")
# set the default time zone
# see https://stackoverflow.com/questions/1301493/setting-timezone-in-python
time.tzset()

class ICSCalendars:
    """A collection of parsed ICS calendars"""

    Calendar = icalendar.Calendar

    def get_calendar(self, content):
        """Return the calendar given the content."""
        return self.Calendar.from_ical(content)

    def __getitem__(self, name):
        return getattr(self, name.replace("-", "_"))

    @property
    def raw(self):
        return ICSCalendars()

    def consistent_tz(self, dt):
        """Make the datetime consistent with the time zones used in these calendars."""
        assert dt.tzinfo is None or "pytz" in dt.tzinfo.__class__.__module__, "We need pytz time zones for now."
        return dt

for calendar_file in os.listdir(CALENDARS_FOLDER):
    calendar_path = os.path.join(CALENDARS_FOLDER, calendar_file)
    name = os.path.splitext(calendar_file)[0]
    with open(calendar_path, "rb") as file:
        content = file.read()
    @property
    def get_calendar(self, content=content):
        return self.get_calendar(content)
    attribute_name = name.replace("-", "_")
    setattr(ICSCalendars, attribute_name, get_calendar)

class Calendars(ICSCalendars):
    """Collection of calendars from recurring_ical_events"""

    def get_calendar(self, content):
        return of(ICSCalendars.get_calendar(self, content))

class ReversedCalendars(ICSCalendars):
    """All test should run in reversed item order.

    RFC5545:
        This memo imposes no ordering of properties within an iCalendar object.
    """

    def get_calendar(self, content):
        """Calendar traversing events in reversed order."""
        calendar = ICSCalendars.get_calendar(self, content)
        _walk = calendar.walk
        def walk():
            """Return properties in reversed order."""
            return reversed(_walk())
        calendar.walk = walk
        return of(calendar)


class ZoneInfoConverter(CalendarWalker):
    """Visit a calendar and change all time zones to ZoneInfo"""

    def walk_value_datetime(self, dt):
         """Chnage timezone of datetime to zoneinfo"""
         py_tz = dt.tzinfo
         if py_tz is None:
             return dt
         name = py_tz.zone #, py_tz.tzname(dt)
         new_tz = _zoneinfo.ZoneInfo(name) # create a zoneinfo from pytz time zone
         return dt.astimezone(new_tz)

class ZoneInfoCalendars(ICSCalendars):
    """Collection of calendars using zoneinfo.ZoneInfo and not pytz."""

    def __init__(self):
        assert _zoneinfo is not None, "zoneinfo must exist to use these calendars"
        self.changer = ZoneInfoConverter()

    def get_calendar(self, content):
        calendar = ICSCalendars.get_calendar(self, content)
        zoneinfo_calendar = self.changer.walk(calendar)
        if zoneinfo_calendar is calendar:
            pytest.skip("ZoneInfo not in use. Already tested..")
        return of(zoneinfo_calendar)

    def consistent_tz(self, dt):
        """To make the time zones consistent with this one, convert them to zoneinfo."""
        return self.changer.walk_value_datetime(dt)


calendar_params = [Calendars, ReversedCalendars]
if _zoneinfo is not None:
    calendar_params.append(ZoneInfoCalendars)

# for parametrizing fixtures, see https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
@pytest.fixture(params=calendar_params, scope="module")
def calendars(request):
    return request.param()

@pytest.fixture()
def todo():
    """Skip a test because it needs to be written first."""
    pytest.skip("This test is not yet implemented.")


@pytest.fixture(scope='module')
def zoneinfo():
    """Return the zoneinfo module if present, otherwise skip the test.

    Uses backports.zoneinfo or zoneinfo.
    """
    if _zoneinfo is None:
        pytest.skip("zoneinfo module not given. Use pip install backports.zoneinfo to install it.")
    return _zoneinfo


@pytest.fixture(scope='module')
def ZoneInfo(zoneinfo):
    """Shortcut for zoneinfo.ZoneInfo."""
    return zoneinfo.ZoneInfo
