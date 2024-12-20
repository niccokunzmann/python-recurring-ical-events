"""Check icalendar's alarms interface.

We need to check if icalendar is doinng the right thing.
Also, recurring ical events now needs to consider alarms
in a different way.
"""

from datetime import date, timedelta

import pytest


def test_an_event_has_subcomponents_even_if_it_has_an_alarm(calendars):
    """We want the events to have no alarms by default."""
    events = calendars.alarm_at_start_of_event.at("20241004")
    assert len(events) == 1
    event = events[0]
    assert event.subcomponents != []
    assert len(event.alarms.times) != 0


@pytest.mark.parametrize("dt", [date(2024, 11, 26), date(2024, 11, 29)])
def test_alarm_time_for_event_is_correctly_computed_for_recurring_instance(
    calendars, dt
):
    """When an event is a repeated instance, we want the alarm times to be right."""
    events = calendars.alarm_recurring_and_acknowledged_at_2024_11_27_16_27.at(dt)
    assert len(events) == 1
    event = events[0]
    assert len(event.alarms.times) == 1
    assert event.alarms.times[0].trigger == event.start - timedelta(hours=1)
