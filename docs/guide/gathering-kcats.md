# Gathering kcats

An empty ecModel has the structure to carry enzyme constraints but no kcat
values yet. This page covers sourcing those values: fuzzy matching against
the BRENDA database, and predicting them with DLKcat or
OpenKineticsPredictor. Each source produces a `kcatList`
(`pandas.DataFrame` in Python) with the same shape, so results from
different sources merge into one list at the end of this page.

Not every enzymatic reaction has a reported measurement. GECKO matches a
BRENDA kcat to a reaction when both the EC number and the organism's
reaction substrate match a BRENDA annotation; if several kcats match, the
highest is selected. DLKcat and OpenKineticsPredictor instead predict a
kcat from enzyme sequence and substrate structure, independent of EC
number, which is useful for less-studied organisms or as the sole kcat
source. Custom values and standard fallback values, covered on
[Applying kcats](applying-kcats.md), complete the picture for reactions
none of these sources cover.

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `getECfromGEM` / `getECfromDatabase` | `fill_eccodes_from_gem` / `fill_eccodes_from_database` | populate EC numbers |
| `fuzzyKcatMatching` | `fuzzy_kcat_matching` | match kcats from BRENDA by EC number, substrate and organism |
| `findMetSmiles` | `find_met_smiles` | annotate metabolites with SMILES for DLKcat/OKP |
| `writeDLKcatInput` / `runDLKcat` / `readDLKcatOutput` | `write_dlkcat_input` / `run_dlkcat` / `read_dlkcat_output` | run DLKcat locally |
| `submitOpenKineticsPredictor` / `fetchOpenKineticsPredictor` | `submit_open_kinetics_predictor` / `fetch_open_kinetics_predictor` | run a kcat prediction job on OpenKineticsPredictor |
| `mergeKcats` | `merge_kcats` | merge kcat lists from multiple sources |

## Choose kcat sources

At least one kcat source is required; any combination works, in any order:

