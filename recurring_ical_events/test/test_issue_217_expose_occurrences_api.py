"""Test the occurrence-returning query and pagination API."""

from datetime import date, datetime, timedelta
from typing import Callable, Iterator

import pytest

import recurring_ical_events
from recurring_ical_events.occurrence import (
    AlarmOccurrence,
    Occurrence,
    OccurrenceID,
)
from recurring_ical_events.pages import (
    OccurrencePage,
    OccurrencePages,
    Page,
    Pages,
)
from recurring_ical_events.test.conftest import ICSCalendars


def _to_components(occurrences):
    """Convert occurrences to components the same way the public API does."""
    return [
        occurrence.as_component(keep_recurrence_attributes=False)
        for occurrence in occurrences
    ]


check_calendars = pytest.mark.parametrize(
    "calendar",
    [
        "no_events",
        "one_event",
        "event_10_times",
        "several_events_at_the_same_time",
        "three_events",
    ],
)


@check_calendars
@pytest.mark.parametrize(
    "between_args",
    [
        ((2000, 1, 1), (2030, 1, 1)),
        ((2020, 1, 13), (2020, 1, 14)),
        ((1970, 1, 1), (1971, 1, 1)),
    ],
)
def test_occurrences_between_matches_between(
    calendars: ICSCalendars, calendar: str, between_args: tuple
):
    """``occurrences_between`` produces the same components as ``between``."""
    query = calendars[calendar]
    start, stop = between_args
    assert _to_components(query.occurrences_between(start, stop)) == query.between(
        start, stop
    )


@check_calendars
@pytest.mark.parametrize(
    "at_argument",
    [
        2020,
        (2020,),
        (2020, 1),
        (2020, 1, 13),
        "20200113",
        date(2020, 1, 13),
        datetime(2020, 1, 13, 7, 45),
        (2020, 1, 13, 7),
        (2020, 1, 13, 7, 45),
        (2020, 1, 13, 7, 45, 0),
    ],
)
def test_occurrences_at_matches_at(calendars: ICSCalendars, calendar: str, at_argument):
    """``occurrences_at`` and ``at`` agree for every supported input form."""
    query = calendars[calendar]
    assert _to_components(query.occurrences_at(at_argument)) == query.at(at_argument)


@check_calendars
def test_occurrences_after_matches_after(calendars: ICSCalendars, calendar: str):
    """``occurrences_after`` and ``after`` agree element by element."""
    limit = 20
    query = calendars[calendar]
    after_components = []
    for i, component in enumerate(query.after(date(2000, 1, 1))):
        if i >= limit:
            break
        after_components.append(component)
    occurrence_components = []
    for i, occurrence in enumerate(query.occurrences_after(date(2000, 1, 1))):
        if i >= limit:
            break
        occurrence_components.append(
            occurrence.as_component(keep_recurrence_attributes=False)
        )
    assert occurrence_components == after_components


@check_calendars
def test_occurrences_all_matches_all(calendars: ICSCalendars, calendar: str):
    """``occurrences_all`` and ``all`` agree element by element."""
    limit = 20
    query = calendars[calendar]
    all_components = []
    for i, component in enumerate(query.all()):
        if i >= limit:
            break
        all_components.append(component)
    occurrence_components = []
    for i, occurrence in enumerate(query.occurrences_all()):
        if i >= limit:
            break
        occurrence_components.append(
            occurrence.as_component(keep_recurrence_attributes=False)
        )
    assert occurrence_components == all_components


@check_calendars
def test_occurrences_count_matches_count(calendars: ICSCalendars, calendar: str):
    """``occurrences_count`` and ``count`` agree."""
    query = calendars[calendar]
    assert query.occurrences_count() == query.count()


def test_first_occurrence_matches_first(calendars: ICSCalendars):
    """``first_occurrence`` produces the same component as ``first``."""
    query = calendars.one_event
    assert (
        query.first_occurrence.as_component(keep_recurrence_attributes=False)
        == query.first
    )


