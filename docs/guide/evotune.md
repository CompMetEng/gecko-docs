# Tune kcats with evotune

Evotune is the kcat tuning of GECKO that fits many kcats at once to maximum growth rates and exchange fluxes, measured in one or more conditions, by minimising the root-mean-square error (RMSE) between simulated and measured values. It searches with CMA-ES (covariance matrix adaptation evolution strategy), and the trust in the source of each kcat limits how far the kcat moves. The steps are: prepare the data files, configure the tuning, rank the kcats by their effect on the fit, review the assignment of the top kcats, and tune. The result is an ecModel whose selected kcats fit the data, and a list of the changed kcats. The functions and settings carry the name: `loadEvotuneData`, `[evotune]` in `model_adapter.toml`, and in Python the module `geckopy.kcat_tuning.evotune`. [Choose a kcat tuning](kcat-tuning.md) compares evotune with `sensitivityTuning`, which reaches one growth rate.

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
  PV(["Previous: Choose a kcat tuning<br/>(protein pool set, sigma not fitted)"]):::ctx
  DF["prepare the data files<br/>(read by loadEvotuneData, which the tuning calls)"]
  CG["[evotune] in model_adapter.toml"]
  SC["screenKcatLeverage"]
  RV["reviewKcatAssignment<br/>ecStatsFromBrenda"]:::opt
  TP["tunePriorPenaltyWeight<br/>seeds and reproducibility"]:::opt
  CM["cmaesKcatTuning<br/>selectTunableMask on the screen"]
  PV --> DF --> CG --> SC --> CM
  SC -.-> RV -.-> CM
  SC -.-> TP -.-> CM
  NP(["Next: Constrain enzymes with proteomics (optional)"]):::ctx
  NA(["Next: Analyse an ecModel"]):::ctx
  CK(["Choose a kcat tuning:<br/>check a tuned kcat"]):::ctx
  CM -.-> CK
  CM --> NP
  CM --> NA
  click PV href "kcat-tuning.html"
  click CK href "kcat-tuning.html"
  click NP href "proteomics.html"
  click NA href "analysis.html"
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
  PV(["Previous: Choose a kcat tuning<br/>(protein pool set, sigma not fitted)"]):::ctx
  DF["prepare the data files<br/>(read by load_experiment_data, which the tuning calls)"]
  CG["[evotune] in model_adapter.toml"]
  SC["screen_kcat_leverage"]
  RV["review_assignment<br/>ec_stats_from_brenda"]:::opt
  TP["tune_prior_penalty_weight<br/>seeds and reproducibility"]:::opt
  CM["cmaes_kcat_tuning<br/>select_tunable_mask on the screen"]
  PV --> DF --> CG --> SC --> CM
  SC -.-> RV -.-> CM
  SC -.-> TP -.-> CM
  NP(["Next: Constrain enzymes with proteomics (optional)"]):::ctx
  NA(["Next: Analyse an ecModel"]):::ctx
  CK(["Choose a kcat tuning:<br/>check a tuned kcat"]):::ctx
  CM -.-> CK
  CM --> NP
  CM --> NA
  click PV href "kcat-tuning.html"
  click CK href "kcat-tuning.html"
  click NP href "proteomics.html"
  click NA href "analysis.html"
