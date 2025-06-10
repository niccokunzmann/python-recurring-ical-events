"""Check that we can still compute if start and end are swapped."""

from datetime import datetime


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


def test_old_example_works_now(calendars):
    """The old tests works now."""
    events = calendars.end_before_start_event.at(2019)
    assert len(events) == 1
