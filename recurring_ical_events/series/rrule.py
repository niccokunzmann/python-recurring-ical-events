"""Calculation of series based on rrule."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Generator, Sequence

from dateutil.rrule import rrule, rruleset, rrulestr
from icalendar.prop import vDDDTypes

from recurring_ical_events.constants import NEGATIVE_RRULE_COUNT_REGEX
from recurring_ical_events.errors import BadRuleStringFormat
from recurring_ical_events.occurrence import Occurrence
from recurring_ical_events.util import (
    compare_greater,
    convert_to_date,
    convert_to_datetime,
    get_any,
    is_date,
    is_pytz,
    is_pytz_dt,
    normalize_pytz,
    to_recurrence_ids,
    with_highest_sequence,
)

if TYPE_CHECKING:
    from recurring_ical_events.adapters.component import ComponentAdapter
    from recurring_ical_events.types import RecurrenceID, Time


class Series:
    """Base class for components that result in a series of occurrences."""

    def occurrence(
        self,
        adapter: ComponentAdapter,
        start: Time | None = None,
        end: Time | None | datetime.timedelta = None,
    ) -> Occurrence:
        """A way to override the occurrence class."""
        return Occurrence(adapter, start, end, sequence=self.sequence)

    class NoRecurrence:
        """A strategy to deal with not having a core with rrules."""

        check_exdates_datetime: set[RecurrenceID] = set()
        check_exdates_date: set[datetime.date] = set()
        replace_ends: dict[RecurrenceID, Time] = {}
        sequence = -1

        def as_occurrence(
            self,
            start: Time,
            stop: Time,
            occurrence: type[Occurrence],
            core: ComponentAdapter,
        ) -> Occurrence:
            raise NotImplementedError("This code should never be reached.")

        @property
        def core(self) -> ComponentAdapter:
            raise NotImplementedError("This code should never be reached.")

        def rrule_between(
            self,
            span_start: Time,  # noqa: ARG002
            span_stop: Time,  # noqa: ARG002
        ) -> Generator[Time, None, None]:
            """No repetition."""
            yield from []

        has_core = False
        extend_query_span_by = (datetime.timedelta(0), datetime.timedelta(0))
        components = []

    class RecurrenceRules:
        """A strategy if we have an actual core with recurrences."""

        has_core = True

        @property
        def sequence(self) -> int:
            """The sequence of the code component."""
            return self.core.sequence

        def __init__(self, core: ComponentAdapter):
            self.core = core
            # Setup complete. We create the attribtues
            self.start = self.original_start = self.core.start
            self.end = self.original_end = self.core.end
            self.exdates: set[Time] = set()
            self.check_exdates_datetime: set[RecurrenceID] = set()  # should be in UTC
            self.check_exdates_date: set[datetime.date] = set()  # should be in UTC
            self.rdates: set[Time] = set()
            self.replace_ends: dict[
                RecurrenceID, datetime.timedelta
            ] = {}  # for periods, in UTC
            # fill the attributes
            for exdate in self.core.exdates:
                self.exdates.add(exdate)
                self.check_exdates_datetime.update(to_recurrence_ids(exdate))
                if is_date(exdate):
                    self.check_exdates_date.add(exdate)
            for rdate in self.core.rdates:
                if isinstance(rdate, tuple):
                    # we have a period as rdate
                    self.rdates.add(rdate[0])
                    for recurrence_id in to_recurrence_ids(rdate[0]):
                        self.replace_ends[recurrence_id] = (
                            rdate[1]
                            if isinstance(rdate[1], datetime.timedelta)
                            else rdate[1] - rdate[0]
                        )
                else:
                    # we have a date/datetime
                    self.rdates.add(rdate)

            # We make sure that all dates and times mentioned here are either:
            # - a date
            # - a datetime with None is tzinfo
            # - a datetime with a timezone
            self.make_all_dates_comparable()

            # Calculate the rules with the same timezones
            rule_set = rruleset(cache=True)
            rule_set.until = None
            self.rrules = [rule_set]
            last_until: Time | None = None
            for rrule_string in self.core.rrules:
                rule = self.create_rule_with_start(rrule_string)
                self.rrules.append(rule)
                if rule.until and (
                    not last_until or compare_greater(rule.until, last_until)
                ):
                    last_until = rule.until

            for exdate in self.exdates:
                self.check_exdates_datetime.add(exdate)
            for rdate in self.rdates:
                rule_set.rdate(rdate)

            if not last_until or not compare_greater(self.start, last_until):
                rule_set.rdate(self.start)

        @property
        def extend_query_span_by(self) -> tuple[datetime.timedelta, datetime.timedelta]:
            """The extension of the time span we need for this component's core."""
            return self.core.extend_query_span_by

        def create_rule_with_start(self, rule_string: str) -> rrule:
            """Helper to create an rrule from a rule_string

            The rrule is starting at the start of the component.
            Since the creation is a bit more complex,
            this function handles special cases.
            """
            try:
                return self.rrulestr(rule_string)
            except ValueError:
                # string: FREQ=WEEKLY;UNTIL=20191023;BYDAY=TH;WKST=SU
                # start: 2019-08-01 14:00:00+01:00
                # ValueError: RRULE UNTIL values must be specified in UTC
                # when DTSTART is timezone-aware
                rule_list = rule_string.split(";UNTIL=")
                if len(rule_list) != 2:
                    raise BadRuleStringFormat(
                        "UNTIL parameter is missing", rule_string
                    ) from None
                date_end_index = rule_list[1].find(";")
                if date_end_index == -1:
                    date_end_index = len(rule_list[1])
                until_string = rule_list[1][:date_end_index]
                if self.is_all_dates:
                    until_string = until_string[:8]
                elif self.tzinfo is None:
                    # remove the Z from the time zone
                    until_string = until_string[:-1]
                else:
                    # we assume the start is timezone aware but the until value
                    # is not, see the comment above
                    if len(until_string) == 8:
                        until_string += "T000000"
                    if len(until_string) != 15:
                        raise BadRuleStringFormat(
                            "UNTIL parameter has a bad format", rule_string
                        ) from None
                    until_string += "Z"  # https://stackoverflow.com/a/49991809
                new_rule_string = (
                    rule_list[0]
                    + rule_list[1][date_end_index:]
                    + ";UNTIL="
                    + until_string
                )
                return self.rrulestr(new_rule_string)

        def rrulestr(self, rule_string) -> rrule:
            """Return an rrulestr with a start. This might fail."""
            rule_string = NEGATIVE_RRULE_COUNT_REGEX.sub("", rule_string)  # Issue 128
            rule = rrulestr(rule_string, dtstart=self.start, cache=True)
            rule.string = rule_string
            rule.until = until = self._get_rrule_until(rule)
            if is_pytz(self.start.tzinfo) and rule.until:
                # when starting in a time zone that is one hour off to the end,
                # we might miss the last occurrence
                # see issue 107 and test/test_issue_107_omitting_last_event.py
                rule = rule.replace(until=rule.until + datetime.timedelta(hours=1))
                rule.until = until
            return rule

        def _get_rrule_until(self, rrule) -> None | Time:
            """Return the UNTIL datetime of the rrule or None if absent."""
            rule_list = rrule.string.split(";UNTIL=")
            if len(rule_list) == 1:
                return None
            if len(rule_list) != 2:
                raise BadRuleStringFormat("There should be only one UNTIL", rrule)
            date_end_index = rule_list[1].find(";")
            if date_end_index == -1:
                date_end_index = len(rule_list[1])
            until_string = rule_list[1][:date_end_index]
            return vDDDTypes.from_ical(until_string)

        def make_all_dates_comparable(self):
            """Make sure we can use all dates with eachother.

            Dates may be mixed and we have many of them.
            - date
            - datetime without timezone
            - datetime with timezone
            These three are not comparable but can be converted.
            """
            self.tzinfo = None
            dates = [self.start, self.end, *self.exdates, *self.rdates]
            self.is_all_dates = not any(
                isinstance(date, datetime.datetime) for date in dates
            )
            for date in dates:
                if isinstance(date, datetime.datetime) and date.tzinfo is not None:
                    self.tzinfo = date.tzinfo
                    break
            self.start = convert_to_datetime(self.start, self.tzinfo)

            self.end = convert_to_datetime(self.end, self.tzinfo)
            self.rdates = {
                convert_to_datetime(rdate, self.tzinfo) for rdate in self.rdates
            }
            self.exdates = {
                convert_to_datetime(exdate, self.tzinfo) for exdate in self.exdates
            }

        def rrule_between(self, span_start: Time, span_stop: Time) -> Generator[Time]:
            """Recalculate the rrules so that minor mistakes are corrected."""
            # make dates comparable, rrule converts them to datetimes
            span_start_dt = convert_to_datetime(span_start, self.tzinfo)
            span_stop_dt = convert_to_datetime(span_stop, self.tzinfo)
            # we have to account for pytz timezones not being properly calculated
            # at the timezone changes. This is a heuristic:
            #   most changes are only 1 hour.
            # This will still create problems at the fringes of
            #   timezone definition changes.
            if is_pytz(self.tzinfo):
                span_start_dt = normalize_pytz(
                    span_start_dt - datetime.timedelta(hours=1)
                )
                span_stop_dt = normalize_pytz(
                    span_stop_dt + datetime.timedelta(hours=1)
                )
            for rule in self.rrules:
                for start in rule.between(span_start_dt, span_stop_dt, inc=True):
                    if is_pytz_dt(start):
                        # update the time zone in case of summer/winter time change
                        start = start.tzinfo.localize(start.replace(tzinfo=None))  # noqa: PLW2901
                    # We could now well be out of bounce of the end of the UNTIL
                    # value. This is tested by test/test_issue_20_exdate_ignored.py.
                    if rule.until is None or not compare_greater(start, rule.until):
                        yield start

        def convert_to_original_type(self, date):
            """Convert a date back if this is possible.

            Dates may get converted to datetimes to make calculations possible.
            This reverts the process where possible so that Repetitions end
            up with the type (date/datetime) that was specified in the icalendar
            component.
            """
            if not isinstance(
                self.original_start, datetime.datetime
            ) and not isinstance(
                self.original_end,
                datetime.datetime,
            ):
                return convert_to_date(date)
            return date

        def as_occurrence(
            self,
            start: Time,
            stop: Time,
            occurrence: type[Occurrence],
            core: ComponentAdapter,
        ) -> Occurrence:
            """Return this as an occurrence at a specific time."""
            return occurrence(
                core,
                self.convert_to_original_type(start),
                self.convert_to_original_type(stop),
            )

        @property
        def components(self) -> list[ComponentAdapter]:
            """The components in this recurrence calculation."""
            return [self.core]

    def __init__(self, components: Sequence[ComponentAdapter]):
        """Create an component which may have repetitions in it."""
        if len(components) == 0:
            raise ValueError("No components given to calculate a series.")
        # We identify recurrences with a timestamp as all recurrence values
        # should be the same in UTC either way and we want to omit
        # inequality because of timezone implementation mismatches.
        self.recurrence_id_to_modification: dict[
            RecurrenceID, ComponentAdapter
        ] = {}  # RECURRENCE-ID -> adapter
        self.this_and_future = []
        self._uid = components[0].uid
        core: ComponentAdapter | None = None
        for component in components:
            if component.is_modification():
                recurrence_ids = component.recurrence_ids
                for recurrence_id in recurrence_ids:
                    self.recurrence_id_to_modification[recurrence_id] = (
                        with_highest_sequence(
                            self.recurrence_id_to_modification.get(recurrence_id),
                            component,
                        )
                    )
                if component.this_and_future:
                    self.this_and_future.append(recurrence_ids[0])
            else:
                core = with_highest_sequence(core, component)
        self.modifications: set[ComponentAdapter] = set(
            self.recurrence_id_to_modification.values()
        )
        del component
        self.recurrence = (
            self.NoRecurrence() if core is None else self.RecurrenceRules(core)
        )
        self.this_and_future.sort()
        self.sequence = max(component.sequence for component in self.components)
        self.compute_span_extension()

    def compute_span_extension(self):
        """Compute how much to extend the span for the rrule to cover all events."""
        self._subtract_from_start, self._add_to_stop = (
            self.recurrence.extend_query_span_by
        )
        for adapter in self.this_and_future_components:
            subtract_from_start, add_to_stop = adapter.extend_query_span_by
            self._subtract_from_start = max(
                subtract_from_start, self._subtract_from_start
            )
            self._add_to_stop = max(add_to_stop, self._add_to_stop)

    @property
    def components(self) -> list[ComponentAdapter]:
        """All the components in this sequence.

        Components with the same UID might not occur if the SEQUENCE
        number suggests that they are obsolete.
        """
        return self.recurrence.components + list(self.modifications)

    @property
    def this_and_future_components(self) -> Generator[ComponentAdapter]:
        """All components that influence future events."""
        if self.recurrence.has_core:
            yield self.recurrence.core
        for recurrence_id in self.this_and_future:
            yield self.recurrence_id_to_modification[recurrence_id]

    def get_component_for_recurrence_id(
        self, recurrence_id: RecurrenceID
    ) -> ComponentAdapter:
        """Get the component which contains all information for the recurrence id.

        This concerns this modifications that have RANGE=THISANDFUTURE set.
        """
        # We assume the the recurrence_id is of the correct timezone.
        component = self.recurrence.core
        for modification_id in self.this_and_future:
            if modification_id < recurrence_id:
                component = self.recurrence_id_to_modification[modification_id]
            else:
                break
        return component

    def rrule_between(self, span_start: Time, span_stop: Time) -> Generator[Time]:
        """Modify the rrule generation span and yield recurrences."""
        expanded_start = normalize_pytz(span_start - self._subtract_from_start)
        expanded_stop = normalize_pytz(span_stop + self._add_to_stop)
        yield from self.recurrence.rrule_between(
            expanded_start,
            expanded_stop,
        )

    def between(self, span_start: Time, span_stop: Time) -> Generator[Occurrence]:
        """Components between the start (inclusive) and end (exclusive).

        The result does not need to be ordered.
        """
        returned_starts: set[Time] = set()
        returned_modifications: set[ComponentAdapter] = set()
        # NOTE: If in the following line, we get an error, datetime and date
        # may still be mixed because RDATE, EXDATE, start and rule.
        for start in self.rrule_between(span_start, span_stop):
            recurrence_ids = to_recurrence_ids(start)
            if (
                start in returned_starts
                or convert_to_date(start) in self.recurrence.check_exdates_date
                or self.recurrence.check_exdates_datetime & set(recurrence_ids)
            ):
                continue
            adapter: ComponentAdapter = get_any(
                self.recurrence_id_to_modification, recurrence_ids, self.recurrence.core
            )
            if adapter is self.recurrence.core:
                # We have no modification for this recurrence, so we record the date
                returned_starts.add(start)
                # This component is the base for this occurrence.
                # It usually is the core. However, we may also find a modification
                # with RANGE=THISANDFUTURE.
                component = self.get_component_for_recurrence_id(recurrence_ids[0])
                occurrence_start = normalize_pytz(start + component.move_recurrences_by)
                # Consider the RDATE with a PERIOD value
                occurrence_end = normalize_pytz(
                    occurrence_start
                    + get_any(
                        self.recurrence.replace_ends,
                        recurrence_ids,
                        component.duration,
                    )
                )
                occurrence = self.recurrence.as_occurrence(
                    occurrence_start, occurrence_end, self.occurrence, component
                )
            else:
                # We found a modification, so we record the modification
                if adapter in returned_modifications:
                    continue
                returned_modifications.add(adapter)
                occurrence = self.occurrence(adapter)
            if occurrence.is_in_span(span_start, span_stop):
                yield occurrence
        for modification in self.modifications:
            # we assume that the modifications are actually included
            if (
                modification in returned_modifications
                or self.recurrence.check_exdates_datetime
                & set(modification.recurrence_ids)
            ):
                continue
            if modification.is_in_span(span_start, span_stop):
                returned_modifications.add(modification)
                yield self.occurrence(modification)

    @property
    def uid(self):
        """The UID that identifies this series."""
        return self._uid

    def __repr__(self):
        """A string representation."""
        return (
            f"<{self.__class__.__name__} uid={self.uid} "
            f"modifications:{len(self.recurrence_id_to_modification)}>"
        )


___all__ = ["Series"]
