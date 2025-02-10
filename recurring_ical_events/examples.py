"""Functionality for smaller examples."""

import icalendar

from recurring_ical_events.constants import CALENDARS


def example_calendar(name: str = "") -> icalendar.Calendar:
    """Return an example calendar.

    Args:
        name (str): The name of the example file.

    Returns:
        icalendar.Calendar: The parsed calendar example.
    """
    if not name.endswith(".ics"):
        name += ".ics"
    path = CALENDARS / name
    try:
        return icalendar.Calendar.from_ical(path.read_bytes())
    except FileNotFoundError:
        raise ValueError(  # noqa: B904
            f"File {name!r} not found. "
            f"Use one of {', '.join(p.name for p in CALENDARS.glob('*.ics'))!r}."
        )


__all__ = ["example_calendar"]
