Recurring ICal events for Python
================================

.. image:: https://github.com/niccokunzmann/python-recurring-ical-events/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/niccokunzmann/python-recurring-ical-events/actions/workflows/tests.yml
   :alt: GitHub CI build and test status
.. image:: https://badge.fury.io/py/recurring-ical-events.svg
   :target: https://pypi.python.org/pypi/recurring-ical-events
   :alt: Python Package Version on Pypi
.. image:: https://img.shields.io/pypi/dm/recurring-ical-events.svg
   :target: https://pypi.org/project/recurring-ical-events/#files
   :alt: Downloads from Pypi
.. image:: https://img.shields.io/opencollective/all/open-web-calendar?label=support%20on%20open%20collective
   :target: https://opencollective.com/open-web-calendar/
   :alt: Support on Open Collective
.. image:: https://img.shields.io/github/issues/niccokunzmann/python-recurring-ical-events?logo=github&label=issues%20seek%20funding&color=%230062ff
   :target: https://polar.sh/niccokunzmann/python-recurring-ical-events
   :alt: issues seek funding



ICal has some complexity to it:
Events, TODOs, Journal entries and Alarms can be repeated, removed from the feed and edited later on.
This tool takes care of these circumstances.

Let's put our expertise together and build a tool that can solve this!

.. image:: https://img.shields.io/badge/RFC_2445-deprecated-red
   :target: https://datatracker.ietf.org/doc/html/rfc2445#section-4.8.5.2
   :alt: RFC 2445 is deprecated
.. image:: https://img.shields.io/badge/RFC_5545-supported-green
   :target: https://datatracker.ietf.org/doc/html/rfc5545
   :alt: RFC 5545 is supported
.. image:: https://img.shields.io/badge/RFC_7529-todo-red
   :target: https://github.com/niccokunzmann/python-recurring-ical-events/issues/142
   :alt: RFC 7529 is not implemented
.. image:: https://img.shields.io/badge/RFC_7953-todo-red
   :target: https://github.com/niccokunzmann/python-recurring-ical-events/issues/143
   :alt: RFC 7953 is not implemented

* day light saving time (DONE)
* recurring events (DONE)
* recurring events with edits (DONE)
* recurring events where events are omitted (DONE)
* recurring events events where the edit took place later (DONE)
* normal events (DONE)
* recurrence of dates but not hours, minutes, and smaller (DONE)
* endless recurrence (DONE)
* ending recurrence (DONE)
* events with start date and no end date (DONE)
* events with start as date and start as datetime (DONE)
* `RRULE <https://www.kanzaki.com/docs/ical/rrule.html>`_ (DONE)
* events with multiple RRULE (DONE)
* `RDATE <https://www.kanzaki.com/docs/ical/rdate.html>`_ (DONE)
* `DURATION <https://www.kanzaki.com/docs/ical/duration.html>`_ (DONE)
* `EXDATE <https://www.kanzaki.com/docs/ical/exdate.html>`_ (DONE)
* `X-WR-TIMEZONE` compatibilty (DONE)
* non-gregorian event repetitions (TODO)
* RECURRENCE-ID with THISANDFUTURE - modify all future events (DONE)

Not included:

* EXRULE (deprecated), see `8.3.2.  Properties Registry
  <https://tools.ietf.org/html/rfc5545#section-8.3.2>`_


Usage
-----

Example
-------

.. code-block:: python






Architecture
------------

.. image:: img/architecture.png
   :alt: Architecture Diagram showing the components interacting

Each icalendar **Calendar** can contain Events, Journal entries,
TODOs and others, called **Components**.
Those entries are grouped by their ``UID``.
Such a ``UID`` defines a **Series** of **Occurrences** that take place at
a given time.
Since each **Component** is different, the **ComponentAdapter** offers a unified
interface to interact with them.
The **Calendar** gets filtered and for each ``UID``,
a **Series** can use one or more **ComponentAdapters** to create 
**Occurrences** of what happens in a time span.
These **Occurrences** are used internally and convert to **Components** for further use.

Extending ``recurring-ical-events``
***********************************

All the functionality of ``recurring-ical-events`` can be extended and modified.
To understand where to extend, have a look at the `Architecture`_.

The first place for extending is the collection of components.
Components are collected into a ``Series``.
A series belongs together because all components have the same ``UID``.
In this example, we collect one VEVENT which matches a certain UID:

