# Applying kcats

With one or more kcat lists gathered on
[Gathering kcats](gathering-kcats.md), this page covers filling in the
gaps, applying the resulting kcat values as enzyme constraints, and
constraining the protein pool exchange reaction. The product is a **draft
ecModel**: enzyme constraints are active, but the protein pool is not yet
bounded to a realistic value, so growth is not yet meaningfully limited.
[Growth-rate tuning](growth-rate-tuning.md) covers making it functional.

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `applyCustomKcats` | `apply_custom_kcats` | apply manually curated kcat values |
| `getKcatAcrossIsozymes` | `fill_kcats_from_isozymes` | fill missing isozyme kcats with the mean of their isozymes |
| `getStandardKcat` | `assign_standard_kcat` | assign a fallback kcat to reactions with no gene association |
| `assignKcatValues` | `apply_kcat_list` | populate `ec.kcat` from a kcat list |
| `applyKcatConstraints` | `apply_kcat_constraints` | apply `ec.kcat` to the model's stoichiometry |
| `setProtPoolSize` / `calculateFfactor` | `set_prot_pool_size` / `calculate_f_factor` | constrain the protein pool exchange reaction |

:::{note} Functions that populate `ec.kcat` run in any order
`assignKcatValues`/`apply_kcat_list`, `applyCustomKcats`/`apply_custom_kcats`
and the other functions below can run in any order. Unless stated
otherwise, each overwrites existing values and documents the source in
`ec.source`, for example `brenda` or `custom`.
:::

## Apply a merged kcat list

