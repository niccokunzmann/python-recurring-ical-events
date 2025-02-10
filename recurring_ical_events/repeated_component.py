from abc import ABC, abstractmethod
import re
from typing import Optional
from recurring_ical_events.repetition import Repetition
from recurring_ical_events.util import compare_greater, convert_to_date, convert_to_datetime, is_pytz


from dateutil.rrule import rruleset, rrulestr
from icalendar.prop import vDDDTypes


import datetime
NEGATIVE_RRULE_COUNT_REGEX = re.compile(r"COUNT=-\d+;?")


class RepeatedComponent(ABC):
    """Base class for RepeatedEvent, RepeatedJournal and RepeatedTodo"""
    
    @abstractmethod
    def _get_component_start(self) -> datetime.date:
        """Return the start of the component."""
        pass
    
    @abstractmethod
    def _get_component_end(self) -> datetime.date:
        """Return the end of the component."""
        pass

    def __init__(self, component, keep_recurrence_attributes=False):
        """Create an component which may have repetitions in it.

        - component - the icalendar component
        - keep_recurrence_attributes whether to copy or delete attributes in repetitions.
        """
        self.component = component
        self.start = self.original_start = self._get_component_start()
        self.end = self.original_end = self._get_component_end()
        self.keep_recurrence_attributes = keep_recurrence_attributes
        self.exdates = []
        self.exdates_utc = set()
        self.replace_ends = {}  # DTSTART -> DTEND # for periods
        exdates = component.get("EXDATE", [])
        for exdates in ((exdates,) if not isinstance(exdates, list) else exdates):
            for exdate in exdates.dts:
                self.exdates.append(exdate.dt)
                self.exdates_utc.add(self._unify_exdate(exdate.dt))
        self.rdates = []
        rdates = component.get("RDATE", [])
        for rdates in ((rdates,) if not isinstance(rdates, list) else rdates):
            for rdate in rdates.dts:
                if isinstance(rdate.dt, tuple):
                    # we have a period as rdate
                    self.rdates.append(rdate.dt[0])
                    self.replace_ends[rdate.dt[0].timestamp()] = rdate.dt[1]
                else:
                    # we have a date/datetime
                    self.rdates.append(rdate.dt)

        self.make_all_dates_comparable()

        self.duration = self.end - self.start
        self.rule = rule = rruleset(cache=True)
        _rule = component.get("RRULE", None)
        if _rule:
            # We don't support multiple RRULE yet, but we can support cases
            # where the same RRULE is erroneously repeated
            if isinstance(_rule, list):
                if len(_rule) > 0 and all(part == _rule[0] for part in _rule):
                    _rule = _rule[0]
                else:
                    raise ValueError("Don't yet support multiple distinct RRULE properties")
            self.rrule = self.create_rule_with_start(_rule.to_ical().decode())
            rule.rrule(self.rrule)
        else:
            self.rrule = None

        for exdate in self.exdates:
            rule.exdate(exdate)
        for rdate in self.rdates:
            rule.rdate(rdate)
        if not self.rrule or not self.rrule.until or not compare_greater(self.start, self.rrule.until):
            rule.rdate(self.start)

    def create_rule_with_start(self, rule_string):
        """Helper to create an rrule from a rule_string starting at the start of the component.

        Since the creation is a bit more complex, this function handles special cases.
        """
        try:
            return self.rrulestr(rule_string)
        except ValueError:
            # string: FREQ=WEEKLY;UNTIL=20191023;BYDAY=TH;WKST=SU
            # start: 2019-08-01 14:00:00+01:00
            # ValueError: RRULE UNTIL values must be specified in UTC when DTSTART is timezone-aware
            rule_list = rule_string.split(";UNTIL=")
            assert len(rule_list) == 2
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
                # we assume the start is timezone aware but the until value is not, see the comment above
                if len(until_string) == 8:
                    until_string += "T000000"
                assert len(until_string) == 15
                until_string += "Z" # https://stackoverflow.com/a/49991809
            new_rule_string = rule_list[0] + rule_list[1][date_end_index:] + ";UNTIL=" + until_string
            return self.rrulestr(new_rule_string)

    def rrulestr(self, rule_string):
        """Return an rrulestr with a start. This might fail."""
        rule_string = NEGATIVE_RRULE_COUNT_REGEX.sub("", rule_string) # Issue 128
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
        assert len(rule_list) == 2, "There should be only one UNTIL."
        date_end_index = rule_list[1].find(";")
        if date_end_index == -1:
            date_end_index = len(rule_list[1])
        until_string = rule_list[1][:date_end_index]
        until = vDDDTypes.from_ical(until_string)
        return until

    def make_all_dates_comparable(self):
        """Make sure we can use all dates with eachother.

        Dates may be mixed and we have many of them.
        - date
        - datetime without timezone
        - datetime with timezone
        These three are not comparable but can be converted.
        """
        self.tzinfo = None
        dates = [self.start, self.end] + self.exdates + self.rdates
        self.is_all_dates = not any(isinstance(date, datetime.datetime) for date in dates)
        for date in dates:
            if isinstance(date, datetime.datetime) and date.tzinfo is not None:
                self.tzinfo = date.tzinfo
                break
        self.start = convert_to_datetime(self.start, self.tzinfo)

        self.end = convert_to_datetime(self.end, self.tzinfo)
        self.rdates = [convert_to_datetime(rdate, self.tzinfo) for rdate in self.rdates]
        self.exdates = [convert_to_datetime(exdate, self.tzinfo) for exdate in self.exdates]

    def _unify_exdate(self, dt):
        """Return a unique string for the datetime which is used to
        compare it with exdates.
        """
        if isinstance(dt, datetime.datetime):
            return dt.timestamp()
        return dt

    def within_days(self, span_start, span_stop):
        """Yield component Repetitions between the start (inclusive) and end (exclusive) of the time span."""
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
                start = start.tzinfo.localize(start.replace(tzinfo=None))
                # We could now well be out of bounce of the end of the UNTIL
                # value. This is tested by test/test_issue_20_exdate_ignored.py.
                if self.rrule is not None and self.rrule.until is not None and start > self.rrule.until and start not in self.rdates:
                    continue
            if self._unify_exdate(start) in self.exdates_utc or start.date() in self.exdates_utc:
                continue
            stop = self.replace_ends.get(start.timestamp(), start + self.duration)
            yield Repetition(
                self.component,
                self.convert_to_original_type(start),
                self.convert_to_original_type(stop),
                self.keep_recurrence_attributes,
                self.end_prop
            )

    def convert_to_original_type(self, date):
        """Convert a date back if this is possible.

        Dates may get converted to datetimes to make calculations possible.
        This reverts the process where possible so that Repetitions end
        up with the type (date/datetime) that was specified in the icalendar
        component.
        """
        if not isinstance(self.original_start, datetime.datetime) and \
                not isinstance(self.original_end, datetime.datetime):
            return convert_to_date(date)
        return date

    def is_recurrence(self):
        """Whether this is a recurrence/modification of an event."""
        return "RECURRENCE-ID" in self.component

    def as_single_event(self) -> Optional[Repetition]:
        """Return as a singe event with no recurrences."""
        for repetition in self.within_days(self.start, self.start):
            return repetition

__all__ = ['RepeatedComponent']
