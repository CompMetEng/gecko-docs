# Guide

The guide shows how to build an enzyme-constrained model (ecModel) from a conventional genome-scale metabolic model (GEM) with GECKO (MATLAB) or geckopy (Python), and how to analyse it. [Build an ecModel](first-ecmodel.md) makes a working ecModel with the default settings. Each step of that page links to a decision page, which describes the options of the step, what each option needs and what it changes in the model. The background pages describe the file formats and the parameters.

:::{admonition} GECKO 4 pre-release
:class: important
GECKO 4 is a pre-release, and the guide describes GECKO 4. A GECKO 3 user finds the changes of results, functions and names, and the steps to upgrade a project, in [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md).
:::

:::{admonition} MATLAB and Python
:class: info
Task pages show both languages in tabs: GECKO (MATLAB), built on RAVEN, and geckopy (Python), built on cobrapy. Function names differ in case (`camelCase` and `snake_case`), and some differ in the word as well; [MATLAB vs Python](../matlab-vs-python.md) lists the name of each function in both languages, and the [API reference](../api/index.md) lists the signatures.

Text outside a MATLAB or Python tab reads the same in both languages. Where it refers to the enzyme data of a model, `ec.kcat` stands for `ecModel.ec.kcat` in MATLAB and `ec_model.ec.kcat` in Python. The field names are identical in both languages except `rxnEnzMat` (Python: `rxn_enz_mat`) and `ec.geckoLight` (Python: `gecko_light`).
:::

## Start

- [Introduction to ecModels](introduction.md): what an ecModel is, the enzyme constraint and the protein pool.
- [Installation](../installation/index.md): install GECKO or geckopy.

## Quick path

- [Build an ecModel](first-ecmodel.md): create a project, make the ecModel, assign kcats, set the protein pool, check the growth rate and save the model, with the default settings.

## Decisions

The decision pages are in the order in which the choices come up during the work.

| Page | Choice |
| --- | --- |
| [Choose the ecModel structure](ecmodel-structure.md) | full or light ecModel, matching of genes to UniProt and KEGG, enzyme complexes |
| [Choose the kcat sources](kcat-sources.md) | the kcat assignment preset, and the treatment of isozymes and of reactions without a kcat |
| [Set custom kcats](custom-kcats.md) | curated kcats that take precedence over the kcat sources |
| [Set the protein pool](protein-pool.md) | the values of the total protein content, the enzyme fraction `f` and the saturation factor `sigma` |
| [Choose a kcat tuning](kcat-tuning.md) | standard or advanced kcat tuning, when the ecModel grows too slowly |
| [Tune kcats against experimental data](advanced-tuning.md) | the data and the settings of the advanced kcat tuning |
| [Constrain enzymes with proteomics](proteomics.md) | the integration of measured enzyme concentrations |
| [Relax proteomics constraints](relaxing-proteomics.md) | the method that loosens proteomics constraints that prevent growth |
| [Analyse an ecModel](analysis.md) | objectives, flux variability, sampling, flux scanning and context-specific ecModels |
| [Enzyme usage and bottlenecks](enzyme-usage.md) | which enzymes a solution uses and which enzymes limit the objective |

## Background

- [ecModel YAML format](yaml-format.md): the file format that both toolboxes read and write.
- [Files in the data folder](data-folder-files.md): the files that the `data` folder of a project can hold.
- [Model adapter parameters](model-adapter-parameters.md): every parameter of `model_adapter.toml` in both languages.
- [Basic model operations](basic-model-operations.md): bounds, objectives, flux balance analysis, flux inspection and export, for conventional GEMs and ecModels.

## Migration

- [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md): the changes of results, errors, functions and names.
- [Project format 4](../gecko4-project-format.md): the project folder, `model_adapter.toml`, the kcat source files and the ecModel format.
- [Upgrade a GECKO 3 project](../gecko3-upgrade-project.md): the steps of `upgradeGECKOproject` and `upgradeEcModel`.
- [Kcat assignment](../gecko4-kcat-assignment.md): the kcat sources, stages and presets of `collectKcats` and `assignKcats`.

## See also

- [API reference](../api/index.md): the generated documentation of the functions of both toolboxes.
- [MATLAB vs Python](../matlab-vs-python.md): the names of the functions in GECKO and geckopy.

```{toctree}
:hidden:
:caption: Start

introduction
../installation/index
```

```{toctree}
:hidden:
:caption: Quick path

first-ecmodel
```

```{toctree}
:hidden:
:caption: Decisions

ecmodel-structure
kcat-sources
custom-kcats
protein-pool
kcat-tuning
advanced-tuning
proteomics
relaxing-proteomics
analysis
enzyme-usage
```

```{toctree}
:hidden:
:caption: Background

yaml-format
data-folder-files
model-adapter-parameters
basic-model-operations
```
