# Set custom kcats

`data/kcats/custom.tsv` holds the curated kcats of a project, for example a value from the literature or a value kept after [kcat tuning](kcat-tuning.md). The result is a `custom.tsv` that `assignKcats` reads before all other sources, and an ecModel with the custom kcats applied.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `assignKcats` | `assign_kcats` | determine the kcats, with the custom kcats first, and apply them; the report lists the rows that were not applied |
| `convertCustomKcats` | `convert_custom_kcats` | convert `data/customKcats.tsv` of a GECKO 3 project into `data/kcats/custom.tsv` |
| `setKcatForReactions` | `set_kcat_for_reactions` | change `ec.kcat` of named reactions in the model |
| `applyKcatConstraints` | `apply_kcat_constraints` | apply `ec.kcat` to the stoichiometry |

## Setup

The examples start from an ecModel made with `makeEcModel` (Python: `make_ec_model`), full or light. In MATLAB, the project is the default model adapter (`ModelAdapterManager.setDefault`); in Python, `ec_model.adapter` holds the project. The other source files of the preset are in `data/kcats` ([Choose the kcat sources](kcat-sources.md#gather-the-source-files)); `assignKcats` leaves a missing source file out.

## Write custom.tsv

Every preset reads `custom.tsv` in its first stage ([Choose the kcat sources](kcat-sources.md)), so a custom kcat is used before all other sources. `updateKcatSources` and `saveKcatSource` do not write this file.

The file is tab-separated. It needs the columns `kcat` and `source`, and `rxn`, `enzymes` or both. The other columns of a kcat source file (`substrate`, `log10_sd`, `detail`, `ec_code`, `note`) are optional. Lines that start with `#` before the column header are header lines.

| Column | Content |
| --- | --- |
| `rxn` | the identifier of the reaction in the conventional GEM, with `_REV` for the reverse direction. Without `enzymes`, the row applies to every isozyme of the reaction |
| `enzymes` | the UniProt accessions of the enzyme, joined by ` + ` in any order. Without `rxn`, the row applies to every reaction whose enzyme set is this set |
| `kcat` | the kcat in s^-1 |
| `source` | where the value comes from, for example `custom`; `ec.source` holds it in lower case, with each run of characters other than letters and digits replaced by `_` |
| `note` | free text, for example the reference |

```text
rxn	enzymes	kcat	source	note
R1	P12345	120	custom	measured value of the organism
R2_REV		35	custom	value for all isozymes
```

`R1`, `R2` and `P12345` stand for reactions of the GEM and a UniProt accession of the organism. The rows are keyed by the conventional reaction and the enzyme set, which do not depend on how the ecModel is built. The file therefore stays valid when the ecModel is rebuilt, and it applies to full and light ecModels. [Project format 4](../gecko4-project-format.md#kcat-source-files) describes the format of all kcat source files.

## Apply the custom kcats

`assignKcats` reads `custom.tsv` with the other source files. A row whose kcat is empty, is text other than a number, or is 0 or below is not applied. A row that matches no reaction of the ecModel, or that matches part of an enzyme set, is not applied either. The report lists these rows per source file:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, decisions, report] = assignKcats(ecModel);
report.sources.custom.invalid
report.sources.custom.unmatched
report.sources.custom.partial
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import assign_kcats

decisions, report = assign_kcats(ec_model)
custom = report["sources"]["custom"]
print(custom["invalid"], custom["unmatched"], custom["partial"])
```
:::
::::

A row in `partial` shares at least half of its enzymes with a reaction of the ecModel. The table names that reaction and its enzymes, so the row can be corrected to the enzyme set of the model.

## Convert the custom kcats of a GECKO 3 project

`convertCustomKcats` (Python: `convert_custom_kcats`) writes the custom kcats of `data/customKcats.tsv` as `data/kcats/custom.tsv`; it needs the full ecModel and does not overwrite an existing `custom.tsv`. [Upgrade a GECKO 3 project](../gecko3-upgrade-project.md) describes this conversion with the other steps of an upgrade.

## Change kcats by hand

`setKcatForReactions` changes `ec.kcat` of the named reactions, and `applyKcatConstraints` applies the change to the stoichiometry. In a full ecModel, a reaction name without `_EXP_<n>` changes all isozymes of the reaction. In a light ecModel, the names in `ec.rxns` have a number prefix (`001_R1`), and the name is given with this prefix. A name that matches no entry of `ec.rxns` is ignored without a message. `ec.source` of a changed reaction reads `manual`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setKcatForReactions(ecModel, {'R1'}, 120);
ecModel = applyKcatConstraints(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_kcat_constraints, set_kcat_for_reactions

set_kcat_for_reactions(ec_model, ["R1"], 120)
apply_kcat_constraints(ec_model)
```
:::
::::

:::{warning}
`assignKcats` replaces all kcats of the model with the values from the source files. A kcat set with `setKcatForReactions` is lost when `assignKcats` runs again. Write a kcat that must stay in the model to `data/kcats/custom.tsv`.
:::

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| A custom kcat is not used | the row matches no reaction, or part of an enzyme set | Read `report.sources.custom` of `assignKcats` and correct `rxn` or `enzymes` |
| A custom row is listed as invalid | the kcat is empty, 0, or not a plain number (for example `5,5` with a decimal comma) | Write the kcat as a number with a decimal point |
| Error `loadKcatSource:columns` (Python: `ValueError` with `needs the columns kcat and source`) | the file lacks `kcat`, `source`, or both `rxn` and `enzymes` | Add the columns to the header line |
| Error `collectKcats:legacyCustomKcats` (Python: `ValueError`) | the project has the GECKO 3 file `data/customKcats.tsv` and no `data/kcats/custom.tsv` | Run `convertCustomKcats` |
| Kcats set by hand are gone | `assignKcats` replaced them | Write them to `data/kcats/custom.tsv` |
| Error `convertCustomKcats:exists` (Python: `FileExistsError`) | the function does not overwrite the file | Remove the file, or give another `outFile` (Python: `out_file`) |
| Error `convertCustomKcats:light` (Python: `ValueError`) | the conversion needs the full ecModel | Convert with the full ecModel; the `custom.tsv` written also applies to the light ecModel |

## See also

- [Choose the kcat sources](kcat-sources.md): the presets and the order of the sources.
- [Choose a kcat tuning](kcat-tuning.md): tuned kcats to check and keep in `custom.tsv`.
- [Project format 4](../gecko4-project-format.md): the layout of `data/kcats` and of the kcat source files.
