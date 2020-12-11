'''
These are tests concerning issue 4
https://github.com/niccokunzmann/python-recurring-ical-events/issues/4

It seems the rrule until parameter includes the last date
https://dateutil.readthedocs.io/en/stable/rrule.html
'''
from datetime import datetime
import pytz

def test_between_8_and_15(calendars):
    localTZ = pytz.timezone("America/Chicago")

    start_time = datetime.now()
    start_time = start_time.replace(
        hour=8, minute=0, second=0, microsecond=0)
    end_time = start_time.replace(hour=15, minute=0)

    start_time=localTZ.localize(start_time)
    end_time=localTZ.localize(end_time)

    events = calendars.issue_48_dst.between(start_time, end_time)
    
    print("Events between {} and {}".format(start_time, end_time))
    for event in events:
        print("{} {}".format(event["DTSTART"].dt, event["SUMMARY"]))
    
    assert len(events) == 4, "four events between 8AM and 3 PM"

def test_between_9_and_15(calendars):
    localTZ = pytz.timezone("America/Chicago")

    start_time = datetime.now()
    start_time = start_time.replace(
        hour=9, minute=0, second=0, microsecond=0)
    end_time = start_time.replace(hour=15, minute=0)

    start_time=localTZ.localize(start_time)
    end_time=localTZ.localize(end_time)

    events = calendars.issue_48_dst.between(start_time, end_time)
    
    print("Events between {} and {}".format(start_time, end_time))
    for event in events:
        print("{} {}".format(event["DTSTART"].dt, event["SUMMARY"]))

    assert len(events) == 3, "three events between 9AM and 3 PM"

def test_between_10_and_15(calendars):
    localTZ = pytz.timezone("America/Chicago")

    start_time = datetime.now()
    start_time = start_time.replace(
        hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time.replace(hour=15, minute=0)

    start_time=localTZ.localize(start_time)
    end_time=localTZ.localize(end_time)

    events = calendars.issue_48_dst.between(start_time, end_time)
    
    print("Events between {} and {}".format(start_time, end_time))
    for event in events:
        print("{} {}".format(event["DTSTART"].dt, event["SUMMARY"]))

    assert len(events) == 3, "three events between 10AM and 3 PM"