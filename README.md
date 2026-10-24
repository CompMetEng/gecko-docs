# GECKO Documentation

Documentation for GECKO, a MATLAB toolbox, and geckopy, its Python port, for reconstructing, simulating and analyzing enzyme-constrained genome-scale metabolic models (ecModels). Built with [Sphinx](https://www.sphinx-doc.org/), [MyST](https://myst-parser.readthedocs.io/) and [pydata-sphinx-theme](https://pydata-sphinx-theme.readthedocs.io/), following the `docs-site` standard of [CompMetEng/skills](https://github.com/CompMetEng/skills), which [raven-docs](https://github.com/CompMetEng/raven-docs) follows for RAVEN and raven-toolbox. The intent of the site is in [DESIGN.md](DESIGN.md).

Alongside the Guide, the site includes an auto-generated **API reference** that documents both implementations side by side, statically extracted at build time from each toolbox's source (pulled in as git submodules). See [API reference (MATLAB + Python)](#api-reference-matlab--python) below.

## Repository layout

```
gecko-docs/
├── .readthedocs.yaml        # Read the Docs build configuration (incl. submodules)
├── .gitmodules              # GECKO + geckopy submodule definitions
├── .github/                 # workflows (build, submodule updates), Dependabot, pull request template
├── requirements.txt         # Python build dependencies
├── DESIGN.md                # what the site should be, and the decisions log
├── CONTRIBUTING.md          # writing rules and build commands
├── README.md                # This file
├── GECKO/                   # submodule: CompMetEng/GECKO        (MATLAB source)
├── geckopy/                 # submodule: CompMetEng/geckopy      (Python source)
├── scripts/
│   ├── project.yml          # names, paths and categories of this site, read by the scripts
│   ├── curated_pairs.yml    # hand-curated name pairs the generator can't match automatically
│   ├── known_names.txt      # names the name checker accepts that are not functions
│   └── *.py                 # copies of docs-site/scripts: API generator, linker, name and site checks
└── docs/
    ├── conf.py              # Sphinx configuration
    ├── index.md             # Landing page
    ├── migrate.md, gecko3-to-gecko4.md, gecko-to-geckopy.md
    ├── references.md        # Citations
    ├── installation/index.md
    ├── guide/               # Introduction, Getting started, and the task pages
    ├── _static/             # stylesheet, logos, favicon
    └── api/                 # index.md is hand-written; matlab/ and python/ are generated (not checked in)
```

## Building locally

```bash
# from the repository root
git submodule update --init --recursive   # fetch the GECKO + geckopy sources
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
sphinx-build -W -b html docs docs/_build/html
```

The `git submodule update --init` step is required: without it the `GECKO/` and `geckopy/` source trees are empty and the API reference builds with no functions in it.

Open `docs/_build/html/index.html` in a browser. There is no live-reload dev server configured; re-run `sphinx-build` after editing. The build uses `-W`, so a warning fails it, as on Read the Docs. Before a pull request, run `python scripts/check_site.py .` as well.

## Hosting on Read the Docs

1. Push this folder to a GitHub, GitLab or Bitbucket repository.
2. Sign in at https://readthedocs.org/ and import the repository.
3. Read the Docs detects `.readthedocs.yaml` and builds the site automatically on every push. In the project settings, enable "Build pull requests for this project" to get a preview of each pull request.

Read the Docs initializes the git submodules automatically because `.readthedocs.yaml` sets `submodules.include: all`, so the API reference is built on every push without any extra configuration. The build fails on warnings (`fail_on_warning: true`).

## API reference (MATLAB + Python)

`docs/api/` documents both toolboxes side by side, plus `docs/matlab-vs-python.md`, a generated table pairing every function that exists in both. All of it, except `docs/api/index.md`, is written by `scripts/gen_api_pages.py` at build time (run from `docs/conf.py`'s `setup()` hook), which extracts MATLAB help blocks and Python docstrings directly from source: no MATLAB runtime, no installed geckopy package, and no live-rendering plugin involved. Nothing under `docs/api/matlab/`, `docs/api/python/` or `docs/matlab-vs-python.md` is checked into the repository or should be hand-edited; regenerate by rebuilding. Function pairs that don't match by name alone (geckopy renamed part of the API during the port) are recorded in `scripts/curated_pairs.yml`, which is validated against the live source at build time.

The scripts in `scripts/` are copies of `docs-site/scripts` in [CompMetEng/skills](https://github.com/CompMetEng/skills). What is specific to this site is in `scripts/project.yml`. A change to a script is made there first.

Sources are git submodules pinned to each project's tracked development branch (see `.gitmodules`):

- `GECKO/`: [CompMetEng/GECKO](https://github.com/CompMetEng/GECKO) (MATLAB)
- `geckopy/`: [CompMetEng/geckopy](https://github.com/CompMetEng/geckopy) (Python)

To refresh the reference against the latest upstream code:

```bash
git submodule update --remote --recursive
git add GECKO geckopy
git commit -m "chore: update submodules to latest tracked branches"
```

`.github/workflows/update-submodules.yml` does this daily and opens a pull request, whose build checks that the new sources still build.

## License and attribution

The GECKO source code is released under the MIT license at https://github.com/CompMetEng/GECKO. The scientific content summarized in these pages is the work of the original authors; see [Citations](docs/references.md) for the papers to cite.
