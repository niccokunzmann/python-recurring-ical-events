import datetime

import pytest


def test_fablab_cottbus(calendars):
    """This calendar threw an exception.

    TypeError: can't compare offset-naive and offset-aware datetimes
    """
    today = datetime.datetime(2019, 3, 4, 16, 52, 10, 215209)
    one_year_ahead = today.replace(year=today.year + 1)
    one_year_before = today.replace(year=today.year - 1)
    calendars.fablab_cottbus.between(one_year_before, one_year_ahead)


def test_example_from_README(calendars):
    """The examples from the README should be tested so we make no
    false promises.
    """

    start_date = (2019, 3, 5)
    end_date = (2019, 4, 1)

    events = calendars.one_day_event_repeat_every_day.between(start_date, end_date)
    for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        print(f"start {start} duration {duration}")
    assert event


def test_no_dtend(calendars):
    """This calendar has events which have no DTEND.

    KeyError: 'DTEND'
    """
    list(calendars.discourse_no_dtend.all())


def test_date_events_are_in_the_date(calendars):
    events = calendars.Germany.at((2014, 5, 11))
    assert len(events) == 1
    event = events[0]
    assert event["SUMMARY"] == "Germany: Mother's Day [Not a public holiday]"
    assert isinstance(event["DTSTART"].dt, datetime.date)


mb_on_tour_dates = [
    (2018, 9, 22),
    (2018, 10, 20),
    (2018, 11, 17),
    (2018, 12, 8),
    (2019, 1, 12),
    (2019, 1, 27),
    (2019, 2, 9),
    (2019, 2, 24),
    (2019, 3, 23),
    (2019, 4, 27),
    (2019, 5, 25),
    (2019, 6, 22),
]


@pytest.mark.parametrize("date", mb_on_tour_dates)
def test_events_are_scheduled(calendars, date):
    events = calendars.machbar_16_feb_2019.at(date)
    assert len(events) == 1


@pytest.mark.parametrize(
    "month",
    [
        (2018, 9),
        (2018, 10),
        (2018, 11),
        (2018, 12),
        (2019, 1),
        (2019, 2),
        (2019, 3),
        (2019, 4),
        (2019, 5),
        (2019, 6),
        (2019, 7),
    ],
)
def test_no_more_events_are_scheduled(calendars, month):
    dates = [date for date in mb_on_tour_dates if date[:2] == month]
    number_of_dates = len(dates)
    events = calendars.machbar_16_feb_2019.at(month)
    mb_events = [event for event in events if "mB-onTour" in event["SUMMARY"]]
    assert len(mb_events) == number_of_dates


def test_german_holidays(calendars):
    """Test the calendar from
    https://www.calendarlabs.com/ical-calendar/ics/46/Germany_Holidays.ics
    """
    holidays = calendars.Germany_Holidays.at(2020)
    assert len(holidays) == 17


def test_exdate_date(calendars):
    """The EXDATE can be a date, too.

    See https://github.com/niccokunzmann/python-recurring-ical-events/pull/121
    """
    assert calendars.date_exclude.at("20231216") == []


@pytest.mark.parametrize(
    ("date", "count"),
    [
        ("20240923", 0),
        ("20240924", 3),
        ("20240925", 0),
        ("20240926", 3),
        ("20240927", 0),
    ],
)
def test_same_events_at_same_time(calendars, date, count):
    """Make sure that events can be moved to the same time."""
    assert len(calendars.same_event_recurring_at_same_time.at(date)) == count
