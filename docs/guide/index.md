# Guide

The guide shows how to build an enzyme-constrained model (ecModel) from a conventional genome-scale metabolic model (GEM) with GECKO (MATLAB) or geckopy (Python), and how to analyse it. [Build an ecModel](first-ecmodel.md) makes a working ecModel with the default settings. Each step of that page links to a decision page, which describes the options of the step, what each option needs and what it changes in the model. The background pages describe the file formats and the parameters. [Executed examples](executed-examples.md) describes which examples are run again on every change and which are not.

## Start

| Page | Content |
| --- | --- |
| [Introduction to ecModels](introduction.md) | what an ecModel is, the enzyme constraint and the protein pool |

## Quick path

| Page | Content |
| --- | --- |
| [Build an ecModel](first-ecmodel.md) | create a project, make the ecModel, assign *k*{sub}`cat` values, set the protein pool, check the growth rate and save the model, with the default settings |

## Workflow

[![Flowchart of the guide pages: project, ecModel structure, *k*{sub}`cat` sources, protein pool, *k*{sub}`cat` tuning, proteomics, relaxation and analysis](../_static/workflow-overview.png){width=200px .no-scaled-link}](workflow.md)

The [workflow overview](workflow.md) shows the order of the pages below, the steps of the quick path, the alternative paths and the functions of each page, in MATLAB and Python.

## Decisions

The decision pages are in the order of the work.

| Page | Choice |
| --- | --- |
| [Choose the ecModel structure](ecmodel-structure.md) | full or light ecModel, matching of genes to UniProt and KEGG, enzyme complexes |
| [Choose the *k*{sub}`cat` sources](kcat-sources.md) | the *k*{sub}`cat` assignment preset, and the treatment of isozymes and of reactions without a *k*{sub}`cat` |
| [Set custom *k*{sub}`cat` values](custom-kcats.md) | curated *k*{sub}`cat` values that take precedence over the *k*{sub}`cat` sources |
| [Set the protein pool](protein-pool.md) | the values of the total protein content, the enzyme fraction $f$ and the saturation factor $\sigma$ |
| [Choose a *k*{sub}`cat` tuning](kcat-tuning.md) | `sensitivityTuning` or evotune, when the ecModel grows too slowly, and the check of a tuned *k*{sub}`cat` |
| [Tune *k*{sub}`cat` values with sensitivityTuning](standard-tuning.md) | the tuning to one maximum growth rate, and the fit of $\sigma$ after it |
| [Tune *k*{sub}`cat` values with evotune](evotune.md) | the data and the settings of the tuning against measured growth rates and fluxes |
| [Compare *k*{sub}`cat` sources](kcat-evidence.md) | the *k*{sub}`cat` of every source file next to the *k*{sub}`cat` of the ecModel and its tuned value, and a *k*{sub}`cat` prediction for a few reactions |
| [Constrain enzymes with proteomics](proteomics.md) | the integration of measured enzyme concentrations |
| [Relax proteomics constraints](relaxing-proteomics.md) | the method that loosens proteomics constraints that prevent growth |
| [Analyse an ecModel](analysis.md) | objectives, flux variability, sampling and the mapping of fluxes to the conventional GEM |
| [Find engineering targets](engineering-targets.md) | the reactions and genes to change for the production of a compound |
| [Make a context-specific ecModel](context-ecmodel.md) | an ecModel of a tissue, cell line or strain, trimmed from a generic ecModel |
| [Enzyme usage and bottlenecks](enzyme-usage.md) | which enzymes a solution uses and which enzymes limit the objective |

## Background

| Page | Content |
| --- | --- |
| [ecModel YAML format](yaml-format.md) | the file format that both toolboxes read and write |
| [Files in the data folder](data-folder-files.md) | the files that the `data` folder of a project can hold |
| [Experimental data](experimental-data.md) | the growth rates and exchange fluxes of growth conditions that constrain and test an ecModel |
| [Model adapter parameters](model-adapter-parameters.md) | every parameter of `model_adapter.toml` in both languages |
| [Project format 4](../gecko4-project-format.md) | the project folder, `model_adapter.toml`, the *k*{sub}`cat` source files and the ecModel format |
| [*K*{sub}`cat` assignment](../gecko4-kcat-assignment.md) | the *k*{sub}`cat` sources, stages and presets of `collectKcats` and `assignKcats` |
| [Basic model operations](basic-model-operations.md) | bounds, objectives, flux balance analysis, flux inspection and export, for conventional GEMs and ecModels |
| [Executed examples](executed-examples.md) | the examples that a workflow runs again on every change, and the pages that it does not run |

## Notes

:::{admonition} MATLAB and Python
:class: note
Task pages show both languages in tabs: GECKO (MATLAB), built on RAVEN, and geckopy (Python), built on cobrapy. Function names differ in case (`camelCase` and `snake_case`), and some differ in the word as well; [MATLAB vs Python](../matlab-vs-python.md) lists the name of each function in both languages, and the [API reference](../api/index.md) lists the signatures.

Text outside a MATLAB or Python tab reads the same in both languages. Where it refers to the enzyme data of a model, `ec.kcat` stands for `ecModel.ec.kcat` in MATLAB and `ec_model.ec.kcat` in Python. The field names are identical in both languages except `rxnEnzMat` (Python: `rxn_enz_mat`) and `ec.geckoLight` (Python: `gecko_light`).
:::

## See also

- [Installation](../installation/index.md): install GECKO or geckopy.
- [API reference](../api/index.md): the generated documentation of the functions of both toolboxes.
- [MATLAB vs Python](../matlab-vs-python.md): the names of the functions in GECKO and geckopy.
- [Migration](../migrate.md): the changes from GECKO 3 to GECKO 4 and the differences between GECKO and geckopy.

```{toctree}
:hidden:
:caption: Start

introduction
```

```{toctree}
:hidden:
:caption: Quick path

first-ecmodel
```

```{toctree}
:hidden:
:caption: Workflow

workflow
```

```{toctree}
:hidden:
:caption: Decisions

ecmodel-structure
kcat-sources
custom-kcats
protein-pool
kcat-tuning
standard-tuning
evotune
kcat-evidence
proteomics
relaxing-proteomics
analysis
engineering-targets
context-ecmodel
enzyme-usage
```

```{toctree}
:hidden:
:caption: Background

yaml-format
data-folder-files
experimental-data
model-adapter-parameters
basic-model-operations
executed-examples
../gecko4-project-format
../gecko4-kcat-assignment
```
