# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Calculate repetitions of icalendar components."""

from __future__ import annotations

import contextlib
import datetime
import re
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import wraps
from typing import TYPE_CHECKING, Callable, Generator, Optional, Sequence, Union

import x_wr_timezone
from dateutil.rrule import rruleset, rrulestr
from icalendar.cal import Component
from icalendar.prop import vDDDTypes

if TYPE_CHECKING:
    from icalendar.cal import Component

    Time = Union[datetime.date, datetime.datetime]
    DateArgument = tuple[int] | Time | str | int
    from dateutil.rrule import rrule

    UID = str
    ComponentID = tuple[str, UID, Time]
    Timestamp = float
    RecurrenceID = datetime.datetime
    RecurrenceIDs = tuple[RecurrenceID]


# The minimum value accepted as date (pytz + zoneinfo)
DATE_MIN = (1970, 1, 1)
DATE_MIN_DT = datetime.date(*DATE_MIN)
# The maximum value accepted as date (pytz + zoneinfo)
DATE_MAX = (2038, 1, 1)
DATE_MAX_DT = datetime.date(*DATE_MAX)


class InvalidCalendar(ValueError):
    """Exception thrown for bad icalendar content."""

    def __init__(self, message: str):
        """Create a new error with a message."""
        self._message = message
        super().__init__(self.message)

    @property
    def message(self) -> str:
        """The error message."""
        return self._message


class PeriodEndBeforeStart(InvalidCalendar):
    """An event or component starts before it ends."""

    def __init__(self, message: str, start: Time, end: Time):
        """Create a new PeriodEndBeforeStart error."""
        super().__init__(message)
        self._start = start
        self._end = end

    @property
    def start(self) -> Time:
        """The start of the component's period."""
        return self._start

    @property
    def end(self) -> Time:
        """The end of the component's period."""
        return self._end


class BadRuleStringFormat(InvalidCalendar):
    """An iCal rule string is badly formatted."""

    def __init__(self, message: str, rule: str):
        """Create an error with a bad rule string."""
        super().__init__(message + ": " + rule)
        self._rule = rule

    @property
    def rule(self) -> str:
        """The malformed rule string"""
        return self._rule


def timestamp(dt: datetime.datetime) -> Timestamp:
    """Return the time stamp of a datetime"""
    return dt.timestamp()


NEGATIVE_RRULE_COUNT_REGEX = re.compile(r"COUNT=-\d+;?")


def convert_to_date(date: Time) -> datetime.date:
    """Converts a date or datetime to a date"""
    return datetime.date(date.year, date.month, date.day)


def convert_to_datetime(date: Time, tzinfo: Optional[datetime.tzinfo]):  # noqa: UP007
    """Converts a date to a datetime.

    Dates are converted to datetimes with tzinfo.
    Datetimes loose their timezone if tzinfo is None.
    Datetimes receive tzinfo as a timezone if they do not have a timezone.
    Datetimes retain their timezone if they have one already (tzinfo is not None).
    """
    if isinstance(date, datetime.datetime):
        if date.tzinfo is None:
            if tzinfo is not None:
                if is_pytz(tzinfo):
                    return tzinfo.localize(date)
                return date.replace(tzinfo=tzinfo)
        elif tzinfo is None:
            return normalize_pytz(date).replace(tzinfo=None)
        return date
    if isinstance(date, datetime.date):
        return datetime.datetime(date.year, date.month, date.day, tzinfo=tzinfo)
    return date


def time_span_contains_event(
    span_start: Time,
    span_stop: Time,
    event_start: Time,
    event_stop: Time,
    comparable: bool = False,  # noqa: FBT001
):
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


def make_comparable(dates: Sequence[Time]) -> list[Time]:
    """Make an list or tuple of dates comparable.

    Returns an list.
    """
    tzinfo = None
    for date in dates:
        tzinfo = getattr(date, "tzinfo", None)
        if tzinfo is not None:
            break
    return [convert_to_datetime(date, tzinfo) for date in dates]


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


def is_pytz(tzinfo: datetime.tzinfo | Time):
    """Whether the time zone requires localize() and normalize().

    pytz requires these funtions to be used in order to correctly use the
    time zones after operations.
    """
    return hasattr(tzinfo, "localize")


def is_pytz_dt(time: Time):
    """Whether the time requires localize() and normalize().

    pytz requires these funtions to be used in order to correctly use the
    time zones after operations.
    """
    return isinstance(time, datetime.datetime) and is_pytz(time.tzinfo)


def normalize_pytz(time: Time):
    """We have to normalize the time after a calculation if we use pytz."""
    if is_pytz_dt(time):
        return time.tzinfo.normalize(time)
    return time


def cached_property(func: Callable):
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


def is_date(time: Time):
    """Whether this is a date and not a datetime."""
    return isinstance(time, datetime.date) and not isinstance(time, datetime.datetime)


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


