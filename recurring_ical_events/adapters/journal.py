"""Adapter for VJOURNAL."""

from recurring_ical_events.adapters.component import ComponentAdapter
from recurring_ical_events.constants import DATE_MIN_DT
from recurring_ical_events.types import Time
from recurring_ical_events.util import cached_property


class JournalAdapter(ComponentAdapter):
    """Apdater for journal entries."""

    @staticmethod
    def component_name() -> str:
        """The icalendar component name."""
        return "VJOURNAL"

    @property
    def end_property(self) -> None:
        """There is no end property"""

    @property
    def raw_start(self) -> Time:
        """Return DTSTART if it set, do not panic if it's not set."""
        ## according to the specification, DTSTART in a VJOURNAL is optional
        dtstart = self._component.get("DTSTART")
        if dtstart is not None:
            return dtstart.dt
        return DATE_MIN_DT

    @cached_property
    def raw_end(self) -> Time:
        """The end time is the same as the start."""
        ## VJOURNAL cannot have a DTEND.  We should consider a VJOURNAL to
        ## describe one day if DTSTART is a date, and we can probably
        ## consider it to have zero duration if a timestamp is given.
        return self.raw_start


__all__ = ["JournalAdapter"]
