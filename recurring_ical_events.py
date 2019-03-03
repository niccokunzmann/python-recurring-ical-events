import icalendar
import datetime
import pytz
from dateutil.rrule import rrulestr, rruleset, rrule, DAILY

def is_event(component):
    """Return whether a component is a calendar event."""
    return isinstance(component, icalendar.cal.Event)

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
    def _convert_date(date):
        """Convert date inputs of various sorts into a datetime object."""
        return datetime.datetime(*date, tzinfo=pytz.utc)

    def all(self):
        """Returns all events."""
        return self.between((1000, 1, 1), (3000, 1, 1))

    def between(self, start, stop): # TODO: add parameters from time_span_contains_event
        """Return events at a time between start (inclusive) and end (inclusive)"""
        span_start = self._convert_date(start)
        span_stop = self._convert_date(stop)
        events = []
        for event in self.calendar.walk():
            if not is_event(event):
                continue
            event_rrule = event.get("RRULE", None)
            event_start = event["DTSTART"].dt
            event_end = event["DTEND"].dt
            event_duration = event_end - event_start
            if event_rrule is None:
                if time_span_contains_event(span_start, span_stop, event_start, event_end):
                    events.append(event)
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
                        #revent = event.copy()
                        events.append(event)
        return events


def of(a_calendar):
    """Unfold recurring events of a_calendar"""
    return UnfoldableCalendar(a_calendar)
