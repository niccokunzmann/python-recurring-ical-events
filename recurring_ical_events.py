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
from collections import defaultdict

import x_wr_timezone
from dateutil.rrule import rruleset, rrulestr
from icalendar.prop import vDDDTypes


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

    def __init__(self, message, start, end):
        """Create a new PeriodEndBeforeStart error."""
        super().__init__(message)
        self._start = start
        self._end = end

    @property
    def start(self):
        """The start of the component's period."""
        return self._start

    @property
    def end(self):
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


def timestamp(dt):
    """Return the time stamp of a datetime"""
    return dt.timestamp()


NEGATIVE_RRULE_COUNT_REGEX = re.compile(r"COUNT=-\d+;?")


def convert_to_date(date):
    """Converts a date or datetime to a date"""
    return datetime.date(date.year, date.month, date.day)


def convert_to_datetime(date, tzinfo):
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
    span_start,
    span_stop,
    event_start,
    event_stop,
    comparable=False,
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


def make_comparable(dates):
    """Make an list or tuple of dates comparable.

    Returns an list.
    """
    tzinfo = None
    for date in dates:
        tzinfo = getattr(date, "tzinfo", None)
        if tzinfo is not None:
            break
    return [convert_to_datetime(date, tzinfo) for date in dates]


def compare_greater(date1, date2):
    """Compare two dates if date1 > date2 and make them comparable before."""
    date1, date2 = make_comparable((date1, date2))
    return date1 > date2


def cmp(date1, date2):
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


def is_pytz(tzinfo):
    """Whether the time zone requires localize() and normalize().

    pytz requires these funtions to be used in order to correctly use the
    time zones after operations.
    """
    return hasattr(tzinfo, "localize")


class Repetition:
    """A repetition of an event."""

    ATTRIBUTES_TO_DELETE_ON_COPY = ["RRULE", "RDATE", "EXDATE"]

    def __init__(
        self,
        source,
        start,
        stop,
        keep_recurrence_attributes=False,
        end_prop="DTEND",
    ):
        """Create an event repetition.

        - source - the icalendar Event
        - start - the start date/datetime
        - stop - the end date/datetime
        - keep_recurrence_attributes - whether to copy or delete attributes
            mentioned in ATTRIBUTES_TO_DELETE_ON_COPY
        """
        self.source = source
        self.start = start
        self.stop = stop
        self.end_prop = end_prop
        self.keep_recurrence_attributes = keep_recurrence_attributes

    def as_vevent(self):
        """Create a shallow copy of the source event and modify some attributes."""
        revent = self.source.copy()
        revent["DTSTART"] = vDDDTypes(self.start)
        revent[self.end_prop] = vDDDTypes(self.stop)
        if not self.keep_recurrence_attributes:
            for attribute in self.ATTRIBUTES_TO_DELETE_ON_COPY:
                if attribute in revent:
                    del revent[attribute]
        for subcomponent in self.source.subcomponents:
            revent.add_component(subcomponent)
        return revent

    def is_in_span(self, span_start, span_stop):
        """Return whether the event is in the span."""
        return time_span_contains_event(span_start, span_stop, self.start, self.stop)

    def __repr__(self):
        """Debug representation with more info."""
        return "{}({{'UID':{}...}}, {}, {})".format(
            self.__class__.__name__,
            self.source.get("UID"),
            self.start,
            self.stop,
        )


