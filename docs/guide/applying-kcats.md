# Applying kcats

The kcat source files gathered on [Gathering kcats](gathering-kcats.md) become one kcat per reaction in `ec.kcat`, the kcats become enzyme constraints in the stoichiometry, and the protein pool exchange reaction gets a bound. The product is a draft ecModel with active enzyme constraints. Its growth rate depends on the sigma, $P_{tot}$ and f parameters, and [Growth-rate tuning](growth-rate-tuning.md) covers making it functional.

## Functions

| MATLAB | Python | Note |
|---|---|---|
| `assignKcats` | `assign_kcats` | decide one kcat per reaction from the kcat source files and apply the kcat constraints |
| `collectKcats` | `collect_kcats` | decide the kcats without changing the model |
| `convertCustomKcats` | `convert_custom_kcats` | convert `data/customKcats.tsv` into `data/kcats/custom.tsv` |
| `applyCustomKcats` | `apply_custom_kcats` | apply the kcats of `data/customKcats.tsv` |
| `getKcatAcrossIsozymes` | `fill_kcats_from_isozymes` | fill missing kcats with the mean of their isozymes |
| `getStandardKcat` | `assign_standard_kcat` | assign a standard kcat to reactions without a gene association |
| `assignKcatValues` | `apply_kcat_list` | write one kcat per reaction from a kcat list to `ec.kcat` |
| `applyKcatConstraints` | `apply_kcat_constraints` | apply `ec.kcat` to the stoichiometry of the ecModel |
| `setProtPoolSize` | `set_prot_pool_size` | set the upper bound of the protein pool exchange reaction |
| `calculateFfactor` | `calculate_f_factor` | compute the f factor from proteomics data |

## Setup

The page continues from an ecModel built as described on [Building an empty ecModel](building-ec-model.md), with the kcat source files in `data/kcats` (see [Gathering kcats](gathering-kcats.md)). The kcat order is set in `[kcat_assignment]` of `model_adapter.toml` (see [Kcat assignment](../gecko4-kcat-assignment.md) and [Model adapter parameters](model-adapter-parameters.md)). The standard kcat needs `data/uniprot.tsv`, and the f factor can use `data/paxDB.tsv` (see [Files in the data folder](data-folder-files.md)).

## Provide custom kcat values

