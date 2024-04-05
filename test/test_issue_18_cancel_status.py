"""Test that cancelled events are actually repeated as cancelled."""

import pytest


@pytest.mark.parametrize(
    ("date", "attr", "value"),
    [
        ("20200128", "STATUS", None),
        ("20200129", "STATUS", "CANCELLED"),
        ("20200130", "STATUS", None),
        ("20200128", "TRANSP", "OPAQUE"),
        ("20200129", "TRANSP", "OPAQUE"),
        ("20200130", "TRANSP", "OPAQUE"),
    ],
)
def test_events_are_cancelles(calendars, date, attr, value):
    event = calendars.issue_18_cancel_status.at(date)[0]
    assert event.get(attr) == value
