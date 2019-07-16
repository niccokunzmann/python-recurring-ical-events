#!/usr/bin/python3
"""The setup and build script for the library named "PACKAGE_NAME"."""
import os
import sys
from setuptools.command.test import test as TestCommandBase
from distutils.core import Command
import subprocess

PACKAGE_NAME = "recurring_ical_events"

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, HERE)  # for package import

__version__ = "0.1.8b"
__author__ = 'Nicco Kunzmann'


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
    author_email='niccokunzmann@rambler.ru',
    description='A Python module which repeats ICalendar events by RRULE, RDATE and EXDATE.',
    license='LGPLv3+',
    url='https://github.com/niccokunzmann/python-recurring-ical-events',
    keywords='icalendar',
)

# set development status from __version__

DEVELOPMENT_STATES = {
        "p": "Development Status :: 1 - Planning",
        "pa": "Development Status :: 2 - Pre-Alpha",
        "a": "Development Status :: 3 - Alpha",
        "b": "Development Status :: 4 - Beta",
        "": "Development Status :: 5 - Production/Stable",
        "m": "Development Status :: 6 - Mature",
        "i": "Development Status :: 7 - Inactive"
    }
development_state = DEVELOPMENT_STATES[""]
for ending in DEVELOPMENT_STATES:
    if ending and __version__.endswith(ending):
        development_state = DEVELOPMENT_STATES[ending]

if not __version__[-1:].isdigit():
    METADATA["version"] += "0"

# tag and upload to github to autodeploy with travis

class TagAndDeployCommand(Command):

    description = "Create a git tag for this version and push it to origin."\
                  "To trigger a travis-ci build and and deploy."
    user_options = []
    name = "tag_and_deploy"
    remote = "origin"
    branch = "master"

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
        print("On branch {}.".format(current_branch))
        if current_branch != self.branch:
            print("ERROR:\n\tNew tags can only be made from branch \"{}\"."
                  "".format(self.branch))
            print("\tYou can use \"git checkout {}\" to switch the branch."
                  "".format(self.branch))
            exit(1)
        tags_output = subprocess.check_output(["git", "tag"])
        tags = [tag.strip().decode() for tag in tags_output.splitlines()]
        tag = "v" + METADATA["version"]
        if tag in tags:
            print("Warning: \n\tTag {} already exists.".format(tag))
            print("\tEdit the version information in {}".format(
                    os.path.join(HERE, PACKAGE_NAME, "__init__.py")
                ))
        else:
            print("Creating tag \"{}\".".format(tag))
            subprocess.check_call(["git", "tag", tag])
        print("Pushing tag \"{}\" to remote \"{}\".".format(tag, self.remote))
        subprocess.check_call(["git", "push", self.remote, tag])

# Extra package metadata to be used only if setuptools is installed

required_packages = read_requirements_file("requirements.txt")
required_test_packages = read_requirements_file("test-requirements.txt")


SETUPTOOLS_METADATA = dict(
    install_requires=required_packages,
    tests_require=required_test_packages,
    include_package_data=False,
    classifiers=[  # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        development_state
        ],
    zip_safe=True,
    cmdclass={
        TagAndDeployCommand.name: TagAndDeployCommand
        },
)


def main():
    # Build the long_description from the README and CHANGES
    METADATA['long_description'] = read_file_named("README.rst")

    # Use setuptools if available, otherwise fallback and use distutils
    try:
        import setuptools
        METADATA.update(SETUPTOOLS_METADATA)
        setuptools.setup(**METADATA)
    except ImportError:
        import distutils.core
        distutils.core.setup(**METADATA)

if __name__ == '__main__':
    main()
