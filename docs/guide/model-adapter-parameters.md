# Model adapter parameters

<!-- docs-site: concept-page -->

`model_adapter.toml` in the project folder holds the parameters of a GECKO 4 project. GECKO (MATLAB) and geckopy (Python) read the same file. The section overview is in [Project format 4](../gecko4-project-format.md). The tables give the parameters, their defaults and the MATLAB name of each parameter. The defaults are those of `src/model_adapter/adapterParameters.tsv` of GECKO, which geckopy uses as well.

## Reading the file

Paths in the file are relative to the project folder. A key that is left out gets the default of the tables. The project folder is the folder of the file, so `path` is no key.

Both toolboxes check every key when they read the file. A key that the tables do not list is an error, and so is a key inside a table that the table does not take: under `[evotune.source_groups.<group>]`, in a `[[kcat_assignment.stage]]` entry and under `[kcat_sources.<name>]`. The message names the file and the key with its full path:

```text
<full path of model_adapter.toml>: unknown key kcat_sources.brenda.k in model_adapter.toml
```

GECKO raises the error with the identifier `GECKO:loadAdapterParams`, and `ModelAdapter.from_folder` of geckopy raises `ValueError`. A parameter that GECKO alone uses goes under `[matlab.params]`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ModelAdapterManager.setDefault(projectPath);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ModelAdapter

adapter = ModelAdapter.from_folder(project_path)
```
:::
::::

`ModelAdapterManager.setDefault` makes the adapter the default of all GECKO functions that take the option `modelAdapter`. In geckopy, `adapter.params` holds the parameters under the TOML key names, and an ecModel made with `make_ec_model` holds the adapter as `ec_model.adapter`.

The `full_ecModel` tutorial uses these entries:

```toml
conv_gem = "models/yeast-GEM.yml"
org_name = "saccharomyces cerevisiae"
sigma = 0.5
p_tot = 0.5
f = 0.5
gr_exp = 0.41
c_source = "r_1714"
bio_rxn = "r_4041"
enzyme_comp = "cytoplasm"

[kegg]
id = "sce"
gene_id = "kegg"

[uniprot]
type = "proteome"
id = "UP000002311"
gene_id_field = "gene_oln"
reviewed = true

[complex]
taxonomic_id = 559292

[spontaneous]
name_contains = "spontaneous"
```

## Showing the resolved parameters

`showAdapterParams` (GECKO) and `geckopy adapter show` (geckopy) print the value of every parameter and the origin of the value. Both print the same lines.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
showAdapterParams(ModelAdapterManager.getDefault())
T = showAdapterParams(adapter);   % table with the columns key, value and origin
```
:::
:::{tab-item} 🐍 Python
:sync: python

```bash
geckopy adapter show path/to/project
```

```python
from geckopy import ModelAdapter, show_adapter_params

show_adapter_params(ModelAdapter.from_folder(project_path))
```
:::
::::

Each line has the form `<key> = <value>  [<origin>]`, in the order of `adapterParameters.tsv`. The origin is `file` (set in `model_adapter.toml`, or by an adapter class), `default`, `preset <name>` (set by the kcat assignment preset) or `not set`. Strings are printed without quotes, lists comma-separated, and whole numbers without decimals. The kcat assignment stages, the settings of each kcat source and the evotune source groups are printed as they are resolved. Some of the lines for a project that sets `gr_exp` and no kcat assignment:

```text
sigma = 0.5  [default]
gr_exp = 0.41  [file]
complex.taxonomic_id =  [not set]
evotune.source_groups.custom = custom; sigma0_log 0.1  [default]
evotune.max_growth_weight = 1  [default]
kcat_assignment.preset = brenda_ec_tree  [default]
kcat_assignment.stage[1] = select: custom, database_top, ec_tree; top_origin_limit=1  [preset brenda_ec_tree]
kcat_assignment.stage[2] = combine: okp  [preset brenda_ec_tree]
kcat_sources.brenda.aggregation = median  [preset brenda_ec_tree]
kcat_sources.ec_tree.k = 5  [preset brenda_ec_tree]
kcat_sources.okp.method = KinForm-H  [default]
```

