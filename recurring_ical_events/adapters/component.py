"""Base class for all adapters."""

from __future__ import annotations

import datetime
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Sequence

from icalendar.prop import vDDDTypes

from recurring_ical_events.util import (
    cached_property,
    make_comparable,
    time_span_contains_event,
    to_recurrence_ids,
)

if TYPE_CHECKING:
    from icalendar import Alarm
    from icalendar.cal import Component

    from recurring_ical_events.series import Series
    from recurring_ical_events.types import UID, RecurrenceIDs, Time


class ComponentAdapter(ABC):
    """A unified interface to work with icalendar components."""

    ATTRIBUTES_TO_DELETE_ON_COPY = ["RRULE", "RDATE", "EXDATE"]

    @staticmethod
    @abstractmethod
    def component_name() -> str:
        """The icalendar component name."""

    def __init__(self, component: Component):
        """Create a new adapter."""
        self._component = component

    @property
    def alarms(self) -> list[Alarm]:
        """The alarms in this component."""
        return self._component.walk("VALARM")

    @property
    def end_property(self) -> str | None:
        """The name of the end property."""
        return None

    @property
    def start(self) -> Time:
        """The start time."""
        return self.span[0]

    @property
    def end(self) -> Time:
        """The end time."""
        return self.span[1]

    @cached_property
    def span(self):
        """Return (start, end)."""
        return make_comparable((self.raw_start, self.raw_end))

    @property
    @abstractmethod
    def raw_start(self):
        """Return the start property of the component."""

    @property
    @abstractmethod
    def raw_end(self):
        """Return the start property of the component."""

    @property
    def uid(self) -> UID:
        """The UID of a component.

        UID is required by RFC5545.
        If the UID is absent, we use the Python ID.
        """
        return self._component.get("UID", str(id(self._component)))

    @classmethod
    def collect_series_from(
        cls, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect all components for this adapter.

        This is a shortcut.
        """
        from recurring_ical_events.selection.name import ComponentsWithName

        return ComponentsWithName(cls.component_name(), cls).collect_series_from(
            source, suppress_errors
        )

    def as_component(
        self,
        start: Optional[Time] = None,
        stop: Optional[Time] = None,
        keep_recurrence_attributes: bool = True,  # noqa: FBT001
    ):
        """Create a shallow copy of the source event and modify some attributes."""
        copied_component = self._component.copy()
        copied_component["DTSTART"] = vDDDTypes(self.start if start is None else start)
        copied_component.pop("DURATION", None)  # remove duplication in event length
        if self.end_property is not None:
            copied_component[self.end_property] = vDDDTypes(
                self.end if stop is None else stop
            )
        if not keep_recurrence_attributes:
            for attribute in self.ATTRIBUTES_TO_DELETE_ON_COPY:
                if attribute in copied_component:
                    del copied_component[attribute]
        for subcomponent in self._component.subcomponents:
            copied_component.add_component(subcomponent)
        if "RECURRENCE-ID" not in copied_component:
            copied_component["RECURRENCE-ID"] = copied_component["DTSTART"]
        return copied_component

    @cached_property
    def recurrence_ids(self) -> RecurrenceIDs:
        """The recurrence ids of the component that might be used to identify it."""
        recurrence_id = self._component.get("RECURRENCE-ID")
        if recurrence_id is None:
            return ()
        return to_recurrence_ids(recurrence_id.dt)

    @cached_property
    def this_and_future(self) -> bool:
        """The recurrence ids has a thisand future range property"""
        recurrence_id = self._component.get("RECURRENCE-ID")
        if recurrence_id is None:
            return False
        if "RANGE" in recurrence_id.params:
            return recurrence_id.params["RANGE"] == "THISANDFUTURE"
        return False

    def is_modification(self) -> bool:
        """Whether the adapter is a modification."""
        return bool(self.recurrence_ids)

    @cached_property
    def sequence(self) -> int:
        """The sequence in the history of modification.

        The sequence is negative if none was found.
        """
        return self._component.get("SEQUENCE", -1)

    def __repr__(self) -> str:
        """Debug representation with more info."""
        return (
            f"<{self.__class__.__name__} UID={self.uid} start={self.start} "
            f"recurrence_ids={self.recurrence_ids} sequence={self.sequence} "
            f"end={self.end}>"
        )

    @cached_property
    def exdates(self) -> list[Time]:
        """A list of exdates."""
        result: list[Time] = []
        exdates = self._component.get("EXDATE", [])
        for exdates in (exdates,) if not isinstance(exdates, list) else exdates:
            result.extend(exdate.dt for exdate in exdates.dts)
        return result

    @cached_property
    def rrules(self) -> set[str]:
        """A list of rrules of this component."""
        rules = self._component.get("RRULE", None)
        if not rules:
            return set()
        return {
            rrule.to_ical().decode()
            for rrule in (rules if isinstance(rules, list) else [rules])
        }

    @cached_property
    def rdates(self) -> list[Time, tuple[Time, Time]]:
        """A list of rdates, possibly a period."""
        rdates = self._component.get("RDATE", [])
        result = []
        for rdates in (rdates,) if not isinstance(rdates, list) else rdates:
            result.extend(rdate.dt for rdate in rdates.dts)
        return result

    @cached_property
    def duration(self) -> datetime.timedelta:
        """The duration of the component."""
        return self.end - self.start

    def is_in_span(self, span_start: Time, span_stop: Time) -> bool:
        """Return whether the component is in the span."""
        return time_span_contains_event(span_start, span_stop, self.start, self.end)

    @cached_property
    def extend_query_span_by(self) -> tuple[datetime.timedelta, datetime.timedelta]:
        """Calculate how much we extend the query span.

        If an event is long, we need to extend the query span by the event's duration.
        If an event has moved, we need to make sure that that is included, too.

        This is so that the RECURRENCE-ID falls within the modified span.
        Imagine if the span is exactly a second. How much would we need to query
        forward and backward to capture the recurrence id?

        Returns two positive spans: (subtract_from_start, add_to_stop)
        """
        subtract_from_start = self.duration
        add_to_stop = datetime.timedelta(0)
        recurrence_id_prop = self._component.get("RECURRENCE-ID")
        if recurrence_id_prop:
            start, end, recurrence_id = make_comparable(
                (self.start, self.end, recurrence_id_prop.dt)
            )
            if start < recurrence_id:
                add_to_stop = recurrence_id - start
            if start > recurrence_id:
                subtract_from_start = end - recurrence_id
        return subtract_from_start, add_to_stop

    @cached_property
    def move_recurrences_by(self) -> datetime.timedelta:
        """Occurrences of this component should be moved by this amount.

        Usually, the occurrence starts at the new start time.
        However, if we have a RANGE=THISANDFUTURE, we need to move the occurrence.

        RFC 5545:

            When the given recurrence instance is
            rescheduled, all subsequent instances are also rescheduled by the
            same time difference.  For instance, if the given recurrence
            instance is rescheduled to start 2 hours later, then all
            subsequent instances are also rescheduled 2 hours later.
            Similarly, if the duration of the given recurrence instance is
            modified, then all subsequence instances are also modified to have
            this same duration.
        """
        if self.this_and_future:
            recurrence_id_prop = self._component.get("RECURRENCE-ID")
            assert recurrence_id_prop, "RANGE=THISANDFUTURE implies RECURRENCE-ID."
            start, recurrence_id = make_comparable((self.start, recurrence_id_prop.dt))
            return start - recurrence_id
        return datetime.timedelta(0)


__all__ = ["ComponentAdapter"]
