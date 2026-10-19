# Guide

Short, task-focused pages: one job per page, in **MATLAB and Python side by
side**. Start at [Introduction](introduction.md) if the ecModel concept is
new, or [Getting started](getting-started.md) to jump straight into loading
a model, and read on from there, or go directly to whichever task is at
hand.

:::{admonition} GECKO 4.0.0b1
:class: important
This Guide documents GECKO 4, a pre-release still under development. Pages
call out functions that are new in GECKO 4 and were not part of the
published GECKO 3.0 Nature Protocols pipeline; see [GECKO 3 →
GECKO 4](../gecko3-to-gecko4.md) for the full list of changes, and for how
to stay on GECKO 3 if a workflow depends on its behavior.
:::

:::{admonition} MATLAB and Python
:class: info
Every task page shows both languages side by side: GECKO (MATLAB), built on
RAVEN, and geckopy (Python), built on cobrapy. Function names differ only
mechanically between the two (`camelCase` vs. `snake_case`); see
[MATLAB ↔ Python](../matlab-vs-python.md) for the full name mapping, and
[API reference](../api/index.md) for every function's signature.

Text outside a MATLAB/Python tab reads the same whichever language is
selected. Where it must refer to the model's enzyme data, `ec.kcat` stands
for `ecModel.ec.kcat` in MATLAB and `ec_model.ec.kcat` in Python; field names
are identical in both languages except `rxnEnzMat` (Python: `rxn_enz_mat`).
:::

## Pages

**Start**

- [Introduction to ecModels](introduction.md), what an ecModel is and how
  enzyme constraints are added to a conventional GEM.
- [Installation](../installation/index.md), set up GECKO or geckopy.

**Guide**, the steps that build and analyze an ecModel, in order:

1. [Getting started](getting-started.md), scaffold a project and load a
   first model.
2. [Building an ecModel](building-ec-model.md), expand a conventional GEM
   into ecModel structure.
3. [Gathering kcat values](gathering-kcats.md), collect turnover numbers
   from BRENDA and DLKcat.
4. [Applying kcat values](applying-kcats.md), write collected kcat values
   into the ecModel's enzyme constraints.
5. [Growth-rate tuning](growth-rate-tuning.md), close the gap between a
   freshly built ecModel's growth rate and the organism's actual one.
6. [Tuning against experimental data](tuning-against-experimental-data.md),
   curate the kcat values tuning identified as limiting.
7. [Proteomics integration](proteomics-integration.md), constrain
   individual enzyme concentrations from measured proteomics data.
8. [Relaxing overconstrained proteomics](relaxing-constraints.md), two ways
   to loosen proteomics constraints that leave the ecModel unable to reach
   its intended growth rate.
9. [Simulation and analysis](simulation-and-analysis.md), objective choice,
   flux variability, sampling, mapping ecModel fluxes back to a
   conventional GEM, and context-specific ecModels.
10. [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), which
    enzymes a solution uses, and which ones are actually limiting the
    objective.

**Background**, reference material the Guide pages above link out to rather
than repeat:

- [GECKO light vs. full ecModels](gecko-light.md), the two ecModel layouts,
  what light gives up, and when to choose each.
- [ecModel YAML format](yaml-format.md), the file format both toolboxes
  read and write, field by field.
- [Files in the data folder](data-folder-files.md), every file a project's
  `data` folder can hold.
- [Model adapter parameters](model-adapter-parameters.md), every model
  adapter parameter, in both languages.

## Approximate timing

Rough wall-clock time for a first pass through each Guide step, on a
genome-scale model such as yeast-GEM. Actual timing depends heavily on model
size, internet connection, and which solver is configured.

| Pages | Approx. timing | Notes |
|---|---|---|
| Getting started, Building an ecModel | 15 min | |
| Gathering kcats, Applying kcats | 1 h | DLKcat prediction accounts for most of it |
| Growth-rate tuning, Tuning against experimental data | 15 min | |
| Proteomics integration | 15 min | |
| Relaxing overconstrained proteomics | 15 min | can take longer with lower-quality proteomics data, more enzymes need flexibilizing |
| Simulation and analysis | 3 h | ecFVA at genome scale accounts for most of it, and is far shorter with a commercial solver configured |
| Enzyme usage and bottlenecks | 15 min | |

## See also

- [GECKO 3 → GECKO 4](../gecko3-to-gecko4.md), the full list of GECKO 4
  changes against the published protocol.
- [API reference](../api/index.md), generated function documentation for
  both toolboxes.
- [MATLAB ↔ Python](../matlab-vs-python.md), the function name mapping
  between GECKO and geckopy.

```{toctree}
:hidden:
:caption: Start

introduction
../installation/index
```

```{toctree}
:hidden:
:caption: Guide

getting-started
building-ec-model
gathering-kcats
applying-kcats
growth-rate-tuning
tuning-against-experimental-data
proteomics-integration
relaxing-constraints
simulation-and-analysis
enzyme-usage-and-bottlenecks
```

```{toctree}
:hidden:
:caption: Background

gecko-light
yaml-format
data-folder-files
model-adapter-parameters
```