```
:::
::::
:::::

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `loadEvotuneData` | `load_experiment_data` | reads the three data files (see [Experimental data](experimental-data.md)); the tuning functions call it when no data are given |
| `screenKcatLeverage` | `screen_kcat_leverage` | ranks the kcats by their effect on the fit, without tuning |
| `selectTunableMask` | `select_tunable_mask` | selects the top kcats of the screen for the search |
| `reviewKcatAssignment` | `review_assignment` | flags kcat assignments that may be wrong, independent of the data |
| `ecStatsFromBrenda` | `ec_stats_from_brenda` | summarises the BRENDA data per EC number for the review |
| `cmaesKcatTuning` | `cmaes_kcat_tuning` | searches the selected kcats for the best fit to the data |
| `tunePriorPenaltyWeight` | `tune_prior_penalty_weight` | runs the tuning for several `prior_penalty_weight` values and seeds, and reports fit and reproducibility |

## Setup

- An ecModel with assigned kcats (see [Choose the kcat sources](kcat-sources.md)) and a set protein pool (see [Set the protein pool](protein-pool.md)), in a project with `model_adapter.toml`.
- At least one of the files `maxGrowth.tsv` and `fluxData.tsv` in the `data` folder of the project. The two files can be combined: `fluxData.tsv` holds the flux conditions, with the uptake of the carbon source limited to the measured rate, and its exchange fluxes constrain the distribution of the fluxes in a condition; `maxGrowth.tsv` holds the maximum-growth conditions, with the uptake of the carbon source unlimited, and constrains the growth rate on each carbon source. The tutorial `full_ecModel` of GECKO has all three data files in its `data` folder.
- MATLAB: `nProc` above 1 needs the Parallel Computing Toolbox. `cmaesKcatTuning` has its own CMA-ES. Python: geckopy installs the CMA-ES package `cma`.

## Prepare the data files

`loadEvotuneData` (Python `load_experiment_data`) reads three tab-separated files from `<project>/data/`. A missing file is skipped. [Experimental data](experimental-data.md) describes the files and their scoring in full.

| File | Contents |
| --- | --- |
| `maxGrowth.tsv` | maximum-growth conditions: maximum growth rates, one row per condition |
| `fluxData.tsv` | flux conditions: growth rates and exchange fluxes, one row per condition |
| `zeroFlux.tsv` | reactions that carry no flux in any condition of `fluxData.tsv` |

The first two files have the layout of the flux data file that `loadFluxData` reads:

```text
Condition	Ptot	grRate	glucose (r_1714)	fructose (r_1709)	oxygen (r_1992)	ethanol (r_1761)	weight	source
glucose	NaN	0.41	-1000	NaN	NaN	NaN	1	reference
fructose	NaN	0.338	NaN	-1000	NaN	NaN	1	reference
```

| Column | Meaning |
| --- | --- |
| 1 (`Condition`) | the carbon source of the row. It must equal the metabolite name of one exchange column, for example `glucose` for `glucose (r_1714)` |
| 2 (`Ptot`) | total protein content in g/gDCW, or `NaN`. A value other than `NaN` or 0 changes the protein content of the biomass for that condition (see [Conditions that change the model](#conditions-that-change-the-model)) |
| 3 (`grRate`) | measured growth rate in 1/h |
| `<metabolite> (<reaction id>)` | measured exchange flux in mmol/gDCW/h, or `NaN` when it was not measured. A column `oxygen` with the value 0 makes the condition anaerobic |
| `weight` | optional; the error of the row is multiplied by this weight, so that a row of lower quality counts less. A row with the weight 0 is left out of the simulation and of the score; without the column every row has the weight 1 |
| `source` | optional; free text, not used in the fit |

Each row is simulated with the uptake of its own carbon source open and the uptake of the carbon sources of the other rows of the same file closed (lower bound 0):

- In `maxGrowth.tsv`, the uptake of the carbon source of the row is set to -1000, and the growth rate is the sole compared value. The value in the carbon source column is not read.
- In `fluxData.tsv`, the lower bound of the carbon source uptake is set to the measured value. The growth rate and every exchange flux that is not `NaN` are compared, and so is every reaction of `zeroFlux.tsv` that carries flux in the simulation.

Fluxes are compared in carbon units: each flux is multiplied by the number of carbon atoms of the exchanged metabolite (1 for a metabolite without carbon), and the growth rate by 41 Cmmol/gDCW. A row whose simulation is infeasible has an RMSE of 99. The RMSE of a file is the mean over its rows with a weight other than 0, each multiplied by its weight, and the RMSE of the fit is `(rmse_flux + w * rmse_max_growth) / (w + 1)`, with `w` the setting `max_growth_weight`.

The conditions are simulated by maximising the growth reaction `bioRxn` of the model adapter, whatever objective the model has; the objective of the model is not changed.

`zeroFlux.tsv` has the header `Rxns` and one reaction ID per line.

A file with the column `evotuneRMSEweight` raises an error that names `weight`. The first row of `fluxData.tsv` in the `full_ecModel` tutorial, `Std`, has the weight 0: it holds the standard condition of the protein-constraint step, which the tuning does not use.

## Configure the tuning

The settings are in the `[evotune]` table of `model_adapter.toml`. Every setting has a default (see [Model adapter parameters](model-adapter-parameters.md#kcat-tuning)). The settings with their defaults:

```toml
[evotune]
sigma0_log_default = 0.5
max_growth_weight = 1.0
prior_penalty_weight = 0.03
tie_isozymes = true
rmse_threshold = 0.2
max_generations = 150

