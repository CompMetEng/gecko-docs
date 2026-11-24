"""Sphinx configuration for the GECKO documentation.

`.readthedocs.yaml` builds from this file; requirements.txt lists the Python
dependencies this build needs. The standard is the `docs-site` plugin of
CompMetEng/skills; a difference from the template is listed in DESIGN.md.
"""

from __future__ import annotations

import sys
import urllib.request

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
    # The workflow diagrams of the guide are Mermaid flowcharts.
    "sphinxcontrib.mermaid",
]

# Diagram height follows the content (the default of 500 px would shrink a tall flowchart).
mermaid_height = "auto"
# Scroll-wheel zoom and drag-to-pan in the page and in the full-screen view
# (static/mermaid-zoom.js limits the wheel in the page to Ctrl or Cmd).
mermaid_d3_zoom = True

intersphinx_mapping = {"cobra": ("https://cobrapy.readthedocs.io/en/latest/", None)}


def _inventory_reachable(base: str) -> bool:
    """True when base + objects.inv can be fetched; a miss prints a note only."""
    try:
        # Read the Docs answers the default Python user agent with 403.
        request = urllib.request.Request(base + "objects.inv", headers={"User-Agent": "sphinx"})
        urllib.request.urlopen(request, timeout=10).close()
    except OSError as err:
        print(f"note: inventory {base} unreachable ({err}); links to it stay plain text", file=sys.stderr)
        return False
    return True


# raven-docs is the sibling site: guide pages link to its pages through its
# inventory. Sphinx fails a strict build on an unreachable inventory and the
# warning has no name to suppress, so the inventory is added only when it can
# be fetched. A link of the form inv:raven:... to a missing inventory then
# stays plain text.
if _inventory_reachable("https://raven-docs.readthedocs.io/en/latest/"):
    intersphinx_mapping["raven"] = ("https://raven-docs.readthedocs.io/en/latest/", None)
suppress_warnings = ["intersphinx.external"]

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
linkcheck_ignore: list[str] = [
    # These sites answer the link checker with 403 but open in a browser.
    r"https://doi\.org/10\.1128/spectrum\.01705-23",  # ASM journals
    r"https://doi\.org/10\.3390/biom12010065",  # MDPI
    r"https://mathworks\.com/.*",  # MathWorks
]
linkcheck_timeout = 20
linkcheck_retries = 2

html_theme = "pydata_sphinx_theme"
# pydata-sphinx-theme's own template appends "-- {{ project }}" to whatever
# html_title is, so the project name must not be repeated here.
html_title = "GECKO documentation"
html_favicon = "_static/gecko-icon.png"
html_static_path = ["_static"]
# site-footer.html is the footer of every page.
templates_path = ["_templates"]
html_css_files = ["custom.css"]
# Remembers the language of the code tabs across pages, browser tabs and visits.
html_js_files = [
    "language-sync.js",
    "mermaid-zoom.js",
    # Page-view statistics of GoatCounter, which sets no cookies.
    (
        "https://gc.zgo.at/count.js",
        {"async": "async", "data-goatcounter": "https://gecko-docs.goatcounter.com/count"},
    ),
]
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
    # One footer: the lab and the sibling site. The theme's copyright and
    # Sphinx version lines are left out.
    "footer_start": ["site-footer"],
    "footer_center": [],
    "footer_end": [],
    # The wordmark carries the project name, so there is no navbar logo text.
    "logo": {
        "image_light": "_static/gecko-logo.png",
        "image_dark": "_static/gecko-logo-white.png",
    },
    "announcement": (
        "This site documents GECKO <strong>4.0.0b3</strong> "
        "(MATLAB and Python), a pre-release version. The API may still "
        "change before the stable 4.0.0 release. The latest stable version is "
        "GECKO <strong>3.2.5</strong>, installed as a MATLAB Add-On; "
        '<a href="{upgrade}">upgrade a GECKO 3 project</a>. '
        '<a href="{release_notes}">Release notes</a>.'
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

    def link_announcement(app, pagename, templatename, context, doctree):
        """Point the announcement to the upgrade page and the release notes from every page."""
        announcement = context.get("theme_announcement")
        if announcement:
            for key, target in (
                ("{upgrade}", "gecko3-upgrade-project"),
                ("{release_notes}", "release-notes/index"),
            ):
                announcement = announcement.replace(key, context["pathto"](target))
            context["theme_announcement"] = announcement

    app.connect("html-page-context", link_announcement)
    return autolink.setup(app)