Integrate a `kcatList` from any previous step, populating `ec.kcat`. Here the merged list from
[Gathering kcats](gathering-kcats.md#merge-dlkcat-and-brenda-structures)
is used:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = assignKcatValues(ecModel, kcatList_merged);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_kcat_list

apply_kcat_list(ec_model, kcat_list_merged)
```

`select_kcat_value` also exists as a deprecated alias of
`apply_kcat_list`.
:::
::::

:::{note} Example output
`ec.kcat` is populated with the selected values, and `ec.source` records
where each is derived from.
:::

## Provide custom kcat values

Custom kcat values can be an alternative or sole source, based on manual
curation, results from later in the reconstruction, or another prediction
procedure such as in vivo apparent enzyme turnover numbers. Document them
in `data/customKcats.tsv` in the adapter folder, mapped to reactions or
enzymes, then apply them:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, rxnUpdated, notMatch] = applyCustomKcats(ecModel);
```

This overwrites existing values in `ecModel.ec.kcat` for matching
reactions, on the assumption that custom values carry higher confidence.

**Custom values that fail to match.** If `notMatch` contains reactions,
their values were not successfully applied, because the gene association
between the model and the input file is a partial match: at least 50%, but
not 100%. A gene association that matches less than 50% is skipped entirely
and does not appear in `notMatch`. Inspect which enzymes are associated with
the reaction in the ecModel and curate the input file to resolve it.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_custom_kcats

apply_custom_kcats(ec_model, path=params.path / "data" / "customKcats.tsv")
```

The same overwrite behavior and the same 50%-gene-match threshold for a
match to be applied hold here; unmatched rows are logged rather than
returned as a `notMatch` list.
:::
::::

## Mean kcat of isozymes (optional)

When a kcat is not defined for every isozymatic variant of a reaction, the
variant lacking a kcat gets no protein cost and is preferred over variants
that do have one, since it looks free in the optimization. Substituting
missing values in `ec.kcat` with the mean kcat of their isozymes
avoids this:

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

`get_kcat_across_isozymes` also exists as a deprecated alias. By default
`fill_kcats_from_isozymes` also calls `apply_kcat_constraints` for the
reactions it filled, so `ec_model.S` reflects the new values immediately;
pass `apply=False` to only update `ec_model.ec.kcat` and defer applying the
constraints, matching the MATLAB behavior.

On a light ecModel (`ec_model.ec.gecko_light == True`),
`fill_kcats_from_isozymes` raises `NotImplementedError`.
:::
::::

This step does not apply to light ecModels, where only the most efficient
isozyme is considered; `getKcatAcrossIsozymes` raises an error on a light
ecModel (Python: `fill_kcats_from_isozymes` raises `NotImplementedError`).

:::{note} Example output
`ec.kcat` is updated so every isozymic reaction has a value, with
`ec.source` for those reactions reading `isozymes`. In MATLAB, the
stoichiometric coefficients are unaffected until the constraints are applied
below; in Python, they are already updated for the affected reactions, since
`fill_kcats_from_isozymes` applies the constraints by default.
:::

## Assign a standard kcat value (optional)

Reactions without genes associated in the starting GEM (empty gene-reaction
rules) cannot carry enzyme constraints, for lack of enzyme data.
For such reactions, excluding exchange, spontaneous, transport and
pseudo-reactions, a standard kcat and a standard pseudo-enzyme
(`prot_standard`) constrain catalytic capacity instead. The standard kcat
is the mean of kcat values for reactions in the same subsystem, or the mean
of every kcat in `ec.kcat` if no subsystem is defined. The standard
molecular weight is the median across every protein in the organism, and a
`usage_prot_standard` reaction is added.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, rxnsMissingGPR, standardMW, standardKcat, rxnsNoKcat] = getStandardKcat(ecModel);
```

The standard MW and the subsystem-agnostic standard kcat are reported in
`standardMW` and `standardKcat`; `rxnsNoKcat` lists the reactions whose
previously zero or `NaN` kcat was replaced with the standard value.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import assign_standard_kcat

assign_standard_kcat(ec_model, uniprot_db)
```

`get_standard_kcat` also exists as a deprecated alias of
`assign_standard_kcat`. The reactions missing a GPR, the standard MW and
the standard kcat are logged rather than returned.
:::
::::

:::{note} Example output
In the `full_ecModel` tutorial, `ec` gains a `standard` pseudo-enzyme of MW
44,898 Da, and reactions without a gene association, together with
reactions whose kcat was zero or `NaN`, receive the standard kcat value of
12.3 s^-1.
:::

## Apply the enzyme constraints

With `ec.kcat` populated from the sources above, apply the enzyme
constraints:

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

This modifies the stoichiometric coefficients of the ecModel (the S-matrix
in MATLAB, the cobra reaction stoichiometries in Python) to directly
include the protein cost, based on the kcat values from `ec.kcat`, the MWs
from `ec.mw` and,
if applied, the enzyme complex stoichiometry from
`applyComplexData`/`apply_complex_data`
(see [Building an empty ecModel](building-ec-model.md#apply-enzyme-complex-stoichiometry-optional)).
Enzymes are directly involved as pseudo-substrates, reflecting enzyme
usage. This function can run again at any point to re-apply the kcat, MW
and complex data.

:::{note} Example output
Every stoichiometric coefficient added or changed above is applied to
the ecModel. The coefficient of an enzyme pseudo-metabolite is:

$$ \frac{MW}{k_{cat} \times 3600} \times (\text{complex stoichiometry}) $$

where the factor 3,600 converts kcat from s^-1 to h^-1, matching the unit
of metabolic rates. Each enzymatic reaction gets one kcat value, which for
complexes can be the highest predicted value across subunits. For example,
if reaction X to Y is catalyzed by a complex of subunits A, B and C at a
ratio 1:1:2, all with MW 27,000 Da and highest predicted kcat of 30 s^-1,
the reaction becomes X + 0.25 A + 0.25 B + 0.5 C to Y.
:::

## Constrain the protein pool exchange reaction

Enzyme pseudo-metabolites are replenished from the total protein pool by
default. Constrain the protein pool exchange reaction to a realistic
value, calculated from the sigma, $P_{tot}$ and f parameters in the model
adapter (average enzyme saturation, total protein content and the fraction
of proteins included in the model):

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setProtPoolSize(ecModel);
```

If quantitative proteomics data are available, for example via PaxDB,
store them in `data/paxDB.tsv` and calculate the f factor:

```matlab
f = calculateFfactor(ecModel);
```

Then use the new f factor to set the protein pool constraint:

```matlab
ecModel = setProtPoolSize(ecModel, [], f);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import set_prot_pool_size

set_prot_pool_size(ec_model, p_tot=params.p_tot, f=params.f, sigma=params.sigma)
```

With no arguments beyond `ec_model`, `set_prot_pool_size` reads `p_tot`,
`f` and `sigma` from `ec_model.adapter.params`; the explicit keyword
arguments above are only needed to override them. If quantitative
proteomics data are available via PaxDB, store them in `data/paxDB.tsv`
and calculate the f factor:

```python
from geckopy import calculate_f_factor, load_pax_db

pax_data = load_pax_db(params.path / "data" / "paxDB.tsv")
f = calculate_f_factor(ec_model, pax_data)
```

Then use the new f factor to set the protein pool constraint:

```python
set_prot_pool_size(ec_model, f=f)
```
:::
::::

:::{note} Values to define the total protein pool are missing
sigma, $P_{tot}$ and f can each be assigned a standard value of 0.5 when no
better estimate exists. If the resulting maximum growth rate is too small
or too large, adjusting sigma manually is a reasonable way to reach a more
plausible value; see
[Growth-rate tuning](growth-rate-tuning.md#too-tight-protein-pool-constraint).
:::

:::{note} Example output
With $P_{tot}$ = 0.5, f = 0.5 and sigma = 0.5, the lower bound of
`prot_pool_exchange` becomes -125 mg/gDCW under the GECKO 3.0 negative-flux
convention (positive under the current GECKO 4 forward convention; see the
tip in [Building an empty ecModel](building-ec-model.md#box-1-extension-of-a-conventional-gem)).
:::

## The ec structure

Enzyme-related information lives in `ecModel.ec` (MATLAB) or `ec_model.ec`
(Python, an `EcData` instance), written `ec` in this Guide. Field names match between languages except
for `rxnEnzMat`/`rxn_enz_mat`. The structure is similar for full and light
ecModels but differs in how the reaction-related fields are populated: in
full ecModels the whole model is expanded, each isozyme gets a separate
reaction, and each reaction maps to one entry in the structure; in light
ecModels the reactions are not split per isozyme, but some starting-GEM
reactions have several entities represented in the structure.

| Field | Data type | Size | Description |
|-------|-----------|------|-------------|
| `rxns` | string array (Python: `list[str]`) | m | Reaction identifiers gathered from the ecModel, after expansion and making irreversible. |
| `rxnEnzMat` (Python: `rxn_enz_mat`) | matrix (Python: sparse `scipy.sparse.csr_matrix`) | m x n | Comparable to the model's reaction-gene matrix, but Enz refers to `ec.enzymes`. Positive integers give the number of enzyme subunits annotated to each reaction. |
| `kcat` | float vector (Python: `numpy.ndarray`) | m | One value per reaction-enzyme (complex) combination, in s^-1, gathered from various sources; `0` means no kcat assigned yet. |
| `source` | string array (Python: `list[str]`) | m | Where the kcat came from, for example `dlkcat`, `brenda`, `standard` or `custom`. |
| `notes` | string array (Python: `list[str]`) | m | Free-text notes the user adds. |
| `eccodes` | string array (Python: `list[str]`) | m | EC numbers gathered from the ecModel and/or UniProt/KEGG, used only for fuzzy kcat matching. |
| `genes` | string array (Python: `list[str]`) | n | Gene identifiers, corresponding to the genes of the ecModel, matching the columns in `rxnEnzMat` (Python: `rxn_enz_mat`). |
| `enzymes` | string array (Python: `list[str]`) | n | UniProt protein identifiers derived from the matching entries in `genes`. |
| `mw` | float vector (Python: `numpy.ndarray`) | n | Molecular weight for each enzyme, in Dalton; unknown is `NaN`. |
| `sequence` | string array (Python: `list[str]`) | n | Amino acid sequence for each enzyme. |
| `concs` | float vector (Python: `numpy.ndarray`) | n | Measured concentration of each enzyme in mg/gDCW; unmeasured is `NaN`. |

In Python, `ec.n_rxns` and `ec.n_enzymes` return the m and n sizes above,
and `ec.gecko_light` is a boolean recording which layout the model uses;
MATLAB has no fields with these names.

## See also

- [Growth-rate tuning](growth-rate-tuning.md), the next step: diagnosing
  why growth is too low and tuning the model to a realistic rate.
- [Gathering kcats](gathering-kcats.md), where the kcat lists applied here
  come from.
- [API reference](../api/index.md), every function in both toolboxes.
