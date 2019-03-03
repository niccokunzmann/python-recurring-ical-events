import icalendar
import datetime
import pytz
from dateutil.rrule import rrulestr, rruleset, rrule, DAILY

def is_event(component):
    """Return whether a component is a calendar event."""
    return isinstance(component, icalendar.cal.Event)

class UnfoldableCalendar:

    def __init__(self, calendar):
        """Create an unfoldable calendar from a given calendar."""
        assert calendar.get("CALSCALE", "GREGORIAN") == "GREGORIAN", "Only Gregorian calendars are supported." # https://www.kanzaki.com/docs/ical/calscale.html
        self.calendar = calendar

    @staticmethod
    def _convert_date(date):
        """Convert date inputs of various sorts into a datetime object."""
        return datetime.datetime(*date, tzinfo=pytz.utc)

    def between(self, start, end):
        """Return events at a time between start (inclusive) and end (exclusive)"""
        span_start = self._convert_date(start)
        span_end = self._convert_date(end)
        events = []
        for event in self.calendar.walk():
            if not is_event(event):
                continue
            event_rrule = event.get("RRULE", None)
            event_start = event["DTSTART"].dt
            event_end = event["DTEND"].dt
            event_duration = event_end - event_start
            if event_rrule is None:
                if event_start < span_start:
                    continue
                if event_end > span_end:
                    continue
                events.append(event)
            else:
                rule_string = event_rrule.to_ical().decode()
                rule = rruleset()
                rule.rrule(rrulestr(rule_string, dtstart=event_start))
                print(event_start, "<", span_start, "==", event_start < span_start)
                if event_start < span_start:
                    rule.exrule(rrule(DAILY, dtstart=event_start, until=span_start))
                for revent_start in rule:
                    print(revent_start, ">", span_end, "==", revent_start > span_end)
                    if revent_start > span_end:
                        break
                    #revent_end = revent_start + event_duration
                    #revent = event.copy()
                    events.append(event)
        return events


def of(a_calendar):
    """Unfold recurring events of a_calendar"""
    return UnfoldableCalendar(a_calendar)
