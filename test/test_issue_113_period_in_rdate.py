"""This tests that RDATE can be a PERIOD.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/113
"""
from datetime import datetime
import pytz

def test_rdate_is_period(calendars):
    """The recurring event has a period rdate."""
    event = calendars.test_issue_113_period_in_rdate.at("20231213")
    assert event["DTSTART"] == pytz.timezone("America/Vancouver").localize(datetime.datetime(2023, 12, 13, 12, 0))