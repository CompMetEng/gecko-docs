# Workflow overview

<!-- docs-site: concept-page -->

The diagram orders the functions that build, parameterise, tune and analyse an ecModel, with the parts that run in parallel and the alternatives. Each stage is a guide page. A solid arrow connects functions that run one after another, a dashed arrow an optional preview or an alternative way to reach the next step, a diamond a choice between paths, and a dashed outline an optional step. The button in the corner of a diagram opens it in full screen, where the mouse wheel zooms and a drag pans. In the page, the wheel zooms with Ctrl (Cmd on macOS) held. Each tab offers its diagram as a PDF.

:::::{tab-set}
::::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```{mermaid}
flowchart TB
  classDef opt stroke-dasharray: 5 4
  A["<b>Getting started</b><br/>createGECKOproject<br/>Fill model_adapter.toml"]
  B["<b>Building an empty ecModel</b><br/>ModelAdapterManager.setDefault<br/>loadConventionalGEM<br/>makeEcModel (full or light)<br/>getComplexData, applyComplexData (optional)<br/>saveEcModel"]
  A --> B
  EC["EC numbers<br/>getECfromGEM or getECfromDatabase"]
  SM["Metabolite SMILES<br/>findMetSmiles"]
  HO["kcatsFromHomologs"]
  BR["kcatsFromBrenda"]
  TR["kcatsFromECTree"]
  DL["kcatsFromDLKcat"]
  OK["kcatsFromOKP"]
  CU["data/kcats/custom.tsv"]:::opt
  GA["<b>Gathering kcats</b><br/>any subset of the sources"]
  B --> GA
  GA --> EC
  GA --> SM
  GA --> HO
  EC --> BR
  EC --> TR
  SM --> DL
  SM --> OK
  AS["<b>Applying kcats</b><br/>assignKcats (preview: collectKcats)<br/>getKcatAcrossIsozymes, getStandardKcat (optional)<br/>applyKcatConstraints<br/>setProtPoolSize"]
  BR --> AS
  TR --> AS
  HO --> AS
  DL --> AS
  OK --> AS
  CU --> AS
  TU{"solveLP: growth reaches the target?"}
  AS --> TU
  SE["<b>Growth-rate tuning</b><br/>sensitivityTuning<br/>sigmaFitter"]
  CM["<b>Tuning against experimental data</b><br/>screenKcatLeverage<br/>reviewKcatAssignment<br/>cmaesKcatTuning"]
  TU -->|no| SE
  TU -->|no, several conditions measured| CM
  FM["Functional ecModel<br/>saveEcModel"]
  TU -->|yes| FM
  SE --> FM
  CM --> FM
  PR["<b>Proteomics integration</b><br/>loadProtData, fillEnzConcs<br/>levelComplexConcs, constrainEnzConcs<br/>calculateFfactor, setProtPoolSize<br/>loadFluxData, constrainFluxData"]:::opt
  FM --> PR
  RL{"Growth reaches the target?"}
  PR --> RL
  FX["<b>Relaxing</b>, gradual<br/>flexibilizeEnzConcs"]
  GR["<b>Relaxing</b>, fast<br/>relaxProteomicsGreedy"]
  RL -->|no, gradual| FX
  RL -->|no, fast| GR
  RD["ecModel for simulation and analysis"]
  RL -->|yes| RD
  FX --> RD
  GR --> RD
  FM -.->|without proteomics| RD
  I1["<b>Simulation</b><br/>ecFVA, randomSampling<br/>ecFSEOF<br/>getSubsetEcModel"]
  I2["<b>Enzyme usage</b><br/>getEnzymeUsage<br/>getEnzymeBottlenecks"]
  RD --> I1
  RD --> I2
```

:::{div} workflow-pdf
{download}`Download the MATLAB diagram as PDF <../_static/workflow-matlab.pdf>`
:::
::::
::::{tab-item} 🐍 Python
:sync: python