- Fuzzy matching with the [BRENDA database](https://www.brenda-enzymes.org/).
- Prediction via the hosted
  [OpenKineticsPredictor](https://predictor.openkinetics.org/) service
  (GECKO 4).
- Deep learning prediction with DLKcat, run locally via Docker.
- A list of manually curated custom kcat values (see
  [Applying kcats](applying-kcats.md#provide-custom-kcat-values)).
- A standard kcat value assigned as a fallback (see
  [Applying kcats](applying-kcats.md#assign-a-standard-kcat-value-optional)).

Both DLKcat and OpenKineticsPredictor are current GECKO 4 options for
predicted kcats; neither supersedes the other; the difference is that
OpenKineticsPredictor runs as a hosted service with a choice of predictor
methods, and DLKcat runs locally via Docker.

## Fuzzy matching with BRENDA

Matching reactions against BRENDA data by EC number and substrate name is
called fuzzy matching, because it allows wildcards in the EC number, or
kcat values from other substrates, when no exact match exists.

### Assign EC numbers to reactions

EC numbers can come from the starting GEM's EC number annotation, if it has
one (MATLAB: the `model.eccodes` field; Python: each reaction's
`annotation["ec-code"]`), or be gathered from UniProt and KEGG annotations.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

If the starting GEM has manually curated EC numbers, populate
`ecModel.ec.eccodes` with model-derived EC numbers first, then fill the
rest from the database. `getECfromDatabase` overwrites entries in
`ecModel.ec.eccodes`, so mark which entries are still empty before calling
it:

```matlab
ecModel = getECfromGEM(ecModel);
noEC = cellfun(@isempty, ecModel.ec.eccodes);
ecModel = getECfromDatabase(ecModel, noEC);
```

If the starting GEM is not annotated with a `model.eccodes` field, does not
contain standard EC numbers (four groups of digits separated by periods),
or its EC annotations are not trusted, run only `getECfromDatabase`:

```matlab
ecModel = getECfromDatabase(ecModel);
```

`applyECcodes` transfers EC numbers derived from the database back into the
`model.eccodes` fields, if desired.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fill_eccodes_from_database, fill_eccodes_from_gem

fill_eccodes_from_gem(ec_model)
fill_eccodes_from_database(ec_model, uniprot_db)
```

`fill_eccodes_from_database` only fills entries that are still empty, so
calling `fill_eccodes_from_gem` first and `fill_eccodes_from_database`
second already has the same effect as the MATLAB two-call sequence above,
with no separate "which entries were not populated" step. If the starting
GEM's EC annotations are not trusted, skip `fill_eccodes_from_gem` and run
only `fill_eccodes_from_database`. `copy_ec_to_gem` is the equivalent of
`applyECcodes`, writing into each reaction's `annotation["ec-code"]`
(cobrapy's convention) rather than a top-level `model.eccodes` cell array.
:::
::::

:::{note} Difficulties finding EC numbers for the reactions
Fuzzy matching requires EC numbers to be matched to reactions. EC numbers
can be entered manually in the model's EC annotation field, based on any
species-specific information available, and loaded with the functions
above. Because DLKcat does not require EC numbers, using only DLKcat as the
kcat source is an alternative strategy when EC numbers are hard to find.
:::

### Query BRENDA

With `ec.eccodes` populated, gather kcat from BRENDA, queried by EC
number, substrate and organism:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
kcatList_fuzzy = fuzzyKcatMatching(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

BRENDA data and the KEGG phylogenetic-distance file (used to find the
phylogenetically closest organism when no exact match exists) are loaded
explicitly, then passed in:

```python
from geckopy import fuzzy_kcat_matching, load_brenda_data, load_phyl_dist

brenda = load_brenda_data(adapter.get_brenda_db_folder())
phyl_dist = load_phyl_dist(params.path / "data" / "PhylDist.mat")
kcat_list_fuzzy = fuzzy_kcat_matching(ec_model, brenda, phyl_dist)
```
:::
::::

The result documents which kcat was assigned to each reaction and how
precise the match is: the number of EC wildcards used, and whether the
match agreed on substrate and organism. It is common, even for model
organisms such as *S. cerevisiae*, that no full match exists, in which case
a partial organism or substrate match is returned. When no kcat exists for
a particular EC number, wildcards are introduced: EC 2.4.2.3 (uridine
phosphorylase), for example, becomes 2.4.2.- (pentosyltransferase).

If a resolution priority is not met, hierarchical matching criteria apply
in order: if the organism does not match, the kcat of the phylogenetically
closest organism is used; if the substrate does not match, the kcat for any
alternative substrate is used; if the EC number is not found, a fuzzy EC
number (with wildcards) is used; and if no kcat is available in BRENDA at
all, specific activities (typically in micromol per min per mg protein) are
converted into kcat values.

:::{note} Example output
In the `full_ecModel` tutorial, the fuzzy `kcatList` documents, per
reaction: the substrates and EC numbers used to match against BRENDA, the
proposed kcat, `wildcardLvl` (Python: `wildcard_level`; 0: `w.x.y.z`, 1: `w.x.y.-`, 2: `w.x.-.-`, 3:
`w.-.-.-`), and `origin`, the specificity level of the match reached (1:
correct organism and substrate; 2: closest related organism, correct
substrate; 3: correct organism, any substrate; 4: closest related organism,
any substrate; 5: correct organism, specific activity; 6: closest related
organism, specific activity).
:::

## Deep learning prediction with DLKcat

DLKcat predicts a kcat from enzyme sequence information and substrate
structural information in SMILES format.

:::{tip} GECKO 4: prefer OpenKineticsPredictor over a local DLKcat
The steps below run DLKcat locally via Docker, the GECKO 3 approach. In
GECKO 4, submitting the same prediction job to the hosted
[OpenKineticsPredictor (OKP)](https://predictor.openkinetics.org/) service,
covered further down this page, is the recommended alternative: no Docker
install, and a choice of several predictor methods behind one API
(CataPro, CatPred, DLKcat itself, EITLEM, KinForm-H, KinForm-L and UniKP),
defaulting to CataPro. OKP shares the same SMILES-annotation step with
DLKcat and produces a `kcatList` in the same shape, so the two are
interchangeable from the merge step onward.
:::

### Gather SMILES annotations

Starting GEMs rarely include SMILES annotation, so this queries PubChem,
creating `data/smilesDB.tsv`, or fills that file manually.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, noSMILES] = findMetSmiles(ecModel);
```

**Unmatched metabolites.** `findMetSmiles` reports the percentage of
unique metabolites assigned a SMILES annotation. If it is below 100%, as
is almost always the case, inspect the `noSMILES` list of metabolite
names. In some models the metabolite name is suffixed with the metabolite
formula, which prevents matching with PubChem; curating `ecModel.metNames`
resolves such issues.

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

`find_met_smiles` mutates `ec_model` in place and reads/writes through the
`cache_path` TSV; an existing cache, as shipped with the tutorial, means no
PubChem network access is needed. Unmatched metabolites are logged rather
than returned as a `noSMILES` list: the number of unique metabolite names
with a SMILES and the number without are logged at INFO level, and each
name without a SMILES at DEBUG level. As in MATLAB, curate metabolite names
(`metabolite.name`) if a formula suffix or similar naming issue prevents
matching.
:::
::::

:::{note} Example output
In the `full_ecModel` tutorial, a SMILES annotation is found for 64% of the
unique metabolite names, after checking the local SMILES database and
querying PubChem for the rest.
:::

### Write the DLKcat input file

DLKcat runs as a separate tool (see below), so an input file is written
from the ecModel. Currency metabolites that occur in pairs
(for example ATP versus ADP, NADH versus NAD) and a selection of small
molecules (for example Fe2+) are excluded, unless a reaction has no other
reactants after removing them, as for ATP synthase. Nonexhaustive exclusion
lists ship with the toolbox as `DLKcatCurrencyMets.tsv` and
`DLKcatIgnoreMets.tsv` (MATLAB: in `GECKO/databases`; Python: inside the
`geckopy.data` package); an ecModel-specific override can be placed under
`data/` in the adapter folder with the same filenames.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
writeDLKcatInput(ecModel);
```

**Full and light ecModels need separate input files.** `DLKcat.tsv` is
specific to either the full or the light version of the ecModel, because
it carries reaction identifiers from `ec.rxns` needed when loading the
predicted values back into the ecModel. Build separate `DLKcat.tsv` files
for the two ecModel versions.
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
exclusion lists (`DLKcatCurrencyMets.tsv`/`DLKcatIgnoreMets.tsv`, or their
project-specific overrides under `data/`) that MATLAB's `writeDLKcatInput`
reads implicitly. The same full-vs-light `DLKcat.tsv` caveat applies: the
file encodes `ec_model.ec.rxns` identifiers, so a full-model file cannot be
reused for a light model or the reverse.
:::
::::

### Run DLKcat and load its output

Running DLKcat downloads and starts a Docker image automatically. No other
input is given, because the function assumes the input file is at
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

:::{note} DLKcat fails to run
DLKcat's Docker requirement can be an obstacle if Docker Desktop cannot be
installed or its use is restricted. `GECKO/src/dlkcat-gecko/` (in the
GECKO repository) contains the Python scripts and data needed to run
DLKcat directly with the `DLKcat.tsv` file written above, without Docker:

```bash
pipenv install -r requirements.txt
pipenv run python DLKcat.py DLKcat.tsv DLKcatOutput.tsv
```

Run both commands from the system terminal, not from MATLAB or Python.
:::

The resulting `kcatList` is similar in shape to the BRENDA one, but has no
EC numbers, wildcard levels or origin values, and instead includes the
`genes` of each reaction. In MATLAB the fields `eccodes`, `wildcardLvl` and
`origin` are absent; in Python the columns `eccode`, `wildcard_level` and
`origin` are present but empty.

## Kcat prediction with OpenKineticsPredictor (GECKO 4)

OpenKineticsPredictor (OKP) shares its input with DLKcat: protein sequences
and single-substrate SMILES, gathered in the section above. It needs no
Docker.

:::{warning} The API key is a secret; never put it in the model adapter
OKP requires a personal Bearer API key (looks like `ak_...`). Get one free,
no registration required, at
[predictor.openkinetics.org/api-docs](https://predictor.openkinetics.org/api-docs)
(the "API key generator" section; the key is shown once, and can be revoked
and regenerated from the same page). Keys are tied to the requesting IP and
carry a daily prediction quota that resets at midnight UTC.

Because the model adapter is typically shared and committed to version
control, the key does not belong there. Both languages resolve it the same
way, checked in this order: an explicit function argument; the
`OKP_API_KEY` environment variable; or a plain-text `data/okpApiKey.txt`
file in the adapter folder (a filename already git-ignored by GECKO).
:::

Submit a prediction job for the whole ecModel:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
jobId = submitOpenKineticsPredictor(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import submit_open_kinetics_predictor

job_id = submit_open_kinetics_predictor(ec_model)
```
:::
::::

Both write the request to `data/OKP.csv` and the returned job id to
`data/OKP_job.txt`, so a later call can find the job without passing
`jobId`/`job_id` explicitly. Pass `method='DLKcat'` (MATLAB) /
`method="DLKcat"` (Python) to request DLKcat specifically through OKP
instead of the CataPro default.

Poll until the job finishes and parse the result into a `kcatList`:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[done, kcatList_OKP] = fetchOpenKineticsPredictor(ecModel, 'wait', true);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fetch_open_kinetics_predictor

done, kcat_list_okp = fetch_open_kinetics_predictor(ec_model, wait=True)
```

`wait=True` polls every 30 seconds (`poll_interval=`) until the job is done
or `timeout` (default one hour) is reached. `wait=False`, the default,
checks once and returns immediately, useful for checking a long-running job
from a separate call without blocking.
:::
::::

The downloaded result is cached at `data/OKP_output.csv`; pass `useStored`
(MATLAB) / `use_stored=True` (Python) to re-parse it without contacting the
API again. `kcatList_OKP` / `kcat_list_okp` has the same shape as the
BRENDA and DLKcat kcat lists above, so the merge step below, and
`assignKcatValues`/`apply_kcat_list` on
[Applying kcats](applying-kcats.md#apply-the-enzyme-constraints), accept it
identically.

## Merge DLKcat and BRENDA structures

Merging kcat lists from multiple sources increases coverage, keeping the
highest-priority source for each reaction. The same call works with
`kcatList_OKP` / `kcat_list_okp` in place of the DLKcat list, since the
function merges by structure rather than by name, regardless of which
predictor produced the second list:

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

`mergeKcats` (MATLAB) / `merge_kcats` (Python) accepts any number of
`kcatList`s, for example BRENDA, DLKcat and OpenKineticsPredictor results
together, each assigned an explicit priority in `sourcePriority` /
`source_priority`. `'database_top'`/`'database_bottom'` are reserved tier
tokens for strong/weak fuzzy BRENDA matches; any other token (`'dlkcat'`,
`'catapro'`, ...) matches a row's own `source` value. A third reserved
tier, `'database_exact'`, ranks above both: an exact experimental
measurement with no fuzzy wildcarding, which OpenKineticsPredictor can
return directly.

:::::{note} `mergeDLKcatAndFuzzyKcats`/`merge_dlkcat_and_fuzzy_kcats` are deprecated
Both are thin two-source wrappers around `mergeKcats`/`merge_kcats` with the
priority order `['database_top', 'dlkcat', 'database_bottom']`, kept only
for backward compatibility with the original two-source signature:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
kcatList_merged = mergeDLKcatAndFuzzyKcats(kcatList_DLKcat, kcatList_fuzzy);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import merge_dlkcat_and_fuzzy_kcats

kcat_list_merged = merge_dlkcat_and_fuzzy_kcats(
    kcat_list_dlkcat, kcat_list_fuzzy,
)
```
:::
::::

Both raise a deprecation warning when called; use `mergeKcats`/`merge_kcats`
directly, as shown above.
:::::

Merging assigns a single kcat to each reaction, with priority given to
BRENDA values from a full EC number match. Mismatches on organism and
substrate are allowed by default, and modifiable through additional input
parameters. If no exact EC match exists, the DLKcat (or OKP) value is used.
If neither predicted a value for a reaction, for example because its
substrate had no SMILES annotation, EC number wildcard matches from fuzzy
matching are allowed if available: instead of assigning a kcat to pyruvate
oxidase by querying EC 1.2.3.3, the merge queries EC 1.2.3.-, which
includes any oxidoreductase acting on the aldehyde or oxo group of donors
with oxygen as acceptor, and selects the highest kcat from that group.

:::{note} Example output
The merged `kcatList` carries the same fields as the fuzzy-matching result
above, plus a `kcatSource` field (Python: the `source` column, which every
list has) naming which source contributed each value individually.
:::

## See also

- [Applying kcats](applying-kcats.md), the next step: custom values,
  isozyme means, a standard fallback, and applying the resulting
  constraints to the ecModel.
- [Building an empty ecModel](building-ec-model.md), where the empty
  ecModel these kcats attach to comes from.
- [API reference](../api/index.md), every function in both toolboxes.
