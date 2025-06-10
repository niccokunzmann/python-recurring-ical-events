from datetime import datetime

import pytest

from recurring_ical_events.errors import PeriodEndBeforeStart
from recurring_ical_events.util import time_span_contains_event


def test_span_in_wrong_order():
    """The timespan only works if the order is correct."""
    with pytest.raises(PeriodEndBeforeStart):
        time_span_contains_event(
            datetime(2019, 10, 13),
            datetime(2019, 10, 12),
            datetime(2019, 10, 13),
            datetime(2019, 10, 14),
        )


def test_event_in_wrong_order():
    """The timespan only works if the order is correct."""
    with pytest.raises(PeriodEndBeforeStart):
        time_span_contains_event(
            datetime(2019, 10, 11),
            datetime(2019, 10, 12),
            datetime(2019, 10, 15),
            datetime(2019, 10, 14),
        )
