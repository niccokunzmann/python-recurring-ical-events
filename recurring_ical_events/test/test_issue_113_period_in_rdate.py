"""This tests that RDATE can be a PERIOD.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/113

    Value Type:  The default value type for this property is DATE-TIME.
       The value type can be set to DATE or PERIOD.

    If the "RDATE" property is
    specified as a PERIOD value the duration of the recurrence
    instance will be the one specified by the "RDATE" property, and
    not the duration of the recurrence instance defined by the
    "DTSTART" property.

"""

from datetime import datetime, timedelta

import pytz


def test_start_of_rdate(calendars):
    """The event starts on that time."""
    event = calendars.issue_113_period_in_rdate.at("20231213")[0]
    expected_start = pytz.timezone("America/Vancouver").localize(
        datetime(2023, 12, 13, 12, 0)
    )
    start = event["DTSTART"].dt
    assert start == expected_start


def test_end_of_rdate(calendars):
    """The event starts on that time."""
    event = calendars.issue_113_period_in_rdate.at("20231213")[0]
    assert event["DTEND"].dt == pytz.timezone("America/Vancouver").localize(
        datetime(2023, 12, 13, 15, 0)
    )


def test_rdate_with_a_period_with_duration(calendars):
    """Check that we can process RDATE with a duration as second value."""
    events = calendars.issue_113_period_rdate_duration.at("20240913")
    assert len(events) == 1, "We found the event with the rdate."
    event = events[0]
    duration = event["DTEND"].dt - event["DTSTART"].dt
    assert duration == timedelta(hours=2)