[evotune.source_groups.custom]
sources = ["custom"]
sigma0_log = 0.1

[evotune.source_groups.brenda]
sources = ["brenda"]
sigma0_log = 0.2

[evotune.source_groups.ec_tree]
sources = ["ec_tree"]
sigma0_log = 0.3

[evotune.source_groups.combined]
sources = ["combined"]
sigma0_log = 0.4
```

| Setting (MATLAB field) | Meaning |
| --- | --- |
| `source_groups` (`kcatSources`) | trust groups, one table each with the `sources` it covers and its `sigma0_log`, the prior standard deviation of the natural log of the kcat |
| `sigma0_log_default` (`sigma0logDefault`) | standard deviation of the natural log of a kcat that matches no group |
| `max_growth_weight` (`maxGrowthWeight`) | weight `w` of the maximum-growth conditions against the flux conditions in the RMSE |
| `prior_penalty_weight` (`priorPenaltyWeight`) | weight `p` of a penalty for moving kcats; the search minimises `rmse + p * mean(((log k - log k0) / sigma0_log)^2)`. At 0 the objective is the RMSE |
| `tie_isozymes` (`tieIsozymes`) | isozyme copies of one reaction with the same kcat and the same group get one shared kcat |
| `rmse_threshold` (`rmseThreshold`) | the search stops when the best RMSE reaches this value; a negative value never stops the search early |
| `max_generations` (`maxGenerations`) | maximum number of CMA-ES generations |

A smaller `sigma0_log` is more trust: the search moves such a kcat less, and the screen ranks it lower. A kcat belongs to a group when the origin of its `ec.source`, or the whole `ec.source`, equals one of the `sources` of the group, without regard to case (see [Provenance of a kcat](../gecko4-kcat-assignment.md#provenance-of-a-kcat)). `brenda (wc=0, origin=1)` is in the group that lists `brenda`, `combined (sd=0.10, n=2)` in the group that lists `combined`, and a tuned kcat such as `brenda (wc=0, origin=1) | tuned=cmaes (prior=2)` stays in the group of `brenda`. An entry that ends in `*` is a prefix pattern: `okp_*` covers the origins that start with `okp_`. Exact entries are matched before patterns; [Source groups](model-adapter-parameters.md#source-groups) gives the full order. In both toolboxes the group of a kcat, in `screen.sourceGroup` (Python `source_group`) and `result.groups`, is the group name.

The default groups cover the origins `custom`, `brenda`, `ec_tree` and `combined` of the preset `brenda_ec_tree`; kcats with the origin `standard` take `sigma0_log_default`. Other presets and stages give other origins, such as `homologs`, `dlkcat` or `okp_<method>`. List the origins of `ec.source` (`parseKcatSource`, Python `parse_kcat_source`, returns the origin of each entry) and give each origin that needs its own trust a group. Groups in `model_adapter.toml` replace all default groups, so a file that adds one group lists the default groups it keeps as well. Kcats in no group take `sigma0_log_default`, and the tuning warns when they are more than 20 % of the tunable kcats.

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

The screen has one row per kcat or tied group: `rxnId` (Python `rxn_id`), `nIsozymes` (`n_isozymes`), `sourceGroup` (`source_group`), `kcat0`, `leverage`, `sigma0log` (`sigma0_log`), `rank` (leverage times `sigma0log`) and `cumLeverageShare` (`cum_leverage_share`), the sum of `rank` from the first row to this row as a fraction of the total. The column `positions` (Python `_positions`) holds the indices into `ec.rxns` of each row. The screen scores two kcat vectors for each kcat or tied group, so its time grows with the number of kcats screened; `tunableMask` (Python `tunable_mask`) restricts the screen to a subset.

## Review the assignments of the top kcats

`reviewKcatAssignment` checks each kcat for these problems: an EC number with specific-activity rows but no kcat rows in BRENDA (`no-ec-evidence`; an EC number that is not in BRENDA is not flagged), the same value in 5 or more reactions (`repeated-value`), the maximum of an EC number that is more than 3 times its median (`ec-maximum`), a value outside 0.01 to 10000 per s (`magnitude`), and a custom value that equals a BRENDA value of its EC number (`custom-duplicate`). The checks that need BRENDA statistics are skipped without `ecStats`. With the leverage of the screen the findings are sorted by leverage, and `coverage` or `top` shortens the list. Correct a wrong kcat in its source (see [Choose the kcat sources](kcat-sources.md) and [Set custom kcats](custom-kcats.md)); every model built from the same files then has the correction.

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

Each finding has the reaction, its EC number, source, kcat and leverage, the number of isozyme copies, the number of other reactions that share an enzyme (with the option `enzymes`), the names of the checks and a `detail` in words. Tied isozyme copies are reported once. Kcats with the source `standard` are reported when `include` lists `standard-fallback`, and the check `tied-isozymes` is added when `include` lists it; the default `include` is empty.

## Run evotune

`cmaesKcatTuning` uses `selectTunableMask` to select the kcats to search: the top rows of the screen, up to the first row at which `cumLeverageShare` reaches `targetImpactShare` (default 0.9). With `screen` the function uses that screen; without it, the function runs a new screen. `tunableMask` (Python `tunable_mask`) gives the set of kcats directly and takes precedence over `screen`.

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

A data row with oxygen uptake 0 or with a value of `Ptot` needs a function that changes the model. MATLAB runs the functions named by `make_model_anaerobic` and `change_protein_biomass` in the `[matlab]` table of `model_adapter.toml` (see [Model adapter parameters](model-adapter-parameters.md#matlab-functions)). Python takes these functions through the arguments `make_anaerobic(model)` and `change_protein_biomass(model, ptot)`; `tutorials/full_ecModel/code/anaerobic.py` in the geckopy repository has an example. Without a function, the condition is simulated without the change.

## The protein pool and sigma

Set the protein pool before evotune, with `setProtPoolSize` and the values of Ptot, f and $\sigma$ in the model adapter (see [Set the protein pool](protein-pool.md)). Evotune simulates each data row with the protein pool of the model; only a row with a value of `Ptot` changes it, through the protein content of the biomass (see [Conditions that change the model](#conditions-that-change-the-model)). The maximum growth rates of `maxGrowth.tsv` are part of the fit, so the tuning fits the kcats to these growth rates with that pool.

Do not run `sigmaFitter` (Python `fit_sigma`) after evotune. It changes the protein pool so that the model reaches one growth rate, which moves every simulated growth rate and flux away from the values that the tuning fitted. A $\sigma$ fitted before evotune, to an ecModel with kcats that are too low, makes the pool compensate for the kcats (see [Sigma and kcat tuning](protein-pool.md#sigma-and-kcat-tuning)), and evotune then fits the kcats to that pool.

## Seeds, reproducibility and parallel runs

`seed` makes a run reproducible. MATLAB and Python have different CMA-ES implementations, so the same seed gives different results in the two toolboxes. In Python, a run with `n_proc` above 1 gives the same result as a run with `n_proc=1` and the same seed. `nProc` has the default 1 in MATLAB; `n_proc` has the default `cobra.Configuration().processes` in Python.

Different kcat vectors can fit the data equally well, so two seeds can move a kcat in different directions. Run the tuning with a second seed and compare the large changes (above two-fold): they should be in the same direction and of similar size. If they are not, increase `prior_penalty_weight`. `tunePriorPenaltyWeight` (Python `tune_prior_penalty_weight`) runs the tuning for each value of `candidates` (default 0, 0.01, 0.03 and 0.1) and each of `seeds` (default 0 and 1), on the same set of kcats, and reports per value the fit, the number of changed kcats and the agreement between seeds. It costs one tuning run per value and seed, and the model is not changed.

## Read the result

`result` (Python `EvotuneResult`) has these fields:

| MATLAB | Python | Meaning |
| --- | --- | --- |
| `rxns`, `oldKcat`, `newKcat`, `groups` | `rxns`, `old_kcat`, `new_kcat`, `groups` | the selected kcats before and after tuning, and the trust group of each; tied copies share one value |
| `rmseTrace`, `objectiveTrace` | `rmse_trace`, `objective_trace` | the best RMSE and the best value of the minimised objective, per generation; the two are equal when `prior_penalty_weight` is 0 |
| `nGenerations` | `n_generations` | number of generations that ran |
| `converged` | `converged` | whether the best RMSE reached `rmse_threshold` |

`ec.source` of every kcat that changed gets the tuning status `tuned=cmaes`, with the kcat before the first tuning as `prior` (see [Provenance of a kcat](../gecko4-kcat-assignment.md#provenance-of-a-kcat)). `nChanged` (Python `n_changed`) counts the kcats that differ from their value before tuning by more than 2 %. A result in which most of the selected kcats changed by a small factor does not identify single kcats; a result in which a few kcats changed by large factors, mostly in groups with a large `sigma0_log`, points to these kcats. `parsimonyFrontier` (Python `parsimony_frontier`) sets each kcat that moved less than a threshold, in units of its `sigma0_log`, back to the value before tuning, and scores the result for a series of thresholds with a scoring function that the caller gives. `bestParsimonious` (Python `best_parsimonious`) returns the point with the fewest changed kcats whose RMSE is within 2 % of the best RMSE. In Python, `result.corrections(leverage=...)` returns one `Correction` per kcat that differs from its value before tuning by more than 2 %, with the fields `rxn_id`, `name`, `ec_code`, `source` (the trust group), `kcat_prior`, `kcat_tuned`, `fold_change`, `leverage`, `leverage_share` and `cumulative_share`. `leverage` has one value per entry of `result.rxns`, and `annotate_from_model` gives the `names` and `ec_codes`. The rows are sorted by leverage, so the kcats that the data barely affect, which can move furthest, come last; `cumulative_share` is the share of the total leverage from the first row to this row. `corrections_tsv` in `geckopy.kcat_tuning` writes the rows as TSV. The module `geckopy.kcat_tuning.evotune.parsimony` has three more measures: `fold_change` (the fold change of each kcat, 1 or more), `source_movement` (per trust group, the median fold change of all kcats and of the kcats that moved, and whether the kcats moved less in the more trusted groups, for an order of trust that the caller gives) and `impact_share` (the share of the summed leverage that the changed kcats account for, without the `sigma0_log` weight of `cumLeverageShare`). Check the tuned model against data that were not used in the fit: an improvement on the fitted conditions without an improvement on other data indicates overfitting (see [Check against data left out of the fit](#check-against-data-left-out-of-the-fit)). As with `sensitivityTuning`, check the large changes against the source of each kcat (see [Choose a kcat tuning](kcat-tuning.md#check-a-tuned-kcat-against-its-source)), and keep curated values in `data/kcats/custom.tsv`.

## Run evotune from start to end

The scripts below run the steps of this page on the project of the tutorial `full_ecModel`: they rank the kcats, tune with two seeds on the same kcats, list the large changes of both seeds and save the tuned ecModel. They start from the ecModel that the tutorial saves before its kcat tuning, with assigned kcats and a set protein pool: `ecYeastGEM_stage_untuned.yml` from `protocol.m` in GECKO, and `ecYeastGEM_stage2.yml` from `protocol.py` in geckopy. Run the tutorial first, and replace `path/to/full_ecModel` with the path of its project. The scripts use 8 parallel processes; set `nProc` (Python `n_proc`) to the number of cores of the computer.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
% runEvotune.m: evotune on the project of the tutorial full_ecModel
ModelAdapterManager.setDefault('path/to/full_ecModel');
params = ModelAdapterManager.getDefault().getParameters();
setRavenSolver('gurobi');
nProc = 8;
outDir = fullfile(params.path, 'output');

% The ecModel with assigned kcats and a set protein pool, saved by protocol.m
ecModel = loadEcModel('ecYeastGEM_stage_untuned.yml');

% Rank the kcats
screen = screenKcatLeverage(ecModel, 'nProc', nProc);
writetable(removevars(screen, 'positions'), fullfile(outDir, 'evotune_screen.tsv'), ...
    'FileType', 'text', 'Delimiter', '\t');

% Tune the same kcats with two seeds
[ecTuned, res0] = cmaesKcatTuning(ecModel, 'screen', screen, 'nProc', nProc, 'seed', 0);
[~, res1] = cmaesKcatTuning(ecModel, 'screen', screen, 'nProc', nProc, 'seed', 1);
fprintf('RMSE %.3f (seed 0) and %.3f (seed 1) after %d generations\n', ...
    res0.rmseTrace(end), res1.rmseTrace(end), res0.nGenerations);

% The kcats that one of the seeds changed more than two-fold
fold0 = log2(res0.newKcat(:) ./ res0.oldKcat(:));
fold1 = log2(res1.newKcat(:) ./ res1.oldKcat(:));
large = abs(fold0) > 1 | abs(fold1) > 1;
enzymes = cell(numel(res0.rxns), 1);
for i = 1:numel(res0.rxns)
    j = strcmp(ecModel.ec.rxns, res0.rxns{i});
    enzymes{i} = strjoin(ecModel.ec.enzymes(ecModel.ec.rxnEnzMat(j, :) ~= 0), ' + ');
end
review = table(res0.rxns(large), enzymes(large), res0.groups(large), ...
    res0.oldKcat(large), res0.newKcat(large), res1.newKcat(large), ...
    sign(fold0(large)) == sign(fold1(large)), 'VariableNames', ...
    {'rxn', 'enzymes', 'group', 'kcat0', 'kcatSeed0', 'kcatSeed1', 'sameDirection'});
writetable(review, fullfile(outDir, 'evotune_review.tsv'), 'FileType', 'text', 'Delimiter', '\t');

saveEcModel(ecTuned, 'ecYeastGEM_evotune.yml');
```

