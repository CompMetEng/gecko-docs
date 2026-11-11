# Tune kcats against experimental data

The advanced kcat tuning fits many kcats at once to maximum growth rates and exchange fluxes, measured in one or more conditions. It searches with CMA-ES (covariance matrix adaptation evolution strategy), and the trust in the source of each kcat limits how far the kcat moves. At the end of this page you have prepared the data files, configured the tuning, ranked the kcats by their effect on the fit, reviewed the assignment of the top kcats, and tuned the ecModel. [Choose a kcat tuning](kcat-tuning.md) compares this tuning with the standard tuning.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `loadEvotuneData` | `load_evotune_data` | reads the three data files; the tuning functions call it when no data are given |
| `screenKcatLeverage` | `screen_kcat_leverage` | ranks the kcats by their effect on the fit, without tuning |
| `selectTunableMask` | `select_tunable_mask` | selects the top kcats of the screen for the search |
| `reviewKcatAssignment` | `review_assignment` | flags kcat assignments that may be wrong, independent of the data |
| `ecStatsFromBrenda` | `ec_stats_from_brenda` | summarizes the BRENDA data per EC number for the review |
| `cmaesKcatTuning` | `cmaes_kcat_tuning` | searches the selected kcats for the best fit to the data |
| `tunePriorPenaltyWeight` | `tune_prior_penalty_weight` | runs the tuning for several `prior_penalty_weight` values and seeds, and reports fit and reproducibility |

## Setup

- An ecModel with assigned kcats (see [Choose the kcat sources](kcat-sources.md)) and a set protein pool (see [Set the protein pool](protein-pool.md)), in a project with `model_adapter.toml`.
- At least one of the files `evotuneMaxGrowth.tsv` and `evotuneFluxData.tsv` in the `data` folder of the project. The tutorial `full_ecModel` of GECKO has all three data files in its `data` folder.
- MATLAB: `nProc` above 1 needs the Parallel Computing Toolbox. `cmaesKcatTuning` has its own CMA-ES. Python: geckopy installs the CMA-ES package `cma`.

## Prepare the data files

`loadEvotuneData` reads three tab-separated files from `<project>/data/`. A missing file is skipped.

| File | Contents |
| --- | --- |
| `evotuneMaxGrowth.tsv` | maximum growth rates, one row per condition |
| `evotuneFluxData.tsv` | growth rates and exchange fluxes, one row per condition |
| `evotuneZeroExch.tsv` | reactions that carry no flux in any condition of `evotuneFluxData.tsv` |

The first two files have the layout of the flux data file that `loadFluxData` reads:

```text
Condition	Ptot	grRate	glucose (r_1714)	fructose (r_1709)	oxygen (r_1992)	ethanol (r_1761)	evotuneRMSEweight	source
glucose	NaN	0.41	-1000	NaN	NaN	NaN	1	reference
fructose	NaN	0.338	NaN	-1000	NaN	NaN	1	reference
```

