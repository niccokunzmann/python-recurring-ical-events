
How to
======

Additionally to the examples listed here, you can have a look the 
`API documentation`_.
In the `Media Section`_, you can videos and useful information on social media.

.. _`API documentation`: ../reference/api.html
.. _`Media Section`: ../community/media.html

Read a file and print events
----------------------------

The following example loads a calendar from a file and
prints the events happening between the 1st of January 2017 and the 1st of January 2018.

.. code-block:: python

    >>> import icalendar
    >>> import recurring_ical_events
    >>> from pathlib import Path

    # read the calendar file and parse it
    # CALENDARS = Path("to/your/calendar/directory")
    >>> calendar_file : Path = CALENDARS / "fablab_cottbus.ics"
    >>> ical_string = calendar_file.read_bytes()
    >>> print(ical_string[:28])
    BEGIN:VCALENDAR
    VERSION:2.0
    >>> a_calendar = icalendar.Calendar.from_ical(ical_string)

    # request the events in a specific interval
    # start on the 1st of January 2017 0:00
    >>> start_date = (2017, 1, 1)

    # the event on the 1st of January 2018 is not included
    >>> end_date =   (2018,  1, 1)
    >>> events = recurring_ical_events.of(a_calendar).between(start_date, end_date)
    >>> for event in events:
    ...     start = event["DTSTART"].dt
    ...     summary = event["SUMMARY"]
    ...     print(f"start {start} summary {summary}")
    start 2017-03-11 17:00:00+01:00 summary Vereinssitzung
    start 2017-06-10 10:00:00+02:00 summary Repair und Recycling Café
    start 2017-06-11 16:30:00+02:00 summary Brandenburger Maker-Treffen
    start 2017-07-05 17:45:00+02:00 summary Der Computer-Treff fällt aus
    start 2017-07-29 14:00:00+02:00 summary Sommerfest
    start 2017-10-19 16:00:00+02:00 summary 3D-Modelle programmieren mit OpenSCAD
    start 2017-10-20 16:00:00+02:00 summary Programmier dir deine eigene Crypto-Währung
    start 2017-10-21 13:00:00+02:00 summary Programmiere deine eigene Wetterstation
    start 2017-10-22 13:00:00+02:00 summary Luftqualität: Ein Workshop zum selber messen (Einsteiger)
    start 2017-10-22 13:00:00+02:00 summary Websites selbst programmieren


List events at certain a time
-----------------------------

You can get all events which take place at ``a_date``.
A date can be a year, e.g. ``2023``, a month of a year e.g. January in 2023 ``(2023, 1)``, a day of a certain month e.g. ``(2023, 1, 1)``, an hour e.g. ``(2023, 1, 1, 0)``, a minute e.g. ``(2023, 1, 1, 0, 0)``, or second as well as a `datetime.date <https://docs.python.org/3/library/datetime.html#datetime.date>`_ object and `datetime.datetime <https://docs.python.org/3/library/datetime.html#datetime.datetime>`_.

The start and end are inclusive. As an example: if an event is longer than one day it is still included if it takes place at ``a_date``.

.. code-block:: python

    >>> import datetime

    # save the query object for the calendar
    >>> query = recurring_ical_events.of(a_calendar)
    >>> len(query.at(2023))                      # a year - 2023 has 12 events happening
    12
    >>> len(query.at((2023,)))                   # a year
    12
    >>> len(query.at((2023, 1)))                 # January in 2023 - only one event is in January
    1
    >>> len(query.at((2023, 1, 1)))              # the 1st of January in 2023
    0
    >>> len(query.at("20230101"))                # the 1st of January in 2023
    0
    >>> len(query.at((2023, 1, 1, 0)))           # the first hour of the year 2023
    0
    >>> len(query.at((2023, 1, 1, 0, 0)))        # the first minute in 2023
    0
    >>> len(query.at(datetime.date(2023, 1, 1))) # the first day in 2023
    0

The resulting ``events`` are a list of `icalendar events <https://icalendar.readthedocs.io/en/latest/api.html#icalendar.cal.Event>`_, see below.

List events within a time range
-------------------------------

``between(start, end)`` returns all events happening between a start and an end time. Both arguments can be `datetime.datetime`_, `datetime.date`_, tuples of numbers passed as arguments to `datetime.datetime`_ or strings in the form of
``%Y%m%d`` (``yyyymmdd``) and ``%Y%m%dT%H%M%SZ`` (``yyyymmddThhmmssZ``).
Additionally, the ``end`` argument can be a ``datetime.timedelta`` to express that the end is relative to the ``start``.
For examples of arguments, see ``at(a_date)`` above.

.. code-block:: python

    >>> query = recurring_ical_events.of(a_calendar)

    # What happens in 2016, 2017 and 2018?
    >>> events = recurring_ical_events.of(a_calendar).between(2016, 2019)
    >>> len(events) # quite a lot is happening!
    39