The anaerobic rows of `fluxData.tsv` use the function `anaerobicModel_GECKO` in the `code` folder of the tutorial, which `make_model_anaerobic` in `model_adapter.toml` names.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
"""run_evotune.py: evotune on the project of the tutorial full_ecModel."""
import os
import sys

import numpy as np

from geckopy import ModelAdapter, load_ec_model, save_ec_model
from geckopy.kcat_tuning import annotate_from_model, corrections_tsv
from geckopy.kcat_tuning.evotune import cmaes_kcat_tuning, screen_kcat_leverage

project = "path/to/full_ecModel"
sys.path.insert(0, os.path.join(project, "code"))
from anaerobic import make_anaerobic  # noqa: E402

adapter = ModelAdapter.from_folder(project)
n_proc = 8
out_dir = os.path.join(project, "output")

# The ecModel with assigned kcats and a set protein pool, saved by protocol.py
ec_model = load_ec_model("ecYeastGEM_stage2.yml", adapter=adapter)

# Rank the kcats
screen = screen_kcat_leverage(ec_model, make_anaerobic=make_anaerobic, n_proc=n_proc)
screen.drop(columns="_positions").to_csv(
    os.path.join(out_dir, "evotune_screen.tsv"), sep="\t", index=False)

# Tune the same kcats with two seeds; each run changes its model in place
ec_seed1 = ec_model.copy()
res0 = cmaes_kcat_tuning(ec_model, screen=screen, make_anaerobic=make_anaerobic,
                         n_proc=n_proc, seed=0)
