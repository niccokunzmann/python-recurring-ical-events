"""Check that we can still compute if start and end are swapped."""

from datetime import datetime

import pytest


def test_event_case(calendars):
    """Test an event with swapped start and end."""
    event = calendars.issue_132_swapped_start_and_end.first
    assert event.start.replace(tzinfo=None) == datetime(2023, 12, 18, 23, 30)
    assert event.end.replace(tzinfo=None) == datetime(2023, 12, 18, 23, 45)


def test_todo_case(calendars):
    """Test an event with swapped start and end."""
    calendars.components = ["VTODO"]
    todo = calendars.issue_132_swapped_start_and_end.first
    print(todo)
    assert todo.start.replace(tzinfo=None) == datetime(2023, 12, 18, 23, 30)
    assert todo.end.replace(tzinfo=None) == datetime(2023, 12, 18, 23, 45)


@pytest.mark.parametrize("skip_invalid", [True, False])
def test_old_example_works_now(calendars, ZoneInfo, skip_invalid):
    """The old tests works now."""
    calendars.skip_bad_series = skip_invalid
    events = calendars.end_before_start_event.at(2019)
    print(list(calendars.end_before_start_event.all()))
    assert len(events) == 1
    event = events[0]
    assert event.start == datetime(
        2019, 3, 4, 8, tzinfo=ZoneInfo("Europe/Berlin")
    )  # 20190304T080000
    assert event.end == datetime(
        2019, 3, 4, 8, 30, tzinfo=ZoneInfo("Europe/Berlin")
    )  # 20190304T080300
