# Experimental data

<!-- docs-site: concept-page -->

Measured growth rates and exchange fluxes of growth conditions constrain an ecModel and test it. A project keeps them in three files of the `data` folder: `fluxData.tsv` with the flux conditions, `maxGrowth.tsv` with the maximum-growth conditions and `zeroFlux.tsv` with the reactions that carry no flux. In a **flux condition** the uptake of the carbon source is limited to its measured rate, and the growth rate and the measured exchange fluxes of the model are compared with the measurements. In a **maximum-growth condition** the uptake of the carbon source is unlimited, and only the maximal growth rate of the model is compared. GECKO (MATLAB) and geckopy (Python) read the same files. The functions that read the files, set the conditions in a model and score a model against the measurements need no enzymes, so they are part of RAVEN (MATLAB, folder `src/experiments`) and raven-toolbox (Python, package `raven_toolbox.experiments`).

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `loadFluxData` | `load_flux_data` | read one flux file into a structure (Python: `FluxData`) |
| `loadExperimentData` | `load_experiment_data` | read the three files of a folder |
| `loadEvotuneData` | `load_experiment_data` | read the three files of the `data` folder of the model adapter; Python takes the folder, `params.path / "data"` |
| `constrainFluxData` | `apply_flux_data_constraints` | constrain the exchange reactions and the growth rate of a model with one condition |
| `simulateConditions` | `simulate_conditions` | simulate the flux conditions or the maximum-growth conditions of one file in a model |
| `computeCarbonWeights` | `compute_carbon_weights` | weight of each exchange reaction in the score |
| `datasetRmse`, `experimentDistance` | `dataset_rmse`, `experiment_distance` | distance between the simulation and the measurements, for one kind of condition and for both kinds combined |

`constrainFluxData` and `apply_flux_data_constraints` take the biomass reaction and the preferred carbon source from the model adapter and pass them on to RAVEN's `applyFluxDataConstraints` and raven-toolbox's `apply_flux_data_constraints`. The tuning functions of [Tune *k*{sub}`cat` values with evotune](evotune.md) call the loaders and the scoring functions.

## Files

The files are read from `<project>/data/`. Each file is optional, and a missing file is skipped.

| File | Content | Used by |
| --- | --- | --- |
| `fluxData.tsv` | Flux conditions: growth rate, protein content and measured exchange fluxes of each condition, one row per condition. | the constraints of [Constrain enzymes with proteomics](proteomics.md), and the *k*{sub}`cat` tuning |
| `maxGrowth.tsv` | Maximum-growth conditions: the maximum growth rate with each carbon source, one carbon source per row, at `-1000` (unconstrained). | the *k*{sub}`cat` tuning |
| `zeroFlux.tsv` | Reaction IDs that carry no flux in any condition. The header is `Rxns` and each following line holds one reaction ID. | the *k*{sub}`cat` tuning |

## Columns of the flux files

`fluxData.tsv` and `maxGrowth.tsv` are tab-separated and share one layout:

```
Condition   Ptot   grRate   glucose (r_1714)   fructose (r_1709)   ...   weight   source
glucose     NaN    0.41     -1000              NaN                 ...   1        DLKcat
fructose    NaN    0.338    NaN                -1000               ...   1        DLKcat
```

- `Condition` names the row. In the files of the *k*{sub}`cat` tuning, the name is the name of the carbon source of the row and equals the metabolite name of one exchange column, for example `glucose` for `glucose (r_1714)`. A name that matches no exchange column raises an error, except in a row with the `weight` 0.
- `Ptot` is the measured protein content in g/gDCW, and `NaN` when it is not measured.
- `grRate` is the measured growth rate in 1/h.
- Each exchange column is headed `<metabolite> (<reaction ID>)` and holds the flux of that reaction in mmol/gDCW/h. Uptake is negative and excretion is positive. The header is split at the parenthesis that closes it, so a reaction ID may contain parentheses (`X (EX_a(e))` is the metabolite `X` and the reaction `EX_a(e)`). A flux of `-1000` or `1000` leaves uptake or excretion unconstrained, and an empty or non-numeric cell is read as `NaN`, which means not measured.
- `weight` is optional and scales the error of the row in the score of the *k*{sub}`cat` tuning. A row with the weight `0` is left out of the simulation and of the score, and its `Condition` need not match an exchange column. Without the column every row has the weight 1. A file with the column `evotuneRMSEweight` raises an error that names `weight`.
- `source` is optional free text that names where the data come from. The columns `weight` and `source` may stand in any position after `grRate`.

A row with the weight `0` can hold a condition that the tuning does not use but another step reads. The first row of `fluxData.tsv` in the `full_ecModel` tutorial is `Std`, with `Ptot` 0.4228, the growth rate 0.1 and the glucose uptake -1.1. Its weight is `0`, so the tuning leaves it out, and the protein-constraint step of the tutorial reads it as the first condition (`condition=0` in Python, `'condition',1` in MATLAB).

## Constraining a model with one condition

