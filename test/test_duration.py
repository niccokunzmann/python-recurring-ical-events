"""
Test the DURATION property.

Not all events have an end.
Some events define no explicit end and some a DURATION.
RFC: https://www.kanzaki.com/docs/ical/duration.html

"""
import pytest

@pytest.mark.parametrize("date,count", [
    # event 3 days
    ("20180110", 1), ("20180111", 1), ("20180112", 1),
    ("20180109", 0), ("20180114", 0),
    # event 3 hours
    ((2018, 1, 15, 10), 1), ((2018, 1, 15, 11), 1), ((2018, 1, 15, 12), 1), 
    ((2018, 1, 15,  9), 0), ((2018, 1, 15, 14), 0), 
    # event with no duration nor end
    ((2018, 1, 20), 1),
    ((2018, 1, 19), 0), ((2018, 1, 21), 0),
])
def test_events_expected(date, count, calendars):
    events = calendars.duration.at(date)
    assert len(events) == count

