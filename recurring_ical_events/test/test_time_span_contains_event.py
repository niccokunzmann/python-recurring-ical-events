from datetime import date, datetime

import pytest
from pytz import timezone, utc

from recurring_ical_events.errors import PeriodEndBeforeStart
from recurring_ical_events.util import time_span_contains_event

berlin = timezone("Europe/Berlin").localize


@pytest.mark.parametrize(
    ("span_start", "span_stop", "event_start", "event_stop", "result", "message"),
    [
        (0, 5, 1, 3, True, "event lies inside"),
        (0, 5, -3, -1, False, "event lies before"),
        (0, 5, 34, 41, False, "event lies after "),
        (0, 5, 4, 6, True, "event overlaps end"),
        (0, 5, -1, 2, True, "event overlaps start"),
        (0, 5, -1, 7, True, "event overlaps start and end"),
        (0, 5, 0, 4, True, "event begins at start"),
        (0, 5, 1, 5, True, "event ends at end"),
        # check that datetime and date can be used and mixed
        (
            datetime(2019, 1, 1, 1),
            datetime(2019, 1, 4, 1),
            date(2019, 1, 2),
            date(2019, 1, 3),
            True,
            "date is in datetime span",
        ),
        (
            date(2019, 1, 3),
            date(2019, 1, 4),
            date(2019, 1, 2),
            date(2019, 1, 3),
            False,
            "date is before span",
        ),
        (
            date(2019, 1, 4),
            date(2019, 1, 4),
            datetime(2019, 1, 2, 1),
            datetime(2019, 1, 4),
            False,
            "datetime is before date span start",
        ),
        (
            date(2019, 1, 4),
            date(2019, 1, 5),
            datetime(2019, 1, 4, 1),
            datetime(2019, 1, 4, 2),
            True,
            "datetime is in date span end",
        ),
        (
            berlin(datetime(2019, 1, 1, 1)),
            berlin(datetime(2019, 1, 4, 2)),
            datetime(2019, 1, 4, 1, 10),
            datetime(2019, 1, 4, 1, 20),
            True,
            "without time zone is put into time zone",
        ),
        (
            berlin(datetime(2019, 1, 1, 1)),
            berlin(datetime(2019, 1, 1, 2)),
            datetime(2019, 1, 1, 0, tzinfo=utc),
            datetime(2019, 1, 1, 1, tzinfo=utc),
            True,
            "comparing times from different time zones 1",
        ),
        (
            berlin(datetime(2019, 1, 1, 4)),
            berlin(datetime(2019, 1, 1, 5)),
            datetime(2019, 1, 1, 0, tzinfo=utc),
            datetime(2019, 1, 1, 1, tzinfo=utc),
            False,
            "comparing times from different time zones 2",
        ),
        # The end of the VEVENT is exclusive, see RFC5545
        #    Note that the "DTEND" property is
        #    set to July 9th, 2007, since the "DTEND" property specifies the
        #    non-inclusive end of the event.
        #
        # Tests:
        # - We should not include an event which ends at a requested start date.
        # - We should include an event which ends at an end date but is included
        #  in the range.
        (
            date(2019, 1, 4),
            date(2019, 1, 5),
            date(2019, 1, 3),
            date(2019, 1, 4),
            False,
            "We should not include an event which ends at a requested start date.",
        ),
        (
            datetime(2019, 1, 4),
            datetime(2019, 1, 5),
            date(2019, 1, 3),
            date(2019, 1, 4),
            False,
            "We should not include an event which ends at a requested start date.",
        ),
        (
            datetime(2019, 1, 4),
            datetime(2019, 1, 5),
            datetime(2019, 1, 4, 3),
            datetime(2019, 1, 5),
            True,
            "We should include an event which ends at an end date but is included",
        ),
        # Events with 0 duration should be tested
        (0, 1, 0, 0, True, "zero size event at start"),
        (0, 2, 1, 1, True, "zero size event in middle"),
        (0, 1, 1, 1, False, "zero size event at end"),
        (1, 1, 1, 1, True, "zero size event at zero size span"),
        (
            date(2019, 1, 4),
            date(2019, 1, 4),
            date(2019, 1, 4),
            date(2019, 1, 4),
            True,
            "We should include an event which is of the same size as the span",
        ),
        (
            date(2019, 1, 3),
            date(2019, 1, 4),
            date(2019, 1, 4),
            date(2019, 1, 4),
            False,
            "We should NOT include an event which ends at an end date but is included",
        ),
        (0, 0, 1, 1, False, "zero size event after"),
        (2, 2, 1, 1, False, "zero size event before"),
        # Test the exclusivity of the end of the span
        (
            1,
            3,
            3,
            4,
            False,
            "When the event starts at the end of the span, it should not be included.",
        ),
        # Test zero size spans
        (1, 1, 0, 0, False, "zero size event before zero size span"),
        (1, 1, 0, 1, False, "event ending at zero size span"),
        (1, 1, 0, 2, True, "event around zero size span"),
        (1, 1, 1, 2, True, "event starting at zero size span"),
        (1, 1, 2, 3, False, "event after zero size span"),
        (1, 1, 2, 2, False, "zero size event after zero size span"),
    ],
)
def test_time_span_inclusion(
    span_start, span_stop, event_start, event_stop, result, message
):
    assert (
        time_span_contains_event(
            span_start,
            span_stop,
            event_start,
            event_stop,
        )
        == result
    ), message


@pytest.mark.parametrize(
    ("span_start", "span_stop", "event_start", "event_stop", "exception_message"),
    [
        (1, 2, 1, 2, None),
        (1, 1, 1, 1, None),
        (1, 2, 2, 1, r"^the event"),
        (2, 1, 1, 2, r"^the time span"),
        (date(2024, 4, 4), date(2024, 4, 4), date(2024, 4, 4), date(2024, 4, 4), None),
        (date(2024, 4, 4), date(2024, 4, 5), date(2024, 4, 4), date(2024, 4, 5), None),
        (
            date(2024, 4, 4),
            date(2024, 4, 5),
            date(2024, 4, 5),
            date(2024, 4, 4),
            r"^the event",
        ),
        (
            date(2024, 4, 5),
            date(2024, 4, 4),
            date(2024, 4, 4),
            date(2024, 4, 5),
            r"^the time span",
        ),
        (
            datetime(2024, 4, 4),
            datetime(2024, 4, 4),
            datetime(2024, 4, 4),
            datetime(2024, 4, 4),
            None,
        ),
        (
            datetime(2024, 4, 4),
            datetime(2024, 4, 5),
            datetime(2024, 4, 4),
            datetime(2024, 4, 5),
            None,
        ),
        (
            datetime(2024, 4, 4),
            datetime(2024, 4, 5),
            datetime(2024, 4, 5),
            datetime(2024, 4, 4),
            r"^the event",
        ),
        (
            datetime(2024, 4, 5),
            datetime(2024, 4, 4),
            datetime(2024, 4, 4),
            datetime(2024, 4, 5),
            r"^the time span",
        ),
    ],
)
def test_time_span_end_before_start_raise_exception(
    span_start, span_stop, event_start, event_stop, exception_message
):
    if exception_message:
        with pytest.raises(PeriodEndBeforeStart, match=exception_message):
            time_span_contains_event(span_start, span_stop, event_start, event_stop)
    else:
        time_span_contains_event(span_start, span_stop, event_start, event_stop)
