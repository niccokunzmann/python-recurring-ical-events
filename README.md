# Recurring ICal events for Python

[![Build Status](https://travis-ci.org/niccokunzmann/python-recurring-ical-events.svg?branch=master)](https://travis-ci.org/niccokunzmann/python-recurring-ical-events)

ICal has some complexity to it:
Events can be repeated, removed from the feed and edited later on.
This tool takes care of these circumstances.

Let's put our expertise together and build a tool that can solve this!

- day light saving time
- recurring events
- recurring events with edits
- recurring events where events are omitted
- recurring events events where the edit took place later
- normal events
- recurrence of dates but not hours, minutes, and smaller
- endless recurrence
- ending recurrence
- events with start date and no and date
- events with start as date and start as datetime
- RRULE, RDATE, EXDATE

```python
import requests
import icalendar
import datetime
import recurring_ical_events

today = datetime.datetime.today()
one_year_ahead = today.replace(year=today.year + 1)

ical_string = requests.get("https://url-to-ical-feed").text
calendar = icalendar.Calendar.from_ical(ical_string)
for event in recurring_ical_events.of(calendar).between(today, one_year_ahead):
    print(event["DTSTART"])
```

## Development

1. Optional: Install virtualenv and Python3 and create a virtual environment.
    ```
    virtualenv -p python3 ENV
    source ENV/bin/activate
    ```
2. Install the packages.
    ```
    pip install -r requirements.txt test-requirements.txt
    ```
3. Run the tests
    ```
    pytest
    ```

## Research
- https://stackoverflow.com/questions/30913824/ical-library-to-iterate-recurring-events-with-specific-instances
- https://github.com/oberron/annum
  - https://stackoverflow.com/questions/28829261/python-ical-get-events-for-a-day-including-recurring-ones#28829401
- https://stackoverflow.com/questions/20268204/ical-get-date-from-recurring-event-by-rrule-and-dtstart
- https://github.com/collective/icalendar/issues/162
- https://stackoverflow.com/questions/46471852/ical-parsing-reoccuring-events-in-python
- RDATE https://stackoverflow.com/a/46709850/1320237
  - https://tools.ietf.org/html/rfc5545#section-3.8.5.2
