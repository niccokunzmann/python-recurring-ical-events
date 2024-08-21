"""EXDATE does not exclude a modified instance for an event with higher SEQUENCE and the same UID.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/163
"""


def test_exdate_excludes_modification(calendars):
    """The exdate should exclude the modification mentioned."""
    events = calendars.issue_163_deleted_modification.at("20240819")
    assert events == []
