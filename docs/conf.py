# icalendar documentation build configuration file
import importlib.metadata
import datetime
import os
from pathlib import Path
import sys

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    # from pydata-sphix-theme
    "myst_parser",
    # from https://sphinx-toolbox.readthedocs.io/
    "sphinx_tabs.tabs",
    "sphinx-prompt",
    # "sphinx_toolbox",
    # "sphinx_toolbox.more_autodoc"
]
source_suffix = {".rst": "restructuredtext"}
master_doc = "index"

project = "recurring-ical-events"
this_year = datetime.date.today().year
copyright = f"{this_year}, Nicco Kunzmann & recurring-ical-events contributors"
release = version = importlib.metadata.version("recurring-ical-events")


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/niccokunzmann/python-recurring-ical-events",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
            "attributes": {
                "target": "_blank",
                "rel": "noopener me",
                "class": "nav-link custom-fancy-css"
            }
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/recurring-ical-events",
            "icon": "fa-solid fa-download",
            "type": "fontawesome",
            "attributes": {
                "target": "_blank",
                "rel": "noopener me",
                "class": "nav-link custom-fancy-css"
            }
        },
        {
            "name": "Mastodon",
            "url": "https://toot.wales/tags/RecurringIcalEvents",
            "icon": "fa-brands fa-mastodon",
            "type": "fontawesome",
            "attributes": {
                "target": "_blank",
                "rel": "noopener me",
                "class": "nav-link custom-fancy-css"
            }
        },
        {
            "name": "Youtube",
            "url": "https://www.youtube.com/watch?v=nwpS2dCk_Rk&list=PLxMGFFiBKgdb3L550U5EAiCvft2IK08xK",
            "icon": "fa-brands fa-youtube",
            "type": "fontawesome",
            "attributes": {
                "target": "_blank",
                "rel": "noopener me",
                "class": "nav-link custom-fancy-css"
            }
        }
    ],
    "navigation_with_keys": True,
    "search_bar_text": "Search",
    "show_nav_level": 2,
    "show_toc_level": 2,
    "use_edit_page_button": True,
}
html_context = {
#     "github_url": "https://github.com", # or your GitHub Enterprise site
    "github_user": "niccokunzmann",
    "github_repo": "python-recurring-ical-events",
    "github_version": "main",
    "doc_path": "docs",
}
htmlhelp_basename = "recurring-ical-events-doc"
pygments_style = "sphinx"


# -- Intersphinx configuration ----------------------------------

# This extension can generate automatic links to the documentation of objects
# in other projects. Usage is simple: whenever Sphinx encounters a
# cross-reference that has no matching target in the current documentation set,
# it looks for targets in the documentation sets configured in
# intersphinx_mapping. A reference like :py:class:`zipfile.ZipFile` can then
# linkto the Python documentation for the ZipFile class, without you having to
# specify where it is located exactly.
#
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "icalendar": ("https://icalendar.readthedocs.io/en/latest", None),
    "dateutil": ("https://dateutil.readthedocs.io/en/stable/", None),
}


man_pages = [("index", "recurring_ical_events", "recurring_ical_events Documentation", ["Nicco Kunzmann"], 1)]

exclude_patterns = [
    "venv"
]

# we have had issues with linkcheck timing and retries on www.gnu.org
linkcheck_retries = 1
linkcheck_timeout = 5
linkcheck_report_timeouts_as_broken = True

# autodoc
autodoc_typehints_format = "short"
autodoc_preserve_defaults = True
autodoc_type_aliases = {
    "datetime": "datetime.datetime",
    "date": "datetime.date",
    "timedelta": "datetime.timedelta",
    "Time": "recurring_ical_events.types.Time",
    "DateArgument": "recurring_ical_events.types.DateArgument",
    "UID": "recurring_ical_events.types.UID",
    "Timestamp": "recurring_ical_events.types.Timestamp",
    "RecurrenceID": "recurring_ical_events.types.RecurrenceID",
    "RecurrenceIDs": "recurring_ical_events.types.RecurrenceIDs",
    "Component": "icalendar.cal.Component",
    "Calendar": "icalendar.cal.Calendar",
    "T_COMPONENTS": "recurring_ical_events.query.T_COMPONENTS",
    "OccurrenceID": "recurring_ical_events.occurrence.OccurrenceID",
    "icalendar.Calendar": "icalendar.cal.Calendar",
}

# sphinx-toolbox
github_username = "niccokunzmann"
github_repository = "python-recurring-ical-events"


# from https://github.com/sphinx-doc/sphinx/issues/10785
nitpick_ignore = [
    # ignore for now
    ("py:class", "recurring_ical_events.types.Time"),
    ("py:class", "recurring_ical_events.types.UID"),
    ("py:class", "recurring_ical_events.types.RecurrenceIDs"),
    ("py:class", "Time"),
    ("py:class", "UID"),
    ("py:class", "RecurrenceID"),
    ("py:class", "TypeAliasForwardRef"),
    # /home/nicco/recurring-ical-events/recurring_ical_events/__init__.py:docstring of recurring_ical_events.OccurrenceID.uid:1: WARNING: duplicate object description of recurring_ical_events.OccurrenceID.uid, other instance in reference/api, use :no-index: for one of them
    ("py:obj", "recurring_ical_events.OccurrenceID.uid"),
]

# make title smaller
# see https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_title
html_title = f"{project} {release}"
html_short_title = project

# try reloading the module
# see https://github.com/sphinx-doc/sphinx/issues/4317#issuecomment-353793061
HERE = Path(__file__).parent
sys.path.insert(0, str(Path(HERE).parent))