A stage line lists the action, the sources, and the criteria and limits that differ from the defaults. With stages in the file, the preset line is `kcat_assignment.preset = none (stages are given)  [file]`.

## Model and protein pool

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `project_format` | `projectFormat` | none | Layout version of the project folder. `upgradeGECKOproject` and `geckopy upgrade` write 4 |
| `conv_gem` | `convGEM` | none (required in geckopy) | Path to the starting conventional GEM file, for example `models/yeast-GEM.yml` |
| `org_name` | `org_name` | none (required in geckopy) | Scientific name of the organism, used by `fuzzyKcatMatching` (Python: `fuzzy_kcat_matching`) and `kcatsFromBrenda` (`kcats_from_brenda`) |
| `sigma` | `sigma` | `0.5` | Average enzyme saturation factor |
| `p_tot` | `Ptot` | `0.5` | Total protein content in the cell [g protein/gDW] |
| `f` | `f` | `0.5` | Fraction of enzymes in the ecModel relative to all proteins (g enzyme/g protein). `calculateFfactor` (Python: `calculate_f_factor`) computes it from a proteomics data set |
| `gr_exp` | `gR_exp` | none | Growth rate in h^-1 that the model should reach when the nutrient uptake does not limit it, for example the measured maximum growth rate. See below the table |
| `c_source` | `c_source` | `""` | Identifier of the exchange reaction of glucose or of another preferred carbon source |
| `bio_rxn` | `bioRxn` | `""` | Identifier of the biomass or growth pseudoreaction, whose flux is the growth rate in h^-1 |
| `enzyme_comp` | `enzyme_comp` | `"cytoplasm"` | Name of the compartment of the added protein pseudometabolites; must match one of the compartment names of the ecModel |

`sensitivityTuning`, `sigmaFitter`, `flexibilizeEnzConcs` and `relaxEnzConcs` (Python: `sensitivity_tuning`, `fit_sigma`, `flexibilize_enz_concs` and `relax_enz_concs`) use `gr_exp` as the target growth rate when the call gives none. When the call gives none and the file does not set `gr_exp`, they raise the error `gr_exp is not set in model_adapter.toml` (GECKO identifier `GECKO:grExpNotSet`, Python `ValueError`).

