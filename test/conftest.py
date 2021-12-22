import pytest
import os
import icalendar
import sys
import time

sys.path.append(".")

from recurring_ical_events import of

HERE = os.path.dirname(__name__) or "test"
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
        return getattr(self, name)

    @property
    def raw(self):
        return ICSCalendars()

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


# for parametrizing fixtures, see https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
@pytest.fixture(params=[Calendars, ReversedCalendars])
def calendars(request):
    return request.param()

@pytest.fixture()
def todo():
    """Skip a test because it needs to be written first."""
    pytest.skip("This test is not yet implemented.")
