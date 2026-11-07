# Proteomics integration

Enzyme usage reactions let a full ecModel take proteomics data directly: individual enzymes with measured concentrations are bounded by those measurements, in addition to drawing from the shared total protein pool. The ecModel is then constrained by the proteomics and the exchange flux data of one experimental condition, and its growth rate is solved.

:::{warning}
The functions below apply to full ecModels. A light ecModel has no per-enzyme usage reactions to constrain; see [GECKO light and full ecModels](gecko-light.md).
:::

<!-- workflow-place -->
:::::{dropdown} Place in the workflow

The diagram orders the functions of this page within the [workflow](workflow.md). Dashed boxes are optional and dotted boxes are neighbouring pages.

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
  PV(["Previous: Growth-rate tuning"]):::ctx
  PV --> A["loadProtData<br/>fillEnzConcs"] --> B["levelComplexConcs<br/>constrainEnzConcs"] --> I["getIsozymeCoverage<br/>zeroUnmeasuredIsozymes"]:::opt --> C["calculateFfactor, setProtPoolSize"] --> D["loadFluxData, constrainFluxData"]:::opt
  NX(["Next: Relaxing overconstrained proteomics"]):::ctx
  D --> NX
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
  PV(["Previous: Growth-rate tuning"]):::ctx
  PV --> A["load_prot_data<br/>fill_enz_concs"] --> B["level_complex_concs<br/>constrain_enz_concs"] --> I["get_isozyme_coverage<br/>zero_unmeasured_isozymes"]:::opt --> C["calculate_f_factor, set_prot_pool_size"] --> D["load_flux_data, apply_flux_data_constraints"]:::opt
  NX(["Next: Relaxing overconstrained proteomics"]):::ctx
  D --> NX
```
:::
::::
:::::

## Functions

| MATLAB | Python | Note |
|---|---|---|
| `loadProtData` | `load_prot_data` | read `proteomics.tsv` into a proteomics data structure and filter it |
| `fillEnzConcs` | `fill_enz_concs` | populate `ec.concs` with the measured concentrations |
| `levelComplexConcs` | `level_complex_concs` | give the subunits of each complex one abundance |
| `getComplexFamilies` | `complex_families` | group the enzymes of multi-subunit reactions into complexes |
| `constrainEnzConcs` | `constrain_enz_concs` | apply the concentrations as upper bounds of the `usage_prot_<id>` reactions |
| `getIsozymeCoverage` | `get_isozyme_coverage` | list the reactions with a measured and an unmeasured isozyme |
| `zeroUnmeasuredIsozymes` | `zero_unmeasured_isozymes` | lower the usage upper bound of the unmeasured isozymes of such a reaction |
| `calculateFfactor` + `setProtPoolSize` | `calculate_f_factor` + `set_prot_pool_size` | recompute the protein pool constraint from the proteomics data |
| `loadFluxData` | `load_flux_data` | read `fluxData.tsv` (exchange fluxes and growth rate of the same experiment) |
| `constrainFluxData` | `apply_flux_data_constraints` | apply the exchange flux and growth rate constraints |

## Setup

The data are in `data/proteomics.tsv` and `data/fluxData.tsv` of the project (see [Files in the data folder](data-folder-files.md)). An ecModel is loaded or built as described in [Building an empty ecModel](building-ec-model.md). The order of the functions is `loadProtData`, `fillEnzConcs`, `levelComplexConcs` (optional), `constrainEnzConcs`, and optionally `zeroUnmeasuredIsozymes`.

Constraining individual enzyme concentrations usually overconstrains the ecModel, because the uncertainty comes from two sources at once: the enzyme levels and the $k_{cat}$ values. Proteomics data need to be of high quality, with low-certainty measurements discarded, or the ecModel does not reach its intended growth rate.

The data are prepared before loading:

- Protein concentrations are in milligram per gram dry cell weight (mg/gDCW); relative proteomics cannot supply this unit (see the warning in [Apply the concentrations as bounds](#apply-the-concentrations-as-bounds)).
- `data/proteomics.tsv` holds the UniProt identifier in the first column and one column per replicate after it, for one or more experimental conditions.
- Low-certainty measurements are filtered out: low concentrations, proteins with a high relative standard deviation across replicates, and proteins absent from most replicates.

:::{admonition} Absolute quantitative data is not the sole option
:class: tip

Proteomics measurements are not always performed with external standards for absolute quantification. Label-free mass spectrometry needs neither external standards nor stable isotope labelling, and has been used with GECKO ecModels.
:::

## Load the proteomics data

`loadProtData` / `load_prot_data` takes the number of replicates of each condition, in the order of the columns of the file. The sum of these numbers must equal the number of replicate columns of the file; otherwise the function raises an error (`loadProtData:replicateMismatch` in MATLAB, `ValueError` in Python). It returns the mean over the replicates of each condition. An abundance of 0 is read as not measured (NaN) before any filter, also when `filterData` is false, unless `zerosAsMeasured` is true. The filtering is controlled by these parameters:

| MATLAB | Python | Default | Effect |
|---|---|---|---|
| `filterData` | `filter_data` | true | when false, the other filtering parameters are not used and the mean of the replicates is returned |
| `maxMissing` | `max_missing` | 2/3 | minimum fraction of replicates with a value above zero; a protein with fewer is discarded for that condition. A vector gives one value per condition |
| `maxRSD` | `max_rsd` | 1 | maximum relative standard deviation across replicates; a protein above it is discarded for that condition |
| `addStdevs` | `add_stdevs` | 1 | number of standard deviations added to the mean of the replicates |
| `minVal` | `min_val` | 0 | minimum value after `addStdevs`; a protein below it is discarded for that condition |
| `cutLowest` | `cut_lowest` | 5 | percentage of the lowest values per condition that is discarded |
| `zerosAsMeasured` | `zeros_as_measured` | false | whether an abundance of 0 is a measurement (see [Measured zeros](#measured-zeros-and-unmeasured-enzymes)) |

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
% one experiment with three replicates
protData = loadProtData(3);

% two experiments with three replicates each (a file with six replicate columns)
protData = loadProtData([3, 3]);
```