class Series:
    """Base class for components that result in a series of occurrences."""

    @property
    def occurrence(self) -> type[Occurrence]:
        """A way to override the occurrence class."""
        return Occurrence

    class NoRecurrence:
        """A strategy to deal with not having a core with rrules."""

        check_exdates_datetime: set[RecurrenceID] = set()
        check_exdates_date: set[datetime.date] = set()
        replace_ends: dict[RecurrenceID, Time] = {}

        def as_occurrence(
            self,
            start: Time,
            stop: Time,
            occurrence: type[Occurrence],
            core: ComponentAdapter,
        ) -> Occurrence:
            raise NotImplementedError("This code should never be reached.")

        @property
        def core(self) -> ComponentAdapter:
            raise NotImplementedError("This code should never be reached.")

        def rrule_between(
            self,
            span_start: Time,  # noqa: ARG002
            span_stop: Time,  # noqa: ARG002
        ) -> Generator[Time, None, None]:
            """No repetition."""
            yield from []

        has_core = False
        extend_query_span_by = (datetime.timedelta(0), datetime.timedelta(0))

    class RecurrenceRules:
        """A strategy if we have an actual core with recurrences."""

        has_core = True

        def __init__(self, core: ComponentAdapter):
            self.core = core
            # Setup complete. We create the attribtues
            self.start = self.original_start = self.core.start
            self.end = self.original_end = self.core.end
            self.exdates: set[Time] = set()
            self.check_exdates_datetime: set[RecurrenceID] = set()  # should be in UTC
            self.check_exdates_date: set[datetime.date] = set()  # should be in UTC
            self.rdates: set[Time] = set()
            self.replace_ends: dict[
                RecurrenceID, datetime.timedelta
            ] = {}  # for periods, in UTC
            # fill the attributes
            for exdate in self.core.exdates:
                self.exdates.add(exdate)
                self.check_exdates_datetime.update(to_recurrence_ids(exdate))
                if is_date(exdate):
                    self.check_exdates_date.add(exdate)
            for rdate in self.core.rdates:
                if isinstance(rdate, tuple):
                    # we have a period as rdate
                    self.rdates.add(rdate[0])
                    for recurrence_id in to_recurrence_ids(rdate[0]):
                        self.replace_ends[recurrence_id] = (
                            rdate[1]
                            if isinstance(rdate[1], datetime.timedelta)
                            else rdate[1] - rdate[0]
                        )
                else:
                    # we have a date/datetime
                    self.rdates.add(rdate)

            # We make sure that all dates and times mentioned here are either:
            # - a date
            # - a datetime with None is tzinfo
            # - a datetime with a timezone
            self.make_all_dates_comparable()

            # Calculate the rules with the same timezones
            rule_set = rruleset(cache=True)
            rule_set.until = None
            self.rrules = [rule_set]
            last_until: Time | None = None
            for rrule_string in self.core.rrules:
                rule = self.create_rule_with_start(rrule_string)
                self.rrules.append(rule)
                if rule.until and (
                    not last_until or compare_greater(rule.until, last_until)
                ):
                    last_until = rule.until

            for exdate in self.exdates:
                self.check_exdates_datetime.add(exdate)
            for rdate in self.rdates:
                rule_set.rdate(rdate)

            if not last_until or not compare_greater(self.start, last_until):
                rule_set.rdate(self.start)

        @property
        def extend_query_span_by(self) -> tuple[datetime.timedelta, datetime.timedelta]:
            """The extension of the time span we need for this component's core."""
            return self.core.extend_query_span_by

        def create_rule_with_start(self, rule_string) -> rrule:
            """Helper to create an rrule from a rule_string

            The rrule is starting at the start of the component.
            Since the creation is a bit more complex,
            this function handles special cases.
            """
            try:
                return self.rrulestr(rule_string)
            except ValueError:
                # string: FREQ=WEEKLY;UNTIL=20191023;BYDAY=TH;WKST=SU
                # start: 2019-08-01 14:00:00+01:00
                # ValueError: RRULE UNTIL values must be specified in UTC
                # when DTSTART is timezone-aware
                rule_list = rule_string.split(";UNTIL=")
                if len(rule_list) != 2:
                    raise BadRuleStringFormat(
                        "UNTIL parameter is missing", rule_string
                    ) from None
                date_end_index = rule_list[1].find(";")
                if date_end_index == -1:
                    date_end_index = len(rule_list[1])
                until_string = rule_list[1][:date_end_index]
                if self.is_all_dates:
                    until_string = until_string[:8]
                elif self.tzinfo is None:
                    # remove the Z from the time zone
                    until_string = until_string[:-1]
                else:
                    # we assume the start is timezone aware but the until value
                    # is not, see the comment above
                    if len(until_string) == 8:
                        until_string += "T000000"
                    if len(until_string) != 15:
                        raise BadRuleStringFormat(
                            "UNTIL parameter has a bad format", rule_string
                        ) from None
                    until_string += "Z"  # https://stackoverflow.com/a/49991809
                new_rule_string = (
                    rule_list[0]
                    + rule_list[1][date_end_index:]
                    + ";UNTIL="
                    + until_string
                )
                return self.rrulestr(new_rule_string)

        def rrulestr(self, rule_string) -> rrule:
            """Return an rrulestr with a start. This might fail."""
            rule_string = NEGATIVE_RRULE_COUNT_REGEX.sub("", rule_string)  # Issue 128
            rule = rrulestr(rule_string, dtstart=self.start, cache=True)
            rule.string = rule_string
            rule.until = until = self._get_rrule_until(rule)
            if is_pytz(self.start.tzinfo) and rule.until:
                # when starting in a time zone that is one hour off to the end,
                # we might miss the last occurrence
                # see issue 107 and test/test_issue_107_omitting_last_event.py
                rule = rule.replace(until=rule.until + datetime.timedelta(hours=1))
                rule.until = until
            return rule

        def _get_rrule_until(self, rrule) -> None | Time:
            """Return the UNTIL datetime of the rrule or None if absent."""
            rule_list = rrule.string.split(";UNTIL=")
            if len(rule_list) == 1:
                return None
            if len(rule_list) != 2:
                raise BadRuleStringFormat("There should be only one UNTIL", rrule)
            date_end_index = rule_list[1].find(";")
            if date_end_index == -1:
                date_end_index = len(rule_list[1])
            until_string = rule_list[1][:date_end_index]
            return vDDDTypes.from_ical(until_string)

        def make_all_dates_comparable(self):
            """Make sure we can use all dates with eachother.

            Dates may be mixed and we have many of them.
            - date
            - datetime without timezone
            - datetime with timezone
            These three are not comparable but can be converted.
            """
            self.tzinfo = None
            dates = [self.start, self.end, *self.exdates, *self.rdates]
            self.is_all_dates = not any(
                isinstance(date, datetime.datetime) for date in dates
            )
            for date in dates:
                if isinstance(date, datetime.datetime) and date.tzinfo is not None:
                    self.tzinfo = date.tzinfo
                    break
            self.start = convert_to_datetime(self.start, self.tzinfo)

            self.end = convert_to_datetime(self.end, self.tzinfo)
            self.rdates = {
                convert_to_datetime(rdate, self.tzinfo) for rdate in self.rdates
            }
            self.exdates = {
                convert_to_datetime(exdate, self.tzinfo) for exdate in self.exdates
            }

        def rrule_between(self, span_start: Time, span_stop: Time) -> Generator[Time]:
            """Recalculate the rrules so that minor mistakes are corrected."""
            # make dates comparable, rrule converts them to datetimes
            span_start_dt = convert_to_datetime(span_start, self.tzinfo)
            span_stop_dt = convert_to_datetime(span_stop, self.tzinfo)
            # we have to account for pytz timezones not being properly calculated
            # at the timezone changes. This is a heuristic:
            #   most changes are only 1 hour.
            # This will still create problems at the fringes of
            #   timezone definition changes.
            if is_pytz(self.tzinfo):
                span_start_dt = normalize_pytz(
                    span_start_dt - datetime.timedelta(hours=1)
                )
                span_stop_dt = normalize_pytz(
                    span_stop_dt + datetime.timedelta(hours=1)
                )
            for rule in self.rrules:
                for start in rule.between(span_start_dt, span_stop_dt, inc=True):
                    if is_pytz_dt(start):
                        # update the time zone in case of summer/winter time change
                        start = start.tzinfo.localize(start.replace(tzinfo=None))  # noqa: PLW2901
                    # We could now well be out of bounce of the end of the UNTIL
                    # value. This is tested by test/test_issue_20_exdate_ignored.py.
                    if rule.until is None or not compare_greater(start, rule.until):
                        yield start

        def convert_to_original_type(self, date):
            """Convert a date back if this is possible.

            Dates may get converted to datetimes to make calculations possible.
            This reverts the process where possible so that Repetitions end
            up with the type (date/datetime) that was specified in the icalendar
            component.
            """
            if not isinstance(
                self.original_start, datetime.datetime
            ) and not isinstance(
                self.original_end,
                datetime.datetime,
            ):
                return convert_to_date(date)
            return date

        def as_occurrence(
            self,
            start: Time,
            stop: Time,
            occurrence: type[Occurrence],
            core: ComponentAdapter,
        ) -> Occurrence:
            """Return this as an occurrence at a specific time."""
            return occurrence(
                core,
                self.convert_to_original_type(start),
                self.convert_to_original_type(stop),
            )

    def __init__(self, components: Sequence[ComponentAdapter]):
        """Create an component which may have repetitions in it."""
        if len(components) == 0:
            raise ValueError("No components given to calculate a series.")
        # We identify recurrences with a timestamp as all recurrence values
        # should be the same in UTC either way and we want to omit
        # inequality because of timezone implementation mismatches.
        self.recurrence_id_to_modification: dict[
            RecurrenceID, ComponentAdapter
        ] = {}  # RECURRENCE-ID -> adapter
        self.this_and_future = []
        self._uid = components[0].uid
        core: ComponentAdapter | None = None
        for component in components:
            if component.is_modification():
                recurrence_ids = component.recurrence_ids
                for recurrence_id in recurrence_ids:
                    self.recurrence_id_to_modification[recurrence_id] = (
                        with_highest_sequence(
                            self.recurrence_id_to_modification.get(recurrence_id),
                            component,
                        )
                    )
                if component.this_and_future:
                    self.this_and_future.append(recurrence_ids[0])
            else:
                core = with_highest_sequence(core, component)
        self.modifications: set[ComponentAdapter] = set(
            self.recurrence_id_to_modification.values()
        )
        del component
        self.recurrence = (
            self.NoRecurrence() if core is None else self.RecurrenceRules(core)
        )
        self.this_and_future.sort()

        self.compute_span_extension()

    def compute_span_extension(self):
        """Compute how much to extend the span for the rrule to cover all events."""
        self._subtract_from_start, self._add_to_stop = (
            self.recurrence.extend_query_span_by
        )
        for adapter in self.this_and_future_components:
            subtract_from_start, add_to_stop = adapter.extend_query_span_by
            self._subtract_from_start = max(
                subtract_from_start, self._subtract_from_start
            )
            self._add_to_stop = max(add_to_stop, self._add_to_stop)

    @property
    def this_and_future_components(self) -> Generator[ComponentAdapter]:
        """All components that influence future events."""
        if self.recurrence.has_core:
            yield self.recurrence.core
        for recurrence_id in self.this_and_future:
            yield self.recurrence_id_to_modification[recurrence_id]

    def get_component_for_recurrence_id(
        self, recurrence_id: RecurrenceID
    ) -> ComponentAdapter:
        """Get the component which contains all information for the recurrence id.

        This concerns this modifications that have RANGE=THISANDFUTURE set.
        """
        # We assume the the recurrence_id is of the correct timezone.
        component = self.recurrence.core
        for modification_id in self.this_and_future:
            if modification_id < recurrence_id:
                component = self.recurrence_id_to_modification[modification_id]
            else:
                break
        return component

    def rrule_between(self, span_start: Time, span_stop: Time) -> Generator[Time]:
        """Modify the rrule generation span and yield recurrences."""
        expanded_start = normalize_pytz(span_start - self._subtract_from_start)
        expanded_stop = normalize_pytz(span_stop + self._add_to_stop)
        yield from self.recurrence.rrule_between(
            expanded_start,
            expanded_stop,
        )

    def between(self, span_start: Time, span_stop: Time) -> Generator[Occurrence]:
        """Components between the start (inclusive) and end (exclusive).

        The result does not need to be ordered.
        """
        returned_starts: set[Time] = set()
        returned_modifications: set[ComponentAdapter] = set()
        # NOTE: If in the following line, we get an error, datetime and date
        # may still be mixed because RDATE, EXDATE, start and rule.
        for start in self.rrule_between(span_start, span_stop):
            recurrence_ids = to_recurrence_ids(start)
            if (
                start in returned_starts
                or convert_to_date(start) in self.recurrence.check_exdates_date
                or self.recurrence.check_exdates_datetime & set(recurrence_ids)
            ):
                continue
            adapter: ComponentAdapter = get_any(
                self.recurrence_id_to_modification, recurrence_ids, self.recurrence.core
            )
            if adapter is self.recurrence.core:
                # We have no modification for this recurrence, so we record the date
                returned_starts.add(start)
                # This component is the base for this occurrence.
                # It usually is the core. However, we may also find a modification
                # with RANGE=THISANDFUTURE.
                component = self.get_component_for_recurrence_id(recurrence_ids[0])
                occurrence_start = normalize_pytz(start + component.move_recurrences_by)
                # Consider the RDATE with a PERIOD value
                occurrence_end = normalize_pytz(
                    occurrence_start
                    + get_any(
                        self.recurrence.replace_ends,
                        recurrence_ids,
                        component.duration,
                    )
                )
                occurrence = self.recurrence.as_occurrence(
                    occurrence_start, occurrence_end, self.occurrence, component
                )
            else:
                # We found a modification, so we record the modification
                if adapter in returned_modifications:
                    continue
                returned_modifications.add(adapter)
                occurrence = self.occurrence(adapter)
            if occurrence.is_in_span(span_start, span_stop):
                yield occurrence
        for modification in self.modifications:
            # we assume that the modifications are actually included
            if (
                modification in returned_modifications
                or self.recurrence.check_exdates_datetime
                & set(modification.recurrence_ids)
            ):
                continue
            if modification.is_in_span(span_start, span_stop):
                returned_modifications.add(modification)
                yield self.occurrence(modification)

    @property
    def uid(self):
        """The UID that identifies this series."""
        return self._uid

    def __repr__(self):
        """A string representation."""
        return (
            f"<{self.__class__.__name__} uid={self.uid} "
            f"modifications:{len(self.recurrence_id_to_modification)}>"
        )


