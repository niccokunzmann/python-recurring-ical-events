"""This tests extneding and modifying the behaviour of recurring ical events."""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import pytest
from icalendar.cal import Component

from recurring_ical_events import (
    AllKnownComponents,
    EventAdapter,
    JournalAdapter,
    Occurrence,
    SelectComponents,
    Series,
    TodoAdapter,
    of,
)

if TYPE_CHECKING:
    from icalendar.cal import Component


class SelectUID1(SelectComponents):
    """Collect only one UID."""

    def __init__(self, uid: str) -> None:
        self.uid = uid

    def collect_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        return [
            series
            for adapter in [EventAdapter, JournalAdapter, TodoAdapter]
            for series in adapter.collect_series_from(source, suppress_errors)
            if series.uid == self.uid
        ]


class SelectUID2(AllKnownComponents):
    def __init__(self, uid: str) -> None:
        super().__init__()
        self.uid = uid

    def collect_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        return [
            series
            for series in super().collect_series_from(source, suppress_errors)
            if series.uid == self.uid
        ]


class SelectUID3(SelectComponents):
    def __init__(self, uid: str) -> None:
        self.uid = uid

    def collect_series_from(
        self,
        source: Component,
        suppress_errors: tuple[Exception],  # noqa: ARG002
    ) -> Sequence[Series]:
        components: list[Component] = []
        for component in source.walk("VEVENT"):
            if component.get("UID") == self.uid:
                components.append(EventAdapter(component))  # noqa: PERF401
        return [Series(components)] if components else []


@pytest.mark.parametrize("collector", [SelectUID1, SelectUID2, SelectUID3])
def test_collect_only_one_uid(calendars, collector):
    """Test that only one UID is used."""
    uid = "4mm2ak3in2j3pllqdk1ubtbp9p@google.com"
    query = of(calendars.raw.machbar_16_feb_2019, components=[collector(uid)])
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
    query = of(
        calendars.raw.one_event,
        components=[AllKnownComponents(occurrence=MyOccurrence)],
    )
    event = next(query.all())
    assert event["X-MY-ATTRIBUTE"] == "my occurrence"
