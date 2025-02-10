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
import dateutil.parser
import x_wr_timezone
from collections import defaultdict
from typing import Optional

from recurring_ical_events.repeated_component import RepeatedComponent
from recurring_ical_events.util import compare_greater

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
                if repetition is None:
                    continue
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
