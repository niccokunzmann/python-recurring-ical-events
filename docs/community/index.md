---
myst:
  html_meta:
    "description lang=en": |
      Documentation for contributors who wish to improve this library.
---

# Contribute

There are various ways in which you can contribute to this library.

## Support this library

Please support the development and upkeep in one of these ways:

- [Support using GitHub Sponsors](https://github.com/sponsors/niccokunzmann)
- [Fund specific issues using Polar](https://polar.sh/niccokunzmann/python-recurring-ical-events)
- [Support using Open Collective](https://opencollective.com/open-web-calendar/)
- [Support using thanks.dev](https://thanks.dev)

We accept donations to sustain our work, once or regular.
Consider donating money to open-source as everyone benefits.

## Improve the documentation

Your help with this documentation is very welcome!
Please feel free to edit the pages with the "Edit on GitHub" button on the side.
With a GitHub account, your contribution will be guided towards a [pull request]
and we can have a look and use your suggestions.

For style and formatting, please consult the [documentation reference section].

[documentation reference section]: ../reference/documentation

## Setup to develop

This section informs you how to work on this project.

### Code style

Please install [pre-commit] before git commit.
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

After installing `tox`, run the tests with your current Python version:

```sh
tox -e py
```

.. info::

  With this, you have all the tools to develop and improve this project.
  Please open an [pull request] as soon as you made a change.
  This is not about being perfect, only about doing your part of the communication.
  Your are welcome!

[pull request]: https://github.com/niccokunzmann/python-recurring-ical-events/pull

#### Extended Testing

When you create a pull request, we will run the tests in all Python versions.
You can do that, too.

```sh
tox
```

To run the tests in a specific Python version:

```sh
tox -e py39
```

### Building the documentation

You can build the documentation locally to see your changes.
To view the documentation in a web page and have it update with every edit,
run the following commands:

```sh
cd docs
make livehtml
```

To clean the build folder, run:

```sh
make clean
```

Commits are tested online to check if the documentation does not contain any
errors or warnings.
To run these checks and see if you can publish the changes, run:

```sh
tox -e docs
```

[test folder]: https://github.com/niccokunzmann/python-recurring-ical-events/tree/master/test
[issue]: https://github.com/niccokunzmann/python-recurring-ical-events/issues
