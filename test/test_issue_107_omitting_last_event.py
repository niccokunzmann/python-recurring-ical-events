"""bug: recurring event series that start in daylight savings time and end in standard time omit last event

Using a calendar application, I created a weekly event series in Pacific Standard Time that begins on January 5th and ends on June 8th. I filtered out events using between from today's date (~January 2023) and 1 year in the future (~January 2024). However, it incorrectly omitted the last event in the series on June 8th.

Upon further investigation, it seems to just be an issue for a recurring event series that begin in standard time but end in daylight savings time.

see https://github.com/niccokunzmann/python-recurring-ical-events/issues/107
see also test_issue_20_exdate_ignored.py - same problem with pytz
"""

import datetime


def test_last_event_is_present(calendars):
    today = datetime.date(2023, 1, 30)
    future = today + datetime.timedelta(days=365)
    events = calendars.issue_107_omitting_last_event.between(today, future)
    dates = [event["DTSTART"].dt.date() for event in events]
    assert datetime.date(2023, 6, 1) in dates, "event before last is present"
    assert datetime.date(2023, 6, 8) in dates, "last event is present"
