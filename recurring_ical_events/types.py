"""Type annotations."""

from __future__ import annotations

import datetime
from typing import Tuple, Union

Time = Union[datetime.date, datetime.datetime]
DateArgument = Union[Tuple[int], datetime.date, str, int]
UID = str
ComponentID = Tuple[str, UID, Time]
Timestamp = float
RecurrenceID = datetime.datetime
RecurrenceIDs = Tuple[RecurrenceID]

__all__ = [
    "Time",
    "DateArgument",
    "UID",
    "ComponentID",
    "Timestamp",
    "RecurrenceID",
    "RecurrenceIDs",
]
