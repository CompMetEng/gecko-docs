# Choose the kcat sources

GECKO selects one kcat per enzymatic reaction from the kcat source files in `data/kcats`, in the order that `[kcat_assignment]` of `model_adapter.toml` defines. The result is a project with a preset (or its own stages) and the source files that the preset reads, and an ecModel with the assigned kcats applied as enzyme constraints.

<!-- workflow-place -->
:::::{dropdown} Place in the workflow

The diagram orders the functions of this page within the [workflow](workflow.md). Boxes with a dashed outline are optional steps, a dotted arrow is an optional path, and a diamond is a choice. Rounded boxes with a dotted outline are the context, other pages or the model to start from, and a click on one opens its page.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```{mermaid}
:align: left

---
config:
  flowchart:
    useMaxWidth: false
---
flowchart TB
  classDef opt stroke-dasharray: 5 4
  classDef ctx fill:transparent,stroke-dasharray: 2 3
  PV(["Previous: Choose the ecModel structure"]):::ctx
  PR["preset or stages<br/>[kcat_assignment] in model_adapter.toml"]
  EC["EC numbers<br/>getECfromGEM, then getECfromDatabase"]
  SM["metabolite SMILES<br/>findMetSmiles"]
  US["updateKcatSources<br/>one file per source in data/kcats"]
  CO["collectKcats<br/>compare presets"]:::opt
  AS["assignKcats"]
  CU(["Set custom kcats"]):::ctx
  PV --> PR
  PR --> EC --> US
  PR --> SM --> US
  US --> CO --> AS
  US --> AS
  CU -.-> AS
  NX(["Next: Set the protein pool"]):::ctx
  AS --> NX
  click PV href "ecmodel-structure.html"
  click CU href "custom-kcats.html"
  click NX href "protein-pool.html"
```
:::
:::{tab-item} 🐍 Python
:sync: python

```{mermaid}
:align: left

---
config:
  flowchart:
    useMaxWidth: false
---
flowchart TB
  classDef opt stroke-dasharray: 5 4
  classDef ctx fill:transparent,stroke-dasharray: 2 3
  PV(["Previous: Choose the ecModel structure"]):::ctx
  PR["preset or stages<br/>[kcat_assignment] in model_adapter.toml"]
  EC["EC numbers<br/>fill_eccodes_from_gem, then fill_eccodes_from_database"]
  SM["metabolite SMILES<br/>find_met_smiles"]
  US["update_kcat_sources<br/>one file per source in data/kcats"]
  CO["collect_kcats<br/>compare presets"]:::opt
  AS["assign_kcats"]
  CU(["Set custom kcats"]):::ctx
  PV --> PR
  PR --> EC --> US
  PR --> SM --> US
  US --> CO --> AS
  US --> AS
  CU -.-> AS
  NX(["Next: Set the protein pool"]):::ctx
  AS --> NX
  click PV href "ecmodel-structure.html"
  click CU href "custom-kcats.html"
  click NX href "protein-pool.html"
```
:::
::::
:::::

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `getECfromGEM` / `getECfromDatabase` | `fill_eccodes_from_gem` / `fill_eccodes_from_database` | fill the EC numbers of `ec.eccodes` |
| `findMetSmiles` | `find_met_smiles` | find the SMILES of the metabolites, for the prediction methods |
| `updateKcatSources` | `update_kcat_sources` | gather the source files that the preset reads and that are missing or outdated |
| `collectKcats` | `collect_kcats` | determine the kcats without changing the model |
| `assignKcats` | `assign_kcats` | determine the kcats and apply them as enzyme constraints |

## Setup

