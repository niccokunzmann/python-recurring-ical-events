"""Test VALARM recurrence.

VALARM is specified in RFC 5545 and RFC 9074.
See also https://github.com/niccokunzmann/python-recurring-ical-events/issues/186
"""

from datetime import datetime, timedelta, timezone

import icalendar
import pytest


@pytest.mark.parametrize(
    ("when", "count"),
    [
        ("20241003", 1),
        ((2024, 10, 3, 13), 1),
        ((2024, 10, 3, 13, 0), 1),
        ((2024, 10, 3, 12), 0),
        ((2024, 10, 3, 14), 0),
    ],
)
def test_can_find_absolute_alarm(alarms, when, count):
    """Find the absolute alarm."""
    a = alarms.alarm_absolute.at(when)
    assert len(a) == count
    if count == 1:
        e: icalendar.Event = a[0]
        assert len(e.alarms.times) == 1
        t = e.alarms.times[0]
        assert t.trigger == datetime(2024, 10, 3, 13, 0, 0, tzinfo=timezone.utc)


def test_edited_alarm_is_moved(alarms):
    """When an absolute alarm is edited, the old one does not occur."""
    assert len(alarms.alarm_absolute_edited.at("20241004")) == 1, "New alarm is found"
    assert len(alarms.alarm_absolute_edited.at("20241003")) == 0, "Old alarm is removed"


@pytest.mark.parametrize(
    ("when", "deltas"),
    [
        ("20241003", {0, 45, 90}),
        ((2024, 10, 3, 13), {0, 45}),
        ((2024, 10, 3, 13, 0), {0}),
        ((2024, 10, 3, 12), set()),
        ((2024, 10, 3, 14), {90}),
    ],
)
def test_can_find_absolute_alarm_with_repeat(alarms, when, deltas):
    """This absolute alarm has 2 repetitions in 45 min later."""
    a = alarms.alarm_absolute_repeat.at(when)
    deltas = {timedelta(minutes=m) for m in deltas}
    e_deltas = set()
    for e in a:
        assert len(e.alarms.times) == 1
        t = e.alarms.times[0]
        e_deltas.add(t.trigger - datetime(2024, 10, 3, 13, 0, 0, tzinfo=timezone.utc))
    assert e_deltas == deltas


@pytest.mark.parametrize("day", [17, 18, 19, 20])
def test_collect_alarms_from_todos_relative_to_start(alarms, day):
    """We also collect alarms from todos."""
    todos = alarms.alarm_removed_and_moved.at((2023, 12, day))
    assert len(todos) == 1
    todo = todos[0]
    assert len(todo.alarms.times) == 1
    alarm = todo.alarms.times[0]
    assert alarm.trigger.replace(tzinfo=None) == datetime(2023, 12, day, 8, 0)


@pytest.mark.parametrize("day", [17, 18, 19, 20])
def test_collect_todos_with_alarms(calendars, day):
    """We also collect alarms from todos."""
    calendars.components = ["VTODO"]
    todos = calendars.alarm_removed_and_moved.at((2023, 12, day))
    assert len(todos) == 1
    todo = todos[0]
    assert todo.start.replace(tzinfo=None) == datetime(2023, 12, day, 9, 0)


def test_collect_alarms_from_todos_relative_to_end(alarms):
    """We also collect alarms from todos."""
    todos = alarms.alarm_removed_and_moved.at((2023, 12, 16, 10))
    assert len(todos) == 1
    todo = todos[0]
    assert todo.start.replace(tzinfo=None) == datetime(2023, 12, 16, 9, 0)
    assert len(todo.alarms.times) == 1
    alarm = todo.alarms.times[0]
    assert alarm.trigger.replace(tzinfo=None) == datetime(2023, 12, 16, 10, 0)


def test_todo_occurs(calendars):
    """The todo should occur so we can find the alarm."""
    calendars.components = ["VTODO"]
    todos = calendars.alarm_removed_and_moved.at((2023, 12, 16, 9))
    for x in todos:
        print(x.to_ical().decode())
        print()
    assert len(todos) == 1
    todo = todos[0]
    assert todo.start.replace(tzinfo=None) == datetime(2023, 12, 16, 9, 0)


