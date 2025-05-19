"""Type annotations."""

from __future__ import annotations

import datetime
from typing import Tuple, TypeAlias, Union

# Any types documented here should also be mentioned in the docs/conf.py.

Time : TypeAlias = Union[datetime.date, datetime.datetime]
DateArgument : TypeAlias = Union[Tuple[int], datetime.date, str, int]
UID : TypeAlias = str
Timestamp : TypeAlias = float
RecurrenceID : TypeAlias = datetime.datetime
RecurrenceIDs : TypeAlias = Tuple[RecurrenceID]


__all__ = [
    "UID",
    "DateArgument",
    "RecurrenceID",
    "RecurrenceIDs",
    "Time",
    "Timestamp",
]
