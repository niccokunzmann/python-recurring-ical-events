"""
These are tests concerning issue 4
https://github.com/niccokunzmann/python-recurring-ical-events/issues/4

It seems the rrule until parameter includes the last date
https://dateutil.readthedocs.io/en/stable/rrule.html
"""

import datetime

start_date = (2019, 6, 13, 12, 00, 00, 00)
end_date = (2019, 6, 14)
a_date = (2019, 6, 13)


def test_print_events(calendars):
    events = calendars.issue_4.between((2019, 6, 1), (2019, 7, 1))
    for event in events:
        print(event["DTSTART"].dt)


def test_between(calendars):
    events = calendars.issue_4.between(start_date, end_date)
    print(events)
    assert len(events) == 1
    assert events[0]["DTSTART"].dt == datetime.date(2019, 6, 13)


def test_at(calendars):
    events = calendars.issue_4.at(a_date)
    print(events)
    assert len(events) == 1
    assert events[0]["DTSTART"].dt == datetime.date(2019, 6, 13)


def test_can_use_different_rrule_until(calendars):
    events = list(calendars.issue_4_rrule_until.all())
    assert len(events) == 12


def test_weidenrinde(calendars):
    events = list(calendars.issue_4_weidenrinde.all())
    assert len(events) == 2
