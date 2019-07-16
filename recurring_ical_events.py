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
from icalendar.prop import vDatetime, vDate

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
        if len(date) == 1:
            return self.between((date[0], 1, 1), (date[0] + 1, 1, 1))
        if len(date) == 2:
            year, month = date
            if month == 12:
                return self.between((year, 12, 1), (year + 1, 1, 1))
            return self.between((year, month, 1), (year, month + 1, 1))
        datetime = self.to_datetime(date)
        return self.between(datetime, datetime + self._DELTAS[len(date) - 3])
    
    def get_event_end(self, event):
        end = event.get("DTEND")
        if end is not None:
            return end.dt
        duration = event.get("DURATION")
        if duration is not None:
            return event["DTSTART"].dt + duration.dt
        return event["DTSTART"].dt

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
            recurrence_id = event.get("RECURRENCE-ID", event["DTSTART"]).dt
            other = same_events.get(recurrence_id, None)
            if other: # TODO: test that this is independet of order
                if event["SEQUENCE"] < other["SEQUENCE"]:
                    return
                events.remove(other)
            same_events[recurrence_id] = event
            events.append(event)

        for event in self.calendar.walk():
            if not is_event(event):
                continue
            event_rrule = event.get("RRULE", None)
            event_start = event["DTSTART"].dt
            event_end = self.get_event_end(event)
            event_duration = event_end - event_start
            rule = rruleset()
            c_event_start = event_start # avoid datetime and date mix
            if event_rrule is not None:
                rule_string = event_rrule.to_ical().decode()
                rule.rrule(rrulestr(rule_string, dtstart=event_start))
            if compare_greater(span_start, event_start):
                c_event_start, c_span_start = make_comparable((event_start, span_start))
                # the rrule until parameter includes the last date
                # thus we need to go one day back
                c_span_start -= datetime.timedelta(days=1)
                if event_end:
                    # do not exclude an event if it spans across the time span
                    c_event_end, c_span_start = make_comparable((event_end, span_start))
                    c_span_start -= c_event_end - c_event_start
                rule.exrule(rrule(DAILY, dtstart=c_event_start, until=c_span_start))
            exdates = event.get("EXDATE", [])
            for exdates in ((exdates,) if not isinstance(exdates, list) else exdates):
                for exdate in exdates.dts:
                    c_event_start, exdate = make_comparable((c_event_start, exdate.dt))
                    rule.exdate(exdate)
            rdates = event.get("RDATE", [])
            for rdates in ((rdates,) if not isinstance(rdates, list) else rdates):
                for rdate in rdates.dts:
                    c_event_start, rdate = make_comparable((c_event_start, rdate.dt))
                    rule.rdate(rdate)
            rule.rdate(c_event_start)
            # TODO: If in the following line, we get an error, datetime and date
            # may still be mixed because RDATE, EXDATE, start and rule.
            for revent_start in rule:
                if isinstance(revent_start, datetime.datetime) and revent_start.tzinfo is not None:
                    revent_start = revent_start.tzinfo.localize(revent_start.replace(tzinfo=None))
                if compare_greater(revent_start, span_stop):
                    break
                revent_stop = revent_start + event_duration
                if time_span_contains_event(span_start, span_stop, revent_start, revent_stop):
                    revent = event.copy()
                    revent["DTSTART"] = self._create_ical_entry_from(revent_start)
                    revent["DTEND"] = self._create_ical_entry_from(revent_stop)
                    add_event(revent)
        return events

    def _create_ical_entry_from(self, date_or_datetime):
        """Choose the correct method for ical representation."""
        if isinstance(date_or_datetime, datetime.datetime):
            return vDatetime(date_or_datetime)
        return vDate(date_or_datetime)


def of(a_calendar):
    """Unfold recurring events of a_calendar"""
    return UnfoldableCalendar(a_calendar)