class RepeatedComponent:
    """Base class for RepeatedEvent, RepeatedJournal and RepeatedTodo"""

    def __init__(self, component, keep_recurrence_attributes=False):
        """Create an component which may have repetitions in it.

        - component - the icalendar component
        - keep_recurrence_attributes whether to copy or delete attributes
          in repetitions.
        """
        self.component = component
        self.start = self.original_start = self.start_of(component)
        self.end = self.original_end = self.end_of(component)
        self.keep_recurrence_attributes = keep_recurrence_attributes
        self.exdates = []
        self.exdates_utc = set()
        self.replace_ends = {}  # DTSTART -> DTEND # for periods
        exdates = component.get("EXDATE", [])
        for exdates in (exdates,) if not isinstance(exdates, list) else exdates:
            for exdate in exdates.dts:
                self.exdates.append(exdate.dt)
                self.exdates_utc.add(self._unify_exdate(exdate.dt))
        self.rdates = []
        rdates = component.get("RDATE", [])
        for rdates in (rdates,) if not isinstance(rdates, list) else rdates:
            for rdate in rdates.dts:
                if isinstance(rdate.dt, tuple):
                    # we have a period as rdate
                    self.rdates.append(rdate.dt[0])
                    self.replace_ends[timestamp(rdate.dt[0])] = rdate.dt[1]
                else:
                    # we have a date/datetime
                    self.rdates.append(rdate.dt)

        self.make_all_dates_comparable()

        self.duration = self.end - self.start
        self.rule = rruleset(cache=True)
        _component_rules = component.get("RRULE", None)
        self.until = None
        if _component_rules:
            if not isinstance(_component_rules, list):
                _component_rules = [_component_rules]
            else:
                _dedup_rules = []
                for _rule in _component_rules:
                    if _rule not in _dedup_rules:
                        _dedup_rules.append(_rule)
                _component_rules = _dedup_rules

            for _rule in _component_rules:
                rrule = self.create_rule_with_start(_rule.to_ical().decode())
                self.rule.rrule(rrule)
                if rrule.until and (
                    not self.until or compare_greater(rrule.until, self.until)
                ):
                    self.until = rrule.until

        for exdate in self.exdates:
            self.rule.exdate(exdate)
        for rdate in self.rdates:
            self.rule.rdate(rdate)

        if not self.until or not compare_greater(self.start, self.until):
            self.rule.rdate(self.start)

    @property
    def sequence(self) -> int:
        """The sequence number in the order of edits. Greater means later."""
        return int(self.component.get("SEQUENCE", 0))

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

    def _unify_exdate(self, dt):
        """
        Return a unique string for the datetime which is used to
        compare it with exdates.
        """
        if isinstance(dt, datetime.datetime):
            return timestamp(dt)
        return dt

    def within_days(self, span_start, span_stop):
        """
        Yield component Repetitions between the start (inclusive)
        and end (exclusive) of the time span.
        """
        # make dates comparable, rrule converts them to datetimes
        span_start = convert_to_datetime(span_start, self.tzinfo)
        span_stop = convert_to_datetime(span_stop, self.tzinfo)
        if compare_greater(span_start, self.start):
            # do not exclude an component if it spans across the time span
            span_start -= self.duration
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
            if (
                self._unify_exdate(start) in self.exdates_utc
                or start.date() in self.exdates_utc
            ):
                continue
            stop = self.replace_ends.get(timestamp(start), start + self.duration)
            yield Repetition(
                self.component,
                self.convert_to_original_type(start),
                self.convert_to_original_type(stop),
                self.keep_recurrence_attributes,
                self.end_prop,
            )

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

    def is_recurrence(self):
        """Whether this is a recurrence/modification of an event."""
        return "RECURRENCE-ID" in self.component

    def as_single_event(self) -> Repetition | None:
        """Return as a singe event with no recurrences."""
        for repetition in self.within_days(self.start, self.start):
            return repetition
        return None

    @property
    def id(self):
        """The ID of this component.

        If the component has no UID, it is assumed to be different from other
        components.
        """
        return self.id_of(self.component)

    @classmethod
    def id_of(cls, component):
        """The ID of this component.

        If the component has no UID, it is assumed to be different from other
        components.
        """
        rid = (
            component.get("RECURRENCE-ID").dt
            if "RECURRENCE-ID" in component
            else cls.start_of(component)
        )
        return (
            component.name,
            component.get("UID", id(component)),
            rid,
        )


class RepeatedEvent(RepeatedComponent):
    """An event with repetitions created from an icalendar event."""

    end_prop = "DTEND"

    @classmethod
    def start_of(cls, component):
        """Return DTSTART"""
        # Arguably, it may be considered a feature that this breaks
        # if no DTSTART is set
        return component["DTSTART"].dt

    @classmethod
    def end_of(cls, component):
        """
        Yield DTEND or calculate the end of the event based on
        DTSTART and DURATION.
        """
        ## an even may have DTEND or DURATION, but not both
        end = component.get("DTEND")
        if end is not None:
            return end.dt
        duration = component.get("DURATION")
        if duration is not None:
            return component["DTSTART"].dt + duration.dt
        return component["DTSTART"].dt


