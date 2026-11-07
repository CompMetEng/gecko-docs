# GECKO light and full ecModels

GECKO builds two ecModel layouts from the same conventional GEM, **full** and **light**. A full ecModel has a pseudo-metabolite and a usage reaction for every enzyme, and a light ecModel has one shared protein pool. Full and light ecModels differ in layout and in the functions that they support.

## Functions

| MATLAB | Python | Note |
|---|---|---|
| `makeEcModel(model, true)` | `make_ec_model(model, adapter, gecko_light=True)` | build a light ecModel in place of a full one |
| `getSubsetEcModel` | `get_subset_ec_model` | build a context-specific ecModel from a general ecModel, full or light |

## Setup

A conventional GEM and a model adapter are needed, as described in [Building an empty ecModel](building-ec-model.md), which also shows the build of both layouts. The flag `geckoLight` (Python: `gecko_light`) is set when the ecModel is built, and it is stored in the ecModel file as `gecko_light` (see [ecModel YAML format](yaml-format.md)).

## Layout of the two ecModels

When a metabolic reaction is catalysed by an enzyme, GECKO encodes the protein cost of that catalysis in the model in one of two ways:

- **Full ecModel.** For each enzyme, GECKO adds a pseudo-metabolite (`prot_<uniprot>`) and a usage reaction (`usage_prot_<uniprot>`). A reaction catalysed by several isozymes is split into one copy per isozyme. The solver reports the usage of each enzyme directly, for example of enzyme P00350. The LP is much larger than that of the conventional GEM: the `ecYeastGEM.yml` of the `full_ecModel` tutorial has 8001 reactions, of which 1145 are protein reactions, and a Human-GEM full ecModel runs into the tens of thousands.
- **Light ecModel.** The per-enzyme pseudo-metabolites and usage reactions are left out, and the cost is drawn from a single shared protein pool. Each catalysed reaction has one extra stoichiometric coefficient against that pool, $-MW_{sum} / (k_{cat} \times 3600)$, where $MW_{sum}$ is the molecular weight of the enzymes of the isozyme, summed with the subunit copies as weights, so the reaction consumes from the pool. Isozymes are not split into separate reactions. `applyKcatConstraints` selects, for each reaction, the isozyme with the smallest $MW_{sum} / k_{cat}$ among the isozymes that have a kcat and an enzyme, and writes that coefficient. A reaction without a usable isozyme gets no coefficient. The LP stays close to the size of the conventional GEM.

A light ecModel suits genome-scale models for which the full layout solves slowly, such as Human-GEM or Recon3D. The full layout suits smaller models, such as yeast or *E. coli*.

| Property | Full | Light |
|---|---|---|
| Isozyme expansion | reactions split, one copy per isozyme (`_EXP_<N>` suffix) | reactions stay singular; `ec.rxns` has one row per isozyme with the prefix `<nnn>_` |
| Per-enzyme pseudo-metabolite `prot_<id>` | yes | no |
| Per-enzyme usage reaction `usage_prot_<id>` | yes | no |
| Shared protein pool | yes | yes, and it is the sole enzyme constraint |
| LP size | much larger than the conventional GEM | close to the conventional GEM |

## Functions that need a full ecModel

A light ecModel has no per-enzyme pseudo-metabolites and no usage reactions. The functions that depend on them raise an error.

| Capability | MATLAB | Python |
|---|---|---|
| Proteomics constraints | `constrainEnzConcs` raises an error, because the usage reactions are missing; `flexibilizeEnzConcs` acts on the same reactions and raises the error `Protein concentrations have not been defined` when no concentration is set | `constrain_enz_concs` raises `ValueError`; `flexibilize_enz_concs` acts on the same reactions |
| Greedy proteomics relaxation | `relaxProteomicsGreedy` raises an error | `relax_proteomics_greedy` raises `NotImplementedError` |
| Enzyme usage and bottlenecks | `getEnzymeUsage`, `getEnzymeBottlenecks` and `getPfbaEnzymes` raise an error; `reportEnzymeUsage` takes the output of `getEnzymeUsage` | `enzyme_usage`, `get_enzyme_bottlenecks` and `pfba_enzymes` raise `NotImplementedError`; `report_enzyme_usage` takes the output of `enzyme_usage` |
| Flux, capacity usage or shadow price of one enzyme | no `usage_prot_<id>` reaction to read | `Enzyme.flux`, `Enzyme.cap_usage`, `Enzyme.upper_bound` and `Enzyme.shadow_price` raise `NotImplementedError` |
| Concentration or kcat of one enzyme | not applicable | the setters of `Enzyme.concentration` and `Enzyme.kcats` raise `NotImplementedError` |
| Isozyme-based functions | `getKcatAcrossIsozymes`, `addNewRxnsToEC` and `convertCustomKcats` raise an error | `fill_kcats_from_isozymes` and `add_new_rxns_to_ec` raise `NotImplementedError`, `convert_custom_kcats` raises `ValueError` |

