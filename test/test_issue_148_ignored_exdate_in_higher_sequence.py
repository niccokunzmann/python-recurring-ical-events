"""Events can be edited and a higher sequence number assigned.

In case the whole event is edited and receives a new sequence number,
the exdate should be considered.
"""

import pytest


def test_total_events(calendars):
    """We should remove the edited event."""
    events = calendars.issue_148_ignored_exdate.all()
    assert len(events) == 2


def test_the_exdate_is_not_available(calendars):
    """Make sure we do not get an event on the ecluded date."""
    events = calendars.issue_148_ignored_exdate.at("20240715")
    assert not events


@pytest.mark.parametrize(
    ("date", "summary"),
    [
        ("20240701", "test123 - edited"),
        ("20240729", "test123 - edited"),
    ],
)
def test_summary_is_modified(calendars, date, summary):
    """The summary of the edited event is used."""
    events = calendars.issue_148_ignored_exdate.at(date)
    assert events
    event = events[0]
    assert event["SUMMARY"] == summary
