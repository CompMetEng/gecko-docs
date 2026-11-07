# Project format 4

<!-- docs-site: concept-page -->

A GECKO 4 project is a folder with a configuration file, input data, kcat source files, saved models and output. GECKO (MATLAB) and geckopy (Python) read the same folder. The configuration `project_format = 4` in `model_adapter.toml` marks the layout described here. [Upgrade a GECKO 3 project](gecko3-upgrade-project.md) converts a project made with GECKO 3.

## Folder layout

| Path | Content |
| --- | --- |
| `model_adapter.toml` | the parameters of the project, read by both toolboxes |
| `data/` | input data: proteomics, UniProt, ComplexPortal and the other files listed in [Files in the data folder](guide/data-folder-files.md) |
| `data/kcats/<source>.tsv` | one kcat source file per source: `custom`, `brenda`, `ec_tree`, `homologs`, `dlkcat`, `okp_<method>` |
| `data/brenda/` | optional BRENDA files of the project. Without this folder, `fetchBrendaAsset` supplies the files of the toolbox-assets release `brenda-2026.1-1` |
| `models/` | conventional GEM and saved ecModels |
| `output/` | results, including `<model id>_kcatDecisions.tsv` written by `assignKcats` |
| `legacy/<yyyy-mm-dd>/` | the files that `upgradeGECKOproject` replaced or converted |

`createGECKOproject` (MATLAB) and `geckopy init` (Python) create the project with `model_adapter.toml`. `createGECKOproject` writes an adapter class instead with the option `'adapterFormat','class'`.

## model_adapter.toml

The file holds the parameters that an adapter class sets in GECKO 3. Paths are relative to the project folder. Keys that are left out get the default listed, with their MATLAB names, in `src/model_adapter/adapterParameters.tsv` of GECKO. A key that `adapterParameters.tsv` does not list is an error in both toolboxes.

| Section | Content |
| --- | --- |
| top level | `project_format`, `conv_gem`, `org_name`, `sigma`, `p_tot`, `f`, `gr_exp`, `c_source`, `bio_rxn`, `enzyme_comp`, `kcat_aggregate_brenda`, and for geckopy `kcat_aggregate_candidates` and `kcat_aggregate_isozymes` |
| `[kegg]`, `[uniprot]`, `[complex]` | the organism and gene identifiers for the database downloads |
| `[spontaneous]` | reactions without an enzyme: a name fragment (`name_contains`) and a file with reaction identifiers (`file`) |
| `[evotune]` | the hyperparameters of the CMA-ES kcat tuning, with the source groups and the prior width per source |
| `[kcat_assignment]` | a preset or stages, and the options `isozymes` and `standard` (see [Kcat assignment](gecko4-kcat-assignment.md)) |
| `[kcat_sources.<name>]` | settings of one source, for example `aggregation` of `brenda` and `methods` of `okp` |
| `[okp]` | the OpenKineticsPredictor settings `method` (default `CataPro`), `handle_long_sequences`, `include_similarity_columns` and `canonicalize_substrates` |
| `[matlab]` | names of MATLAB functions for the anaerobic model and the protein content of the biomass. GECKO alone reads this section |
| `[matlab.params]` | parameters that GECKO uses and geckopy does not use |

`ModelAdapterManager.getAdapter` and `ModelAdapterManager.setDefault` take the project folder or the TOML file and return a `TomlAdapter`. A class that needs more code can subclass `TomlAdapter`. In geckopy, `ModelAdapter.from_folder` reads the folder. An adapter class of GECKO 3 keeps working, and `convertAdapterToToml` writes it as `model_adapter.toml` and lists the methods it cannot convert.

## Kcat source files

A kcat source file stores the kcats of one source. Each row is keyed by the conventional reaction and the enzyme set, which do not depend on the index in `model.ec.rxns`. A file stays valid when the ecModel is rebuilt and applies to full and light ecModels. GECKO and geckopy read and write the same files.

`loadKcatSource` maps a file to a model and reports the rows with an invalid kcat, the rows that fit no reaction, and the rows that match part of an enzyme set. `saveKcatSource` writes a kcat list as a source file. `getEcRxnKeys` returns the conventional reaction and the enzyme set of every reaction in `model.ec`.

| Source file | Function that writes it |
| --- | --- |
| `custom.tsv` | `convertCustomKcats`, or written by hand |
| `brenda.tsv` | `kcatsFromBrenda` |
| `ec_tree.tsv` | `kcatsFromECTree` |
| `homologs.tsv` | `kcatsFromHomologs` |
| `dlkcat.tsv` | `kcatsFromDLKcat` |
| `okp_<method>.tsv` | `kcatsFromOKP` |

## ecModel format

`saveEcModel` writes `gecko_format` (the ecModel format, 4) and `generator` (the release of the toolbox that wrote the file) to the `metaData` of the YAML file. The key `geckopy_version` of earlier geckopy releases is not written. A model without a description gets `Enzyme-constrained model of <id>`, and an existing description is kept.

`loadEcModel` upgrades an ecModel whose protein reactions run in the GECKO 3 direction in the loaded model and prints a warning. It raises an error for a `gecko_format` above 4. See [ecModel YAML format](guide/yaml-format.md) for the file structure.

## BRENDA data

GECKO does not include BRENDA data. `fetchBrendaAsset` downloads the files `kcat.tsv`, `sa.tsv`, `mw.tsv` and `measurements.tsv` of the toolbox-assets release `brenda-2026.1-1` (BRENDA 2026.1, CC BY 4.0) on first use, checks them against the checksums of the toolbox-assets manifest, and unpacks them into `databases/brenda-2026.1-1` in the GECKO folder. The release also holds `sequences.fasta`, `substrates.tsv` and `kcatCombineParams.tsv`. geckopy reads the same release (`fetch_brenda_asset`).

`kcat.tsv` and `sa.tsv` record a maximum and a median per EC number, substrate and organism. `kcat_aggregate_brenda = "max"` (default) or `"median"` selects the value for `fuzzyKcatMatching` and `loadBRENDAdata`, and `'kcatAggregation'` sets it for one call.

## See also

- [Upgrade a GECKO 3 project](gecko3-upgrade-project.md)
- [Kcat assignment](gecko4-kcat-assignment.md)
- [Model adapter parameters](guide/model-adapter-parameters.md)
