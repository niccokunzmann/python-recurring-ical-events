"""All adapters for different kinds of components."""

from .alarm import AbsoluteAlarmAdapter
from .component import ComponentAdapter
from .event import EventAdapter
from .journal import JournalAdapter
from .todo import TodoAdapter

__all__ = [
    "AbsoluteAlarmAdapter",
    "ComponentAdapter",
    "EventAdapter",
    "JournalAdapter",
    "TodoAdapter",
]
