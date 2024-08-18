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
import functools
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Generator, Optional, Sequence, Union, Callable

import x_wr_timezone
from dateutil.rrule import rruleset, rrulestr
from icalendar.prop import vDDDTypes
from functools import wraps

if TYPE_CHECKING:
    from icalendar.cal import Component
    Time = Union[datetime.date, datetime.datetime]
    DateArgument= tuple[int] | Time | str | int
    from dateutil.rrule import rrule


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

    def __init__(self, message:str , start:Time, end:Time):
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


def timestamp(dt : datetime.datetime) -> float:
    """Return the time stamp of a datetime"""
    return dt.timestamp()


NEGATIVE_RRULE_COUNT_REGEX = re.compile(r"COUNT=-\d+;?")


def convert_to_date(date: Time) -> datetime.date:
    """Converts a date or datetime to a date"""
    return datetime.date(date.year, date.month, date.day)


def convert_to_datetime(date: Time, tzinfo: Optional[datetime.tzinfo]):  # noqa: UP007
    """Converts a date to a datetime"""
    if isinstance(date, datetime.datetime):
        if date.tzinfo is None:
            if tzinfo is not None:
                if is_pytz(tzinfo):
                    return tzinfo.localize(date)
                return date.replace(tzinfo=tzinfo)
        elif tzinfo is None:
            return date.replace(tzinfo=None)
        return date
    if isinstance(date, datetime.date):
        return datetime.datetime(date.year, date.month, date.day, tzinfo=tzinfo)
    return date


