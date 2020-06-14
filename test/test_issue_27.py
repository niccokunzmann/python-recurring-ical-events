"""These tests are for Issue 27
https://github.com/niccokunzmann/python-recurring-ical-events/issues/27

"""

start_date = (2020, 4, 25)
end_date =   (2020, 4, 30)

def print_events(events):
    for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        print("start {} duration {}".format(start, duration))


def test_until_value_with_unknown_timezone_works_with_exdate(calendars):
    """The until value has no time zone attached."""
    events = calendars.issue_27_t1.between(start_date, end_date)
    print_events(events)
    assert len(events) == 2, "two events, exdate matches one"


def test_until_value_with_default_timezone_works_with_exdate(calendars):
    """The until value uses the default time zone."""
    events = calendars.issue_27_t2.between(start_date, end_date)
    print_events(events)
    assert len(events) == 2, "two events, exdate matches one"




