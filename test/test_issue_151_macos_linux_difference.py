"""This tests if there is a difference between macOS and Linux

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/151
"""

from datetime import datetime, timezone
from recurring_ical_events import time_span_contains_event
import pytest


def _test_count_events_from_issue(calendars):
    """Avents were omitted through version upgrade from 2.2.2 to 2.2.3."""

    start_time = datetime.fromtimestamp(1722564000, timezone.utc)
    end_time = datetime.fromtimestamp(1722567600, timezone.utc)
    print(f"from {start_time.timestamp()} to {end_time.timestamp()}")
    events = calendars.issue_151_macos_linux_difference.between(start_time, end_time)
    for event in events:
        print(event["UID"], event["DTSTART"], event["SUMMARY"])
    assert len(events) == 1

def _test_check_event_count_for_that_day(calendars):
    """Avents were omitted through version upgrade from 2.2.2 to 2.2.3."""

    events = calendars.issue_151_macos_linux_difference.at("20140801")
    for event in events:
        print(event["UID"], event["DTSTART"], event["SUMMARY"], event["DTSTART"].dt.timestamp())
    assert len(events) == 1 and False  # noqa: PT018


def test_that_time_span_contains_event(calendars, utc):
    """Check that the timespan issue is due to the timezone provided."""
    start_time = datetime.fromtimestamp(1722564000, utc)
    end_time = datetime.fromtimestamp(1722567600, utc)
    events = [e for e in calendars.raw.issue_151_macos_linux_difference.walk("VEVENT") if 'RECURRENCE-ID' in e]

    assert len(events) == 1, "We find the recurrence"
    event = events[0]
    event_start_time = event["DTSTART"].dt
    event_end_time = event["DTEND"].dt
    print(f"time_span_contains_event(\n\t{start_time}, \n\t{end_time}, \n\t{event_start_time}, \n\t{event_end_time})")
    assert time_span_contains_event(start_time, end_time, event_start_time, event_end_time)

@pytest.mark.parametrize("comparable", [True, False])
def test_that_time_span_contains_event_in_same_timezone(calendars, utc, comparable):
    """Check that the timespan issue is due to the timezone provided."""
    start_time = datetime.fromtimestamp(1722564000, utc)
    end_time = datetime.fromtimestamp(1722567600, utc)
    events = [e for e in calendars.raw.issue_151_macos_linux_difference.walk("VEVENT") if 'RECURRENCE-ID' in e]

    assert len(events) == 1, "We find the recurrence"
    event = events[0]
    event_start_time = event["DTSTART"].dt
    start_time = start_time.astimezone(event_start_time.tzinfo)
    event_end_time = event["DTEND"].dt
    end_time = end_time.astimezone(event_start_time.tzinfo)
    print(f"time_span_contains_event(\n\t{start_time}, \n\t{end_time}, \n\t{event_start_time}, \n\t{event_end_time}, comparable={comparable})")
    assert time_span_contains_event(start_time, end_time, event_start_time, event_end_time, comparable=comparable)