def test_collect_alarms_from_todos_absolute(alarms):
    """We also collect alarms from todos."""
    todos = alarms.alarm_removed_and_moved.at((2023, 12, 13, 18, 0))
    assert len(todos) == 1
    todo = todos[0]
    assert len(todo.alarms.times) == 1
    alarm = todo.alarms.times[0]
    assert alarm.trigger.replace(tzinfo=None) == datetime(2023, 12, 13, 18, 0)


def test_series_of_events_with_alarms_but_alarm_removed(alarms):
    """We test that an alarm is removed and does not turn up."""
    assert alarms.alarm_removed_and_moved.at("20241221") == []


def test_alarm_is_moved(alarms):
    """The alarm is moved to 30 min before."""
    a = alarms.alarm_removed_and_moved.at("20241222")
    assert len(a) == 1
    e = a[0]
    assert len(e.alarms.times) == 1
    alarm = e.alarms.times[0]
    assert alarm.trigger.hour == 8
    assert alarm.trigger.minute == 30


def test_event_is_moved(alarms):
    """The event has been moved but the alarm is still 1h before."""
    a = alarms.alarm_removed_and_moved.at("20241219")
    for x in a:
        print(x.to_ical().decode())
        print()
    assert len(a) == 1
    e = a[0]
    assert len(e.alarms.times) == 1
    alarm = e.alarms.times[0]
    assert alarm.trigger.hour == 11
    assert alarm.trigger.minute == 0


def test_series_of_events_with_alarms_but_alarm_removed_relative_to_end():
    pytest.skip("TODO - but probably covered by the calculation relative to start")


def test_series_of_events_with_alarms_but_alarm_edited_relative_to_end():
    pytest.skip("TODO - but probably covered by the calculation relative to start")


def test_series_of_events_with_alarm_relative_to_end(alarms):
    """We check alarms relative to the end and start.

    DTSTART;TZID=Europe/London:20241004T110000
    DTEND;TZID=Europe/London:20241004T114500

    15min before start&end
    15min after start&end

    """
    q = alarms.alarm_around_event_boundaries
    assert len(q.at((2024, 10, 4, 10, 45))) == 1, "15 min before start"
    assert len(q.at((2024, 10, 4, 11, 15))) == 1, "15 min after start"
    assert len(q.at((2024, 10, 4, 11, 30))) == 1, "15 min before end"
    assert len(q.at((2024, 10, 4, 12, 0))) == 1, "15 min after end"


@pytest.mark.parametrize(
    ("dt", "trigger"),
    [
        ("20241126", datetime(2024, 11, 26, 13, 0, 0)),
        ("20241127", datetime(2024, 11, 27, 13, 0, 0)),
        ("20241128", datetime(2024, 11, 28, 13, 0, 0)),
        ("20241129", datetime(2024, 11, 29, 13, 0, 0)),
        # narrow it down
        ((2024, 11, 28, 12), None),
        ((2024, 11, 28, 12, 30), None),
        ((2024, 11, 28, 13), datetime(2024, 11, 28, 13, 0, 0)),
        ((2024, 11, 28, 13, 0), datetime(2024, 11, 28, 13, 0, 0)),
        ((2024, 11, 28, 13, 0, 0), datetime(2024, 11, 28, 13, 0, 0)),
        ((2024, 11, 28, 13, 0, 1), None),
        ((2024, 11, 28, 14), None),
    ],
)
def test_series_of_event_with_alarm_relative_to_start(alarms, dt, trigger):
    """This series of events all are preceded by an alarm.

    The alarm occurs 1h before the event starts.
    In this test, we narrow down our query time to make sure we find it.
    """
    a = alarms.alarm_recurring_and_acknowledged_at_2024_11_27_16_27.at(dt)
    if trigger is None:
        assert len(a) == 0
        return
    assert len(a) == 1, f"{dt} has {len(a)} alarms"
    event = a[0]
    assert len(event.alarms.times) == 1
    only_trigger = event.alarms.times[0].trigger
    assert only_trigger.replace(tzinfo=None) == trigger
    assert icalendar.timezone.tzid_from_dt(only_trigger) == "Europe/London"


def test_alarm_without_trigger_is_ignored_as_invalid(alarms):
    """Alarms can be malformed in many ways. This skips a few possibilities."""
    alarms.skip_bad_series = True
    q = alarms.issue_186_invalid_trigger
    e = list(q.all())
    for a in e:
        assert len(a.alarms.times) == 1
        description = a.alarms.times[0].alarm["DESCRIPTION"]
        assert description in ("correct trigger", "absolute trigger")
    assert len(e) == 2


