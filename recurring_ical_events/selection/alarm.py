"""Selection for alarms."""

from __future__ import annotations

import contextlib
import datetime
from typing import TYPE_CHECKING, Sequence

from recurring_ical_events.adapters.event import EventAdapter
from recurring_ical_events.adapters.todo import TodoAdapter
from recurring_ical_events.selection.base import SelectComponents

if TYPE_CHECKING:
    from icalendar.cal import Component

    from recurring_ical_events.adapters.component import ComponentAdapter
    from recurring_ical_events.series import Series


class Alarms(SelectComponents):
    """Select alarms and find their times.

    By default, alarms from TODOs and events are collected.
    You can use this to change which alarms are collected:

        Alarms((EventAdapter,))
        Alarms((TodoAdapter,))
    """

    def __init__(
        self,
        parents: tuple[type[ComponentAdapter] | SelectComponents] = (
            EventAdapter,
            TodoAdapter,
        ),
    ):
        self.parents = parents

    @staticmethod
    def component_name():
        """The name of the component we calculate."""
        return "VALARM"

    def collect_parent_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect the parent components of alarms."""
        return [
            s
            for parent in self.parents
            for s in parent.collect_series_from(source, suppress_errors)
        ]

    def collect_series_from(
        self, source: Component, suppress_errors: tuple[Exception]
    ) -> Sequence[Series]:
        """Collect all TODOs and Alarms from VEVENTs and VTODOs.

        suppress_errors - a list of errors that should be suppressed.
            A Series of events with such an error is removed from all results.
        """
        from recurring_ical_events.series.alarm import (
            AbsoluteAlarmSeries,
            AlarmSeriesRelativeToEnd,
            AlarmSeriesRelativeToStart,
        )

        absolute_alarms = AbsoluteAlarmSeries()
        result = []
        # alarms might be copied several times. We only compute them once.
        for series in self.collect_parent_series_from(source, suppress_errors):
            used_alarms = []
            for component in series.components:
                for alarm in component.alarms:
                    with contextlib.suppress(suppress_errors):
                        trigger = alarm.TRIGGER
                        if trigger is None or alarm in used_alarms:
                            continue
                        if isinstance(trigger, datetime.datetime):
                            absolute_alarms.add(alarm, component)
                            used_alarms.append(alarm)
                        elif alarm.TRIGGER_RELATED == "START":
                            result.append(AlarmSeriesRelativeToStart(alarm, series))
                            used_alarms.append(alarm)
                        elif alarm.TRIGGER_RELATED == "END":
                            result.append(AlarmSeriesRelativeToEnd(alarm, series))
                            used_alarms.append(alarm)
        if not absolute_alarms.is_empty():
            result.append(absolute_alarms)
        return result


__all__ = ["Alarms"]
