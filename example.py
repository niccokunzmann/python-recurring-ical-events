import icalendar
import datetime
import recurring_ical_events
import urllib.request

start_date = (2019, 3, 5)
end_date =   (2019, 4, 1)
url = "http://tinyurl.com/y24m3r8f"

ical_string = urllib.request.urlopen(url).read() # https://stackoverflow.com/a/645318
calendar = icalendar.Calendar.from_ical(ical_string)
events = recurring_ical_events.of(calendar).between(start_date, end_date)
for event in events:
    start = event["DTSTART"].dt
    duration = event["DTEND"].dt - event["DTSTART"].dt
    print("start {} duration {}".format(start, duration))
# start 2019-03-18 04:00:00+01:00 duration 1:00:00
# start 2019-03-20 04:00:00+01:00 duration 1:00:00
# start 2019-03-19 04:00:00+01:00 duration 1:00:00
# start 2019-03-07 02:00:00+01:00 duration 1:00:00
# start 2019-03-08 01:00:00+01:00 duration 2:00:00
# start 2019-03-09 03:00:00+01:00 duration 0:30:00
# start 2019-03-10 duration 1 day, 0:00:00
