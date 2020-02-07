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

from collections import defaultdict
from icalendar.prop import vDDDTypes

if sys.version_info[0] == 2:
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

def is_event(component):
    """Return whether a component is a calendar event."""
    return isinstance(component, icalendar.cal.Event)

def convert_to_date(date):
    """converts a date or datetime to a date"""
    return datetime.date(date.year, date.month, date.day)

def convert_to_datetime(date, tzinfo):
    """converts a date to a datetime"""
    if isinstance(date, datetime.datetime):
        if date.tzinfo is None:
            if tzinfo is not None:
                return tzinfo.localize(date)
        else:
            assert tzinfo is not None, "Error in algorithm: tzinfo expected to be known."
        return date
    elif isinstance(date, datetime.date):
        return datetime.datetime(date.year, date.month, date.day, tzinfo=tzinfo)
    return date

def time_span_contains_event(span_start, span_stop, event_start, event_stop,
        include_start=True, include_stop=True, comparable=False):
    """Return whether an event should is included within a time span.

    - span_start and span_stop define the time span
    - event_start and event_stop define the event time
    - include_start defines whether events overlapping the start of the
        time span should be included
    - include_stop defines whether events overlapping the stop of the
        time span should be included
    - comparable indicates whether the dates can be compared.
        You can set it to True if you are sure you have timezones and
        date/datetime correctly or used make_comparable() before.
    """
    if not comparable:
        span_start, span_stop, event_start, event_stop = make_comparable((
            span_start, span_stop, event_start, event_stop
        ))
    assert event_start <= event_stop, "the event must start before it ends"
    assert span_start <= span_stop, "the time span must start before it ends"
    return (include_start or span_start <= event_start) and \
        (include_stop or event_stop <= span_stop) and \
        (event_start < span_stop and span_start <= event_stop)


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

