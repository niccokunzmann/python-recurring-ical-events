Recurring ICal events for Python
================================

.. image:: https://travis-ci.org/niccokunzmann/python-recurring-ical-events.svg?branch=master
   :target: https://travis-ci.org/niccokunzmann/python-recurring-ical-events
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
* `RDATE <https://www.kanzaki.com/docs/ical/rdate.html>`_
* `DURATION <https://www.kanzaki.com/docs/ical/duration.html>`_ (DONE)
* `EXDATE <https://www.kanzaki.com/docs/ical/exdate.html>`_ (DONE)

Not included:

* EXRULE (deprecated), see `8.3.2.  Properties Registry
  <https://tools.ietf.org/html/rfc5545#section-8.3.2>`_


Installation
------------

.. code:: shell

    pip install python-recurring-ical-events

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

    a_date = 2023 # a year
    a_date = (2023, 1) # January in 2023
    a_date = (2023, 1, 1) # the 1st of January in 2023
    a_date = (2023, 1, 1, 0) # the first hour of the year 2023
    a_date = (2023, 1, 1, 0, 0) # the first minute in 2023
    a_date = datetime.date(2023) # the first day in 2023
    a_date = datetime.date(2023, 1, 1) # the first day in 2023
    
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

* DTSTART which is the start of the event instance.
* DTEND which is the end of the event instance.
* RDATE, EXDATE, RRULE are the rules to create event repetitions. If they are included is undefined. Future requirements may remove them. If you like to have them included, please write a test or `open an issue <https://github.com/niccokunzmann/python-recurring-ical-events/issues>`_.

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

To release new versions, edit setup.py, the ``__version__`` variable and run

.. code-block:: shell

    python3 setup.py tag_and_deploy

Related Projects
----------------

- `icalevents <https://github.com/irgangla/icalevents>`_

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
