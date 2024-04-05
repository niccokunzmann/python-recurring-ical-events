"""This file tests the issue 15.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/15

calendars = <conftest.ReversedCalendars object at 0x79c21bcb9b70>

    def test_rdate_does_not_double_rrule_entry(calendars):
>       events = calendars.rdate.at("20140705")

test/test_rdate.py:56:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
recurring_ical_events.py:277: in at
    return self.between(dt, dt + self._DELTAS[len(date) - 3])
recurring_ical_events.py:306: in between
    add_event(repetition.as_vevent())
recurring_ical_events.py:292: in add_event
    if event["SEQUENCE"] < other["SEQUENCE"]:

"""


def test_sequence_is_not_present(calendars):
    events = calendars.issue_15_duplicated_events.at("20130803")
    assert len(events) == 3