class RepeatedTodo(RepeatedComponent):
    end_prop = "DUE"

    @classmethod
    def start_of(cls, component):
        """Return DTSTART if it set, do not panic if it's not set."""
        ## easy case - DTSTART set
        start = component.get("DTSTART")
        if start is not None:
            return start.dt
        ## Tasks may have DUE set, but no DTSTART.
        ## Let's assume 0 duration and return the DUE
        due = component.get("DUE")
        if due is not None:
            return due.dt

        ## Assume infinite time span if neither is given
        ## (see the comments under _get_event_end)
        return DATE_MIN_DT

    @classmethod
    def end_of(cls, component):
        """Return DUE or DTSTART+DURATION or something"""
        ## Easy case - DUE is set
        end = component.get("DUE")
        if end is not None:
            return end.dt

        dtstart = component.get("DTSTART")

        ## DURATION can be specified instead of DUE.
        duration = component.get("DURATION")
        ## It is no requirement that DTSTART is set.
        ## Perhaps duration is a time estimate rather than an indirect
        ## way to set DUE.
        if duration is not None and dtstart is not None:
            return component["DTSTART"].dt + duration.dt

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
        return datetime.date(*DATE_MAX)


class RepeatedJournal(RepeatedComponent):
    end_prop = ""

    @classmethod
    def start_of(cls, component):
        """Return DTSTART if it set, do not panic if it's not set."""
        ## according to the specification, DTSTART in a VJOURNAL is optional
        dtstart = component.get("DTSTART")
        if dtstart is not None:
            return dtstart.dt
        return DATE_MIN_DT

    ## VJOURNAL cannot have a DTEND.  We should consider a VJOURNAL to
    ## describe one day if DTSTART is a date, and we can probably
    ## consider it to have zero duration if a timestamp is given.
    end_of = start_of


# The minimum value accepted as date (pytz + zoneinfo)
DATE_MIN = (1970, 1, 1)
DATE_MIN_DT = datetime.date(*DATE_MIN)
# The maximum value accepted as date (pytz + zoneinfo)
DATE_MAX = (2038, 1, 1)
DATE_MAX_DT = datetime.date(*DATE_MAX)


