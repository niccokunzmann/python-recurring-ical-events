"""
This tests that subcomponents are carried over to different events.
"""

def test_subcomponents_are_compied(calendars):
    event = calendars.subcomponents.all()[0]
    assert event.subcomponents

def test_there_are_no_subcomponents(calendars):
    event = calendars.Germany.all()[0]
    assert not event.subcomponents

