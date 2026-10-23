"""Tests for RFC 5545 examples of recurrences.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/197

RFC 5545 defines several recurrence examples in Section 3.8.5.3.
This test file verifies that the library correctly handles these examples.
"""

import pytest
from datetime import datetime, timedelta


def test_rfc5545_example_1_every_3_hours(calendars):
    """Every 3 hours from 9:00 AM to 5:00 PM on a specific day.

    DTSTART;TZID=America/New_York:19970902T090000
    RRULE:FREQ=HOURLY;INTERVAL=3;UNTIL=19970902T170000Z

    ==> (September 2, 1997 EDT) 09:00, 12:00, 15:00

    Note: The RFC example shows 3 occurrences (09:00, 12:00, 15:00), but
    UNTIL=19970902T170000Z is 13:00 EDT (UTC-4), so only 09:00 and 12:00
    are before the UNTIL time. This test verifies the correct behavior
    per RFC 5545 UNTIL semantics.
    """
    # Get all occurrences on September 2, 1997
    occurrences = calendars.issue_197_rfc5545_examples.at("19970902")
    
    # Filter for the hourly event
    hourly_events = [e for e in occurrences if "3 hours" in str(e.get("SUMMARY", ""))]
    
    # UNTIL=170000Z = 13:00 EDT, so only 09:00 and 12:00 are included
    assert len(hourly_events) == 2, f"Expected 2 occurrences, got {len(hourly_events)}"

    # Check the times (in UTC, New York is UTC-4 in September)
    times = sorted([o["DTSTART"].dt for o in hourly_events])
    expected_times = [
        datetime(1997, 9, 2, 9, 0),   # 09:00 EDT = 13:00 UTC
        datetime(1997, 9, 2, 12, 0),  # 12:00 EDT = 16:00 UTC
    ]
    for i, (actual, expected) in enumerate(zip(times, expected_times)):
        # Compare as naive datetimes for simplicity
        assert actual.replace(tzinfo=None) == expected, (
            f"Occurrence {i}: expected {expected}, got {actual}"
        )


def test_rfc5545_example_2_every_15_minutes(calendars):
    """Every 15 minutes for 6 occurrences.

    DTSTART;TZID=America/New_York:19970902T090000
    RRULE:FREQ=MINUTELY;INTERVAL=15;COUNT=6

    ==> (September 2, 1997 EDT) 09:00, 09:15, 09:30, 09:45, 10:00, 10:15
    """
    # Get all occurrences on September 2, 1997
    occurrences = calendars.issue_197_rfc5545_examples.at("19970902")
    
    # Filter for the 15-minute event
    fifteen_min_events = [e for e in occurrences if "15 minutes" in str(e.get("SUMMARY", ""))]
    assert len(fifteen_min_events) == 6, f"Expected 6 occurrences, got {len(fifteen_min_events)}"

    # Check the times
    times = sorted([o["DTSTART"].dt for o in fifteen_min_events])
    expected_times = [
        datetime(1997, 9, 2, 9, 0),
        datetime(1997, 9, 2, 9, 15),
        datetime(1997, 9, 2, 9, 30),
        datetime(1997, 9, 2, 9, 45),
        datetime(1997, 9, 2, 10, 0),
        datetime(1997, 9, 2, 10, 15),
    ]
    for i, (actual, expected) in enumerate(zip(times, expected_times)):
        assert actual.replace(tzinfo=None) == expected, (
            f"Occurrence {i}: expected {expected}, got {actual}"
        )


def test_rfc5545_example_3_every_hour_and_a_half(calendars):
    """Every hour and a half for 4 occurrences.

    DTSTART;TZID=America/New_York:19970902T090000
    RRULE:FREQ=MINUTELY;INTERVAL=90;COUNT=4

    ==> (September 2, 1997 EDT) 09:00, 10:30, 12:00, 13:30
    """
    # Get all occurrences on September 2, 1997
    occurrences = calendars.issue_197_rfc5545_examples.at("19970902")
    
    # Filter for the 90-minute event
    ninety_min_events = [e for e in occurrences if "hour and a half" in str(e.get("SUMMARY", ""))]
    assert len(ninety_min_events) == 4, f"Expected 4 occurrences, got {len(ninety_min_events)}"

    # Check the times
    times = sorted([o["DTSTART"].dt for o in ninety_min_events])
    expected_times = [
        datetime(1997, 9, 2, 9, 0),
        datetime(1997, 9, 2, 10, 30),
        datetime(1997, 9, 2, 12, 0),
        datetime(1997, 9, 2, 13, 30),
    ]
    for i, (actual, expected) in enumerate(zip(times, expected_times)):
        assert actual.replace(tzinfo=None) == expected, (
            f"Occurrence {i}: expected {expected}, got {actual}"
        )


def test_rfc5545_example_4_every_20_minutes(calendars):
    """Every 20 minutes from 9:00 AM to 4:40 PM every day.

    DTSTART;TZID=America/New_York:19970902T090000
    RRULE:FREQ=DAILY;BYHOUR=9,10,11,12,13,14,15,16;BYMINUTE=0,20,40

    ==> (September 2, 1997 EDT) 9:00, 9:20, 9:40, 10:00, 10:20,
                                ... 16:00, 16:20, 16:40
    """
    # Get all occurrences on September 2, 1997
    occurrences = calendars.issue_197_rfc5545_examples.at("19970902")
    
    # Filter for the 20-minute event
    twenty_min_events = [e for e in occurrences if "20 minutes" in str(e.get("SUMMARY", ""))]
    
    # 8 hours * 3 occurrences per hour = 24 occurrences
    assert len(twenty_min_events) == 24, f"Expected 24 occurrences, got {len(twenty_min_events)}"

    # Check that all times are correct (every 20 minutes from 9:00 to 16:40)
    times = sorted([o["DTSTART"].dt.replace(tzinfo=None) for o in twenty_min_events])
    
    # Generate expected times
    expected_times = []
    for hour in range(9, 17):  # 9:00 to 16:xx
        for minute in [0, 20, 40]:
            expected_times.append(datetime(1997, 9, 2, hour, minute))
    
    assert times == expected_times, f"Times don't match expected pattern"
