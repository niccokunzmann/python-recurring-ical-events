import pytest
from recurring_ical_events import DATE_MAX


def test_recurring_task_is_not_included1(calendars):
    tasks = calendars.simple_todo.between((1989, 1, 1), (1991,1,1))
    assert not tasks

def test_recurring_task_is_not_included2(calendars):
    tasks = calendars.simple_todo.between((1998, 1, 1), (1998,4,14))
    assert not tasks

def test_recurring_task_is_repeated(calendars):
    events = calendars.simple_todo.between((1995, 1, 1), (2022,1,1))
    assert len(events) == 7

## Hmm ... I hate copying code, there is most likely some smart way to reuse
## the code above, but whatever ...
def test_recurring_journal_is_not_included1(calendars):
    tasks = calendars.simple_journal.between((1989, 1, 1), (1991,1,1))
    assert not tasks

def test_recurring_journal_is_not_included2(calendars):
    tasks = calendars.simple_journal.between((1998, 1, 1), (1998,4,14))
    assert not tasks

def test_recurring_journal_is_repeated(calendars):
    events = calendars.simple_journal.between((1995, 1, 1), (2022,1,1))
    assert len(events) == 7