The resulting ``events`` are in a list of `icalendar events`_, see below.

List events after a certain time
--------------------------------

You can retrieve events that happen after a time or date using ``after(earliest_end)``.
Events that are happening during the ``earliest_end`` are included in the iteration.

.. code-block:: python

    >>> earlierst_end = 2023
    >>> for i, event in enumerate(query.after(earlierst_end)):
    ...     print(f"{event['SUMMARY']} ends {event['DTEND'].dt}") # all dates printed are after January 1st 2023
    ...     if i > 10: break  # we might get endless events and a lot of them!
    Repair Café ends 2023-01-07 17:00:00+01:00
    Repair Café ends 2023-02-04 17:00:00+01:00
    Repair Café ends 2023-03-04 17:00:00+01:00
    Repair Café ends 2023-04-01 17:00:00+02:00
    Repair Café ends 2023-05-06 17:00:00+02:00
    Repair Café ends 2023-06-03 17:00:00+02:00
    Repair Café ends 2023-07-01 17:00:00+02:00
    Repair Café ends 2023-08-05 17:00:00+02:00
    Repair Café ends 2023-09-02 17:00:00+02:00
    Repair Café ends 2023-10-07 17:00:00+02:00
    Repair Café ends 2023-11-04 17:00:00+01:00
    Repair Café ends 2023-12-02 17:00:00+01:00


List all events
---------------

If you wish to iterate over all occurrences of the components, then you can use ``all()``.
Since a calendar can define a huge amount of recurring entries, this method generates them
and forgets them, reducing memory overhead.

This example shows the first event that takes place in the calendar:

.. code-block:: python

    >>> first_event = next(query.all()) # not all events are generated
    >>> print(f"The first event is {first_event['SUMMARY']}")
    The first event is Weihnachts Repair-Café

Count events
------------

You can count occurrences of events and other components using ``count()``.

.. code-block:: python

    >>> number_of_TODOs = recurring_ical_events.of(a_calendar, components=["VTODO"]).count()
    >>> print(f"You have {number_of_TODOs} things to do!")
    You have 0 things to do!

    >>> number_of_journal_entries = recurring_ical_events.of(a_calendar, components=["VJOURNAL"]).count()
    >>> print(f"There are {number_of_journal_entries} journal entries in the calendar.")
    There are 0 journal entries in the calendar.

However, this can be very costly!

Split a query into pages
------------------------

Pagination allows you to chop the resulting components into chunks of a certain size.

.. code-block:: python

    # we get a calendar with 10 events and 2 events per page
    >>> ten_events = recurring_ical_events.example_calendar("event_10_times")
    >>> pages = recurring_ical_events.of(ten_events).paginate(2)

    # we can iterate over the pages with 2 events each
    >>> for i, last_page in enumerate(pages):
    ...     print(f"page: {i}")
    ...     for event in last_page:
    ...         print(f"->  {event.start}")
    ...     if i == 1: break
    page: 0
    ->  2020-01-13 07:45:00+01:00
    ->  2020-01-14 07:45:00+01:00
    page: 1
    ->  2020-01-15 07:45:00+01:00
    ->  2020-01-16 07:45:00+01:00

If you run a web service and you would like to continue pagination after a certain page,
this can be done, too. Just hand someone the ``next_page_id`` and continue from there on.

.. code-block:: python

    # resume the same query from the next page
    >>> pages = recurring_ical_events.of(ten_events).paginate(2, next_page_id = last_page.next_page_id)
    >>> for i, last_page in enumerate(pages):
    ...     print(f"page: {i + 2}")
    ...     for event in last_page:
    ...         print(f"->  {event.start}")
    ...     if i == 1: break
    page: 2
    ->  2020-01-17 07:45:00+01:00
    ->  2020-01-18 07:45:00+01:00
    page: 3
    ->  2020-01-19 07:45:00+01:00
    ->  2020-01-20 07:45:00+01:00

The ``last_page.next_page_id`` is a string so that it can be used easily.
It is tested against malicious modification and can safely be passed from a third party source.

Additionally to the page size, you can also pass a ``start`` and an ``end`` to the pages so that
all components are visible within that time.

Get Todos and Journal entries
-----------------------------

By default the ``recurring_ical_events`` only selects events as the name already implies.
However, there are different `components <https://icalendar.readthedocs.io/en/latest/api.html#icalendar.cal.Component>`_ available in a `calendar <https://icalendar.readthedocs.io/en/latest/api.html#icalendar.cal.Calendar>`_.
You can select which components you like to have returned by passing ``components`` to the ``of`` function:

.. code-block:: python

    of(a_calendar, components=["VEVENT"])

Here is a template code for choosing the supported types of components:

.. code-block:: python

    >>> query_events = recurring_ical_events.of(a_calendar)
    >>> query_journals = recurring_ical_events.of(a_calendar, components=["VJOURNAL"])
    >>> query_todos = recurring_ical_events.of(a_calendar, components=["VTODO"])
    >>> query_all = recurring_ical_events.of(a_calendar, components=["VTODO", "VEVENT", "VJOURNAL"])

