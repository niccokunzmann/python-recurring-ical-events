"""This tests extneding and modifying the behaviour of recurring ical events."""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

import pytest
from icalendar.cal import Component

from recurring_ical_events import (
    of,
)
from recurring_ical_events.adapters.event import EventAdapter
from recurring_ical_events.adapters.journal import JournalAdapter
from recurring_ical_events.adapters.todo import TodoAdapter
from recurring_ical_events.occurrence import Occurrence
from recurring_ical_events.selection.all import AllKnownComponents
from recurring_ical_events.selection.base import SelectComponents
from recurring_ical_events.selection.name import ComponentsWithName
from recurring_ical_events.series import Series

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
        print(components)
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


@pytest.mark.parametrize(
    ("calendar", "count", "collector"),
    [
        # all
        ("one_event", 1, AllKnownComponents()),
        ("issue_97_simple_todo", 1, AllKnownComponents()),
        ("issue_97_simple_journal", 1, AllKnownComponents()),
        # events
        ("one_event", 1, ComponentsWithName("VEVENT")),
        ("issue_97_simple_todo", 0, ComponentsWithName("VEVENT")),
        ("issue_97_simple_journal", 0, ComponentsWithName("VEVENT")),
        # todos
        ("one_event", 0, ComponentsWithName("VTODO")),
        ("issue_97_simple_todo", 1, ComponentsWithName("VTODO")),
        ("issue_97_simple_journal", 0, ComponentsWithName("VTODO")),
        # journals
        ("one_event", 0, ComponentsWithName("VJOURNAL")),
        ("issue_97_simple_todo", 0, ComponentsWithName("VJOURNAL")),
        ("issue_97_simple_journal", 1, ComponentsWithName("VJOURNAL")),
    ],
)
def test_we_collect_all_components(
    calendars, calendar, count, collector: SelectComponents
):
    """Check that the calendars have the right amount of series collected."""
    series = collector.collect_series_from(calendars.raw[calendar], [])
    print(series)
    assert len(series) == count
