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
* RRULE (DONE)
* RDATE
* EXRULE
* EXDATE (DONE)


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

.. code-block::

    start 2019-03-18 04:00:00+01:00 duration 1:00:00
    start 2019-03-20 04:00:00+01:00 duration 1:00:00
    start 2019-03-19 04:00:00+01:00 duration 1:00:00
    start 2019-03-07 02:00:00+01:00 duration 1:00:00
    start 2019-03-08 01:00:00+01:00 duration 2:00:00
    start 2019-03-09 03:00:00+01:00 duration 0:30:00
    start 2019-03-10 duration 1 day, 0:00:00

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
