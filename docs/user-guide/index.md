---
myst:
  html_meta:
    "description lang=en": |
      Documentation for users who wish query calendars for occurrences of events and other components.
---

# Get started

This section gets you started using this library.

## Installation

```{eval-rst}
.. tabs::

   .. tab:: Pip

      .. code-block:: bash

          pip install 'recurring-ical-events==3.*'

   .. tab:: Debian/Ubuntu

      .. code-block:: bash

          sudo apt-get install python-recurring-ical-events

   .. tab:: Alpine Linux

      .. code-block:: bash

          apk add py3-recurring-ical-events

   .. tab:: Fedora

      .. code-block:: bash

        sudo dnf install ???

   .. tab:: Arch Linux

      .. code-block:: bash

        ???


```


If not listed, this library is available as a package on the following platforms:

[![Packaging status](https://repology.org/badge/vertical-allrepos/python%3Arecurring-ical-events.svg?columns=3)](https://repology.org/project/python%3Arecurring-ical-events/versions)

## Usage

The [icalendar] module is responsible for parsing files with a calendar specification in it.
This library takes such a {py:class}:`icalendar.Calendar` and computes the occurrences.

To import this module, write

```python
>>> import recurring_ical_events
```

If you like to go deeper, have a look at the [API documentation](../reference/api) at this point.
We have a comprehensive list of **[examples]** to get you started.

[icalendar]: https://icalendar.readthedocs.io
[examples]: ../examples/index.rst
