import pytest
import os
import icalendar
import sys

sys.path.append(".")

from recurring_ical_events import of

HERE = os.path.dirname(__name__) or "test"
CALENDARS_FOLDER = os.path.join(HERE, "calendars")

class Calendars:
    """Collection of calendars"""

    Calendar = icalendar.Calendar

    def get_calendar(self, content):
        """Return the calendar given the content."""
        return self.Calendar.from_ical(content)


for calendar_file in os.listdir(CALENDARS_FOLDER):
    calendar_path = os.path.join(CALENDARS_FOLDER, calendar_file)
    name = os.path.splitext(calendar_file)[0]
    with open(calendar_path, "rb") as file:
        content = file.read()
    @property
    def get_calendar(self, content=content):
        return of(self.get_calendar(content))
    attribute_name = name.replace("-", "_")
    setattr(Calendars, attribute_name, get_calendar)

class ReversedCalendars(Calendars):
    """All test should run in reversed item order.

    RFC5545:
        This memo imposes no ordering of properties within an iCalendar object.
    """

    def get_calendar(self, content):
        """Calendar traversing events in reversed order."""
        calendar = Calendars.get_calendar(self, content)
        _walk = calendar.walk
        def walk():
            """Return properties in reversed order."""
            return reversed(_walk())
        calendar.walk = walk
        return calendar


# for parametrizing fixtures, see https://docs.pytest.org/en/latest/fixture.html#parametrizing-fixtures
@pytest.fixture(params=[Calendars, ReversedCalendars])
def calendars(request):
    return request.param()

@pytest.fixture()
def todo():
    """Skip a test because it needs to be written first."""
    pytest.skip("This test is not yet implemented.")
