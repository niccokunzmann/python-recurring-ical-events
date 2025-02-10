"""The atlassian confluence calendar sets the count value to -1 when future events are deleted.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/128
"""

import pytest

import recurring_ical_events.constants


def test_all_events_are_present(calendars):
    """All events are shown and not just the first one."""
    assert len(list(calendars.issue_128_only_first_event.all())) == 7


@pytest.mark.parametrize(
    ("string", "matches"),
    [
        ("COUNT=1", False),
        ("COUNT=1;", False),
        ("COUNT=-1", True),
        ("COUNT=-1;", True),
        ("COUNT=-100", True),
        ("COUNT=-100;", True),
    ],
)
def test_matching_negative_count(string, matches):
    """Make sure the general replacement pattern works."""
    actually_matches = (
        recurring_ical_events.constants.NEGATIVE_RRULE_COUNT_REGEX.match(string)
        is not None
    )
    assert actually_matches == matches
