"""
This tests the issue 20. Exdates seem to be ignored.
https://github.com/niccokunzmann/python-recurring-ical-events/issues/20

Another issue of this calendar is that the UNTIL value ends one second
before the next event.
The event in February should be exluded therefore.
"""

import pytest


@pytest.mark.parametrize(
    "exdate",
    # exdates copied from the source
    [
        "20191015T141500Z",
        "20191022T141500Z",
        "20191105T151500Z",
        "20191119T151500Z",
        "20191126T151500Z",
        "20191203T151500Z",
        "20191217T151500Z",
        "20191224T151500Z",
        "20191231T151500Z",
    ],
)
def test_exdates_do_not_show_up(exdate, calendars):
    """Test that certain exdates do not occur."""
    events = calendars.issue_20_exdate_ignored.at(exdate[:8])
    assert not events, f"{events[0].to_ical().decode()} should not occur at {exdate}."


expected_dates = [
    #    "20191015", # exdates are commented out
    #    "20191022",
    "20191029",
    #    "20191105",
    "20191112",
    #    "20191119",
    #    "20191126",
    #    "20191203",
    "20191210",
    #    "20191217",
    #    "20191224",
    #    "20191231",
    "20200107",
    "20200114",
    "20200121",
    "20200128",
]


@pytest.mark.parametrize("date", expected_dates)
def test_rrule_dates_show_up(date, calendars):
    """Test that the other events are present.

    The exdates are commented out.
    """
    events = calendars.issue_20_exdate_ignored.at(date)
    assert len(events) == 1, "There should be an event at.".format()


def test_there_are_n_events(calendars):
    """Test the total numer of events."""
    events = list(calendars.issue_20_exdate_ignored.all())
    for event, expected_date in zip(events, expected_dates):
        print("start: {} expected: {}".format(event["DTSTART"].dt, expected_date))
    for date in expected_dates[len(events) :]:
        print(f"expected: {date}")
    for event in events[len(expected_dates) :]:
        print("not expected: {}".format(event["DTSTART"].dt))
    assert len(events) == 7


def test_rdate_after_until_also_in_rrule(calendars):
    """Special test for pytz, if the event is included."""
    events = calendars.rdate_falls_on_rrule_until.at("20200204")
    for event in events:
        print(event)
    assert len(events) == 1
