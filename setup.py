#!/usr/bin/python3
# ruff: noqa
"""The setup and build script for the library named "PACKAGE_NAME"."""

import os
import subprocess
import sys
from distutils.core import Command

PACKAGE_NAME = "recurring_ical_events"

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, HERE)  # for package import

__version__ = "3.3.0"
__author__ = "Nicco Kunzmann"


def read_file_named(file_name):
    file_path = os.path.join(HERE, file_name)
    with open(file_path) as file:
        return file.read()


def read_requirements_file(file_name):
    content = read_file_named(file_name)
    lines = []
    for line in content.splitlines():
        comment_index = line.find("#")
        if comment_index >= 0:
            line = line[:comment_index]
        line = line.strip()
        if not line:
            continue
        lines.append(line)
    return lines


# The base package metadata to be used by both distutils and setuptools
METADATA = dict(
    name=PACKAGE_NAME,
    version=__version__,
    py_modules=[PACKAGE_NAME],
    author=__author__,
    author_email="niccokunzmann@rambler.ru",
    description="Calculate recurrence times of events, todos and journals based on icalendar RFC5545.",
    license="LGPL-3.0-or-later",
    url="https://github.com/niccokunzmann/python-recurring-ical-events",
    keywords="icalendar",
)

# set development status from __version__

DEVELOPMENT_STATES = {
    "p": "Development Status :: 1 - Planning",
    "pa": "Development Status :: 2 - Pre-Alpha",
    "a": "Development Status :: 3 - Alpha",
    "b": "Development Status :: 4 - Beta",
    "": "Development Status :: 5 - Production/Stable",
    "m": "Development Status :: 6 - Mature",
    "i": "Development Status :: 7 - Inactive",
}
development_state = DEVELOPMENT_STATES[""]
for ending in DEVELOPMENT_STATES:
    if ending and __version__.endswith(ending):
        development_state = DEVELOPMENT_STATES[ending]

if not __version__[-1:].isdigit():
    METADATA["version"] += "0"

# tag and upload to github to autodeploy with travis


class TagAndDeployCommand(Command):
    description = (
        "Create a git tag for this version and push it to origin."
        "To trigger a travis-ci build and and deploy."
    )
    user_options = []
    name = "tag_and_deploy"
    remote = "origin"
    branch = "main"

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if subprocess.call(["git", "--version"]) != 0:
            print("ERROR:\n\tPlease install git.")
            exit(1)
        status_lines = subprocess.check_output(["git", "status"]).splitlines()
        current_branch = status_lines[0].strip().split()[-1].decode()
        print(f"On branch {current_branch}.")
        if current_branch != self.branch:
            print(
                f'ERROR:\n\tNew tags can only be made from branch "{self.branch}".' ""
            )
            print(
                f'\tYou can use "git checkout {self.branch}" to switch the branch.' ""
            )
            exit(1)
        tags_output = subprocess.check_output(["git", "tag"])
        tags = [tag.strip().decode() for tag in tags_output.splitlines()]
        tag = "v" + METADATA["version"]
        if tag in tags:
            print(f"Warning: \n\tTag {tag} already exists.")
            print(
                "\tEdit the version information in {}".format(
                    os.path.join(HERE, PACKAGE_NAME, "__init__.py"),
                )
            )
        else:
            print(f'Creating tag "{tag}".')
            subprocess.check_call(["git", "tag", tag])
        print(f'Pushing tag "{tag}" to remote "{self.remote}".')
        subprocess.check_call(["git", "push", self.remote, tag])


# Extra package metadata to be used only if setuptools is installed

required_packages = read_requirements_file("requirements.txt")
required_test_packages = read_requirements_file("test-requirements.txt")


SETUPTOOLS_METADATA = dict(
    install_requires=required_packages,
    tests_require=required_test_packages,
    include_package_data=False,
    classifiers=[  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        development_state,
    ],
    zip_safe=True,
    cmdclass={
        TagAndDeployCommand.name: TagAndDeployCommand,
    },
)


def main():
    # Build the long_description from the README and CHANGES
    METADATA["long_description"] = read_file_named("README.rst")

    # Use setuptools if available, otherwise fallback and use distutils
    try:
        import setuptools

        METADATA.update(SETUPTOOLS_METADATA)
        setuptools.setup(**METADATA)
    except ImportError:
        import distutils.core

        distutils.core.setup(**METADATA)


if __name__ == "__main__":
    main()
