# Workflow overview

<!-- docs-site: concept-page -->

The diagram shows the order of the guide pages, from a new project to the analysis of an ecModel, with the functions of each page. The boxes with a thick outline are the steps of [Build an ecModel](first-ecmodel.md), which makes a working ecModel with the default settings; that page skips the functions marked optional, and the steps from the ecModel structure to the kcat tuning each have a decision page with the options; the diamond of the kcat tuning opens its decision page. A solid arrow connects pages that run one after another, a dotted arrow is an optional path, a diamond a choice between paths, and a dashed outline an optional page. A click on a box opens its page. The button in the corner of a diagram opens it in full screen, where the mouse wheel zooms and a drag pans. In the page, the wheel zooms with Ctrl (Cmd on macOS) held. The download icon at the top of each tab saves its diagram as a PDF.

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
  K["<b>Choose the kcat sources</b><br/>getECfromGEM, then getECfromDatabase<br/>findMetSmiles<br/>updateKcatSources<br/>collectKcats (optional preview)<br/>assignKcats"]:::quick
  C["<b>Set custom kcats</b><br/>data/kcats/custom.tsv<br/>convertCustomKcats (required for a<br/>GECKO 3 data/customKcats.tsv)"]:::opt
  PP["<b>Set the protein pool</b><br/>setProtPoolSize<br/>calculateFfactor (optional)"]:::quick
  G{"<b>Choose a kcat tuning</b><br/>measured data"}
  T["<b>Tune kcats with sensitivityTuning</b><br/>sensitivityTuning<br/>(no change when growth reaches the target)<br/>then sigmaFitter when growth is above the target"]:::quick
  A["<b>Tune kcats with evotune</b><br/>screenKcatLeverage<br/>reviewKcatAssignment (optional)<br/>cmaesKcatTuning (selects with selectTunableMask)<br/>no sigmaFitter afterwards"]
  F["<b>Functional ecModel</b><br/>saveEcModel"]:::quick
  P --> S --> K --> PP --> G
  C -.-> K
  T -.->|keep a tuned kcat| C
  A -.->|keep a tuned kcat| C
  G -->|one maximum growth rate| T
  G -->|measured fluxes or several growth rates| A
  T --> F
  A --> F
  PR["<b>Constrain enzymes with proteomics</b> (full ecModel)<br/>loadProtData, fillEnzConcs<br/>levelComplexConcs (optional), constrainEnzConcs<br/>getIsozymeCoverage, zeroUnmeasuredIsozymes (optional)<br/>loadFluxData, calculateFfactor (optional)<br/>setProtPoolSize, constrainFluxData"]:::opt
  F -.-> PR
  F -.-> CX
  CX -.->|proteomics of the context| PR
  CX -.-> RD
  CX -.->|or build an ecModel from the context-specific GEM| P
  RL{"Growth reaches the measured growth rate?"}
  PR --> RL
  RX["<b>Relax proteomics constraints</b><br/>flexibilizeEnzConcs (recommended),<br/>relaxProteomicsGreedy when enzymes at 0 limit,<br/>relaxEnzConcs to compare"]
  RL -->|no| RX
  RD["ecModel for simulation and analysis"]
  RL -->|yes| RD
  RX --> RD
  F -.->|without proteomics| RD
  AN["<b>Analyse an ecModel</b><br/>ecFVA, plotEcFVA<br/>randomSampling (RAVEN)<br/>mapRxnsToConv"]
  EN["<b>Find engineering targets</b><br/>ecFSEOF"]
  CX["<b>Make a context-specific ecModel</b><br/>getSubsetEcModel, before proteomics"]:::opt
  EU["<b>Enzyme usage and bottlenecks</b> (full ecModel)<br/>getEnzymeUsage, reportEnzymeUsage<br/>getEnzymeBottlenecks, getConcControlCoeffs<br/>getPfbaEnzymes"]
  RD --> AN
  RD --> EN
  RD --> EU
  click P href "first-ecmodel.html"
  click S href "ecmodel-structure.html"
  click K href "kcat-sources.html"
  click C href "custom-kcats.html"
  click PP href "protein-pool.html"
  click G href "kcat-tuning.html"
  click T href "standard-tuning.html"
  click A href "evotune.html"
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
  K["<b>Choose the kcat sources</b><br/>load_uniprot_tsv, load_kegg_tsv<br/>fill_eccodes_from_gem, then fill_eccodes_from_database<br/>find_met_smiles<br/>update_kcat_sources<br/>collect_kcats (optional preview)<br/>assign_kcats"]:::quick
  C["<b>Set custom kcats</b><br/>data/kcats/custom.tsv<br/>convert_custom_kcats (required for a<br/>GECKO 3 data/customKcats.tsv)"]:::opt
  PP["<b>Set the protein pool</b><br/>set_prot_pool_size<br/>calculate_f_factor (optional)"]:::quick
  G{"<b>Choose a kcat tuning</b><br/>measured data"}
  T["<b>Tune kcats with sensitivity_tuning</b><br/>sensitivity_tuning<br/>(no change when growth reaches the target)<br/>then fit_sigma when growth is above the target"]:::quick
  A["<b>Tune kcats with evotune</b><br/>screen_kcat_leverage<br/>review_assignment (optional)<br/>cmaes_kcat_tuning (selects with select_tunable_mask)<br/>no fit_sigma afterwards"]
  F["<b>Functional ecModel</b><br/>save_ec_model"]:::quick
  P --> S --> K --> PP --> G
  C -.-> K
  T -.->|keep a tuned kcat| C
  A -.->|keep a tuned kcat| C
  G -->|one maximum growth rate| T
  G -->|measured fluxes or several growth rates| A
  T --> F
  A --> F
  PR["<b>Constrain enzymes with proteomics</b> (full ecModel)<br/>load_prot_data, fill_enz_concs<br/>level_complex_concs (optional), constrain_enz_concs<br/>get_isozyme_coverage, zero_unmeasured_isozymes (optional)<br/>load_flux_data, calculate_f_factor (optional)<br/>set_prot_pool_size, apply_flux_data_constraints"]:::opt
  F -.-> PR
  F -.-> CX
  CX -.->|proteomics of the context| PR
  CX -.-> RD
  CX -.->|or build an ecModel from the context-specific GEM| P
  RL{"Growth reaches the measured growth rate?"}
  PR --> RL
  RX["<b>Relax proteomics constraints</b><br/>flexibilize_enz_concs (recommended),<br/>relax_proteomics_greedy when enzymes at 0 limit,<br/>relax_enz_concs to compare"]
  RL -->|no| RX
  RD["ecModel for simulation and analysis"]
  RL -->|yes| RD
  RX --> RD
  F -.->|without proteomics| RD
  AN["<b>Analyse an ecModel</b><br/>ec_fva<br/>random_sampling (raven-toolbox)<br/>map_rxns_to_conv"]
  EN["<b>Find engineering targets</b><br/>ec_fseof"]
  CX["<b>Make a context-specific ecModel</b><br/>get_subset_ec_model, before proteomics"]:::opt
  EU["<b>Enzyme usage and bottlenecks</b> (full ecModel)<br/>enzyme_usage, report_enzyme_usage<br/>get_enzyme_bottlenecks, get_conc_control_coeffs<br/>pfba_enzymes"]
  RD --> AN
  RD --> EN
  RD --> EU
  click P href "first-ecmodel.html"
  click S href "ecmodel-structure.html"
  click K href "kcat-sources.html"
  click C href "custom-kcats.html"
  click PP href "protein-pool.html"
  click G href "kcat-tuning.html"
  click T href "standard-tuning.html"
  click A href "evotune.html"
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
| [Set custom kcats](custom-kcats.md) (optional) | the ecModel structure, or a kcat tuning whose result is kept; read by the first stage of every preset | `data/kcats/custom.tsv` |
| [Set the protein pool](protein-pool.md) | applied kcats | upper bound of the protein pool exchange |
| [Choose a kcat tuning](kcat-tuning.md) | protein pool | the choice between the two tunings; the check of a tuned kcat against its source |
| [Tune kcats with sensitivityTuning](standard-tuning.md) | protein pool, and one maximum growth rate; changes no kcat when the growth rate reaches the target | tuned `ec.kcat`, and $\sigma$ lowered when the growth rate ended above the target |
| [Tune kcats with evotune](evotune.md) | protein pool, and measured maximum growth rates, exchange fluxes or both, of one or more conditions; alternative to `sensitivityTuning` | tuned `ec.kcat`; $\sigma$ stays as set |
| [Constrain enzymes with proteomics](proteomics.md) (optional) | functional full ecModel | proteomics-constrained ecModel |
| [Relax proteomics constraints](relaxing-proteomics.md) | proteomics-constrained ecModel below the measured growth rate | relaxed ecModel |
| [Analyse an ecModel](analysis.md), [Find engineering targets](engineering-targets.md), [Enzyme usage and bottlenecks](enzyme-usage.md) | a functional, proteomics-constrained or relaxed ecModel (enzyme usage: full ecModel only); independent of each other | results |
| [Make a context-specific ecModel](context-ecmodel.md) (optional) | functional ecModel without proteomics constraints | a context-specific ecModel, to which the proteomics of the context can be added |

