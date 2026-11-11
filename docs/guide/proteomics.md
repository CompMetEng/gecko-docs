# Constrain enzymes with proteomics

Load the absolute proteomics data and the exchange fluxes of one experiment, bound the usage of each measured enzyme by its concentration, set the protein pool for the experiment, and constrain the exchange reactions and the growth rate. At the end, the ecModel describes the experiment, and solving it shows whether the ecModel reaches the measured growth rate. Proteomics data require a full ecModel, which has a usage reaction per enzyme; a light ecModel has none (see [Choose the ecModel structure](ecmodel-structure.md)).

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `loadProtData` | `load_prot_data` | reads `proteomics.tsv`, filters it and averages the replicates of each condition |
| `fillEnzConcs` | `fill_enz_concs` | writes the concentrations of one condition to `ec.concs` |
| `levelComplexConcs` | `level_complex_concs` | gives the subunits of each complex one abundance |
| `constrainEnzConcs` | `constrain_enz_concs` | sets the concentrations as upper bounds of the `usage_prot_<id>` reactions |
| `getIsozymeCoverage` | `get_isozyme_coverage` | lists the reactions with a measured and an unmeasured isozyme |
| `zeroUnmeasuredIsozymes` | `zero_unmeasured_isozymes` | lowers the usage bound of the unmeasured isozymes of these reactions |
| `calculateFfactor` | `calculate_f_factor` | calculates f from the proteomics data |
| `setProtPoolSize` | `set_prot_pool_size` | sets the upper bound of `prot_pool_exchange` to $P_{tot} \cdot f \cdot \sigma \cdot 1000$ mg/gDCW |
| `loadFluxData` | `load_flux_data` | reads `fluxData.tsv` |
| `constrainFluxData` | `apply_flux_data_constraints` | sets the bounds of the growth rate and the exchange reactions of one condition |

## Setup

A full ecModel with kcats and a protein pool (see [Build an ecModel](first-ecmodel.md)), in the variable `ecModel` (MATLAB) or `ec_model` (Python), and the files `data/proteomics.tsv` and `data/fluxData.tsv` of the project. In MATLAB, the model adapter of the project is the default adapter; in Python, the examples read the project folder from `params = ec_model.adapter.params`. The examples assume a `proteomics.tsv` with two conditions of three replicates each, and select the first condition in both files.

## Choose the options

| Choice | Options | Criteria |
| --- | --- | --- |
| Complexes | level with `levelComplexConcs`, or keep each subunit as measured | Level when the subunits of a complex are measured at different amounts. |
| Unmeasured isozymes | no bound (default), a bound at the detection limit, or a bound of 0 | A protein that is missing from the data can be absent or below the detection limit. |
| f | the value in `model_adapter.toml`, or `calculateFfactor` on the proteomics of the condition | f from the same proteomics data describes the same proteome as the concentrations. |
| Exchange fluxes | `'loose'`, or a percentage around the measured value | A percentage forces a flux through each reaction. |
| Growth rate | `'max'` or `'min'` | `'max'` suits growth as objective; `'min'` suits the minimal protein pool usage as objective. |

A complex that is bounded subunit by subunit carries no more flux than its least abundant subunit allows. Levelling uses the subunit copies in `ec.rxnEnzMat`, which come from the complex data (`applyComplexData`); without complex data, every subunit counts as one copy.

An unmeasured isozyme without a bound can carry the flux of a measured one. A bound of 0 treats the protein as absent; a bound at the detection limit treats it as present at a low amount.

The f in `model_adapter.toml` is often calculated from PaxDB data, or is the default 0.5 (see [Set the protein pool](protein-pool.md)).

`'loose'` bounds each exchange reaction between 0 and the measured value. With a percentage, an error in the fluxes or in the enzyme data can make the ecModel infeasible. `'max'` sets the measured growth rate as upper bound and `'min'` as lower bound (see [Analyse an ecModel](analysis.md) for the objectives).

Start with `'loose'` and `'max'`. The ecModel then has a solution also when the proteomics limit growth, which `flexibilizeEnzConcs` and `relaxProteomicsGreedy` need (see [Relax proteomics constraints](relaxing-proteomics.md)). With `'min'`, an ecModel that cannot reach the growth rate is infeasible.

## Prepare the data files

