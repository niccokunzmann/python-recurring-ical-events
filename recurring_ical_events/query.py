"""Core functionality: querying the calendar for occurrences."""

from __future__ import annotations

import contextlib
import datetime
import itertools
import sys
from typing import TYPE_CHECKING, ClassVar, Generator, Optional, Sequence

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

import icalendar

from recurring_ical_events.adapters.component import ComponentAdapter
from recurring_ical_events.constants import DATE_MAX_DT, DATE_MIN_DT
from recurring_ical_events.errors import (
    BadRuleStringFormat,
    InvalidCalendar,
    PeriodEndBeforeStart,
)
from recurring_ical_events.occurrence import OccurrenceID
from recurring_ical_events.pages import Pages
from recurring_ical_events.selection.base import SelectComponents
from recurring_ical_events.util import compare_greater

if TYPE_CHECKING:
    from icalendar.cal import Component

    from recurring_ical_events.occurrence import Occurrence
    from recurring_ical_events.series import Series
    from recurring_ical_events.types import (
        DateArgument,
        Time,
    )

if sys.version_info >= (3, 10):
    T_COMPONENTS : TypeAlias = Sequence[str | type[ComponentAdapter] | SelectComponents]
else:
    # see https://github.com/python/cpython/issues/86399#issuecomment-1093889925
    T_COMPONENTS : TypeAlias = Sequence[str]