res1 = cmaes_kcat_tuning(ec_seed1, screen=screen, make_anaerobic=make_anaerobic,
                         n_proc=n_proc, seed=1)
print(f"RMSE {res0.rmse_trace[-1]:.3f} (seed 0) and {res1.rmse_trace[-1]:.3f} "
      f"(seed 1) after {res0.n_generations} generations")

# The kcats that one of the seeds changed more than two-fold
fold0 = np.log2(res0.new_kcat / res0.old_kcat)
fold1 = np.log2(res1.new_kcat / res1.old_kcat)
for i in np.flatnonzero((np.abs(fold0) > 1) | (np.abs(fold1) > 1)):
    same = np.sign(fold0[i]) == np.sign(fold1[i])
    print(f"{res0.rxns[i]} ({res0.groups[i]}): {res0.old_kcat[i]:.3g} -> "
          f"{res0.new_kcat[i]:.3g} (seed 0), {res1.new_kcat[i]:.3g} (seed 1), "
          f"same direction: {same}")

# The changes of seed 0, sorted by the leverage of the screen
leverage = np.zeros(len(ec_model.ec.rxns))
for _, row in screen.iterrows():
    leverage[list(row["_positions"])] = row["leverage"]
positions = [ec_model.ec.rxns.index(r) for r in res0.rxns]
info = annotate_from_model(ec_model, res0.rxns)
rows = res0.corrections(leverage=leverage[positions], names=info["names"],
                        ec_codes=info["ec_codes"])
