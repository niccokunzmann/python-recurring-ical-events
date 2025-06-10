"""The RECURRENCE-ID should not be identical to DTSTART.

That is confusing.
See https://github.com/niccokunzmann/python-recurring-ical-events/issues/243
"""

from datetime import datetime


def test_recurrence_id_is_not_identical_to_dtstart(calendars):
    """We need to make sure they are distinct to set the values independently."""
    start = datetime(2015,9,1)
    end = datetime(2015,9,4)
    recurrings = calendars.issue_243_recurrence_id_is_not_identical_to_dtstart.between(start, end)
    r = recurrings[0]

    ## This break, it should pass
    assert id(r["dtstart"]) != id(r["recurrence-id"])
    assert r["dtstart"] is not r["recurrence-id"]

    ## This is true
    assert r["recurrence-id"].dt == datetime(2015,9,1,8)

    ## The test recurrence at this particlar day should start at 9, not at 8
    r["dtstart"].dt = datetime(2015,9,1,9)

    ## This should not break, but breaks
    assert r["recurrence-id"].dt == datetime(2015,9,1,8)

    r["dtstart"] = datetime(2015,9,1,9)

    ## This should not break, but breaks
    assert r["recurrence-id"].dt == datetime(2015,9,1,8)