If a type of component is not listed here, it can be added.
Please create an issue for this in the source code repository.

For further customization, please refer to the section on how to extend the default functionality.

Calculate Alarm times
---------------------

Alarms are subcomponents of events and todos. They only make sense with an event or todo.
Thus the interface is slightly different.

Add ``VALARM`` as the component you would like:

.. code-block:: python

    >>> query_alarms = recurring_ical_events.of(a_calendar, components=["VALARM"])

In the following example, an event has an alarm one week before it starts.
The component returned is not a ``VALARM`` component but instead the ``VEVENT`` with only
one ``VALARM`` in it.

.. code-block:: python

    # read an .ics file with an event with an alarm
    >>> calendar_with_alarm = recurring_ical_events.example_calendar("alarm_1_week_before_event")
    >>> alarm_day = datetime.date(2024, 12, 2)

    # we get the event that has an alarm on that day
    >>> event = recurring_ical_events.of(calendar_with_alarm, components=["VALARM"]).at(alarm_day)[0]
    >>> len(event.alarms.times)
    1
    >>> alarm = event.alarms.times[0]

    # the alarm happens one week before the event
    >>> event.start - alarm.trigger
    datetime.timedelta(days=7)

In the following code, we query the same day for a ``VEVENT`` component and we find nothing.
The event happens a week later.

.. code-block:: python

    # No events on that day. There is only an alarm.
    >>> recurring_ical_events.of(calendar_with_alarm, components=["VEVENT"]).at(alarm_day)
    []

When querying events and todos, they keep their alarms and other subcompnents.
These alarm times can be outside of the dates requested.

In this example, we get an event and find that it has several alarms in it.

.. code-block:: python

    >>> event_day = alarm_day + datetime.timedelta(days=7)
    >>> event = recurring_ical_events.of(calendar_with_alarm, components=["VEVENT"]).at(event_day)[0]

    # The event a week later has more than one alarm.
    >>> len(event.walk("VALARM"))
    2


Edit one event of an existing series
------------------------------------

Editing one event of a series is necessary for calendar invites e.g. via email.

Below, you see how to edit an event that occurs in a series.
It is important that you increase the `sequence number <https://www.rfc-editor.org/rfc/rfc5545#section-3.8.7.4>`_
of the event to indicate the new version.

.. code-block:: python

    >>> calendar = recurring_ical_events.example_calendar("recurring_events_moved")
    >>> event = recurring_ical_events.of(calendar).at("20190309")[0]

    # This event happens on 2019-03-09.
    >>> print(event["SUMMARY"])
    New Event

    # The event can be modified.
    >>> event["SUMMARY"] = "Modified Again!"

    # Make sure to increase the sequence number!
    # If you do not do that, the modification will not appear.
    >>> event["SEQUENCE"] = event.get("SEQUENCE", 0) + 1

    # Add the modified event to the calendar to replace the original.
    >>> calendar.add_component(event)

    # Get the day again and see the modified event.
    >>> event = recurring_ical_events.of(calendar).at("20190309")[0]
    >>> print(event["SUMMARY"])
    Modified Again!


Extend ``recurring-ical-events``
--------------------------------

All the functionality of ``recurring-ical-events`` can be extended and modified.
To understand where to extend, have a look at the `Architecture <../reference/architecture.html>`_.

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


Increase Performance
--------------------

If you use :meth:`recurring_ical_events.CalendarQuery.between` and other queries
several times, it is faster to re-use the object coming from :func:`recurring_ical_events.of`.

.. code-block:: python

    >>> query = recurring_ical_events.of(a_calendar)
    >>> events_of_day_1 = query.at((2019, 2, 1))
    >>> events_of_day_2 = query.at((2019, 2, 2))
    >>> events_of_day_3 = query.at((2019, 2, 3))

    # ... and so on


Skip badly formatted ical events
--------------------------------

Some events may be badly formatted and therefore cannot be handled by ``recurring-ical-events``.
Passing ``skip_bad_series=True`` as ``of()`` argument will totally skip theses events.

.. code-block:: python

    # Create a calendar that contains broken events.
    >>> calendar_file = CALENDARS / "bad_rrule_missing_until_event.ics"
    >>> calendar_with_bad_event = icalendar.Calendar.from_ical(calendar_file.read_bytes())

     # By default, broken events result in errors.
    >>> recurring_ical_events.of(calendar_with_bad_event, skip_bad_series=False).count()
    Traceback (most recent call last):
      ...
    recurring_ical_events.errors.BadRuleStringFormat: UNTIL parameter is missing: FREQ=WEEKLY;BYDAY=TH;WKST=SU;UNTL=20191023

    # With skip_bad_series=True we skip the series that we cannot handle.
    >>> recurring_ical_events.of(calendar_with_bad_event, skip_bad_series=True).count()
    0
