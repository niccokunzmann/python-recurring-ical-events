"""Selection of all components with the correct adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from recurring_ical_events.occurrence import Occurrence
from recurring_ical_events.selection.base import SelectComponents
from recurring_ical_events.selection.name import ComponentsWithName
from recurring_ical_events.series import Series

if TYPE_CHECKING:
    from icalendar.cal import Component

    from recurring_ical_events.adapters.component import ComponentAdapter


class AllKnownComponents(SelectComponents):
    """Group all known components into series."""

    @property
    def _component_adapters(self) -> Sequence[ComponentAdapter]:
        """Return all known component adapters."""
        return ComponentsWithName.component_adapters

    @property
    def names(self) -> list[str]:
        """Return the names of the components to collect."""
        result = [adapter.component_name() for adapter in self._component_adapters]
        result.sort()
        return result

    def __init__(
        self,
        series: type[Series] = Series,
        occurrence: type[Occurrence] = Occurrence,
        collector: type[ComponentsWithName] = ComponentsWithName,
    ) -> None:
        """Collect all known components and overide the series and occurrence.

        series - the Series class to override that is queried for Occurrences
        occurrence - the occurrence class that creates the resulting components
        collector - if you want to override the SelectComponentsByName class
        """
        self._series = series
        self._occurrence = occurrence
        self._collector = collector

    def collect_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect the components from the source groups into a series."""
        result = []
        for name in self.names:
            collector = self._collector(
                name, series=self._series, occurrence=self._occurrence
            )
            result.extend(collector.collect_series_from(source, suppress_errors))
        return result


__all__ = ["AllKnownComponents"]
