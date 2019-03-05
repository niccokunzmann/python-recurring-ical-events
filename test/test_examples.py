import datetime

def test_fablab_cottbus(calendars):
    """This calendar threw an exception.

        TypeError: can't compare offset-naive and offset-aware datetimes
    """
    today = datetime.datetime(2019, 3, 4, 16, 52, 10, 215209)
    one_year_ahead = today.replace(year=today.year + 1)
    one_year_before = today.replace(year=today.year - 1)
    events = calendars.fablab_cottbus.between(one_year_before, one_year_ahead)

def test_example_from_README(calendars):
    """The examples from the README should be tested so we make no
    false promises.
    """
    #import requests
    import icalendar
    import datetime
    import recurring_ical_events

    today = datetime.datetime.today()
    print(today)
    one_year_ahead = today.replace(year=today.year + 1)

    #ical_string = requests.get("https://url-to-ical-feed").text
    #calendar = icalendar.Calendar.from_ical(ical_string)
    for event in calendars.one_day_event_repeat_every_day.between(today, one_year_ahead):
        print(event["DTSTART"])


def test_no_dtend(calendars):
    """This calendar has events which have no DTEND.

        KeyError: 'DTEND'
    """
    events = calendars.discourse_no_dtend.all()


def test_date_events_are_in_the_date(calendars):
    events = calendars.Germany.between("20140511T000000Z", "20140511T000000Z")
    assert len(events) == 1
    event = events[0]
    assert event["SUMMARY"] == "Germany: Mother's Day [Not a public holiday]"
    assert isinstance(event["DTSTART"].dt, datetime.date)
