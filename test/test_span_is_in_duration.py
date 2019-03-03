from recurring_ical_events import time_span_contains_event
import pytest

@pytest.mark.parametrize(
    "span_start,span_stop,event_start,event_stop,"
    "include_start,include_stop,result,message", [

    (0, 5, 1, 3, True, True, True, "event lies inside 1"),
    (0, 5, 1, 3, False, True, True, "event lies inside 2"),
    (0, 5, 1, 3, True, False, True, "event lies inside 3"),
    (0, 5, 1, 3, False, False, True,"event lies inside 4"),

    (0, 5, -3, -1, True, True, False, "event lies before 1"),
    (0, 5, -3, -1, False, True, False, "event lies before 2"),
    (0, 5, -3, -1, True, False, False, "event lies before 3"),
    (0, 5, -3, -1, False, False, False, "event lies before 4"),

    (0, 5, 34, 41, True, True, False, "event lies after 1"),
    (0, 5, 34, 41, False, True, False, "event lies after 2"),
    (0, 5, 34, 41, True, False, False, "event lies after 3"),
    (0, 5, 34, 41, False, False, False, "event lies after 4"),

    (0, 5, 4, 6, True, True, True, "event overlaps end 1"),
    (0, 5, 4, 6, False, True, True, "event overlaps end 2"),
    (0, 5, 4, 6, True, False, False, "event overlaps end 3"),
    (0, 5, 4, 6, False, False, False, "event overlaps end 4"),

    (0, 5, -1, 2, True, True, True, "event overlaps start 1"),
    (0, 5, -1, 2, False, True, False, "event overlaps start 2"),
    (0, 5, -1, 2, True, False, True, "event overlaps start 3"),
    (0, 5, -1, 2, False, False, False, "event overlaps start 4"),

    (0, 5, 0, 4, True, True, True, "event begins at start 1"),
    (0, 5, 0, 4, False, True, True, "event begins at start 2"),
    (0, 5, 0, 4, True, False, True, "event begins at start 3"),
    (0, 5, 0, 4, False, False, True, "event begins at start 4"),

    (0, 5, 1, 5, True, True, True, "event ends at end 1"),
    (0, 5, 1, 5, False, True, True, "event ends at end 2"),
    (0, 5, 1, 5, True, False, True, "event ends at end 3"),
    (0, 5, 1, 5, False, False, True, "event ends at end 4"),
])
def test_time_span_inclusion(
    span_start, span_stop, event_start, event_stop, include_start, include_stop,
    result, message):
    assert time_span_contains_event(
        span_start, span_stop, event_start, event_stop,
        include_start, include_stop
        ) == result, message
