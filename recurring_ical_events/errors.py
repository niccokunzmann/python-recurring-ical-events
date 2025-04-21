"""All the errors."""

from recurring_ical_events.types import Time


class InvalidCalendar(ValueError):
    """Exception thrown for bad icalendar content."""

    def __init__(self, message: str):
        """Create a new error with a message."""
        self._message = message
        super().__init__(self.message)

    @property
    def message(self) -> str:
        """The error message."""
        return self._message


class PeriodEndBeforeStart(InvalidCalendar):
    """An event or component starts before it ends."""

    def __init__(self, message: str, start: Time, end: Time):
        """Create a new PeriodEndBeforeStart error."""
        super().__init__(message)
        self._start = start
        self._end = end

    @property
    def start(self) -> Time:
        """The start of the component's period."""
        return self._start

    @property
    def end(self) -> Time:
        """The end of the component's period."""
        return self._end


class BadRuleStringFormat(InvalidCalendar):
    """An iCal rule string is badly formatted."""

    def __init__(self, message: str, rule: str):
        """Create an error with a bad rule string."""
        super().__init__(message + ": " + rule)
        self._rule = rule

    @property
    def rule(self) -> str:
        """The malformed rule string"""
        return self._rule


__all__ = ["BadRuleStringFormat", "InvalidCalendar", "PeriodEndBeforeStart"]
