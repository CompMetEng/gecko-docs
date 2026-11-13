# Workflow overview

<!-- docs-site: concept-page -->

The diagram shows the order of the guide pages, from a new project to the analysis of an ecModel, with the functions of each page. The boxes with a thick outline are the steps of [Build an ecModel](first-ecmodel.md), which makes a working ecModel with the default settings; each of these steps has a decision page with its options. A solid arrow connects pages that run one after another, a dashed arrow a step without the optional part, a diamond a choice between paths, and a dashed outline an optional page. A click on a box opens its page. The button in the corner of a diagram opens it in full screen, where the mouse wheel zooms and a drag pans. In the page, the wheel zooms with Ctrl (Cmd on macOS) held. The download icon at the top of each tab saves its diagram as a PDF.

:::::{tab-set}
::::{tab-item} Ⓜ️ MATLAB
:sync: matlab

:::{div} workflow-pdf
{download}`Download the MATLAB diagram as PDF <../_static/workflow-matlab.pdf>`
:::

```{mermaid}
:config: {"flowchart": {"useMaxWidth": false}}

flowchart TB
  classDef quick stroke-width:3px
  classDef opt stroke-dasharray: 5 4
  P["<b>Build an ecModel</b><br/>createGECKOproject<br/>fill model_adapter.toml"]:::quick
  S["<b>Choose the ecModel structure</b><br/>ModelAdapterManager.setDefault<br/>loadConventionalGEM<br/>makeEcModel (full or light)<br/>getComplexData, applyComplexData (optional)"]:::quick
  K["<b>Choose the kcat sources</b><br/>getECfromGEM or getECfromDatabase<br/>findMetSmiles<br/>updateKcatSources<br/>assignKcats (preview: collectKcats)"]:::quick
  C["<b>Set custom kcats</b><br/>data/kcats/custom.tsv<br/>convertCustomKcats (GECKO 3 file)"]:::opt
  PP["<b>Set the protein pool</b><br/>setProtPoolSize<br/>calculateFfactor (optional)"]:::quick
  G{"solveLP: growth reaches the target?"}
  T["<b>Choose a kcat tuning</b><br/>standard: sensitivityTuning, sigmaFitter"]:::quick
  A["<b>Tune kcats against experimental data</b><br/>screenKcatLeverage, selectTunableMask<br/>reviewKcatAssignment<br/>cmaesKcatTuning"]
  F["<b>Functional ecModel</b><br/>saveEcModel"]:::quick
  P --> S --> K --> PP --> G
  C --> K
  G -->|no| T
  G -->|no, several conditions measured| A
  G -->|yes| F
  T --> F
  A --> F
  PR["<b>Constrain enzymes with proteomics</b><br/>loadProtData, fillEnzConcs<br/>levelComplexConcs, constrainEnzConcs<br/>calculateFfactor, setProtPoolSize<br/>loadFluxData, constrainFluxData"]:::opt
  F --> PR
  RL{"Growth reaches the target?"}
  PR --> RL
  RX["<b>Relax proteomics constraints</b><br/>one of flexibilizeEnzConcs,<br/>relaxProteomicsGreedy, relaxEnzConcs"]
  RL -->|no| RX
  RD["ecModel for simulation and analysis"]
  RL -->|yes| RD
  RX --> RD
  F -.->|without proteomics| RD
  AN["<b>Analyse an ecModel</b><br/>ecFVA, plotEcFVA<br/>randomSampling<br/>mapRxnsToConv"]
  EN["<b>Find engineering targets</b><br/>ecFSEOF"]
  CX["<b>Make a context-specific ecModel</b><br/>getSubsetEcModel"]
  EU["<b>Enzyme usage and bottlenecks</b><br/>getEnzymeUsage, reportEnzymeUsage<br/>getEnzymeBottlenecks, getConcControlCoeffs<br/>getPfbaEnzymes"]
  RD --> AN
  RD --> EN
  RD --> CX
  RD --> EU
  click P href "first-ecmodel.html"
  click S href "ecmodel-structure.html"
  click K href "kcat-sources.html"
  click C href "custom-kcats.html"
  click PP href "protein-pool.html"
  click T href "kcat-tuning.html"
  click A href "advanced-tuning.html"
  click F href "first-ecmodel.html"
  click PR href "proteomics.html"
  click RX href "relaxing-proteomics.html"
  click AN href "analysis.html"
  click EN href "engineering-targets.html"
  click CX href "context-ecmodel.html"
  click EU href "enzyme-usage.html"
```
::::
::::{tab-item} 🐍 Python
:sync: python

:::{div} workflow-pdf
{download}`Download the Python diagram as PDF <../_static/workflow-python.pdf>`
:::