`data/proteomics.tsv` is tab-delimited with one header row. The first column holds the UniProt identifiers, and every following column holds one replicate, in mg/gDCW. The replicates of the first condition come first, then those of the second condition, and so on. The header must have one column more than the total number of replicates; otherwise `loadProtData` raises the error `loadProtData:replicateMismatch` (Python: `ValueError`). A cell with `NA`, `na`, `NaN`, `#VALUE!` or no value is not measured, and a row without an identifier is removed. Relative proteomics data cannot be used: a concentration in another unit gives wrong bounds and no error.

`data/fluxData.tsv` is tab-delimited with one header row and one row per condition. The columns are the condition name, the total protein content Ptot (g/gDCW), the growth rate (1/h), and then one column per exchange reaction, in mmol/gDCW/h, negative for uptake and positive for excretion. The header of an exchange column has the form `<metabolite> (<reaction id>)`. Optional columns `evotuneRMSEweight` and `source` can be at any position. A line with a different number of cells than the header raises an error. The example shows the first 7 of the 11 columns of `fluxData.tsv` in the `full_ecModel` tutorial of GECKO, which uses yeast-GEM; `r_1714` is the glucose exchange of yeast-GEM:

```text
Condition	Ptot	grRate	glucose (r_1714)	CO2 (r_1672)	oxygen (r_1992)	ethanol (r_1761)
Std	0.4228	0.1	-1.1	2.7	-2.5	1.00E-05
```

The `proteomics.tsv` of the same tutorial has one condition with three replicates, so it is loaded with `loadProtData(3)`; the `[3, 3]` of the examples below raises `loadProtData:replicateMismatch` on it. See [Files in the data folder](data-folder-files.md) for the other files of the project.

## Load the proteomics data

`loadProtData` takes the number of replicates of each condition, in the order of the columns. It returns one column per condition. With the default settings, it filters each condition in this order:

| MATLAB | Python | Default | Effect |
| --- | --- | --- | --- |
| `maxMissing` | `max_missing` | 2/3 | a protein measured in fewer than this fraction of the replicates is removed; a vector gives one value per condition |
| `maxRSD` | `max_rsd` | 1 | a protein with a higher relative standard deviation over the replicates is removed |
| `addStdevs` | `add_stdevs` | 1 | the concentration is the mean of the replicates plus this number of standard deviations |
| `minVal` | `min_val` | 0 | a protein with a lower concentration is removed |
| `cutLowest` | `cut_lowest` | 5 | this percentage of the lowest concentrations is removed |
| `filterData` | `filter_data` | true | false skips the filters above and returns the mean of the replicates |
| `zerosAsMeasured` | `zeros_as_measured` | false | whether a 0 is a measurement |

A protein that is removed is NaN for that condition, and its enzyme draws from the protein pool without a bound of its own. By default a 0 is read as not measured, because proteomics reports a protein below the detection limit as 0 or as missing. With `zerosAsMeasured` true, a 0 counts as a measured replicate, and a protein measured as 0 in every replicate keeps the concentration 0. `constrainEnzConcs` then sets the usage bound of its enzyme to 0, which removes every flux through the enzyme. Set it to true when a 0 means that the protein is absent, for example in a deletion strain.

`fillEnzConcs` writes the concentrations of one condition to `ec.concs` and sets every other enzyme to NaN. The condition index starts at 1 in MATLAB and at 0 in Python.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
% two conditions with three replicates each
protData = loadProtData([3, 3]);
ecModel  = fillEnzConcs(ecModel, protData, 'dataCol', 1);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fill_enz_concs, load_prot_data

params = ec_model.adapter.params
# two conditions with three replicates each
prot_data = load_prot_data(params.path / "data" / "proteomics.tsv", [3, 3])
fill_enz_concs(ec_model, prot_data, data_col=0)
```
:::
::::

## Level the concentrations of complexes

`levelComplexConcs` runs after `fillEnzConcs` and before `constrainEnzConcs`. It groups the enzymes of the reactions with several subunits into complexes (`getComplexFamilies`), converts the concentrations to molar amounts with `ec.mw`, and writes the median over the measured subunits, per copy, back to every subunit of the complex, multiplied by its copies. The option `statistic` selects `'median'` or `'mean'`. With `fillMissing` true (default), an unmeasured subunit of a complex receives the concentration of the complex. A subunit that belongs to more than one complex, or that also catalyses a reaction alone, keeps its measured value, and a subunit measured as 0 stays 0.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, levelResult] = levelComplexConcs(ecModel);
```

