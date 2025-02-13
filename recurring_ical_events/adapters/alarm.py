"""Adapter for VALARM components."""

from __future__ import annotations

from typing import TYPE_CHECKING

from recurring_ical_events.adapters.component import ComponentAdapter

if TYPE_CHECKING:
    from icalendar import Alarm


class AbsoluteAlarmAdapter(ComponentAdapter):  # TODO: remove
    """Adapter for absolute alarms."""

    def __init__(self, alarm: Alarm, parent: ComponentAdapter):
        """Create a new adapter."""
        super().__init__(alarm)
        self.parent = parent


__all__ = ["AbsoluteAlarmAdapter"]
