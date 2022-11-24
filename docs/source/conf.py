"""Configuration file for Sphinx."""

# Python imports
import datetime

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "mailsrv"
author = "Mischback"
copyright = "{}, {}".format(datetime.datetime.now().year, author)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # automatically insert labels for section titles
    "sphinx.ext.autosectionlabel",
    # make links to other, often referenced sites easier
    "sphinx.ext.extlinks",
    # Use the RtD theme
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = []


# -- extlinks ----------------------------------------------------------------
extlinks = {
    # will show commit's SHA1
    "commit": ("https://github.com/Mischback/mailsrv/commit/%s", "%s"),
    # will show "issue [number]"
    "issue": ("https://github.com/Mischback/mailsrv/issues/%s", "issue %s"),
    # A file or directory. GitHub redirects from blob to tree if needed.
    # will show file/path relative to root-directory of the repository
    "source": (
        "https://github.com/Mischback/mailsrv/blob/development/%s",
        "%s",
    ),
    # will show "Wikipedia: [title]"
    "wiki": ("https://en.wikipedia.org/wiki/%s", "Wikipedia: %s"),
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

html_theme_options = {
    # 'canonical_url': 'http://django-calingen.readthedocs.io',  # adjust to real url
    # 'analytics_id': 'UA-XXXXXXX-1',  #  Provided by Google in your dashboard
    # 'logo_only': False,
    # 'display_version': True,
    # 'prev_next_buttons_location': 'bottom',
    "style_external_links": True,  # default: False
    # 'vcs_pageview_mode': '',
    # 'style_nav_header_background': 'white',
    # Toc options
    # 'collapse_navigation': True,
    # 'sticky_navigation': True,
    # 'navigation_depth': 4,  # might be decreased?
    # 'includehidden': True,
    # 'titles_only': False
}
