# Guide

The guide has one page per job, with MATLAB and Python side by side. [Introduction to ecModels](introduction.md) describes the ecModel concept, [Getting started](getting-started.md) scaffolds a project, and the following pages follow the order of the work from a conventional GEM to an analysed ecModel. Each page is also readable by itself.

:::{admonition} GECKO 4.0.0b1
:class: important
This guide documents GECKO 4, a pre-release. The pages follow the structure of the published GECKO 3.0 Nature Protocols pipeline and describe GECKO 4. [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md) lists the changes against that protocol and describes how to stay on GECKO 3 for a workflow that depends on its behaviour.
:::

:::{admonition} MATLAB and Python
:class: info
Task pages show both languages in tabs: GECKO (MATLAB), built on RAVEN, and geckopy (Python), built on cobrapy. Function names differ in case (`camelCase` and `snake_case`), and some differ in the word as well; [MATLAB vs Python](../matlab-vs-python.md) lists the name of each function in both languages, and the [API reference](../api/index.md) lists the signatures.

Text outside a MATLAB or Python tab reads the same in both languages. Where it refers to the enzyme data of a model, `ec.kcat` stands for `ecModel.ec.kcat` in MATLAB and `ec_model.ec.kcat` in Python. The field names are identical in both languages except `rxnEnzMat` (Python: `rxn_enz_mat`) and `ec.geckoLight` (Python: `gecko_light`).
:::

## Pages

Start:

- [Introduction to ecModels](introduction.md), what an ecModel is and how GECKO adds enzyme constraints to a conventional GEM.
- [Installation](../installation/index.md), set up GECKO or geckopy.

Steps, in the order of the work:

1. [Getting started](getting-started.md), scaffold a project and fill the model adapter.
2. [Building an empty ecModel](building-ec-model.md), expand a conventional GEM into the structure of an ecModel.
3. [Gathering kcats](gathering-kcats.md), collect the kcats of each source.
4. [Applying kcats](applying-kcats.md), write kcats into the enzyme constraints of the ecModel.
5. [Growth-rate tuning](growth-rate-tuning.md), close the gap between the growth rate of a new ecModel and that of the organism.
6. [Tuning against experimental data](tuning-against-experimental-data.md), fit and curate the kcats that limit the model.
7. [Proteomics integration](proteomics-integration.md), constrain the concentrations of individual enzymes with proteomics data.
8. [Relaxing overconstrained proteomics](relaxing-constraints.md), loosen proteomics constraints that keep the ecModel from its growth rate.
9. [Simulation and analysis](simulation-and-analysis.md), objectives, flux variability, sampling, flux scanning, mapping to the conventional GEM and context-specific ecModels.
10. [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), which enzymes a solution uses and which enzymes limit the objective.

Background, the reference material that the steps link to:

- [GECKO light and full ecModels](gecko-light.md), the two ecModel layouts and the choice between them.
- [ecModel YAML format](yaml-format.md), the file format that both toolboxes read and write.
- [Files in the data folder](data-folder-files.md), every file that the `data` folder of a project can hold.
- [Model adapter parameters](model-adapter-parameters.md), every parameter of `model_adapter.toml` in both languages.

Migration, pages for GECKO 3 projects and scripts:

- [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md), the changes of results, errors, functions and names.
- [Project format 4](../gecko4-project-format.md), the project folder, `model_adapter.toml`, kcat source files and the ecModel format.
- [Upgrade a GECKO 3 project](../gecko3-upgrade-project.md), the steps of `upgradeGECKOproject` and `upgradeEcModel`.
- [Kcat assignment](../gecko4-kcat-assignment.md), the kcat sources, stages and presets of `collectKcats` and `assignKcats`.

## Approximate timing

The table lists the wall-clock time of a first pass through each step on a genome-scale model such as yeast-GEM. The time depends on the size of the model, the internet connection and the configured solver.

| Pages | Approximate time | Notes |
|---|---|---|
| Getting started, Building an empty ecModel | 15 min | |
| Gathering kcats, Applying kcats | 1 h | the prediction of kcats accounts for most of the time |
| Growth-rate tuning, Tuning against experimental data | 15 min | |
| Proteomics integration | 15 min | |
| Relaxing overconstrained proteomics | 15 min | longer with proteomics data of lower quality, which needs more enzymes to be flexibilised |
| Simulation and analysis | 3 h | `ecFVA` at genome scale accounts for most of the time, and it is much shorter with a commercial solver |
| Enzyme usage and bottlenecks | 15 min | |

## See also

- [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md), the changes of GECKO 4 against the published protocol.
- [API reference](../api/index.md), the generated documentation of the functions of both toolboxes.
- [MATLAB vs Python](../matlab-vs-python.md), the names of the functions in GECKO and geckopy.

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