`loadProtData` also filters the dataset. When `protData` holds several experiments, select which one to use (experiment 1 here):

```matlab
ecModel = fillEnzConcs(ecModel, protData, 1);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fill_enz_concs, load_prot_data

# one experiment with three replicates, as a one-element list
prot_data = load_prot_data(
    params.path / "data" / "proteomics.tsv", repl_per_cond=[3],
)

# two experiments with three replicates each: repl_per_cond=[3, 3]
```

`data_col` selects which experiment to use, 0-indexed (MATLAB's experiment index is 1-indexed), so the first experiment is `data_col=0`:

```python
fill_enz_concs(ec_model, prot_data, data_col=0)
```
:::
::::

`fillEnzConcs` / `fill_enz_concs` replaces `ec.concs` with the concentrations of the selected experiment. An enzyme without a measurement has `NaN`. A negative abundance of an enzyme of the model raises the error `fillEnzConcs:negativeAbundance` in MATLAB and a `ValueError` in Python. In Python, a `data_col` outside the columns of the abundances raises an `IndexError`.

### Measured zeros and unmeasured enzymes

`ec.concs` distinguishes two cases of an enzyme without a positive concentration:

- **NaN:** the enzyme is not measured. Its usage reaction draws from the protein pool without a bound of its own.
- **0:** the enzyme was measured as absent. `constrainEnzConcs` sets the upper bound of its usage reaction to 0, which removes every flux through the enzyme.

Proteomics reports a protein below the detection limit as 0 or as missing, so a 0 is not always an absent protein. By default (`zerosAsMeasured` false), `loadProtData` reads every 0 as NaN: the mean of a protein over its replicates leaves the zeros out, and a protein whose replicates are all 0 is removed. With `zerosAsMeasured` true, a 0 counts as a measured replicate and is kept in the mean. A protein whose replicates are all 0 is returned as 0, and neither `minVal` nor `cutLowest` removes it. A measured 0 constrains the model more than an unmeasured enzyme does and can lower the growth rate or make the model infeasible. `levelComplexConcs` keeps a subunit with a concentration of 0 at 0.

An enzyme with a concentration of 0 is not raised by `flexibilizeEnzConcs`, because the bound is raised as a factor of the concentration (see [Relaxing overconstrained proteomics](relaxing-constraints.md)).

## Level the concentrations of complexes

Absolute proteomics recovers the subunits of a complex unevenly, so the subunits of one complex can disagree several fold about the amount of it that is present. When each subunit is capped by its own measurement, the complex carries no more flux than its least abundant subunit allows. `levelComplexConcs` / `level_complex_concs` gives each complex one abundance. It runs after `fillEnzConcs` and before `constrainEnzConcs`.

`getComplexFamilies` / `complex_families` groups the enzymes of the multi-subunit reactions (`ec.rxnEnzMat`, Python: `ec.rxn_enz_mat`) into complexes. Two enzyme sets are one complex when they share at least `minShared` subunits (default 2) and at least a fraction `minOverlap` (default 0.5) of the larger set (Python: `min_shared`, `min_overlap`). A subunit that appears in two complexes belongs to the complex whose enzyme sets catalyse more reactions. A subunit in three or more complexes, in two complexes of equal weight, or that also catalyses a reaction on its own is shared and stays as measured.

The concentrations (mg/gDCW) are converted to molar amounts with `ec.mw`. Per complex, the median (default) of the molar amount divided by the copies of the subunit, over the measured subunits that belong to the complex, is written back to every such subunit, multiplied by its copies and its molecular weight. The option `statistic` selects `'median'` or `'mean'`. With `fillMissing` true (default; Python: `fill_missing`), subunits of the complex without a measurement receive the concentration of the complex, and are constrained by `constrainEnzConcs` afterwards.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, levelResult] = levelComplexConcs(ecModel);
```

`levelResult` has the fields `adjusted` (measured subunits whose concentration was replaced), `added` (unmeasured subunits that received the concentration of the complex), `shared` (measured subunits left as measured) and `skipped` (complexes without a measured subunit that belongs to them). The option `families` takes the output of `getComplexFamilies`, to reuse a grouping with other parameters.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import level_complex_concs

level_result = level_complex_concs(ec_model)
```

