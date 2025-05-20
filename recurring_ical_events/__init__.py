# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Calculate repetitions of icalendar components."""

from __future__ import annotations

from typing import TYPE_CHECKING

import x_wr_timezone

from recurring_ical_events.adapters import (
    AbsoluteAlarmAdapter,
    ComponentAdapter,
    EventAdapter,
    JournalAdapter,
    TodoAdapter,
)
from recurring_ical_events.constants import DATE_MAX, DATE_MAX_DT, DATE_MIN, DATE_MIN_DT
from recurring_ical_events.errors import (
    BadRuleStringFormat,
    InvalidCalendar,
    PeriodEndBeforeStart,
)
from recurring_ical_events.examples import example_calendar
from recurring_ical_events.query import T_COMPONENTS, CalendarQuery
from recurring_ical_events.selection import (
    Alarms,
    AllKnownComponents,
    ComponentsWithName,
    SelectComponents,
)

from .occurrence import AlarmOccurrence, Occurrence, OccurrenceID
from .series import (
    AbsoluteAlarmSeries,
    AlarmSeriesRelativeToEnd,
    AlarmSeriesRelativeToStart,
    Series,
)

if TYPE_CHECKING:
    from icalendar.cal import Component


def of(
    a_calendar: Component,
    keep_recurrence_attributes=False,
    components: T_COMPONENTS = ("VEVENT",),
    skip_bad_series: bool = False,  # noqa: FBT001
    calendar_query: type[CalendarQuery] = CalendarQuery,
) -> CalendarQuery:
    """Create a query for recurring components in a_calendar.

    If the argument is a calendar, this will also correct
    times according to ``X-WR-TIMEZONE``.

    Arguments:
        a_calendar: an :class:`icalendar.cal.Calendar` component like
            :class:`icalendar.cal.Calendar`.
        keep_recurrence_attributes: Whether to keep attributes that are only used
            to calculate the recurrence (``RDATE``, ``EXDATE``, ``RRULE``).
        components: A list of component type names of which the recurrences
            should be returned. This can also be instances of :class:`SelectComponents`.
            Examples: ``("VEVENT", "VTODO", "VJOURNAL", "VALARM")``
        skip_bad_series: Whether to skip series of components that contain
            errors. You can use :attr:`CalendarQuery.suppressed_errors` to
            specify which errors to skip.
        calendar_query: The :class:`CalendarQuery` class to use.
    """
    a_calendar = x_wr_timezone.to_standard(a_calendar)
    return calendar_query(
        a_calendar, keep_recurrence_attributes, components, skip_bad_series
    )


__all__ = [
    "DATE_MAX",
    "DATE_MAX_DT",
    "DATE_MIN",
    "DATE_MIN_DT",
    "AbsoluteAlarmAdapter",
    "AbsoluteAlarmSeries",
    "AlarmOccurrence",
    "AlarmSeriesRelativeToEnd",
    "AlarmSeriesRelativeToStart",
    "Alarms",
    "AllKnownComponents",
    "BadRuleStringFormat",
    "CalendarQuery",
    "ComponentAdapter",
    "ComponentsWithName",
    "EventAdapter",
    "InvalidCalendar",
    "JournalAdapter",
    "Occurrence",
    "OccurrenceID",
    "PeriodEndBeforeStart",
    "SelectComponents",
    "Series",
    "TodoAdapter",
    "example_calendar",
    "of",
]
