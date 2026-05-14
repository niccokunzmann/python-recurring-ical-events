"""Pagination for recurring ical events.

See

- https://github.com/niccokunzmann/python-recurring-ical-events/issues/211
- https://github.com/niccokunzmann/python-recurring-ical-events/issues/217
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Iterator, Optional, TypeVar

from recurring_ical_events.util import compare_greater

if TYPE_CHECKING:
    from icalendar import Component

    from recurring_ical_events.occurrence import Occurrence
    from recurring_ical_events.types import Time

T = TypeVar("T")


class _PageBase(Generic[T]):
    """Shared behaviour for :class:`Page` and :class:`OccurrencePage`."""

    def __init__(self, items: list[T], next_page_id: str = ""):
        self._items = items
        self._next_page_id = next_page_id

    def has_next_page(self) -> bool:
        """Wether there is a page following this one."""
        return self._next_page_id != ""

    @property
    def next_page_id(self) -> str:
        """The id of the next page or ``''``."""
        return self._next_page_id

    def is_last(self) -> bool:
        """Wether this is the last page and there is no other page following."""
        return self._next_page_id == ""

    def __len__(self) -> int:
        """The number of items on this page."""
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over the items."""
        return iter(self._items)


class Page(_PageBase["Component"]):
    """One page in a series of pages.

    Examples:
        Check if the page has components.

        .. code-block:: python

            if page:
                print(f"We have {len(page)} components.")

        Go though the components:

        .. code-block:: python

            for component in page:
                print(component)
    """

    def __init__(self, components: list[Component], next_page_id: str = ""):
        """ "Create a new page."""
        super().__init__(components, next_page_id)

    @property
    def components(self) -> list[Component]:
        """All the components of this page."""
        return self._items


class OccurrencePage(_PageBase["Occurrence"]):
    """One page of occurrences in a series of pages.

    Examples:
        Check if the page has occurrences.

        .. code-block:: python

            if page:
                print(f"We have {len(page)} occurrences.")

        Go though the occurrences:

        .. code-block:: python

            for occurrence in page:
                print(occurrence)
    """

    def __init__(self, occurrences: list[Occurrence], next_page_id: str = ""):
        """Create a new occurrence page."""
        super().__init__(occurrences, next_page_id)

    @property
    def occurrences(self) -> list[Occurrence]:
        """All the occurrences of this page."""
        return self._items


class _PagesBase(Generic[T]):
    """Shared iteration state for :class:`Pages` and :class:`OccurrencePages`."""

    def __init__(
        self,
        occurrence_iterator: Iterator[Occurrence],
        size: int,
        stop: Optional[Time] = None,
    ):
        self._iterator = occurrence_iterator
        self._stop = stop
        self._size = size
        if self._size <= 0:
            raise ValueError(f"A page must have at least one item, not {self._size}.")
        self._next_occurrence: Optional[Occurrence] = None
        for occurrence in self._iterator:
            if self._stop is None or compare_greater(self._stop, occurrence.start):
                self._next_occurrence = occurrence
            break

    @property
    def size(self) -> int:
        """The maximum number of components per page."""
        return self._size

    def generate_next_page(self) -> T:
        """Generate the next page.

        In contrast to ``next(pages)``, this does not raise :class:`StopIteration`.
        But it works the same: the next page is generated and returned.
        The last page is empty.
        """
        for page in self:
            return page
        return self._empty_page()

    def _empty_page(self) -> T:
        """The empty page returned past the end of the iterator."""
        raise NotImplementedError

    def _collect_next_page(self) -> list[Occurrence]:
        """Pull the next page-worth of occurrences from the source iterator."""
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
        return occurrences

    def _next_page_id_string(self) -> str:
        """The id of the page following the one we just emitted, or ``''``."""
        return (
            self._next_occurrence.id.to_string()
            if self._next_occurrence is not None
            else ""
        )


class Pages(_PagesBase["Page"]):
    """A pagination configuration to iterate over pages.

    This is an :class:`Iterator` that returns :class:`Page` objects.
    """

    def __init__(
        self,
        occurrence_iterator: Iterator[Occurrence],
        size: int,
        stop: Optional[Time] = None,
        keep_recurrence_attributes: bool = False,  # noqa: FBT001
    ):
        """Create a new paginated iterator over components."""
        super().__init__(occurrence_iterator, size, stop)
        self._keep_recurrence_attributes = keep_recurrence_attributes

    def _empty_page(self) -> Page:
        return Page([])

    def __next__(self) -> Page:
        """Return the next page."""
        occurrences = self._collect_next_page()
        return Page(
            [
                occurrence.as_component(self._keep_recurrence_attributes)
                for occurrence in occurrences
            ],
            next_page_id=self._next_page_id_string(),
        )

    def __iter__(self) -> Pages:
        """Return the iterator."""
        return self


class OccurrencePages(_PagesBase["OccurrencePage"]):
    """A pagination configuration to iterate over pages of occurrences.

    This is an :class:`Iterator` that returns :class:`OccurrencePage` objects.
    """

    def _empty_page(self) -> OccurrencePage:
        return OccurrencePage([])

    def __next__(self) -> OccurrencePage:
        """Return the next page."""
        occurrences = self._collect_next_page()
        return OccurrencePage(occurrences, next_page_id=self._next_page_id_string())

    def __iter__(self) -> OccurrencePages:
        """Return the iterator."""
        return self


__all__ = ["OccurrencePage", "OccurrencePages", "Page", "Pages"]
