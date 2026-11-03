# Model adapter parameters

<!-- docs-site: concept-page -->

`model_adapter.toml` in the project folder holds the parameters of a GECKO 4 project. GECKO (MATLAB) and geckopy (Python) read the same file. The section overview is in [Project format 4](../gecko4-project-format.md). The tables give the parameters, their defaults and the MATLAB name of each parameter. The defaults are those of `src/model_adapter/adapterParameters.tsv` of GECKO, which geckopy uses as well.

## Reading the file

Paths in the file are relative to the project folder. A key that is left out gets the default of the tables. A key that the tables do not list is an error in both toolboxes; a parameter that GECKO alone uses goes under `[matlab.params]`. The project folder is the folder of the file, so `path` is no key.

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

## Model and protein pool

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `project_format` | `projectFormat` | none | Layout version of the project folder. `upgradeGECKOproject` and `geckopy upgrade` write 4 |
| `conv_gem` | `convGEM` | none (required in geckopy) | Path to the starting conventional GEM file, for example `models/yeast-GEM.yml` |
| `org_name` | `org_name` | none (required in geckopy) | Scientific name of the organism, used by `fuzzyKcatMatching` (Python: `fuzzy_kcat_matching`) and `kcatsFromBrenda` (`kcats_from_brenda`) |
| `sigma` | `sigma` | `0.5` | Average enzyme saturation factor |
| `p_tot` | `Ptot` | `0.5` | Total protein content in the cell [g protein/gDW] |
| `f` | `f` | `0.5` | Fraction of enzymes in the ecModel relative to all proteins (g enzyme/g protein). `calculateFfactor` (Python: `calculate_f_factor`) computes it from a proteomics data set |
| `gr_exp` | `gR_exp` | `0.41` | Reference (experimentally observed) maximum growth rate in h^-1, the default tuning target in [Growth-rate tuning](growth-rate-tuning.md#sensitivity-tuning-of-kcat-values) |
| `c_source` | `c_source` | `""` | Identifier of the exchange reaction of glucose or of another preferred carbon source |
| `bio_rxn` | `bioRxn` | `""` | Identifier of the biomass or growth pseudoreaction, whose flux is the growth rate in h^-1 |
| `enzyme_comp` | `enzyme_comp` | `"cytoplasm"` | Name of the compartment of the added protein pseudometabolites; must match one of the compartment names of the ecModel |

## Kcat aggregation

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `kcat_aggregate_brenda` | `kcatAggregation` | `"max"` | BRENDA aggregate (`max` or `median`) that direct calls of `fuzzyKcatMatching`, `loadBRENDAdata` and `kcatsFromBrenda` read per EC number, substrate and organism. `updateKcatSources` and `assignKcats` pass `aggregation` of `[kcat_sources.brenda]` instead, which the presets set (`median` for `brenda_ec_tree`, `ec_tree_homologs`, `ec_tree_okp` and `gecko_median`; `max` for `gecko_classic`), which overrides this key for a `brenda.tsv` gathered that way |
| `kcat_aggregate_candidates` | none | `"max"` | Used by geckopy. Aggregation of several candidate kcats of one reaction in `apply_kcat_list` when `criteria` is not given: `max`, `min`, `median` or `mean` |
| `kcat_aggregate_isozymes` | none | `"mean"` | Used by geckopy. Aggregation of the kcats of the isozymes in `fill_kcats_from_isozymes` when `aggregate` is not given: `max`, `median` or `mean` |

GECKO accepts the two geckopy keys in the file and does not use them. `getKcatAcrossIsozymes` uses the mean.

## Database identifiers

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `kegg.id` | `kegg.ID` | `"sce"` | Organism code in the KEGG database, from the [KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html) |
| `kegg.gene_id` | `kegg.geneID` | `"kegg"` | Field of the KEGG entry that matches the gene identifiers of the ecModel. `kegg` takes the KEGG entry identifier. Identifiers from the "Other DBs" section of the KEGG page, such as `NCBI-GeneID`, `UniProt` or `Ensembl` (for Human-GEM), are available for some organisms |
| `uniprot.type` | `uniprot.type` | `"taxonomy"` | Whether `uniprot.id` is a taxonomy identifier (`taxonomy`) or a proteome identifier (`proteome`) |
| `uniprot.id` | `uniprot.ID` | `"559292"` | Identifier of the UniProt data set (by taxonomy or proteome) with complete coverage of the genes of the ecModel |
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
| `kcat_sources.<name>` | `kcat_sources.<name>` | none | Settings of one source file, for example `aggregation` in `[kcat_sources.brenda]` and `methods` in `[kcat_sources.okp]`, the OKP methods of the source group `okp` |

A stage has the keys `action` (`select`, the default, or `combine`), `sources`, `criteria` (`max`, `min`, `median` or `mean`; default `max`), `top_origin_limit` (default 4), `bottom_origin_limit` (default 6) and `wildcard_limit` (default 3). [Kcat assignment](../gecko4-kcat-assignment.md) describes the presets and the stages.

## Kcat tuning

The `[evotune]` section holds the hyperparameters of the CMA-ES kcat tuning described in [Tuning against experimental data](tuning-against-experimental-data.md).

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `evotune.sigma0_log_default` | `evotune.sigma0logDefault` | `0.5` | Prior standard deviation (log) of the kcats whose source is in no group |
| `evotune.source_groups` | `evotune.kcatSources` | none | Trust tiers: a table `[evotune.source_groups.<group>]` per group with the `ec.source` values it covers as `sources`. With `match_okp = true`, a group also covers the method of `[okp] method` |
| `evotune.sigma0_log_source` | `evotune.sigma0logSource` | none | Prior standard deviation (log) per group; the keys are the group names of `evotune.source_groups` |
| `evotune.rmse_threshold` | `evotune.rmseThreshold` | `0.2` | The search stops when the best RMSE reaches this value |
| `evotune.max_generations` | `evotune.maxGenerations` | `150` | Maximum number of CMA-ES generations |
| `evotune.max_growth_weight` | `evotune.maxGrowthWeight` | `1.0` | Weight of the maximum-growth RMSE against the flux RMSE |
| `evotune.prior_penalty_weight` | `evotune.priorPenaltyWeight` | `0.03` | Weight of the prior term in the search objective |
| `evotune.tie_isozymes` | `evotune.tieIsozymes` | `true` | Give the isozyme copies of one reaction a single kcat |

When `[evotune]` has no `source_groups`, the groups are `dlkcat`, `brenda` and `custom`, each with the source of the same name, and `sigma0_log_source` is 0.4, 0.2 and 0.1.

## OpenKineticsPredictor

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `okp.method` | `okp.method` | `"CataPro"` | OpenKineticsPredictor method |
| `okp.handle_long_sequences` | `okp.handleLongSequences` | `"truncate"` | How OpenKineticsPredictor handles sequences that are too long |
| `okp.include_similarity_columns` | `okp.includeSimilarityColumns` | `true` | Return the similarity to the training data of the method |
| `okp.canonicalize_substrates` | `okp.canonicalizeSubstrates` | `true` | Canonicalise substrate SMILES before the prediction |

The API key is no parameter. It is an argument of the functions, the environment variable `OKP_API_KEY` or the file `data/okpApiKey.txt`.

## MATLAB functions

| TOML key | MATLAB parameter | Default | Description |
|---|---|---|---|
| `matlab.make_model_anaerobic` | `matlab.makeModelAnaerobic` | none | Name of a MATLAB function that constrains the ecModel to anaerobic growth |
| `matlab.change_protein_biomass` | `matlab.changeProteinBiomass` | none | Name of a MATLAB function that changes the protein content of the biomass; it receives the ecModel and the protein content |
| `matlab.params` | the parameter name | none | Parameters that GECKO uses and geckopy does not use, kept under their MATLAB names |

geckopy ignores the `[matlab]` section. The functions are searched on the MATLAB path, to which the `code` folder of the project is added.

## Adapter classes

A GECKO 3 adapter class keeps working. It sets `obj.params` with the MATLAB names of the tables above, and `ModelAdapterManager.setDefault` takes the path of its `.m` file. `convertAdapterToToml` writes the parameters of a class as `model_adapter.toml` and lists the methods that the class overrides and the file cannot carry. The option `'adapterFormat','class'` of `createGECKOproject` creates a project with a class.

A class that needs code beyond the file can read its parameters from the file in the constructor:

```matlab
obj.params = loadAdapterParams(fullfile(projectPath, 'model_adapter.toml'));
```

In geckopy, a subclass of `ModelAdapter` overrides `get_spontaneous_reactions`, `get_uniprot_compatible_genes`, `get_uniprot_ids_from_table`, `get_kegg_compatible_genes`, `get_brenda_db_folder` or `get_phyl_dist_path`. It is instantiated explicitly; `from_folder` does not discover it.

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| `Unknown key "<key>" in <full path of model_adapter.toml>.` (GECKO) or a validation error that names the key (geckopy) | the key is not in the tables above, or is misspelled | Correct the key, or place a parameter that GECKO alone uses under `[matlab.params]` |
| Error about a preset and stages | `[kcat_assignment]` has both `preset` and `[[kcat_assignment.stage]]` | Keep one of the two |
| `No model_adapter.toml found in <folder>` | the folder given holds no `model_adapter.toml` | Give the folder that holds the file |

## See also

- [Project format 4](../gecko4-project-format.md), the sections of `model_adapter.toml`.
- [Kcat assignment](../gecko4-kcat-assignment.md), the presets and stages of `[kcat_assignment]`.
- [Getting started](getting-started.md), where the model adapter is created and populated.
- [Files in the data folder](data-folder-files.md), the other project-wide reference table.
