from __future__ import annotations

from typing import TYPE_CHECKING

from icalendar import Alarm

from recurring_ical_events.adapters.component import ComponentAdapter
from recurring_ical_events.types import ComponentID
from recurring_ical_events.util import (
    cached_property,
    make_comparable,
    time_span_contains_event,
)

if TYPE_CHECKING:
    import datetime

    from icalendar import Alarm
    from icalendar.cal import Component

    from recurring_ical_events.adapters.component import ComponentAdapter
    from recurring_ical_events.types import ComponentID, RecurrenceIDs, Time


class Occurrence:
    """A repetition of an event."""

    def __init__(
        self,
        adapter: ComponentAdapter,
        start: Time | None = None,
        end: Time | None | datetime.timedelta = None,
    ):
        """Create an event repetition.

        - source - the icalendar Event
        - start - the start date/datetime to replace
        - stop - the end date/datetime to replace
        """
        self._adapter = adapter
        self.start = adapter.start if start is None else start
        self.end = adapter.end if end is None else end

    def as_component(self, keep_recurrence_attributes: bool) -> Component:  # noqa: FBT001
        """Create a shallow copy of the source component and modify some attributes."""
        return self._adapter.as_component(
            self.start, self.end, keep_recurrence_attributes
        )

    def is_in_span(self, span_start: Time, span_stop: Time) -> bool:
        """Return whether the component is in the span."""
        return time_span_contains_event(span_start, span_stop, self.start, self.end)

    def __lt__(self, other: Occurrence) -> bool:
        """Compare two occurrences for sorting.

        See https://stackoverflow.com/a/4010558/1320237
        """
        self_start, other_start = make_comparable((self.start, other.start))
        return self_start < other_start

    @cached_property
    def id(self) -> ComponentID:
        """The id of the component."""
        recurrence_id = (*self._adapter.recurrence_ids, self.start)[0]
        return (
            self._adapter.component_name(),
            self._adapter.uid,
            recurrence_id,
        )

    def __hash__(self) -> int:
        """Hash this for an occurrence."""
        return hash(self.id)

    def __eq__(self, other: Occurrence) -> bool:
        """self == other"""
        return self.id == other.id

    def component_name(self) -> str:
        """The name of this component."""
        return self._adapter.component_name()

    @property
    def uid(self) -> str:
        """The UID of this occurrence."""
        return self._adapter.uid

    def has_alarm(self, alarm: Alarm) -> bool:
        """Wether this alarm is in this occurrence."""
        return alarm in self._adapter.alarms

    @property
    def recurrence_ids(self) -> RecurrenceIDs:
        """The recurrence ids."""
        return self._adapter.recurrence_ids


class AlarmOccurrence(Occurrence):
    """Adapter for absolute alarms."""

    def __init__(
        self,
        trigger: datetime.datetime,
        alarm: Alarm,
        parent: ComponentAdapter | Occurrence,
    ) -> None:
        super().__init__(alarm, trigger, trigger)
        self.parent = parent
        self.alarm = alarm

    def as_component(self, keep_recurrence_attributes):
        """Return the alarm's parent as a modified component."""
        parent = self.parent.as_component(
            keep_recurrence_attributes=keep_recurrence_attributes
        )
        alarm_once = self.alarm.copy()
        alarm_once.TRIGGER = self.start
        alarm_once.REPEAT = 0
        parent.subcomponents = [alarm_once]
        return parent

    @cached_property
    def id(self) -> ComponentID:
        """The id of the component."""
        return (
            self.parent.component_name(),
            self.parent.uid,
            *self.parent.recurrence_ids[:1],
            self.start,
        )

    def __repr__(self) -> str:
        """repr(self)"""
        return (
            f"<{self.__class__.__name__} at {self.start} of"
            f" {self.alarm} in {self.parent}"
        )
