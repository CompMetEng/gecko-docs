# Gathering kcats

An empty ecModel has the structure to carry enzyme constraints but no kcat values. Kcats are gathered from each source into a kcat source file in `data/kcats`: [BRENDA](https://www.brenda-enzymes.org/) by fuzzy matching, the EC tree, measured homologs, DLKcat and OpenKineticsPredictor. At the end, every source that the project uses has a source file that `assignKcats` can read.

Not every enzymatic reaction has a reported measurement. BRENDA kcats are matched to a reaction by EC number and by the substrates of the reaction. DLKcat and OpenKineticsPredictor predict a kcat from the enzyme sequence and the substrate structure, independent of the EC number, which covers organisms with few measurements and reactions without an EC number. [Kcat assignment](../gecko4-kcat-assignment.md) describes how the source files are combined into one kcat per reaction, and [Applying kcats](applying-kcats.md) the steps after that.

## Functions

| MATLAB | Python | Note |
|---|---|---|
| `getECfromGEM` / `getECfromDatabase` | `fill_eccodes_from_gem` / `fill_eccodes_from_database` | populate EC numbers |
| `kcatsFromBrenda` | `kcats_from_brenda` | match kcats from BRENDA by EC number, substrate and organism, and write `brenda.tsv` |
| `fuzzyKcatMatching` | `fuzzy_kcat_matching` | the BRENDA matching alone, without a source file |
| `kcatsFromECTree` | `kcats_from_ec_tree` | estimate kcats from the EC tree, and write `ec_tree.tsv` |
| `kcatsFromHomologs` | `kcats_from_homologs` | estimate kcats from measured homologs, and write `homologs.tsv` |
| `findMetSmiles` | `find_met_smiles` | annotate metabolites with SMILES for DLKcat and OpenKineticsPredictor |
| `kcatsFromDLKcat` | `kcats_from_dlkcat` | run or read DLKcat, and write `dlkcat.tsv` |
| `writeDLKcatInput` / `runDLKcat` / `readDLKcatOutput` | `write_dlkcat_input` / `run_dlkcat` / `read_dlkcat_output` | the steps of a DLKcat run |
| `kcatsFromOKP` | `kcats_from_okp` | submit or fetch an OpenKineticsPredictor job, and write `okp_<method>.tsv` |
| `submitOpenKineticsPredictor` / `fetchOpenKineticsPredictor` | `submit_open_kinetics_predictor` / `fetch_open_kinetics_predictor` | the steps of an OpenKineticsPredictor job |
| `saveKcatSource` / `loadKcatSource` | `save_kcat_source` / `load_kcat_source` | write a kcat list as a source file, and map a source file to the ecModel |
| `updateKcatSources` | `update_kcat_sources` | gather the sources that `model_adapter.toml` needs |
| `mergeKcats` | `merge_kcats` | merge kcat lists from multiple sources |

## Setup

The ecModel comes from [Building an empty ecModel](building-ec-model.md), and the project folder has a `model_adapter.toml` ([Project format 4](../gecko4-project-format.md)). The sources have these requirements:

| Source file | Needs |
|---|---|
| `brenda.tsv` | EC numbers; the BRENDA files and the KEGG phylogenetic distances |
| `ec_tree.tsv` | EC numbers; the BRENDA files |
| `homologs.tsv` | enzyme sequences (`ec.sequence`); the BRENDA files; DIAMOND |
| `dlkcat.tsv` | SMILES of the metabolites; Docker for a DLKcat run |
| `okp_<method>.tsv` | SMILES of the metabolites; an OpenKineticsPredictor API key |

GECKO does not ship BRENDA data. `fetchBrendaAsset` (Python: `fetch_brenda_asset`) downloads the files of the toolbox-assets release `brenda-2026.1-1` on first use, and a project uses its own files when it has the folder `data/brenda`. DIAMOND is the executable of RAVEN (`getDiamond`), which is downloaded when missing. Reactions that no source covers get custom kcats and the standard kcat, described in [Applying kcats](applying-kcats.md#provide-custom-kcat-values) and [Applying kcats](applying-kcats.md#assign-a-standard-kcat-value-optional).

## Kcat source files

Each `kcatsFrom*` function (Python: `kcats_from_*`) writes the kcats of one source to `data/kcats/<source>.tsv` and returns the same kcat list (`kcatList`, `pandas.DataFrame` in Python). The option `save` set to false skips the file, and `saveAs` (Python: `save_as`) sets another name. The option `ecRxns` (Python: `ec_rxns`) restricts the reactions, except for `kcatsFromHomologs`: MATLAB takes a logical vector over `ecModel.ec.rxns`, Python a list of reaction identifiers. With a subset and the default name, the file holds the reactions of the subset and no others.

The rows of a source file are keyed by the conventional reaction and the enzyme set. The index in `ecModel.ec.rxns` is not part of the key. A file stays valid when the ecModel is rebuilt, and applies to a full and a light ecModel. `saveKcatSource` writes a kcat list made in another way, for example one that `fuzzyKcatMatching` returned, and `loadKcatSource` maps a file back to the ecModel and reports the rows that fit no reaction. A file with `kind: curated` in its header, such as `custom.tsv`, is never overwritten.

`assignKcats` reads the files that `[kcat_assignment]` lists, so any combination of sources works. The hosted [OpenKineticsPredictor](https://predictor.openkinetics.org/) service offers several predictor methods and needs no Docker, which makes it the recommended alternative to a local DLKcat run. DLKcat runs locally in a Docker image.

## Assign EC numbers to reactions

BRENDA matching and the EC tree use EC numbers. EC numbers can come from the starting GEM's EC number annotation, if it has one (MATLAB: the `model.eccodes` field; Python: each reaction's `annotation["ec-code"]`), or be gathered from UniProt and KEGG annotations.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

If the starting GEM has manually curated EC numbers, populate `ecModel.ec.eccodes` with model-derived EC numbers first, then fill the rest from the database. `getECfromDatabase` overwrites entries in `ecModel.ec.eccodes`, so mark which entries are still empty before calling it:

```matlab
ecModel = getECfromGEM(ecModel);
noEC = cellfun(@isempty, ecModel.ec.eccodes);
ecModel = getECfromDatabase(ecModel, noEC);
```

If the starting GEM is not annotated with a `model.eccodes` field, does not contain standard EC numbers (four groups of digits separated by periods), or its EC annotations are not trusted, run `getECfromDatabase` alone:

```matlab
ecModel = getECfromDatabase(ecModel);
```

`applyECcodes` transfers EC numbers derived from the database back into the
`model.eccodes` fields, if desired.
:::
:::{tab-item} 🐍 Python
:sync: python

`fill_eccodes_from_database` rewrites every entry that `ec_rxns` selects, all reactions by default, so the reactions without an EC number are selected explicitly. The UniProt data `uniprot_db` is loaded with `load_uniprot_tsv`:

```python
from geckopy import fill_eccodes_from_database, fill_eccodes_from_gem

fill_eccodes_from_gem(ec_model)
no_ec = [
    rxn for rxn, ec in zip(ec_model.ec.rxns, ec_model.ec.eccodes) if not ec
]
fill_eccodes_from_database(ec_model, uniprot_db, ec_rxns=no_ec)
```

If the starting GEM's EC annotations are not trusted, skip `fill_eccodes_from_gem` and call `fill_eccodes_from_database(ec_model, uniprot_db)`. With the argument `kegg_db` (loaded with `load_kegg_tsv`), KEGG supplies the EC number of a reaction for which UniProt has no EC number or an incomplete one (ending in `-`). `copy_ec_to_gem` is the equivalent of `applyECcodes`, writing into each reaction's `annotation["ec-code"]` (cobrapy's convention) while MATLAB writes a top-level `model.eccodes` cell array.
:::
::::

:::{note} Difficulties finding EC numbers for the reactions
BRENDA matching and the EC tree require EC numbers. EC numbers can be entered manually in the model's EC annotation field, based on any species-specific information available, and loaded with the functions above. DLKcat and OpenKineticsPredictor do not require EC numbers, so a predictor can be the sole kcat source when EC numbers are hard to find.
:::

## Gather kcats from BRENDA

Fuzzy matching queries BRENDA by EC number, substrate and organism. It is called fuzzy because it allows kcats from other organisms or substrates, and wildcards in the EC number, when no exact match exists.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
kcatList_fuzzy = kcatsFromBrenda(ecModel);
```

The BRENDA files come from `fetchBrendaAsset`, and the KEGG phylogenetic distances from RAVEN.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcats_from_brenda

kcat_list_fuzzy = kcats_from_brenda(ec_model)
```

`kcats_from_brenda` loads the BRENDA files from `adapter.get_brenda_db_folder()` and the KEGG phylogenetic distances from `data/PhylDist.mat`, which is downloaded when missing. Both can be passed as the arguments `brenda` (loaded with `load_brenda_data`) and `phyl_dist` (loaded with `load_phyl_dist`).
:::
::::

The option `aggregation` (`'max'` or `'median'`) selects the BRENDA value per EC number, substrate and organism; the default is `kcat_aggregate_brenda` of `model_adapter.toml`, or `'max'`. The option `forceWClvl` (Python: `force_wildcard_level`) replaces that number of EC levels, from the right, by a wildcard in every EC number. `fuzzyKcatMatching` (Python: `fuzzy_kcat_matching`, which takes the loaded `brenda` and `phyl_dist`) returns the same list without writing a file.

Each BRENDA kcat is divided by the coefficient of the substrate that it was measured on, so a reaction that consumes two molecules of that substrate gets a kcat per molecule of the substrate ([GECKO 3 to GECKO 4](../gecko3-to-gecko4.md) describes the change from GECKO 3).

The kcat list documents which kcat was assigned to each reaction and how precise the match is: the number of EC wildcards used, and whether the match agreed on substrate and organism. A full match often does not exist, even for model organisms such as *S. cerevisiae*, and a partial organism or substrate match is returned. For each EC number, the levels of organism and substrate are tried in the order of the origin values 1, 2, 3, 5, 4 and 6 (see the example output below). When no level matches, the rightmost EC level is replaced by a wildcard and the levels are tried again. EC 2.4.2.3 (uridine phosphorylase), for example, becomes 2.4.2.- (pentosyltransferase). With a wildcard, the levels that require a matching substrate (origin 1 and 2) are skipped, because the last digits of the EC number carry the substrate specificity. When a reaction has several EC numbers, the match with the fewest wildcards and the earliest level is selected, and among those the highest kcat.

:::{note} Example output
In the `full_ecModel` tutorial, the fuzzy `kcatList` documents, per reaction: the substrates and EC numbers matched against BRENDA, the proposed kcat, `wildcardLvl` (Python: `wildcard_level`; 0: `w.x.y.z`, 1: `w.x.y.-`, 2: `w.x.-.-`, 3:
`w.-.-.-`, 4: `-.-.-.-`), and `origin`, the specificity level of the match reached (1:
correct organism and substrate; 2: closest related organism, correct substrate; 3: correct organism, any substrate; 4: closest related organism, any substrate; 5: correct organism, specific activity; 6: closest related organism, specific activity).
:::

## Estimate kcats from the EC tree

The EC tree takes the median of all wild-type BRENDA measurements of the EC number, from any organism and substrate, and shrinks it towards the median of the 3-digit and 2-digit EC classes with the weight `n/(n+k)` for `n` measurements. A reaction with several EC numbers uses the one with the most measurements. Reactions without an EC number, or with EC classes without measurements, get no value.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
kcatList_ecTree = kcatsFromECTree(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcats_from_ec_tree

kcat_list_ec_tree = kcats_from_ec_tree(ec_model)
```
:::
::::

The option `k` sets the shrinkage constant (default 5). The `detail` column of the kcat list holds the number of measurements of the EC number (`n`) and the deepest EC level with measurements (`depth`).

## Estimate kcats from measured homologs

For each reaction, enzyme and substrate, DIAMOND searches the enzyme sequence against the sequences of the BRENDA measurements (at least 40 % identity and 80 % coverage of both sequences). The estimate is the mean of the `k` most identical homologs that were measured on the same substrate, weighted by identity; with homologs of at least 95 % identity, it is the median of those alone. For an enzyme complex, the estimate is the median over the subunits.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
kcatList_homologs = kcatsFromHomologs(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcats_from_homologs

kcat_list_homologs = kcats_from_homologs(ec_model)
```
:::
::::

The options `k` (default 10), `minIdentity` (Python: `min_identity`, default 0.4), `coverage` (default 0.8) and `threads` set the number of homologs and the DIAMOND thresholds. Model metabolites are matched to the substrates of the measurements through their ChEBI annotations, then their MetaNetX annotations, then their names. Reactions without a homolog that was measured on one of their substrates get no value.

## Gather SMILES annotations

DLKcat and OpenKineticsPredictor take the substrates as SMILES. Starting GEMs rarely include SMILES annotation, so this queries PubChem, creating `data/smilesDB.tsv`, or fills that file manually.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, noSMILES] = findMetSmiles(ecModel);
```

`findMetSmiles` reports the percentage of
unique metabolites assigned a SMILES annotation. If it is below 100 %, as is almost always the case, inspect the `noSMILES` list of metabolite names. In some models the metabolite name is suffixed with the metabolite formula, which prevents matching with PubChem; curating `ecModel.metNames` resolves such issues.

MATLAB prints the progress and result:

```
Check for local SMILES database... done.
SMILES could be found for 64% of the unique metabolite names.
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import find_met_smiles

find_met_smiles(ec_model, cache_path=params.path / "data" / "smilesDB.tsv")
```

`find_met_smiles` mutates `ec_model` in place and reads and writes through the
`cache_path` TSV; an existing cache, as shipped with the tutorial, means no
PubChem network access is needed. Unmatched metabolites are logged rather than returned as a `noSMILES` list: the number of unique metabolite names with a SMILES and the number without are logged at INFO level, and each name without a SMILES at DEBUG level. As in MATLAB, curate metabolite names
(`metabolite.name`) if a formula suffix or similar naming issue prevents
matching.
:::
::::

:::{note} Example output
In the `full_ecModel` tutorial, a SMILES annotation is found for 64 % of the unique metabolite names, after checking the local SMILES database and querying PubChem for the rest.
:::

## Predict kcats with DLKcat

DLKcat predicts a kcat from enzyme sequence information and substrate structural information in SMILES format. `kcatsFromDLKcat` with the option `run` writes the DLKcat input, runs DLKcat in a Docker image and keeps the predictions as `dlkcat.tsv`. The run downloads and starts the Docker image `ghcr.io/sysbiochalmers/dlkcat-gecko:0.1` automatically, so Docker must be installed and running. A run records the number of reactions it covered in `data/DLKcat_run.txt`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
kcatList_DLKcat = kcatsFromDLKcat(ecModel, 'run', true);
```

Without `'run', true`, `kcatsFromDLKcat` reads the output of an earlier run from `data/DLKcat.tsv`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcats_from_dlkcat

kcat_list_dlkcat = kcats_from_dlkcat(ec_model, run=True)
```

Without `run=True`, `kcats_from_dlkcat` reads the output of an earlier run from `data/DLKcat.tsv` and raises `FileNotFoundError` when the file is missing.
:::
::::

The kcat list is similar in shape to the BRENDA one, but has no EC numbers, wildcard levels or origin values, and instead includes the `genes` of each reaction. In MATLAB the fields `eccodes`, `wildcardLvl` and `origin` are absent; in Python the columns `eccode`, `wildcard_level` and `origin` are present but empty.

### Write the DLKcat input file

`kcatsFromDLKcat` with `'run', true` replaces `data/DLKcat.tsv`. The input file can also be written, run and read in separate steps. Currency metabolites that occur in pairs (for example ATP versus ADP, NADH versus NAD) and a selection of small molecules (for example Fe2+) are excluded, unless a reaction has no other reactants after removing them, as for ATP synthase. Nonexhaustive exclusion lists ship with the toolbox as `DLKcatCurrencyMets.tsv` and `DLKcatIgnoreMets.tsv` (MATLAB: in `GECKO/databases`; Python: inside the `geckopy.data` package); an ecModel-specific override can be placed under `data/` in the adapter folder with the same filenames. The lists apply to the OpenKineticsPredictor input and to the substrates of the homolog search as well.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
writeDLKcatInput(ecModel);
```

`writeDLKcatInput` raises an error when `data/DLKcat.tsv` exists; the option `'overwrite', true` replaces the file and discards the predictions that it holds.

`DLKcat.tsv` is specific to either the full or the light version of the ecModel, because
it carries reaction identifiers from `ec.rxns` needed when loading the predicted values back into the ecModel. Build separate `DLKcat.tsv` files for the two ecModel versions. The source file `dlkcat.tsv` is keyed by the conventional reaction and applies to both.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import load_dlkcat_ignore_lists, write_dlkcat_input

ignore_lists = load_dlkcat_ignore_lists(params.path / "data")
write_dlkcat_input(
    ec_model, params.path / "data" / "DLKcat.tsv", ignore_lists,
)
```

`load_dlkcat_ignore_lists` reads the currency-metabolite and small-molecule
exclusion lists (`DLKcatCurrencyMets.tsv`/`DLKcatIgnoreMets.tsv`, or their project-specific overrides under `data/`) that MATLAB's `writeDLKcatInput` reads implicitly. `write_dlkcat_input` raises `FileExistsError` when the file exists; `overwrite=True` replaces it. The same full-vs-light `DLKcat.tsv` caveat applies: the file encodes `ec_model.ec.rxns` identifiers, so a full-model file cannot be reused for a light model or the reverse. The source file `dlkcat.tsv` is keyed by the conventional reaction and applies to both.
:::
::::

### Run DLKcat and load its output

No other input is given, because the function assumes the input file is at
`data/DLKcat.tsv`:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
runDLKcat();
kcatList_DLKcat = readDLKcatOutput(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import read_dlkcat_output, run_dlkcat

run_dlkcat(params.path / "data" / "DLKcat.tsv")
kcat_list_dlkcat = read_dlkcat_output(
    ec_model, params.path / "data" / "DLKcat.tsv",
)
```
:::
::::

These steps do not write `data/kcats/dlkcat.tsv`. `kcatsFromDLKcat(ecModel)` without `'run', true` reads `data/DLKcat.tsv` and writes the source file. `saveKcatSource(ecModel, kcatList_DLKcat, 'dlkcat')` (Python: `save_kcat_source(ec_model, kcat_list_dlkcat, "dlkcat")`) writes the list that `readDLKcatOutput` returned.

## Predict kcats with OpenKineticsPredictor

OpenKineticsPredictor (OKP) shares its input with DLKcat: protein sequences and single-substrate SMILES, gathered in the section on SMILES annotations. It needs no Docker. The method is set by the option `method` or, without it, by `[okp] method` of `model_adapter.toml` (default CataPro). The methods are CataPro, CatPred, CatRange, DLKcat, EITLEM, KinForm-H, KinForm-L, OmniESI, OmniESI-O2DENet, TurNup and UniKP. `kcatsFromOKP` submits enzyme-substrate pairs and raises an error for CatPred and TurNup, which read whole reactions.

:::{warning} The API key is a secret; never put it in the model adapter
OKP requires a personal Bearer API key (looks like `ak_...`). Get one free, no registration required, at [predictor.openkinetics.org/api-docs](https://predictor.openkinetics.org/api-docs) (the "API key generator" section; the key is shown once, and can be revoked and regenerated from the same page). Keys are tied to the requesting IP and carry a daily prediction quota that resets at midnight UTC.

Because the model adapter is shared and committed to version control, the key does not belong there. Both languages resolve it the same way, checked in this order: an explicit function argument; the
`OKP_API_KEY` environment variable; or a plain-text `data/okpApiKey.txt`
file in the adapter folder (a filename already git-ignored by GECKO).
:::

OKP is a web service with a job queue. `kcatsFromOKP` submits a job when the method has none, and fetches the result of the job on a later call. The file `okp_<method>.tsv` is written once the job is done.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
kcatsFromOKP(ecModel, 'method', 'CataPro');
[kcatList_OKP, done] = kcatsFromOKP(ecModel, 'method', 'CataPro', 'wait', true);
```

The first call submits the job. The second call waits for the result with `'wait', true`; without it, the call reports the status of the job and returns `done` as false, and `kcatList_OKP` is empty.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcats_from_okp

kcats_from_okp(ec_model, method="CataPro")
kcat_list_okp, done = kcats_from_okp(ec_model, method="CataPro", wait=True)
```

The first call submits the job. The second call waits for the result with `wait=True`, polling every 30 seconds; without it, the call returns `(None, False)` while the job runs.
:::
::::

Each method keeps its job in `data/OKP_job_<method>.txt` and its result in `data/OKP_output_<method>.csv`, so the jobs of several methods can run at the same time. The option `resubmit` submits a new job and removes the earlier result, and `useStored` (Python: `use_stored`) reads the stored result of the current job without contacting OKP. The `detail` column of the source file holds the similarity of the enzyme to the training sequences of the method.

`submitOpenKineticsPredictor` and `fetchOpenKineticsPredictor` are the steps that `kcatsFromOKP` calls. They write the request to `data/OKP.csv` and the job identifier to `data/OKP_job.txt`, store the result in `data/OKP_output.csv`, and do not write a source file. `fetchOpenKineticsPredictor` returns `[done, kcatList]`; with `'wait', true` (Python: `wait=True`) it polls every `pollInterval` seconds (Python: `poll_interval`, default 30; `timeout`, default one hour).

## Gather all configured sources

`updateKcatSources` gathers the source files that `[kcat_assignment]` of `model_adapter.toml` uses and that are missing or outdated, with the functions above. A file is outdated when its header records other settings than `[kcat_sources.<name>]` asks for, or for `brenda` and `ec_tree` another BRENDA release than the files in use. `custom.tsv` is left as it is. The function checks Docker and the OKP API key first.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
report = updateKcatSources(ecModel, 'dryRun', true);
report = updateKcatSources(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import update_kcat_sources

report = update_kcat_sources(ec_model, dry_run=True)
report = update_kcat_sources(ec_model)
```
:::
::::

`report` has one row per source with the columns `source`, `status` (current, gathered, pending, outdated, missing, failed or skipped) and `note`. An OKP source is pending while its job runs, and a later call fetches the result.

## Merge kcat lists

`assignKcats` (Python: `assign_kcats`) reads the source files, merges them by the stages of the preset and writes the result to the ecModel. `mergeKcats` (Python: `merge_kcats`) merges kcat lists that are in memory, for example those returned in the sections above, by a priority order that the caller gives. It keeps the highest-priority source for each reaction. The same call works with `kcatList_OKP` / `kcat_list_okp` in place of the DLKcat list, since the function merges by structure:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
kcatList_merged = mergeKcats({kcatList_fuzzy, kcatList_DLKcat}, ...
    {'database_top', 'dlkcat', 'database_bottom'});
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import merge_kcats

kcat_list_merged = merge_kcats(
    kcat_list_fuzzy, kcat_list_dlkcat,
    source_priority=["database_top", "dlkcat", "database_bottom"],
)
```
:::
::::

`mergeKcats` accepts any number of kcat lists, each assigned an explicit priority in `sourcePriority` (Python: `source_priority`). Sources that the priority does not list are dropped. Three reserved tier tokens rank BRENDA rows, and the position in the priority order sets the rank:

| Token | Rows |
|---|---|
| `database_exact` | an exact experimental measurement without fuzzy metadata, which OpenKineticsPredictor can return directly |
| `database_top` | fuzzy BRENDA matches without EC wildcard and with an origin up to `topOriginLimit` (Python: `top_origin_limit`, default 4) |
| `database_bottom` | weaker fuzzy matches: origin up to `bottomOriginLimit` (default 6), and at most `wildcardLimit` (default 3) EC wildcards |

Any other token (`'dlkcat'`, `'catapro'`, ...) matches the `source` value of a row, in lower case with other characters than letters and digits as `_`; a leading `okp_` of the source of an OpenKineticsPredictor row is dropped for the match. The default `topOriginLimit` of 4 ranks BRENDA matches from specific activities (origin 5 and 6) after the other sources, and the value 6 ranks them with the other `database_top` matches. All rows of the winning tier of a reaction are kept, and `assignKcatValues` (Python: `apply_kcat_list`) selects the value among them (default: the highest).

The merge does not query a wildcard EC number itself. The wildcard rows exist in the BRENDA kcat list, and `database_bottom` admits them for a reaction that no source of a higher tier covers. The merged list has the fields of the fuzzy-matching list and a `kcatSource` field (Python: the `source` column, which every list has) naming which source contributed each value.

`mergeDLKcatAndFuzzyKcats` (Python: `merge_dlkcat_and_fuzzy_kcats`) wraps `mergeKcats` with the priority `database_top`, `dlkcat`, `database_bottom` and prints a deprecation warning ([GECKO 3 to GECKO 4](../gecko3-to-gecko4.md)).

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| `kcatsFromBrenda` returns kcats for few reactions | many reactions have no EC number | Fill `ecModel.ec.eccodes` (section on EC numbers), or use a predictor |
| `Cannot find Docker` in `runDLKcat` | Docker is not installed or not running | Install and start Docker (start MATLAB from the command line when the launcher does not find Docker), or use OpenKineticsPredictor with the method DLKcat |
| `writeDLKcatInput` reports that `DLKcat.tsv` already exists | the file can hold predictions, so the function does not replace it | Delete the file, or set `'overwrite', true` |
| `kcatsFromOKP` returns `done` as false | the OpenKineticsPredictor job is still running | Call it again later, or with `'wait', true` |
| Error `kcatsFromOKP:method` | the method is CatPred or TurNup | Select another method |
| No OpenKineticsPredictor API key found | no key as argument, in `OKP_API_KEY` or in `data/okpApiKey.txt` | Generate a key and store it in one of the three places of the warning in the OpenKineticsPredictor section |
| Rows of a source file are not applied | the row fits no reaction, or part of an enzyme set | Read the report of `loadKcatSource` |
| `mergeKcats` drops a source | the source is not in the priority order | Add its token to `sourcePriority` |

## See also

- [Kcat assignment](../gecko4-kcat-assignment.md), how the source files become one kcat per reaction.
- [Applying kcats](applying-kcats.md), the next step: custom values, isozyme means, a standard fallback, and applying the resulting constraints to the ecModel.
- [Project format 4](../gecko4-project-format.md), the layout of `data/kcats` and the kcat source files.
- [Building an empty ecModel](building-ec-model.md), where the empty ecModel these kcats attach to comes from.
- [API reference](../api/index.md), every function in both toolboxes.