def test_first_occurrence_raises_index_error_when_empty(calendars: ICSCalendars):
    """``first`` and ``first_occurrence`` both raise on an empty calendar."""
    query = calendars.no_events
    with pytest.raises(IndexError):
        _ = query.first
    with pytest.raises(IndexError):
        _ = query.first_occurrence


def test_first_occurrence_is_an_occurrence(calendars: ICSCalendars):
    """``first_occurrence`` returns an :class:`Occurrence` instance."""
    assert isinstance(calendars.one_event.first_occurrence, Occurrence)


@pytest.fixture(params=[1, 5, 30])
def page_size(request: pytest.FixtureRequest) -> int:
    return request.param


def _iterate_pages(get_pages: Callable[[], OccurrencePages]) -> Iterator[Occurrence]:
    pages = get_pages()
    for page in pages:
        occurrences = page.occurrences
        assert len(occurrences) == pages.size or (
            not page.has_next_page() and 0 < len(occurrences) <= pages.size
        )
        yield from occurrences


def _iterate_next_page(
    get_pages: Callable[[], OccurrencePages],
) -> Iterator[Occurrence]:
    pages = get_pages()
    while True:
        page = pages.generate_next_page()
        yield from page.occurrences
        if not page:
            break


def _continue_with_page_id(
    get_pages: Callable[[str], OccurrencePages],
) -> Iterator[Occurrence]:
    pages = get_pages()
    page = pages.generate_next_page()
    while page:
        yield from page.occurrences
        assert (page.next_page_id == "") == page.is_last()
        if not page.next_page_id:
            break
        pages = get_pages(page.next_page_id)
        page = pages.generate_next_page()


@pytest.fixture(params=[_iterate_pages, _iterate_next_page, _continue_with_page_id])
def occurrence_page_iterator(request: pytest.FixtureRequest):
    return request.param


