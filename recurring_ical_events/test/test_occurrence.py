"""The all() function can be exposed now that we have the after() function.

all() becomes a Generator.
We do not wish to retain a high memory footprint on the occurrences.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, NamedTuple

import pytest

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from recurring_ical_events.occurrence import Occurrence, OccurrenceID

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


def occurrence_id(adapter: Adapter):
    """Check the id of the occurrence."""
    return Occurrence(adapter).id


def occurrence_id_string(adapter: Adapter):
    """Check the string of the occurrence id."""
    return Occurrence(adapter).id.to_string()


def occurrence_id_string_parsed(adapter: Adapter):
    """Check the string of the occurrence id."""
    return OccurrenceID.from_string(Occurrence(adapter).id.to_string())


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
        ## I cannot think of a possible example where the recurrence id is the same but the
        ## start differs - especially after the occurrences are calculated.
        # (
        #     Adapter("asd", "asd", (date(2020, 10, 2),), date(2020, 10, 1)),
        #     Adapter("asd", "asd", (date(2020, 10, 2),), date(2020, 10, 2)),
        #     True,
        #     "different start but recurrence id is the same",
        # ),
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
        (
            Adapter("VEVENT", "uid", (), datetime(2020, 10, 2, 10)),
            Adapter("VEVENT", "uid", (), datetime(2020, 10, 2, 10)),
            True,
            "datetime",
        ),
        (
            Adapter(
                "VEVENT", "uid", (), datetime(2020, 10, 2, 10, tzinfo=ZoneInfo("UTC"))
            ),
            Adapter(
                "VEVENT", "uid", (), datetime(2020, 10, 2, 10, tzinfo=ZoneInfo("UTC"))
            ),
            True,
            "UTC date",
        ),
        (
            Adapter(
                "VEVENT",
                "uid",
                (),
                datetime(2020, 10, 2, 10, tzinfo=ZoneInfo("Europe/Berlin")),
            ),
            Adapter(
                "VEVENT",
                "uid",
                (),
                datetime(2020, 10, 2, 10, tzinfo=ZoneInfo("Europe/Berlin")),
            ),
            True,
            "Europe/Berlin date",
        ),
        (
            Adapter(
                "VEVENT", "uid", (), datetime(2020, 10, 2, 10, tzinfo=ZoneInfo("UTC"))
            ),
            Adapter("VEVENT", "uid", (), datetime(2020, 10, 2, 10)),
            False,
            "timezone differs - UTC",
        ),
        (
            Adapter(
                "VEVENT",
                "uid",
                (),
                datetime(2020, 10, 2, 10, tzinfo=ZoneInfo("Europe/Berlin")),
            ),
            Adapter("VEVENT", "uid", (), datetime(2020, 10, 2, 10)),
            False,
            "timezone differs - Europe/Berlin",
        ),
        (
            Adapter(
                "VEVENT",
                "uid",
                (),
                datetime(2020, 10, 2, 10, tzinfo=ZoneInfo("Europe/Berlin")),
            ),
            Adapter(
                "VEVENT", "uid", (), datetime(2020, 10, 2, 10, tzinfo=ZoneInfo("UTC"))
            ),
            False,
            "timezone differs - Europe/Berlin + UTC",
        ),
    ],
)
@pytest.mark.parametrize(
    "create_occurrence",
    [Occurrence, occurrence_id, occurrence_id_string, occurrence_id_string_parsed],
)
def test_equality(adapter1, adapter2, equality, message, create_occurrence):
    """Check the equality of Occurrences."""
    occurrence1 = create_occurrence(adapter1)
    occurrence2 = create_occurrence(adapter2)
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


ALL_CHARS = "".join(map(chr, range(256)))


@pytest.mark.parametrize(
    ("original_component_id", "message"),
    [
        (
            OccurrenceID("VEVENT", "awdd", date(1970, 2, 12), date(1971, 2, 12)),
            "date and all values given",
        ),
        (
            OccurrenceID(
                "VTODO", "+-2123_", datetime(1970, 2, 12), datetime(1971, 2, 12)
            ),
            "datetime and all values given",
        ),
        (
            OccurrenceID("VTODO", "+-2123_", None, datetime(1971, 2, 12, 10, 21)),
            "datetime no recurrence id",
        ),
        (
            OccurrenceID("asd", "+-2123_", None, date(1971, 2, 12)),
            "date no recurrence id",
        ),
        (
            OccurrenceID("VALARM", ALL_CHARS, None, date(1971, 2, 12)),
            "no recurrence id and a wild UID",
        ),
        (
            OccurrenceID(
                "asd",
                ALL_CHARS,
                datetime(2025, 2, 11, 14, 14),
                datetime(1971, 2, 12, 10, 23),
            ),
            "recurrence id and a wild UID",
        ),
        (
            OccurrenceID(
                "VEVENT",
                "",
                None,
                datetime(1971, 2, 12, 10, 23, tzinfo=ZoneInfo("UTC")),
            ),
            "start in UTC",
        ),
        (
            OccurrenceID(
                "VEVENT",
                "",
                None,
                datetime(1971, 2, 12, 10, 23, tzinfo=ZoneInfo("Europe/Berlin")),
            ),
            "start in Europe/Berlin",
        ),
    ],
)
def test_equality_after_parsed(original_component_id: OccurrenceID, message: str):
    """Check the equality after parsing."""
    parsed_component_id = OccurrenceID.from_string(original_component_id.to_string())
    assert original_component_id == parsed_component_id, (
        "The parsed component id should be equal to its source. " + message
    )
    assert original_component_id.to_string() == parsed_component_id.to_string(), (
        "The string representation cannot change. " + message
    )