`level_complex_concs` changes `ec_model.ec.concs` in place and returns a `LevelComplexResult` with `adjusted`, `added`, `shared` and `skipped` (a list of tuples of subunits, one per complex).
:::
::::

A model with levelled complexes is relaxed with the option `perComplex` of `flexibilizeEnzConcs` (see [Relaxing overconstrained proteomics](relaxing-constraints.md)).

## Apply the concentrations as bounds

Each `usage_prot_<id>` reaction of an enzyme with a measured concentration receives that concentration as its upper bound. Every usage reaction keeps drawing from the protein pool, with or without a bound. A concentration of 0 gives an upper bound of 0 (see [Measured zeros](#measured-zeros-and-unmeasured-enzymes)), and an enzyme with a NaN concentration keeps the default upper bound.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = constrainEnzConcs(ecModel);
```

A negative concentration in `ec.concs` raises the error `constrainEnzConcs:negativeConcentration`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import constrain_enz_concs

constrain_enz_concs(ec_model)
```

Raises `ValueError` on a light ecModel: light ecModels have no `usage_prot_*` reactions to constrain. A negative concentration also raises `ValueError`.
:::
::::

:::{warning}
Enzyme concentrations must be in mg/gDCW. Relative proteomics data loaded with the wrong units produces an ecModel with nonsensical constraints and raises no error.
:::

## Limit unmeasured isozymes

A reaction with several isozymes can have a measured isozyme and an unmeasured one. The unmeasured isozyme then draws from the protein pool without a bound, although the reaction is already catalysed by the measured one. `getIsozymeCoverage` / `get_isozyme_coverage` lists these reactions without changing the ecModel. The entries of `ec.rxns` that share an identifier once the suffix `_EXP_<n>` is removed are the isozymes of one reaction. An entry is measured when one of its enzymes has a concentration above 0, and unmeasured when all its enzymes are NaN; the kcat is not considered. An enzyme of an unmeasured entry that also catalyses an entry outside the unmeasured entries of partially covered reactions is listed as shared and is not changed.

`zeroUnmeasuredIsozymes` / `zero_unmeasured_isozymes` lowers the upper bound of the `usage_prot_<id>` reaction of the other enzymes of the unmeasured entries. It runs after `constrainEnzConcs`, which resets the bounds, and no other function calls it. It does not change `ec.concs` and never raises a bound. The `method` is `'zero'` (Python: `"zero"`, default), which sets the bound to 0, or `'detectionLimit'` (Python: `"detection_limit"`), which sets it to `limit` in mg/gDCW (default: the smallest concentration above 0 in `ec.concs`). A protein below the detection limit is missing from the data as well as an absent protein, so `'zero'` can remove a flux that exists and lower the growth rate. An enzyme that was lowered is a candidate for `relaxProteomicsGreedy` like any enzyme with a bound below the default.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[coverage, zeroable] = getIsozymeCoverage(ecModel);
[ecModel, changed] = zeroUnmeasuredIsozymes(ecModel, 'method', 'detectionLimit');
```

`coverage` is a table with one row per partially covered reaction and the variables `rxn`, `nEntries`, `nMeasured`, `nUnmeasured`, `measuredEnzymes`, `unmeasuredEnzymes` and `sharedEnzymes`. `zeroable` holds the enzymes that `zeroUnmeasuredIsozymes` acts on. `changed` is a table with one row per enzyme and the variables `uniprot` and `newUpperBound`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import get_isozyme_coverage, zero_unmeasured_isozymes

coverage, zeroable = get_isozyme_coverage(ec_model)
changed = zero_unmeasured_isozymes(ec_model, method="detection_limit")
```

`coverage` is a `DataFrame` with the columns `rxn`, `n_entries`, `n_measured`, `n_unmeasured`, `measured_enzymes`, `unmeasured_enzymes` and `shared_enzymes`, and `zeroable` is a list of enzymes. `zero_unmeasured_isozymes` lowers the bounds of `ec_model` in place and returns a `DataFrame` with the columns `uniprot` and `new_upper_bound`. Both functions raise `NotImplementedError` on a light ecModel.
:::
::::

## Set the protein pool from the proteomics data

A proteomics experiment may reflect a physiology different from the default assumption. The pool size is recomputed from a sample-specific total protein content (for example 0.5 g/gDCW) in place of the adapter default `Ptot` (Python: `p_tot`), and from the f-factor of the proteomics data, the fraction of the measured protein mass that is accounted for by enzymes of the model. With several experiments in `protData`, `calculateFfactor` averages the abundance of each protein over the experiments in which it is measured. `updateProtPool` is a function of GECKO 4 that raises an error when a usage reaction with an upper bound other than 1000 draws from the protein pool, which is the case for every ecModel with concentration-bounded usage reactions from GECKO 3.2 on; `setProtPoolSize` sizes the pool for such ecModels.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
f = calculateFfactor(ecModel, 'protData', protData);
ecModel = setProtPoolSize(ecModel, 'Ptot', 0.5, 'f', f);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import calculate_f_factor, set_prot_pool_size

f = calculate_f_factor(ec_model, prot_data)
set_prot_pool_size(ec_model, p_tot=0.5, f=f)
```
:::
::::

## Constrain with experimentally measured exchange fluxes

Because the integrated enzyme concentrations come from one particular experiment, any exchange reaction for which that experiment has measured data, such as glucose uptake, ethanol production or CO2 exchange rate, is constrained too. `data/fluxData.tsv` can hold multiple experiments and as many reaction fluxes as needed; a flux of zero blocks the corresponding exchange reaction, and a flux of -1000 or 1000 leaves uptake or excretion unconstrained. Load it:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
fluxData = loadFluxData();
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import load_flux_data

flux_data = load_flux_data(params.path / "data" / "fluxData.tsv")
```
:::
::::

Two choices determine how the constraint is applied:

1. **Loose or strict.** With loose constraints, the measured rate is set as the upper bound and the lower bound stays at zero (for a reaction with a negative rate, the lower bound gets the measured value and the upper bound stays at zero). With strict constraints, a percentage between 0 and 100 is passed in place of `'loose'` (Python: a number), and the lower and upper bounds are both set around the measured value; 10 gives 95 % and 105 % of it. Strict constraints force the ecModel to follow the measured fluxes closely, but imprecision in either the fluxes or the enzyme concentrations can then make the model infeasible; if that happens, loosen the constraint.
2. **Max or min growth.** With `max`, the measured growth rate is the upper bound, the ceiling the ecModel should reach; this suits growth as the objective function. With `min`, the measured growth rate is the lower bound, the floor the ecModel must reach; this suits minimising protein pool usage as the objective (see [Simulation and analysis](simulation-and-analysis.md)).

Loose constraints for the metabolic exchange fluxes and `max` for growth make the ecModel least likely to be overconstrained. The following applies the data of the first experiment and solves:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = constrainFluxData(ecModel, fluxData, 1, 'max', 'loose');
sol = solveLP(ecModel);
fprintf('Growth rate that is reached: %f /hour\n', abs(sol.f))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints

apply_flux_data_constraints(
    ec_model, flux_data,
    condition=0, max_min_growth="max", loose_strict_flux="loose",
)
sol = ec_model.optimize()
print(f"Growth rate that is reached: {sol.objective_value:.4f} /hour")
```

`condition` is 0-indexed (MATLAB's experiment index is 1-indexed), so the first experiment is `condition=0`.
:::
::::

With `max` and loose constraints, FBA reaches a solution unless too many exchange fluxes were pinned to zero. If the reachable growth rate falls short of the intended one, the enzyme levels are overconstrained; relax them with the functions of [Relaxing overconstrained proteomics](relaxing-constraints.md). Applying the same flux constraints to the conventional GEM, with no enzyme constraints, shows which part is overconstrained: if the conventional GEM also falls short of the intended growth rate, the exchange flux data are the limit.

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| `loadProtData:replicateMismatch` (Python: `ValueError` from `load_prot_data`) | the sum of `replPerCond` differs from the number of replicate columns of the file | Correct `replPerCond` (Python: `repl_per_cond`) |
| `updateProtPool` raises an error | a usage reaction with an upper bound other than 1000 draws from the protein pool, as in every ecModel with concentration-bounded usage reactions | Calculate the f-factor and call `setProtPoolSize` |
| The growth rate that is reached is below the intended one | the enzyme levels, the $k_{cat}$ values or the exchange flux data are overconstrained | Relax the enzyme concentrations (see [Relaxing overconstrained proteomics](relaxing-constraints.md)), or loosen the flux constraints |
| `calculate_f_factor` returns 0 with a warning | none of the UniProt identifiers of the proteomics data matches an enzyme of the model | Use the same identifier namespace in `proteomics.tsv` and `ec.enzymes` |
| A complex is still limited by one subunit | the subunit is shared between complexes or catalyses a reaction on its own, and stays as measured | Check the `shared` field of the result of `levelComplexConcs` |
| The growth rate drops or the ecModel is infeasible after `constrainEnzConcs` | enzymes with a concentration of 0 (`zerosAsMeasured` true) or unmeasured isozymes limited to 0 (`zeroUnmeasuredIsozymes` with `'zero'`) have an upper bound of 0 | Load with `zerosAsMeasured` false, use `'detectionLimit'`, or relax with `relaxProteomicsGreedy` |
| A protein with a replicate of 0 is missing from `protData` or has a higher mean than in the file | the 0 is read as not measured by default | Set `zerosAsMeasured` (Python: `zeros_as_measured`) to true when the 0 is a measurement |
| `ValueError` from `constrain_enz_concs` | the ecModel is a light ecModel, or `ec.concs` has a negative value | Use a full ecModel; correct the proteomics data |

## See also

- [Relaxing overconstrained proteomics](relaxing-constraints.md), for an ecModel that cannot reach its intended growth rate after constraining.
- [GECKO light and full ecModels](gecko-light.md), why light ecModels cannot take proteomics data.
- [Simulation and analysis](simulation-and-analysis.md), the choice between maximising growth and minimising protein pool usage as the objective.
- [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md), for the changes in `loadProtData` and `calculateFfactor`.