@pytest.mark.parametrize(
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
def test_occurrences_paginate_matches_paginate(
    calendars: ICSCalendars,
    calendar: str,
    start: date,
    stop,
    page_size: int,
    occurrence_page_iterator,
    expected_count: int,
):
    """``occurrences_paginate`` produces the same components as ``paginate``."""

    def paginate(next_page_id: str = ""):
        return calendars[calendar].occurrences_paginate(
            page_size, start, stop, next_page_id
        )

    count = 0
    for occurrence, after_component in zip(
        occurrence_page_iterator(paginate), calendars[calendar].after(start)
    ):
        assert (
            occurrence.as_component(keep_recurrence_attributes=False) == after_component
        )
        count += 1
    assert count == expected_count


def test_empty_occurrence_page_bool():
    """An empty page is falsy."""
    assert not OccurrencePage([])


def test_filled_occurrence_page_bool():
    """A non-empty page is truthy."""
    assert OccurrencePage([object()])


@pytest.mark.parametrize("last_page", [OccurrencePage([]), OccurrencePage([object()])])
def test_occurrence_page_next_absent(last_page: OccurrencePage):
    """A page with no ``next_page_id`` reports itself as last."""
    assert not last_page.has_next_page()
    assert last_page.next_page_id == ""
    assert last_page.is_last()


@pytest.mark.parametrize(
    "page",
    [
        OccurrencePage([object(), object()], next_page_id="123"),
        OccurrencePage([object()], next_page_id="abc"),
    ],
)
def test_occurrence_page_next_present(page: OccurrencePage):
    """A page with a ``next_page_id`` reports itself as not last."""
    assert page.next_page_id != ""
    assert page.has_next_page()
    assert not page.is_last()


def test_occurrence_pages_size_is_the_same_as_parameter(page_size: int):
    """``OccurrencePages.size`` reflects the ``size`` constructor argument."""
    assert OccurrencePages(iter([]), page_size).size == page_size


@pytest.mark.parametrize("invalid_page_size", [-1, 0, -1100])
def test_occurrence_paginate_invalid_int(invalid_page_size: int):
    """Invalid sizes raise ``ValueError``."""
    with pytest.raises(ValueError):
        OccurrencePages(iter([]), invalid_page_size)


def test_occurrences_paginate_cannot_escape_start_with_pagination_id(
    calendars: ICSCalendars,
):
    """Tampered ``next_page_id`` start times can't reach behind ``earliest_end``."""
    start = date(2020, 1, 17)
    pages = calendars.event_10_times.occurrences_paginate(1, start)
    first_page = pages.generate_next_page()
    assert first_page
    assert not first_page.is_last()
    oid = OccurrenceID.from_string(first_page.next_page_id)
    rewound = OccurrenceID(
        oid.name, oid.uid, oid.recurrence_id, oid.start - timedelta(days=30)
    )
    pages = calendars.event_10_times.occurrences_paginate(
        1, start, next_page_id=rewound.to_string()
    )
    next_page = pages.generate_next_page()
    assert next_page.occurrences[0].start == first_page.occurrences[0].start


def _invalidate_recurrence_id(next_page_id: str) -> str:
    oid = OccurrenceID.from_string(next_page_id)
    return OccurrenceID(oid.name, oid.uid, date(1990, 10, 11), oid.start).to_string()


def _invalidate_uid(next_page_id: str) -> str:
    oid = OccurrenceID.from_string(next_page_id)
    return OccurrenceID(
        oid.name, oid.uid + "-changed", oid.recurrence_id, oid.start
    ).to_string()


@pytest.mark.parametrize("invalidate_id", [_invalidate_uid, _invalidate_recurrence_id])
def test_occurrences_paginate_invalid_id_falls_back_to_date(
    calendars: ICSCalendars, invalidate_id: Callable[[str], str]
):
    """If the resume id can't be found, pagination resumes at the requested date."""
    start = date(2020, 1, 17)
    pages = calendars.event_10_times.occurrences_paginate(1, start)
    first_page = pages.generate_next_page()
    real_next_page = pages.generate_next_page()
    pages = calendars.event_10_times.occurrences_paginate(
        1, start, next_page_id=invalidate_id(first_page.next_page_id)
    )
    modified_next_page = pages.generate_next_page()
    assert (
        real_next_page.occurrences[0].start == modified_next_page.occurrences[0].start
    )


def test_occurrences_paginate_resume_past_the_end_yields_no_pages(
    calendars: ICSCalendars,
):
    """A resume id past the last occurrence produces no pages."""
    far_future = OccurrenceID("VEVENT", "ghost-uid", None, date(9999, 1, 1)).to_string()
    pages = calendars.event_10_times.occurrences_paginate(1, next_page_id=far_future)
    first_page = pages.generate_next_page()
    assert len(first_page) == 0
    assert first_page.is_last()


def test_occurrence_pages_yield_occurrence_objects(calendars: ICSCalendars):
    """Pages from ``occurrences_paginate`` yield :class:`Occurrence` instances."""
    pages = calendars.event_10_times.occurrences_paginate(2)
    page = pages.generate_next_page()
    assert page
    for occurrence in page:
        assert isinstance(occurrence, Occurrence)


def test_alarm_pages_yield_alarm_occurrence_objects(calendars: ICSCalendars):
    """Alarm queries yield :class:`AlarmOccurrence` instances."""
    calendars.components = ["VALARM"]
    pages = calendars.alarm_15_min_before_event_snoozed.occurrences_paginate(2)
    page = pages.generate_next_page()
    assert page
    for occurrence in page:
        assert isinstance(occurrence, AlarmOccurrence)


def test_top_level_reexports_pagination_classes():
    """The pagination classes re-export from the package root."""
    assert recurring_ical_events.Page is Page
    assert recurring_ical_events.Pages is Pages
    assert recurring_ical_events.OccurrencePage is OccurrencePage
    assert recurring_ical_events.OccurrencePages is OccurrencePages


def test_paginated_occurrence_can_keep_recurrence_attributes(calendars: ICSCalendars):
    """The caller controls ``keep_recurrence_attributes`` at materialization time."""
    pages = calendars.event_10_times.occurrences_paginate(1)
    occurrence = pages.generate_next_page().occurrences[0]
    stripped = occurrence.as_component(keep_recurrence_attributes=False)
    kept = occurrence.as_component(keep_recurrence_attributes=True)
    assert "RRULE" not in stripped
    assert "RRULE" in kept