See [Proteomics integration](proteomics-integration.md), [Relaxing overconstrained proteomics](relaxing-constraints.md) and [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md) for what these functions do on a full ecModel.

`assignKcats` and `collectKcats` skip the filling of kcats from isozymes on a light ecModel and apply the standard kcat when it is configured. The `custom.tsv` file written for a full ecModel applies to a light ecModel too.

## Functions that work on a light ecModel

Functions that read `ec.kcat` and `ec.mw`, or edit the LP directly, work on a light ecModel. These are the kcat sources and their assignment, `applyCustomKcats`, `applyKcatConstraints`, `getStandardKcat`, the kcat sensitivity tuning (`sensitivityTuning`), `applyComplexData`, `getEcRxnKeys` and `getSubsetEcModel`. `getSubsetEcModel` removes the rows of `ec.rxns` of the reactions it removes, after it drops the prefix `<nnn>_` of the row identifiers. See [Gathering kcat values](gathering-kcats.md), [Applying kcat values](applying-kcats.md) and [Growth-rate tuning](growth-rate-tuning.md).

## Reconstruction time and simulation accuracy

The comparison below builds a light and a full ecModel of yeast-GEM, populated with kcat values from BRENDA fuzzy matching alone, and runs FBA with growth maximised on each. Both toolboxes include the comparison script (`plotlightVSfull` and `plot_light_vs_full`). It sets the lower bound of the glucose uptake reaction `r_1714` to -1000 and the growth reaction `r_2111` as the objective:

| Measure | Light | Full |
|---|---|---|
| ecModel reconstruction (s) | 39 | 41 |
| FBA (s) | 0.57 | 0.89 |
| Mapping fluxes (s) | 0.103 | 0.161 |
| Growth rate that is reached (/hour) | 0.0252 | 0.0252 |

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

The `plotlightVSfull` script of the `full_ecModel` tutorial prints this comparison:

```
Comparison of duration light vs. full ecModel
ecModel reconstruction: 95% (39 vs 41 seconds)
FBA: 64% (0.57 vs 0.89 seconds)
Mapping fluxes: 64% (0.103 vs 0.161 seconds)
Growth rate that is reached: 0.0252 vs 0.0252
```
:::
::::

Reconstruction time does not differ much between the two, because both require the same time-consuming BRENDA fuzzy matching step. FBA and flux mapping back to the conventional GEM (see [Simulation and analysis](simulation-and-analysis.md)) are substantially faster on the light ecModel. The difference matters most when many simulations are run, such as an extensive ecFVA scan or many single-cell ecModels built from the same generic model.

The two ecModels reach the same growth rate, and the flux distributions they predict are near identical: the reactions that deviate by more than 0.1 % between the two are in lipid metabolism. Yeast-GEM's lipid metabolism follows the SLIMEr formulation, where reactions for each possible fatty-acyl-chain configuration are explicit and catalysed by the same enzyme, so the network has flexibility in which path it takes through lipid metabolism while reaching the same overall acyl-chain distribution. That flexibility comes from the conventional GEM and is independent of whether the enzyme constraints are recorded per enzyme or pooled.

:::{tip}
When proteomics integration is not needed, a light ecModel gives comparable predictions to a full one at a fraction of the simulation cost. Proteomics integration, per-enzyme usage and bottleneck ranking need a full ecModel; there is no light equivalent for them.
:::

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| Error `This function does not work on GECKO light models.` from `getEnzymeUsage` | The ecModel is light | Build a full ecModel |
| Error from `getEnzymeBottlenecks`, `getPfbaEnzymes` or `relaxProteomicsGreedy` that a full ecModel is required | The ecModel is light | Build a full ecModel |
| `NotImplementedError` that names gecko-light (Python) | The function or property needs per-enzyme reactions | Build a full ecModel |
| The reaction identifiers of `ec.rxns` do not match `model.rxns` | A light ecModel prefixes the rows of `ec.rxns` with `<nnn>_` | Remove the first four characters of the `ec.rxns` identifier |

## See also

- [Building an empty ecModel](building-ec-model.md), where the `geckoLight` (Python: `gecko_light`) choice is made.
- [Proteomics integration](proteomics-integration.md) and [Relaxing overconstrained proteomics](relaxing-constraints.md), which need a full ecModel.
- [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), which needs a full ecModel.
- [ecModel YAML format](yaml-format.md), for the `gecko_light` section and the identifiers of the rows of `ec.rxns`.