class CalendarQuery:
    """Query a calendar for occurrences.

    Functions like :meth:`at`, :meth:`between` andm :meth:`after`
    can be used to query the selected components.
    If any malformed icalendar information is found,
    an :class:`InvalidCalendar` exception is raised.
    For other bad arguments, you should expect a :class:`ValueError`.

    Attributes:
        suppressed_errors: a list of errors to suppress when
            skip_bad_series is True
    """

    suppressed_errors : ClassVar[type[Exception]] = [
        BadRuleStringFormat,
        PeriodEndBeforeStart,
        icalendar.InvalidCalendar,
    ]
    from recurring_ical_events.selection.name import ComponentsWithName

    def __init__(
        self,
        calendar: Component,
        keep_recurrence_attributes: bool = False,  # noqa: FBT001
        components: T_COMPONENTS = ("VEVENT",),
        skip_bad_series: bool = False,  # noqa: FBT001
    ):
        """Create an unfoldable calendar from a given calendar.

        Arguments:
            calendar: an :class:`icalendar.cal.Calendar` component like
                :class:`icalendar.cal.Calendar`.
            keep_recurrence_attributes: Whether to keep attributes that are only used
                to calculate the recurrence (``RDATE``, ``EXDATE``, ``RRULE``).
            components: A list of component type names of which the recurrences
                should be returned. This can also be instances of
                :class:`SelectComponents`.
                Examples: ``("VEVENT", "VTODO", "VJOURNAL", "VALARM")``
            skip_bad_series: Whether to skip series of components that contain
                errors. You can use :attr:`CalendarQuery.suppressed_errors` to
                specify which errors to skip.
        """
        self.keep_recurrence_attributes = keep_recurrence_attributes
        if calendar.get("CALSCALE", "GREGORIAN") != "GREGORIAN":
            # https://www.kanzaki.com/docs/ical/calscale.html
            raise InvalidCalendar("Only Gregorian calendars are supported.")

        self.series: list[Series] = []  # component
        self._skip_errors = tuple(self.suppressed_errors) if skip_bad_series else ()
        for component_adapter_id in components:
            if isinstance(component_adapter_id, str):
                component_adapter = self.ComponentsWithName(component_adapter_id)
            else:
                component_adapter = component_adapter_id
            self.series.extend(
                component_adapter.collect_series_from(calendar, self._skip_errors)
            )

    @staticmethod
    def to_datetime(date: DateArgument):
        """Convert date inputs of various sorts into a datetime object.

        Arguments:
            date: A date specification.

        Date Specification:
        
        - a year like ``(2019,)`` or ``2019`` (:class:`int`)
        - a month like ``(2019, 1)`` for January of 2019
        - a day like ``(2019, 1, 19)`` for the first of January 2019
        - a day with hours, ``(2019, 1, 19, 1)``
        - a day with minutes, ``(2019, 1, 19, 13, 30 )``
        - a day with seconds, ``(2019, 1, 19, 13, 30, 59)``
        - a :class:`datetime.datetime` or :class:`datetime.date`
        - a :class:`str` in the format ``yyyymmdd``
        - a :class:`str` in the format ``yyyymmddThhmmssZ``

        """
        if isinstance(date, int):
            date = (date,)
        if isinstance(date, tuple):
            date += (1,) * (3 - len(date))
            return datetime.datetime(*date)  # noqa: DTZ001
        if isinstance(date, str):
            # see https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
            if len(date) == 8:
                return datetime.datetime.strptime(date, "%Y%m%d")  # noqa: DTZ007
            return datetime.datetime.strptime(date, "%Y%m%dT%H%M%SZ")  # noqa: DTZ007
        return date

    def all(self) -> Generator[Component]:
        """Generate all Components.

        The Components are sorted from the first to the last Occurrence.
        Calendars can contain millions of Occurrences. This iterates
        safely across all of them.
        """
        # MAX and MIN values may change in the future
        return self.after(DATE_MIN_DT)

    _DELTAS = [
        datetime.timedelta(days=1),
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=1),
        datetime.timedelta(seconds=1),
    ]

    def at(self, date: DateArgument):
        """Return all events within the next 24 hours of starting at the given day.

        Arguments:
            date: A date specification, see :meth:`to_datetime`.

        This is translated to :meth:`between` in the following way:

        - A year returns all occurrences within that year.
            Example: ``(2019,)``, ``2019``
        - A month returns all occurrences within that month.
            Example: ``(2019, 1)``
        - A day returns all occurrences within that day.
            Examples:

            - ``(2019, 1, 19)``
            - ``datetime.date(2019, 1, 19)``
            - ``"20190101"``

        - An hour returns all occurrences within that hour.
            Example: ``(2019, 1, 19, 1)``
        - A minute returns all occurrences within that minute.
            Example: ``(2019, 1, 19, 13, 30 )``
        - A second returns all occurrences at that exact second.
            Examples:

            - ``(2019, 1, 19, 13, 30, 59)``
            - ``datetime.datetime(2019, 1, 19, 13, 30, 59)``
            - ``datetime.datetime(2019, 1, 19, tzinfo=datetime.timezone.utc)``,
            - ``datetime.datetime(2019, 1, 19, 13, 30, 59, tzinfo=ZoneInfo('Europe/London'))``
            - ``"20190119T133059Z"``
        """  # noqa: E501
        if isinstance(date, int):
            date = (date,)
        if isinstance(date, str):
            if len(date) != 8 or not date.isdigit():
                raise ValueError(f"Format yyyymmdd expected for {date!r}.")
            date = (int(date[:4], 10), int(date[4:6], 10), int(date[6:]))
        if isinstance(date, datetime.datetime):
            return self.between(date, date)
        if isinstance(date, datetime.date):
            return self.between(date, date + datetime.timedelta(days=1))
        if len(date) == 1:
            return self.between((date[0], 1, 1), (date[0] + 1, 1, 1))
        if len(date) == 2:
            year, month = date
            if month == 12:
                return self.between((year, 12, 1), (year + 1, 1, 1))
            return self.between((year, month, 1), (year, month + 1, 1))
        dt = self.to_datetime(date)
        return self._between(dt, dt + self._DELTAS[len(date) - 3])

    def between(self, start: DateArgument, stop: DateArgument | datetime.timedelta):
        """Return events at a time between start (inclusive) and end (inclusive)

        Arguments:
            start: A date specification. See :meth:`to_datetime`.
            stop: A date specification or a :class:`datetime.timedelta`
                relative to start.

        .. warning::

            If you pass a :class:`datetime.datetime` to both ``start`` and
            ``stop``, make sure the :attr:`datetime.datetime.tzinfo` is
            the same.
        """
        start = self.to_datetime(start)
        stop = (
            start + stop
            if isinstance(stop, datetime.timedelta)
            else self.to_datetime(stop)
        )
        return self._between(start, stop)

    def _occurrences_to_components(
        self, occurrences: list[Occurrence]
    ) -> list[Component]:
        """Map occurrences to components."""
        return [
            occurrence.as_component(self.keep_recurrence_attributes)
            for occurrence in occurrences
        ]

    def _between(self, start: Time, end: Time) -> list[Component]:
        """Return the occurrences between the start and the end."""
        return self._occurrences_to_components(self._occurrences_between(start, end))

    def _occurrences_between(self, start: Time, end: Time) -> list[Occurrence]:
        """Return the components between the start and the end."""
        occurrences: list[Occurrence] = []
        for series in self.series:
            with contextlib.suppress(self._skip_errors):
                occurrences.extend(series.between(start, end))
        return occurrences

    def after(self, earliest_end: DateArgument) -> Generator[Component]:
        """Iterate over components happening during or after earliest_end.

        Arguments:
            earliest_end: A date specification. See :meth:`to_datetime`.
                Anything happening during or after earliest_end is returned
                in the order of start time.
        """
        earliest_end = self.to_datetime(earliest_end)
        for occurrence in self._after(earliest_end):
            yield occurrence.as_component(self.keep_recurrence_attributes)

    def _after(self, earliest_end: Time) -> Generator[Occurrence]:
        """Iterate over occurrences happening during or after earliest_end."""
        time_span = datetime.timedelta(days=1)
        min_time_span = datetime.timedelta(minutes=15)
        done = False
        result_ids: set[OccurrenceID] = set()

        while not done:
            try:
                next_end = earliest_end + time_span
            except OverflowError:
                # We ran to the end
                next_end = DATE_MAX_DT
                if compare_greater(earliest_end, next_end):
                    return  # we might run too far
                done = True
            occurrences = self._occurrences_between(earliest_end, next_end)
            occurrences.sort()
            for occurrence in occurrences:
                if occurrence.id not in result_ids:
                    yield occurrence
                    result_ids.add(occurrence.id)
            # prepare next query
            time_span = max(
                time_span / 2 if occurrences else time_span * 2,
                min_time_span,
            )  # binary search to improve speed
            earliest_end = next_end

    def count(self) -> int:
        """Return the amount of recurring components in this calendar.

        .. warning::

            Do not use this in production as it generates all occurrences.
        """
        i = 0
        for _ in self.all():
            i += 1
        return i

    @property
    def first(self) -> Component:
        """Return the first recurring component in this calendar.

        Returns:
            The first recurring component in this calendar.

        Raises:
            IndexError: if the calendar is empty
        """
        for component in self.all():
            return component
        raise IndexError("No components found.")

    def paginate(
        self,
        page_size: int,
        earliest_end: Optional[DateArgument] = None,
        latest_start: Optional[DateArgument] = None,
        next_page_id: str = "",
    ) -> Pages:
        """Return pages for pagination.

        Args:
            page_size: the number of components per page
            earliest_end: the start of the first page
                All components occur after this date.
                See :meth:`to_datetime` for possible values.
            latest_start: the end of the last page
                All components occur before this date.
                See :meth:`to_datetime` for possible values.
            next_page_id: The id of the next page.
                This is optional for the first page.
                These are safe to pass outside of the application and back in.
        """
        latest_start = None if latest_start is None else self.to_datetime(latest_start)
        earliest_end = (
            DATE_MIN_DT if earliest_end is None else self.to_datetime(earliest_end)
        )
        if next_page_id:
            first_occurrence_id = OccurrenceID.from_string(next_page_id)
            if not compare_greater(earliest_end, first_occurrence_id.start):
                iterator = self._after(first_occurrence_id.start)
                lost_occurrences = []  # in case we do not find the event
                for occurrence in iterator:
                    lost_occurrences.append(occurrence)
                    oid = occurrence.id
                    if oid == first_occurrence_id:
                        iterator = itertools.chain([occurrence], iterator)
                        break
                    if compare_greater(oid.start, first_occurrence_id.start):
                        iterator = itertools.chain(lost_occurrences, iterator)
                        break
            else:
                iterator = self._after(earliest_end)
        else:
            iterator = self._after(earliest_end)
        return Pages(
            occurrence_iterator=iterator,
            size=page_size,
            stop=latest_start,
            keep_recurrence_attributes=self.keep_recurrence_attributes,
        )


__all__ = ["T_COMPONENTS", "CalendarQuery"]
