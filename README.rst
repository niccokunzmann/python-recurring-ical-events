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









