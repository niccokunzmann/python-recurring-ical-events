"""Test the example function."""

import pytest

from recurring_ical_events.examples import example_calendar


def test_valid_example_is_returned():
    """We can get a valid example."""
    c = example_calendar("fablab_cottbus")
    assert c["X-FROM-URL"] == "http://blog.fablab-cottbus.de"


def test_we_can_remove_the_ics():
    """We can get a valid example."""
    assert example_calendar("duration") == example_calendar("duration.ics")


def test_we_know_which_files_are_ok():
    """The error message shows us which examples to use."""
    with pytest.raises(ValueError) as e:
        example_calendar("missing")
    assert "issue_4" in str(e.value)
