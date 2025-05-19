---
myst:
  html_meta:
    "description lang=en": |
      Versions and changes
---

# Changelog

We use [Semantic Versioning](https://semver.org)

- Breaking changes increase the **major** version number.
- New features increase the **minor** version number.
- Minor changes and bug fixes increase the **patch** version number.

## v3.7.0

- Set `SEQUENCE` to highest version of any used event in a series. See [Issue 223](https://github.com/niccokunzmann/python-recurring-ical-events/issues/223)

## v3.6.1

- Remove unused files: `requirements.txt` and `setup.py`.
- Use version identifier for PyPI.

## v3.6.0

- Add the `RECURRENCE-ID` to all the occurrences, see [Issue 219](https://github.com/niccokunzmann/python-recurring-ical-events/issues/219)
- Document how to edit one event inside of an existing calendar.

## v3.5.2

- Fix computation of mixed start and end times, see [Issue 201](https://github.com/niccokunzmann/python-recurring-ical-events/issues/201)

## v3.5.1

- Move to `pyproject.toml` format to include directory structure more easily. See [Issue 214](https://github.com/niccokunzmann/python-recurring-ical-events/issues/214)
- Remove release 3.5.0 as it does not contain any source files.

## v3.5.0 - yanked

- Restructure module into package with a file structure.
- Add pagination, see [Issue 211](https://github.com/niccokunzmann/python-recurring-ical-events/issues/211)

## v3.4.1

- Improve Alarm documentation

## v3.4.0

- Add `VALARM` support: Calculate alarm times. See [Issue 186](https://github.com/niccokunzmann/python-recurring-ical-events/issues/186)

## v3.3.4

- Allow `x-wr-timezone` `1.*` and `2.*` for this lib to remove dependency update problems.

## v3.3.3

- Fix: Events with DTSTART of type date have a duration of one day, see [Issue 179](https://github.com/niccokunzmann/python-recurring-ical-events/issues/179)

## v3.3.2

- Update x-wr-timezone

## v3.3.1

- Support RDATE with PERIOD value type where the end is a duration, see [Pull Request 180](https://github.com/niccokunzmann/python-recurring-ical-events/pull/180)
- Support modifying all events in the future (RECURRENCE-ID with RANGE=THISANDFUTURE), see [Issue 75](https://github.com/niccokunzmann/python-recurring-ical-events/issues/75)

## v3.3.0

- Make tests work with `icalendar` version 5
- Restructure README to be tested with `doctest`
- Remove `DURATION` from the result, see [Issue 139](https://github.com/niccokunzmann/python-recurring-ical-events/issues/139)
- Document new way of extending the functionality, see [Issue 133](https://github.com/niccokunzmann/python-recurring-ical-events/issues/133) and [Pull Request 175](https://github.com/niccokunzmann/python-recurring-ical-events/pull/175)

## v3.2.0

- Allow `datetime.timedelta` as second argument to `between(absolute_time, datetime.timedelta())`

## v3.1.1

- Fix: Remove duplication of modification with same sequence number, see [Issue 164](https://github.com/niccokunzmann/python-recurring-ical-events/issues/164)
- Fix: EXDATE now excludes a modified instance for an event with higher `SEQUENCE`, see [Issue](https://github.com/niccokunzmann/python-recurring-ical-events/issues/163)

## v3.1.0

- Add `count() -> int` to count all occurrences within a calendar
- Add `all() -> Generator[icalendar.Component]` to iterate over the whole calendar

## v3.0.0

- Change the architecture and add a diagram
- Add type hints, see [Issue 91](https://github.com/niccokunzmann/python-recurring-ical-events/issues/91)
- Rename `UnfoldableCalendar` to `CalendarQuery`
- Rename `of(skip_bad_events=None)` to `of(skip_bad_series=False)`
- `of(components=[...])` now also takes `ComponentAdapters`
- Fix edit sequence problems, see [Issue 151](https://github.com/niccokunzmann/python-recurring-ical-events/issues/151)

## v2.2.3

- Fix: Edits of whole event are now considering RDATE and EXDATE, see [Issue 148](https://github.com/niccokunzmann/python-recurring-ical-events/issues/148)

## v2.2.2

- Test support for `icalendar==6.*`
- Remove Python 3.7 from tests and compatibility list
- Remove pytz from requirements

## v2.2.1

- Add support for multiple RRULE in events.

## v2.2.0

- Add `after()` method to iterate over upcoming events.

## v2.1.3

- Test and support Python 3.12.
- Change SPDX license header.
- Fix RRULE with negative COUNT, see [Issue 128](https://github.com/niccokunzmann/python-recurring-ical-events/issues/128)

## v2.1.2

- Fix RRULE with EXDATE as DATE, see [Pull Request 121](https://github.com/niccokunzmann/python-recurring-ical-events/pull/121) by Jan Grasnick and [Pull Request 122](https://github.com/niccokunzmann/python-recurring-ical-events/pull/122).

## v2.1.1

- Claim and test support for Python 3.11.
- Support deleting events by setting RRULE UNTIL < DTSTART, see [Issue 117](https://github.com/niccokunzmann/python-recurring-ical-events/issues/117).

## v2.1.0

- Added support for PERIOD values in RDATE. See [Issue 113](https://github.com/niccokunzmann/python-recurring-ical-events/issues/113).
- Fixed `icalendar>=5.0.9` to support `RDATE` of type `PERIOD` with a time zone.
- Fixed `pytz>=2023.3` to assure compatibility.

## v2.0.2

- Fixed omitting last event of `RRULE` with `UNTIL` when using `pytz`, the event starting in winter time and ending in summer time. See [Issue 107](https://github.com/niccokunzmann/python-recurring-ical-events/issues/107).

## v2.0.1

- Fixed crasher with duplicate RRULE. See [Pull Request 104](https://github.com/niccokunzmann/python-recurring-ical-events/pull/104)

## v2.0.0b

- Only return `VEVENT` by default. Add `of(... ,components=...)` parameter to select which kinds of components should be returned. See [Issue 101](https://github.com/niccokunzmann/python-recurring-ical-events/issues/101).
- Remove `beta` indicator. This library works okay: Feature requests come in, not so much bug reports.

## v1.1.0b

- Add repeated TODOs and Journals. See [Pull Request 100](https://github.com/niccokunzmann/python-recurring-ical-events/pull/100) and [Issue 97](https://github.com/niccokunzmann/python-recurring-ical-events/issues/97).

## v1.0.3b

- Remove syntax anomalies in README.
- Switch to GitHub actions because GitLab decided to remove support.

## v1.0.2b

- Add support for `X-WR-TIMEZONE` calendars which contain events without an explicit time zone, see [Issue 86](https://github.com/niccokunzmann/python-recurring-ical-events/issues/86).

## v1.0.1b

- Add support for `zoneinfo.ZoneInfo` time zones, see [Issue 57](https://github.com/niccokunzmann/python-recurring-ical-events/issues/57).
- Migrate from Travis CI to Gitlab CI.
- Add code coverage on Gitlab.

## v1.0.0b

- Remove Python 2 support, see [Issue 64](https://github.com/niccokunzmann/python-recurring-ical-events/issues/64).
- Remove support for Python 3.5 and 3.6.
- Note: These deprecated Python versions may still work. We just do not claim they do.
- `X-WR-TIMEZONE` support, see [Issue 71](https://github.com/niccokunzmann/python-recurring-ical-events/issues/71).

## v0.2.4b

- Events with a duration of 0 seconds are correctly returned.
- `between()` and `at()` take the same kind of arguments. These arguments are documented.

## v0.2.3b

- `between()` and `at()` allow arguments with time zones now when calendar events do not have time zones, reported in [Issue 61](https://github.com/niccokunzmann/python-recurring-ical-events/issues/61) and [Issue 52](https://github.com/niccokunzmann/python-recurring-ical-events/issues/52).

## v0.2.2b

- Check that `at()` does not return an event starting at the next day, see [Issue 44](https://github.com/niccokunzmann/python-recurring-ical-events/issues/44).

## v0.2.1b

- Check that recurring events are removed if they are modified to leave the requested time span, see [Issue 62](https://github.com/niccokunzmann/python-recurring-ical-events/issues/62).

## v0.2.0b

- Add ability to keep the recurrence attributes (RRULE, RDATE, EXDATE) on the event copies instead of stripping them. See [Pull Request 54](https://github.com/niccokunzmann/python-recurring-ical-events/pull/54).

## v0.1.21b

- Fix issue with repetitions over DST boundary. See [Issue 48](https://github.com/niccokunzmann/python-recurring-ical-events/issues/48).

## v0.1.20b

- Fix handling of modified recurrences with lower sequence number than their base event [Pull Request 45](https://github.com/niccokunzmann/python-recurring-ical-events/pull/45)

## v0.1.19b

- Benchmark using [@mrx23dot](https://github.com/mrx23dot)'s script and speed up recurrence calculation by factor 4, see [Issue 42](https://github.com/niccokunzmann/python-recurring-ical-events/issues/42).

## v0.1.18b

- Handle [Issue 28](https://github.com/niccokunzmann/python-recurring-ical-events/issues/28) so that EXDATEs match as expected.
- Handle [Issue 27](https://github.com/niccokunzmann/python-recurring-ical-events/issues/27) so that parsing some rrule UNTIL values does not crash.

## v0.1.17b

- Handle [Issue 28](https://github.com/niccokunzmann/python-recurring-ical-events/issues/28) where passed arguments lead to errors where it is expected to work.

## v0.1.16b

- Events with an empty RRULE are handled like events without an RRULE.
- Remove fixed dependency versions, see [Issue 14](https://github.com/niccokunzmann/python-recurring-ical-events/issues/14)

## v0.1.15b

- Repeated events also include subcomponents. [Issue 6](https://github.com/niccokunzmann/python-recurring-ical-events/issues/6)

## v0.1.14b

- Fix compatibility [Issue 20](https://github.com/niccokunzmann/python-recurring-ical-events/issues/20): EXDATEs of different time zones are now supported.

## v0.1.13b

- Remove attributes RDATE, EXDATE, RRULE from repeated events [Issue 23](https://github.com/niccokunzmann/python-recurring-ical-events/issues/23).
- Use vDDDTypes instead of explicit date/datetime type [Pull Request 19](https://github.com/niccokunzmann/python-recurring-ical-events/pull/19).
- Start Changelog
