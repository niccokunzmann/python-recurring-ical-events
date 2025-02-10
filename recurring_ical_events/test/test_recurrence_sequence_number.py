"""
Tests for modified recurrences with lower sequence number than their base event
"""


def test_modified_recurrence_lower_sequence_number(calendars):
    events = calendars.recurrence_sequence_number.at("20200922")
    assert len(events) == 1
    assert events[0].get("SUMMARY") == "Modified event"