class UnfoldableCalendar:

    class RepeatedEvent:
        """An event with repetitions created from an ical event."""
        
        class Repetition:
            """A repetition of an event."""

            ATTRIBUTES_TO_DELETE_ON_COPY = [
                "RRULE", "RDATE", "EXDATE"
            ]

            def __init__(self, source, start, stop):
                self.source = source
                self.start = start
                self.stop = stop

            def as_vevent(self):
                revent = self.source.copy()
                revent["DTSTART"] = vDDDTypes(self.start)
                revent["DTEND"] = vDDDTypes(self.stop)
                for attribute in self.ATTRIBUTES_TO_DELETE_ON_COPY:
                    if attribute in revent:
                        del revent[attribute]
                for subcomponent in self.source.subcomponents:
                    revent.add_component(subcomponent)
                return revent

            def is_in_span(self, span_start, span_stop):
                return time_span_contains_event(span_start, span_stop, self.start, self.stop)

        def __init__(self, event, span_start):
            self.event = event
            self.span_start = span_start
            self.start = self.original_start = event["DTSTART"].dt
            self.end = self.original_end = self._get_event_end()
            self.exdates = []
            self.exdates_utc = set()
            exdates = event.get("EXDATE", [])
            for exdates in ((exdates,) if not isinstance(exdates, list) else exdates):
                for exdate in exdates.dts:
                    self.exdates.append(exdate.dt)
                    self.exdates_utc.add(self._unify_exdate(exdate.dt))
            self.rdates = []
            rdates = event.get("RDATE", [])
            for rdates in ((rdates,) if not isinstance(rdates, list) else rdates):
                for rdate in rdates.dts:
                    self.rdates.append(rdate.dt)
            
            self.make_all_dates_comparable()
            
            self.duration = self.end - self.start
            self.rule = rule = rruleset()
            _rule = event.get("RRULE", None)
            if _rule:
                rule.rrule(self.create_rule_with_start(_rule.to_ical().decode(), self.start))

            if compare_greater(self.span_start, self.start):
                # the rrule until parameter includes the last date
                # thus we need to go one day back
                span_start = self.span_start - datetime.timedelta(days=1)
                # do not exclude an event if it spans across the time span
                span_start -= self.duration
                rule.exrule(rrule(DAILY, dtstart=self.start, until=span_start))

            for exdate in self.exdates:
                rule.exdate(exdate)
            for rdate in self.rdates:
                rule.rdate(rdate)
            rule.rdate(self.start)
            
        def create_rule_with_start(self, rule_string, start):
            try:
                return rrulestr(rule_string, dtstart=start)
            except ValueError:
                # string: FREQ=WEEKLY;UNTIL=20191023;BYDAY=TH;WKST=SU
                # start: 2019-08-01 14:00:00+01:00
                # ValueError: RRULE UNTIL values must be specified in UTC when DTSTART is timezone-aware
                assert self.start.tzinfo is not None, "we assume the start is timezone aware but the until value is not" # see the comment above
                rule_list = rule_string.split(";UNTIL=")
                assert len(rule_list) == 2
                date_end_index = rule_list[1].find(";")
                if date_end_index == -1:
                    date_end_index = len(rule_list[1])
                until_string = rule_list[1][:date_end_index]
                rule_string = rule_list[0] + rule_list[1][date_end_index:] + ";UNTIL=" + until_string + \
                    "T000000Z" # https://stackoverflow.com/a/49991809
                return rrulestr(rule_string, dtstart=self.start)


        def make_all_dates_comparable(self):
            """Make sure we can use all dates with eachother.
            
            Dates may be mixed and we have many of them.
            - date
            - datetime without timezome
            - datetime with timezone
            These three are not comparable but can be converted.
            """
            dates = [self.start, self.end, self.span_start] + self.exdates + self.rdates
            if not any(isinstance(date, datetime.datetime) for date in dates):
                return
            tzinfo = None
            for date in dates:
                if isinstance(date, datetime.datetime) and date.tzinfo is not None:
                    tzinfo = date.tzinfo
                    break
            self.start = convert_to_datetime(self.start, tzinfo)
            self.span_start = convert_to_datetime(self.span_start, tzinfo)
            self.end = convert_to_datetime(self.end, tzinfo)
            self.rdates = [convert_to_datetime(rdate, tzinfo) for rdate in self.rdates]
            self.exdates = [convert_to_datetime(exdate, tzinfo) for exdate in self.exdates]
        
        def _unify_exdate(self, dt):
            """Return a unique string for the datetime which is used to
            compare it with exdates.
            """
            if isinstance(dt, datetime.datetime):
                return timestamp(dt)
            return dt
       
        def __iter__(self):
            # TODO: If in the following line, we get an error, datetime and date
            # may still be mixed because RDATE, EXDATE, start and rule.
            for start in self.rule:
                if isinstance(start, datetime.datetime) and start.tzinfo is not None:
                    start = start.tzinfo.localize(start.replace(tzinfo=None))
                stop = start + self.duration
                if self._unify_exdate(start) in self.exdates_utc:
                    continue
                yield self.Repetition(
                    self.event,
                    self.convert_to_original_type(start),
                    self.convert_to_original_type(stop))
        
        def convert_to_original_type(self, date):
            if not isinstance(self.original_start, datetime.datetime) and \
                    not isinstance(self.original_end, datetime.datetime):
                return convert_to_date(date)
            return date
                
        def _get_event_end(self):
            end = self.event.get("DTEND")
            if end is not None:
                return end.dt
            duration = self.event.get("DURATION")
            if duration is not None:
                return self.event["DTSTART"].dt + duration.dt
            return self.event["DTSTART"].dt


    def __init__(self, calendar):
        """Create an unfoldable calendar from a given calendar."""
        assert calendar.get("CALSCALE", "GREGORIAN") == "GREGORIAN", "Only Gregorian calendars are supported." # https://www.kanzaki.com/docs/ical/calscale.html
        self.calendar = calendar

    @staticmethod
    def to_datetime(date):
        """Convert date inputs of various sorts into a datetime object."""
        if isinstance(date, tuple):
            return datetime.datetime(*date)
        elif isinstance(date, str):
            # see https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
            if len(date) == 8:
                return datetime.datetime.strptime(date, "%Y%m%d")
            return datetime.datetime.strptime(date, "%Y%m%dT%H%M%SZ")
        return date

    def all(self):
        """Returns all events."""
        # TODO: test MAX and MIN values
        return self.between((1000, 1, 1), (3000, 1, 1))

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
    
    def between(self, start, stop): # TODO: add parameters from time_span_contains_event
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
            other = same_events.get(recurrence_id, None)
            if other: # TODO: test that this is independet of order
                event_sequence = event.get("SEQUENCE", None)
                other_sequence = other.get("SEQUENCE", None)
                if event_sequence is not None and other_sequence is not None:
                    if event["SEQUENCE"] < other["SEQUENCE"]:
                        return
                    events.remove(other)
            same_events[recurrence_id] = event
            events.append(event)

        for event in self.calendar.walk():
            if not is_event(event):
                continue
            repetitions = self.RepeatedEvent(event, span_start)
            for repetition in repetitions:
                if compare_greater(repetition.start, span_stop):
                    break
                if repetition.is_in_span(span_start, span_stop):
                    add_event(repetition.as_vevent())
        return events

def of(a_calendar):
    """Unfold recurring events of a_calendar"""
    return UnfoldableCalendar(a_calendar)
