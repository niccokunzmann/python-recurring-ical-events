#py3
#
# This is the benchmark for rrule speed
# see https://github.com/niccokunzmann/python-recurring-ical-events/issues/42
#

import icalendar
import os
import sys

HERE = os.path.dirname(__file__) or "."
sys.path.append(os.path.join(HERE, ".."))

import recurring_ical_events

# read utf
text = []
with open(os.path.join(HERE, 'issue42.ics'), "rb") as fobj:
  text += fobj.readlines()
text_utf = []
for i in text:
  text_utf.append(i.decode("utf-8"))
ical_string = "".join(text_utf)


calendar = icalendar.Calendar.from_ical(ical_string)

rec_calendar = recurring_ical_events.of(calendar)

for day in range(1,29):
  print("day",day)
  start_date = (2011, 11, day)
  events = rec_calendar.at(start_date)
