Architecture
============

.. image:: ../img/architecture.png
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
