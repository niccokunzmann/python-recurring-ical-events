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
import icalendar
import datetime
import pytz
from dateutil.rrule import rrulestr, rruleset, rrule, DAILY
import dateutil.parser
import sys
import x_wr_timezone
from collections import defaultdict
from icalendar.prop import vDDDTypes

if sys.version_info[0] == 2:
    # Python2 has no ZoneInfo. We can assume that pytz is used.
    _EPOCH = datetime.datetime.utcfromtimestamp(0)
    _EPOCH_TZINFO = pytz.UTC.localize(_EPOCH)
    def timestamp(dt):
        """Return the time stamp of a datetime"""
        # from https://stackoverflow.com/a/35337826
        if dt.tzinfo:
            return (dt - _EPOCH_TZINFO).total_seconds()
        return (dt - _EPOCH).total_seconds()
else:
    def timestamp(dt):
        """Return the time stamp of a datetime"""
        return dt.timestamp() 

def convert_to_date(date):
    """converts a date or datetime to a date"""
    return datetime.date(date.year, date.month, date.day)

def convert_to_datetime(date, tzinfo):
    """converts a date to a datetime"""
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

def time_span_contains_event(span_start, span_stop, event_start, event_stop, comparable=False):
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


def is_pytz(tzinfo):
    """Whether the time zone requires localize() and normalize().

    pytz requires these funtions to be used in order to correctly use the
    time zones after operations.
    """
    return hasattr(tzinfo , "localize")


class Repetition:
    """A repetition of an event."""

    ATTRIBUTES_TO_DELETE_ON_COPY = [
        "RRULE", "RDATE", "EXDATE"
    ]

    def __init__(self, source, start, stop, keep_recurrence_attributes=False, end_prop='DTEND'):
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
        return "{}({{'UID':{}...}}, {}, {})".format(self.__class__.__name__, self.source.get("UID"), self.start, self.stop)

class RepeatedComponent:
    """Base class for RepeatedEvent, RepeatedJournal and RepeatedTodo"""
    
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
        exdates = component.get("EXDATE", [])
        for exdates in ((exdates,) if not isinstance(exdates, list) else exdates):
            for exdate in exdates.dts:
                self.exdates.append(exdate.dt)
                self.exdates_utc.add(self._unify_exdate(exdate.dt))
        self.rdates = []
        rdates = component.get("RDATE", [])
        for rdates in ((rdates,) if not isinstance(rdates, list) else rdates):
            for rdate in rdates.dts:
                self.rdates.append(rdate.dt)

        self.make_all_dates_comparable()

        self.duration = self.end - self.start
        self.rule = rule = rruleset(cache=True)
        _rule = component.get("RRULE", None)
        if _rule:
            self.rrule = self.create_rule_with_start(_rule.to_ical().decode())
            rule.rrule(self.rrule)
        else:
            self.rrule = None

        for exdate in self.exdates:
            rule.exdate(exdate)
        for rdate in self.rdates:
            rule.rdate(rdate)
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
        rule = rrulestr(rule_string, dtstart=self.start)
        rule.string = rule_string
        return rule

    _until = UNTIL_NOT_SET = "NOT_SET"
    def get_rrule_until(self):
        """Return the UNTIL datetime of the rrule or None is absent."""
        if self._until is not self.UNTIL_NOT_SET:
            return self._until
        self._until = None
        if self.rrule is None:
            return None
        rule_list = self.rrule.string.split(";UNTIL=")
        if len(rule_list) == 1:
            return None
        assert len(rule_list) == 2, "There should be only one UNTIL."
        date_end_index = rule_list[1].find(";")
        if date_end_index == -1:
            date_end_index = len(rule_list[1])
        until_string = rule_list[1][:date_end_index]
        self._until = vDDDTypes.from_ical(until_string)
        return self._until

    def make_all_dates_comparable(self):
        """Make sure we can use all dates with eachother.

        Dates may be mixed and we have many of them.
        - date
        - datetime without timezome
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
            return timestamp(dt)
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
                until = self.get_rrule_until()
                if until is not None and start > until and start not in self.rdates:
                    continue
            if self._unify_exdate(start) in self.exdates_utc:
                continue
            stop = start + self.duration
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

    def as_single_event(self):
        """Return as a singe event with no recurrences."""
        for repetition in self.within_days(self.start, self.start):
            return repetition


class RepeatedEvent(RepeatedComponent):
    """An event with repetitions created from an icalendar event."""
    end_prop = 'DTEND'

    def _get_component_start(self):
        """Return DTSTART"""
        ## Arguably, it may be considered a feature that this breaks if no DTSTART is set
        return self.component['DTSTART'].dt
    
    def _get_component_end(self):
        """Yield DTEND or calculate the end of the event based on DTSTART and DURATION."""
        ## an even may have DTEND or DURATION, but not both
        end = self.component.get("DTEND")
        if end is not None:
            return end.dt
        duration = self.component.get("DURATION")
        if duration is not None:
            return self.component["DTSTART"].dt + duration.dt
        return self.component["DTSTART"].dt

class RepeatedTodo(RepeatedComponent):
    end_prop = 'DUE'

    def _get_component_start(self):
        """Return DTSTART if it set, do not panic if it's not set."""
        ## easy case - DTSTART set
        start = self.component.get('DTSTART')
        if start is not None:
            return start.dt
        ## Tasks may have DUE set, but no DTSTART.
        ## Let's assume 0 duration and return the DUE
        due = self.component.get('DUE')
        if due is not None:
            return due.dt
        
        ## Assume infinite time span if neither is given
        ## (see the comments under _get_event_end)
        return datetime.date(*DATE_MIN)

    def _get_component_end(self):
        """Return DUE or DTSTART+DURATION or something"""
        ## Easy case - DUE is set
        end = self.component.get('DUE')
        if end is not None:
            return end.dt
        
        dtstart = self.component.get("DTSTART")
        
        ## DURATION can be specified instead of DUE.
        duration = self.component.get("DURATION")
        ## It is no requirement that DTSTART is set.
        ## Perhaps duration is a time estimate rather than an indirect
        ## way to set DUE.
        if duration is not None and dtstart is not None:
            return self.component["DTSTART"].dt + duration.dt
        
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
    end_prop = ''

    def _get_component_start(self):
        """Return DTSTART if it set, do not panic if it's not set."""
        ## according to the specification, DTSTART in a VJOURNAL is optional
        dtstart = self.component.get("DTSTART")
        if dtstart is not None:
            return dtstart.dt
        return datetime.date(*DATE_MIN)

    ## VJOURNAL cannot have a DTEND.  We should consider a VJOURNAL to
    ## describe one day if DTSTART is a date, and we can probably
    ## consider it to have zero duration if a timestamp is given.
    _get_component_end = _get_component_start

    