class UnfoldableCalendar:
    """A calendar that can unfold its events at a certain time.

    Functions like at(), between() and after() can be used to query the
    selected components. If any malformed icalendar information is found,
    an InvalidCalendar exception is raised. For other bad arguments, you
    should expect a ValueError.
    """

    recurrence_calculators = {
        "VEVENT": RepeatedEvent,
        "VTODO": RepeatedTodo,
        "VJOURNAL": RepeatedJournal,
    }
    skip_bad_events = False

    def __init__(
        self,
        calendar,
        keep_recurrence_attributes=False,
        components=None,
        skip_bad_events=None,
    ):
        """Create an unfoldable calendar from a given calendar."""
        if calendar.get("CALSCALE", "GREGORIAN") != "GREGORIAN":
            # https://www.kanzaki.com/docs/ical/calscale.html
            raise InvalidCalendar("Only Gregorian calendars are supported.")

        if skip_bad_events is not None:
            self.skip_bad_events = skip_bad_events

        self.repetitions = {}  # id -> component
        components = components or ["VEVENT"]
        for component_name in components:
            if component_name not in self.recurrence_calculators:
                recurrence_calculators_str = ", ".join(self.recurrence_calculators)
                raise ValueError(
                    f'"{component_name}" is an unknown name for a recurring component.'
                    f"I only know these: {recurrence_calculators_str}."
                )

            recurrence_calculator = self.recurrence_calculators[component_name]
            for event in calendar.walk(component_name):
                with self.__handle_invalid_calendar_errors:
                    recurring_component = recurrence_calculator(
                        event, keep_recurrence_attributes
                    )
                    rid = self._get_event_id(event)
                    # TODO: This is a little off: The calendar merges the
                    #       events but actually that could be done by the
                    #       components themselves.
                    if (
                        rid not in self.repetitions
                        or recurring_component.sequence > self.repetitions[rid].sequence
                    ):
                        # we have to replace a later edit
                        self.repetitions[rid] = recurring_component

    @staticmethod
    def to_datetime(date):
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
        return self.between(DATE_MIN, DATE_MAX)

    _DELTAS = [
        datetime.timedelta(days=1),
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=1),
        datetime.timedelta(seconds=1),
    ]

    def at(self, date):
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
        return self.between(dt, dt + self._DELTAS[len(date) - 3])

    def between(self, start, stop):
        """Return events at a time between start (inclusive) and end (inclusive)"""
        span_start = self.to_datetime(start)
        span_stop = self.to_datetime(stop)
        events = []
        events_by_id = defaultdict(
            dict,
        )  # UID (str) : RECURRENCE-ID(datetime) : event (Event)
        default_uid = object()

        def add_event(event):
            """Add an event and check if it was edited."""
            same_events = events_by_id[event.get("UID", default_uid)]
            # TODO: this is still wrong: what if there are different events at
            # the same time?
            recurrence_id = event.get(
                "RECURRENCE-ID",
                event["DTSTART"],
            ).dt
            if isinstance(recurrence_id, datetime.datetime):
                recurrence_id = recurrence_id.date()
            other = same_events.get(recurrence_id, None)
            if other:
                event_recurrence_id = event.get("RECURRENCE-ID", None)
                other_recurrence_id = other.get("RECURRENCE-ID", None)
                if event_recurrence_id is not None and other_recurrence_id is None:
                    events.remove(other)
                elif event_recurrence_id is None and other_recurrence_id is not None:
                    return
                else:
                    event_sequence = event.get("SEQUENCE", None)
                    other_sequence = other.get("SEQUENCE", None)
                    if event_sequence is not None and other_sequence is not None:
                        if event["SEQUENCE"] < other["SEQUENCE"]:
                            return
                        events.remove(other)
            same_events[recurrence_id] = event
            events.append(event)

        span_start_day = span_start
        if isinstance(span_start_day, datetime.datetime):
            span_start_day = span_start_day.replace(hour=0, minute=0, second=0)
        span_stop_day = span_stop
        if isinstance(span_stop_day, datetime.datetime):
            span_stop_day = span_stop.replace(hour=23, minute=59, second=59)

        # repetitions must be considered because the may remove events from
        # the time span
        # see https://github.com/niccokunzmann/python-recurring-ical-events/issues/62
        remove_because_not_in_span = []
        for event_repetitions in self.repetitions.values():
            with self.__handle_invalid_calendar_errors:
                if event_repetitions.is_recurrence():
                    repetition = event_repetitions.as_single_event()
                    if repetition is None:
                        continue
                    vevent = repetition.as_vevent()
                    add_event(vevent)
                    if not repetition.is_in_span(span_start, span_stop):
                        remove_because_not_in_span.append(vevent)
                    continue
                for repetition in event_repetitions.within_days(
                    span_start_day,
                    span_stop_day,
                ):
                    if compare_greater(repetition.start, span_stop):
                        break
                    if repetition.is_in_span(span_start, span_stop):
                        add_event(repetition.as_vevent())

        for vevent in remove_because_not_in_span:
            with contextlib.suppress(ValueError):
                events.remove(vevent)

        return events

    def _get_event_id(self, event):
        """Return a tuple that identifies the event.

        => (name, UID, recurrence-id)
        """
        return self.recurrence_calculators[event.name].id_of(event)

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
            events = self.between(earliest_end, next_end)
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
    components=None,
    skip_bad_events=False,
) -> UnfoldableCalendar:
    """Unfold recurring events of a_calendar

    - a_calendar is an icalendar VCALENDAR component or something like that.
    - keep_recurrence_attributes - whether to keep attributes that are only used
      to calculate the recurrence.
    - components is a list of component type names of which the recurrences
      should be returned.
    """
    components = components or ["VEVENT"]
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
]
