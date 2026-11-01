# Files in the data folder

<!-- docs-site: concept-page -->

The `data` folder of a GECKO 4 project holds the input data of the reconstruction, the kcat source files and the files of the kcat predictors. GECKO (MATLAB) and geckopy (Python) read and write the same files, so a `data` folder made with one toolbox is used by the other. [Getting started](getting-started.md) describes the layout of a project and [Project format 4](../gecko4-project-format.md) the folders outside `data`.

## Databases and gene identifiers

| File | Content | Functions | Page |
|---|---|---|---|
| `uniprot.tsv` | UniProt data for the organism: protein identifier, gene identifier, EC number, MW and sequence. `loadDatabases` downloads it when it is missing | `loadDatabases` (Python: `geckopy uniprot-download`) writes; `makeEcModel`, `getStandardKcat` and `calculateFfactor` read | [Getting started](getting-started.md), [Building an empty ecModel](building-ec-model.md) |
| `kegg.tsv` | KEGG data for the organism: UniProt protein ID, gene, KEGG gene ID, EC number, MW, pathway and sequence. `loadDatabases` downloads it when it is missing | `loadDatabases` (Python: `geckopy kegg-download`) writes; `makeEcModel` (`make_ec_model`) reads | [Getting started](getting-started.md), [Gathering kcats](gathering-kcats.md) |
| `uniprotConversion.tsv` | Conversion table for models whose gene identifiers match no UniProt field. A header row, then the gene identifier of the model and the UniProt identifier. A gene that is not listed keeps its identifier. Written by the user | `ModelAdapter.getUniprotIDsFromTable` (Python: `get_uniprot_ids_from_table`) | [Getting started](getting-started.md) |
| `pseudoRxns.tsv` | Optional. Reaction identifiers in the first column and reaction names, for reference, in the second. These reactions lose their gene association in `makeEcModel` (`make_ec_model`) and receive no standard kcat in `getStandardKcat` (`assign_standard_kcat`). Written by the user | `makeEcModel`, `getStandardKcat` | [Building an empty ecModel](building-ec-model.md), [Applying kcats](applying-kcats.md) |
| `ComplexPortal.json` | Enzyme complex information from the Complex Portal | `getComplexData` (Python: `get_complex_data`) writes; `applyComplexData` (`apply_complex_data`) reads | [Building an empty ecModel](building-ec-model.md) |
| `smilesDB.tsv` | SMILES for the metabolites of the ecModel, a cache of the PubChem queries | `findMetSmiles` (Python: `find_met_smiles`) | [Gathering kcats](gathering-kcats.md) |

## Kcat source files and BRENDA data

