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

`--pre` is required while geckopy and raven-toolbox are pre-releases on
PyPI.
:::
:::{tab-item} Python (Git)

```bash
pip install \
    git+https://github.com/CompMetEng/raven-toolbox.git@develop \
    git+https://github.com/CompMetEng/geckopy.git@develop
```

Tracks the `develop` branch of both packages, ahead of the latest PyPI
release.
:::
:::{tab-item} MATLAB (Add-Ons)

Home → Add-Ons → Get Add-Ons → search "GECKO Toolbox".
:::
:::{tab-item} MATLAB (git)

```bash
git clone --depth=1 https://github.com/CompMetEng/GECKO
```

Then run `GECKOInstaller.install` in MATLAB.
:::
::::

## Key features

::::{grid} 1 2 3 3

:::{grid-item-card} Enzyme constraints
Convert a conventional GEM into an ecModel by bounding reaction rates with
enzyme kcat and abundance.
:::

:::{grid-item-card} Proteomics integration
Constrain individual enzyme usage with absolute or relative proteomics
measurements.
:::

:::{grid-item-card} Light ecModels
A smaller, faster-simulating ecModel variant for when full proteome coverage
isn't needed.
:::

::::

## Quick start

::::{tab-set}
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import load_ec_model

# load a previously built ecModel
model = load_ec_model("ecYeastGEM.yml")

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
% load a previously built ecModel
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

:::{grid-item-card} Guide
:link: guide/index
:link-type: doc

Task-focused pages covering the full ecModel pipeline, MATLAB and Python
side by side.
:::

:::{grid-item-card} API reference
:link: api/index
:link-type: doc

Complete function reference for both GECKO (MATLAB) and geckopy (Python).
:::

:::{grid-item-card} Installation
:link: installation/index
:link-type: doc

Set up GECKO in MATLAB or geckopy in Python, plus the Gurobi/SoPlex solver
and Docker for DLKcat.
:::

:::{grid-item-card} GECKO vs. geckopy
:link: gecko-to-geckopy
:link-type: doc

Which to use for what, what only one of them has, and where the same
function gives a different answer.
:::

::::

## Citing GECKO

If you use GECKO in your research, please cite:

> Chen, Y., Gustafsson, J., Tafur Rangel, A., Anton, M., Domenzain, I.,
> Kittikunapong, C., Li, F., Yuan, L., Nielsen, J. & Kerkhoven, E. J.
> **Reconstruction, simulation and analysis of enzyme-constrained metabolic
> models using GECKO Toolbox 3.0.** *Nature Protocols* **19**, 629-667
> (2024). <https://doi.org/10.1038/s41596-023-00931-7>

See [Citations](references.md) for the full list, including key papers that
have used this protocol.

## Source code

GECKO is publicly available under the MIT license at
<https://github.com/CompMetEng/GECKO>, archived at
<https://doi.org/10.5281/zenodo.7699818>. geckopy, the Python port, is at
<https://github.com/CompMetEng/geckopy>.

## Getting help

Report a bug or request a feature against whichever implementation it
concerns; ask a usage question in either repository's Discussions.

| | Issues | Discussions |
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
