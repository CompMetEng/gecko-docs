# GECKO

<div class="site-hero">
  <div class="site-logo-row">
    <img class="site-logo-light" src="_static/gecko-logo.png" alt="GECKO">
    <img class="site-logo-dark" src="_static/gecko-logo-white.png" alt="GECKO">
    <p class="site-tag">MATLAB &amp; Python</p>
  </div>
  <p class="site-tagline">Reconstruction, simulation and analysis of enzyme-constrained metabolic models (ecModels): a MATLAB toolbox built on RAVEN, and geckopy, a Python port built on cobrapy.</p>
</div>

## Install

::::{tab-set}
:::{tab-item} Python (PyPI)

```bash
pip install --pre geckopy
```

`--pre` is required: the GECKO 4 releases of geckopy and the releases of raven-toolbox that it depends on are pre-releases. Without `--pre`, pip installs geckopy 2.0.2, an earlier and unrelated package of the same name.
:::
:::{tab-item} Python (Git)

```bash
pip install \
    git+https://github.com/CompMetEng/raven-toolbox.git@develop \
    git+https://github.com/CompMetEng/geckopy.git@develop
```

Installs the `develop` branch of both packages, which is ahead of the latest PyPI release.
:::
:::{tab-item} MATLAB (git)

```bash
git clone --depth=1 https://github.com/CompMetEng/GECKO
```

Then run `GECKOInstaller.install` in MATLAB. The clone is the `develop` branch; `--branch <tag>` selects a release tag listed on the [tags page](https://github.com/CompMetEng/GECKO/tags).
:::
:::{tab-item} MATLAB (Add-Ons)

Home → Add-Ons → Get Add-Ons → search "GECKO Toolbox". The Add-On installs a GitHub release; the latest, v3.2.5, is GECKO 3 (see [GECKO 3 to GECKO 4](gecko3-to-gecko4.md#staying-on-gecko-3)). GECKO 4 is a pre-release, installed with git or from a ZIP archive.
:::
::::

## Features

::::{grid} 1 2 3 3

:::{grid-item-card} Enzyme constraints
Convert a conventional GEM into an ecModel by bounding reaction rates with enzyme kcat and abundance.
:::

:::{grid-item-card} Proteomics integration
Constrain the usage of individual enzymes with absolute proteomics measurements.
:::

:::{grid-item-card} Light ecModels
A smaller, faster-simulating ecModel variant for when full proteome coverage is not needed.
:::

::::

## Quick start

::::{tab-set}
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ModelAdapter, load_ec_model

# load a previously built ecModel from a project folder
adapter = ModelAdapter.from_folder("path/to/project")
model = load_ec_model("ecYeastGEM.yml", adapter)

# set growth as the objective
model.objective = "r_2111"

# run FBA -- simulation comes from cobrapy, unchanged
sol = model.optimize()
print(f"Growth rate: {sol.objective_value:.4f} h⁻¹")
```
:::
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
% load a previously built ecModel from a project folder
ModelAdapterManager.setDefault('path/to/project');
model = loadEcModel('ecYeastGEM.yml');

% set growth as the objective
model = setParam(model, 'obj', 'r_2111', 1);

% run FBA
sol = solveLP(model);
fprintf('Growth rate: %.4f h-1\n', sol.f);
```
:::
::::

## Documentation

::::{grid} 1 2 2 2

:::{grid-item-card} Build an ecModel
:link: guide/first-ecmodel
:link-type: doc

A working ecModel with the default settings, from a project folder to a saved model, in MATLAB and Python.
:::

:::{grid-item-card} Upgrade a GECKO 3 project
:link: gecko3-upgrade-project
:link-type: doc

Convert a GECKO 3 project and its ecModel to project format 4 with `upgradeGECKOproject` or `geckopy upgrade`.
:::

:::{grid-item-card} Installation
:link: installation/index
:link-type: doc

Set up GECKO in MATLAB or geckopy in Python, the solver and Docker for DLKcat.
:::

:::{grid-item-card} GECKO and geckopy
:link: gecko-to-geckopy
:link-type: doc

Corresponding objects, names that differ, functions of one implementation and differences in behaviour.
:::

::::

## Citing GECKO

Publications that use GECKO cite:

> Chen, Y., Gustafsson, J., Tafur Rangel, A., Anton, M., Domenzain, I., Kittikunapong, C., Li, F., Yuan, L., Nielsen, J. & Kerkhoven, E. J. **Reconstruction, simulation and analysis of enzyme-constrained metabolic models using GECKO Toolbox 3.0.** *Nature Protocols* **19**, 629-667 (2024). <https://doi.org/10.1038/s41596-023-00931-7>

See [Citations](references.md) for the full list, including papers that have used this protocol.

## Source code

GECKO is publicly available under the MIT licence at <https://github.com/CompMetEng/GECKO>, archived at <https://doi.org/10.5281/zenodo.7699818>. geckopy, the Python port, is at <https://github.com/CompMetEng/geckopy>.

## Getting help

Report a bug or request a feature against whichever implementation it concerns; ask a usage question in either repository's Discussions.

| Implementation | Issues | Discussions |
|---|---|---|
| GECKO (MATLAB) | [github.com/CompMetEng/GECKO/issues](https://github.com/CompMetEng/GECKO/issues) | [github.com/CompMetEng/GECKO/discussions](https://github.com/CompMetEng/GECKO/discussions) |
| geckopy (Python) | [github.com/CompMetEng/geckopy/issues](https://github.com/CompMetEng/geckopy/issues) | [github.com/CompMetEng/geckopy/discussions](https://github.com/CompMetEng/geckopy/discussions) |

```{toctree}
:hidden:

migrate
guide/index
api/index
references
```
