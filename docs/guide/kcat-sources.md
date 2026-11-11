# Choose the kcat sources

GECKO decides one kcat per enzymatic reaction from kcat source files in `data/kcats`, in the order that `[kcat_assignment]` of `model_adapter.toml` defines. At the end of this page, the project has a preset (or its own stages), the source files that the preset reads, optional custom kcats, and an ecModel with the assigned kcats applied as enzyme constraints.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `getECfromGEM` / `getECfromDatabase` | `fill_eccodes_from_gem` / `fill_eccodes_from_database` | fill the EC numbers of `ec.eccodes` |
| `findMetSmiles` | `find_met_smiles` | find the SMILES of the metabolites, for the prediction methods |
| `updateKcatSources` | `update_kcat_sources` | gather the source files that the preset reads and that are missing or outdated |
| `collectKcats` | `collect_kcats` | decide the kcats without changing the model |
| `assignKcats` | `assign_kcats` | decide the kcats and apply them as enzyme constraints |

## The choice

`[kcat_assignment] preset` selects one of six presets. Each preset is a list of stages, and a stage gives a kcat to the reactions that the earlier stages left without one. Every preset starts with the custom kcats of the project. In the table, "OKP" means the OpenKineticsPredictor methods of `[kcat_sources.okp] methods`; the default methods are CataPro, DLKcat, EITLEM, KinForm-H, KinForm-L, OmniESI, OmniESI-O2DENet and UniKP.

| Preset | Kcat of a reaction, in this order | Needs |
| --- | --- | --- |
| `brenda_ec_tree` (default) | BRENDA median of measurements of the organism on the substrate of the reaction; the EC tree; the OKP methods combined | EC numbers, BRENDA files, SMILES, OKP API key |
| `ec_tree_homologs` | BRENDA value of the organism; the EC tree and the measured homologs combined; the OKP methods combined | as `brenda_ec_tree`, plus DIAMOND |
| `ec_tree_okp` | BRENDA value of the organism; the EC tree, the homologs and the OKP methods combined; the OKP methods combined | as `ec_tree_homologs` |
| `okp` | the OKP methods combined | SMILES, OKP API key |
| `gecko_median` | BRENDA median of matches without EC wildcards (origin 1 to 4); DLKcat; the other BRENDA matches | EC numbers, BRENDA files, SMILES, OKP API key or `data/DLKcat.tsv` |
| `gecko_classic` | as `gecko_median` with the BRENDA maximum, and with the matches from specific activities (origin 5 and 6) before DLKcat | as `gecko_median` |

A "combined" value is the mean of the values of several sources in log10 units, each corrected for the bias of its source and weighted by the precision of the source for that reaction. `gecko_classic` is the order of the GECKO 3 tutorial. [Kcat assignment](../gecko4-kcat-assignment.md) describes each source, the BRENDA origin levels and the exact stages of each preset.