```{mermaid}
flowchart TB
  classDef opt stroke-dasharray: 5 4
  A["<b>Getting started</b><br/>geckopy init<br/>Fill model_adapter.toml"]
  B["<b>Building an empty ecModel</b><br/>ModelAdapter.from_folder<br/>load_conventional_gem<br/>make_ec_model (full or light)<br/>get_complex_data, apply_complex_data (optional)<br/>save_ec_model"]
  A --> B
  EC["EC numbers<br/>fill_eccodes_from_gem or fill_eccodes_from_database"]
  SM["Metabolite SMILES<br/>find_met_smiles"]
  HO["kcats_from_homologs"]
  BR["kcats_from_brenda"]
  TR["kcats_from_ec_tree"]
  DL["kcats_from_dlkcat"]
  OK["kcats_from_okp"]
  CU["data/kcats/custom.tsv"]:::opt
  GA["<b>Gathering kcats</b><br/>any subset of the sources"]
  B --> GA
  GA --> EC
  GA --> SM
  GA --> HO
  EC --> BR
  EC --> TR
  SM --> DL
  SM --> OK
  AS["<b>Applying kcats</b><br/>assign_kcats (preview: collect_kcats)<br/>fill_kcats_from_isozymes, assign_standard_kcat (optional)<br/>apply_kcat_constraints<br/>set_prot_pool_size"]
  BR --> AS
  TR --> AS
  HO --> AS
  DL --> AS
  OK --> AS
  CU --> AS
  TU{"model.optimize: growth reaches the target?"}
  AS --> TU
  SE["<b>Growth-rate tuning</b><br/>sensitivity_tuning<br/>fit_sigma"]
  CM["<b>Tuning against experimental data</b><br/>screen_kcat_leverage<br/>review_assignment<br/>cmaes_kcat_tuning"]
  TU -->|no| SE
  TU -->|no, several conditions measured| CM
  FM["Functional ecModel<br/>save_ec_model"]
  TU -->|yes| FM
  SE --> FM
  CM --> FM
  PR["<b>Proteomics integration</b><br/>load_prot_data, fill_enz_concs<br/>level_complex_concs, constrain_enz_concs<br/>calculate_f_factor, set_prot_pool_size<br/>load_flux_data, apply_flux_data_constraints"]:::opt
  FM --> PR
  RL{"Growth reaches the target?"}
  PR --> RL
  FX["<b>Relaxing</b>, gradual<br/>flexibilize_enz_concs"]
  GR["<b>Relaxing</b>, fast<br/>relax_proteomics_greedy"]
  RL -->|no, gradual| FX
  RL -->|no, fast| GR
  SA["<b>Relaxing</b>, smallest total amount<br/>relax_enz_concs"]
  RL -->|no, smallest total amount| SA
  RD["ecModel for simulation and analysis"]
  RL -->|yes| RD
  FX --> RD
  GR --> RD
  SA --> RD
  FM -.->|without proteomics| RD
  I1["<b>Simulation</b><br/>ec_fva, random_sampling<br/>ec_fseof<br/>get_subset_ec_model"]
  I2["<b>Enzyme usage</b><br/>enzyme_usage<br/>get_enzyme_bottlenecks"]
  RD --> I1
  RD --> I2
```

:::{div} workflow-pdf
{download}`Download the Python diagram as PDF <../_static/workflow-python.pdf>`
:::
::::
:::::

## Stages, order and alternatives

Each row is a stage with the stage it runs after, its functions and what it leaves behind. "Any subset" marks functions that run independently of each other, "alternative" a path that replaces another, and "one of" a choice of algorithm.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

| Stage | Run after | Functions | Output |
| --- | --- | --- | --- |
| [Getting started](getting-started.md) | none | `createGECKOproject`, then edit `model_adapter.toml`; `loadDatabases('kegg')` (optional) | project folder |
| [Building an empty ecModel](building-ec-model.md) | project and model adapter | `ModelAdapterManager.setDefault`, `loadConventionalGEM`, `makeEcModel` (full or light), `getComplexData, applyComplexData` (optional), `saveEcModel` | ecModel file |
| [Gathering kcats](gathering-kcats.md) | built ecModel | any subset of `kcatsFromBrenda`, `kcatsFromECTree`, `kcatsFromHomologs`, `kcatsFromDLKcat`, `kcatsFromOKP`; `updateKcatSources` gathers all sources of `model_adapter.toml` | `data/kcats/<source>.tsv` |
| [Applying kcats](applying-kcats.md) | at least one source file or `custom.tsv` | `assignKcats` (preview: `collectKcats`), `getKcatAcrossIsozymes` and `getStandardKcat` (optional), `applyKcatConstraints`, `setProtPoolSize` | `ec.kcat`, constrained ecModel |
| [Growth-rate tuning](growth-rate-tuning.md) | applied kcats, growth rate below the target | `sensitivityTuning`, then `sigmaFitter` | tuned `ec.kcat` |
| [Tuning against experimental data](tuning-against-experimental-data.md) | applied kcats, growth rates and fluxes of several conditions | alternative to sensitivity tuning: `screenKcatLeverage`, `reviewKcatAssignment`, `cmaesKcatTuning` | tuned `ec.kcat` |
| [Proteomics integration](proteomics-integration.md) | functional ecModel | `loadProtData`, `fillEnzConcs`, `levelComplexConcs`, `constrainEnzConcs`, `calculateFfactor, setProtPoolSize`, `loadFluxData, constrainFluxData` (optional) | proteomics-constrained ecModel |
| [Relaxing overconstrained proteomics](relaxing-constraints.md) | proteomics-constrained ecModel below the target growth rate | one of `flexibilizeEnzConcs`, `relaxProteomicsGreedy` | relaxed ecModel |
| [Simulation and analysis](simulation-and-analysis.md), [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md) | any ecModel | independent of each other: `ecFVA`, `randomSampling`, `ecFSEOF`, `getSubsetEcModel`, `getEnzymeUsage`, `getEnzymeBottlenecks` | results |
:::
:::{tab-item} 🐍 Python
:sync: python

