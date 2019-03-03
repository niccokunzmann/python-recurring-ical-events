import pytest
import os
import icalendar
import sys

sys.path.append(".")

HERE = os.path.dirname(__name__) or "test"
CALENDARS_FOLDER = os.path.join(HERE, "calendars")

class Calendars:
    """Collection of calendars"""

for calendar_file in os.listdir(CALENDARS_FOLDER):
    calendar_path = os.path.join(CALENDARS_FOLDER, calendar_file)
    name = os.path.splitext(calendar_file)[0]
    with open(calendar_path, "rb") as file:
        content = file.read()
    @property
    def get_calendar(self, content=content):
        return icalendar.Calendar.from_ical(content)
    attribute_name = name.replace("-", "_")
    setattr(Calendars, attribute_name, get_calendar)

@pytest.fixture()
def calendars():
    return Calendars()