`constrainFluxData` (Python `apply_flux_data_constraints`) sets the growth rate and the exchange fluxes of one condition, chosen by its index or its name, as bounds. The loose setting keeps one bound at zero, and a percentage sets both bounds around the measured value. [Constrain enzymes with proteomics](proteomics.md#constrain-the-exchange-fluxes-and-the-growth-rate) shows the call and the choice of settings. The preferred carbon source of the model adapter is blocked before the data are applied, so that the data alone determine the carbon source.

## Scoring a model against all conditions

The *k*{sub}`cat` tuning simulates every row of `fluxData.tsv` and `maxGrowth.tsv` whose `weight` is not `0`.

1. For a flux condition (a row of `fluxData.tsv`), the uptake of the carbon source is fixed at the measured value. Exchange reactions that are the carbon source of some row are blocked in every other row. The growth rate and the measured exchange fluxes are compared with the simulation, and so is the flux of each reaction of `zeroFlux.tsv`, which adds a term only when its simulated flux is not zero.
2. For a maximum-growth condition (a row of `maxGrowth.tsv`), the uptake of the carbon source is opened to `-1000`, and only the growth rate is compared.
3. Each difference is multiplied by the carbon weight of its reaction: the carbon number of the exchanged metabolite, with `1` for a metabolite without carbon, without a formula or with a formula that cannot be read, and `41` for the growth rate. A formula is read as element symbols with an optional integer or decimal count (`C6H12O6`, `C2.5H5`); a charge sign and a `*` between parts of the formula are ignored, and a formula with parentheses (`C6H12O6(H2O)2`) or an unknown element symbol cannot be read. The error of a condition is the root mean square of its weighted differences, and it is `99` when the model is infeasible in that condition.
4. The error of a dataset is the mean, over its conditions with a `weight` other than `0`, of the error of each condition multiplied by its `weight`. A condition with the weight `0` is not simulated, has no error (`NaN` in the per-condition errors) and does not count in the mean. A dataset in which every condition has the weight `0` is left out of the score. The score is `(rmse_flux + w * rmse_max_growth) / (w + 1)`, where `w` is `max_growth_weight` of the `[evotune]` table.

Two steps depend on the organism and are passed as functions: an anaerobic switch, which runs for a row whose `oxygen` column is exactly `0`, and a change of the protein content, which runs for a row with a `Ptot` value. Without the function, the row is simulated without that step.

Each condition is solved by maximising the growth. The scoring of the tuning sets the biomass reaction `bioRxn` of the model adapter as the objective for the simulations, whatever objective the model has, and leaves the objective of the model as it was. The growth rate is the flux of `bioRxn` in that solution. When the experiment functions of RAVEN or raven-toolbox are called directly, the objective of the model is used as it is: a warning (`simulateConditions:objectiveNotGrowth` in MATLAB, a `UserWarning` in Python) is issued once per call when it is not the maximisation of the biomass reaction alone, and a maximum-growth condition then compares a flux that is not the maximal growth rate with the measurement.

## Examples

The tutorial `full_ecModel` has the three files in its `data` folder.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
experimentData = loadExperimentData(fullfile('tutorials', 'full_ecModel', 'data'));
fprintf('%d flux conditions, %d max-growth conditions, %d zero-flux reactions\n', ...
    numel(experimentData.fluxData.conds), numel(experimentData.maxGrowth.conds), ...
    numel(experimentData.zeroFlux))
```

Output in the `full_ecModel` tutorial:

```
34 flux conditions, 8 max-growth conditions, 219 zero-flux reactions
```

`experimentData` is a structure with the fields `fluxData`, `maxGrowth` and `zeroFlux`. The two flux structures have the fields `conds`, `Ptot`, `grRate`, `exchFluxes`, `exchMets`, `exchRxnIDs` and, when the file has the columns, `weight` and `source`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from raven_toolbox.experiments import load_experiment_data

experiment_data = load_experiment_data("tutorials/full_ecModel/data")
print(
    len(experiment_data.flux_data.conds), "flux conditions,",
    len(experiment_data.max_growth.conds), "max-growth conditions,",
    len(experiment_data.zero_flux), "zero-flux reactions",
)
```

Output in the `full_ecModel` tutorial:

```
34 flux conditions, 8 max-growth conditions, 219 zero-flux reactions
```

`experiment_data` is an `ExperimentData` with the attributes `flux_data`, `max_growth` and `zero_flux`. `flux_data` and `max_growth` are `FluxData` objects with the attributes `conds`, `p_tot`, `gr_rate`, `exch_fluxes`, `exch_mets`, `exch_rxn_ids`, `weight` and `source`.
:::
::::

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| Error that a carbon source in the provided flux data or max-growth data cannot be matched by name with an exchange reaction | The `Condition` of a row with a `weight` other than `0` is not the metabolite name of an exchange column | Rename the condition to the metabolite name of the column of its carbon source, or set its `weight` to `0` if the row is not for the tuning |
| Error that the header has fewer than three columns, or that a row has a different number of cells than the header | The file is not tab-separated, or a line is incomplete | Correct the line that the message names |
| Error `loadEvotuneData:legacyWeightColumn` from `loadEvotuneData` or the tuning functions, which names the column `weight` | `fluxData.tsv` or `maxGrowth.tsv` has the column `evotuneRMSEweight` | Rename the column to `weight` |
| Error that there are no exchange-flux columns | No column after `grRate` is headed `<metabolite> (<reaction ID>)` | Head each exchange column in that form |
| Error `evotune:noData` that the experimental data have neither flux data nor max-growth data | `fluxData.tsv` and `maxGrowth.tsv` are missing from `<project>/data/` | Add one of the files, or pass the loaded data |
| A condition scores `99` | The model is infeasible in that condition | Check the carbon source, the oxygen flux and the bounds of the measured fluxes |

## See also

- [Tune *k*{sub}`cat` values with evotune](evotune.md), the *k*{sub}`cat` tuning that scores a model against these files.
- [Constrain enzymes with proteomics](proteomics.md), where `fluxData.tsv` constrains the ecModel.
- [Files in the data folder](data-folder-files.md), every file of the `data` folder.
- [API reference](../api/index.md), every function in both toolboxes.