## Database identifiers

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `kegg.id` | `kegg.ID` | `""` (KEGG is not used) | Organism code in the KEGG database, from the [KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html) |
| `kegg.gene_id` | `kegg.geneID` | `"kegg"` | Field of the KEGG entry that matches the gene identifiers of the ecModel. `kegg` takes the KEGG entry identifier. Identifiers from the "Other DBs" section of the KEGG page, such as `NCBI-GeneID`, `UniProt` or `Ensembl` (for Human-GEM), are available for some organisms |
| `uniprot.type` | `uniprot.type` | `"taxonomy"` | Whether `uniprot.id` is a taxonomy identifier (`taxonomy`) or a proteome identifier (`proteome`) |
| `uniprot.id` | `uniprot.ID` | `""` (required unless `data/uniprot.tsv` exists) | Identifier of the UniProt data set (by taxonomy or proteome) with complete coverage of the genes of the ecModel |
| `uniprot.gene_id_field` | `uniprot.geneIDfield` | `"gene_oln"` | UniProt field with the gene identifiers used in the ecModel; one of the "Returned Field" entries under "Names & Taxonomy" of the [UniProt return fields](https://www.uniprot.org/help/return_fields) |
| `uniprot.reviewed` | `uniprot.reviewed` | `false` | Whether the data is limited to reviewed (Swiss-Prot) entries. Reviewed data has the highest confidence but can have low coverage for non-model organisms |
| `complex.taxonomic_id` | `complex.taxonomicID` | none | Taxonomy identifier as available from the [Complex Portal](https://www.ebi.ac.uk/complexportal/home). Without it, no Complex Portal query is made |

## Spontaneous reactions

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `spontaneous.name_contains` | `spontaneous.name_contains` | none | Reactions whose name contains this text are spontaneous |
| `spontaneous.file` | `spontaneous.file` | none | TSV of spontaneous reactions, relative to the project folder: a header row, reaction identifiers in the first column and, optionally, a second column in which `1` or `true` marks the spontaneous reactions |

A reaction is spontaneous when either rule matches. `getStandardKcat` (Python: `assign_standard_kcat`) gives spontaneous reactions no standard kcat.

## Kcat assignment

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `kcat_assignment.preset` | `kcat_assignment.preset` | `"brenda_ec_tree"` without stages | One of `brenda_ec_tree`, `ec_tree_homologs`, `ec_tree_okp`, `okp`, `gecko_median` and `gecko_classic`. A preset and stages exclude each other |
| `kcat_assignment.isozymes` | `kcat_assignment.isozymes` | `true` | Fill reactions without a kcat from their isozymes after the stages |
| `kcat_assignment.standard` | `kcat_assignment.standard` | `true` | Give the remaining reactions the standard kcat |
| `kcat_assignment.stage` | `kcat_assignment.stage` | none | Stages in place of a preset, written as `[[kcat_assignment.stage]]` tables |
| `kcat_sources.<name>` | `kcat_sources.<name>` | set by the preset | Settings of one source file, described in [Kcat source settings](#kcat-source-settings) |

A stage has the keys `action` (`select`, the default, or `combine`), `sources`, `criteria` (`max`, `min`, `median` or `mean`; default `max`), `top_origin_limit` (default 4), `bottom_origin_limit` (default 6) and `wildcard_limit` (default 3). [Kcat assignment](../gecko4-kcat-assignment.md) describes the presets and the stages.

## Kcat source settings

A `[kcat_sources.<name>]` table holds the settings with which `updateKcatSources` (Python: `update_kcat_sources`) gathers the source file `data/kcats/<name>.tsv`. A preset sets some of these settings. A table in the file replaces the keys that it sets and keeps the other settings of the preset. Each source takes the keys in the table; [Gather the source files](kcat-sources.md#gather-the-source-files) gives their meaning and defaults.

| Table | Keys |
|---|---|
| `[kcat_sources.brenda]` | `aggregation` (`"max"` or `"median"`), `force_wildcard_level` |
| `[kcat_sources.ec_tree]` | `k` |
| `[kcat_sources.homologs]` | `k`, `min_identity`, `coverage` |
| `[kcat_sources.okp]` | `method` |
| `[kcat_sources.custom]`, `[kcat_sources.dlkcat]`, `[kcat_sources.okp_<method>]` | none |

A table of another source is an unknown key, and so is `[kcat_sources.okp_<x>]` unless `okp_<x>` is the file of an accepted OpenKineticsPredictor method (see [OpenKineticsPredictor](#openkineticspredictor)). An empty table of a known source is accepted. An entry for a known source that is not a table raises `<file>: kcat_sources.<name> must be a table`.

### BRENDA aggregation

`kcat.tsv` of the BRENDA release records a maximum and a median kcat per EC number, substrate and organism. `[kcat_sources.brenda] aggregation` selects which of the two is used, and no other key of the file selects it. `updateKcatSources` gathers `brenda.tsv` with this setting. `kcatsFromBrenda`, `fuzzyKcatMatching` and `loadBRENDAdata` (Python: `kcats_from_brenda` and `fuzzy_kcat_matching`), called without an aggregation, use the same setting as the kcat assignment configuration resolves it:

| Kcat assignment in the file | BRENDA aggregation |
|---|---|
| none, so the default preset `brenda_ec_tree` | `median` |
| preset `ec_tree_homologs`, `ec_tree_okp` or `gecko_median` | `median` |
| preset `gecko_classic` | `max` |
| preset `okp`, or stages, without `[kcat_sources.brenda] aggregation` | `max` |
| any, with `[kcat_sources.brenda] aggregation` | the value of `aggregation` |

An aggregation given in the call is used in place of the setting: `aggregation` of `kcatsFromBrenda` and `kcats_from_brenda`, `kcatAggregation` of `fuzzyKcatMatching` and `loadBRENDAdata`, and `aggregate` of `fuzzy_kcat_matching`. A value other than `max` or `median` raises `<file>: kcat_sources.brenda.aggregation must be max or median` when the file is read, and `aggregation must be max or median` when it is given in a call.

To use the BRENDA maximum with the default preset:

```toml
[kcat_sources.brenda]
aggregation = "max"
```

## Kcat tuning

The `[evotune]` section holds the hyperparameters of the CMA-ES kcat tuning described in [Tune kcats with evotune](evotune.md).

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `evotune.sigma0_log_default` | `evotune.sigma0logDefault` | `0.5` | Prior standard deviation of the natural log of the kcat, for the kcats that match no source group |
| `evotune.source_groups` | `evotune.kcatSources` | four groups (see [Source groups](#source-groups)) | Trust tiers: one table `[evotune.source_groups.<group>]` per group, with `sources` and `sigma0_log` |
| `evotune.rmse_threshold` | `evotune.rmseThreshold` | `0.2` | The search stops when the best distance to the measurements reaches this value |
| `evotune.max_generations` | `evotune.maxGenerations` | `150` | Maximum number of CMA-ES generations |
| `evotune.max_growth_weight` | `evotune.maxGrowthWeight` | `1.0` | Weight of the distance of the maximum-growth conditions against that of the flux conditions |
| `evotune.prior_penalty_weight` | `evotune.priorPenaltyWeight` | `0.03` | Weight of the prior term in the search objective |
| `evotune.tie_isozymes` | `evotune.tieIsozymes` | `true` | Give the isozyme copies of one reaction a single kcat |

### Source groups

A source group gives the kcats of some sources one prior width. Each group is a table with two required keys:

```toml
[evotune.source_groups.brenda]
sources = ["brenda"]
sigma0_log = 0.2

[evotune.source_groups.okp]
sources = ["okp_*"]
sigma0_log = 0.5
```

| Key | Value |
|---|---|
| `sources` | non-empty list of origins of `ec.source` (see [Provenance of a kcat](../gecko4-kcat-assignment.md#provenance-of-a-kcat)). An entry that ends in `*` is a prefix pattern on the origin: `okp_*` matches `okp_kinform_h` and `okp_unikp` |
| `sigma0_log` | positive number: the prior standard deviation of the natural log of the kcat. A smaller value is more trust |

The `sd` in an `ec.source` label such as `combined (sd=0.10, n=2)` is a standard deviation of the log10 of the kcat; a standard deviation of 0.1 in log10 is 0.23 in natural log.

A kcat is in the group of the first entry that matches it, in this order:

1. The entries without `*`, of all groups in the order of the file. An entry matches when it equals the origin of `ec.source` or the whole `ec.source`, without regard to case.
2. The patterns, the longest prefix first, and patterns of equal length in the order of the file. A pattern matches when the origin starts with its prefix, without regard to case.

A kcat is labelled with the name of its group, in `sourceGroup` of the screen and `groups` of the tuning result (Python `source_group` and `groups`). A kcat that matches no group gets `sigma0_log_default`. When more than 20 % of the tunable kcats match no group, the tuning warns:

```text
<n> of <m> tunable kcats match no evotune source group and get sigma0_log_default (<value>); origins: <origins>
```

The warning lists up to five origins, the most frequent first and in alphabetical order among equal counts. The GECKO identifier of the warning is `resolveTunableContext:unlabelled`; geckopy issues a `UserWarning`.

Without `[evotune.source_groups]` in the file, the groups are:

| Group | `sources` | `sigma0_log` |
|---|---|---|
| `custom` | `["custom"]` | 0.1 |
| `brenda` | `["brenda"]` | 0.2 |
| `ec_tree` | `["ec_tree"]` | 0.3 |
| `combined` | `["combined"]` | 0.4 |

Groups in the file replace all default groups.

## OpenKineticsPredictor

`[kcat_sources.okp] method` is the one setting that names the OpenKineticsPredictor (OKP) method; the default is `"KinForm-H"`. The `okp` source of the presets and stages stands for the file `okp_<method>.tsv` of this method, `updateKcatSources` gathers that file, and `kcatsFromOKP` (Python: `kcats_from_okp`) called without `method` uses it. The `[okp]` table names no method; it holds the options of each request to the OKP service:

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `okp.handle_long_sequences` | `okp.handleLongSequences` | `"truncate"` | Action of OpenKineticsPredictor on sequences that are too long |
| `okp.include_similarity_columns` | `okp.includeSimilarityColumns` | `true` | Return the similarity to the training data of the method |
| `okp.canonicalize_substrates` | `okp.canonicalizeSubstrates` | `true` | Canonicalise substrate SMILES before the prediction |

```toml
[kcat_sources.okp]
method = "UniKP"
```

`method` accepts the methods that predict from one enzyme and one substrate: CataPro, CatRange, DLKcat, EITLEM, KinForm-H, KinForm-L, OmniESI, OmniESI-O2DENet and UniKP. CatPred and TurNup read whole reactions, and `kcatsFromOKP` does not submit them. The file of a method is `okp_` followed by the method name in lower case, with each run of characters other than letters and digits replaced by `_`: `okp_kinform_h` for KinForm-H and `okp_omniesi_o2denet` for OmniESI-O2DENet. When the file is read, a name that is not in this list raises:

```text
Unknown OKP method <name> in [kcat_sources.okp] method; supported: <accepted methods>
```

A value that is not a string raises `kcat_sources.okp.method must be a string`.

The API key is no parameter. It is an argument of the functions, the environment variable `OKP_API_KEY` or the file `data/okpApiKey.txt`.

## MATLAB functions

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `matlab.make_model_anaerobic` | `matlab.makeModelAnaerobic` | none | Name of a MATLAB function that constrains the ecModel to anaerobic growth |
| `matlab.change_protein_biomass` | `matlab.changeProteinBiomass` | none | Name of a MATLAB function that changes the protein content of the biomass; it receives the ecModel and the protein content |
| `matlab.params` | the parameter name | none | Parameters that GECKO uses and geckopy does not use, kept under their MATLAB names. `kcatAggregation` and `evotune` are not allowed here, as they have keys of their own |

geckopy ignores the `[matlab]` section. The functions are searched on the MATLAB path, to which the `code` folder of the project is added.

A GECKO 3 adapter class sets the same parameters in MATLAB code; [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md#adapter-classes) describes how such a class is used and converted.

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| `<file>: unknown key <dotted.key> in model_adapter.toml` | the key is missing from the tables above, is misspelled, or belongs to no key list of its group, stage or kcat source table | Correct the key, or place a parameter that GECKO alone uses under `[matlab.params]` |
| `<file>: matlab.params.kcatAggregation is not allowed; set it in [kcat_sources.brenda] aggregation` (or `matlab.params.evotune`, `set it in [evotune]`) | `[matlab.params]` sets a parameter that has a key of its own | Move the setting to `[kcat_sources.brenda]` or `[evotune]` |
| `<file>: evotune.source_groups.<group> needs both sources and sigma0_log`, or `must be a table with sources and sigma0_log` | a group lacks one of the two keys, or is a single value in place of a table | Write the group as a table with `sources` and `sigma0_log` |
| `<file>: evotune.source_groups.<group>.sources must be a non-empty list of strings`, or `.sigma0_log must be a positive number` | `sources` is empty or not a list of strings; `sigma0_log` is zero, negative, not finite or not a number | Correct the value |
| `Unknown OKP method <name> in [kcat_sources.okp] method; supported: ...` | the method name is misspelled, or is CatPred or TurNup | Use the names of [OpenKineticsPredictor](#openkineticspredictor) |
| `gr_exp is not set in model_adapter.toml` | a function that needs a target growth rate got none, and the file does not set `gr_exp` | Set `gr_exp`, or give the growth rate in the call |
| Error about a preset and stages | `[kcat_assignment]` has both `preset` and `[[kcat_assignment.stage]]` | Keep one of the two |
| `No model_adapter.toml found in <folder>` | the folder given holds no `model_adapter.toml` | Give the folder that holds the file |

## See also

- [Project format 4](../gecko4-project-format.md), the sections of `model_adapter.toml`.
- [Kcat assignment](../gecko4-kcat-assignment.md), the presets and stages of `[kcat_assignment]`.
- [Build an ecModel](first-ecmodel.md), where the model adapter is created and populated.
- [Files in the data folder](data-folder-files.md), the other project-wide reference table.