| Column | Meaning |
| --- | --- |
| 1 (`Condition`) | the carbon source of the row. It must equal the metabolite name of one exchange column, for example `glucose` for `glucose (r_1714)` |
| 2 (`Ptot`) | total protein content in g/gDCW, or `NaN`. A value other than `NaN` or 0 changes the protein content of the biomass for that condition (see [Conditions that change the model](#conditions-that-change-the-model)) |
| 3 (`grRate`) | measured growth rate in 1/h |
| `<metabolite> (<reaction id>)` | measured exchange flux in mmol/gDCW/h, or `NaN` when it was not measured. A column `oxygen` with the value 0 makes the condition anaerobic |
| `evotuneRMSEweight` | optional; the RMSE of the row is multiplied by this weight |
| `source` | optional; free text, not used in the fit |

Each row is simulated with the uptake of its own carbon source open and the uptake of the carbon sources of the other rows of the same file closed (lower bound 0):

- In `evotuneMaxGrowth.tsv`, the uptake of the carbon source of the row is set to -1000, and only the growth rate is compared. The value in the carbon source column is not read.
- In `evotuneFluxData.tsv`, the lower bound of the carbon source uptake is set to the measured value. The growth rate and every exchange flux that is not `NaN` are compared, and so is every reaction of `evotuneZeroExch.tsv` that carries flux in the simulation.

Fluxes are compared in carbon units: each flux is multiplied by the number of carbon atoms of the exchanged metabolite (1 for a metabolite without carbon), and the growth rate by 41 Cmmol/gDCW. A row whose simulation is infeasible has an RMSE of 99. The RMSE of a file is the mean over its rows, and the RMSE of the fit is `(rmse_flux + w * rmse_max_growth) / (w + 1)`, with `w` the setting `max_growth_weight`.

`evotuneZeroExch.tsv` has the header `Rxns` and one reaction ID per line.

## Configure the tuning

The settings are in the `[evotune]` table of `model_adapter.toml`. Every setting has a default (see [Model adapter parameters](model-adapter-parameters.md#kcat-tuning)). The template of `createGECKOproject` writes these values:

```toml
[evotune]
sigma0_log_default = 0.5
max_growth_weight = 1.0
prior_penalty_weight = 0.03
tie_isozymes = true
rmse_threshold = 0.2
max_generations = 150

[evotune.source_groups.dlkcat]
sources = ["dlkcat"]

[evotune.source_groups.brenda]
sources = ["brenda"]

[evotune.source_groups.custom]
sources = ["custom"]

[evotune.sigma0_log_source]
dlkcat = 0.4
brenda = 0.2
custom = 0.1
```

| Setting (MATLAB field) | Meaning |
| --- | --- |
| `source_groups` (`kcatSources`) | trust groups. A kcat belongs to a group when its `ec.source`, or the part of `ec.source` before ` (`, equals one of the `sources` of the group, without regard to case. `brenda (wc=0, origin=1)` is in the group that lists `brenda`, and `combined (sd=0.10, n=2)` in the group that lists `combined`. With `match_okp = true`, a group also covers the method of `[okp] method` |
| `sigma0_log_source` (`sigma0logSource`) | standard deviation in log space for each group; the keys must be the group names. A smaller value is more trust: the search moves such a kcat less, and the screen ranks it lower |
| `sigma0_log_default` (`sigma0logDefault`) | standard deviation for a kcat whose source is in no group |
| `max_growth_weight` (`maxGrowthWeight`) | weight `w` of the maximum growth rates against the fluxes in the RMSE |
| `prior_penalty_weight` (`priorPenaltyWeight`) | weight `p` of a penalty for moving kcats; the search minimizes `rmse + p * mean(((log k - log k0) / sigma0_log)^2)`. At 0 the search minimizes the RMSE only |
| `tie_isozymes` (`tieIsozymes`) | isozyme copies of one reaction with the same kcat and the same group get one shared kcat |
| `rmse_threshold` (`rmseThreshold`) | the search stops when the best RMSE reaches this value; a negative value never stops the search early |
| `max_generations` (`maxGenerations`) | maximum number of CMA-ES generations |

The groups depend on the source labels in the model. With the default kcat assignment, `ec.source` also holds labels such as `ec_tree`, `combined (...)` and `standard`, which the template groups do not list, so these kcats take `sigma0_log_default`. List the labels of `ec.source` (`unique(ecModel.ec.source)`, Python `set(ec_model.ec.source)`) and add a group for each label that needs its own trust. When a label matches several groups, the last group applies in MATLAB and the first in Python.

## Rank the kcats by their effect

`screenKcatLeverage` multiplies and divides each kcat (or each group of tied isozyme copies) by `fold` (default 2) and records the largest change of the RMSE, the leverage. The rows are sorted by leverage multiplied by the `sigma0_log` of the kcat. The screen runs one simulation per condition for each of these probes and one baseline, so on a genome-scale model it takes about as long as a tuning run.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ModelAdapterManager.setDefault('path/to/project');
ecModel = loadEcModel();

screen = screenKcatLeverage(ecModel, 'nProc', 8);
removevars(screen(1:20, :), 'positions')
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ModelAdapter, load_ec_model
from geckopy.kcat_tuning.evotune import screen_kcat_leverage

adapter = ModelAdapter.from_folder("path/to/project")
ec_model = load_ec_model(adapter=adapter)  # models/ecModel.yml

screen = screen_kcat_leverage(ec_model, n_proc=8)
screen.drop(columns="_positions").head(20)
```
:::
::::

The screen has one row per kcat or tied group: `rxnId` (Python `rxn_id`), `nIsozymes`, `sourceGroup`, `kcat0`, `leverage`, `sigma0log`, `rank` (leverage times `sigma0log`) and `cumLeverageShare`, the sum of `rank` from the first row to this row as a fraction of the total. The column `positions` (Python `_positions`) holds the indices into `ec.rxns` of each row.

## Review the assignments of the top kcats

`reviewKcatAssignment` checks each kcat for these problems: no kcat rows in BRENDA for its EC number (`no-ec-evidence`), the same value in 5 or more reactions (`repeated-value`), the maximum of an EC number that is more than 3 times its median (`ec-maximum`), a value outside 0.01 to 10000 per s (`magnitude`), and a custom value that equals a BRENDA value of its EC number (`custom-duplicate`). The checks that need BRENDA statistics are skipped without `ecStats`. With the leverage of the screen the findings are sorted by leverage, and `coverage` or `top` shortens the list. A wrong kcat is corrected in its source (see [Choose the kcat sources](kcat-sources.md) and [Set custom kcats](custom-kcats.md)), so that the correction is in every model built from the same files.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[KCATcell, SAcell] = loadBRENDAdata('kcatAggregation', 'max');
KCATmedianCell = loadBRENDAdata('kcatAggregation', 'median');
ecStats = ecStatsFromBrenda(KCATcell, SAcell, KCATmedianCell);

leverage = zeros(numel(ecModel.ec.rxns), 1);
for i = 1:height(screen)
    leverage(screen.positions{i}) = screen.leverage(i);
end
findings = reviewKcatAssignment(ecModel.ec.rxns, ecModel.ec.kcat, ...
    ecModel.ec.source, ecModel.ec.eccodes, 'ecStats', ecStats, ...
    'leverage', leverage, 'coverage', 0.9);
writetable(findings, 'findings.tsv', 'FileType', 'text', 'Delimiter', '\t')
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import numpy as np
from geckopy import ec_stats_from_brenda, load_brenda_data, review_assignment
from geckopy.gather_kcats.review import findings_tsv

ec_stats = ec_stats_from_brenda(load_brenda_data(adapter.get_brenda_db_folder()))

leverage = np.zeros(len(ec_model.ec.rxns))
for _, row in screen.iterrows():
    leverage[list(row["_positions"])] = row["leverage"]
findings = review_assignment(
    ec_model.ec.rxns, ec_model.ec.kcat, ec_model.ec.source, ec_model.ec.eccodes,
    ec_stats=ec_stats, leverage=leverage, coverage=0.9,
)
open("findings.tsv", "w").write(findings_tsv(findings))
```
:::
::::

Each finding has the reaction, its EC number, source, kcat and leverage, the number of isozyme copies, the number of other reactions that share an enzyme (with the option `enzymes`), the names of the checks and a `detail` in words. Tied isozyme copies are reported once. Kcats with the source `standard` are reported only when `include` lists `standard-fallback`, and the check `tied-isozymes` is added only when `include` lists it.

## Tune

`cmaesKcatTuning` uses `selectTunableMask` to select the kcats to search: the top rows of the screen, up to the first row at which `cumLeverageShare` reaches `targetImpactShare` (default 0.9). With `screen` the function uses that screen; without it, the function runs a new screen. `tunableMask` (Python `tunable_mask`) gives the set of kcats directly and is used instead of the screen.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, result] = cmaesKcatTuning(ecModel, 'screen', screen, ...
    'nProc', 8, 'seed', 0);
saveEcModel(ecModel, 'ecModel_tuned.yml');
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import save_ec_model
from geckopy.kcat_tuning.evotune import cmaes_kcat_tuning

result = cmaes_kcat_tuning(ec_model, screen=screen, n_proc=8, seed=0)
save_ec_model(ec_model, "ecModel_tuned.yml", adapter=adapter)
```
:::
::::

Each candidate kcat lies between `min(0.01, k0/100)` and `max(10000, 100*k0)` per s, where `k0` is the kcat before tuning. After the run, the selected kcats hold the values of the best candidate, and their enzyme constraints are applied. Python changes `ec_model` in place. `popsize` sets the number of candidates per generation (default `4 + floor(3*log(n))` for `n` free kcats). In Python, the search can also stop earlier on a convergence criterion of the `cma` package, such as `tolx`.

### Conditions that change the model

A data row with oxygen uptake 0 or with a value of `Ptot` needs a function that changes the model. MATLAB runs the functions named by `make_model_anaerobic` and `change_protein_biomass` in the `[matlab]` table of `model_adapter.toml` (see [Model adapter parameters](model-adapter-parameters.md#matlab-functions)). Python takes the functions as the arguments `make_anaerobic(model)` and `change_protein_biomass(model, ptot)`; `tutorials/full_ecModel/code/anaerobic.py` in the geckopy repository has an example. Without a function, the condition is simulated without the change.

## Seeds, reproducibility and parallel runs

`seed` makes a run reproducible. MATLAB and Python have different CMA-ES implementations, so the same seed gives different results in the two toolboxes. In Python, a run with `n_proc` above 1 gives the same result as a run with `n_proc=1` and the same seed. `nProc` has the default 1 in MATLAB; `n_proc` has the default `cobra.Configuration().processes` in Python.

Different kcat vectors can fit the data equally well, so two seeds can move a kcat in different directions. Run the tuning with a second seed and compare the large changes (above two-fold): they should be in the same direction and of similar size. If they are not, increase `prior_penalty_weight`. `tunePriorPenaltyWeight` (Python `tune_prior_penalty_weight`) runs the tuning for each value of `candidates` (default 0, 0.01, 0.03 and 0.1) and each of `seeds` (default 0 and 1), on the same set of kcats, and reports per value the fit, the number of changed kcats and the agreement between seeds. It costs one tuning run per value and seed, and the model is not changed.

## Read the result

`result` (Python `EvotuneResult`) has these fields:

| MATLAB | Python | Meaning |
| --- | --- | --- |
| `rxns`, `oldKcat`, `newKcat`, `groups` | `rxns`, `old_kcat`, `new_kcat`, `groups` | the selected kcats before and after tuning, and the trust group of each; tied copies share one value |
| `rmseTrace`, `objectiveTrace` | `rmse_trace`, `objective_trace` | the best RMSE and the best value of the minimized objective, per generation; the two are equal when `prior_penalty_weight` is 0 |
| `nGenerations` | `n_generations` | number of generations that ran |
| `converged` | `converged` | whether the best RMSE reached `rmse_threshold` |

`nChanged` (Python `n_changed`) counts the kcats that differ from their value before tuning by more than 2 %. `parsimonyFrontier` (Python `parsimony_frontier`) sets each kcat that moved less than a threshold, in units of its `sigma0_log`, back to the value before tuning, and scores the result for a series of thresholds with a scoring function that the caller gives. `bestParsimonious` (Python `best_parsimonious`) returns the point with the fewest changed kcats whose RMSE is within 2 % of the best RMSE. In Python, `result.corrections(leverage=...)` returns one row per changed kcat, sorted by the leverage of the screen; `corrections_tsv` in `geckopy.kcat_tuning` writes the rows as TSV. As with the standard tuning, check the large changes against the source of each kcat (see [Choose a kcat tuning](kcat-tuning.md#check-a-tuned-kcat-against-its-source)), and keep curated values in `data/kcats/custom.tsv`.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| `ValueError` that `evotune_data` has neither `flux_data` nor `max_grate` (Python) | Neither `evotuneFluxData.tsv` nor `evotuneMaxGrowth.tsv` is in `<project>/data/` | Add one of the files |
| Error that a carbon source cannot be matched by name with an exchange reaction | The `Condition` of a row is not the metabolite name of an exchange column | Use the metabolite name of the column header as the condition |
| Error `No tunable kcats` | No kcat is above 0, or the mask excludes every kcat | Assign kcats first, or widen the mask |
| Error `Only 1 free parameter(s) after masking and tying` | The mask and the isozyme tying leave fewer than two free kcats | Raise `targetImpactShare`, or give a wider `tunableMask` |
| Error that the keys of `sigma0_log_source` must be the group names of `source_groups` | A group has no width, or a width has no group | Give each group one value in `[evotune.sigma0_log_source]` |
| Most kcats take `sigma0_log_default` | The `sources` of the groups do not match the labels in `ec.source` | List the labels that occur in `ec.source` in `source_groups` |
| The large changes differ in direction between seeds | Several kcat vectors fit the data equally well | Increase `prior_penalty_weight`, and compare values with `tunePriorPenaltyWeight` |

## See also

- [Choose a kcat tuning](kcat-tuning.md), the standard tuning and the check of a tuned kcat.
- [Files in the data folder](data-folder-files.md), every file of the `data` folder.
- [Model adapter parameters](model-adapter-parameters.md#kcat-tuning), the `[evotune]` settings in both toolboxes.
- [API reference](../api/index.md), every function in both toolboxes.
