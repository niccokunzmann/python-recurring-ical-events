"""Test the pagination behaviour of the query."""

from datetime import date
from typing import Callable, Iterator

import pytest
from icalendar import Component

from recurring_ical_events.pages import Page, Pages
from recurring_ical_events.test.conftest import ICSCalendars
from recurring_ical_events.util import compare_greater


@pytest.fixture(params=[1, 5, 30])
def page_size(request: pytest.FixtureRequest) -> int:
    """Return the number of events per page."""
    return request.param


def iterate_pages(pages: Pages):
    """Iterate over the pages and return all the events as a list."""
    for page in pages:
        components = page.components
        assert len(components) == pages.size or (
            not page.has_next_page and 0 < len(components) <= pages.size
        )
        yield from components


def iterate_next_page(pages: Pages):
    """Iterate with the next page attribute."""
    while True:
        page = pages.generate_next_page()
        yield from page.components
        if not page:
            break


@pytest.fixture(params=[iterate_pages, iterate_next_page])
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
    pages = calendars[calendar].paginate(page_size, start, stop)
    count = 0
    for page_component, after_component in zip(
        page_iterator(pages), calendars[calendar].after(start)
    ):
        assert page_component == after_component
        assert compare_greater(stop, page_component.start)
        print(f"page_component: {page_component}")
        count += 1
    assert count == expected_count


def test_end_after_start_returns_empty_page():
    pytest.skip("TODO")


def test_empty_page_bool():
    """Check an empty page."""
    assert not Page([])


def test_filled_page_bool():
    """Check the page has content."""
    assert Page([1])


def test_next_page_absent():
    """Check not having a next page."""
    assert not Page([]).has_next_page
    assert not Page([1]).has_next_page
    assert Page([]).next_page_id == ""


def test_next_page_present():
    """Check having a next page."""
    page = Page([1, 2], next_page_id="asd")
    assert page.next_page_id == "asd"
    assert page.has_next_page


def test_pages_size_is_the_same_as_parameter():
    pytest.skip("TODO")


def test_optional_stop_argument():
    pytest.skip("TODO")


def test_paginate_invalid_int():
    """Raise a ValueError if we have an invalid page size."""


def test_count_events(calendars: ICSCalendars):
    """Check that there is an event."""
    assert calendars.one_event.count() == 1
    assert calendars.no_events.count() == 0
