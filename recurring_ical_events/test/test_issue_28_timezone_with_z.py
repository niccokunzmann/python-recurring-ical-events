"""These tests are for Issue 28
https://github.com/niccokunzmann/python-recurring-ical-events/issues/28

"""


def test_expected_amount_of_events(calendars):
    events = calendars.issue_28_rrule_with_UTC_endinginZ.between(
        (2020, 5, 25),
        (2020, 9, 5),
    )
    assert len(events) == 15, (
        "Microsoft Outlook online imports this calendar and shows that there are 15 events."
    )


def test_modification_of_event(calendars):
    events = calendars.issue_28_rrule_with_UTC_endinginZ.between(
        (2020, 9, 3),
        (2020, 9, 5),
    )
    assert len(events) == 1, "Microsoft Outlook online shows one event moved."
