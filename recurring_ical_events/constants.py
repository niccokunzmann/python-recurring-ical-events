"""Constants for recurring_ical_events."""

import datetime
import re
from pathlib import Path

# The minimum value accepted as date (pytz + zoneinfo)
DATE_MIN = (1970, 1, 1)
DATE_MIN_DT = datetime.date(*DATE_MIN)
# The maximum value accepted as date (pytz + zoneinfo)
DATE_MAX = (2038, 1, 1)
DATE_MAX_DT = datetime.date(*DATE_MAX)

# the location of this file
HERE = Path(__file__).parent

# the directory with all example calendars
CALENDARS = HERE / "test" / "calendars"

NEGATIVE_RRULE_COUNT_REGEX = re.compile(r"COUNT=-\d+;?")

__all__ = [
    "CALENDARS",
    "DATE_MAX",
    "DATE_MAX_DT",
    "DATE_MIN",
    "DATE_MIN_DT",
    "NEGATIVE_RRULE_COUNT_REGEX",
]
