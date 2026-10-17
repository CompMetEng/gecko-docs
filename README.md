# GECKO Documentation

Documentation for GECKO, a MATLAB toolbox, and geckopy, its Python port, for
reconstructing, simulating and analyzing enzyme-constrained genome-scale
metabolic models (ecModels). Built with [Sphinx](https://www.sphinx-doc.org/),
[MyST](https://myst-parser.readthedocs.io/) and
[pydata-sphinx-theme](https://pydata-sphinx-theme.readthedocs.io/), matching
the [raven-docs](https://github.com/edkerk/raven-docs) setup for RAVEN and
raven-toolbox.

Alongside the Guide, the site includes an auto-generated **API reference**
that documents both implementations side by side, statically extracted at
build time from each toolbox's source (pulled in as git submodules). See
[API reference (MATLAB + Python)](#api-reference-matlab--python) below.

## Repository layout

```
gecko-docs/
├── .readthedocs.yaml       # Read the Docs build configuration (incl. submodules)
├── .gitmodules              # GECKO + geckopy submodule definitions
├── requirements-sphinx.txt  # Python build dependencies
├── README.md                # This file
├── GECKO/                   # submodule: CompMetEng/GECKO        (MATLAB source)
├── geckopy/                  # submodule: CompMetEng/geckopy      (Python source)
├── scripts/
│   ├── api_index.py             # shared MATLAB/Python source-collection helpers
│   ├── gen_api_pages_sphinx.py  # generates docs/api/ and docs/matlab-vs-python.md
│   └── curated_pairs.yml        # hand-curated name pairs the generator can't match automatically
└── docs/
    ├── conf.py               # Sphinx configuration
    ├── index.md               # Landing page
    ├── migrate.md, gecko3-to-gecko4.md, gecko-to-geckopy.md
    ├── references.md          # Citations
    ├── installation/index.md
    ├── guide/                 # Introduction, Getting started, and the task pages
    └── api/                   # auto-generated bilingual API reference (not checked in)
```

## Building locally

```bash
# from the repository root
git submodule update --init --recursive   # fetch the GECKO + geckopy sources
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install -r requirements-sphinx.txt
sphinx-build -b html docs docs/_build/html
```

The `git submodule update --init` step is required: without it the `GECKO/`
and `geckopy/` source trees are empty and the API reference builds with no
functions in it.

Open `docs/_build/html/index.html` in a browser. There is no live-reload dev
server configured; re-run `sphinx-build` after editing.

## Hosting on Read the Docs

1. Push this folder to a GitHub, GitLab or Bitbucket repository.
2. Sign in at https://readthedocs.org/ and import the repository.
3. Read the Docs detects `.readthedocs.yaml` and builds the site
   automatically on every push.

Read the Docs initializes the git submodules automatically because
`.readthedocs.yaml` sets `submodules.include: all`, so the API reference is
built on every push without any extra configuration.

## API reference (MATLAB + Python)

`docs/api/` documents both toolboxes side by side, plus
`docs/matlab-vs-python.md`, a generated table pairing every function that
exists in both. All of it is written by `scripts/gen_api_pages_sphinx.py`
at build time (run from `docs/conf.py`'s `setup()` hook), which extracts
MATLAB help blocks and Python docstrings directly from source: no MATLAB
runtime, no installed geckopy package, and no live-rendering plugin
involved. Nothing under `docs/api/` or `docs/matlab-vs-python.md` is
checked into the repository or should be hand-edited; regenerate by
rebuilding. Function pairs that don't match by name alone (geckopy renamed
part of the API during the port) are recorded in `scripts/curated_pairs.yml`,
which is validated against the live source at build time.

Sources are git submodules pinned to each project's tracked development
branch (see `.gitmodules`):

- `GECKO/`   — [CompMetEng/GECKO](https://github.com/CompMetEng/GECKO) (MATLAB)
- `geckopy/` — [CompMetEng/geckopy](https://github.com/CompMetEng/geckopy) (Python)

To refresh the reference against the latest upstream code:

```bash
git submodule update --remote --recursive
git add GECKO geckopy
git commit -m "chore: update submodules to latest tracked branches"
```

(`.github/workflows/update-submodules.yml` does this automatically on a
daily schedule.)

## License and attribution

The GECKO source code is released under the MIT license at
https://github.com/CompMetEng/GECKO. The scientific content summarized
in these pages is the work of the original authors; see
[Citations](docs/references.md) for the papers to cite.
