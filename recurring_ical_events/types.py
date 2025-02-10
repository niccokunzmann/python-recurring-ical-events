"""Type annotations."""
from __future__ import annotations

import datetime
from typing import Union

Time = Union[datetime.date, datetime.datetime]
DateArgument = Union[tuple[int], datetime.date, str, int]
UID = str
ComponentID = tuple[str, UID, Time]
Timestamp = float
RecurrenceID = datetime.datetime
RecurrenceIDs = tuple[RecurrenceID]

__all__ = [
    "Time",
    "DateArgument",
    "UID",
    "ComponentID",
    "Timestamp",
    "RecurrenceID",
    "RecurrenceIDs",
]
