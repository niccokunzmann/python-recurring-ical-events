"""We want to check that the DURATION is removed.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/139
"""


def test_no_duration_in_event(calendars):
    """Check that there is no DURATION in the event."""
    for event in calendars.duration.all():
        assert "DURATION" not in event
        assert "DTEND" in event
