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

- **Home** (`docs/index.md`): one sentence on GECKO and geckopy, the install tabs for both languages, key features, quick start, links to the papers.
- **Installation** (`docs/installation/`).
- **Guide** (`docs/guide/`): *Start* (Introduction, Installation), *Quick path* (Build an ecModel: a working ecModel with the default settings), *Decisions* (one page per choice the user makes, in the order the user meets it: the ecModel structure, the kcat sources, custom kcats, the protein pool, the kcat tuning, the advanced kcat tuning, proteomics, relaxing proteomics, analysis, engineering targets, context-specific ecModels, enzyme usage and bottlenecks), *Background* (the YAML format, the files of the data folder, the model adapter parameters, basic model operations). A decision page sets out the options (what each needs and changes), gives a recommendation where a source supports one, and then the procedure of each option. The guide describes GECKO 4 only; the migration pages describe the changes against GECKO 3. The Introduction and the YAML, data folder and model adapter pages explain a concept or a format and are marked `<!-- docs-site: concept-page -->`, so they need no function table.
- **Migration**: `migrate.md`, `gecko3-to-gecko4.md` and `gecko-to-geckopy.md`.
- **API reference** (`docs/api/`): a hand-written index, then generated MATLAB pages by folder and Python pages by package, and `docs/matlab-vs-python.md`.
- **References** (`docs/references.md`): the papers to cite.

## 5. Conventions

- Code tabs are labelled MATLAB and Python, linked, with MATLAB first.
- MATLAB `camelCase` and Python `snake_case` are paired by normalised name; pairs that differ are in `scripts/curated_pairs.yml`.
- Functions that resolve to cobrapy are marked with the cobrapy badge.
- Prose follows `CONTRIBUTING.md`. No mention of AI tools.

## 6. Differences from the standard

| Difference | Reason |
| --- | --- |
| `sphinx.ext.mathjax` in `extensions` | the Introduction contains equations |

## 7. Open questions

- **Unresolved names.** `scripts/check_names.py` reports 121 distinct names on the guide pages that are neither a top-level function or class of the toolboxes nor in `scripts/known_names.txt`. Most are keyword arguments, struct fields, YAML keys and variables of the examples; four (`cap_usage`, `from_folder`, `shadow_price`, `upper_bound`) are methods or properties. Someone who knows the pages has to sort them, and allow-list the ones that are not functions, before the check can block CI.
- **Link check.** `docs-build.yml` does not fail on the link check yet; the state of the external links was not known when the check was added.
- **Site scripts.** `scripts/check_site.py` and `scripts/autolink.py` differ from `docs-site/scripts` on main (the expected section names), and `check_style.py` and `run_examples.py` are missing. Until they are copied, `check_site.py` reports the section names "Functions on this page" and "What can go wrong" as missing on pages that use "Functions" and "Troubleshooting".
- **Examples are not run.** The code blocks of the guide are written from the source and have not been executed; the site has no `run_examples.py` and no examples workflow yet.

## 8. Decisions log

- 2026-10-24: the site follows the `docs-site` standard. `requirements-sphinx.txt` is `requirements.txt` and `gen_api_pages_sphinx.py` is `gen_api_pages.py`. The brand colours are `#43684B` for tabs and borders and `#2D6E3B` for links, with `#5F936A` and `#87d398` in dark mode, set as `--pst-color-primary`, `--pst-color-link` and `--site-accent`. Logos and the favicon are in `docs/_static` only, with a white logo for dark mode. The API pages use the numpydoc rendering and show signatures.
- 2026-10-24: Read the Docs and CI build with `-W`. The submodule update opens a pull request against `develop` instead of pushing to it.
- 2026-10-24: `docs/_static/gecko-logo-white.png`, the logo for dark mode, was made from `gecko-logo.png` by making every pixel white and keeping the alpha channel, the way `gecko-icon-white.png` was made. The maintainer accepted it. The unused `gecko-icon-color.png` and `gecko-icon-white.png` of the former `docs/assets` folder were removed and are in the history.
- 2026-10-24: the language of the code tabs (MATLAB or Python) is remembered in `localStorage` by `docs/_static/language-sync.js`, so it applies to every tab on a page, to the next pages, to new browser tabs and to later visits, and install tabs follow it. sphinx-design alone keeps the choice in `sessionStorage` for one browser tab.
- **Broken links and code owner:** `.github/workflows/link-issue.yml` checks the external links every Wednesday and keeps one open issue labelled `broken-links` with the broken ones; it closes the issue when none is broken. `.github/CODEOWNERS` names `@edkerk` as the owner of the repository, who is asked to review every pull request.
- **Rules for every session:** `CLAUDE.md` holds the baseline rules of the `craft` plugin, `.claude/settings.json` enables the `craft` and `docs-site` plugins and turns on the hooks in `.githooks`, and `.github/workflows/repo-hygiene.yml` runs `.github/scripts/repo_hygiene.py` on every pull request. They refuse a tool author, trailer, mention, branch name or pull request footer.
- 2026-11-11: the guide no longer follows the order of the GECKO 3 Nature Protocols pipeline. GECKO 4 is configured by `model_adapter.toml`, and `assignKcats` replaces the manual steps of gathering, merging and applying kcats, so most of the work is choosing settings. The guide has one quick-path page and one page per decision; each page was written from the code, not edited from the earlier pages.
- 2026-11-11: the workflow diagrams (`docs/_static/workflow-*.pdf`, `workflow-overview.png`, the Mermaid page `guide/workflow.md`) and the table of approximate timings are removed. The diagrams showed the order of the GECKO 3 protocol, and the timings had no source.
- 2026-11-11: the guide calls `sensitivityTuning` the standard kcat tuning (it needs one maximum growth rate) and `cmaesKcatTuning` the advanced kcat tuning (it fits maximum growth rates and exchange fluxes of one or more conditions). They are alternatives; neither is called legacy. The API category of `src/kcat_tuning` is named kcat tuning.
- 2026-11-11: DLKcat predictions are described as coming from the DLKcat method of OpenKineticsPredictor, which `kcatsFromDLKcat` uses when `data/DLKcat.tsv` does not exist; the local Docker run is described as the older method in one admonition.
- 2026-11-11: the guide describes KinForm-H as the default OpenKineticsPredictor method and the presets' `okp` stage with KinForm-H alone, as GECKO and geckopy set it. Where the guide cites the measured comparison of the presets, it states that the comparison combined eight OKP methods. Functions that GECKO deprecates (`updateProtPool`, `mergeDLKcatAndFuzzyKcats`, adapter classes) appear on guide pages only in troubleshooting, and on the migration page.