```{mermaid}
:config: {"flowchart": {"useMaxWidth": false}}

flowchart TB
  classDef quick stroke-width:3px
  classDef opt stroke-dasharray: 5 4
  P["<b>Build an ecModel</b><br/>geckopy init<br/>fill model_adapter.toml"]:::quick
  S["<b>Choose the ecModel structure</b><br/>ModelAdapter.from_folder<br/>load_conventional_gem<br/>make_ec_model (full or light)<br/>get_complex_data, apply_complex_data (optional)"]:::quick
  K["<b>Choose the kcat sources</b><br/>fill_eccodes_from_gem or fill_eccodes_from_database<br/>find_met_smiles<br/>update_kcat_sources<br/>assign_kcats (preview: collect_kcats)"]:::quick
  C["<b>Set custom kcats</b><br/>data/kcats/custom.tsv<br/>convert_custom_kcats (GECKO 3 file)"]:::opt
  PP["<b>Set the protein pool</b><br/>set_prot_pool_size<br/>calculate_f_factor (optional)"]:::quick
  G{"model.slim_optimize: growth reaches the target?"}
  T["<b>Choose a kcat tuning</b><br/>standard: sensitivity_tuning, fit_sigma"]:::quick
  A["<b>Tune kcats against experimental data</b><br/>screen_kcat_leverage, select_tunable_mask<br/>review_assignment<br/>cmaes_kcat_tuning"]
  F["<b>Functional ecModel</b><br/>save_ec_model"]:::quick
  P --> S --> K --> PP --> G
  C --> K
  G -->|no| T
  G -->|no, several conditions measured| A
  G -->|yes| F
  T --> F
  A --> F
  PR["<b>Constrain enzymes with proteomics</b><br/>load_prot_data, fill_enz_concs<br/>level_complex_concs, constrain_enz_concs<br/>calculate_f_factor, set_prot_pool_size<br/>load_flux_data, apply_flux_data_constraints"]:::opt
  F --> PR
  RL{"Growth reaches the target?"}
  PR --> RL
  RX["<b>Relax proteomics constraints</b><br/>one of flexibilize_enz_concs,<br/>relax_proteomics_greedy, relax_enz_concs"]
  RL -->|no| RX
  RD["ecModel for simulation and analysis"]
  RL -->|yes| RD
  RX --> RD
  F -.->|without proteomics| RD
  AN["<b>Analyse an ecModel</b><br/>ec_fva<br/>random_sampling<br/>map_rxns_to_conv"]
  EN["<b>Find engineering targets</b><br/>ec_fseof"]
  CX["<b>Make a context-specific ecModel</b><br/>get_subset_ec_model"]
  EU["<b>Enzyme usage and bottlenecks</b><br/>enzyme_usage, report_enzyme_usage<br/>get_enzyme_bottlenecks, get_conc_control_coeffs<br/>pfba_enzymes"]
  RD --> AN
  RD --> EN
  RD --> CX
  RD --> EU
  click P href "first-ecmodel.html"
  click S href "ecmodel-structure.html"
  click K href "kcat-sources.html"
  click C href "custom-kcats.html"
  click PP href "protein-pool.html"
  click T href "kcat-tuning.html"
  click A href "advanced-tuning.html"
  click F href "first-ecmodel.html"
  click PR href "proteomics.html"
  click RX href "relaxing-proteomics.html"
  click AN href "analysis.html"
  click EN href "engineering-targets.html"
  click CX href "context-ecmodel.html"
  click EU href "enzyme-usage.html"
```
::::
:::::

## Pages, order and alternatives

Each row is a guide page with the page it runs after and what it leaves behind. The functions of each page are listed in the diagram and in the Functions table of the page.

| Page | Run after | Output |
| --- | --- | --- |
| [Build an ecModel](first-ecmodel.md) | none | a project folder with `model_adapter.toml`, and at the end a saved functional ecModel |
| [Choose the ecModel structure](ecmodel-structure.md) | project folder | ecModel with enzymes and protein pool, without kcats |
| [Choose the kcat sources](kcat-sources.md) | ecModel structure | `data/kcats/<source>.tsv`, and `ec.kcat` applied as enzyme constraints |
| [Set custom kcats](custom-kcats.md) (optional) | none; read by the first stage of every preset | `data/kcats/custom.tsv` |
| [Set the protein pool](protein-pool.md) | applied kcats | upper bound of the protein pool exchange |
| [Choose a kcat tuning](kcat-tuning.md) | protein pool, growth rate below the target | tuned `ec.kcat` and $\sigma$ |
| [Tune kcats against experimental data](advanced-tuning.md) | protein pool, growth rates and exchange fluxes of several conditions; alternative to the standard tuning | tuned `ec.kcat` |
| [Constrain enzymes with proteomics](proteomics.md) (optional) | functional ecModel | proteomics-constrained ecModel |
| [Relax proteomics constraints](relaxing-proteomics.md) | proteomics-constrained ecModel below the target growth rate | relaxed ecModel |
| [Analyse an ecModel](analysis.md), [Find engineering targets](engineering-targets.md), [Make a context-specific ecModel](context-ecmodel.md), [Enzyme usage and bottlenecks](enzyme-usage.md) | any ecModel; independent of each other | results, or a context-specific ecModel |

## Reading the paths

- **Quick path:** [Build an ecModel](first-ecmodel.md) runs the boxes with a thick outline in one go, with the default of each decision page. A decision page is needed only to change a default.
- **Kcats:** `updateKcatSources` (Python: `update_kcat_sources`) makes the source files that the preset of `model_adapter.toml` reads, and `assignKcats` (Python: `assign_kcats`) selects one kcat per reaction from them, with the custom kcats first.
- **Tuning:** the standard tuning raises kcats one at a time until one target growth rate is reached. Tuning against experimental data fits many kcats to the measured growth rates and fluxes of several conditions.
- **Relaxation:** the relaxation methods are alternatives with different stringency ([Relax proteomics constraints](relaxing-proteomics.md)).
- **Analysis:** the analysis pages work on any ecModel and do not depend on each other.

## See also

- [Guide](index.md), the list of pages.
- [Basic model operations](basic-model-operations.md), bounds, objectives and FBA.
