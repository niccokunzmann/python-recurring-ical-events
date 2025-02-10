"""The all() function can be exposed now that we have the after() function.

all() becomes a Generator.
We do not wish to retain a high memory footprint on the occurrences.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, NamedTuple

import pytest

from recurring_ical_events.occurrence import Occurrence

if TYPE_CHECKING:
    from recurring_ical_events.types import RecurrenceIDs, Time


class Adapter(NamedTuple):
    uid: str
    name: str
    recurrence_ids: RecurrenceIDs
    start: Time
    end: Time = date(2020, 10, 10)

    def component_name(self):
        return self.name


@pytest.mark.parametrize(
    ("adapter1", "adapter2", "equality", "message"),
    [
        (
            Adapter("asd", "asd", (date(2020, 10, 2),), date(2020, 10, 2)),
            Adapter("asd", "asd", (date(2020, 10, 2),), date(2020, 10, 2)),
            True,
            "same copy",
        ),
        (
            Adapter("asd1", "asd", (date(2020, 10, 2),), date(2020, 10, 2)),
            Adapter("asd", "asd", (date(2020, 10, 2),), date(2020, 10, 2)),
            False,
            "different name",
        ),
        (
            Adapter("asd", "asd", (date(2020, 10, 2),), date(2020, 10, 2)),
            Adapter("asd", "asd1", (date(2020, 10, 2),), date(2020, 10, 2)),
            False,
            "different uid",
        ),
        (
            Adapter("asd", "asd", (date(2020, 10, 1),), date(2020, 10, 2)),
            Adapter("asd", "asd", (date(2020, 10, 2),), date(2020, 10, 2)),
            False,
            "different recurrence id",
        ),
        (
            Adapter("asd", "asd", (date(2020, 10, 2),), date(2020, 10, 1)),
            Adapter("asd", "asd", (date(2020, 10, 2),), date(2020, 10, 2)),
            True,
            "different start but recurrence id is the same",
        ),
        (
            Adapter("asd", "asd", (), date(2020, 10, 2)),
            Adapter("asd", "asd", (), date(2020, 10, 2)),
            True,
            "no recurrence id but copy",
        ),
        (
            Adapter("asd", "asd", (), date(2020, 10, 2)),
            Adapter("asd", "asd", (), date(2020, 10, 1)),
            False,
            "no recurrence id but start differs",
        ),
    ],
)
def test_equality(adapter1, adapter2, equality, message):
    """Check the equality of Occurrences."""
    occurrence1 = Occurrence(adapter1)
    occurrence2 = Occurrence(adapter2)
    assert (occurrence1 == occurrence2) == equality, "1 == 2 - " + message
    assert (occurrence1 != occurrence2) != equality, "1 != 2 - " + message
    assert (occurrence2 == occurrence1) == equality, "2 == 1 - " + message
    assert (occurrence2 != occurrence1) != equality, "2 != 1 - " + message
    assert (hash(occurrence1) == hash(occurrence2)) == equality, (
        "hash1 == hash2 - " + message
    )
    assert (hash(occurrence1) != hash(occurrence2)) != equality, (
        "hash1 != hash2 - " + message
    )
