"""
This tests that subcomponents are carried over to different events.
"""


def test_subcomponents_are_compied(calendars):
    event = next(calendars.subcomponents.all())
    assert event.subcomponents


def test_there_are_no_subcomponents(calendars):
    event = next(calendars.Germany.all())
    assert not event.subcomponents
