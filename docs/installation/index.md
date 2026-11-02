---
icon: material/folder-open
---

# Installation

GECKO is available as a MATLAB toolbox and as the Python package geckopy. Both implement the same procedure and reconstruct, simulate and analyse the same ecModels (see [GECKO and geckopy](../gecko-to-geckopy.md)). GECKO 4 and geckopy 4 are pre-releases.

## Equipment

A computer running macOS, Windows or Linux, with an internet connection to reach [KEGG](https://www.genome.jp/kegg/), [UniProt](https://www.uniprot.org/), [PubChem](https://pubchem.ncbi.nlm.nih.gov/) and [GitHub](https://github.com/CompMetEng/GECKO/). Data from these sources can also be downloaded or reconstructed manually elsewhere; GECKO functions download them directly.

The starting point is a conventional constraint-based metabolic model, at genome scale or smaller, in SBML format L3V1 FBCv2. The procedure works on any valid model, whether or not it belongs to a model organism.

## Software

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

- **MATLAB**. The test workflow of GECKO runs MATLAB R2024b; the repository states no minimum version
  ([MathWorks](https://mathworks.com/products/matlab.html)). No additional MathWorks toolboxes are required.
- **RAVEN toolbox** version 3 or later ([repository](https://github.com/CompMetEng/RAVEN)), which provides the reconstruction functions GECKO builds on, and some of the functions used to simulate and analyse ecModels. GECKO 4 does not support RAVEN 2.
:::
:::{tab-item} 🐍 Python
:sync: python

- **Python** 3.11 or above.
- **geckopy** ([repository](https://github.com/CompMetEng/geckopy)), built on [cobrapy](https://github.com/opencobra/cobrapy) for the constraint-based modelling layer and [raven-toolbox](https://github.com/CompMetEng/raven-toolbox) (the Python port of RAVEN) for model-manipulation primitives and ecModel YAML input and output. Installing geckopy installs both dependencies.
:::
::::

Both toolboxes also need a linear-programming solver (see [Choosing a solver](#choosing-a-solver) below) and, for DLKcat, [Docker](#docker).

## RAVEN toolbox / raven-toolbox

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

Installation instructions are in the [RAVEN documentation](https://raven-docs.readthedocs.io/en/latest/installation/raven.html): the repository is downloaded with `git clone`, as a ZIP archive from GitHub, or installed as a MATLAB Add-On. Instructions for installing the solver Gurobi are in the same page, under [Choosing and configuring a solver](https://raven-docs.readthedocs.io/en/latest/installation/raven.html#choosing-and-configuring-a-solver).

After finishing installation, run the checks in MATLAB:

```matlab
checkRaven;
```
:::
:::{tab-item} 🐍 Python
:sync: python

raven-toolbox is a dependency of geckopy and is installed with it (see [GECKO Toolbox / geckopy](#gecko-toolbox-geckopy)); it has no separate installation step.
:::
::::

(gecko-toolbox-geckopy)=
## GECKO Toolbox / geckopy

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

GECKO 4 is a pre-release. It is installed with `git` or from a ZIP archive of a release tag:

```bash
git clone --depth=1 https://github.com/CompMetEng/GECKO
```

The clone is the `develop` branch; adding `--branch <tag>` selects a release tag. The tags and their ZIP archives are on the [tags page](https://github.com/CompMetEng/GECKO/tags) of the repository; it is extracted to a location with read and write access.

The [MATLAB Add-On](https://mathworks.com/help/matlab/matlab_env/get-add-ons.html) (Home → Add-Ons → Get Add-Ons → search "GECKO Toolbox") installs a GitHub release; the latest, v3.2.5, is GECKO 3 (see [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md#staying-on-gecko-3)).

After cloning or extracting, navigate to the GECKO folder in MATLAB and install it, which adds the GECKO subfolders to the MATLAB path:

```matlab
cd('path/to/GECKO')
GECKOInstaller.install
```

To remove:

```matlab
GECKOInstaller.uninstall
```

Upgrading with any install method: run `GECKOInstaller.uninstall` first, regardless of how GECKO was installed: it clears the old GECKO folder from the MATLAB path so a later session does not warn about paths that no longer exist. Then update (the Add-On manager's Check for Updates, a fresh ZIP extract, or `git pull`) and run `GECKOInstaller.install` again.
:::
:::{tab-item} 🐍 Python
:sync: python

The GECKO 4 releases of geckopy and the releases of raven-toolbox that it depends on are pre-releases on PyPI, so `--pre` is required. Without `--pre`, pip installs geckopy 2.0.2, an earlier and unrelated package of the same name:

```bash
pip install --pre geckopy
```

The dependency of geckopy on raven-toolbox names a pre-release, so `--pre` also selects the pre-release of raven-toolbox, which does not need naming separately. A version of geckopy is pinned with `==` and the version number from the [PyPI release history](https://pypi.org/project/geckopy/#history):

```bash
pip install --pre geckopy==<version>
```

For the development branch, ahead of the latest PyPI release, install from GitHub instead:

```bash
pip install \
    git+https://github.com/CompMetEng/raven-toolbox.git@develop \
    git+https://github.com/CompMetEng/geckopy.git@develop
```

Verify the install:

```bash
python -c "from importlib.metadata import version; print(version('geckopy'))"
```

Optional extras: `geckopy[tutorial]` adds matplotlib for the plots of the tutorial, and `geckopy[evotune]` adds `cma`, which `cmaes_kcat_tuning` needs.

```bash
pip install --pre "geckopy[tutorial,evotune]"
```

To remove:

```bash
pip uninstall geckopy raven-toolbox
```

geckopy installs the command-line tool `geckopy` with the subcommands `init` (new ecModel project), `upgrade` (GECKO 3 project to the GECKO 4 layout), `brenda-refresh`, `uniprot-download` and `kegg-download`.
:::
::::

## Choosing a solver

| Solver | License | Good for |
|---|---|---|
| Gurobi | Free academic | Genome-scale models and large ecModels (recommended) |
| SCIP | Open source | Open-source solver of RAVEN (`setRavenSolver('scip')`); RAVEN provides a precompiled MEX binary for Windows only, and other systems compile the interface |
| HiGHS through the optlang scipy interface | Open source | Solver of geckopy that needs no licence |

MATLAB reaches the solvers through RAVEN and the COBRA Toolbox, Python through cobrapy.

:::{admonition} Avoid GLPK
:class: tip

GLPK, the default solver of RAVEN, is not recommended for GECKO: ecModels are larger and more numerically demanding than the conventional GEMs for which GLPK is adequate. Configure Gurobi, or in MATLAB SCIP, before working with an ecModel of genome scale.
:::

## Docker

`runDLKcat` (Python: `run_dlkcat`) runs DLKcat in a Docker container from the image `ghcr.io/sysbiochalmers/dlkcat-gecko:0.1`. Installation instructions are at [docs.docker.com/get-started/get-docker](https://docs.docker.com/get-started/get-docker/).

:::{admonition} kcat prediction without Docker
:class: tip

`kcatsFromOKP` (Python: `kcats_from_okp`) predicts kcat values with the hosted [OpenKineticsPredictor](https://predictor.openkinetics.org/) service. The service needs an API key and no Docker installation (see [Kcat assignment](../gecko4-kcat-assignment.md)).
:::

## Tutorial code

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

In `GECKO/tutorials`:

- `full_ecModel/protocol.m` reconstructs and analyzes a tutorial ecModel for *Saccharomyces cerevisiae*.
- `light_ecModel/protocol.m` builds a light ecModel of the generic human-GEM.
:::
:::{tab-item} 🐍 Python
:sync: python

In `geckopy/tutorials`:

- `full_ecModel/protocol.py` mirrors the MATLAB full-ecModel tutorial step for step, covering the full pipeline for *S. cerevisiae*.
- `light_ecModel/protocol.py` builds a light ecModel from a small 5-reaction demo model (`geckopy/examples/ecTestGEM`) without external data.
:::
::::

The ecModels that the tutorials generate are for use within the tutorials; they may need additional curation before other use.
