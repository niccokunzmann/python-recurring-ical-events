'''
This tests the issue 20. Exdates seem to be ignored.
https://github.com/niccokunzmann/python-recurring-ical-events/issues/20
'''
import pytest

@pytest.mark.parametrize("exdate", 
    # exdates copied from the source
    "20191015T141500Z,20191022T141500Z,20191105T151500Z,20191119T151500Z,"
    "20191126T151500Z,20191203T151500Z,20191217T151500Z,20191224T151500Z,201912"
    "31T151500Z".split(","))
def test_exdates_do_not_show_up(exdate, calendars):
    """Test that certain exdates do not occur."""
    events = calendars.issue_20_exdate_ignored.at(exdate[:8])
    assert not events, "{} should not occur at {}.".format(
        events[0].to_ical().decode(),
        exdate)
    
def test_there_are_n_events(calendars):
    """Test the total numer of events."""
    assert len(calendars.issue_20_exdate_ignored.all()) == 8

