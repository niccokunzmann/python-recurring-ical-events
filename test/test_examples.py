import datetime
import pytest

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
    events = calendars.Germany.at((2014, 5, 11))
    assert len(events) == 1
    event = events[0]
    assert event["SUMMARY"] == "Germany: Mother's Day [Not a public holiday]"
    assert isinstance(event["DTSTART"].dt, datetime.date)

mbOnTourDates = [
    (2018, 9, 22), (2018, 10, 20), (2018, 11, 17), (2018, 12, 8),
    (2019, 1, 12), (2019, 1, 27), (2019, 2, 9), (2019, 2, 24),
    (2019, 3, 23), (2019, 4, 27), (2019, 5, 25), (2019, 6, 22),
]

@pytest.mark.parametrize("date", mbOnTourDates)
def test_events_are_scheduled(calendars, date):
    events = calendars.machbar_16_feb_2019.at(date)
    assert len(events) == 1

@pytest.mark.parametrize("month", [
    (2018, 9), (2018, 10), (2018, 11), (2018, 12),
    (2019, 1), (2019, 2), (2019, 3), (2019, 4), (2019, 5), (2019, 6), (2019, 7),
])
def test_no_more_events_are_scheduled(calendars, month):
    dates = [date for date in mbOnTourDates if date[:2] == month]
    number_of_dates = len(dates)
    events = calendars.machbar_16_feb_2019.at(month)
    mb_events = [event for event in events if "mB-onTour" in event["SUMMARY"]]
    assert len(mb_events) == number_of_dates
