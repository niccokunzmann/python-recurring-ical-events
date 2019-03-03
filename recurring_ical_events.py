import icalendar
import datetime
import pytz

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
        return datetime.datetime(*date, tzinfo=pytz.utc)

    def between(self, start, end):
        """Return events at a time between start (inclusive) and end (exclusive)"""
        span_start = self._convert_date(start)
        span_end = self._convert_date(end)
        events = []
        for event in self.calendar.walk():
            if not is_event(event):
                continue
            event_start = event["DTSTART"].dt
            if event_start < span_start:
                continue
            event_end = event["DTEND"].dt
            if event_end > span_end:
                continue
            events.append(event)
        return events


def of(a_calendar):
    """Unfold recurring events of a_calendar"""
    return UnfoldableCalendar(a_calendar)
