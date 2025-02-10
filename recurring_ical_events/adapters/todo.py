"""Adapter for VTODO."""

from recurring_ical_events.adapters.component import ComponentAdapter
from recurring_ical_events.constants import DATE_MAX_DT, DATE_MIN_DT
from recurring_ical_events.types import Time
from recurring_ical_events.util import cached_property, normalize_pytz


class TodoAdapter(ComponentAdapter):
    """Unified access to TODOs."""

    @staticmethod
    def component_name() -> str:
        """The icalendar component name."""
        return "VTODO"

    @property
    def end_property(self) -> str:
        """DUE"""
        return "DUE"

    @cached_property
    def start(self) -> Time:
        """Return DTSTART if it set, do not panic if it's not set."""
        ## easy case - DTSTART set
        start = self._component.get("DTSTART")
        if start is not None:
            return start.dt
        ## Tasks may have DUE set, but no DTSTART.
        ## Let's assume 0 duration and return the DUE
        due = self._component.get("DUE")
        if due is not None:
            return due.dt

        ## Assume infinite time span if neither is given
        ## (see the comments under _get_event_end)
        return DATE_MIN_DT

    @cached_property
    def end(self) -> Time:
        """Return DUE or DTSTART+DURATION or something"""
        ## Easy case - DUE is set
        end = self._component.get("DUE")
        if end is not None:
            return end.dt

        dtstart = self._component.get("DTSTART")

        ## DURATION can be specified instead of DUE.
        duration = self._component.get("DURATION")
        ## It is no requirement that DTSTART is set.
        ## Perhaps duration is a time estimate rather than an indirect
        ## way to set DUE.
        if duration is not None and dtstart is not None:
            return normalize_pytz(self._component["DTSTART"].dt + duration.dt)

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
        return DATE_MAX_DT


__all__ = ["TodoAdapter"]
