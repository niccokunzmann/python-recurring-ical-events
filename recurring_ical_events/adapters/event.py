"""Adapter for VEVENT."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from recurring_ical_events.adapters.component import ComponentAdapter
from recurring_ical_events.util import cached_property, is_date, normalize_pytz

if TYPE_CHECKING:
    from recurring_ical_events.types import Time


class EventAdapter(ComponentAdapter):
    """An icalendar event adapter."""

    @staticmethod
    def component_name() -> str:
        """The icalendar component name."""
        return "VEVENT"

    @property
    def end_property(self) -> str:
        """DTEND"""
        return "DTEND"

    @cached_property
    def start(self) -> Time:
        """Return DTSTART"""
        # Arguably, it may be considered a feature that this breaks
        # if no DTSTART is set
        return self._component["DTSTART"].dt

    @cached_property
    def end(self) -> Time:
        """Yield DTEND or calculate the end of the event based on
        DTSTART and DURATION.
        """
        ## an even may have DTEND or DURATION, but not both
        end = self._component.get("DTEND")
        if end is not None:
            return end.dt
        duration = self._component.get("DURATION")
        if duration is not None:
            return normalize_pytz(self._component["DTSTART"].dt + duration.dt)
        start = self._component["DTSTART"].dt
        if is_date(start):
            return start + datetime.timedelta(days=1)
        return start


__all__ = ["EventAdapter"]
