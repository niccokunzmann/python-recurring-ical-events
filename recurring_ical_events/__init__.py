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

from recurring_ical_events.query import T_COMPONENTS, CalendarQuery
from recurring_ical_events.selection.base import SelectComponents

if TYPE_CHECKING:
    from icalendar.cal import Component


def of(
    a_calendar: Component,
    keep_recurrence_attributes=False,
    components: T_COMPONENTS = ("VEVENT",),
    skip_bad_series: bool = False,  # noqa: FBT001
    calendar_query: type[CalendarQuery] = CalendarQuery,
) -> CalendarQuery:
    """Unfold recurring events of a_calendar

    - a_calendar is an icalendar VCALENDAR component or something like that.
    - keep_recurrence_attributes - whether to keep attributes that are only used
      to calculate the recurrence.
    - components is a list of component type names of which the recurrences
      should be returned. This can also be instances of SelectComponents.
    - skip_bad_series - whether to skip a series of components that contains
      errors.
    - calendar_query - The calendar query class to use.
    """
    a_calendar = x_wr_timezone.to_standard(a_calendar)
    return calendar_query(
        a_calendar, keep_recurrence_attributes, components, skip_bad_series
    )


__all__ = [
    "of",
    "Alarms",
    "PeriodEndBeforeStart",
    "BadRuleStringFormat",
    "DATE_MIN",
    "DATE_MAX",
    "EventAdapter",
    "TodoAdapter",
    "JournalAdapter",
    "RecurrenceID",
    "RecurrenceIDs",
    "SelectComponents",
    "ComponentsWithName",
    "T_COMPONENTS",
]
