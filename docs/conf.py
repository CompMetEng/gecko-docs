"""Sphinx configuration for the GECKO documentation.

`.readthedocs.yaml` builds from this file; requirements.txt lists the Python
dependencies this build needs. The standard is the `docs-site` plugin of
CompMetEng/skills; a difference from the template is listed in DESIGN.md.
"""

from __future__ import annotations

project = "GECKO"
copyright = "CompMetEng"
author = "Chen, Gustafsson, Tafur Rangel et al."

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    # For a Python side that builds on cobrapy: scripts/autolink.py links
    # cobrapy names through this inventory.
    "sphinx.ext.intersphinx",
    # The GECKO introduction has equations ($$ ... $$): dollarmath below parses
    # them into math nodes and this extension renders them with MathJax.
    "sphinx.ext.mathjax",
]

intersphinx_mapping = {"cobra": ("https://cobrapy.readthedocs.io/en/latest/", None)}

source_suffix = {".md": "markdown"}
root_doc = "index"

myst_enable_extensions = [
    "colon_fence",  # the ::: directive spelling used throughout the site
    "deflist",
    "attrs_inline",
    "dollarmath",
]
myst_heading_anchors = 4
# Straight quotes stay straight: the API pages quote MATLAB and Python
# literals such as 'rxns', which must paste back into code unchanged.
smartquotes = False

exclude_patterns = [
    "_build",
    "conf.py",
]

# External links that reject crawlers go here, each with the reason.
linkcheck_ignore: list[str] = []
linkcheck_timeout = 20
linkcheck_retries = 2

html_theme = "pydata_sphinx_theme"
# pydata-sphinx-theme's own template appends "-- {{ project }}" to whatever
# html_title is, so the project name must not be repeated here.
html_title = "GECKO documentation"
html_favicon = "_static/gecko-icon.png"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
# Remembers the language of the code tabs across pages, browser tabs and visits.
html_js_files = ["language-sync.js"]
# The source pages are generated MyST files, not something a reader can edit.
html_show_sourcelink = False

html_theme_options = {
    "show_nav_level": 1,
    "navigation_depth": 4,
    # Only the active path expands.
    "collapse_navigation": True,
    "show_toc_level": 2,
    "use_edit_page_button": False,
    "icon_links": [
        {
            "name": "GECKO (MATLAB) on GitHub",
            "url": "https://github.com/CompMetEng/GECKO",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
        {
            "name": "geckopy (Python) on GitHub",
            "url": "https://github.com/CompMetEng/geckopy",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    # The wordmark carries the project name, so there is no navbar logo text.
    "logo": {
        "image_light": "_static/gecko-logo.png",
        "image_dark": "_static/gecko-logo-white.png",
    },
    "announcement": (
        "This site documents GECKO <strong>4.0.0b1</strong> "
        "(MATLAB and Python), a pre-release version. The API may still "
        "change before the stable 4.0.0 release."
    ),
}

html_context = {
    "default_mode": "auto",
}


def setup(app):
    """Generate the API reference and link the guide pages to it.

    The generator collects from the tracked submodules and writes static pages
    before Sphinx's own file discovery runs; scripts/autolink.py then links
    function names on the guide pages.
    """
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    import autolink
    import gen_api_pages

    gen_api_pages.generate(Path(__file__).resolve().parent)
    return autolink.setup(app)