## Reading the paths

- **Quick path:** [Build an ecModel](first-ecmodel.md) runs the boxes with a thick outline in one go, without the functions marked optional and with the default of each decision page. A decision page is needed only to change a default.
- **Kcats:** `updateKcatSources` (Python: `update_kcat_sources`) makes the source files that the preset of `model_adapter.toml` reads, and `assignKcats` (Python: `assign_kcats`) selects one kcat per reaction from them, with the custom kcats first.
- **Tuning:** [Choose a kcat tuning](kcat-tuning.md) compares the two tunings. `sensitivityTuning` (Python: `sensitivity_tuning`) raises kcats one at a time until one target growth rate is reached, and `sigmaFitter` (Python: `fit_sigma`) then lowers $\sigma$ when the growth rate ended above it; a kcat tuning only raises kcats. Evotune (`cmaesKcatTuning`, Python: `cmaes_kcat_tuning`) fits many kcats to measured growth rates, exchange fluxes or both, of one or more conditions, with $\sigma$ as set before the tuning.
- **Relaxation:** `flexibilizeEnzConcs` is the method to start with; `relaxProteomicsGreedy` raises enzymes with a bound of 0, and `relaxEnzConcs` gives a result that does not depend on the order in which enzymes become limiting, to compare with ([Relax proteomics constraints](relaxing-proteomics.md)).
- **Analysis:** the analysis pages do not depend on each other. Enzyme usage and proteomics need a full ecModel. A context-specific ecModel is trimmed from an ecModel without proteomics constraints, and the proteomics of the context are added afterwards; the other way builds an ecModel from the context-specific GEM with the steps of Build an ecModel.

## See also

- [Guide](index.md), the list of pages.
- [Basic model operations](basic-model-operations.md), bounds, objectives and FBA.
