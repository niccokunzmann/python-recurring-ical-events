"""These tests are for Issue 28
https://github.com/niccokunzmann/python-recurring-ical-events/issues/28

"""
import pytest

def test_expected_amount_of_events(calendars):
    events = calendars.issue_28_rrule_with_UTC_endinginZ.between((2020, 5, 25),(2020, 9, 5))
    assert len(events) == 15

