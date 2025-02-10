import pytest

from recurring_ical_events.constants import DATE_MAX


def test_event_is_not_included_if_it_is_later(calendars):
    events = calendars.three_events.between((2000, 1, 1), (2001, 1, 1))
    assert not events


def test_event_is_not_included_if_it_is_earlier(calendars):
    events = calendars.three_events.between((2030, 1, 1), DATE_MAX)
    assert not events


def test_all_events_in_time_span(calendars):
    events = calendars.three_events.between((2000, 1, 1), DATE_MAX)
    assert len(events) == 3


@pytest.mark.parametrize(
    ("count", "end"),
    [
        (0, (2019, 3, 3)),
        (1, (2019, 3, 5)),
        (2, (2019, 3, 8)),
    ],
)
def test_events_occur_after_and_before_span_end(calendars, count, end):
    events = calendars.three_events.between((2000, 1, 1), end)
    assert len(events) == count


@pytest.mark.parametrize(
    ("count", "start"),
    [
        (3, (2019, 3, 3)),
        (2, (2019, 3, 5)),
        (1, (2019, 3, 8)),
    ],
)
def test_events_occur_after_and_before_span_start(calendars, count, start):
    events = calendars.three_events.between(start, DATE_MAX)
    assert len(events) == count