`levelResult` has the fields `adjusted` (measured subunits that received the concentration of the complex), `added` (unmeasured subunits that received it), `shared` (subunits kept as measured) and `skipped` (complexes without a measured subunit).
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import level_complex_concs

level_result = level_complex_concs(ec_model)
```

`level_complex_concs` changes `ec_model.ec.concs` and returns a `LevelComplexResult` with the attributes `adjusted`, `added`, `shared` and `skipped`.
:::
::::

An ecModel with levelled complexes is relaxed per complex (see [Relax proteomics constraints](relaxing-proteomics.md)).

## Apply the concentrations as bounds

`constrainEnzConcs` sets the upper bound of the `usage_prot_<id>` reaction of each enzyme with a concentration to that concentration, and the upper bound of each enzyme with NaN to 1000. Every usage reaction draws from the protein pool, also when it has a measured bound.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = constrainEnzConcs(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import constrain_enz_concs

constrain_enz_concs(ec_model)
```
:::
::::

The option `removeConstraints` (Python: `remove_constraints`) resets all usage bounds to 1000 and leaves `ec.concs` unchanged.

## Limit unmeasured isozymes

A reaction can have a measured isozyme and an unmeasured one. The unmeasured isozyme then draws from the protein pool without a bound, and the ecModel can use it in place of the measured one. `getIsozymeCoverage` lists these reactions and does not change the ecModel. `zeroUnmeasuredIsozymes` runs after `constrainEnzConcs`, calls `getIsozymeCoverage`, and lowers the usage bound of the enzymes of the unmeasured isozymes. The method `'zero'` (default) sets the bound to 0; `'detectionLimit'` (Python: `"detection_limit"`) sets it to `limit` in mg/gDCW, by default the smallest concentration above 0 in `ec.concs`. An enzyme that also catalyses a reaction without a measured isozyme is not changed. `ec.concs` is not changed, and no other GECKO function calls `zeroUnmeasuredIsozymes`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[coverage, zeroable] = getIsozymeCoverage(ecModel);
[ecModel, changed] = zeroUnmeasuredIsozymes(ecModel, 'method', 'detectionLimit');
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import get_isozyme_coverage, zero_unmeasured_isozymes

coverage, zeroable = get_isozyme_coverage(ec_model)
changed = zero_unmeasured_isozymes(ec_model, method="detection_limit")
```
:::
::::

`coverage` has one row per reaction, with its measured and unmeasured enzymes. `changed` has one row per enzyme with its new upper bound.

## Set the protein pool for the condition

The upper bound of the protein pool exchange is $P_{tot} \cdot f \cdot \sigma \cdot 1000$ mg/gDCW (see [Set the protein pool](protein-pool.md)). Use the Ptot of the condition from `fluxData.tsv`. `calculateFfactor` divides the summed concentrations of the enzymes of the ecModel by the summed concentrations of all proteins in the data. It uses the proteins that `loadProtData` kept, so the filters change f. To calculate f over all measured proteins of one condition, load the data without filters and select the column of the condition. With several columns, `calculateFfactor` averages each protein over the columns in which it is measured. Sigma is read from `model_adapter.toml` when it is not given.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
fluxData = loadFluxData();
protAll  = loadProtData([3, 3], 'filterData', false);
protAll.abundances = protAll.abundances(:, 1);
f = calculateFfactor(ecModel, 'protData', protAll);
ecModel = setProtPoolSize(ecModel, 'Ptot', fluxData.Ptot(1), 'f', f);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import (
    ProtData, calculate_f_factor, load_flux_data, set_prot_pool_size,
)

flux_data = load_flux_data(params.path / "data" / "fluxData.tsv")
prot_all = load_prot_data(
    params.path / "data" / "proteomics.tsv", [3, 3], filter_data=False,
)
prot_cond = ProtData(
    uniprot_ids=prot_all.uniprot_ids, abundances=prot_all.abundances[:, [0]],
)
f = calculate_f_factor(ec_model, prot_cond)
set_prot_pool_size(ec_model, p_tot=float(flux_data.p_tot[0]), f=f)
```
:::
::::

## Constrain the exchange fluxes and the growth rate

