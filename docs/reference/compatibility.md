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

### RFC 7529 - Non-Gregorian Recurrence Rules

![RFC 7529 is not implemented](https://img.shields.io/badge/RFC_7529-todo-red)

{rfc}`7529` is not implemented.

### RFC 7953 - Calendar Availability

![RFC 7953 is not implemented](https://img.shields.io/badge/RFC_7953-todo-red)

{rfc}`7953` is not implemented.

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
