"""The atlassian confluence calendar sets the until value lower than the DTSTART when then event is deleted.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/117
"""


def test_event_is_deleted(calendars):
    """No event takes place."""
    assert not list(calendars.issue_117_until_before_dtstart.all())
