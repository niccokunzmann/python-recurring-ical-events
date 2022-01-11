Recurring ICal events for Python
================================

.. image:: https://app.travis-ci.com/niccokunzmann/python-recurring-ical-events.svg?branch=master
   :target: https://app.travis-ci.com/github/niccokunzmann/python-recurring-ical-events
   :alt: Travis Build and Tests Status

.. image:: https://badge.fury.io/py/recurring-ical-events.svg
   :target: https://pypi.python.org/pypi/recurring-ical-events
   :alt: Python Package Version on Pypi

.. image:: https://img.shields.io/pypi/dm/recurring-ical-events.svg
   :target: https://pypi.python.org/pypi/recurring-ical-events#downloads
   :alt: Downloads from Pypi


ICal has some complexity to it:
Events can be repeated, removed from the feed and edited later on.
This tool takes care of these circumstances.

Let's put our expertise together and build a tool that can solve this!

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
* `RDATE <https://www.kanzaki.com/docs/ical/rdate.html>`_ (DONE)
* `DURATION <https://www.kanzaki.com/docs/ical/duration.html>`_ (DONE)
* `EXDATE <https://www.kanzaki.com/docs/ical/exdate.html>`_ (DONE)

Not included:

* EXRULE (deprecated), see `8.3.2.  Properties Registry
  <https://tools.ietf.org/html/rfc5545#section-8.3.2>`_
* ``X-WR-TIMEZONE`` support at the moment, see `Issue 71 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/71>`_.

Installation
------------

.. code:: shell

    pip install recurring-ical-events

Example
-------

.. code-block:: python

    import icalendar
    import recurring_ical_events
    import urllib.request

    start_date = (2019, 3, 5)
    end_date =   (2019, 4, 1)
    url = "http://tinyurl.com/y24m3r8f"

    ical_string = urllib.request.urlopen(url).read()
    calendar = icalendar.Calendar.from_ical(ical_string)
    events = recurring_ical_events.of(calendar).between(start_date, end_date)
    for event in events:
        start = event["DTSTART"].dt
        duration = event["DTEND"].dt - event["DTSTART"].dt
        print("start {} duration {}".format(start, duration))

Output:

.. code-block:: text

    start 2019-03-18 04:00:00+01:00 duration 1:00:00
    start 2019-03-20 04:00:00+01:00 duration 1:00:00
    start 2019-03-19 04:00:00+01:00 duration 1:00:00
    start 2019-03-07 02:00:00+01:00 duration 1:00:00
    start 2019-03-08 01:00:00+01:00 duration 2:00:00
    start 2019-03-09 03:00:00+01:00 duration 0:30:00
    start 2019-03-10 duration 1 day, 0:00:00


Usage
-----

The `icalendar <https://pypi.org/project/icalendar/>`_ module is responsible for parsing and converting calendars.
The `recurring_ical_events <https://pypi.org/project/recurring-ical-events/>`_ module uses such a calendar and creates all repetitions of its events within a time span.

To import this module, write 

.. code:: Python

    import recurring_ical_events

There are several methods you can use to unfold repeating events, such as ``at(a_time)`` and ``between(a_start, an_end)``.

``at(a_date)``
**************

You can get all events which take place at ``a_date``.
A date can be a year, e.g. ``2023``, a month of a year e.g. January in 2023 ``(2023, 1)``, a day of a certain month e.g. ``(2023, 1, 1)``, an hour e.g. ``(2023, 1, 1, 0)``, a minute e.g. ``(2023, 1, 1, 0, 0)``, or second as well as a `datetime.date <https://docs.python.org/3/library/datetime.html#datetime.date>`_ object and `datetime.datetime <https://docs.python.org/3/library/datetime.html#datetime.datetime>`_.

The start and end are inclusive. As an example: if an event is longer than one day it is still included if it takes place at ``a_date``.

.. code:: Python

    a_date =  2023   # a year
    a_date = (2023,) # a year
    a_date = (2023, 1) # January in 2023
    a_date = (2023, 1, 1) # the 1st of January in 2023
    a_date = "20230101"   # the 1st of January in 2023
    a_date = (2023, 1, 1, 0) # the first hour of the year 2023
    a_date = (2023, 1, 1, 0, 0) # the first minute in 2023
    a_date = datetime.date(2023) # the first day in 2023
    a_date = datetime.date(2023, 1, 1) # the first day in 2023
    a_date = datetime.datetime.now() # this exact second
    
    events = recurring_ical_events.of(an_icalendar_object).at(a_date)

The resulting ``events`` are a list of icalendar events, see below.

``between(start, end)``
***********************

``between(start, end)`` returns all events happening between a start and an end time. Both arguments can be `datetime.datetime`_, `datetime.date`_, tuples of numbers passed as arguments to `datetime.datetime`_ or strings in the form of
``%Y%m%d`` (``yyyymmdd``) and ``%Y%m%dT%H%M%SZ`` (``yyyymmddThhmmssZ``).
For examples, see ``at(a_date)`` above.

.. code:: Python

    events = recurring_ical_events.of(an_icalendar_object).between(start, end)

The resulting ``events`` are in a list, see below.

``events`` as list
******************

The result of both ``between(start, end)`` and ``at(a_date)`` is a list of `icalendar`_ events.
By default, all attributes of the event with repetitions are copied, like UID and SUMMARY.
However, these attributes may differ from the source event:

* **DTSTART** which is the start of the event instance. (always present)
* **DTEND** which is the end of the event instance. (always present)
* **RDATE**, **EXDATE**, **RRULE** are the rules to create event repetitions.
  They are **not** included in repeated events, see `Issue 23 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/23>`_.
  To change this, use ``of(calendar, keep_recurrence_attributes=True)``.

