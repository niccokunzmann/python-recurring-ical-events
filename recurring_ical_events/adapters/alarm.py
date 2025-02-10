from icalendar import Alarm

from recurring_ical_events.adapters.component import ComponentAdapter


class AbsoluteAlarmAdapter(ComponentAdapter):
    """Adapter for absolute alarms."""

    def __init__(self, alarm: Alarm, parent: ComponentAdapter):
        """Create a new adapter."""
        super().__init__(alarm)
        self.parent = parent
