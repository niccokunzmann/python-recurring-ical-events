"""Test the pagination behaviour of the query."""

from datetime import date, timedelta
from typing import Callable, Iterator

import pytest
from icalendar import Component

from recurring_ical_events.occurrence import OccurrenceID
from recurring_ical_events.pages import Page, Pages
from recurring_ical_events.test.conftest import ICSCalendars
from recurring_ical_events.util import compare_greater


@pytest.fixture(params=[1, 5, 30])
def page_size(request: pytest.FixtureRequest) -> int:
    """Return the number of events per page."""
    return request.param


GET_PAGES = Callable[[], Pages]


def iterate_pages(get_pages: GET_PAGES):
    """Iterate over the pages and return all the events as a list."""
    pages = get_pages()
    for page in pages:
        components = page.components
        assert len(components) == pages.size or (
            not page.has_next_page() and 0 < len(components) <= pages.size
        )
        yield from components


def iterate_next_page(get_pages: GET_PAGES):
    """Iterate with the next page attribute."""
    pages = get_pages()
    while True:
        page = pages.generate_next_page()
        yield from page.components
        if not page:
            break


def continue_iteration_with_page_id(get_pages: Callable[[str], Pages]):
    """Restart the iteration process with a new pages object."""
    pages: Pages = get_pages()
    page = pages.generate_next_page()
    while page:
        yield from page.components
        assert (page.next_page_id == "") == page.is_last()
        if not page.next_page_id:
            break
        pages = get_pages(page.next_page_id)
        page = pages.generate_next_page()


@pytest.fixture(
    params=[iterate_pages, iterate_next_page, continue_iteration_with_page_id]
)
def page_iterator(
    request: pytest.FixtureRequest,
) -> Callable[[Pages], Iterator[Component]]:
    return request.param


check_calendars = pytest.mark.parametrize(
    ("calendar", "start", "stop", "expected_count"),
    [
        ("no_events", date(1970, 12, 11), date(2030, 12, 12), 0),
        ("one_event", date(2000, 12, 11), date(2020, 12, 12), 1),
        ("event_10_times", date(2020, 1, 13), date(2020, 1, 14), 1),
        ("event_10_times", date(2020, 1, 13), date(2023, 12, 14), 10),
        ("event_10_times", date(2020, 1, 13), None, 10),
        ("event_10_times", date(2020, 1, 13), date(1970, 12, 14), 0),
        ("several_events_at_the_same_time", date(2019, 1, 13), None, 10),
    ],
)


@check_calendars
def test_compare_events_with_expected(
    calendars: ICSCalendars,
    calendar: str,
    start: date,
    stop: date,
    page_size: int,
    page_iterator: Callable[[Pages], Iterator[Component]],
    expected_count: int,
):
    """Test the pagination with only one event."""

    def paginate(next_page_id: str = ""):
        return calendars[calendar].paginate(page_size, start, stop, next_page_id)

    count = 0
    for page_component, after_component in zip(
        page_iterator(paginate), calendars[calendar].after(start)
    ):
        assert page_component == after_component
        assert stop is None or compare_greater(stop, page_component.start)
        print(f"page_component: {page_component}")
        count += 1
    assert count == expected_count


def test_empty_page_bool():
    """Check an empty page."""
    assert not Page([])


def test_filled_page_bool():
    """Check the page has content."""
    assert Page([1])


@pytest.mark.parametrize("last_page", [Page([]), Page([1])])
def test_next_page_absent(last_page: Page):
    """Check not having a next page."""
    assert not last_page.has_next_page()
    assert last_page.next_page_id == ""
    assert last_page.is_last()


@pytest.mark.parametrize(
    "page", [Page([1, 2, 3], next_page_id="123"), Page([1], next_page_id="asd")]
)
def test_next_page_present(page: Page):
    """Check having a next page.

    We must at least have a component.
    """
    assert page.next_page_id != ""
    assert page.has_next_page()
    assert not page.is_last()


def test_pages_size_is_the_same_as_parameter(page_size: int):
    """The size parameter is passed."""
    pages = Pages([], page_size)
    assert pages.size == page_size


@pytest.mark.parametrize("invalid_page_size", [-1, 0, -1100])
def test_paginate_invalid_int(invalid_page_size):
    """Raise a ValueError if we have an invalid page size."""
    with pytest.raises(ValueError):
        Pages([], invalid_page_size)


def test_count_events(calendars: ICSCalendars):
    """Check that there is an event."""
    assert calendars.one_event.count() == 1
    assert calendars.no_events.count() == 0


def test_cannot_escape_start_with_pagination_id(calendars: ICSCalendars):
    """The pagination id is passed from outside to this.

    We must make sure that we cannot be hacked.
    """
    start = date(2020, 1, 17)  # the first event is at the 13th
    pages: Pages = calendars.event_10_times.paginate(1, start)
    first_page = pages.generate_next_page()
    assert first_page
    assert not first_page.is_last()
    # request the next page but with an earlier id
    oid = OccurrenceID.from_string(first_page.next_page_id)
    new_oid = OccurrenceID(
        oid.name, oid.uid, oid.recurrence_id, oid.start - timedelta(days=30)
    )
    pages: Pages = calendars.event_10_times.paginate(
        1, start, next_page_id=new_oid.to_string()
    )
    # we cannot be earlier than start though
    next_page = pages.generate_next_page()
    assert next_page.components[0].start == first_page.components[0].start
    assert next_page.components == first_page.components


def invalidate_recurrence_id(next_page_id: str) -> str:
    """We change the recurrence id."""
    oid = OccurrenceID.from_string(next_page_id)
    return OccurrenceID(oid.name, oid.uid, date(1990, 10, 11), oid.start).to_string()


def invalidate_uid(next_page_id: str) -> str:
    """We change the uid."""
    oid = OccurrenceID.from_string(next_page_id)
    return OccurrenceID(
        oid.name, oid.uid + "-changed", oid.recurrence_id, oid.start
    ).to_string()


@pytest.mark.parametrize("invalidate_id", [invalidate_uid, invalidate_recurrence_id])
def test_invalid_recurrence_id_uid_will_not_go_though_all_events_but_stop_after_that_date(
    calendars: ICSCalendars, invalidate_id: Callable[[str], str]
):
    """If we cannot find an event, the page starts on the day it should."""
    start = date(2020, 1, 17)  # the first event is at the 13th
    pages: Pages = calendars.event_10_times.paginate(1, start)
    first_page = pages.generate_next_page()
    real_next_page = pages.generate_next_page()
    # invalidate the event we are looking for
    pages: Pages = calendars.event_10_times.paginate(
        1, start, next_page_id=invalidate_id(first_page.next_page_id)
    )
    # we will still find the correct event because of the start
    # and we only have one event per day
    modified_next_page = pages.generate_next_page()
    assert real_next_page.components[0].start == modified_next_page.components[0].start
    assert real_next_page.components == modified_next_page.components