with open(os.path.join(out_dir, "evotune_corrections.tsv"), "w") as fh:
    fh.write(corrections_tsv(rows))

save_ec_model(ec_model, "ecYeastGEM_evotune.yml", adapter=adapter)
```

The anaerobic rows of `fluxData.tsv` need `make_anaerobic` from `code/anaerobic.py` of the tutorial; without it, these rows are simulated with oxygen. The function is defined at module level, so the parallel processes of the screen and the tuning can import it.
:::
::::

<!-- Run times and RMSE of these scripts on the tutorial: to be added from a measured run. -->

### Run time and the solver

The run time grows with the number of data rows, the number of kcats in the screen, `popsize` and the number of generations: the screen solves one FBA problem per data row for two kcat vectors per kcat, and each generation of the tuning one per data row for `popsize` kcat vectors. The scripts run the screen once and the tuning twice.

Use Gurobi. MATLAB uses the solver that `setRavenSolver` sets; check it with `getpref('RAVEN', 'solver')`. Python uses the solver of cobrapy, which takes Gurobi when the package `gurobipy` can be imported and a licence is found, and otherwise GLPK without an error; GLPK makes the run many times slower. Check the solver before a long run:

```python
import cobra
print(cobra.Configuration().solver)
```

### Run a long tuning

The screen and the tuning run in parallel over `nProc` (Python `n_proc`) processes, so a computer with many cores shortens a long run. MATLAB needs the Parallel Computing Toolbox for `nProc` above 1. The scripts save the tuned ecModel at the end, so a run that is stopped before it ends loses the results that the script has not yet written. Run a long job in a way that keeps it alive when the terminal closes, and set a time limit, if the computer has one, with a margin over the expected run time.

### Choose the number of kcats and generations

`targetImpactShare` (default 0.9) sets how many kcats the tuning searches: the top rows of the screen up to that share of the weighted effect on the fit. The share is relative to the total of the screen, so the same value selects a comparable part of the effect on the fit in another model. Each searched kcat is a free parameter of the fit, so a higher share fits more kcats to the same data. With few data rows, keep the share low, and compare the fit and the agreement between seeds for two or three values. In Python, `sweep_tunable_mask_size` runs the tuning for a series of values and `recommend_target_impact_share` picks one from the results.

`max_generations` is the most generations the tuning runs. Plot `rmseTrace` (Python `rmse_trace`) against the generation: when the RMSE still falls at the last generation, raise `max_generations`; when it is flat over the last part of the run, the tuning can stop earlier. `popsize` grows with the number of free kcats, so a run with more kcats costs more per generation.

### Check against data left out of the fit

A fit to the data that were used for the tuning does not show that the tuned kcats predict other conditions. Leave some conditions out of the tuning, tune on the others, and compare the RMSE of the left-out conditions before and after the tuning. The example leaves out the maximum growth rates on galactose and maltose by giving their rows the weight 0 in the tuning data. The rows stay in the data, so that their carbon sources stay closed when the other rows are simulated (see [Prepare the data files](#prepare-the-data-files)). The scripts use the names of the scripts above, with the ecModel before the tuning: in MATLAB `ecModel` is not changed by the tuning, while in Python `cmaes_kcat_tuning` changed `ec_model` in place, so the Python script loads it again.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
experimentData = loadEvotuneData();
test = ismember(experimentData.maxGrowth.conds, {'galactose', 'maltose'});
train = experimentData;
train.maxGrowth.weight = double(~test);

screenTrain = screenKcatLeverage(ecModel, 'experimentData', train, 'nProc', nProc);
ecTrain = cmaesKcatTuning(ecModel, 'experimentData', train, 'screen', screenTrain, ...
    'nProc', nProc, 'seed', 0);

% Score the maximum growth rates of the left-out conditions
held = experimentData;
held.fluxData = [];
[~, ~, before] = evotuneScore(ecModel, held);
[~, ~, after] = evotuneScore(ecTrain, held);
fprintf('Left-out RMSE: %.3f before, %.3f after the tuning\n', ...
    mean([before{test, 2}]), mean([after{test, 2}]))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import copy

from raven_toolbox.experiments import (
    compute_carbon_weights, dataset_rmse, load_experiment_data, simulate_conditions,
)

ec_model = load_ec_model("ecYeastGEM_stage2.yml", adapter=adapter)
bio = adapter.params.bio_rxn
experiment_data = load_experiment_data(adapter.params.path / "data")
test = np.isin(experiment_data.max_growth.conds, ["galactose", "maltose"])
train = copy.deepcopy(experiment_data)
train.max_growth.weight = (~test).astype(float)

ec_train = ec_model.copy()
screen_train = screen_kcat_leverage(ec_train, experiment_data=train,
                                    make_anaerobic=make_anaerobic, n_proc=n_proc)
cmaes_kcat_tuning(ec_train, experiment_data=train, screen=screen_train,
                  make_anaerobic=make_anaerobic, n_proc=n_proc, seed=0)

# Score the maximum growth rates of the left-out conditions
mg = experiment_data.max_growth
carbon_weights = compute_carbon_weights(ec_model, mg.exch_rxn_ids, bio)
for when, model in [("before", ec_model), ("after", ec_train)]:
    with model:
        model.objective = bio
        sims = simulate_conditions(model, mg, constrain=False, zero_flux_rxns=[],
                                   bio_rxn_id=bio)
    _, per_row = dataset_rmse(mg, sims, constrain=False, carbon_weights=carbon_weights)
    print(f"Left-out RMSE {when} the tuning: {per_row[test].mean():.3f}")
```
:::
::::