# The minimum value accepted as date (pytz + zoneinfo)
DATE_MIN = (1970, 1, 1)
# The maximum value accepted as date (pytz + zoneinfo)
DATE_MAX = (2038, 1, 1)

class UnsupportedComponent(ValueError):
    """This error is raised when a component is not supported, yet."""


class UnfoldableCalendar:
    '''A calendar that can unfold its events at a certain time.'''
    
    recurrence_calculators = {
        "VEVENT": RepeatedEvent,
        "VTODO": RepeatedTodo,
        "VJOURNAL": RepeatedJournal,
    }

    def __init__(self, calendar, keep_recurrence_attributes=False, components=["VEVENT"]):
        """Create an unfoldable calendar from a given calendar."""
        assert calendar.get("CALSCALE", "GREGORIAN") == "GREGORIAN", "Only Gregorian calendars are supported." # https://www.kanzaki.com/docs/ical/calscale.html
        self.repetitions = []
        for component_name in components:
            if component_name not in self.recurrence_calculators:
                raise UnsupportedComponent(f"\"{component_name}\" is an unknown name for a component. I only know these: {', '.join(self.recurrence_calculators)}.")
            for event in calendar.walk(component_name):
                recurrence_calculator = self.recurrence_calculators[component_name]
                self.repetitions.append(recurrence_calculator(event, keep_recurrence_attributes))

    @staticmethod
    def to_datetime(date):
        """Convert date inputs of various sorts into a datetime object."""
        if isinstance(date, int):
            date = (date,)
        if isinstance(date, tuple):
            date += (1,) * (3 - len(date))
            return datetime.datetime(*date)
        elif isinstance(date, str):
            # see https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
            if len(date) == 8:
                return datetime.datetime.strptime(date, "%Y%m%d")
            return datetime.datetime.strptime(date, "%Y%m%dT%H%M%SZ")
        return date

    def all(self):
        """Returns all events.

        I personally do not recommend to use this because
        this method is not documented and you may end up with lots of events most of which you may not use anyway."""
        # MAX and MIN values may change in the future
        return self.between(DATE_MIN, DATE_MAX)

    _DELTAS = [
        datetime.timedelta(days=1),
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=1),
        datetime.timedelta(seconds=1)
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
            assert len(date) == 8 and date.isdigit(), "format yyyymmdd expected"
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
        events_by_id = defaultdict(dict) # UID (str) : RECURRENCE-ID(datetime) : event (Event)
        default_uid = object()
        def add_event(event):
            """Add an event and check if it was edited."""
            same_events = events_by_id[event.get("UID", default_uid)] # TODO: test what comes first
            recurrence_id = event.get("RECURRENCE-ID", event["DTSTART"]).dt # TODO: this is still wrong: what if there are different events at the same time?
            if isinstance(recurrence_id, datetime.datetime):
                recurrence_id = recurrence_id.date()
            other = same_events.get(recurrence_id, None)
            if other: # TODO: test that this is independet of order
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
            span_start_day = span_start_day.replace(hour=0,minute=0,second=0)
        span_stop_day = span_stop
        if isinstance(span_stop_day, datetime.datetime):
            span_stop_day = span_stop.replace(hour=23,minute=59,second=59)

        # repetitions must be considered because the may remove events from the time span
        # see https://github.com/niccokunzmann/python-recurring-ical-events/issues/62
        remove_because_not_in_span = []
        for event_repetitions in self.repetitions:
            if event_repetitions.is_recurrence():
                repetition = event_repetitions.as_single_event()
                vevent = repetition.as_vevent()
                add_event(vevent)
                if not repetition.is_in_span(span_start, span_stop):
                    remove_because_not_in_span.append(vevent)
                continue
            for repetition in event_repetitions.within_days(span_start_day, span_stop_day):
                if compare_greater(repetition.start, span_stop):
                    break
                if repetition.is_in_span(span_start, span_stop):
                    add_event(repetition.as_vevent())

        for vevent in remove_because_not_in_span:
            try:
                events.remove(vevent)
            except ValueError:
                pass

        return events

def of(a_calendar, keep_recurrence_attributes=False, components=["VEVENT"]):
    """Unfold recurring events of a_calendar
    
    - a_calendar is an icalendar VCALENDAR component or something like that.
    - keep_recurrence_attributes - whether to keep attributes that are only used to calculate the recurrence.
    - components is a list of component type names of which the recurrences should be returned.
    """
    a_calendar = x_wr_timezone.to_standard(a_calendar)
    return UnfoldableCalendar(a_calendar, keep_recurrence_attributes, components)

