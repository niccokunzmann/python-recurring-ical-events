"""This file tests the `keep_recurrence_attributes` argument of `of` works as expected."""
import os

from datetime import datetime
from recurring_ical_events import of
from icalendar import Calendar

HERE = os.path.dirname(__name__) or "test"
CALENDARS_FOLDER = os.path.join(HERE, "calendars")
calendar_path = os.path.join(CALENDARS_FOLDER, "rdate.ics")


def test_keep_recurrence_attributes_default(calendars):
    with open(calendar_path, "rb") as file:
        content = file.read()

    calendar = Calendar.from_ical(content)
    today = datetime.today()
    one_year_ahead = today.replace(year=today.year + 1)

    events = of(calendar).between(today, one_year_ahead)
    for event in events:
        assert event.get("RRULE", False) is False
        assert event.get("RDATE", False) is False
        assert event.get("EXDATE", False) is False


def test_keep_recurrence_attributes_false(calendars):
    with open(calendar_path, "rb") as file:
        content = file.read()

    calendar = Calendar.from_ical(content)
    today = datetime.today()
    one_year_ahead = today.replace(year=today.year + 1)

    events = of(calendar, keep_recurrence_attributes=False).between(today, one_year_ahead)
    for event in events:
        assert event.get("RRULE", False) is False
        assert event.get("RDATE", False) is False
        assert event.get("EXDATE", False) is False


def test_keep_recurrence_attributes_true(calendars):
    with open(calendar_path, "rb") as file:
        content = file.read()

    calendar = Calendar.from_ical(content)
    today = datetime.today()
    one_year_ahead = today.replace(year=today.year + 1)

    events = of(calendar, keep_recurrence_attributes=True).between(today, one_year_ahead)
    for event in events:
        assert event.get("RRULE", False) is not False
        assert event.get("RDATE", False) is not False
        assert event.get("EXDATE", False) is not False
