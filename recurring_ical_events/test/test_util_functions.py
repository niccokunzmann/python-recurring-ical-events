"""Check some utility functions."""

from typing import NamedTuple

import pytest

from recurring_ical_events.util import with_highest_sequence


class Component(NamedTuple):
    sequence: int


@pytest.mark.parametrize(
    ("a1", "a2", "result"),
    [
        (None, None, None),
        (Component(1), Component(2), Component(2)),
        (Component(5), Component(2), Component(5)),
        (Component(1), None, Component(1)),
        (None, Component(4), Component(4)),
        (None, Component(-3), Component(-3)),
        (Component(-1), None, Component(-1)),
    ],
)
def test_highest_sequence(a1, a2, result):
    """Check the result"""
    assert with_highest_sequence(a1, a2) == result
