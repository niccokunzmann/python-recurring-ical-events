"""These tests are for Issue 27
https://github.com/niccokunzmann/python-recurring-ical-events/issues/27
https://github.com/niccokunzmann/python-recurring-ical-events/pull/32

Diff of the two files:

diff test/calendars/issue-27-t1.ics test/calendars/issue-27-t2.ics

    < RRULE:FREQ=DAILY;UNTIL=20200429T000000
    < EXDATE:20200427T120000Z
    ---
    > RRULE:FREQ=DAILY;UNTIL=20200429T000000Z
    > EXDATE:20200427T140000Z

"""

start_date = (2020, 4, 25)
end_date = (2020, 4, 30)


def print_events(events):
    for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        print(f"start {start} duration {duration}")


def test_until_value_with_UNKNOWN_timezone_works_with_exdate(calendars):
    """The until value has no time zone attached."""
    events = calendars.issue_27_t1.between(start_date, end_date)
    print_events(events)
    assert len(events) == 2, "two events, exdate matches one"


def test_until_value_with_DEFAULT_timezone_works_with_exdate(calendars):
    """The until value uses the default time zone."""
    events = calendars.issue_27_t2.between(start_date, end_date)
    print_events(events)
    assert len(events) == 2, "two events, exdate matches one"
