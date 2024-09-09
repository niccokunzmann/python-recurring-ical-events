"""This tests extneding and modifying the behaviour of recurring ical events."""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from recurring_ical_events import (
    CollectComponents,
    EventAdapter,
    JournalAdapter,
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
