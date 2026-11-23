# GECKO

<div class="site-hero">
  <div class="site-logo-row">
    <img class="site-logo-light" src="_static/gecko-logo.png" alt="GECKO">
    <img class="site-logo-dark" src="_static/gecko-logo-white.png" alt="GECKO">
    <p class="site-tag">MATLAB &amp; Python</p>
  </div>
  <p class="site-tagline">Reconstruction, simulation and analysis of enzyme-constrained metabolic models (ecModels): a MATLAB toolbox built on RAVEN, and geckopy, a Python package built on cobrapy.</p>
</div>

GECKO exists as a MATLAB toolbox and as the Python package geckopy. This site documents both.

## Installation

::::{tab-set}
:::{tab-item} MATLAB (git)

```bash
git clone --depth=1 https://github.com/CompMetEng/GECKO
```

The clone is the development version, the `develop` branch. The [tags page](https://github.com/CompMetEng/GECKO/tags) lists the releases, and `--branch <tag>` selects one. Run `GECKOInstaller.install` in MATLAB. GECKO 4 needs RAVEN 3.0.0b3 or later.
:::
:::{tab-item} MATLAB (Add-Ons)

Home, Add-Ons, Get Add-Ons, search for "GECKO Toolbox". The Add-On installs the latest stable release, GECKO 3.2.5 (see [GECKO 3 to GECKO 4](gecko3-to-gecko4.md#staying-on-gecko-3)). GECKO 4, which this site documents, is a pre-release and is installed with git or from a ZIP archive of a tag. RAVEN 2.x, which the RAVEN Add-On installs, does not work with GECKO 4.
:::
:::{tab-item} Python (pip)

```bash
pip install --pre geckopy
```

`--pre` is required: the GECKO 4 releases of geckopy and the releases of raven-toolbox that it depends on are pre-releases. Without `--pre`, pip installs geckopy 2.0.2, an earlier and unrelated package of the same name.
:::
:::{tab-item} Python (git)

```bash
pip install \
    git+https://github.com/CompMetEng/raven-toolbox.git@develop \
    git+https://github.com/CompMetEng/geckopy.git@develop
```

The command installs the development version, the `develop` branch of both packages, which is ahead of the latest PyPI release. The tags pages of [raven-toolbox](https://github.com/CompMetEng/raven-toolbox/tags) and [geckopy](https://github.com/CompMetEng/geckopy/tags) list the releases, and `@<tag>` in place of `@develop` selects one.
:::
::::

[Installation](installation/index.md) lists the requirements, how to verify, upgrade and remove an installation, and how to choose a solver.

## Features

::::{grid} 1 2 3 3

:::{grid-item-card} Enzyme constraints
:link: guide/ecmodel-structure
:link-type: doc

Converts a conventional GEM into a full or a light ecModel by bounding reaction rates with enzyme kcat and abundance.
:::

:::{grid-item-card} kcat sources and tuning
:link: guide/kcat-sources
:link-type: doc

Assigns a kcat to each reaction from source files in a set order, and tunes the kcats that limit growth to measured data.
:::

:::{grid-item-card} Proteomics integration
:link: guide/proteomics
:link-type: doc

Constrains the usage of individual enzymes with absolute proteomics measurements.
:::

:::{grid-item-card} Enzyme usage
:link: guide/enzyme-usage
:link-type: doc

Lists the enzymes that a solution uses and the enzymes that limit the objective.
:::

:::{grid-item-card} Engineering targets
:link: guide/engineering-targets
:link-type: doc

Finds the reactions and genes to change for the production of a compound.
:::

:::{grid-item-card} Context-specific ecModels
:link: guide/context-ecmodel
:link-type: doc

Trims a generic ecModel to the reactions and genes of a tissue, cell line or strain.
:::

::::

## Quick start

The example loads the ecModel of *Saccharomyces cerevisiae* from a project folder, sets growth as the objective and runs FBA. The project folder `ecYeastGEM` is in the [ecModels repository](https://github.com/SysBioChalmers/ecModels/tree/gecko4/ecYeastGEM), and [Build an ecModel](guide/first-ecmodel.md) makes such a folder from a genome-scale model. The folder holds `model_adapter.toml`, the input data in `data/` and the ecModel in `models/ecYeastGEM.yml`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
% load a previously built ecModel from a project folder
ModelAdapterManager.setDefault('path/to/ecYeastGEM');
model = loadEcModel('ecYeastGEM.yml');

% set growth as the objective
model = setParam(model, 'obj', 'r_2111', 1);

% run FBA
sol = solveLP(model);
fprintf('Growth rate: %.4f h-1\n', sol.f);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ModelAdapter, load_ec_model

# load a previously built ecModel from a project folder
adapter = ModelAdapter.from_folder("path/to/ecYeastGEM")
model = load_ec_model("ecYeastGEM.yml", adapter)

# set growth as the objective
model.objective = "r_2111"

# run FBA; simulation comes from cobrapy
sol = model.optimize()
print(f"Growth rate: {sol.objective_value:.4f} h-1")
```
:::
::::

## Documentation

::::{grid} 1 2 2 2

:::{grid-item-card} Build an ecModel
:link: guide/first-ecmodel
:link-type: doc

A working ecModel with the default settings, from a project folder to a saved model.
:::

:::{grid-item-card} Guide
:link: guide/index
:link-type: doc

One page per choice, from the ecModel structure to the analysis, with MATLAB and Python tabs.
:::

:::{grid-item-card} API reference
:link: api/index
:link-type: doc

The functions of GECKO and geckopy, generated from their sources.
:::

:::{grid-item-card} Installation
:link: installation/index
:link-type: doc

The requirements, the installation, the upgrade and the removal of GECKO and geckopy, and the choice of a solver.
:::

:::{grid-item-card} MATLAB and Python
:link: matlab-vs-python
:link-type: doc

The name of each function in GECKO and in geckopy.
:::

:::{grid-item-card} Migration
:link: migrate
:link-type: doc

The changes from GECKO 3 to GECKO 4, the upgrade of a project, and the differences between GECKO and geckopy.
:::

:::{grid-item-card} Release notes
:link: release-notes/index
:link-type: doc

The changes of each release of GECKO and geckopy.
:::

::::

## Help

Report a bug or request a feature against the implementation that it concerns; ask a usage question in the Discussions of either repository.

| Repository | Issues | Discussions |
| --- | --- | --- |
| GECKO (MATLAB) | [Issues](https://github.com/CompMetEng/GECKO/issues) | [Discussions](https://github.com/CompMetEng/GECKO/discussions) |
| geckopy (Python) | [Issues](https://github.com/CompMetEng/geckopy/issues) | [Discussions](https://github.com/CompMetEng/geckopy/discussions) |

```{toctree}
:hidden:

installation/index
guide/index
api/index
migrate
release-notes/index
references
```
