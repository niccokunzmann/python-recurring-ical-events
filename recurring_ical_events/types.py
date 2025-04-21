"""Type annotations."""

from __future__ import annotations

import datetime
from typing import Tuple, Union

Time = Union[datetime.date, datetime.datetime]
DateArgument = Union[Tuple[int], datetime.date, str, int]
UID = str
Timestamp = float
RecurrenceID = datetime.datetime
RecurrenceIDs = Tuple[RecurrenceID]


__all__ = [
    "UID",
    "DateArgument",
    "RecurrenceID",
    "RecurrenceIDs",
    "Time",
    "Timestamp",
]