def time_span_contains_event(
    span_start : Time,
    span_stop : Time,
    event_start : Time,
    event_stop : Time,
    comparable:bool=False,  # noqa: FBT001
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


def make_comparable(dates:Sequence[Time]) -> list[Time]:
    """Make an list or tuple of dates comparable.

    Returns an list.
    """
    tzinfo = None
    for date in dates:
        tzinfo = getattr(date, "tzinfo", None)
        if tzinfo is not None:
            break
    return [convert_to_datetime(date, tzinfo) for date in dates]


def compare_greater(date1:Time, date2:Time) -> bool:
    """Compare two dates if date1 > date2 and make them comparable before."""
    date1, date2 = make_comparable((date1, date2))
    return date1 > date2


def cmp(date1:Time, date2:Time) -> int:
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


def is_pytz(tzinfo: datetime.tzinfo):
    """Whether the time zone requires localize() and normalize().

    pytz requires these funtions to be used in order to correctly use the
    time zones after operations.
    """
    return hasattr(tzinfo, "localize")


def cached_property(func:Callable):
    """Cache the property value for speed up."""
    name = f"_cached_{func.__name__}"
    not_found = object()
    @property
    @wraps(func)
    def cached_property(self:object):
        value = self.__dict__.get(name, not_found)
        if value is not_found:
            self.__dict__[name] = value = func(self)
        return value
    return cached_property
    



class Series:
    """Base class for components that result in a series of occurrences."""

    def __init__(self, components: Sequence[ComponentAdapter]):
        """Create an component which may have repetitions in it."""
        if len(components) == 0:
            raise ValueError("No components given to calculate a series.")
        self.modifications : dict[datetime.date | None, ComponentAdapter] = {}  # RECURRENCE-ID -> adapter
        for component in components:
            recurrence_id = component.recurrence_id
            other_component = self.modifications.get(recurrence_id)
            if other_component is None or other_component.sequence < component.sequence:
                self.modifications[recurrence_id] = component
        del component
        self.core = self.modifications.pop(None, None)
        if self.core is None:
            raise InvalidCalendar(f"The event definition for {components[0].uid} only contain modifications.")
        # Setup complete. Now we calculate the series
        self.start = self.original_start = self.core.start
        self.end = self.original_end = self.core.end
        self.exdates = []
        self.check_exdates : set[datetime.date] = set()
        self.replace_ends : dict[datetime.date, Time] = {}  # for periods
        for exdate in self.core.exdates:
            self.exdates.append(exdate)
            self.check_exdates.add(convert_to_date(exdate))
        self.rdates : list[Time] = []
        for rdate in self.core.rdates:
            if isinstance(rdate, tuple):
                # we have a period as rdate
                self.rdates.append(rdate[0])
                # TODO: Test RDATE Period with duration
                self.replace_ends[convert_to_date(rdate[0])] = rdate[1]
            else:
                # we have a date/datetime
                self.rdates.append(rdate)

        self.make_all_dates_comparable()

        self.rule = rruleset(cache=True)
        self.until : Time | None = None
        for rrule_string in self.core.rrules:
            _rrule : rrule = self.create_rule_with_start(rrule_string)
            self.rule.rrule(_rrule)
            if _rrule.until and (
                not self.until or compare_greater(_rrule.until, self.until)
            ):
                self.until = _rrule.until

        for exdate in self.exdates:
            self.rule.exdate(exdate)
        for rdate in self.rdates:
            self.rule.rdate(rdate)

        if not self.until or not compare_greater(self.start, self.until):
            self.rule.rdate(self.start)


    def create_rule_with_start(self, rule_string):
        """Helper to create an rrule from a rule_string

        The rrule is starting at the start of the component.
        Since the creation is a bit more complex, this function handles special cases.
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
                rule_list[0] + rule_list[1][date_end_index:] + ";UNTIL=" + until_string
            )
            return self.rrulestr(new_rule_string)

    def rrulestr(self, rule_string):
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

    def _get_rrule_until(self, rrule):
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
        self.rdates = [convert_to_datetime(rdate, self.tzinfo) for rdate in self.rdates]
        self.exdates = [
            convert_to_datetime(exdate, self.tzinfo) for exdate in self.exdates
        ]

    def between(self, span_start: Time, span_stop: Time) -> Generator[Occurrence]:
        """components between the start (inclusive) and end (exclusive)"""
        # make dates comparable, rrule converts them to datetimes
        span_start = convert_to_datetime(span_start, self.tzinfo)
        span_stop = convert_to_datetime(span_stop, self.tzinfo)
        if compare_greater(span_start, self.start):
            # do not exclude an component if it spans across the time span
            span_start -= self.core.duration
        returned_starts : set[Time] = set()
        # NOTE: If in the following line, we get an error, datetime and date
        # may still be mixed because RDATE, EXDATE, start and rule.
        for start in self.rule.between(span_start, span_stop, inc=True):
            if isinstance(start, datetime.datetime) and is_pytz(start.tzinfo):
                # update the time zone in case of summer/winter time change
                start = start.tzinfo.localize(start.replace(tzinfo=None))  # noqa: PLW2901
                # We could now well be out of bounce of the end of the UNTIL
                # value. This is tested by test/test_issue_20_exdate_ignored.py.
                if (
                    self.until is not None
                    and start > self.until
                    and start not in self.rdates
                ):
                    continue
            start_date = convert_to_date(start)
            if start_date in self.check_exdates:
                continue
            component = self.modifications.get(start_date, self.core)
            # TODO: Test: use time from event modification over RDATE
            stop = self.replace_ends.get(start_date, start + component.duration)
            if start in returned_starts:
                continue
            returned_starts.add(start)
            occurrence = Occurrence(
                component,
                self.convert_to_original_type(start),
                self.convert_to_original_type(stop)
            )
            if occurrence.is_in_span(span_start, span_stop):
                yield occurrence

    def convert_to_original_type(self, date):
        """Convert a date back if this is possible.

        Dates may get converted to datetimes to make calculations possible.
        This reverts the process where possible so that Repetitions end
        up with the type (date/datetime) that was specified in the icalendar
        component.
        """
        if not isinstance(self.original_start, datetime.datetime) and not isinstance(
            self.original_end,
            datetime.datetime,
        ):
            return convert_to_date(date)
        return date

class ComponentAdapter(ABC):
    """A unified interface to work with icalendar components."""
    
    ATTRIBUTES_TO_DELETE_ON_COPY = ["RRULE", "RDATE", "EXDATE"]

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
    def uid(self) -> str:
        """The UID of a component.
        
        UID is required by RFC5545.
        If the UID is absent, we use the Python ID.
        """
        return self._component.get("UID", str(id(self._component)))
        
    @classmethod
    def collect_components(cls, source: Component) -> Sequence[Series]:
        """Collect all components from the source component."""
        components : dict[str, list[Component]] = defaultdict(list) # UID -> components
        for component in source.walk(cls.component_name()):
            adapter = cls(component)
            components[adapter.uid].append(adapter)
        return [Series(components) for components in components.values()]

    def as_component(self, start: Time, stop:Time, keep_recurrence_attributes: bool):  # noqa: FBT001
        """Create a shallow copy of the source event and modify some attributes."""
        copied_component = self._component.copy()
        copied_component["DTSTART"] = vDDDTypes(start)
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
    def recurrence_id(self) -> datetime.date | None:
        """The recurrence id of the component or None.
        
        The basic event definiton has no recurrence id.
        All modifications have recurrence ids.
        """
        recurrence_id = self._component.get("RECURRENCE-ID")
        if recurrence_id is None:
            return None
        return convert_to_date(recurrence_id.dt)
    
    @cached_property
    def sequence(self) -> int:
        """The sequence in the history of modification.
        
        The sequence is negative if none was found.
        """
        return self._component.get("SEQUENCE", -1)
    
    def __repr__(self)->str:
        """Debug representation with more info."""
        return f"<{self.__class__.__name__} UID={self.uid} start={self.start} recurrence_id={self.recurrence_id} sequence={self.sequence} end={self.end}>"

    @cached_property
    def exdates(self) -> list[Time]:
        """A list of exdates."""
        result : list[Time] = []
        exdates = self._component.get("EXDATE", [])
        for exdates in (exdates,) if not isinstance(exdates, list) else exdates:
            result.extend(exdate.dt for exdate in exdates.dts)
        return result

    @cached_property
    def rrules(self) -> list[str]:
        """A list of rrules of this component."""
        rrules = self._component.get("RRULE", None)
        if not rrules:
            return []
        if not isinstance(rrules, list):
            rrules = [rrules]
        else:
            _dedup_rules = []
            for _rule in rrules:
                if _rule not in _dedup_rules:
                    _dedup_rules.append(_rule)
            rrules = _dedup_rules
        return [rrule.to_ical().decode() for rrule in rrules]

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
            return self._component["DTSTART"].dt + duration.dt
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
            return self._component["DTSTART"].dt + duration.dt

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

    ATTRIBUTES_TO_DELETE_ON_COPY = ["RRULE", "RDATE", "EXDATE"]

    def __init__(
        self,
        adapter: ComponentAdapter,
        start: Time,
        stop:Time
    ):
        """Create an event repetition.

        - source - the icalendar Event
        - start - the start date/datetime
        - stop - the end date/datetime
        """
        self._adapter = adapter
        self.start = start
        self.stop = stop

    def as_component(self, keep_recurrence_attributes:bool) -> Component:  # noqa: FBT001
        """Create a shallow copy of the source component and modify some attributes."""
        return self._adapter.as_component(self.start, self.stop, keep_recurrence_attributes)

    def is_in_span(self, span_start:Time, span_stop:Time) -> bool:
        """Return whether the event is in the span."""
        return time_span_contains_event(span_start, span_stop, self.start, self.stop)




class UnfoldableCalendar:
    """A calendar that can unfold its events at a certain time.

    Functions like at(), between() and after() can be used to query the
    selected components. If any malformed icalendar information is found,
    an InvalidCalendar exception is raised. For other bad arguments, you
    should expect a ValueError.
    """

    component_adapters : dict[str: type[ComponentAdapter]] = {
        EventAdapter.component_name(): EventAdapter,
        TodoAdapter.component_name(): TodoAdapter,
        JournalAdapter.component_name(): JournalAdapter,
    }

    def __init__(
        self,
        calendar:Component,
        keep_recurrence_attributes:bool=False,  # noqa: FBT001
        components:Sequence[str|type[ComponentAdapter]]=("VEVENT",),
        skip_bad_events:bool=False,  # noqa: FBT001
    ):
        """Create an unfoldable calendar from a given calendar."""
        self.keep_recurrence_attributes = keep_recurrence_attributes
        self.skip_bad_events = skip_bad_events
        if calendar.get("CALSCALE", "GREGORIAN") != "GREGORIAN":
            # https://www.kanzaki.com/docs/ical/calscale.html
            raise InvalidCalendar("Only Gregorian calendars are supported.")

        self.series : list[Series] = []  # component
        for component_adapter_id in components:
            if isinstance(component_adapter_id, str):
                if component_adapter_id not in self.component_adapters:
                    raise ValueError(
                        f'"{component_adapter_id}" is an unknown name for a '
                        'recurring component.'
                        f"I only know these: { ', '.join(self.component_adapters)}."
                    )
                component_adapter = self.component_adapters[component_adapter_id]
            else:
                component_adapter = component_adapter_id
            self.series.extend(component_adapter.collect_components(calendar))

    @staticmethod
    def to_datetime(date:DateArgument):
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

    def all(self):
        """Returns all events.

        I personally do not recommend to use this because
        this method is not documented and you may end up with lots of events
        most of which you may not use anyway.
        """
        # MAX and MIN values may change in the future
        return self._between(DATE_MIN_DT, DATE_MAX_DT)

    _DELTAS = [
        datetime.timedelta(days=1),
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=1),
        datetime.timedelta(seconds=1),
    ]

    def at(self, date:DateArgument):
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

    def between(self, start:DateArgument, stop:DateArgument):
        """Return events at a time between start (inclusive) and end (inclusive)"""
        return self._between(self.to_datetime(start), self.to_datetime(stop))
    
    def _between(self, start: Time, end: Time):
        """Return the components between the start and the end."""
        occurrences : list[Occurrence] = []
        for series in self.series:
            occurrences.extend(series.between(start, end))
        return [occurrence.as_component(self.keep_recurrence_attributes) for occurrence in occurrences]

    def after(self, earliest_end):
        """
        Return an iterator over the next events that happen during or after
        the earliest_end.
        """
        time_span = datetime.timedelta(days=1)
        min_time_span = datetime.timedelta(minutes=15)
        earliest_end = self.to_datetime(earliest_end)
        done = False
        returned_events = set()  # (UID, recurrence-id)

        def cmp_event(event1, event2):
            """Cmp for events"""
            return cmp(event1["DTSTART"].dt, event2["DTSTART"].dt)

        while not done:
            try:
                next_end = earliest_end + time_span
            except OverflowError:
                # We ran to the end
                next_end = DATE_MAX_DT
                if compare_greater(earliest_end, next_end):
                    return  # we might run too far
                done = True
            events = self._between(earliest_end, next_end)
            events.sort(
                key=functools.cmp_to_key(cmp_event),
            )  # see https://docs.python.org/3/howto/sorting.html#comparison-functions
            for event in events:
                event_id = self._get_event_id(event)
                if event_id not in returned_events:
                    yield event
                    returned_events.add(event_id)
            # prepare next query
            time_span = max(
                time_span / 2 if events else time_span * 2,
                min_time_span,
            )  # binary search to improve speed
            earliest_end = next_end

    @property
    @contextlib.contextmanager
    def __handle_invalid_calendar_errors(self):
        """
        Private context manager which catch `InvalidCalendar` exceptions and
        silently skip them if `self.skip_bad_events` is `True`

        Usage:
        with self.__handle_invalid_calendar_errors:
            ...
        """
        try:
            yield
        except InvalidCalendar:
            if not self.skip_bad_events:
                raise


def of(
    a_calendar,
    keep_recurrence_attributes=False,
    components:Sequence[str|type[ComponentAdapter]]=("VEVENT",),
    skip_bad_events:bool=False,  # noqa: FBT001
) -> UnfoldableCalendar:
    """Unfold recurring events of a_calendar

    - a_calendar is an icalendar VCALENDAR component or something like that.
    - keep_recurrence_attributes - whether to keep attributes that are only used
      to calculate the recurrence.
    - components is a list of component type names of which the recurrences
      should be returned.
    """
    a_calendar = x_wr_timezone.to_standard(a_calendar)
    return UnfoldableCalendar(
        a_calendar, keep_recurrence_attributes, components, skip_bad_events
    )


__all__ = [
    "of",
    "InvalidCalendar",
    "PeriodEndBeforeStart",
    "BadRuleStringFormat",
    "is_pytz",
    "DATE_MIN",
    "DATE_MAX",
    "UnfoldableCalendar",
    "ComponentAdapter",
]