`constrainFluxData` sets the bounds of the carbon source uptake reaction of `model_adapter.toml` (`c_source`) to 0, then sets the growth rate and the exchange fluxes of the condition. The condition is an index (from 1 in MATLAB, from 0 in Python) or a name from the first column of `fluxData.tsv`. The proteomics column and the flux condition are selected separately; select the same experiment in both.

- With `'loose'`, a negative flux becomes the lower bound with an upper bound of 0, and a positive flux becomes the upper bound with a lower bound of 0. A flux of 0 blocks the reaction.
- With a percentage `p`, the bounds are the measured value × (1 ± p/200); 10 gives 95 % and 105 % of the measured value.
- A flux of -1000 allows any uptake and 1000 allows any excretion, with both options.
- An empty cell leaves the bounds of the reaction unchanged.
- An exchange reaction that is not in the ecModel raises an error.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = constrainFluxData(ecModel, 'fluxData', fluxData, 'condition', 1, ...
    'maxMinGrowth', 'max', 'looseStrictFlux', 'loose');
sol = solveLP(ecModel);
fprintf('Growth rate: %g /h, measured: %g /h\n', sol.f, fluxData.grRate(1))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints

apply_flux_data_constraints(
    ec_model, flux_data, condition=0,
    max_min_growth="max", loose_strict_flux="loose",
)
growth = ec_model.slim_optimize()
print(f"Growth rate: {growth:g} /h, measured: {flux_data.gr_rate[0]:g} /h")
```
:::
::::

With `'max'`, the growth rate cannot exceed the measured one. A growth rate below it means that the enzyme concentrations, the kcats, the protein pool or the exchange fluxes limit growth. [Relax proteomics constraints](relaxing-proteomics.md) raises the limiting enzyme bounds and shows how to find which of these limits growth.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| `loadProtData:replicateMismatch` (Python: `ValueError` from `load_prot_data`) | the replicate numbers do not add up to the number of replicate columns of `proteomics.tsv` | Correct `replPerCond` (Python: `repl_per_cond`) or the header of the file |
| `fillEnzConcs:negativeAbundance` (Python: `ValueError` from `fill_enz_concs`) | an enzyme of the ecModel has a negative concentration in the selected condition | Correct `proteomics.tsv` |
| `IndexError` from `fill_enz_concs` | `data_col` is outside the conditions of `prot_data`; it counts from 0 | Use a column index from 0 to the number of conditions minus 1 |
| `calculateFfactor` returns 0 (Python: with a warning) | the identifiers in `proteomics.tsv` do not match `ec.enzymes` | Use UniProt identifiers in `proteomics.tsv`, as in `ec.enzymes` |
| A protein with a replicate of 0 is missing or has a higher mean than expected | a 0 is read as not measured | Set `zerosAsMeasured` (Python: `zeros_as_measured`) to true if the 0 is a measurement |
| The ecModel is infeasible or grows much slower after `constrainEnzConcs` or `zeroUnmeasuredIsozymes` | enzymes with a bound of 0: measured zeros, or isozymes set to 0 | Load with `zerosAsMeasured` false, use `'detectionLimit'`, or relax with `relaxProteomicsGreedy` |
| A complex is still limited by one subunit after levelling | the subunit belongs to more than one complex or catalyses a reaction alone, and keeps its measured value | Check the field `shared` of the result of `levelComplexConcs` |
| `constrainFluxData:missingReaction` (Python: `ValueError`) | a reaction identifier in the header of `fluxData.tsv` is not in the ecModel | Correct the header to `<metabolite> (<reaction id>)` |
| `ValueError` from `constrain_enz_concs` | the ecModel is a light ecModel, or `ec.concs` has a negative value | Use a full ecModel; correct the proteomics data |
| `updateProtPool` raises an error | `updateProtPool` is deprecated and does not accept an ecModel in which measured enzymes draw from the protein pool | Use `setProtPoolSize` with the Ptot and f of the condition |

## See also

- [Relax proteomics constraints](relaxing-proteomics.md), for an ecModel that does not reach the measured growth rate.
- [Set the protein pool](protein-pool.md), for Ptot, f and sigma.
- [Analyse an ecModel](analysis.md), for the objectives that go with `'max'` and `'min'`.
- [Files in the data folder](data-folder-files.md).
