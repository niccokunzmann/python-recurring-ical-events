import pytest

def test_expected_amount_of_events(calendars):
    events = calendars.issue_28_rrule_with_UTC_endinginZ.between((2020, 5, 25),(2020, 9, 5))
    assert len(events) == 15

