import sys
import time
from datetime import timezone
from pathlib import Path

import dateutil
import icalendar
import pytest
import pytz

from recurring_ical_events import of

try:
    import zoneinfo as _zoneinfo
except ImportError:
    import backports.zoneinfo as _zoneinfo

HERE = Path(__file__).parent
REPO = Path(HERE).parent.parent

sys.path.append(str(REPO))


CALENDARS_FOLDER = HERE / "calendars"
# set the default time zone
# see https://stackoverflow.com/questions/1301493/setting-timezone-in-python
time.tzset()


class ICSCalendars:
    """A collection of parsed ICS calendars

    components is the argument to pass to the of function"""

    Calendar = icalendar.Calendar
    components = None
    skip_bad_series = None

    def __init__(self, tzp):
        """Create ICS calendars in a specific timezone."""
        self.tzp = tzp

    def get_calendar(self, content):
        """Return the calendar given the content."""
        self.tzp()
        return self.Calendar.from_ical(content)

    def __getitem__(self, name):
        return getattr(self, name)

    @property
    def raw(self):
        return ICSCalendars(self.tzp)

    def consistent_tz(self, dt):
        """Make the datetime consistent with the time zones used in these calendars."""
        assert dt.tzinfo is None or "pytz" in dt.tzinfo.__class__.__module__, (
            "We need pytz time zones for now."
        )
        return dt

    def _of(self, calendar):
        """Return the calendar but also with selected components."""
        kw = {}
        if self.skip_bad_series is not None:
            kw["skip_bad_series"] = self.skip_bad_series
        if self.components is not None:
            kw["components"] = self.components
        return of(calendar, **kw)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.tzp.__name__})"


_calendar_names = []
for calendar_path in CALENDARS_FOLDER.iterdir():
    content = calendar_path.read_bytes()

    @property
    def get_calendar(self, content=content):  # noqa: PLR0206
        return self.get_calendar(content)

    attribute_name = calendar_path.stem
    setattr(ICSCalendars, attribute_name, get_calendar)
    _calendar_names.append(attribute_name)


class Calendars(ICSCalendars):
    """Collection of calendars from recurring_ical_events"""

    def get_calendar(self, content):
        return self._of(ICSCalendars.get_calendar(self, content))


class ReversedCalendars(ICSCalendars):
    """All test should run in reversed item order.

    RFC5545:
        This memo imposes no ordering of properties within an iCalendar object.
    """

    def get_calendar(self, content):
        """Calendar traversing events in reversed order."""
        calendar = ICSCalendars.get_calendar(self, content)
        _walk = calendar.walk

        def walk(*args, **kw):
            """Return properties in reversed order."""
            return reversed(_walk(*args, **kw))

        calendar.walk = walk
        return self._of(calendar)


if hasattr(icalendar, "use_pytz") and hasattr(icalendar, "use_zoneinfo"):
    tzps = [icalendar.use_pytz, icalendar.use_zoneinfo]
else:
    tzps = [lambda: ...]


@pytest.fixture(params=tzps, scope="module")
def tzp(request):
    """The timezone provider supported by icalendar."""
    return request.param


# for parametrizing fixtures, see https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
@pytest.fixture(params=[Calendars, ReversedCalendars], scope="module")
def calendars(request, tzp) -> ICSCalendars:
    """The calendars we can use in the tests."""
    return request.param(tzp)


@pytest.fixture
def todo():
    """Skip a test because it needs to be written first."""
    pytest.skip("This test is not yet implemented.")


@pytest.fixture(scope="module")
def zoneinfo():
    """Return the zoneinfo module if present, otherwise skip the test.

    Uses backports.zoneinfo or zoneinfo.
    """
    return _zoneinfo


@pytest.fixture(scope="module")
def ZoneInfo(zoneinfo):
    """Shortcut for zoneinfo.ZoneInfo."""
    return zoneinfo.ZoneInfo


@pytest.fixture(
    scope="module",
    params=[pytz.utc, _zoneinfo.ZoneInfo("UTC"), timezone.utc, dateutil.tz.UTC],
)
def utc(request):
    """Return all the UTC implementations."""
    return request.param


class DoctestZoneInfo(_zoneinfo.ZoneInfo):
    """Constent ZoneInfo representation for tests."""

    def __repr__(self):
        return f"ZoneInfo(key={self.key!r})"


def doctest_print(obj):
    """doctest print"""
    if isinstance(obj, bytes):
        obj = obj.decode("UTF-8")
    print(str(obj).strip().replace("\r\n", "\n").replace("\r", "\n"))


@pytest.fixture
def env_for_doctest(monkeypatch):
    """Modify the environment to make doctests run."""
    monkeypatch.setitem(sys.modules, "zoneinfo", _zoneinfo)
    monkeypatch.setattr(_zoneinfo, "ZoneInfo", DoctestZoneInfo)
    from icalendar.timezone.zoneinfo import ZONEINFO

    monkeypatch.setattr(ZONEINFO, "utc", _zoneinfo.ZoneInfo("UTC"))
    return {
        "print": doctest_print,
        "CALENDARS": CALENDARS_FOLDER,
    }


# remove invalid names
_calendar_names.remove("end_before_start_event")
_calendar_names.sort()


@pytest.fixture(scope="module", params=_calendar_names)
def calendar_name(request) -> str:
    """All the calendar names."""
    return request.param


@pytest.fixture
def alarms(calendars) -> ICSCalendars:
    """The calendars to query for alarms.

    This modifies the calendars fixture.
    """
    calendars.components = ["VALARM"]
    return calendars
