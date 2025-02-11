"""Pagination for recurring ical events.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/211
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional

from recurring_ical_events.util import compare_greater

if TYPE_CHECKING:
    from icalendar import Component

    from recurring_ical_events.occurrence import Occurrence
    from recurring_ical_events.types import Time


class Page:
    """One page in a series of pages."""

    def __init__(self, components: list[Component], next_page_id: str = ""):
        """ "Create a new page."""
        self._components = components
        self._next_page_id = next_page_id

    @property
    def components(self) -> list[Component]:
        """All the components of one page."""
        return self._components

    def has_next_page(self) -> bool:
        """Wether there is a page following this one."""
        return self.next_page_id != ""

    @property
    def next_page_id(self) -> str:
        """Return the id of the next page or ''."""
        return self._next_page_id

    def __len__(self) -> int:
        """The number of components."""
        return len(self.components)

    def is_last(self):
        """Wether this is the last page and there is no other page following."""
        return self._next_page_id == ""

    def __iter__(self) -> Iterator[Component]:
        """Return an iterator over the components."""
        return iter(self.components)


class Pages:
    """A pagination configuration to iterate over pages."""

    def __init__(
        self,
        occurrence_iterator: Iterator[Occurrence],
        size: int,
        stop: Optional[Time] = None,
        keep_recurrence_attributes: bool = False,  # noqa: FBT001
    ):
        """Create a new paginated iterator over components."""
        self._iterator = occurrence_iterator
        self._stop = stop
        self._size = size
        if self._size <= 0:
            raise ValueError(
                f"A page must have at least one component, not {self._size}."
            )
        self._keep_recurrence_attributes = keep_recurrence_attributes
        self._next_occurrence: Optional[Occurrence] = None
        for occurrence in self._iterator:
            if self._stop is None or compare_greater(self._stop, occurrence.start):
                self._next_occurrence = occurrence
            break

    @property
    def size(self) -> int:
        """The maximum number of components per page."""
        return self._size

    def generate_next_page(self) -> Page:
        """Generate the next page.

        In contrast to next(self), this does not raise StopIteration.
        But it works the same: the next page is generated and returned.
        """
        for page in self:
            return page
        return Page([])

    def __next__(self) -> Page:
        """Return the next page."""
        if self._next_occurrence is None:
            raise StopIteration
        last_occurrence = self._next_occurrence
        occurrences = [last_occurrence]
        for occurrence in self._iterator:
            if self._stop is not None and compare_greater(occurrence.start, self._stop):
                break
            last_occurrence = occurrence
            if len(occurrences) < self._size:
                occurrences.append(occurrence)
            else:
                break
        if occurrences[-1] == last_occurrence:
            self._next_occurrence = None
        else:
            self._next_occurrence = last_occurrence
        return self._create_page_from_occurrences(occurrences)

    def _create_page_from_occurrences(self, occurrences: list[Occurrence]) -> Page:
        """Create a new page from the occurrences listed."""
        return Page(
            [
                occurrence.as_component(self._keep_recurrence_attributes)
                for occurrence in occurrences
            ],
            next_page_id=self._next_occurrence.id.to_string()
            if self._next_occurrence is not None
            else "",
        )

    def __iter__(self) -> Pages:
        """Return the iterator."""
        return self


__all__ = ["Page", "Pages"]
