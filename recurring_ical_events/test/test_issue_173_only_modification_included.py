"""Calendars do not only contain events with an RRULE but they can contain recurrences without
any RRULE in them.

I assume this can happen for example when one accepts a calendar invitation of
one instance of an recurring event.

See https://github.com/niccokunzmann/python-recurring-ical-events/issues/173
"""


def test_event_can_be_found_in_the_right_time(calendars):
    """The event reported should be present in the calculations."""
    events = calendars.issue_173_only_modifications_error.at("20240108")
    assert len(events) >= 1
    uid = "_6krj2dhl74q34b9j60sj4b9k8h238b9p6gok2ba68gojgchl6cpj0h1o88_R20231009T130000@google.com"
    assert any(event["UID"] == uid for event in events)
