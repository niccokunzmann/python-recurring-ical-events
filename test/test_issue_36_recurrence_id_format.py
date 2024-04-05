"""
These tests are for issue 36
https://github.com/niccokunzmann/python-recurring-ical-events/issues/36
"""


def test_datetime_replaced_by_datetime(calendars):
    events = calendars.issue_36_recurrence_ID_format.at("20200917")
    assert len(events) == 1
    assert events[0].get("SUMMARY") == "Modified event"


def test_date_replaced_by_date(calendars):
    events = calendars.issue_36_recurrence_ID_format.at("20200914")
    assert len(events) == 1
    assert events[0].get("SUMMARY") == "Modified event 1"


def test_date_replaced_by_datetime(calendars):
    events = calendars.issue_36_recurrence_ID_format.at("20200921")
    assert len(events) == 1
    assert events[0].get("SUMMARY") == "Modified event 2"
