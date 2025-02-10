from recurring_ical_events.util import time_span_contains_event


from icalendar.prop import vDDDTypes


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

__all__ = ['Repetition']
