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
from collections import defaultdict
from icalendar.prop import vDatetime

def is_event(component):
    """Return whether a component is a calendar event."""
    return isinstance(component, icalendar.cal.Event)

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
        include_start=True, include_stop=True):
    """Return whether an event should is included within a time span.

    - span_start and span_stop define the time span
    - event_start and event_stop define the event time
    - include_start defines whether events overlapping the start of the
        time span should be included
    - include_stop defines whether events overlapping the stop of the
        time span should be included
    """
    tzinfo = getattr(span_start, "tzinfo", None) or \
        getattr(span_stop, "tzinfo", None) or \
        getattr(event_start, "tzinfo", None) or \
        getattr(event_stop, "tzinfo", None)
    span_start = convert_to_datetime(span_start, tzinfo)
    span_stop = convert_to_datetime(span_stop, tzinfo)
    event_start = convert_to_datetime(event_start, tzinfo)
    event_stop = convert_to_datetime(event_stop, tzinfo)
    assert event_start <= event_stop, "the event must start before it ends"
    assert span_start <= span_stop, "the time span must start before it ends"
    return (include_start or span_start <= event_start) and \
        (include_stop or event_stop <= span_stop) and \
        (event_start <= span_stop and span_start <= event_stop)

class UnfoldableCalendar:

    def __init__(self, calendar):
        """Create an unfoldable calendar from a given calendar."""
        assert calendar.get("CALSCALE", "GREGORIAN") == "GREGORIAN", "Only Gregorian calendars are supported." # https://www.kanzaki.com/docs/ical/calscale.html
        self.calendar = calendar

    @staticmethod
    def to_datetime(date):
        """Convert date inputs of various sorts into a datetime object."""
        if isinstance(date, tuple):
            return datetime.datetime(*date, tzinfo=pytz.utc)
        elif isinstance(date, str):
            # see https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
            if len(date) == 8:
                return datetime.datetime.strptime(date, "%Y%m%d").replace(tzinfo=pytz.utc)
            return datetime.datetime.strptime(date, "%Y%m%dT%H%M%SZ").replace(tzinfo=pytz.utc)
        return date

    def all(self):
        """Returns all events."""
        return self.between((1000, 1, 1), (3000, 1, 1))

    def between(self, start, stop): # TODO: add parameters from time_span_contains_event
        """Return events at a time between start (inclusive) and end (inclusive)"""
        span_start = self.to_datetime(start)
        span_stop = self.to_datetime(stop)
        events = []
        events_by_id = defaultdict(dict) # UID (str) : RECURRENCE-ID(datetime) : event (Event)
        def add_event(event):
            """Add an event and check if it was edited."""
            same_events = events_by_id[event["UID"]] # TODO: test what comes first
            start = event["DTSTART"].dt
            other = same_events.get(start, None)
            if other:
                events.remove(other)
            same_events[start] = event
            events.append(event)

        for event in self.calendar.walk():
            if not is_event(event):
                continue
            event_rrule = event.get("RRULE", None)
            event_start = event["DTSTART"].dt
            event_end = event["DTEND"].dt
            event_duration = event_end - event_start
            if event_rrule is None:
                if time_span_contains_event(span_start, span_stop, event_start, event_end):
                    add_event(event)
            else:
                rule_string = event_rrule.to_ical().decode()
                rule = rruleset()
                rule.rrule(rrulestr(rule_string, dtstart=event_start))
                print(event_start, "<", span_start, "==", event_start < span_start)
                if event_start < span_start:
                    rule.exrule(rrule(DAILY, dtstart=event_start, until=span_start)) # TODO: test overlap with -event_duration
                exdates = event.get("EXDATE", [])
                for exdates in ([exdates] if not isinstance(exdates, list) else exdates):
                    for exdate in exdates.dts:
                        rule.exdate(exdate.dt)
                for revent_start in rule:
                    print(revent_start, ">", span_stop, "==", revent_start > span_stop)
                    if revent_start > span_stop:
                        break
                    revent_stop = revent_start + event_duration
                    if time_span_contains_event(span_start, span_stop, revent_start, revent_stop):
                        revent = event.copy()
                        revent["DTSTART"] = vDatetime(revent_start)
                        revent["DTEND"] = vDatetime(revent_stop)
                        add_event(revent)
        return events


def of(a_calendar):
    """Unfold recurring events of a_calendar"""
    return UnfoldableCalendar(a_calendar)
