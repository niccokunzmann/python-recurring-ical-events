import pytest

calendars_parametrized = pytest.mark.parametrize(
    "ical_file",
    [
        "issue_97_simple_todo",
        "issue_97_simple_journal",
        "issue_97_todo_nodtstart",
    ],
)


@calendars_parametrized
def test_recurring_task_is_not_included1(calendars, ical_file):
    """The three files given starts in late 1991, no recurrences
    should be found before 1991.  Refers to
    https://github.com/niccokunzmann/python-recurring-ical-events/issues/97.
    Test passes prior to fixing #97, should still pass after #97 is
    fixed.
    """
    calendars.components = ["VJOURNAL", "VTODO", "VEVENT"]
    tasks = calendars[ical_file].between((1989, 1, 1), (1991, 1, 1))
    assert not tasks


@calendars_parametrized
def test_recurring_task_is_not_included2(calendars, ical_file):
    """Every recurrence of the three ical files is in October, hence
    no recurrences should be found.  Refers to
    https://github.com/niccokunzmann/python-recurring-ical-events/issues/97.
    Test passes prior to fixing #97, should still pass after #97 is
    fixed.
    """
    calendars.components = ["VJOURNAL", "VTODO", "VEVENT"]
    tasks = calendars[ical_file].between((1998, 1, 1), (1998, 4, 14))
    assert not tasks


@calendars_parametrized
def test_recurring_task_is_repeated(calendars, ical_file):
    """Expansion of a yearly task over seven years.
    The issue
    https://github.com/niccokunzmann/python-recurring-ical-events/issues/97
    needs to be fixed before this test can pass
    """
    calendars.components = ["VJOURNAL", "VTODO", "VEVENT"]
    events = calendars[ical_file].between((1995, 1, 1), (2002, 1, 1))
    assert len(events) == 7