def test_event_is_not_modified_with_2_alarms(alarms):
    """The base event should not be modified."""
    q = alarms.alarm_1_week_before_event
    assert len(q.at("20241202")) == 1, "We find the alarm"
    assert len(q.at("20241202")) == 1, "We find the alarm again"
    assert len(q.at("20241207")) == 1, "We also find the other alarm"


def test_repeating_event_is_not_modified_with_repeating_alarm(alarms):
    """The base event should not be modified."""
    q = alarms.alarm_absolute_repeat
    assert len(list(q.all())) == 3, "We find the alarms"
    assert len(list(q.all())) == 3, "We find the alarm again"


def test_repeating_event_is_not_modified(alarms):
    """The base event should not be modified."""
    q = alarms.alarm_recurring_and_acknowledged_at_2024_11_27_16_27
    assert len(q.between("20241126", "20241130")) == 4, "We find the alarms"
    assert len(q.between("20241126", "20241130")) == 4, "We find the alarm again"


EXPECTED_TRIGGERS = [
    datetime(2024, 12, 18, 8, 0),
    datetime(2024, 12, 19, 11, 0),
    datetime(2024, 12, 20, 8, 0),
    # datetime(2024, 12, 21, 8, 0),  # event without alarm
    datetime(2024, 12, 22, 8, 30),
    datetime(2024, 12, 23, 8, 0),
]
EXPECTED_STARTS = [
    datetime(2024, 12, 18, 9, 0),
    datetime(2024, 12, 19, 12, 0),
    datetime(2024, 12, 20, 9, 0),
    # datetime(2024, 12, 21, 9, 0),  # event without alarm
    datetime(2024, 12, 22, 9, 0),
    datetime(2024, 12, 23, 9, 0),
]


def test_after_with_alarms(alarms):
    """The after function checks if an event was already returned.

    This is likely to cause problems because it should be there several times.
    """
    found_triggers = []
    i = 0
    it = alarms.alarm_removed_and_moved.after(2024)
    for expected_trigger, event, expected_start in zip(
        EXPECTED_TRIGGERS, it, EXPECTED_STARTS
    ):
        print(
            f"{i} start {event.start} is {('' if event.start.replace(tzinfo=None) == expected_start else 'NOT ')}as expected"
        )
        assert len(event.alarms.times) == 1
        trigger = event.alarms.times[0].trigger.replace(tzinfo=None)
        found_triggers.append(trigger)
        print(
            f"{i} trigger {trigger} is {('' if trigger == expected_trigger else 'NOT ')}as expected"
        )
        i += 1  # noqa: SIM113
        print()
    print("\n".join(map(str, zip(found_triggers, EXPECTED_TRIGGERS))))
    assert found_triggers == EXPECTED_TRIGGERS
    with pytest.raises(StopIteration):
        next(it)


def test_all_alarms_are_present(alarms):
    """Check that we find all alarms."""
    events = alarms.alarm_several_in_one.all()
    triggers = []
    for event in events:
        assert len(event.alarms.times) == 1
        triggers.append(event.alarms.times[0].trigger - event.start)
    assert triggers == [
        timedelta(hours=-1),
        timedelta(minutes=-15),
        timedelta(minutes=15),
        timedelta(hours=1),
        timedelta(hours=2),
        timedelta(hours=3),
    ]


def test_several_alarms_occur_for_a_slightly_different_event(alarms):
    """Edited subevents have all an alarm that occurs at the same time.

    Thus, they all should appear.
    """
    events = list(alarms.alarms_at_the_same_time.all())
    summaries = {event["SUMMARY"] for event in events}
    assert summaries == {
        "event with alarm at the same time 1",
        "event with alarm at the same time 2",
        "event with alarm at the same time 3",
    }


@pytest.mark.parametrize("dt", ["20241220", "20241221", "20241222"])
def test_different_alarms_at_the_same_time_merge_into_one(alarms, dt):
    """If an event has different alarms happening at the same time,

    these alarms are in the event.
    """
    events: list[icalendar.Event] = alarms.alarms_different_in_same_event.at(dt)
    alarm_names = {
        alarm_time.alarm["DESCRIPTION"]
        for event in events
        for alarm_time in event.alarms.times
    }
    assert alarm_names >= {"Alarm 1", "Alarm 2", "Alarm 3"}
    if dt == "20241220":
        assert "Alarm 4" in alarm_names