Speed
*****

If you use ``between()`` or ``at()``
several times, it is faster to re-use the object coming from ``of()``.

.. code:: Python

    rcalendar = recurring_ical_events.of(an_icalendar_object)
    events_of_day_1 = rcalendar.at(day_1)
    events_of_day_2 = rcalendar.at(day_2)
    events_of_day_3 = rcalendar.at(day_3)
    # ...

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

Development
-----------

1. Optional: Install virtualenv and Python3 and create a virtual environment.
    .. code-block:: shell

        virtualenv -p python3 ENV
        source ENV/bin/activate
2. Install the packages.
    .. code-block:: shell

        pip install -r requirements.txt -r test-requirements.txt
3. Run the tests
    .. code-block:: shell

        pytest

New Releases
------------

To release new versions,

1. edit the Changelog Section
2. edit setup.py, the ``__version__`` variable
3. create a commit and push it
4. Wait for `Travis <https://app.travis-ci.com/github/niccokunzmann/python-recurring-ical-events>`_ to finish the build.
5. run
    .. code-block:: shell

        python3 setup.py tag_and_deploy
6. notify the issues about their release

Testing
*******

This project's development is driven by tests.
Tests assure a consistent interface and less knowledge lost over time.
If you like to change the code, tests help that nothing breaks in the future.
They are required in that sense.
Example code and ics files can be transferred into tests and speed up fixing bugs.

You can view the tests in the `test folder
<https://github.com/niccokunzmann/python-recurring-ical-events/tree/master/test>`_.
If you have a calendar ICS file for which this library does not
generate the desired output, you can add it to the ``test/calendars``
folder and write tests for what you expect.
If you like, `open an issue <https://github.com/niccokunzmann/python-recurring-ical-events/issues>`_ first, e.g. to discuss the changes and
how to go about it.

Changelog
---------
- v0.2.4b
    - Events with a duration of 0 seconds are correctly returned.
    - ``between()`` and ``at()`` take the same kind of arguments. These arguments are documented.
- v0.2.3b
    - ``between()`` and ``at()`` allow arguments with time zones now when calendar events do not have time zones, reported in `Issue 61 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/61>`_ and `Issue 52 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/52>`_.
- v0.2.2b
    - Check that ``at()`` does not return an event starting at the next day, see `Issue 44 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/44>`_.
- v0.2.1b
    - Check that recurring events are removed if they are modified to leave the requested time span, see `Issue 62 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/62>`_.
- v0.2.0b
    - Add ability to keep the recurrence attributes (RRULE, RDATE, EXDATE) on the event copies instead of stripping them. See `Pull Request 54 <https://github.com/niccokunzmann/python-recurring-ical-events/pull/54>`_.
- v0.1.21b
    - Fix issue with repetitions over DST boundary. See `Issue 48 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/48>`_.
- v0.1.20b
    - Fix handling of modified recurrences with lower sequence number than their base event `Pull Request 45 <https://github.com/niccokunzmann/python-recurring-ical-events/pull/45>`_
- v0.1.19b
    - Benchmark using `@mrx23dot <https://github.com/mrx23dot>`_'s script and speed up recurrence calculation by factor 4, see `Issue 42 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/42>`_.
- v0.1.18b
    - Handle `Issue 28 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/28>`__ so that EXDATEs match as expected.
    - Handle `Issue 27 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/27>`_ so that parsing some rrule UNTIL values does not crash.
- v0.1.17b
    - Handle `Issue 28 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/28>`__ where passed arguments lead to errors where it is expected to work.
- v0.1.16b
    - Events with an empty RRULE are handled like events without an RRULE.
    - Remove fixed dependency versions, see `Issue 14 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/14>`_
- v0.1.15b
    - Repeated events also include subcomponents. `Issue 6 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/6>`_
- v0.1.14b
    - Fix compatibility `issue 20 <https://github.com/niccokunzmann/python-recurring-ical-events/issues/20>`_: EXDATEs of different time zones are now supported.
- v0.1.13b
    - Remove attributes RDATE, EXDATE, RRULE from repeated events `Issue 23`_
    - Use vDDDTypes instead of explicit date/datetime type `Pull Request 19 <https://github.com/niccokunzmann/python-recurring-ical-events/pull/19>`_
    - Start Changelog

Libraries Used
--------------

- `python-dateutil <https://pypi.org/project/python-dateutil/>`_ - to compute the recurrences of events using ``rrule``
- `icalendar`_ - the library used to parse ICS files
- `pytz <https://pypi.org/project/pytz/>`_ - for timezones

Related Projects
----------------

- `icalevents <https://github.com/irgangla/icalevents>`_ - another library for roughly the same use-case
- `Open Web Calendar <https://github.com/niccokunzmann/open-web-calendar>`_ - a web calendar to embed into websites which uses this library

Research
--------

- `RFC 5545 <https://tools.ietf.org/html/rfc5545>`_
- `Stackoverflow question this is created for <https://stackoverflow.com/questions/30913824/ical-library-to-iterate-recurring-events-with-specific-instances>`_
- `<https://github.com/oberron/annum>`_
  - `<https://stackoverflow.com/questions/28829261/python-ical-get-events-for-a-day-including-recurring-ones#28829401>`_
- `<https://stackoverflow.com/questions/20268204/ical-get-date-from-recurring-event-by-rrule-and-dtstart>`_
- `<https://github.com/collective/icalendar/issues/162>`_
- `<https://stackoverflow.com/questions/46471852/ical-parsing-reoccuring-events-in-python>`_
- RDATE `<https://stackoverflow.com/a/46709850/1320237>`_
    - `<https://tools.ietf.org/html/rfc5545#section-3.8.5.2>`_
