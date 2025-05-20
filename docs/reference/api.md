---
myst:
  html_meta:
    "description lang=en": |
      API Reference of functions and classes.
---


# API Reference

This is the public API for this library.

## Core functionality

This is the core of the functionality of the library.

The first step is to customize which components to query with {py:func}`recurring_ical_events.of`.

```{eval-rst}
.. autofunction:: recurring_ical_events.of 
```

## Query

`of()` returns a {py:class}`recurring_ical_events.CalendarQuery` object, which can be used to query the calendar.
For the most common cases, you do not need to look any further.

```{eval-rst}
.. autoclass:: recurring_ical_events.CalendarQuery
    :members:
    :exclude-members: ComponentsWithName
```

### list from `at()` and `between()`

The result of both {py:meth}`recurring_ical_events.CalendarQuery.between` and
{py:meth}`recurring_ical_events.CalendarQuery.at` is a list of {py:class}`icalendar.cal.Component`
objects like {py:class}`icalendar.cal.Event`.
By default, all attributes of the event with repetitions are copied, like ``UID`` and ``SUMMARY``.
However, these attributes may differ from the source event:

* ``DTSTART`` which is the start of the event instance. (always present)
* ``DTEND`` which is the end of the event instance. (always present)
* ``RDATE``, ``EXDATE``, ``RRULE`` are the rules to create event repetitions.
  They are **not** included in repeated events, see [Issue 23].
  To change this, use ``of(calendar, keep_recurrence_attributes=True)``.

[Issue 23]: https://github.com/niccokunzmann/python-recurring-ical-events/issues/23

### Generator from `after()` and `all()`

If the resulting components are ordered when {py:meth}`recurring_ical_events.CalendarQuery.after` or 
{py:meth}`recurring_ical_events.CalendarQuery.all` is used.
The result is an iterator that returns the events in order.

```python
for event in recurring_ical_events.of(an_icalendar_object).after(datetime.datetime.now()):
    print(event["DTSTART"]) # The start is ordered
```

## Timezones and floating time

This library makes a distinction between floating time and times with timezones.

Examples:

* Event 1 happes at 12:00 in Singapore and event 2 on the same day at 12:00 in New York.

  * If you query that day without timezone, you will get both events.
  * If you query 12:00 - 13:00 without timezone, you will get both events.
  * If you query 12:00 - 13:00 in `Asia/Singapore`, you will only get event 1.
  * If you query 12:00 - 13:00 in `America/New_York`, you will only get event 2.

* If an event happens at night in floating time (without timezone) and
  you query that day it will appear regardless of the timezone of the query.
  Which is at different times in different timezones.

* {py:class}`icalendar.cal.Alarm` has a `TRIGGER` which is in UTC.
  The timezone to compute that for alarms relative to floating events will be taken
  from the start and stop arguments.

## Pagination

For ease of use, pagination has been introduced.
These are the pages returned by the query.

```{eval-rst}
.. automodule:: recurring_ical_events.pages
    :members:
```

## Complete API

```{eval-rst}

.. automodule:: recurring_ical_events
    :show-inheritance:
    :members:
    :exclude-members: CalendarQuery, of, OccurrenceID

.. automodule:: recurring_ical_events.types
    :members:

.. autoclass:: recurring_ical_events.OccurrenceID

  .. automethod:: to_string
  .. automethod:: from_string
  .. automethod:: from_occurrence

```
