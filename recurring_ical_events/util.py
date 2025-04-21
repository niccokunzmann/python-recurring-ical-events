"""Utility functions."""

from __future__ import annotations

import datetime
from functools import wraps
from typing import TYPE_CHECKING, Callable, Optional, Sequence

from recurring_ical_events.errors import PeriodEndBeforeStart

if TYPE_CHECKING:
    from recurring_ical_events.adapters.component import ComponentAdapter
    from recurring_ical_events.types import RecurrenceIDs, Time, Timestamp


def timestamp(dt: datetime.datetime) -> Timestamp:
    """Return the time stamp of a datetime"""
    return dt.timestamp()


def convert_to_date(date: Time) -> datetime.date:
    """Converts a date or datetime to a date"""
    return datetime.date(date.year, date.month, date.day)


def is_pytz(tzinfo: datetime.tzinfo | Time):
    """Whether the time zone requires localize() and normalize().

    pytz requires these funtions to be used in order to correctly use the
    time zones after operations.
    """
    return hasattr(tzinfo, "localize")


def normalize_pytz(time: Time) -> Time:
    """We have to normalize the time after a calculation if we use pytz."""
    if is_pytz_dt(time):
        return time.tzinfo.normalize(time)
    return time


def is_date(time: Time) -> bool:
    """Whether this is a date and not a datetime."""
    return isinstance(time, datetime.date) and not isinstance(time, datetime.datetime)


def is_datetime(time: Time) -> bool:
    """Whether this is a datetime and not a date."""
    return isinstance(time, datetime.datetime)


def has_timezone(time: Time) -> bool:
    """Whether this date/datetime has a timezone."""
    return is_datetime(time) and time.tzinfo is not None


def convert_to_datetime(
    date: Time, tzinfo: Optional[datetime.tzinfo]
) -> datetime.datetime:
    """Converts a date to a datetime.

    Dates are converted to datetimes with tzinfo.
    Datetimes loose their timezone if tzinfo is None.
    Datetimes receive tzinfo as a timezone if they do not have a timezone.
    Datetimes retain their timezone if they have one already (tzinfo is not None).
    """
    if is_date(date):
        date = datetime.datetime(date.year, date.month, date.day)  # noqa: DTZ001
    if isinstance(date, datetime.datetime):
        if date.tzinfo is None:
            if tzinfo is not None:
                if is_pytz(tzinfo):
                    return tzinfo.localize(date)
                return date.replace(tzinfo=tzinfo)
        elif tzinfo is None:
            return normalize_pytz(date).replace(tzinfo=None)
        return date
    return date


def make_comparable(dates: Sequence[Time]) -> list[Time]:
    """Make an list or tuple of dates comparable.

    Returns an list.
    """
    tzinfo = None
    all_dates = True
    for date in dates:
        if not is_date(date):
            all_dates = False
            if has_timezone(date):
                tzinfo = date.tzinfo
                break
    if all_dates:
        return dates
    return [convert_to_datetime(date, tzinfo) for date in dates]


def time_span_contains_event(
    span_start: Time,
    span_stop: Time,
    event_start: Time,
    event_stop: Time,
    comparable: bool = False,  # noqa: FBT001
) -> bool:
    """Return whether an event should is included within a time span.

    - span_start and span_stop define the time span
    - event_start and event_stop define the event time
    - comparable indicates whether the dates can be compared.
        You can set it to True if you are sure you have timezones and
        date/datetime correctly or used make_comparable() before.

    Note that the stops are exlusive but the starts are inclusive.

    This is an essential function of the module. It should be tested in
    test/test_time_span_contains_event.py.

    This raises a PeriodEndBeforeStart exception if a start is after an end.
    """
    if not comparable:
        span_start, span_stop, event_start, event_stop = make_comparable(
            (span_start, span_stop, event_start, event_stop)
        )
    if event_start > event_stop:
        raise PeriodEndBeforeStart(
            (
                "the event must start before it ends"
                f"(start: {event_start} end: {event_stop})"
            ),
            event_start,
            event_stop,
        )
    if span_start > span_stop:
        raise PeriodEndBeforeStart(
            (
                "the time span must start before it ends"
                f"(start: {span_start} end: {span_stop})"
            ),
            span_start,
            span_stop,
        )
    if event_start == event_stop:
        if span_start == span_stop:
            return event_start == span_start
        return span_start <= event_start < span_stop
    if span_start == span_stop:
        return event_start <= span_start < event_stop
    return event_start < span_stop and span_start < event_stop


def compare_greater(date1: Time, date2: Time) -> bool:
    """Compare two dates if date1 > date2 and make them comparable before."""
    date1, date2 = make_comparable((date1, date2))
    return date1 > date2


def cmp(date1: Time, date2: Time) -> int:
    """Compare two dates, like cmp().

    Returns
    -------
        -1 if date1 < date2
         0 if date1 = date2
         1 if date1 > date2

    """
    # credits: https://www.geeksforgeeks.org/python-cmp-function/
    # see https://stackoverflow.com/a/22490617/1320237
    date1, date2 = make_comparable((date1, date2))
    return (date1 > date2) - (date1 < date2)


def is_pytz_dt(time: Time) -> bool:
    """Whether the time requires localize() and normalize().

    pytz requires these funtions to be used in order to correctly use the
    time zones after operations.
    """
    return isinstance(time, datetime.datetime) and is_pytz(time.tzinfo)


def cached_property(func: Callable) -> property:
    """Cache the property value for speed up."""
    name = f"_cached_{func.__name__}"
    not_found = object()

    @property
    @wraps(func)
    def cached_property(self: object):
        value = self.__dict__.get(name, not_found)
        if value is not_found:
            self.__dict__[name] = value = func(self)
        return value

    return cached_property


def to_recurrence_ids(time: Time) -> RecurrenceIDs:
    """Convert the time to a recurrence id so it can be hashed and recognized.

    The first value should be used to identify a component as it is a datetime in UTC.
    The other values can be used to look the component up.
    """
    # We are inside the Series calculation with this and want to identify
    # a date. It is fair to assume that the timezones are the same now.
    if not isinstance(time, datetime.datetime):
        return (convert_to_datetime(time, None),)
    if time.tzinfo is None:
        return (time,)
    return (
        time.astimezone(datetime.timezone.utc).replace(tzinfo=None),
        time.replace(tzinfo=None),
    )


def with_highest_sequence(
    adapter1: ComponentAdapter | None, adapter2: ComponentAdapter | None
):
    """Return the one with the highest sequence."""
    return max(
        adapter1,
        adapter2,
        key=lambda adapter: -1e10 if adapter is None else adapter.sequence,
    )


def get_any(dictionary: dict, keys: Sequence[object], default: object = None):
    """Get any item from the keys and return it."""
    result = default
    for key in keys:
        result = dictionary.get(key, result)
    return result


__all__ = [
    "PeriodEndBeforeStart",
    "cmp",
    "convert_to_datetime",
    "get_any",
    "has_timezone",
    "is_date",
    "is_datetime",
    "is_pytz",
    "is_pytz_dt",
    "make_comparable",
    "normalize_pytz",
    "time_span_contains_event",
    "to_recurrence_ids",
    "with_highest_sequence",
]
