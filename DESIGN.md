# GECKO documentation: design and content guide

This document is the source of intent. It describes how the site should be designed and what it should contain, not the current state of `develop`. When the site and this document disagree, the site is brought in line, or the decision is recorded here first. New decisions go in the decisions log; resolved items leave "Open questions".

The site follows the `docs-site` standard of [CompMetEng/skills](https://github.com/CompMetEng/skills). Differences from the standard are listed in section 6.

Before any work in this repository, fetch all remotes of the repository and of every submodule. The submodules are updated often and automatically, so a local checkout becomes stale quickly:

```bash
git fetch --all --prune
git checkout develop && git pull --ff-only
git submodule sync --recursive
git submodule update --init --recursive
```

## 1. Purpose

One documentation site for **GECKO**, the MATLAB toolbox, and **geckopy**, its Python port, for reconstructing, simulating and analyzing enzyme-constrained genome-scale metabolic models (ecModels). A user learns a task once and applies it in either language. Readers are researchers who build ecModels from a genome-scale model, and many of them are not native English speakers.

## 2. Principles

- **Both languages together.** MATLAB and Python are presented side by side: paired API entries and linked code tabs.
- **Single source of truth.** The API reference is generated from the function help in the toolbox sources, which are git submodules tracking the branches in `.gitmodules`.
- **Low maintenance.** What can be generated is generated at build time. Prose pages are short and have one job.
- **Curated content.** A small set of correct pages is preferred to a large set of stale ones.
- **Literal prose.** The writing rules of `CONTRIBUTING.md` apply to every page, because many readers are not native English speakers.

## 3. Technical foundation

- Sphinx, MyST Markdown, PyData theme, `sphinx-design`, `sphinx-copybutton`. Read the Docs builds with warnings as errors.
- Submodules: `GECKO` (branch `develop`) and `geckopy` (branch `develop`).
- The API reference is generated at build time by `scripts/gen_api_pages.py`, called from `docs/conf.py`. The scripts in `scripts/` are copies of `docs-site/scripts` in CompMetEng/skills; what is specific to this site is in `scripts/project.yml`, `scripts/curated_pairs.yml` and `scripts/known_names.txt`. A change to a script is made in the plugin first.
- `.github/workflows/docs-build.yml` runs `scripts/check_site.py`, the build with `-W`, the name check and the link check.

## 4. Site structure

- **Home** (`docs/index.md`), in this order:
  - the hero (logo, tag "MATLAB & Python", a tagline that names GECKO and geckopy) and the banner above the page, which names the documented version, says that it is a pre-release, names the stable version with the way to install it, and links the upgrade page and the release notes;
  - *Installation*: tabs `MATLAB (git)`, `MATLAB (Add-Ons)`, `Python (pip)` and `Python (git)`, MATLAB first. The git tabs say that they install the development version and link the tags page of the repository for a release. The Python tabs say why `pip install` needs `--pre` (without it, pip installs geckopy 2.0.2, an unrelated earlier package). The MATLAB tabs say that GECKO needs RAVEN 3 and that the Add-On installs GECKO 3. One link leads to the Installation page;
  - *Features*: cards, each linking into the guide, with sentences of one grammar;
  - *Quick start*: an example in both languages, MATLAB first, that links [Build an ecModel](docs/guide/first-ecmodel.md) and the ecModels repository for the model it loads, and says what the project folder holds;
  - *Documentation*: cards for Installation, Build an ecModel, Guide, API reference, MATLAB and Python, Migration and Release notes, each with a sentence that names what the page holds;
  - *Help*: two cards, one to report a bug or request a feature and one to ask a usage question, each with a link per repository.

  The home page holds no paper, no licence text, no DOI and no source-code section: the papers and the way to cite are on the references page, and the repositories are the two icons of the navbar. Every page ends with a footer that has the link to the Kerkhoven lab (<https://www.kerkhovenlab.eu>) with the mark of the lab, and a link to raven-docs with its icon, and nothing else.
- **Installation** (`docs/installation/`), at the root of the sidebar before the guide. The sub-headings are Requirements, Install, Verify, Upgrade, Remove and Solver, in the order that the reader needs them. The solver section says why GLPK is not recommended for ecModels.
- **Guide** (`docs/guide/`): *Start* (Introduction), *Quick path* (Build an ecModel: a working ecModel with the default settings), *Workflow* (the workflow overview), *Decisions* (one page per choice the user makes, in the order the user meets it: the ecModel structure, the kcat sources, custom kcats, the protein pool, the kcat tuning, the advanced kcat tuning, proteomics, relaxing proteomics, analysis, engineering targets, context-specific ecModels, enzyme usage and bottlenecks), *Background* (the YAML format, the files of the data folder, the experimental data, the model adapter parameters, basic model operations, the project format and the kcat assignment). The guide index states its purpose, then the table of pages, then the notes. A decision page sets out the options (what each needs and changes), gives a recommendation where a source supports one, and then the procedure of each option. The guide describes GECKO 4 only; the migration pages describe the changes against GECKO 3. The Introduction and the YAML, data folder, model adapter, project format and kcat assignment pages explain a concept or a format and are marked `<!-- docs-site: concept-page -->`, so they need no function table.
- **Workflow** (`docs/guide/workflow.md`): the order of the guide pages as one Mermaid diagram per language, with a PDF of each diagram (`docs/_static/workflow-matlab.pdf`, `workflow-python.pdf`) and a PNG of the overview.
- **Migration** (the navbar label; `migrate.md`): `gecko3-to-gecko4.md`, `gecko3-upgrade-project.md` and `gecko-to-geckopy.md`.
- **API reference** (`docs/api/`): a hand-written index, then generated MATLAB pages by folder and Python pages by package, and `docs/matlab-vs-python.md`.
- **Release notes** (`docs/release-notes/`): the notes of GECKO and of geckopy.
- **References** (`docs/references.md`): the papers, then a short "How to cite" paragraph that names the Python packages and the version and states that the paper of GECKO 3 describes GECKO 3.
- **Sidebar order**: Installation, Guide, API reference, Migration, Release notes, References.
- **Links to raven-docs** use the intersphinx inventory of that site. The inventory is optional: a build that cannot fetch it warns and does not fail.

## 5. Conventions

- Code tabs are labelled MATLAB and Python, linked, with MATLAB first. The install tabs are labelled `MATLAB (git)`, `MATLAB (Add-Ons)`, `Python (pip)` and `Python (git)`, with MATLAB first.
- Python names go in the Functions table or the tab, not in prose. Text outside a tab reads the same in both languages; where a name differs, the table of the page lists it. The existing `(Python: name)` parentheticals on the guide pages are replaced when a page is next edited.
- A troubleshooting row names the error identifier when one exists, so that a search for the identifier finds the row. There is no page of common errors.
- MATLAB `camelCase` and Python `snake_case` are paired by normalised name; pairs that differ are in `scripts/curated_pairs.yml`.
- Functions that resolve to cobrapy are marked with the cobrapy badge.
- Prose follows `CONTRIBUTING.md`. No mention of AI tools.

## 6. Differences from the standard

| Difference | Reason |
| --- | --- |
| `sphinx.ext.mathjax` in `extensions` | the Introduction contains equations |
| `sphinxcontrib.mermaid` in `extensions`, with `mermaid-zoom.js` | the workflow overview is a Mermaid diagram |
| `custom.css` sets a thinner header (3.4 rem), a page width of 104 rem, an article width of 80 em and a sidebar width of 18% | the workflow diagrams and the wide tables need the width; the layout is not part of the standard and stays a difference of this site until the standard adopts it |
| Home headings Installation, Features, Quick start, Documentation and Help, and a footer | decided for both documentation sites on 2026-11-23; the plugin template follows |
| The Functions table calls its last column "Note" and the troubleshooting section is a table (Problem, Possible reason, Solution) | raven-docs uses "Purpose" and a warning admonition; each site keeps one form |

## 7. Open questions

- **Link check.** `docs-build.yml` does not fail on the link check yet; the state of the external links was not known when the check was added.
- **Examples are not run.** The code blocks of the guide are written from the source and have not been executed. `scripts/run_examples.py` exists, and no examples workflow runs it yet.
- **`(Python: name)` in prose.** The guide pages hold about 120 parentheticals that name the Python function in text that reads the same in both languages (section 5). They are replaced when a page is next edited.

## 8. Decisions log

- 2026-10-24: the site follows the `docs-site` standard. `requirements-sphinx.txt` is `requirements.txt` and `gen_api_pages_sphinx.py` is `gen_api_pages.py`. The brand colours are `#43684B` for tabs and borders and `#2D6E3B` for links, with `#5F936A` and `#87d398` in dark mode, set as `--pst-color-primary`, `--pst-color-link` and `--site-accent`. Logos and the favicon are in `docs/_static` only, with a white logo for dark mode. The API pages use the numpydoc rendering and show signatures.
- 2026-10-24: Read the Docs and CI build with `-W`. The submodule update opens a pull request against `develop` instead of pushing to it.
- 2026-10-24: `docs/_static/gecko-logo-white.png`, the logo for dark mode, was made from `gecko-logo.png` by making every pixel white and keeping the alpha channel, the way `gecko-icon-white.png` was made. The maintainer accepted it. The unused `gecko-icon-color.png` and `gecko-icon-white.png` of the former `docs/assets` folder were removed and are in the history.
- 2026-10-24: the language of the code tabs (MATLAB or Python) is remembered in `localStorage` by `docs/_static/language-sync.js`, so it applies to every tab on a page, to the next pages, to new browser tabs and to later visits, and install tabs follow it. sphinx-design alone keeps the choice in `sessionStorage` for one browser tab.
- **Broken links and code owner:** `.github/workflows/link-issue.yml` checks the external links every Wednesday and keeps one open issue labelled `broken-links` with the broken ones; it closes the issue when none is broken. `.github/CODEOWNERS` names `@edkerk` as the owner of the repository, who is asked to review every pull request.
- **Rules for every session:** `CLAUDE.md` holds the baseline rules of the `craft` plugin, `.claude/settings.json` enables the `craft` and `docs-site` plugins and turns on the hooks in `.githooks`, and `.github/workflows/repo-hygiene.yml` runs `.github/scripts/repo_hygiene.py` on every pull request. They refuse a tool author, trailer, mention, branch name or pull request footer.
- 2026-11-11: the guide no longer follows the order of the GECKO 3 Nature Protocols pipeline. GECKO 4 is configured by `model_adapter.toml`, and `assignKcats` replaces the manual steps of gathering, merging and applying kcats, so most of the work is choosing settings. The guide has one quick-path page and one page per decision; each page was written from the code, not edited from the earlier pages.
- 2026-11-11: the table of approximate timings is dropped, because it had no source. The workflow diagrams of the GECKO 3 protocol are dropped as well; on 2026-11-13 the page `guide/workflow.md` was written again with diagrams in the order of the guide pages, with `docs/_static/workflow-matlab.pdf`, `workflow-python.pdf` and `workflow-overview.png`. The page stays.
- 2026-11-11: the guide calls `sensitivityTuning` the standard kcat tuning (it needs one maximum growth rate) and `cmaesKcatTuning` the advanced kcat tuning (it fits maximum growth rates and exchange fluxes of one or more conditions). They are alternatives; neither is called legacy. The API category of `src/kcat_tuning` is named kcat tuning.
- 2026-11-11: DLKcat predictions are described as coming from the DLKcat method of OpenKineticsPredictor, which `kcatsFromDLKcat` uses when `data/DLKcat.tsv` does not exist; the local Docker run is described as the older method in one admonition.
- 2026-11-11: the guide describes KinForm-H as the default OpenKineticsPredictor method, which the presets' `okp` stage uses, as GECKO and geckopy set it. Where the guide cites the measured comparison of the presets, it states that KinForm-H was not compared separately. Functions that GECKO deprecates (`updateProtPool`, `mergeDLKcatAndFuzzyKcats`, adapter classes) appear on guide pages only in troubleshooting, and on the migration page.
- 2026-11-23: landing page and navigation. The home page holds no paper, no licence text and no source-code section; the papers and a "How to cite" paragraph are on the references page. The home sections are Installation, Features, Quick start, Documentation and Help, in this order, with the install tabs and the Documentation cards of section 4. A banner names the stable version and links the upgrade page and the release notes. The footer holds the link to the lab and the link to raven-docs. Installation is at the root of the sidebar before the guide, and the navbar label of the migration pages is "Migration". The quick start links out for the model it loads. Links to raven-docs use its intersphinx inventory, and a missing inventory is a warning. The troubleshooting form (table), the Functions table header ("Note") and the `(Python: name)` parentheticals stay as they are. The guide pages do not get a page of common errors. The licence of GECKO and geckopy is the GNU General Public License v3. The pages of this repository carry no cluster commands.
