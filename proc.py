#py3

import icalendar
import recurring_ical_events
import urllib.request

# read utf
text = []
with open('dummy.ics', "rb") as fobj:
  text += fobj.readlines()
text_utf = []
for i in text:
  text_utf.append(i.decode("utf-8"))
ical_string = "".join(text_utf)


calendar = icalendar.Calendar.from_ical(ical_string)

for day in range(1,29):
  print("day",day)
  start_date = (2011, 11, day)
  events = recurring_ical_events.of(calendar).at(start_date)
