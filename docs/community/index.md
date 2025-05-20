---
myst:
  html_meta:
    "description lang=en": |
      Documentation for contributors who wish to improve this library.
---

# Contribute

There are various ways in which you can contribute to this library.

## Support

Please support the development and upkeep in one of these ways:

- [Support using GitHub Sponsors](https://github.com/sponsors/niccokunzmann)
- [Fund specific issues using Polar](https://polar.sh/niccokunzmann/python-recurring-ical-events)
- [Support using Open Collective](https://opencollective.com/open-web-calendar/)
- [Support using thanks.dev](https://thanks.dev)

We accept donations to sustain our work, once or regular.
Consider donating money to open-source as everyone benefits.

## Setup to develop

This section informs you how to work on this project.

### Code style

Please install [pre-commit]_before git commit.
It will ensure that the code is formatted and linted as expected using [ruff].

```sh
pre-commit install
```

[pre-commit]: https://pre-commit.com/
[ruff]: https://docs.astral.sh/ruff/

### Testing

This project's development is driven by tests.
Tests assure a consistent interface and less knowledge lost over time.
If you like to change the code, tests help that nothing breaks in the future.
They are required in that sense.
Example code and ics files can be transferred into tests and speed up fixing bugs.

You can view the tests in the [test folder]
If you have a calendar ICS file for which this library does not
generate the desired output, you can add it to the `test/calendars`
folder and write tests for what you expect.
If you like, open an [issue] first, e.g. to discuss the changes and
how to go about it.


To run the tests, we use `tox`.
`tox` tests all different Python versions which we want to  be compatible to.

```sh
pip3 install tox
```

To run all the tests:

```sh
tox
```

To run the tests in a specific Python version:

```sh
tox -e py39
```

[test folder]: https://github.com/niccokunzmann/python-recurring-ical-events/tree/master/test
[issue]: https://github.com/niccokunzmann/python-recurring-ical-events/issues