| Stage | Run after | Functions | Output |
| --- | --- | --- | --- |
| [Getting started](getting-started.md) | none | `geckopy init`, then edit `model_adapter.toml`; `geckopy kegg-download` (optional) | project folder |
| [Building an empty ecModel](building-ec-model.md) | project and model adapter | `ModelAdapter.from_folder`, `load_conventional_gem`, `make_ec_model` (full or light), `get_complex_data, apply_complex_data` (optional), `save_ec_model` | ecModel file |
| [Gathering kcats](gathering-kcats.md) | built ecModel | any subset of `kcats_from_brenda`, `kcats_from_ec_tree`, `kcats_from_homologs`, `kcats_from_dlkcat`, `kcats_from_okp`; `update_kcat_sources` gathers all sources of `model_adapter.toml` | `data/kcats/<source>.tsv` |
| [Applying kcats](applying-kcats.md) | at least one source file or `custom.tsv` | `assign_kcats` (preview: `collect_kcats`), `fill_kcats_from_isozymes` and `assign_standard_kcat` (optional), `apply_kcat_constraints`, `set_prot_pool_size` | `ec.kcat`, constrained ecModel |
| [Growth-rate tuning](growth-rate-tuning.md) | applied kcats, growth rate below the target | `sensitivity_tuning`, then `fit_sigma` | tuned `ec.kcat` |
| [Tuning against experimental data](tuning-against-experimental-data.md) | applied kcats, growth rates and fluxes of several conditions | alternative to sensitivity tuning: `screen_kcat_leverage`, `review_assignment`, `cmaes_kcat_tuning` | tuned `ec.kcat` |
| [Proteomics integration](proteomics-integration.md) | functional ecModel | `load_prot_data`, `fill_enz_concs`, `level_complex_concs`, `constrain_enz_concs`, `calculate_f_factor, set_prot_pool_size`, `load_flux_data, apply_flux_data_constraints` (optional) | proteomics-constrained ecModel |
| [Relaxing overconstrained proteomics](relaxing-constraints.md) | proteomics-constrained ecModel below the target growth rate | one of `flexibilize_enz_concs`, `relax_proteomics_greedy`, `relax_enz_concs` | relaxed ecModel |
| [Simulation and analysis](simulation-and-analysis.md), [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md) | any ecModel | independent of each other: `ec_fva`, `random_sampling`, `ec_fseof`, `get_subset_ec_model`, `enzyme_usage`, `get_enzyme_bottlenecks` | results |
:::
::::

## Reading the paths

- **Kcat sources:** each `kcatsFrom*` function (Python `kcats_from_*`) writes its own file in `data/kcats`. `assignKcats` reads the files that `[kcat_assignment]` of `model_adapter.toml` lists, so any combination of sources works. The EC numbers feed the BRENDA, EC tree and homolog sources, and the metabolite SMILES feed DLKcat and OpenKineticsPredictor (see [Gathering kcats](gathering-kcats.md)). `updateKcatSources` (Python `update_kcat_sources`) gathers the sources that `model_adapter.toml` needs in one call.
- **Tuning:** sensitivity tuning raises kcats one at a time until one target growth rate is reached. Tuning against experimental data fits many kcats to the measured growth rates and fluxes of several conditions.
- **Relaxation:** `flexibilizeEnzConcs` and `relaxProteomicsGreedy` are alternatives with different stringency (see [Relaxing overconstrained proteomics](relaxing-constraints.md)).
- **Analysis:** the analysis functions work on the finished ecModel and do not depend on each other.

## See also

- [Guide](index.md), the list of pages.
- [Basic model operations](basic-model-operations.md), bounds, objectives and FBA.