.. code-block:: python

    >>> from recurring_ical_events import SelectComponents, EventAdapter, Series
    >>> from icalendar.cal import Component
    >>> from typing import Sequence

    # create the calendar
    >>> calendar_file = CALENDARS / "machbar_16_feb_2019.ics"
    >>> machbar_calendar = icalendar.Calendar.from_ical(calendar_file.read_bytes())

    # Create a collector of components that searches for an event with a specific UID
    >>> class CollectOneUIDEvent(SelectComponents):
    ...     def __init__(self, uid:str) -> None:
    ...         self.uid = uid
    ...     def collect_series_from(self, source: Component, suppress_errors: tuple) -> Sequence[Series]:
    ...         components : list[Component] = []
    ...         for component in source.walk("VEVENT"):
    ...             if component.get("UID") == self.uid:
    ...                 components.append(EventAdapter(component))
    ...         return [Series(components)] if components else []

    # collect only one UID: 4mm2ak3in2j3pllqdk1ubtbp9p@google.com
    >>> one_uid = CollectOneUIDEvent("4mm2ak3in2j3pllqdk1ubtbp9p@google.com")
    >>> uid_query = recurring_ical_events.of(machbar_calendar, components=[one_uid])
    >>> uid_query.count()  # the event has no recurrence and thus there is only one
    1

Several ways of extending the functionality have been created to override internals.
These can be subclassed or composed.

Below, you can choose to collect all components. Subclasses can be created for the
``Series`` and the ``Occurrence``. 

.. code-block:: python

    >>> from recurring_ical_events import AllKnownComponents, Series, Occurrence

    # we create a calendar with one event
    >>> calendar_file = CALENDARS / "one_event.ics"
    >>> one_event = icalendar.Calendar.from_ical(calendar_file.read_bytes())

    # You can override the Occurrence and Series classes for all computable components
    >>> select_all_known = AllKnownComponents(series=Series, occurrence=Occurrence)
    >>> select_all_known.names  # these are the supported types of components
    ['VALARM', 'VEVENT', 'VJOURNAL', 'VTODO']
    >>> query_all_known = recurring_ical_events.of(one_event, components=[select_all_known])

    # There should be exactly one event.
    >>> query_all_known.count()
    1

This example shows that the behavior for specific types of components can be extended.
Additional to the series, you can change the ``ComponentAdapter`` that provides
a unified interface for all the components with the same name (``VEVENT`` for example).

.. code-block:: python

    >>> from recurring_ical_events import ComponentsWithName, EventAdapter, JournalAdapter, TodoAdapter

    # You can also choose to select only specific subcomponents by their name.
    # The default arguments are added to show the extensibility.
    >>> select_events =   ComponentsWithName("VEVENT",   adapter=EventAdapter,   series=Series, occurrence=Occurrence)
    >>> select_todos =    ComponentsWithName("VTODO",    adapter=TodoAdapter,    series=Series, occurrence=Occurrence)
    >>> select_journals = ComponentsWithName("VJOURNAL", adapter=JournalAdapter, series=Series, occurrence=Occurrence)

    # There should be one event happening and nothing else
    >>> recurring_ical_events.of(one_event, components=[select_events]).count()
    1
    >>> recurring_ical_events.of(one_event, components=[select_todos]).count()
    0
    >>> recurring_ical_events.of(one_event, components=[select_journals]).count()
    0

So, if you would like to modify all events that are returned by the query,
you can do that subclassing the ``Occurrence`` class.


.. code-block:: python

    # This occurence changes adds a new attribute to the resulting events
    >>> class MyOccurrence(Occurrence):
    ...     """An occurrence that modifies the component."""
    ...     def as_component(self, keep_recurrence_attributes: bool) -> Component:
    ...         """Return a shallow copy of the source component and modify some attributes."""
    ...         component = super().as_component(keep_recurrence_attributes)
    ...         component["X-MY-ATTRIBUTE"] = "my occurrence"
    ...         return component
    >>> query = recurring_ical_events.of(one_event, components=[ComponentsWithName("VEVENT", occurrence=MyOccurrence)])
    >>> event = next(query.all())
    >>> event["X-MY-ATTRIBUTE"]
    'my occurrence'

This library allows extension of functionality during the selection of components to calculate using these classes:

* ``ComponentsWithName`` - for components of a certain name
* ``AllKnownComponents`` - for all components known
* ``SelectComponents`` - the interface to provide

You can further customize behaviour by subclassing these:

* ``ComponentAdapter`` such as ``EventAdapter``, ``JournalAdapter`` or ``TodoAdapter``.
* ``Series``
* ``Occurrence``
* ``CalendarQuery``

Version Fixing
**************

If you use this library in your code, you may want to make sure that
updates can be received but they do not break your code.
The version numbers are handeled this way: ``a.b.c`` example: ``0.1.12``

- ``c`` is changed for each minor bug fix.
- ``b`` is changed whenever new features are added.
- ``a`` is changed when the interface or major assumptions change that may break your code.

So, I recommend to version-fix this library to stay with the same ``a``
while ``b`` and ``c`` can change.


