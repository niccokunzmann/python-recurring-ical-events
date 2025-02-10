"""Useful functions for many purposes."""
from __future__ import annotations

import datetime




def convert_to_date(date:datetime.date) -> datetime.date:
    """converts a date or datetime to a date"""
    return datetime.date(date.year, date.month, date.day)


def is_pytz(tzinfo:datetime.tzinfo) -> bool:
    """Whether the time zone requires localize() and normalize().

    pytz requires these funtions to be used in order to correctly use the
    time zones after operations.
    """
    return hasattr(tzinfo , "localize")


def convert_to_datetime(date: datetime.date, tzinfo: datetime.tzinfo) -> datetime.datetime:
    """Converts a date or datetime to a datetime.
    
    tzinfo is the timezone to use.
    """
    if isinstance(date, datetime.datetime):
        if date.tzinfo is None:
            if tzinfo is not None:
                if is_pytz(tzinfo):
                    return tzinfo.localize(date)
                return date.replace(tzinfo=tzinfo)
        elif tzinfo is None:
            return date.replace(tzinfo=None)
        return date
    elif isinstance(date, datetime.date):
        return datetime.datetime(date.year, date.month, date.day, tzinfo=tzinfo)
    return date


def make_comparable(dates: list[datetime.date]|tuple[datetime.date]) -> list[datetime.datetime]:
    """Make an list or tuple of dates comparable.

    Returns an list.
    """
    tzinfo = None
    for date in dates:
        tzinfo = getattr(date, "tzinfo", None)
        if tzinfo is not None:
            break
    return [convert_to_datetime(date, tzinfo) for date in dates]


def compare_greater(date1:datetime.date, date2:datetime.date) -> bool:
    """Compare two dates if date1 > date2 and make them comparable before."""
    date1, date2 = make_comparable((date1, date2))
    return date1 > date2


def time_span_contains_event(span_start:datetime.date, span_stop:datetime.date, event_start:datetime.date, event_stop:datetime.date, comparable=False) -> bool:
    """Return whether an event should is included within a time span.

    - span_start and span_stop define the time span
    - event_start and event_stop define the event time
    - comparable indicates whether the dates can be compared.
        You can set it to True if you are sure you have timezones and
        date/datetime correctly or used make_comparable() before.

    Note that the stops are exlusive but the starts are inclusive.

    This is an essential function of the module. It should be tested in
    test/test_time_span_contains_event.py.
    """
    if not comparable:
        span_start, span_stop, event_start, event_stop = make_comparable((
            span_start, span_stop, event_start, event_stop
        ))
    assert event_start <= event_stop, "the event must start before it ends"
    assert span_start <= span_stop, "the time span must start before it ends"
    if event_start == event_stop:
        if span_start == span_stop:
            return event_start == span_start
        return span_start <= event_start < span_stop
    if span_start == span_stop:
        return event_start <= span_start < event_stop
    return event_start < span_stop and span_start < event_stop


__all__ = ["convert_to_date", "convert_to_datetime", "is_pytz", "compare_greater", "time_span_contains_event"]

