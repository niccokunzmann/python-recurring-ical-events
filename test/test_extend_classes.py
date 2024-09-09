"""This tests extneding and modifying the behaviour of recurring ical events."""
from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Sequence

from icalendar.cal import Component

from recurring_ical_events import (
    CollectComponents,
    CollectKnownComponents,
    EventAdapter,
    JournalAdapter,
    Occurrence,
    Series,
    TodoAdapter,
    of,
)

if TYPE_CHECKING:
    from icalendar.cal import Component


class CollectOneUIDEvent(CollectComponents):
    """Collect only one UID."""

    def __init__(self, uid:str) -> None:
        self.uid = uid

    def collect_components(self, source: Component, suppress_errors: tuple[Exception]) -> Sequence[Series]:
        return [
            series
            for adapter in [EventAdapter, JournalAdapter, TodoAdapter]
            for series in adapter.collect_components(source, suppress_errors)
            if series.uid == self.uid
        ]


def test_collect_only_one_uid(calendars):
    """Test that only one UID is used."""
    one_uid = CollectOneUIDEvent("4mm2ak3in2j3pllqdk1ubtbp9p@google.com")
    query = of(calendars.raw.machbar_16_feb_2019, components=[one_uid])
    assert query.count() == 1


class MyOccurrence(Occurrence):
    """An occurrence that modifies the component."""

    def as_component(self, keep_recurrence_attributes: bool) -> Component:  # noqa: FBT001
        """Return a shallow copy of the source component and modify some attributes."""
        component = super().as_component(keep_recurrence_attributes)
        component["X-MY-ATTRIBUTE"] = "my occurrence"
        return component

def test_added_attributes(calendars):
    """Test that attributes are added."""
    query = of(calendars.raw.one_event, components=[CollectKnownComponents(occurrence=MyOccurrence)])
    event = next(query.all())
    assert event["X-MY-ATTRIBUTE"] == "my occurrence"
