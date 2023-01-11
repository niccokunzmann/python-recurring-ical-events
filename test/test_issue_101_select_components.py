"""These tests make sure that you can select which components should be returned.

By default, it should be events.
If a component is not supported, an error is raised.
"""
import pytest


@pytest.mark.parametrize("components,count,calendar,message", [
    (None, 0, "issue-97-simple-todo", "by default, only events are returned"),
    (None, 0, "issue-97-simple-journal", "by default, only events are returned"),
    ([], 0, "rdate", "no components, no result"),
    ([], 0, "issue-97-simple-todo", "no components, no result"),
    ([], 0, "issue-97-simple-journal", "no components, no result"),
    (["VEVENT"], 0, "issue-97-simple-todo", "no events in the calendar"),
    (["VEVENT"], 0, "issue-97-simple-journal", "no events in the calendar"),

    (["VJOURNAL"], 0, "issue-97-simple-todo", "no journal, just a todo"),
    (["VTODO"], 1, "issue-97-simple-todo", "one todo is found"),

    (["VTODO"], 0, "issue-97-simple-journal", "no todo, just a journal"),
    (["VJOURNAL"], 1, "issue-97-simple-journal", "one journal is found"),

    (["VTODO", "VEVENT"], 0, "issue-97-simple-journal", "no todo, just a journal"),
    (["VJOURNAL", "VEVENT"], 1, "issue-97-simple-journal", "one journal is found"),
    (["VJOURNAL", "VEVENT", "VTODO"], 1, "issue-97-simple-journal", "one journal is found"),
])
def test_components_and_their_count(calendars, components, count, calendar, message):
    calendars.components = components
    repeated_components = calendars[calendar].at(2022)
    print(repeated_components)
    assert len(repeated_components) == count, f"{message}: {components}, {calendar}"


@pytest.mark.parametrize("component", [
    "VALARM", # existing but not supported, yet
    "vevent", # misspelled
    "ALDHKSJHK", # does not exist
])
def test_unsupported_component_raises_error(component, calendars):
    """If a component is not recognized, we want to inform the user."""
    with pytest.raises(ValueError) as error:
        calendars.components = [component]
        calendars.rdate
    assert f"\"{component}\"" in str(error)