The screen of this check is run on the tuning data, so that the left-out conditions also take no part in the choice of the kcats. When the RMSE of the left-out conditions falls, the tuning improves conditions it was not fitted to. When it stays the same or rises while the RMSE of the fit falls, the tuning fits the kcats to the particular conditions: search fewer kcats, or raise `prior_penalty_weight`. Repeat the check with other left-out conditions, because one pair of conditions can be easy or hard by chance.

### Keep the corrections

The tuned ecModel holds the tuned kcats, but the next `assignKcats` replaces them with the values of the kcat source files. `evotune_review.tsv` (MATLAB) and `evotune_corrections.tsv` (Python) list the changed kcats with the value before and after the tuning. Check each large change against the source of the kcat (see [Check a tuned kcat against its source](kcat-tuning.md#check-a-tuned-kcat-against-its-source)), and add each value you keep to `data/kcats/custom.tsv` by hand (see [Keep a curated kcat](kcat-tuning.md#keep-a-curated-kcat)), with the evidence in the column `note`. In `custom.tsv`, `rxn` is the reaction of the conventional GEM: remove the suffix `_EXP_<n>` of an isozyme copy. A row without `enzymes` applies to every isozyme of the reaction, which matches isozyme copies that the tuning tied to one kcat; for a single copy, give its enzymes. A large change that differs in direction between the seeds is not supported by the data, and is not a correction to keep.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| The screen or the tuning runs many times longer than expected (Python) | `gurobipy` cannot be imported or finds no licence, and cobrapy uses GLPK | Check `cobra.Configuration().solver` before the run, and install `gurobipy` with a licence |
| The RMSE still falls at the last generation | `max_generations` ends the search before it converges | Raise `max_generations` |
| The RMSE of the fit falls, but the RMSE of left-out conditions does not | The tuning fits the kcats to the conditions of the data | Search fewer kcats (`targetImpactShare`), or raise `prior_penalty_weight` |
| The anaerobic conditions fit badly (Python) | `make_anaerobic` was not given, so these rows are simulated with oxygen | Pass `make_anaerobic` to the screen and the tuning |
| Error `evotune:noData` (MATLAB), or `ValueError` that `experiment_data` has neither `flux_data` nor `max_growth` (Python) | Neither `fluxData.tsv` nor `maxGrowth.tsv` is in `<project>/data/` | Add one of the files, or pass the loaded data |
| Error that a carbon source cannot be matched by name with an exchange reaction | The `Condition` of a row differs from every metabolite name in the exchange column headers | Use the metabolite name of the column header as the condition |
| Error `No tunable kcats` | No kcat is above 0, or the mask excludes every kcat | Assign kcats first, or widen the mask |
| Error `Only 1 free parameter(s) after masking and tying` | The mask and the isozyme tying leave fewer than two free kcats | Raise `targetImpactShare`, or give a wider `tunableMask` |
| Error `GECKO:loadAdapterParams`: `<file>: evotune.source_groups.<group> needs both sources and sigma0_log` | A group lacks `sources` or `sigma0_log` | Give each group both keys |
| Warning `<n> of <m> tunable kcats match no evotune source group and get sigma0_log_default` | The `sources` of the groups do not match the origins of `ec.source` in the model | List the origins that the warning names in the `sources` of a group, or use a pattern such as `okp_*` |
| The large changes differ in direction between seeds | Several kcat vectors fit the data equally well | Increase `prior_penalty_weight`, and compare values with `tunePriorPenaltyWeight` |

## See also

- [Choose a kcat tuning](kcat-tuning.md), the choice between evotune and `sensitivityTuning`, and the check of a tuned kcat.
- [Set the protein pool](protein-pool.md), Ptot, f and sigma.
- [Files in the data folder](data-folder-files.md), every file of the `data` folder.
- [Model adapter parameters](model-adapter-parameters.md#kcat-tuning), the `[evotune]` settings in both toolboxes.
- [API reference](../api/index.md), every function in both toolboxes.
