---
icon: material/folder-open
---

# Installation

GECKO is available as a **MATLAB toolbox** and as the **Python package
geckopy**. Both implement the same procedure and can reconstruct, simulate
and analyze the same ecModels: pick whichever fits your existing workflow.

## Equipment

A computer running macOS, Windows or Linux, with an internet connection to
reach [KEGG](https://www.genome.jp/kegg/), [UniProt](https://www.uniprot.org/),
[PubChem](https://pubchem.ncbi.nlm.nih.gov/) and
[GitHub](https://github.com/CompMetEng/GECKO/). Data from these sources
can also be downloaded or reconstructed manually elsewhere, but downloading
it directly through GECKO functions is the most convenient route.

The starting point is a conventional constraint-based metabolic model, at
genome scale or smaller, in SBML format L3V1 FBCv2. A well-curated model
produces a well-performing ecModel, but the procedure works on any valid
model, regardless of whether it belongs to a model organism.

## Software

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

- **MATLAB** version 2019b or above
  ([MathWorks](https://mathworks.com/products/matlab.html)). No additional
  MathWorks toolboxes are required.
- **RAVEN toolbox** version 2.9.2 or later
  ([repository](https://github.com/CompMetEng/RAVEN)), which provides
  the reconstruction functions GECKO builds on, and some of the functions
  used to simulate and analyze ecModels.
:::
:::{tab-item} 🐍 Python
:sync: python

- **Python** 3.11 or above.
- **geckopy** ([repository](https://github.com/CompMetEng/geckopy)),
  built on [cobrapy](https://github.com/opencobra/cobrapy) for the
  constraint-based modeling layer and
  [raven-toolbox](https://github.com/CompMetEng/raven-toolbox) (the
  Python port of RAVEN) for model-manipulation primitives and ecModel YAML
  I/O. Installing geckopy pulls in both dependencies automatically.
:::
::::

Both toolboxes also need a linear-programming solver (see
[Choosing a solver](#choosing-a-solver) below) and, for DLKcat,
[Docker](#docker).

## RAVEN toolbox / raven-toolbox

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

Installation instructions are in the
[RAVEN documentation](https://raven-docs.readthedocs.io/en/latest/installation/raven.html):
the repository is downloaded via `git clone`, as a ZIP archive from GitHub, or
installed as a MATLAB Add-On. Instructions for installing the recommended
solver Gurobi are in the same page, under
[Choosing and configuring a solver](https://raven-docs.readthedocs.io/en/latest/installation/raven.html#choosing-and-configuring-a-solver).

After finishing installation, run the checks in MATLAB:

```matlab
checkRaven;
```
:::
:::{tab-item} 🐍 Python
:sync: python

raven-toolbox is a dependency of geckopy and installs automatically with it
(see [GECKO Toolbox / geckopy](#gecko-toolbox-geckopy) below); there is no
separate installation step.
:::
::::

(gecko-toolbox-geckopy)=
## GECKO Toolbox / geckopy

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

The latest GECKO release installs as a
[MATLAB Add-On](https://mathworks.com/help/matlab/matlab_env/get-add-ons.html):
Home → Add-Ons → Get Add-Ons → search "GECKO Toolbox".

Cloning the repository with `git` is recommended instead, since it makes
upgrading a `git pull` rather than a full reinstall:

```bash
git clone --depth=1 https://github.com/CompMetEng/GECKO
```

or download a ZIP archive from the
[GitHub releases page](https://github.com/CompMetEng/GECKO/releases) and
extract it to a location with read and write access.

After cloning or extracting, navigate to the GECKO folder in MATLAB and
install it, which adds the GECKO subfolders to the MATLAB path:

```matlab
cd('path/to/GECKO')
GECKOInstaller.install
```

To remove:

```matlab
GECKOInstaller.uninstall
```

**Upgrading, with any install method.** Run `GECKOInstaller.uninstall`
first, regardless of how GECKO was installed: it clears the old GECKO
folder from the MATLAB path so a later session does not warn about paths
that no longer exist. Then update (Add-On manager's Check for Updates, a
fresh ZIP extract, or `git pull` on the `main` branch) and run
`GECKOInstaller.install` again.
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy and raven-toolbox are both pre-release on PyPI, so `--pre` is
required:

```bash
pip install --pre geckopy
```

geckopy's dependency on raven-toolbox already names a pre-release specifier,
which opts pip into matching pre-releases for that package too; `--pre`
alone is enough, raven-toolbox does not need naming separately. To pin the
exact versions of both instead of "whatever's newest":

```bash
pip install raven-toolbox==3.0.0b1 geckopy==4.0.0b1
```

For the development branch, ahead of the latest PyPI release, install from
GitHub instead:

```bash
pip install \
    git+https://github.com/CompMetEng/raven-toolbox.git@develop \
    git+https://github.com/CompMetEng/geckopy.git@develop
```

Verify the install:

```bash
python -c "import geckopy; print(geckopy.__version__)"
```

To remove:

```bash
pip uninstall geckopy raven-toolbox
```

geckopy also installs a `geckopy` command-line tool, used to scaffold new
ecModel projects and to download UniProt/KEGG data.
:::
::::

## Choosing a solver

| Solver | License | Good for |
|---|---|---|
| Gurobi | Free academic | Genome-scale models, sensitivity tuning, large ecModels (recommended) |
| SoPlex (SCIP Optimization Suite) | Open source | An open-source alternative to Gurobi |

Both MATLAB and Python use the same underlying solvers: MATLAB through RAVEN
and the COBRA Toolbox, Python through cobrapy.

:::{tip} Avoid GLPK
GLPK, the default solver of RAVEN, is not recommended for GECKO: ecModels
are larger and more numerically demanding than the conventional GEMs GLPK
is adequate for. Configure Gurobi or SoPlex before working with an ecModel
of genome scale.
:::

## Docker

DLKcat runs in a Docker container. Installation instructions are at
[docs.docker.com/get-started/get-docker](https://docs.docker.com/get-started/get-docker/).

:::{tip} Running DLKcat without Docker
If installing Docker Desktop is difficult, the `src/dlkcat-gecko/` folder of
the GECKO repository contains the Python scripts and data needed to run
DLKcat directly from the `DLKcat.tsv` output of `writeDLKcatInput` (Python:
`write_dlkcat_input`).
:::

## Tutorial code

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

In `GECKO/tutorials`:

- `full_ecModel/protocol.m` reconstructs and analyzes a tutorial ecModel for
  *Saccharomyces cerevisiae*.
- `light_ecModel/protocol.m` builds a light ecModel of the generic
  human-GEM.
:::
:::{tab-item} 🐍 Python
:sync: python

In `geckopy/tutorials`:

- `full_ecModel/protocol.py` mirrors the MATLAB full-ecModel tutorial step
  for step, covering the full pipeline for *S. cerevisiae*.
- `light_ecModel/protocol.py` builds a light ecModel from a small
  5-reaction demo model (`geckopy/examples/ecTestGEM`), so it runs in
  seconds without external data.
:::
::::

Both tutorials, in both languages, generate ecModels suitable only for use
within the respective tutorials; the reconstructed models may need
additional curation before other use.
