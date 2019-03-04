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

* day light saving time
* recurring events
* recurring events with edits
* recurring events where events are omitted
* recurring events events where the edit took place later
* normal events
* recurrence of dates but not hours, minutes, and smaller
* endless recurrence
* ending recurrence
* events with start date and no and date
* events with start as date and start as datetime
* RRULE, RDATE, EXDATE

.. code-block:: python

    import requests
    import icalendar
    import datetime
    import recurring_ical_events

    today = datetime.datetime.today()
    one_year_ahead = today.replace(year=today.year + 1)

    ical_string = requests.get("https://url-to-ical-feed").text
    calendar = icalendar.Calendar.from_ical(ical_string)
    for event in recurring_ical_events.of(calendar).between(today, one_year_ahead):
        print(event["DTSTART"])

Installation
------------

.. code:: shell

    pip install python-recurring-ical-events

Development
-----------

1. Optional: Install virtualenv and Python3 and create a virtual environment.
    .. code-block:: shell

        virtualenv -p python3 ENV
        source ENV/bin/activate
2. Install the packages.
    .. code-block:: shell

        pip install -r requirements.txt test-requirements.txt
3. Run the tests
    .. code-block:: shell

        pytest

To release new versions, edit setup.py, the ``__version__`` variable and run


.. code-block:: shell

    python3 setup.py tag_and_deploy


Research
--------

- `<https://stackoverflow.com/questions/30913824/ical-library-to-iterate-recurring-events-with-specific-instances>`_
- `<https://github.com/oberron/annum>`_
  - `<https://stackoverflow.com/questions/28829261/python-ical-get-events-for-a-day-including-recurring-ones#28829401>`_
- `<https://stackoverflow.com/questions/20268204/ical-get-date-from-recurring-event-by-rrule-and-dtstart>`_
- `<https://github.com/collective/icalendar/issues/162>`_
- `<https://stackoverflow.com/questions/46471852/ical-parsing-reoccuring-events-in-python>`_
- RDATE `<https://stackoverflow.com/a/46709850/1320237>`_
    - `<https://tools.ietf.org/html/rfc5545#section-3.8.5.2>`_
