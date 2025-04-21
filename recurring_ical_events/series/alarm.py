"""Series calculation for alarms."""

import datetime
from collections import defaultdict
from typing import Generator

from dateutil.rrule import rruleset
from icalendar import Alarm

from recurring_ical_events.adapters.component import ComponentAdapter
from recurring_ical_events.occurrence import AlarmOccurrence, Occurrence
from recurring_ical_events.series.rrule import Series
from recurring_ical_events.types import Time
from recurring_ical_events.util import convert_to_datetime


class AbsoluteAlarmSeries:
    """A series of absolute alarms."""

    tzinfo = datetime.timezone.utc

    def __init__(self):
        """Create a new series of absolute alarms."""
        self.times = rruleset(cache=True)
        self.times2occurence: dict[datetime.datetime, list[Occurrence]] = defaultdict(
            list
        )

    def add(self, alarm: Alarm, parent: ComponentAdapter):
        """Add an absolute alarm with a parent component."""
        trigger = alarm.TRIGGER
        self._add(trigger, alarm, parent)
        for _ in range(alarm.REPEAT):
            trigger += alarm.DURATION
            self._add(trigger, alarm, parent)

    def _add(self, dt: datetime.datetime, alarm: Alarm, parent: ComponentAdapter):
        """Add an alarm at a specific time."""
        self.times.rdate(dt)
        self.times2occurence[dt].append(self.occurrence(dt, alarm, parent))

    def between(
        self, span_start: Time, span_stop: Time
    ) -> Generator[Occurrence, None, None]:
        """Components between the start (inclusive) and end (exclusive).

        The result does not need to be ordered.
        """
        span_start_dt = convert_to_datetime(span_start, self.tzinfo)
        span_stop_dt = convert_to_datetime(span_stop, self.tzinfo)
        for dt in self.times.between(span_start_dt, span_stop_dt, inc=True):
            for occurrence in self.times2occurence[dt]:
                if occurrence.is_in_span(span_start_dt, span_stop_dt):
                    yield occurrence

    def occurrence(
        self, dt: datetime.datetime, alarm: Alarm, parent: ComponentAdapter
    ) -> Occurrence:
        """Create a new occurrence."""
        return AlarmOccurrence(dt, alarm, parent)

    def is_empty(self) -> bool:
        """Whether this series is empty."""
        return not self.times2occurence


class AlarmSeriesRelativeToStart:
    """A series of alarms relative to the start of a component."""

    def __init__(self, alarm: Alarm, series: Series) -> None:
        """Create a series of alarms that are relative to the start of a series."""
        self._alarm = alarm
        self._series = series
        self._offsets: list[datetime.timedelta] = [alarm.TRIGGER]
        for _ in range(alarm.REPEAT):
            self._offsets.append(self._offsets[-1] + alarm.DURATION)

    def between(
        self, span_start: Time, span_stop: Time
    ) -> Generator[Occurrence, None, None]:
        """Components between the start (inclusive) and end (exclusive).

        The result does not need to be ordered.
        """
        # TODO: Reduce time span to reduce occurrences
        for offset in self._offsets:
            # If we are before the event start (negative offset),
            # we have to add the time span to request the event later.
            for parent in self._series.between(span_start - offset, span_stop - offset):
                if parent.has_alarm(self._alarm):
                    occurrence = self.occurrence(offset, self._alarm, parent)
                    if occurrence.is_in_span(span_start, span_stop):
                        yield occurrence

    def occurrence(
        self, offset: datetime.timedelta, alarm: Alarm, parent: Occurrence
    ) -> Occurrence:
        """Create a new occurrence."""
        return AlarmOccurrence(offset + parent.start, alarm, parent)

    def __repr__(self) -> str:
        """repr()"""
        return (
            f"<{self.__class__.__name__} "
            f"of {self._alarm} in {self._series} "
            f"with offsets {', '.join(map(str, self._offsets))}>"
        )


class AlarmSeriesRelativeToEnd(AlarmSeriesRelativeToStart):
    """A series of alarms relative to the start of a component."""

    def between(self, span_start, span_stop):
        """Components between the start (inclusive) and end (exclusive).

        The result does not need to be ordered.
        """
        # The end is exclusive. We must adjust the timespan to include it.
        return super().between(span_start - datetime.timedelta(seconds=1), span_stop)

    def occurrence(
        self, offset: datetime.timedelta, alarm: Alarm, parent: Occurrence
    ) -> Occurrence:
        """Create a new occurrence."""
        return AlarmOccurrence(offset + parent.end, alarm, parent)


__all__ = [
    "AbsoluteAlarmSeries",
    "AlarmSeriesRelativeToEnd",
    "AlarmSeriesRelativeToStart",
]
