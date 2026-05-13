---
myst:
  html_meta:
    "description lang=en": |
      Specifications and compatibility
---

# Compatibility

## RFC Specifications

### RFC 2445 - iCalendar

![RFC 2445 is deprecated](https://img.shields.io/badge/RFC_2445-deprecated-red)

{rfc}`2445` is deprecated and has been replaced by {rfc}`5545` and {rfc}`7529`.

### RFC 5545 - iCalendar

![RFC 5545 is supported](https://img.shields.io/badge/RFC_5545-supported-green)

{rfc}`5545` is fully supported.

This is the core specification for the occurrences that this library computes:
``VEVENT``, ``VTODO``, ``VJOURNAL``, ``VALARM``, ``RRULE``, ``RDATE``,
``EXDATE``, ``RECURRENCE-ID``, and the alarm ``TRIGGER`` rules.

### RFC 7529 - Non-Gregorian Recurrence Rules

![RFC 7529 is not implemented](https://img.shields.io/badge/RFC_7529-todo-red)

{rfc}`7529` is not implemented.

### RFC 7953 - Calendar Availability

![RFC 7953 is not implemented](https://img.shields.io/badge/RFC_7953-todo-red)

{rfc}`7953` is not implemented.

### RFC 9074 - VALARM Extensions for iCalendar

![RFC 9074 is partially supported](https://img.shields.io/badge/RFC_9074-partial-yellow)

{rfc}`9074` updates ``VALARM`` components.
This library computes alarm occurrences from the ``TRIGGER``, ``REPEAT``, and
``DURATION`` rules defined for alarms by {rfc}`5545`.
The extra alarm metadata and interoperability features from {rfc}`9074`, such
as ``UID``, ``ACKNOWLEDGED``, ``RELATED-TO``, and ``PROXIMITY``, do not change
which occurrences are returned.

## RFCs and occurrence calculation

The library computes when supported calendar components occur.
RFCs that change recurrence rules, component time spans, or alarm trigger times
can affect this computation.
RFCs that add descriptive metadata, relationship metadata, or scheduling
protocol semantics can be present in iCalendar data, but they do not by
themselves change the result of ``at()``, ``between()``, ``after()``, or
``all()``.

| RFC | Scope for this library |
| --- | --- |
| {rfc}`5545` | Core recurrence, exception, component, and alarm trigger rules. |
| {rfc}`5546` | iTIP scheduling messages; not used to expand occurrence times. |
| {rfc}`6868` | Parameter value encoding; handled before recurrence logic. |
| {rfc}`7529` | Non-Gregorian ``RRULE`` support; affects recurrence calculation but is not implemented. |
| {rfc}`7953` | ``VAVAILABILITY`` and availability calculation; outside the queried components. |
| {rfc}`7986` | New descriptive properties; no direct effect on occurrence times. |
| {rfc}`9073` | Event publishing properties, components, and structured data; no direct effect on occurrence times. |
| {rfc}`9074` | Alarm extensions; base alarm trigger calculation is supported through {rfc}`5545`, while the added metadata does not change occurrence times. |
| {rfc}`9253` | Relationship and linking properties; not used to expand or filter occurrences. |

## Other Specifications

### X-WR-TIMEZONE

`X-WR-TIMEZONE` is supported through the [X-WR-TIMEZONE] library.

## Feature list

* ✅ day light saving time (DONE)
* ✅ recurring events (DONE)
* ✅ recurring events with edits (DONE)
* ✅ recurring events where events are omitted (DONE)
* ✅ recurring events events where the edit took place later (DONE)
* ✅ normal events (DONE)
* ✅ recurrence of dates but not hours, minutes, and smaller (DONE)
* ✅ endless recurrence (DONE)
* ✅ ending recurrence (DONE)
* ✅ events with start date and no end date (DONE)
* ✅ events with start as date and start as datetime (DONE)
* ✅ [RRULE](https://www.kanzaki.com/docs/ical/rrule.html) (DONE)
* ✅ events with multiple RRULE (DONE)
* ✅ [RDATE](https://www.kanzaki.com/docs/ical/rdate.html) (DONE)
* ✅ [DURATION](https://www.kanzaki.com/docs/ical/duration.html) (DONE)
* ✅ [EXDATE](https://www.kanzaki.com/docs/ical/exdate.html) (DONE)
* ✅ [X-WR-TIMEZONE] compatibilty (DONE)
* ✅ RECURRENCE-ID with THISANDFUTURE - modify all future events (DONE)

## Missing features

* ❌ non-gregorian event repetitions (TODO)
* ❌ EXRULE (deprecated), see [8.3.2.  Properties Registry](https://tools.ietf.org/html/rfc5545#section-8.3.2)


[X-WR-TIMEZONE]: https://pypi.org/project/x-wr-timezone