A project can list its own stages in `[[kcat_assignment.stage]]` tables in place of a preset. [Kcat assignment](../gecko4-kcat-assignment.md#presets) gives the TOML syntax and the stage options.

### Recommendation

The only measured comparison of the sources is this one, from [Kcat assignment](../gecko4-kcat-assignment.md#presets):

> Against measured kcats hidden from the search, the EC tree was closer than the BRENDA median at origin 2, at origin 4 and with EC wildcards, and as close at origin 1 and 3. The EC tree combined with the OKP methods was slightly closer than the EC tree, and the OKP methods combined were as close. In ecModels, values combined with predictions set high-turnover enzymes such as ATP synthase too low. The default therefore uses predictions where measurements give no value.

On that basis, start with `brenda_ec_tree`. The comparison does not include the homologs or DLKcat. Use `gecko_classic` to compare an ecModel with one built by GECKO 3.

## Prepare the inputs

The sources read different parts of the ecModel and of the project:

| Input | Read by | How to get it |
| --- | --- | --- |
| EC numbers in `ec.eccodes` | BRENDA, EC tree | from the GEM, or from UniProt and KEGG (code below) |
| SMILES of the metabolites | OKP methods, DLKcat | `findMetSmiles` (code below); substrates without a SMILES are left out of a prediction |
| enzyme sequences in `ec.sequence` | OKP methods, DLKcat, homologs | `makeEcModel` fills them from UniProt ([Choose the ecModel structure](ecmodel-structure.md)) |
| BRENDA files | BRENDA, EC tree, homologs, combined stages | `fetchBrendaAsset` downloads the release `brenda-2026.1-1` on first use. A project folder `data/brenda` takes precedence. MATLAB needs RAVEN 3 for the download |
| DIAMOND | homologs | the DIAMOND executable of RAVEN (MATLAB) or raven-toolbox (Python) |
| OpenKineticsPredictor API key | OKP methods, DLKcat without `data/DLKcat.tsv` | generate a key at [predictor.openkinetics.org](https://predictor.openkinetics.org/) |

GECKO looks for the API key in the environment variable `OKP_API_KEY` and then in the file `data/okpApiKey.txt` of the project. The key is never read from `model_adapter.toml`. Do not commit `data/okpApiKey.txt` to a public repository.

`getECfromDatabase` replaces the EC numbers of the reactions it is given, so the reactions that still have no EC number after `getECfromGEM` are selected:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = getECfromGEM(ecModel);
noEC = cellfun(@isempty, ecModel.ec.eccodes);
ecModel = getECfromDatabase(ecModel, noEC);
[ecModel, noSMILES] = findMetSmiles(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fill_eccodes_from_database, fill_eccodes_from_gem, find_met_smiles, load_uniprot_tsv

fill_eccodes_from_gem(ec_model)
no_ec = [rxn for rxn, ec in zip(ec_model.ec.rxns, ec_model.ec.eccodes) if not ec]
uniprot_db = load_uniprot_tsv(ec_model.adapter.params.path / "data" / "uniprot.tsv")
fill_eccodes_from_database(ec_model, uniprot_db, ec_rxns=no_ec)
find_met_smiles(ec_model)
```
:::
::::

`findMetSmiles` queries PubChem by metabolite name and keeps the results in `data/smilesDB.tsv`. A metabolite name that PubChem does not find gets no SMILES; correct the name in the model or add the SMILES to `data/smilesDB.tsv`.

## Gather the source files

`updateKcatSources` lists the source files that the preset reads and gathers each file that is missing or outdated. A file is outdated when the settings in its header differ from `[kcat_sources.<name>]`, or when it was made from another BRENDA release than the BRENDA files in use. `custom.tsv` is never gathered or changed. The option `dryRun` reports the status of each file without gathering.

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

`report` has one row per source file, with the columns `source`, `status` and `note`. The status is `current`, `gathered`, `pending`, `outdated`, `missing`, `failed` or `skipped`. OpenKineticsPredictor is a web service with a job queue: the first call submits one job per method and reports the source as `pending`, and a later call fetches the result and writes the file. Call `updateKcatSources` again until no source is `pending`. A source that is `failed` has the reason in `note`, for example a missing API key.

The source `dlkcat` (presets `gecko_median` and `gecko_classic`) reads `data/DLKcat.tsv` when the file exists. Without it, `dlkcat` is predicted with the DLKcat method of OpenKineticsPredictor.

:::{admonition} DLKcat in Docker
:class: note

DLKcat can also run on the local computer, in the Docker image `ghcr.io/sysbiochalmers/dlkcat-gecko:0.1`. This is the older method and needs Docker installed and running. `kcatsFromDLKcat(ecModel, 'via', 'docker')` (Python: `kcats_from_dlkcat(ec_model, via="docker")`) runs it and writes `data/kcats/dlkcat.tsv`; `updateKcatSources` then finds the file current.
:::

## Compare presets before applying

`collectKcats` makes the same decisions as `assignKcats` and does not change the model. It writes the decisions to `output/<model id>_kcatDecisions.tsv` unless `writeReport` (Python: `write_report`) is false. The file has one row per reaction of `ec.rxns` with these columns (Python names in parentheses):

| Column | Content |
| --- | --- |
| `ecRxn` (`ec_rxn`) | the reaction of `ec.rxns` |
| `stage` | the number of the stage that gave the kcat, `custom`, `isozymes` or `standard`; empty when the reaction has no kcat |
| `source` | the source as written to `ec.source` |
| `kcat` | the kcat in s^-1 |
| `candidates` | the number of values that the deciding source had for the reaction, or the number of sources combined |
| `spreadLog10` (`spread_log10`) | the range of these values in log10 units |
| `sdLog10` (`sd_log10`) | the uncertainty of a combined value in log10 units |

To compare two presets, change the preset of a copy of the adapter, gather its sources, and collect the decisions of both:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
adapter = ModelAdapterManager.getDefault();
other = adapter;
other.params.kcat_assignment.preset = 'ec_tree_okp';
updateKcatSources(ecModel, 'modelAdapter', other);
a = collectKcats(ecModel, 'writeReport', false);
b = collectKcats(ecModel, 'modelAdapter', other, 'writeReport', false);
groupcounts(a, 'stage')
groupcounts(b, 'stage')
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import collect_kcats, update_kcat_sources

settings = ec_model.adapter.params.kcat_assignment
a, _, _ = collect_kcats(ec_model, write_report=False)
default_preset = settings.preset
settings.preset = "ec_tree_okp"
update_kcat_sources(ec_model)
b, _, _ = collect_kcats(ec_model, write_report=False)
settings.preset = default_preset
print(a["stage"].value_counts())
print(b["stage"].value_counts())
```
:::
::::

The MATLAB adapter is a value object, so `other` is a copy and the default adapter keeps its preset. In Python, the preset is changed on the adapter of the model and set back afterwards. To keep the other preset, write it in `model_adapter.toml`.

## Assign the kcats

`assignKcats` decides the kcats, writes `ec.kcat` and `ec.source`, applies the enzyme constraints and writes the decisions file. The kcats that the model had before are replaced.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, decisions, report] = assignKcats(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import assign_kcats

decisions, report = assign_kcats(ec_model)  # changes ec_model in place
```
:::
::::

`report` lists the source files that a stage names and that do not exist (`missing`), and per source file the rows that were not applied. A missing source file is left out with a message, and the other stages still give kcats.

After the stages, two settings of `[kcat_assignment]` fill the reactions that are still without a kcat:

- `isozymes` (default true): in a full ecModel, a reaction without a kcat gets the mean kcat of its isozymes. A light ecModel uses the most efficient isozyme and skips this step.
- `standard` (default true): the remaining reactions get the standard kcat, which is the median kcat of the subsystem of the reaction when the subsystem has at least 10 reactions with a kcat, and the median of all kcats otherwise. Reactions without a gene association get the pseudo-enzyme `prot_standard`, with the median molecular weight of the proteins in `data/uniprot.tsv`. Exchange, transport, spontaneous and pseudo-reactions get no standard kcat; list other reactions to leave out in `data/pseudoRxns.tsv` ([Files in the data folder](data-folder-files.md)).

## Add custom kcats

`data/kcats/custom.tsv` holds the kcats that the project curates. Every preset reads it in its first stage, so a custom kcat is used before all other sources. [Set custom kcats](custom-kcats.md) describes the file, the conversion of `data/customKcats.tsv` of a GECKO 3 project, and how to change a kcat by hand.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| OKP sources stay `pending` | the OpenKineticsPredictor jobs are still running | Call `updateKcatSources` again later |
| OKP sources are `failed` with `No OpenKineticsPredictor API key found` | no key in `OKP_API_KEY` or in `data/okpApiKey.txt` | Generate a key and store it in one of the two places |
| `No kcat source file <file>; it is left out` | a stage names a source that has no file in `data/kcats` | Run `updateKcatSources`, or remove the source from the stages |
| BRENDA and the EC tree give kcats for few reactions | many reactions have no EC number | Fill `ec.eccodes` (section [Prepare the inputs](#prepare-the-inputs)) |
| Few reactions get a predicted kcat | many metabolites have no SMILES | Read `noSMILES` of `findMetSmiles` (Python: the log of `find_met_smiles`) and correct the metabolite names or `data/smilesDB.tsv` |
| Error `kcatAssignment:config` (Python: a validation error of the adapter) | an unknown preset, a preset and stages together, or a stage with a wrong option | Correct `[kcat_assignment]` |
| Kcats set by hand are gone | `assignKcats` replaced them | Write them to `data/kcats/custom.tsv` ([Set custom kcats](custom-kcats.md)) |

## See also

- [Kcat assignment](../gecko4-kcat-assignment.md): the sources, the stages and the presets in detail.
- [Project format 4](../gecko4-project-format.md): the layout of `data/kcats` and of the kcat source files.
- [Model adapter parameters](model-adapter-parameters.md): `[kcat_assignment]` and `[kcat_sources]`.
- [Set custom kcats](custom-kcats.md): the curated kcats of the project.
- [Set the protein pool](protein-pool.md): the next step after the kcats.
- [Choose a kcat tuning](kcat-tuning.md): when the model grows too slowly with the assigned kcats.
