# py3
#
# This is the benchmark for rrule speed
# see https://github.com/niccokunzmann/python-recurring-ical-events/issues/42
#

import sys
from pathlib import Path

import icalendar

import recurring_ical_events

HERE = Path(__file__).parent or Path()
sys.path.append(HERE.parent)


# read utf
text = []
with Path(HERE / "issue42.ics").open("rb") as fobj:
    text += fobj.readlines()
text_utf = [i.decode("utf-8") for i in text]

ical_string = "".join(text_utf)


calendar = icalendar.Calendar.from_ical(ical_string)

rec_calendar = recurring_ical_events.of(calendar)

for day in range(1, 29):
    print("day", day)  # noqa: T201
    start_date = (2011, 11, day)
    events = rec_calendar.at(start_date)