The examples start from an ecModel made with `makeEcModel` (Python: `make_ec_model`), full or light ([Choose the ecModel structure](ecmodel-structure.md)). In MATLAB, the project is the default model adapter (`ModelAdapterManager.setDefault`); in Python, `ec_model.adapter` holds the project. The project folder has `data/uniprot.tsv` and `data/kegg.tsv` from making the ecModel. The OpenKineticsPredictor (OKP) method and DLKcat without `data/DLKcat.tsv` need an OKP API key ([Prepare the inputs](#prepare-the-inputs)). The BRENDA download, the PubChem queries and OpenKineticsPredictor need internet access.

## Presets

`[kcat_assignment] preset` selects one of six presets. Each preset is a list of stages, and a stage gives a kcat to the reactions that the earlier stages left without one. Every preset starts with the custom kcats of the project. In the table, "the OKP predictions" are those of the OKP method of `[kcat_sources.okp] method`; the default is KinForm-H, and a stage uses its prediction with the bias correction of that method.

| Preset | Kcat of a reaction, in this order | Needs |
| --- | --- | --- |
| `brenda_ec_tree` (default) | BRENDA median of measurements of the organism on the substrate of the reaction; the EC tree; the OKP predictions | EC numbers, BRENDA files, SMILES, OKP API key |
| `ec_tree_homologs` | BRENDA value of the organism; the EC tree and the measured homologs combined; the OKP predictions | as `brenda_ec_tree`, plus DIAMOND |
| `ec_tree_okp` | BRENDA value of the organism; the EC tree, the homologs and the OKP predictions combined; the OKP predictions | as `ec_tree_homologs` |
| `okp` | the OKP predictions | SMILES, OKP API key |
| `gecko_median` | BRENDA median of matches without EC wildcards (origin 1 to 4); DLKcat; the other BRENDA matches | EC numbers, BRENDA files, SMILES, OKP API key or `data/DLKcat.tsv` |
| `gecko_classic` | the order of the GECKO 3 tutorial: as `gecko_median` with the BRENDA maximum, and with the matches from specific activities (origin 5 and 6) before DLKcat | as `gecko_median` |

A "combined" value is the mean of the values of several sources in log10 units, each corrected for the bias of its source and weighted by the precision of the source for that reaction. The origin levels of BRENDA matches are explained in [BRENDA origin and wildcard levels](#brenda-origin-and-wildcard-levels). [Kcat assignment](../gecko4-kcat-assignment.md) describes each source and the exact stages of each preset.

A project can list its own stages in `[[kcat_assignment.stage]]` tables in place of a preset. [Kcat assignment](../gecko4-kcat-assignment.md#presets) gives the TOML syntax and the stage options.

### Preset to start with

Against measured kcats hidden from the search, the EC tree was as close as or closer than the BRENDA median at origins 1 to 4 and with EC wildcards, and the EC tree combined with OKP predictions was slightly closer than the EC tree; in ecModels, however, values combined with predictions set high-turnover enzymes such as ATP synthase too low ([Kcat assignment](../gecko4-kcat-assignment.md#presets)). No other comparison of the presets has been measured, and KinForm-H, the default OKP method, was not compared separately. `brenda_ec_tree`, the default, uses predictions for the reactions without a value from measurements, and is the preset to start with.

### BRENDA median and maximum

`kcat.tsv` of the BRENDA release has one entry per EC number, substrate and organism, with the maximum and the median of the measured kcats of that entry. When several entries match a reaction, for example with an EC wildcard or on any substrate, `fuzzyKcatMatching` (Python: `fuzzy_kcat_matching`) takes the maximum or the median of the matched values as well, with the same setting. The presets `brenda_ec_tree`, `ec_tree_homologs`, `ec_tree_okp` and `gecko_median` use the median, because the maximum is often far above a typical measurement; `gecko_classic` uses the maximum. In `kcat.tsv` of the release `brenda-2026.1-1`, with trypsin (EC 3.4.21.4) left out of the analysis:

- 9,549 of the 39,053 entries (24 %) hold more than one measurement. In these entries, the median of log10(maximum/median) was 0.16 and the mean 0.26 (a factor of 1.4 and 1.8). The maximum was at least 10 times the median in 4.8 % of these entries, and at least 100 times in 1.2 %.
- For the 1,722 EC numbers with at least five entries, the maximum over all entries of the EC number was at least 10 times the median of the entry medians for 59.5 % of the EC numbers, at least 100 times for 24.2 % and at least 1,000 times for 8.6 %. The mean log10 ratio was 1.45. Of this, 1.38 came from taking the maximum over the entries and 0.06 from taking the maximum within an entry.
- For esterase (EC 3.1.1.1, 355 entries), the maximum was 431,000 s⁻¹ and the median of the entry medians 24 s⁻¹.

These numbers compare the BRENDA values with each other. They do not compare the predictions of ecModels made with the maximum and with the median.

## BRENDA origin and wildcard levels

A BRENDA match records how specific it is in two numbers, which `ec.source` shows as `brenda (wc=<wildcard level>, origin=<origin>)` and which the presets use to rank BRENDA values.

| Origin | BRENDA value |
| --- | --- |
| 1 | kcat of the organism, on the substrate of the reaction |
| 2 | kcat of the closest related organism (by KEGG phylogeny), on the substrate |
| 3 | kcat of the organism, on any substrate |
| 4 | kcat of the closest related organism, on any substrate |
| 5 | specific activity of the organism, converted with the molecular weight |
| 6 | specific activity of the closest related organism |

| Wildcard level | EC number used |
| --- | --- |
| 0 | `w.x.y.z` |
| 1 | `w.x.y.-` |
| 2 | `w.x.-.-` |
| 3 | `w.-.-.-` |
| 4 | `-.-.-.-` (every EC number in BRENDA) |

Matches at wildcard level 4 are kept in `brenda.tsv`, and no stage uses them: the `wildcard_limit` of a stage is at most 3.

For each EC number, the origins are tried in the order 1, 2, 3, 5, 4, 6, so a specific activity of the organism is used before a kcat of another organism on another substrate. When no origin gives a value, the rightmost level of the EC number that is not yet a wildcard is replaced by `-`, and the origins are tried again. With a wildcard, origins 1 and 2 are skipped, because the last levels of an EC number define the substrate specificity. When a reaction has several EC numbers, the match with the fewest wildcards, then the earliest tried origin, then the highest kcat is used.

## Prepare the inputs

The sources read different parts of the ecModel and of the project:

| Input | Read by | How to get it |
| --- | --- | --- |
| EC numbers in `ec.eccodes` | BRENDA, EC tree | `getECfromGEM` (from the GEM), `getECfromDatabase` (from UniProt and KEGG) |
| SMILES of the metabolites | OKP, DLKcat | `findMetSmiles`; substrates without a SMILES are left out of a prediction |
| enzyme sequences in `ec.sequence` | OKP, DLKcat, homologs | `makeEcModel` fills them from UniProt ([Choose the ecModel structure](ecmodel-structure.md)) |
| BRENDA files | BRENDA, EC tree, homologs, combined stages | `fetchBrendaAsset` downloads the release `brenda-2026.1-1` on first use. A project folder `data/brenda` takes precedence. MATLAB needs RAVEN 3 for the download |
| DIAMOND | homologs | the DIAMOND executable of RAVEN (MATLAB) or raven-toolbox (Python) |
| OpenKineticsPredictor API key | OKP, DLKcat without `data/DLKcat.tsv` | generate a key at [predictor.openkinetics.org](https://predictor.openkinetics.org/) |

GECKO looks for the API key in the environment variable `OKP_API_KEY` and then in the file `data/okpApiKey.txt` of the project. The key is never read from `model_adapter.toml`. Do not commit `data/okpApiKey.txt` to a public repository.

`getECfromDatabase` replaces the EC numbers of the reactions it is given, so the reactions that still have no EC number after `getECfromGEM` are selected. In Python, KEGG fills the reactions without a UniProt EC number when `kegg_db` is given:

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
from geckopy.databases import load_kegg_tsv

data = ec_model.adapter.params.path / "data"
fill_eccodes_from_gem(ec_model)
no_ec = [rxn for rxn, ec in zip(ec_model.ec.rxns, ec_model.ec.eccodes) if not ec]
uniprot_db = load_uniprot_tsv(data / "uniprot.tsv")
kegg_db = load_kegg_tsv(data / "kegg.tsv")
fill_eccodes_from_database(ec_model, uniprot_db, kegg_db=kegg_db, ec_rxns=no_ec)
find_met_smiles(ec_model)
```
:::
::::

When the EC numbers of the GEM are not reliable, skip `getECfromGEM` and fill all reactions from the databases: `ecModel = getECfromDatabase(ecModel);` (Python: `fill_eccodes_from_database(ec_model, uniprot_db, kegg_db=kegg_db)`).

`findMetSmiles` queries PubChem by metabolite name and keeps the results in `data/smilesDB.tsv`. A metabolite name that PubChem does not find gets no SMILES; correct the name in the model or add the SMILES to `data/smilesDB.tsv`.

## Gather the source files

`updateKcatSources` lists the source files that the preset reads and gathers each file that is missing or outdated. A file is outdated when the settings in its header differ from the settings of the preset and `[kcat_sources.<name>]`, or when it was made from another BRENDA release than the BRENDA files in use. `custom.tsv` is never gathered or changed. The option `dryRun` reports the status of each file without gathering.

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

`report` has one row per source file, with the columns `source`, `status` and `note`. The status is `current`, `gathered`, `pending`, `outdated`, `missing`, `failed` or `skipped`. OpenKineticsPredictor is a web service with a job queue: the first call submits the job and reports the source as `pending`, and a later call fetches the result and writes the file. Call `updateKcatSources` again until no source is `pending`. A source that is `failed` has the reason in `note`, for example a missing API key.

`[kcat_sources.<name>]` of `model_adapter.toml` holds the settings with which `updateKcatSources` gathers a source file. A preset sets `aggregation` of `brenda` and `k` of `ec_tree`. A `[kcat_sources.<name>]` table in `model_adapter.toml` overrides the keys that it sets and keeps the other settings of the preset. A source file gathered before a change of these settings is then reported as `outdated`.

| Table | Key | Default |
| --- | --- | --- |
| `[kcat_sources.brenda]` | `aggregation`: `max` or `median` of the BRENDA values per EC number, substrate and organism | set by the preset (`median` for `brenda_ec_tree`, `ec_tree_homologs`, `ec_tree_okp` and `gecko_median`, `max` for `gecko_classic`); `max` for the preset `okp` and for stages |
| `[kcat_sources.brenda]` | `force_wildcard_level`: number of EC levels replaced by a wildcard in every EC number | 0 |
| `[kcat_sources.ec_tree]` | `k`: shrinkage constant | 5 |
| `[kcat_sources.homologs]` | `k`: number of homologs | 10 |
| `[kcat_sources.homologs]` | `min_identity`: minimum sequence identity, as a fraction | 0.4 |
| `[kcat_sources.homologs]` | `coverage`: minimum coverage of both sequences, as a fraction | 0.8 |
| `[kcat_sources.okp]` | `method`: the OpenKineticsPredictor method whose file `okp_<method>.tsv` `okp` stands for in a stage | `"KinForm-H"` |

The tables of `custom`, `dlkcat` and `okp_<method>` take no keys; the method of an `okp_<method>` file is the method whose name gives the file name. Any other key is an error when `model_adapter.toml` is read (see [Model adapter parameters](model-adapter-parameters.md#kcat-source-settings)). The BRENDA aggregation also applies to `kcatsFromBrenda` and `fuzzyKcatMatching` called without an aggregation ([BRENDA aggregation](model-adapter-parameters.md#brenda-aggregation)).

The source `dlkcat` (presets `gecko_median` and `gecko_classic`) reads `data/DLKcat.tsv` when the file exists. Without it, `dlkcat` is predicted with the DLKcat method of OpenKineticsPredictor.

:::{admonition} DLKcat in Docker
:class: note

DLKcat can also run on the local computer, in the Docker image `ghcr.io/sysbiochalmers/dlkcat-gecko:0.1`. This is the older method and needs Docker installed and running. `kcatsFromDLKcat(ecModel, 'via', 'docker')` (Python: `kcats_from_dlkcat(ec_model, via="docker")`) runs it and writes `data/kcats/dlkcat.tsv`; `updateKcatSources` then finds the file current.
:::

## Compare presets before applying

`collectKcats` determines the kcats as `assignKcats` does and does not change the model. It writes the result to `output/<model id>_kcatDecisions.tsv` unless `writeReport` (Python: `write_report`) is false. The file has one row per reaction of `ec.rxns` with these columns; the table that MATLAB returns has the names in parentheses:

| Column | Content |
| --- | --- |
| `ec_rxn` (`ecRxn`) | the reaction of `ec.rxns` |
| `stage` | the number of the stage that gave the kcat (`1` for a kcat from `custom.tsv`), `isozymes` or `standard`; empty when the reaction has no kcat |
| `source` | the source as written to `ec.source` |
| `kcat` | the kcat in s^-1 |
| `candidates` | the number of values that the selected source had for the reaction, or the number of sources combined |
| `spread_log10` (`spreadLog10`) | the range of these values in log10 units |
| `sd_log10` (`sdLog10`) | the uncertainty of a combined value in log10 units |

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

Presets with other source settings share the source files: `gecko_classic` gathers `brenda.tsv` with the BRENDA maximum and the other presets with the median. Gathering the sources of one preset then makes the file outdated for the other. Compare such presets in a copy of the project folder, or run `updateKcatSources` with the preset of the project again before `assignKcats`.

## Assign the kcats

`assignKcats` determines the kcats, writes `ec.kcat` and `ec.source` (see [Provenance of a kcat](../gecko4-kcat-assignment.md#provenance-of-a-kcat)), applies the enzyme constraints and writes the decisions file. The kcats that the model had before are replaced.

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

- `isozymes` (default true): in a full ecModel, a reaction without a kcat gets the mean kcat of its isozymes. An isozyme reaction with a kcat of 0 has no enzyme cost after `applyKcatConstraints`, so an optimisation uses it in place of the isozymes that have a kcat. A light ecModel uses the most efficient isozyme and skips this step.
- `standard` (default true): the remaining reactions get the standard kcat, which is the median kcat of the subsystem of the reaction when the subsystem has at least 10 reactions with a kcat, and the median of all kcats otherwise. Reactions without a gene association get the pseudo-enzyme `prot_standard`, with the median molecular weight of the proteins in `data/uniprot.tsv`. Exchange, transport, spontaneous and pseudo-reactions get no standard kcat; list other reactions to leave out in `data/pseudoRxns.tsv` ([Files in the data folder](data-folder-files.md)).

## Add custom kcats

`data/kcats/custom.tsv` holds the curated kcats of the project. Every preset reads it in its first stage, so a custom kcat is used before all other sources. [Set custom kcats](custom-kcats.md) describes the file, the conversion of `data/customKcats.tsv` of a GECKO 3 project, and how to change a kcat by hand.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| OKP sources stay `pending` | the OpenKineticsPredictor job is still running | Call `updateKcatSources` again later |
| OKP sources are `failed` with `No OpenKineticsPredictor API key found` | no key in `OKP_API_KEY` or in `data/okpApiKey.txt` | Generate a key and store it in one of the two places |
| `No kcat source file <file>; it is left out` | a stage names a source that has no file in `data/kcats` | Run `updateKcatSources`, or remove the source from the stages |
| BRENDA and the EC tree give kcats for few reactions | many reactions have no EC number | Fill `ec.eccodes` (section [Prepare the inputs](#prepare-the-inputs)) |
| Few reactions get a predicted kcat | many metabolites have no SMILES | Read `noSMILES` of `findMetSmiles` (Python: the log of `find_met_smiles`, with the number at INFO level and the names at DEBUG level) and correct the metabolite names or `data/smilesDB.tsv` |
| Error `kcatAssignment:config` (Python: a validation error of the adapter) | an unknown preset, a preset and stages together, a stage with a wrong value, or an unknown OKP method in `[kcat_sources.okp] method` | Correct `[kcat_assignment]` or `[kcat_sources.okp]` |
| Kcats set by hand are gone | `assignKcats` replaced them | Write them to `data/kcats/custom.tsv` ([Set custom kcats](custom-kcats.md)) |

## See also

- [Kcat assignment](../gecko4-kcat-assignment.md): the sources, the stages and the presets in detail.
- [Project format 4](../gecko4-project-format.md): the layout of `data/kcats` and of the kcat source files.
- [Model adapter parameters](model-adapter-parameters.md): `[kcat_assignment]` and `[kcat_sources]`.
- [Set custom kcats](custom-kcats.md): the curated kcats of the project.
- [Set the protein pool](protein-pool.md): the next step after the kcats.
- [Choose a kcat tuning](kcat-tuning.md): when the model grows too slowly with the assigned kcats.
