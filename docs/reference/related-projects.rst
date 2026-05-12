

Related Projects
================

These projects either build on ``recurring-ical-events``, solve related
calendar problems, or provide calendar and recurrence functionality that this
project uses.

Core calendar libraries
-----------------------

- `icalendar`_ - parses and writes iCalendar files
- `python-dateutil`_ - computes recurrence rules with ``rrule``
- `x-wr-timezone`_ - handles the non-standard ``X-WR-TIMEZONE`` property
- `tzdata`_ - provides time zone data when the operating system does not

Projects using or similar to recurring-ical-events
--------------------------------------------------

- `icalevents <https://github.com/irgangla/icalevents>`_ - another library for roughly the same use-case
- `Open Web Calendar <https://github.com/niccokunzmann/open-web-calendar>`_ - a web calendar to embed into websites which uses this library
- `icspy <https://icspy.readthedocs.io/>`_ - to create your own calendar events
- `pyICSParser <https://pypi.org/project/pyICSParser/>`_ - parse icalendar files and return event times (`GitHub <https://github.com/oberron/pyICSParser>`__)
- `ics-query`_ - a **command line** implementation of ``recurring-ical-events``
- `icalendar-events-cli`_ - another **command line** implementation of ``recurring-ical-events``
- `caldav`_ - the python caldav client library
- `plann`_ - a **command line** caldav client
- `ics_calendar`_ - Provides a component for ICS (icalendar) calendars for `Home Assistant`_

.. _`icalendar`: https://pypi.org/project/icalendar/
.. _`python-dateutil`: https://pypi.org/project/python-dateutil/
.. _`x-wr-timezone`: https://github.com/niccokunzmann/x-wr-timezone
.. _`tzdata`: https://pypi.org/project/tzdata/
.. _`ics-query`: https://github.com/niccokunzmann/ics-query#readme
.. _`icalendar-events-cli`: https://github.com/waldbaer/icalendar-events-cli#readme
.. _`caldav`:  https://github.com/python-caldav/caldav
.. _`plann`: https://github.com/tobixen/plann
.. _`ics_calendar`: https://github.com/franc6/ics_calendar/
.. _`Home Assistant`: https://www.home-assistant.io/

Command line interface
----------------------

If you would like to use this functionality on the command line or in the shell, you can use
`ics-query`_.
