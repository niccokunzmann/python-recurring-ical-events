"""Base interface for selection of components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from icalendar.cal import Component

    from recurring_ical_events.series import Series


class SelectComponents(ABC):
    """Abstract class to select components from a calendar."""

    @staticmethod
    def component_name():
        """The name of the component if there is only one."""
        raise NotImplementedError("This should be implemented in subclasses.")

    @abstractmethod
    def collect_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect all components from the source grouped together into a series.

        suppress_errors - a list of errors that should be suppressed.
            A Series of events with such an error is removed from all results.
        """


__all__ = ["SelectComponents"]