Custom kcat values can be an alternative or sole source, based on manual curation, results from later in the reconstruction, or another prediction procedure such as in vivo apparent enzyme turnover numbers. The source file `data/kcats/custom.tsv` holds them. It is a TSV with `#` header lines and the columns `rxn`, `enzymes`, `substrate`, `kcat`, `log10_sd`, `source`, `detail`, `ec_code` and `note`. A row names a reaction in `rxn` (the identifier of the conventional reaction, with `_REV` for the reverse direction), the UniProt accessions of an enzyme set in `enzymes` (joined by ` + `), or both, and the kcat in s^-1. Every preset starts with the stage `custom`, so the custom kcats take precedence over all other sources. [Project format 4](../gecko4-project-format.md#kcat-source-files) describes the format of the kcat source files.

A project of GECKO 3 documents the custom kcats in `data/customKcats.tsv` in the project folder. `convertCustomKcats` converts the file with the matching rules of `applyCustomKcats`, including which of two entries for the same reaction wins, and writes `data/kcats/custom.tsv`. The ecModel must be a full ecModel; the `custom.tsv` written also applies to light ecModels. An existing `custom.tsv` is not overwritten.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[file, report] = convertCustomKcats(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import convert_custom_kcats

path, report = convert_custom_kcats(ec_model)
```
:::
::::

In MATLAB, `report` is a struct: `report.rows` is the number of rows written and `report.partial` lists the reactions whose enzymes match an entry in part. In Python, `report` is a dict with the number of rows written as `report["rows"]`, and has no `partial`.

Without `data/kcats/custom.tsv`, `collectKcats` applies `data/customKcats.tsv` itself when a stage lists `custom`. The file can also be applied to an ecModel directly:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, rxnUpdated, notMatch] = applyCustomKcats(ecModel);
```

This overwrites existing values in `ecModel.ec.kcat` for matching reactions, on the assumption that custom values carry higher confidence. The stoichiometry changes when `applyKcatConstraints` runs.

Custom values that fail to match: if `notMatch` contains reactions, their values were not successfully applied, because the gene association between the model and the input file is a partial match: at least 50 %, but not 100 %. A gene association that matches less than 50 % is skipped and does not appear in `notMatch`. Inspect which enzymes are associated with the reaction in the ecModel and curate the input file to resolve it.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_custom_kcats

apply_custom_kcats(ec_model, path=params.path / "data" / "customKcats.tsv")
```

The same overwrite behaviour and the same gene-match threshold of 50 % apply here; unmatched rows are logged and no `notMatch` list is returned. By default, `apply_custom_kcats` calls `apply_kcat_constraints` after updating `ec.kcat`; `apply=False` leaves the stoichiometry unchanged.
:::
::::

## Assign kcats from the source files

`assignKcats` decides one kcat per reaction from the kcat source files, writes `ec.kcat` and `ec.source`, and applies the kcat constraints with `applyKcatConstraints`. The order of the sources follows the preset or the stages of `[kcat_assignment]`; [Kcat assignment](../gecko4-kcat-assignment.md) describes the presets, the stages and the gathering of missing source files with `updateKcatSources`. Kcats that the model had are replaced, because the source files are the input of the assignment. After the stages, `assignKcats` fills reactions without a kcat from their isozymes for full ecModels when `isozymes` is true, and gives the remaining reactions the standard kcat when `standard` is true; both options are true by default.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, decisions] = assignKcats(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import assign_kcats

decisions, report = assign_kcats(ec_model)
```
:::
::::

`decisions` has one row per reaction of `ec`: the stage that decided the kcat (a stage number, `custom`, `isozymes` (full ecModels) or `standard`, and empty when no kcat was found), the source as written to `ec.source`, the kcat, the number of candidate values and their range in log10 units. For a combined value it also has the uncertainty in log10 units. The table is written to `output/<model id>_kcatDecisions.tsv` unless `writeReport` (Python: `write_report`) is false. `report` records the preset, the source files that a stage names and that do not exist, and the reactions of each source file that were not applied.

`collectKcats` makes the same decisions without changing the model and returns the ecModel with the decided kcats, before the kcat constraints. The reactions without a kcat are those with an empty stage:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
decisions = collectKcats(ecModel);
decisions(strcmp(decisions.stage, ''), :)
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import collect_kcats

decisions, report, ec_copy = collect_kcats(ec_model)
decisions[decisions["stage"] == ""]
```

`collect_kcats` returns a copy of the ecModel.
:::
::::

`assignKcatValues` (Python: `apply_kcat_list`) writes one kcat per reaction from a kcat list in memory to `ec.kcat`, with the criteria `max`, `min`, `median` or `mean`. [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md) describes how it relates to `assignKcats`.

The functions of the following sections change `ec.kcat` of a model that has been assigned, or of a model whose kcats were set in other ways. `assignKcats` replaces all kcats, `applyCustomKcats` overwrites the matching reactions, and the isozyme and standard steps fill the reactions without a kcat. Each documents its source in `ec.source`, for example `custom`, `isozymes` or `standard`.

## Mean kcat of isozymes (optional)

When a kcat is not defined for every isozymatic variant of a reaction, the variant lacking a kcat gets no protein cost and is preferred over variants that do have one, since it looks free in the optimisation. Substituting missing values in `ec.kcat` with the mean kcat of their isozymes avoids this. Isozymes with a kcat above 0 enter the mean.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = getKcatAcrossIsozymes(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fill_kcats_from_isozymes

fill_kcats_from_isozymes(ec_model)
```

`get_kcat_across_isozymes` also exists as a deprecated alias. `fill_kcats_from_isozymes` updates `ec_model.ec.kcat`, as `getKcatAcrossIsozymes` does; `apply=True` also calls `apply_kcat_constraints` for the reactions it filled. The option `aggregate` (`mean`, `median` or `max`) sets how the kcats of the isozymes are combined; the default is `kcat_aggregate_isozymes` of the model adapter, which is `mean`.
:::
::::

This step does not apply to light ecModels, where the most efficient isozyme sets the cost; `getKcatAcrossIsozymes` raises an error on a light ecModel (Python: `fill_kcats_from_isozymes` raises `NotImplementedError`).

:::{admonition} Example output
:class: note

`ec.kcat` is updated so every isozymic reaction with at least one kcat has a value, with `ec.source` for those reactions reading `isozymes`. The stoichiometric coefficients are unaffected until the constraints are applied below.
:::

## Assign a standard kcat value (optional)

Reactions without genes associated in the starting GEM (empty gene-reaction rules) cannot carry enzyme constraints, for lack of enzyme data. For such reactions, excluding exchange, spontaneous, transport and pseudo-reactions (reaction names that contain `pseudoreaction` or `SLIME rxn`, and the reactions in `data/pseudoRxns.tsv`), a standard kcat and a standard pseudo-enzyme (`prot_standard`) constrain catalytic capacity instead. The standard kcat is the median of the kcat values of the reactions in the same subsystem, when the subsystem has at least 10 reactions with a kcat (the option `threshold`), and the median of every kcat in `ec.kcat` otherwise. The standard molecular weight is the median across every protein in the organism, and a `usage_prot_standard` reaction is added.

Reactions that are annotated with an enzyme but have a kcat of 0 or `NaN` receive the standard kcat as well and keep their enzyme. Earlier standard assignments (`standard` in `ec.source`) are removed when the function runs again.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, rxnsMissingGPR, standardMW, standardKcat, rxnsNoKcat] = getStandardKcat(ecModel);
```

The standard MW and the subsystem-agnostic standard kcat are reported in `standardMW` and `standardKcat`; `rxnsNoKcat` lists the reactions whose kcat of 0 or `NaN` was replaced with the standard value.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import assign_standard_kcat

assign_standard_kcat(ec_model, uniprot_db)
```

`get_standard_kcat` also exists as a deprecated alias of `assign_standard_kcat`. The function returns nothing; the reactions missing a GPR, the standard MW and the standard kcat are logged.
:::
::::

## Apply the enzyme constraints

With `ec.kcat` populated from the sources above, apply the enzyme constraints. `assignKcats` has applied them already; this call re-applies them after a change of `ec.kcat`, `ec.mw` or the complex data:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = applyKcatConstraints(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_kcat_constraints

apply_kcat_constraints(ec_model)
```
:::
::::

This modifies the stoichiometric coefficients of the ecModel (the S-matrix in MATLAB, the cobra reaction stoichiometries in Python) to directly include the protein cost, based on the kcat values from `ec.kcat`, the MWs from `ec.mw` and, if applied, the enzyme complex stoichiometry from `applyComplexData`/`apply_complex_data` (see [Building an empty ecModel](building-ec-model.md#apply-enzyme-complex-stoichiometry-optional)). Enzymes are directly involved as pseudo-substrates, reflecting enzyme usage. Existing enzyme constraints of the reactions are removed first, so the function can run again at any point. A reaction with a kcat of 0 or `NaN` gets no enzyme cost. Both toolboxes can restrict the update to some reactions (MATLAB: the option `updateRxns`, Python: the argument `update_rxns`).

In a light ecModel, the cost of a reaction is the lowest MW/kcat across its isozymes, written to the `prot_pool` row of the reaction.

:::{admonition} Example output
:class: note

Every stoichiometric coefficient added or changed above is applied to the ecModel. The coefficient of an enzyme pseudo-metabolite is:

$$ \frac{MW}{k_{cat} \times 3600} \times (\text{complex stoichiometry}) $$

where the factor 3,600 converts kcat from s^-1 to h^-1, matching the unit of metabolic rates. Each enzymatic reaction gets one kcat value, which for complexes can be the highest predicted value across subunits. For example, if reaction X to Y is catalysed by a complex of subunits A, B and C at a ratio 1:1:2, all with MW 27,000 Da and highest predicted kcat of 30 s^-1, the reaction becomes X + 0.25 A + 0.25 B + 0.5 C to Y.
:::

## Constrain the protein pool exchange reaction

Enzyme pseudo-metabolites are replenished from the total protein pool by default. The protein pool exchange reaction `prot_pool_exchange` runs forward, from nothing to `prot_pool`, with the bounds 0 and 1000. The `usage_prot_<enzyme>` reactions run forward as well, from `prot_pool` to `prot_<enzyme>`. `setProtPoolSize` sets the upper bound of `prot_pool_exchange` to $P_{tot} \times f \times \sigma \times 1000$ mg/gDCW, calculated from the sigma, $P_{tot}$ and f parameters in the model adapter (average enzyme saturation, total protein content and the fraction of proteins included in the model). An ecModel of GECKO 3 has the protein reactions in the reverse direction; `upgradeEcModel` converts it (see [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md)).

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setProtPoolSize(ecModel);
```

If quantitative proteomics data are available, for example via PaxDB, store them in `data/paxDB.tsv` and calculate the f factor:

```matlab
f = calculateFfactor(ecModel);
```

Then use the new f factor to set the protein pool constraint:

```matlab
ecModel = setProtPoolSize(ecModel, [], f);
```

Without `data/paxDB.tsv` and without the option `protData`, `calculateFfactor` returns 0.5 and prints a warning.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import set_prot_pool_size

set_prot_pool_size(ec_model, p_tot=params.p_tot, f=params.f, sigma=params.sigma)
```

With no arguments beyond `ec_model`, `set_prot_pool_size` reads `p_tot`, `f` and `sigma` from `ec_model.adapter.params`; the explicit keyword arguments above override them. The function returns the bound it set. If quantitative proteomics data are available via PaxDB, store them in `data/paxDB.tsv` and calculate the f factor:

```python
from geckopy import calculate_f_factor, load_pax_db

pax_data = load_pax_db(params.path / "data" / "paxDB.tsv", uniprot_db)
f = calculate_f_factor(ec_model, pax_data)
```

Then use the new f factor to set the protein pool constraint:

```python
set_prot_pool_size(ec_model, f=f)
```

`calculate_f_factor` has no default for the proteomics data; without measurements, `f = 0.5` is used directly.
:::
::::

:::{admonition} Values to define the total protein pool are missing
:class: note

sigma, $P_{tot}$ and f each have the standard value 0.5 when no better estimate exists. If the resulting maximum growth rate is too small or too large, adjusting sigma manually is a reasonable way to reach a more plausible value; see [Growth-rate tuning](growth-rate-tuning.md#protein-pool-constraint).
:::

:::{admonition} Example output
:class: note

With $P_{tot}$ = 0.5, f = 0.5 and sigma = 0.5, the upper bound of `prot_pool_exchange` becomes 125 mg/gDCW.
:::

## The ec structure

Enzyme-related information is stored in `ecModel.ec` (MATLAB) or `ec_model.ec` (Python, an `EcData` instance), both referred to as `ec`. Field names match between languages except for `rxnEnzMat`/`rxn_enz_mat`. The structure is similar for full and light ecModels but differs in how the reaction-related fields are populated: in full ecModels the whole model is expanded, each isozyme gets a separate reaction, and each reaction maps to one entry in the structure; in light ecModels the reactions are not split per isozyme, and some starting-GEM reactions have several entities represented in the structure.

| Field | Data type | Size | Description |
|-------|-----------|------|-------------|
| `rxns` | string array (Python: `list[str]`) | m | Reaction identifiers gathered from the ecModel, after expansion and making irreversible. |
| `rxnEnzMat` (Python: `rxn_enz_mat`) | matrix (Python: sparse `scipy.sparse.csr_matrix`) | m x n | Comparable to the model's reaction-gene matrix, but Enz refers to `ec.enzymes`. Positive integers give the number of enzyme subunits annotated to each reaction. |
| `kcat` | float vector (Python: `numpy.ndarray`) | m | One value per reaction-enzyme (complex) combination, in s^-1, gathered from various sources; `0` means no kcat assigned yet. |
| `source` | string array (Python: `list[str]`) | m | Where the kcat came from, for example `dlkcat`, `custom`, `brenda (wc=0, origin=1)`, `combined (sd=<log10 sd>, n=<sources>)`, `isozymes` or `standard`. |
| `notes` | string array (Python: `list[str]`) | m | Free-text notes the user adds. |
| `eccodes` | string array (Python: `list[str]`) | m | EC numbers gathered from the ecModel and/or UniProt or KEGG, used for matching kcats by EC number. |
| `genes` | string array (Python: `list[str]`) | n | Gene identifiers, corresponding to the genes of the ecModel, matching the columns in `rxnEnzMat` (Python: `rxn_enz_mat`). |
| `enzymes` | string array (Python: `list[str]`) | n | UniProt protein identifiers derived from the matching entries in `genes`. |
| `mw` | float vector (Python: `numpy.ndarray`) | n | Molecular weight for each enzyme, in Dalton; unknown is `NaN`. |
| `sequence` | string array (Python: `list[str]`) | n | Amino acid sequence for each enzyme. |
| `concs` | float vector (Python: `numpy.ndarray`) | n | Measured concentration of each enzyme in mg/gDCW; unmeasured is `NaN`. |

In Python, `ec.n_rxns` and `ec.n_enzymes` return the m and n sizes above, and `ec.gecko_light` is a boolean recording which layout the model uses; MATLAB has no fields with these names.

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| `No kcat source file <file>; it is left out` | a stage names a source that has no file in `data/kcats` | Gather the file with `updateKcatSources`, or remove the source from the stage |
| Kcats set with `setKcatForReactions` are gone after `assignKcats` | `assignKcats` replaces the kcats of the model | Place the kcats in `data/kcats/custom.tsv`, or set them after the assignment and apply the constraints again |
| `notMatch` of `applyCustomKcats` is not empty | the enzymes of an entry match the reaction in part | Curate `data/customKcats.tsv` or `custom.tsv` for the enzyme set of the reaction |
| `No kcat values are provided in model.ec.kcat` | every kcat is 0 when `getKcatAcrossIsozymes` or `applyKcatConstraints` runs; `applyKcatConstraints` also clears existing enzyme constraints, `getKcatAcrossIsozymes` leaves the model unchanged | Run `assignKcats` first |
| `convertCustomKcats` raises an error that `custom.tsv` exists | the target file is not overwritten | Remove the file or give another `outFile` |
| `getKcatAcrossIsozymes` raises an error on a light ecModel | isozymes are not split in a light ecModel | Skip the step; the constraint uses the most efficient isozyme |
| Growth rate far from the experimental value | sigma, $P_{tot}$ or f differs from the cell | See [Growth-rate tuning](growth-rate-tuning.md) |

## See also

- [Kcat assignment](../gecko4-kcat-assignment.md), the presets and stages of `assignKcats`.
- [Growth-rate tuning](growth-rate-tuning.md), the next step: diagnosing why growth is too low and tuning the model to a realistic rate.
- [Gathering kcats](gathering-kcats.md), where the kcat source files applied here come from.
- [API reference](../api/index.md), every function in both toolboxes.
