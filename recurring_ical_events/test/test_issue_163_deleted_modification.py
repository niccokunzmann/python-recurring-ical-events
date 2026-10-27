"""EXDATE does not exclude a modified instance for an event with higher SEQUENCE and the same UID.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/163
"""


def test_exdate_excludes_modification(calendars):
    """The exdate should exclude the modification mentioned."""
    events = calendars.issue_163_deleted_modification.at("20240819")
    assert events == []


def test_date_exdate_excludes_modification_of_datetime_series(calendars):
    """An EXDATE with a date excludes a moved occurrence on that local day."""
    calendar = calendars.issue_163_date_exdate_datetime_series
    moved = [event["SUMMARY"] for event in calendar.at("20240110")]
    assert moved == ["new york next day moved"]
    assert len(list(calendar.all())) == 12