| Path | Content | Functions | Page |
|---|---|---|---|
| `kcats/<source>.tsv` | One kcat source file per source: `custom`, `brenda`, `ec_tree`, `homologs`, `dlkcat` and `okp_<method>`. The format is described in [Kcat source files](../gecko4-project-format.md#kcat-source-files) | `kcatsFromBrenda`, `kcatsFromECTree`, `kcatsFromHomologs`, `kcatsFromDLKcat` and `kcatsFromOKP` write; `loadKcatSource` and `collectKcats` read. `custom.tsv` is written by hand or by `convertCustomKcats` (`convert_custom_kcats`) | [Gathering kcats](gathering-kcats.md), [Applying kcats](applying-kcats.md) |
| `brenda/` | Optional. The BRENDA files of the project: `kcat.tsv`, `sa.tsv`, `mw.tsv`, `measurements.tsv` and the other files of the BRENDA release. Without the folder, the files of the toolbox-assets release are downloaded once | `ModelAdapter.getBrendaDBFolder` (Python: `get_brenda_db_folder`); `geckopy brenda-refresh` writes the folder, by default `data/brenda` of the current directory | [Gathering kcats](gathering-kcats.md) |
| `customKcats.tsv` | Curated kcats in the format of GECKO 3, with the columns `proteins`, `genes`, `gene_name`, `kcat`, `rxns`, `notes` and `stoicho`. `collectKcats` applies the file when a stage lists `custom` and `kcats/custom.tsv` does not exist | `applyCustomKcats` (Python: `apply_custom_kcats`) reads; `convertCustomKcats` (`convert_custom_kcats`) converts | [Applying kcats](applying-kcats.md) |
| `PhylDist.mat` | KEGG phylogenetic distances, which geckopy uses to match kcats of other organisms. Downloaded when it is missing. GECKO reads the corresponding file of RAVEN | `kcats_from_brenda` | [Gathering kcats](gathering-kcats.md) |

## Predictor files

| File | Content | Functions | Page |
|---|---|---|---|
| `DLKcat.tsv` | Input of DLKcat and, after a run, its output | `writeDLKcatInput` (Python: `write_dlkcat_input`) and `runDLKcat` write; `kcatsFromDLKcat` and `readDLKcatOutput` read | [Gathering kcats](gathering-kcats.md) |
| `DLKcat_run.txt` | The number of reactions that the last DLKcat run covered, when it covered a subset of the reactions | `kcatsFromDLKcat` (Python: `kcats_from_dlkcat`) | [Gathering kcats](gathering-kcats.md) |
| `DLKcatIgnoreMets.tsv`, `DLKcatCurrencyMets.tsv` | Optional project copies of the lists of metabolites that are left out of the DLKcat and OKP input: names with SMILES, and pairs of currency metabolites. Without them, the files of the toolbox are used | `writeDLKcatInput`, `writeOpenKineticsPredictorInput` | [Gathering kcats](gathering-kcats.md) |
| `OKP.csv` | Input of an OpenKineticsPredictor job | `writeOpenKineticsPredictorInput`, `submitOpenKineticsPredictor` | [Gathering kcats](gathering-kcats.md) |
| `OKP_job_<method>.txt`, `OKP_output_<method>.csv` | The job and the result of one OKP method | `kcatsFromOKP` (Python: `kcats_from_okp`) | [Gathering kcats](gathering-kcats.md) |
| `OKP_job.txt`, `OKP_output.csv` | The job and the result of a job that `submitOpenKineticsPredictor` and `fetchOpenKineticsPredictor` handle. `kcatsFromOKP` adopts them for its method when no job of that method exists | `submitOpenKineticsPredictor`, `fetchOpenKineticsPredictor` | [Gathering kcats](gathering-kcats.md) |
| `okpApiKey.txt` | The API key of OpenKineticsPredictor, an alternative to the argument `apiKey` and to the environment variable `OKP_API_KEY` | `submitOpenKineticsPredictor`, `fetchOpenKineticsPredictor` | [Gathering kcats](gathering-kcats.md) |

## Proteomics, flux data and tuning data

| File | Content | Functions | Page |
|---|---|---|---|
| `paxDB.tsv` | Protein abundance data from [PaxDB](https://pax-db.org) for the f factor (the mass fraction of proteins accounted for in the ecModel). Header lines start with `#`, followed by three tab-separated columns: an internal identifier, the gene and the abundance. Without the file, `calculateFfactor` returns 0.5 | `calculateFfactor` (Python: `load_pax_db`, `calculate_f_factor`) | [Applying kcats](applying-kcats.md) |
| `proteomics.tsv` | Measured protein levels (mg protein/gDCW) from one or more experiments: UniProt identifiers in the first column, protein levels from individual replicates in each subsequent column | `loadProtData` (Python: `load_prot_data`) | [Proteomics integration](proteomics-integration.md) |
| `fluxData.tsv` | Experimental growth rate, protein content and carbon-source uptake, that constrain the ecModel during proteomics integration and in flux-variability comparisons. Exchange fluxes in mmol/gDCWh; uptake negative, excretion positive. Not required for the initial reconstruction | `loadFluxData` (Python: `load_flux_data`), `constrainFluxData` | [Proteomics integration](proteomics-integration.md), [Simulation and analysis](simulation-and-analysis.md) |
| `evotuneFluxData.tsv`, `evotuneMaxGrowth.tsv`, `evotuneZeroExch.tsv` | Optional data of the kcat tuning with CMA-ES: flux data, maximum growth rates and exchange reactions with zero flux | `loadEvotuneData` | [Tuning against experimental data](tuning-against-experimental-data.md) |

## Spontaneous reactions

The file that `[spontaneous] file` in `model_adapter.toml` names is a TSV with a header row. It lists reaction identifiers in the first column and, optionally, a second column in which `1` or `true` marks the spontaneous reactions. The path is relative to the project folder and the file name is free. See [Model adapter parameters](model-adapter-parameters.md#spontaneous-reactions).

## See also

- [Getting started](getting-started.md), where a project's `data` folder is created.
- [Model adapter parameters](model-adapter-parameters.md), the parameters of `model_adapter.toml`.
- [Project format 4](../gecko4-project-format.md), the folder layout of a GECKO 4 project.
