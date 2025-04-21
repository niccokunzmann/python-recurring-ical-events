"""Selecting components by name."""

from __future__ import annotations

import contextlib
from collections import defaultdict
from typing import TYPE_CHECKING, Sequence

from recurring_ical_events.adapters.event import EventAdapter
from recurring_ical_events.adapters.journal import JournalAdapter
from recurring_ical_events.adapters.todo import TodoAdapter
from recurring_ical_events.occurrence import Occurrence
from recurring_ical_events.selection.alarm import Alarms
from recurring_ical_events.selection.base import SelectComponents
from recurring_ical_events.series import Series
from recurring_ical_events.util import cached_property

if TYPE_CHECKING:
    from icalendar.cal import Component

    from recurring_ical_events.adapters.component import ComponentAdapter


class ComponentsWithName(SelectComponents):
    """This is a component collecttion strategy.

    Components can be collected in different ways.
    This class allows extension of the functionality by
    - subclassing to filter the resulting components
    - composition to combine collection behavior (see AllKnownComponents)
    """

    component_adapters: list[type[ComponentAdapter] | SelectComponents] = [
        EventAdapter,
        TodoAdapter,
        JournalAdapter,
        Alarms(),
    ]

    @cached_property
    def _component_adapters(self) -> dict[str : type[ComponentAdapter]]:
        """A mapping of component adapters."""
        return {
            adapter.component_name(): adapter for adapter in self.component_adapters
        }

    def __init__(
        self,
        name: str,
        adapter: type[ComponentAdapter] | None = None,
        series: type[Series] = Series,
        occurrence: type[Occurrence] = Occurrence,
    ) -> None:
        """Create a new way of collecting components.

        name - the name of the component to collect ("VEVENT", "VTODO", "VJOURNAL")
        adapter - the adapter to use for these components with that name
        series - the series class that hold a series of components
        occurrence - the occurrence class that creates the resulting components
        """
        if adapter is None:
            if name not in self._component_adapters:
                raise ValueError(
                    f'"{name}" is an unknown name for a '
                    "recurring component. "
                    f"I only know these: {', '.join(self._component_adapters)}."
                )
            adapter = self._component_adapters[name]
        if occurrence is not Occurrence:
            _occurrence = occurrence

            class series(series):  # noqa: N801
                occurrence = _occurrence

        self._name = name
        self._series = series
        self._adapter = adapter

    def collect_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect all components from the source component.

        suppress_errors - a list of errors that should be suppressed.
            A Series of events with such an error is removed from all results.
        """
        if isinstance(self._adapter, SelectComponents):
            return self._adapter.collect_series_from(source, suppress_errors)
        components: dict[str, list[Component]] = defaultdict(list)  # UID -> components
        for component in source.walk(self._name):
            adapter = self._adapter(component)
            components[adapter.uid].append(adapter)
        result = []
        for components in components.values():
            with contextlib.suppress(suppress_errors):
                result.append(self._series(components))
        return result


__all__ = ["ComponentsWithName"]
