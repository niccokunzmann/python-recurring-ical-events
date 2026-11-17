"""Type annotations."""

from __future__ import annotations

import datetime
from typing import Tuple, Union

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

# Any types documented here should also be mentioned in the docs/conf.py.

Time: TypeAlias = Union[datetime.date, datetime.datetime]
DateArgument: TypeAlias = Union[Tuple[int], datetime.date, str, int]
UID: TypeAlias = str
Timestamp: TypeAlias = float
RecurrenceID: TypeAlias = datetime.datetime
RecurrenceIDs: TypeAlias = Tuple[RecurrenceID]
RecurrenceIDKey: TypeAlias = Tuple[str, RecurrenceID]


__all__ = [
    "UID",
    "DateArgument",
    "RecurrenceID",
    "RecurrenceIDKey",
    "RecurrenceIDs",
    "Time",
    "Timestamp",
]