class ComponentAdapter(ABC):
    """A unified interface to work with icalendar components."""

    ATTRIBUTES_TO_DELETE_ON_COPY = ["RRULE", "RDATE", "EXDATE", "RECURRENCE-ID"]

    @staticmethod
    @abstractmethod
    def component_name() -> str:
        """The icalendar component name."""

    def __init__(self, component: Component):
        """Create a new adapter."""
        self._component = component

    @property
    def end_property(self) -> str | None:
        """The name of the end property."""
        return None

    @property
    @abstractmethod
    def start(self) -> Time:
        """The start time."""

    @property
    @abstractmethod
    def end(self) -> Time:
        """The end time."""

    @property
    def uid(self) -> UID:
        """The UID of a component.

        UID is required by RFC5545.
        If the UID is absent, we use the Python ID.
        """
        return self._component.get("UID", str(id(self._component)))

    @classmethod
    def collect_series_from(
        cls, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect all components for this adapter.

        This is a shortcut.
        """
        return ComponentsWithName(cls.component_name(), cls).collect_series_from(
            source, suppress_errors
        )

    def as_component(self, start: Time, stop: Time, keep_recurrence_attributes: bool):  # noqa: FBT001
        """Create a shallow copy of the source event and modify some attributes."""
        copied_component = self._component.copy()
        copied_component["DTSTART"] = vDDDTypes(start)
        copied_component.pop("DURATION", None)  # remove duplication in event length
        if self.end_property is not None:
            copied_component[self.end_property] = vDDDTypes(stop)
        if not keep_recurrence_attributes:
            for attribute in self.ATTRIBUTES_TO_DELETE_ON_COPY:
                if attribute in copied_component:
                    del copied_component[attribute]
        for subcomponent in self._component.subcomponents:
            copied_component.add_component(subcomponent)
        return copied_component

    @cached_property
    def recurrence_ids(self) -> RecurrenceIDs:
        """The recurrence ids of the component that might be used to identify it."""
        recurrence_id = self._component.get("RECURRENCE-ID")
        if recurrence_id is None:
            return ()
        return to_recurrence_ids(recurrence_id.dt)

    @cached_property
    def this_and_future(self) -> bool:
        """The recurrence ids has a thisand future range property"""
        recurrence_id = self._component.get("RECURRENCE-ID")
        if recurrence_id is None:
            return False
        if "RANGE" in recurrence_id.params:
            return recurrence_id.params["RANGE"] == "THISANDFUTURE"
        return False

    def is_modification(self) -> bool:
        """Whether the adapter is a modification."""
        return bool(self.recurrence_ids)

    @cached_property
    def sequence(self) -> int:
        """The sequence in the history of modification.

        The sequence is negative if none was found.
        """
        return self._component.get("SEQUENCE", -1)

    def __repr__(self) -> str:
        """Debug representation with more info."""
        return (
            f"<{self.__class__.__name__} UID={self.uid} start={self.start} "
            f"recurrence_ids={self.recurrence_ids} sequence={self.sequence} "
            f"end={self.end}>"
        )

    @cached_property
    def exdates(self) -> list[Time]:
        """A list of exdates."""
        result: list[Time] = []
        exdates = self._component.get("EXDATE", [])
        for exdates in (exdates,) if not isinstance(exdates, list) else exdates:
            result.extend(exdate.dt for exdate in exdates.dts)
        return result

    @cached_property
    def rrules(self) -> set[str]:
        """A list of rrules of this component."""
        rules = self._component.get("RRULE", None)
        if not rules:
            return set()
        return {
            rrule.to_ical().decode()
            for rrule in (rules if isinstance(rules, list) else [rules])
        }

    @cached_property
    def rdates(self) -> list[Time, tuple[Time, Time]]:
        """A list of rdates, possibly a period."""
        rdates = self._component.get("RDATE", [])
        result = []
        for rdates in (rdates,) if not isinstance(rdates, list) else rdates:
            result.extend(rdate.dt for rdate in rdates.dts)
        return result

    @cached_property
    def duration(self) -> datetime.timedelta:
        """The duration of the component."""
        return self.end - self.start

    def is_in_span(self, span_start: Time, span_stop: Time) -> bool:
        """Return whether the component is in the span."""
        return time_span_contains_event(span_start, span_stop, self.start, self.end)

    @cached_property
    def extend_query_span_by(self) -> tuple[datetime.timedelta, datetime.timedelta]:
        """Calculate how much we extend the query span.

        If an event is long, we need to extend the query span by the event's duration.
        If an event has moved, we need to make sure that that is included, too.

        This is so that the RECURRENCE-ID falls within the modified span.
        Imagine if the span is exactly a second. How much would we need to query
        forward and backward to capture the recurrence id?

        Returns two positive spans: (subtract_from_start, add_to_stop)
        """
        subtract_from_start = self.duration
        add_to_stop = datetime.timedelta(0)
        recurrence_id_prop = self._component.get("RECURRENCE-ID")
        if recurrence_id_prop:
            start, end, recurrence_id = make_comparable(
                (self.start, self.end, recurrence_id_prop.dt)
            )
            if start < recurrence_id:
                add_to_stop = recurrence_id - start
            if start > recurrence_id:
                subtract_from_start = end - recurrence_id
        return subtract_from_start, add_to_stop

    @cached_property
    def move_recurrences_by(self) -> datetime.timedelta:
        """Occurrences of this component should be moved by this amount.

        Usually, the occurrence starts at the new start time.
        However, if we have a RANGE=THISANDFUTURE, we need to move the occurrence.

        RFC 5545:

            When the given recurrence instance is
            rescheduled, all subsequent instances are also rescheduled by the
            same time difference.  For instance, if the given recurrence
            instance is rescheduled to start 2 hours later, then all
            subsequent instances are also rescheduled 2 hours later.
            Similarly, if the duration of the given recurrence instance is
            modified, then all subsequence instances are also modified to have
            this same duration.
        """
        if self.this_and_future:
            recurrence_id_prop = self._component.get("RECURRENCE-ID")
            assert recurrence_id_prop, "RANGE=THISANDFUTURE implies RECURRENCE-ID."
            start, recurrence_id = make_comparable((self.start, recurrence_id_prop.dt))
            return start - recurrence_id
        return datetime.timedelta(0)


class EventAdapter(ComponentAdapter):
    """An icalendar event adapter."""

    @staticmethod
    def component_name() -> str:
        """The icalendar component name."""
        return "VEVENT"

    @property
    def end_property(self) -> str:
        """DTEND"""
        return "DTEND"

    @cached_property
    def start(self) -> Time:
        """Return DTSTART"""
        # Arguably, it may be considered a feature that this breaks
        # if no DTSTART is set
        return self._component["DTSTART"].dt

    @cached_property
    def end(self) -> Time:
        """Yield DTEND or calculate the end of the event based on
        DTSTART and DURATION.
        """
        ## an even may have DTEND or DURATION, but not both
        end = self._component.get("DTEND")
        if end is not None:
            return end.dt
        duration = self._component.get("DURATION")
        if duration is not None:
            return normalize_pytz(self._component["DTSTART"].dt + duration.dt)
        return self._component["DTSTART"].dt


class TodoAdapter(ComponentAdapter):
    """Unified access to TODOs."""

    @staticmethod
    def component_name() -> str:
        """The icalendar component name."""
        return "VTODO"

    @property
    def end_property(self) -> str:
        """DUE"""
        return "DUE"

    @cached_property
    def start(self) -> Time:
        """Return DTSTART if it set, do not panic if it's not set."""
        ## easy case - DTSTART set
        start = self._component.get("DTSTART")
        if start is not None:
            return start.dt
        ## Tasks may have DUE set, but no DTSTART.
        ## Let's assume 0 duration and return the DUE
        due = self._component.get("DUE")
        if due is not None:
            return due.dt

        ## Assume infinite time span if neither is given
        ## (see the comments under _get_event_end)
        return DATE_MIN_DT

    @cached_property
    def end(self) -> Time:
        """Return DUE or DTSTART+DURATION or something"""
        ## Easy case - DUE is set
        end = self._component.get("DUE")
        if end is not None:
            return end.dt

        dtstart = self._component.get("DTSTART")

        ## DURATION can be specified instead of DUE.
        duration = self._component.get("DURATION")
        ## It is no requirement that DTSTART is set.
        ## Perhaps duration is a time estimate rather than an indirect
        ## way to set DUE.
        if duration is not None and dtstart is not None:
            return normalize_pytz(self._component["DTSTART"].dt + duration.dt)

        ## According to the RFC, a VEVENT without an end/duration
        ## is to be considered to have zero duration.  Assuming the
        ## same applies to VTODO.
        if dtstart:
            return dtstart.dt

        ## The RFC says this about VTODO:
        ## > A "VTODO" calendar component without the "DTSTART" and "DUE" (or
        ## > "DURATION") properties specifies a to-do that will be associated
        ## > with each successive calendar date, until it is completed.
        ## It can be interpreted in different ways, though probably it may
        ## be considered equivalent with a DTSTART in the infinite past and DUE
        ## in the infinite future?
        return DATE_MAX_DT


class JournalAdapter(ComponentAdapter):
    """Apdater for journal entries."""

    @staticmethod
    def component_name() -> str:
        """The icalendar component name."""
        return "VJOURNAL"

    @property
    def end_property(self) -> str:
        """There is no end property"""
        return None

    @cached_property
    def start(self) -> Time:
        """Return DTSTART if it set, do not panic if it's not set."""
        ## according to the specification, DTSTART in a VJOURNAL is optional
        dtstart = self._component.get("DTSTART")
        if dtstart is not None:
            return dtstart.dt
        return DATE_MIN_DT

    @cached_property
    def end(self) -> Time:
        """The end time is the same as the start."""
        ## VJOURNAL cannot have a DTEND.  We should consider a VJOURNAL to
        ## describe one day if DTSTART is a date, and we can probably
        ## consider it to have zero duration if a timestamp is given.
        return self.start


class Occurrence:
    """A repetition of an event."""

    def __init__(
        self,
        adapter: ComponentAdapter,
        start: Time | None = None,
        end: Time | None | datetime.timedelta = None,
    ):
        """Create an event repetition.

        - source - the icalendar Event
        - start - the start date/datetime to replace
        - stop - the end date/datetime to replace
        """
        self._adapter = adapter
        self.start = adapter.start if start is None else start
        self.end = adapter.end if end is None else end

    def as_component(self, keep_recurrence_attributes: bool) -> Component:  # noqa: FBT001
        """Create a shallow copy of the source component and modify some attributes."""
        return self._adapter.as_component(
            self.start, self.end, keep_recurrence_attributes
        )

    def is_in_span(self, span_start: Time, span_stop: Time) -> bool:
        """Return whether the component is in the span."""
        return time_span_contains_event(span_start, span_stop, self.start, self.end)

    def __lt__(self, other: Occurrence) -> bool:
        """Compare two occurrences for sorting.

        See https://stackoverflow.com/a/4010558/1320237
        """
        self_start, other_start = make_comparable((self.start, other.start))
        return self_start < other_start

    @cached_property
    def id(self) -> ComponentID:
        """The id of the component."""
        recurrence_id = ((*self._adapter.recurrence_ids, self.start))[0]
        return (
            self._adapter.component_name(),
            self._adapter.uid,
            recurrence_id,
        )

    def __hash__(self) -> int:
        """Hash this for an occurrence."""
        return hash(self.id)

    def __eq__(self, other: Occurrence) -> bool:
        """self == other"""
        return self.id == other.id


class SelectComponents(ABC):
    """Abstract class to select components from a calendar."""

    @abstractmethod
    def collect_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect all components from the source grouped together into a series.

        suppress_errors - a list of errors that should be suppressed.
            A Series of events with such an error is removed from all results.
        """


class ComponentsWithName(SelectComponents):
    """This is a component collecttion strategy.

    Components can be collected in different ways.
    This class allows extension of the functionality by
    - subclassing to filter the resulting components
    - composition to combine collection behavior (see AllKnownComponents)
    """

    component_adapters = [EventAdapter, TodoAdapter, JournalAdapter]

    @cached_property
    def _component_adapters(self) -> dict[str : type[ComponentAdapter]]:
        """A mapping of component adapters."""
        return {
            adapter.component_name(): adapter for adapter in self.component_adapters
        }

    def __init__(
        self,
        name: str,
        adapter: type[ComponentAdapter] | None = None,
        series: type[Series] = Series,
        occurrence: type[Occurrence] = Occurrence,
    ) -> None:
        """Create a new way of collecting components.

        name - the name of the component to collect ("VEVENT", "VTODO", "VJOURNAL")
        adapter - the adapter to use for these components with that name
        series - the series class that hold a series of components
        occurrence - the occurrence class that creates the resulting components
        """
        if adapter is None:
            if name not in self._component_adapters:
                raise ValueError(
                    f'"{name}" is an unknown name for a '
                    'recurring component. '
                    f"I only know these: { ', '.join(self._component_adapters)}."
                )
            adapter = self._component_adapters[name]
        if occurrence is not Occurrence:
            _occurrence = occurrence

            class series(series):  # noqa: N801
                occurrence = _occurrence

        self._name = name
        self._series = series
        self._adapter = adapter

    def collect_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect all components from the source component.

        suppress_errors - a list of errors that should be suppressed.
            A Series of events with such an error is removed from all results.
        """
        components: dict[str, list[Component]] = defaultdict(list)  # UID -> components
        for component in source.walk(self._name):
            adapter = self._adapter(component)
            components[adapter.uid].append(adapter)
        result = []
        for components in components.values():
            with contextlib.suppress(suppress_errors):
                result.append(self._series(components))
        return result


class AllKnownComponents(SelectComponents):
    """Group all known components into series."""

    @property
    def _component_adapters(self) -> Sequence[ComponentAdapter]:
        """Return all known component adapters."""
        return ComponentsWithName.component_adapters

    @property
    def names(self) -> list[str]:
        """Return the names of the components to collect."""
        return [adapter.component_name() for adapter in self._component_adapters]

    def __init__(
        self,
        series: type[Series] = Series,
        occurrence: type[Occurrence] = Occurrence,
        collector: type[ComponentsWithName] = ComponentsWithName,
    ) -> None:
        """Collect all known components and overide the series and occurrence.

        series - the Series class to override that is queried for Occurrences
        occurrence - the occurrence class that creates the resulting components
        collector - if you want to override the SelectComponentsByName class
        """
        self._series = series
        self._occurrence = occurrence
        self._collector = collector

    def collect_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect the components from the source groups into a series."""
        result = []
        for name in self.names:
            collector = self._collector(
                name, series=self._series, occurrence=self._occurrence
            )
            result.extend(collector.collect_series_from(source, suppress_errors))
        return result


if sys.version_info >= (3, 10):
    T_COMPONENTS = Sequence[str | type[ComponentAdapter] | SelectComponents]
else:
    # see https://github.com/python/cpython/issues/86399#issuecomment-1093889925
    T_COMPONENTS = Sequence[str]


class CalendarQuery:
    """A calendar that can unfold its events at a certain time.

    Functions like at(), between() and after() can be used to query the
    selected components. If any malformed icalendar information is found,
    an InvalidCalendar exception is raised. For other bad arguments, you
    should expect a ValueError.

    suppressed_errors - a list of errors to suppress when
        skip_bad_series is True

    component_adapters - a list of component adapters
    """

    suppressed_errors = [BadRuleStringFormat, PeriodEndBeforeStart]
    ComponentsWithName = ComponentsWithName

    def __init__(
        self,
        calendar: Component,
        keep_recurrence_attributes: bool = False,  # noqa: FBT001
        components: T_COMPONENTS = ("VEVENT",),
        skip_bad_series: bool = False,  # noqa: FBT001
    ):
        """Create an unfoldable calendar from a given calendar.

        calendar - an icalendar component - probably a calendar -
            from which occurrences will be calculated
        keep_recurrence_attributes - whether to keep values
            in the results that are used for calculation
        skip_bad_events - whether to skip a series of components that
            contains errors. This skips self.suppressed_errors.
        """
        self.keep_recurrence_attributes = keep_recurrence_attributes
        if calendar.get("CALSCALE", "GREGORIAN") != "GREGORIAN":
            # https://www.kanzaki.com/docs/ical/calscale.html
            raise InvalidCalendar("Only Gregorian calendars are supported.")

        self.series: list[Series] = []  # component
        self._skip_errors = tuple(self.suppressed_errors) if skip_bad_series else ()
        for component_adapter_id in components:
            if isinstance(component_adapter_id, str):
                component_adapter = self.ComponentsWithName(component_adapter_id)
            else:
                component_adapter = component_adapter_id
            self.series.extend(
                component_adapter.collect_series_from(calendar, self._skip_errors)
            )

    @staticmethod
    def to_datetime(date: DateArgument):
        """Convert date inputs of various sorts into a datetime object."""
        if isinstance(date, int):
            date = (date,)
        if isinstance(date, tuple):
            date += (1,) * (3 - len(date))
            return datetime.datetime(*date)  # noqa: DTZ001
        if isinstance(date, str):
            # see https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
            if len(date) == 8:
                return datetime.datetime.strptime(date, "%Y%m%d")  # noqa: DTZ007
            return datetime.datetime.strptime(date, "%Y%m%dT%H%M%SZ")  # noqa: DTZ007
        return date

    def all(self) -> Generator[Component]:
        """Generate all Components.

        The Components are sorted from the first to the last Occurrence.
        Calendars can contain millions of Occurrences. This iterates
        safely across all of them
        """
        # MAX and MIN values may change in the future
        return self.after(DATE_MIN_DT)

    _DELTAS = [
        datetime.timedelta(days=1),
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=1),
        datetime.timedelta(seconds=1),
    ]

    def at(self, date: DateArgument):
        """Return all events within the next 24 hours of starting at the given day.

        - date can be a year like (2019,) or 2099
        - a month like (2019, 1) for January of 2019
        - a day like (2019, 1, 1) for the first of January 2019
        - a day with hours, (2019, 1, 1, 1)
        - a day with minutes, (2019, 1, 1, 1, 1)
        - a day with seconds, (2019, 1, 1, 1, 1, 1)
        """
        if isinstance(date, int):
            date = (date,)
        if isinstance(date, str):
            if len(date) != 8 or not date.isdigit():
                raise ValueError(f"Format yyyymmdd expected for {date!r}.")
            date = (int(date[:4], 10), int(date[4:6], 10), int(date[6:]))
        if isinstance(date, datetime.datetime):
            return self.between(date, date)
        if isinstance(date, datetime.date):
            return self.between(date, date + datetime.timedelta(days=1))
        if len(date) == 1:
            return self.between((date[0], 1, 1), (date[0] + 1, 1, 1))
        if len(date) == 2:
            year, month = date
            if month == 12:
                return self.between((year, 12, 1), (year + 1, 1, 1))
            return self.between((year, month, 1), (year, month + 1, 1))
        dt = self.to_datetime(date)
        return self._between(dt, dt + self._DELTAS[len(date) - 3])

    def between(self, start: DateArgument, stop: DateArgument | datetime.timedelta):
        """Return events at a time between start (inclusive) and end (inclusive)"""
        start = self.to_datetime(start)
        stop = (
            start + stop
            if isinstance(stop, datetime.timedelta)
            else self.to_datetime(stop)
        )
        return self._between(start, stop)

    def _occurrences_to_components(
        self, occurrences: list[Occurrence]
    ) -> list[Component]:
        """Map occurrences to components."""
        return [
            occurrence.as_component(self.keep_recurrence_attributes)
            for occurrence in occurrences
        ]

    def _between(self, start: Time, end: Time) -> list[Component]:
        """Return the occurrences between the start and the end."""
        return self._occurrences_to_components(self._occurrences_between(start, end))

    def _occurrences_between(self, start: Time, end: Time) -> list[Occurrence]:
        """Return the components between the start and the end."""
        occurrences: list[Occurrence] = []
        for series in self.series:
            with contextlib.suppress(self._skip_errors):
                occurrences.extend(series.between(start, end))
        return occurrences

    def after(self, earliest_end: DateArgument) -> Generator[Component]:
        """
        Return an iterator over the next events that happen during or after
        the earliest_end.
        """
        time_span = datetime.timedelta(days=1)
        min_time_span = datetime.timedelta(minutes=15)
        earliest_end = self.to_datetime(earliest_end)
        done = False
        result_ids: set[ComponentID] = set()

        while not done:
            try:
                next_end = earliest_end + time_span
            except OverflowError:
                # We ran to the end
                next_end = DATE_MAX_DT
                if compare_greater(earliest_end, next_end):
                    return  # we might run too far
                done = True
            occurrences = self._occurrences_between(earliest_end, next_end)
            occurrences.sort()
            for occurrence in occurrences:
                if occurrence.id not in result_ids:
                    yield occurrence.as_component(self.keep_recurrence_attributes)
                    result_ids.add(occurrence.id)
            # prepare next query
            time_span = max(
                time_span / 2 if occurrences else time_span * 2,
                min_time_span,
            )  # binary search to improve speed
            earliest_end = next_end

    def count(self) -> int:
        """Return the amount of recurring components in this calendar."""
        i = 0
        for _ in self.all():
            i += 1
        return i


def of(
    a_calendar: Component,
    keep_recurrence_attributes=False,
    components: T_COMPONENTS = ("VEVENT",),
    skip_bad_series: bool = False,  # noqa: FBT001
    calendar_query: type[CalendarQuery] = CalendarQuery,
) -> CalendarQuery:
    """Unfold recurring events of a_calendar

    - a_calendar is an icalendar VCALENDAR component or something like that.
    - keep_recurrence_attributes - whether to keep attributes that are only used
      to calculate the recurrence.
    - components is a list of component type names of which the recurrences
      should be returned. This can also be instances of SelectComponents.
    - skip_bad_series - whether to skip a series of components that contains
      errors.
    - calendar_query - The calendar query class to use.
    """
    a_calendar = x_wr_timezone.to_standard(a_calendar)
    return calendar_query(
        a_calendar, keep_recurrence_attributes, components, skip_bad_series
    )


__all__ = [
    "of",
    "InvalidCalendar",
    "PeriodEndBeforeStart",
    "BadRuleStringFormat",
    "is_pytz",
    "DATE_MIN",
    "DATE_MAX",
    "CalendarQuery",
    "ComponentAdapter",
    "EventAdapter",
    "TodoAdapter",
    "JournalAdapter",
    "Time",
    "RecurrenceID",
    "RecurrenceIDs",
    "SelectComponents",
    "ComponentsWithName",
    "T_COMPONENTS",
]
