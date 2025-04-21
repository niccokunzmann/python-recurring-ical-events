"""Occurrences of events and other components."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, NamedTuple, Optional

from icalendar import Alarm

from recurring_ical_events.adapters.component import ComponentAdapter
from recurring_ical_events.util import (
    cached_property,
    make_comparable,
    time_span_contains_event,
)

if TYPE_CHECKING:
    from icalendar import Alarm
    from icalendar.cal import Component

    from recurring_ical_events.adapters.component import ComponentAdapter
    from recurring_ical_events.types import UID, RecurrenceIDs, Time


class OccurrenceID(NamedTuple):
    """The ID of a component's occurrence to identify it clearly.

    Attributes:
        name: The name of the component, e.g. "VEVENT"
        uid: The UID of the component.
        recurrence_id: The Recurrence-ID of the component in UTC but without tzinfo.
        start: The start of the component
    """

    name: str
    uid: UID
    recurrence_id: Optional[Time]
    start: Time

    def to_string(self) -> str:
        """Return a string representation of this id."""
        return "#".join(
            [
                self.name,
                self.recurrence_id.isoformat() if self.recurrence_id else "",
                self.start.isoformat(),
                self.uid,
            ]
        )

    @staticmethod
    def _dt_from_string(iso_string: str) -> Time:
        """Create a datetime from the string representation."""
        if len(iso_string) == 10:
            return date.fromisoformat(iso_string)
        return datetime.fromisoformat(iso_string)

    @classmethod
    def from_string(cls, string_id: str) -> OccurrenceID:
        """Parse a string and return the component id."""
        name, recurrence_id, start, uid = string_id.split("#", 3)
        return cls(
            name,
            uid,
            cls._dt_from_string(recurrence_id) if recurrence_id else None,
            cls._dt_from_string(start),
        )

    @classmethod
    def from_occurrence(
        cls, name: str, uid: str, recurrence_ids: RecurrenceIDs, start: Time
    ):
        """Create a new OccurrenceID from the given values.

        Args:
            name: The component name.
            uid: The UID string.
            recurrence_ids: The recurrence ID tuple.
                This is expected as UTC with tzinfo being None.
            start: start time of the component either with or without timezone
        """
        return cls(name, uid, recurrence_ids[0] if recurrence_ids else None, start)


class Occurrence:
    """A repetition of an event."""

    def __init__(
        self,
        adapter: ComponentAdapter,
        start: Time | None = None,
        end: Time | None | timedelta = None,
        sequence: int = -1,
    ):
        """Create an event repetition.

        - source - the icalendar Event
        - start - the start date/datetime to replace
        - stop - the end date/datetime to replace
        - sequence - if positive or 0, this sets the SEQUENCE property
        """
        self._adapter = adapter
        self.start = adapter.start if start is None else start
        self.end = adapter.end if end is None else end
        self.sequence = sequence

    def as_component(self, keep_recurrence_attributes: bool) -> Component:  # noqa: FBT001
        """Create a shallow copy of the source component and modify some attributes."""
        component = self._adapter.as_component(
            self.start, self.end, keep_recurrence_attributes
        )
        if self.sequence >= 0:
            component["SEQUENCE"] = self.sequence
        return component

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
    def id(self) -> OccurrenceID:
        """The id of the component."""
        return OccurrenceID.from_occurrence(
            self._adapter.component_name(),
            self._adapter.uid,
            self._adapter.recurrence_ids,
            self.start,
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
        trigger: datetime,
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
    def id(self) -> OccurrenceID:
        """The id of the component."""
        return OccurrenceID.from_occurrence(
            self.parent.component_name(),
            self.parent.uid,
            self.parent.recurrence_ids,
            self.start,
        )

    def __repr__(self) -> str:
        """repr(self)"""
        return (
            f"<{self.__class__.__name__} at {self.start} of"
            f" {self.alarm} in {self.parent}"
        )


__all__ = [
    "AlarmOccurrence",
    "Occurrence",
    "OccurrenceID",
]
