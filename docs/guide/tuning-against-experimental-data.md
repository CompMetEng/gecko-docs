# Tuning against experimental data

[Growth-rate tuning](growth-rate-tuning.md) raises kcats one at a time until a single target growth rate is reached. `cmaesKcatTuning` (Python `cmaes_kcat_tuning`) fits many kcats at once with CMA-ES against measured growth rates and fluxes of several conditions, weighted by how much the source of each kcat is trusted. The result is a ranking of the kcats that the data can inform, a review of the assignment behind the top kcats, a tuned ecModel and a list of the changes of the tuning for a curator to review.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `loadEvotuneData` | `load_evotune_data` | loads the three data files; the tuning functions call it when no data are given |
| `screenKcatLeverage` | `screen_kcat_leverage` | reports which kcats the data can inform, without any optimisation |
| `selectTunableMask` | `select_tunable_mask` | turns the screen into the set of kcats that are searched |
| `reviewKcatAssignment` | `review_assignment` | flags kcat assignments that deserve a second look, independent of the data |
| `ecStatsFromBrenda` | `ec_stats_from_brenda` | summarises BRENDA per EC number for the assignment review |
| `cmaesKcatTuning` | `cmaes_kcat_tuning` | searches the tunable kcats with CMA-ES for the best fit to the data |
| `tunePriorPenaltyWeight` | `tune_prior_penalty_weight` | sweeps `priorPenaltyWeight` and reports fit against reproducibility across seeds |
| `nChanged`, `parsimonyFrontier`, `bestParsimonious` | `n_changed`, `parsimony_frontier`, `best_parsimonious` | count the changed kcats and trade their number against the fit |
| | `EvotuneResult.corrections` | turns the result into a reviewable list of changes (no MATLAB counterpart) |

## Setup

- An ecModel with a model adapter and the project folders `models/` and `data/` (see [Getting started](getting-started.md) and [Building an empty ecModel](building-ec-model.md)), with kcats assigned (see [Kcat assignment](../gecko4-kcat-assignment.md)).
- Python: `pip install geckopy[evotune]`. The CMA-ES package `cma` is an optional dependency that the base installation does not include. MATLAB needs no additional package; `cmaesKcatTuning` contains its own separable (diagonal-covariance) CMA-ES.
- Experimental data in at least one of the files `evotuneFluxData.tsv` (measured exchange fluxes per condition) and `evotuneMaxGrowth.tsv` (measured maximum growth rates per carbon source). Both together pin the shape of metabolism (fluxes) and its rate (growth rate). Python raises a `ValueError` when neither file exists.

## Prepare the experimental data

Three tab-separated files are read from `<project>/data/`. A missing file is skipped. The `full_ecModel` tutorial of GECKO has all three in its `data` folder.

| File | Contents | Required |
| --- | --- | --- |
| `evotuneFluxData.tsv` | Measured exchange fluxes, one row per condition. | One of these two |
| `evotuneMaxGrowth.tsv` | Measured maximum growth rate, one row per condition, one active carbon source per row (at `-1000`, unconstrained). | One of these two |
| `evotuneZeroExch.tsv` | Reaction IDs assumed to carry zero flux in every condition. | No |

The two flux files share the column layout of the regular flux data file, read by `loadFluxData` (Python `load_flux_data`):

```
Condition   Ptot   grRate   glucose (r_1714)   fructose (r_1709)   ...   evotuneRMSEweight   source
glucose     NaN    0.41     -1000              NaN                ...   1                     DLKcat
fructose    NaN    0.338    NaN                -1000              ...   1                     DLKcat
```

`Condition` names the row, `grRate` is the measured growth rate and `Ptot` is the measured protein content (`NaN` if not measured). Each `<met> (<rxn>)` column holds a measured or fixed flux of that exchange reaction. `evotuneRMSEweight` scales the contribution of the row to the RMSE (usually `1`), and `source` is free text. `evotuneZeroExch.tsv` has a `Rxns` header followed by one reaction ID per line.

## Configure evotune in model_adapter.toml

Every setting has a default, so the `[evotune]` table can be omitted. A configured example:

```toml
[evotune]
sigma0_log_default = 0.3   # trust for any source not listed below
max_growth_weight = 2.0    # weight the growth-rate data double against flux data

[evotune.source_groups.okp]
sources = ["CataPro"]
match_okp = true

[evotune.source_groups.brenda]
sources = ["brenda"]

[evotune.source_groups.custom]
sources = ["custom"]

[evotune.sigma0_log_source]
okp = 0.25
brenda = 0.2
custom = 0.1
```

The default template sets `sigma0_log_default = 0.5`, the groups `dlkcat`, `brenda` and `custom` with `sigma0_log_source` values 0.4, 0.2 and 0.1, `max_growth_weight = 1.0`, `prior_penalty_weight = 0.03`, `tie_isozymes = true`, `rmse_threshold = 0.2` and `max_generations = 150`. MATLAB reads the same keys under other names, for example `evotune.sigma0logDefault`, listed in `adapterParameters.tsv`.

- **Trust tiers** (`source_groups`, `sigma0_log_source` and `sigma0_log_default`). Kcats are grouped by their entry in `ec.source`, and each group has a standard deviation in log space. A smaller value means more trust, so the search needs stronger evidence before it moves such a kcat far. With the values above, a curated kcat (`custom`, 0.1) is three times more trusted than a kcat of an unlisted source (0.3). A kcat belongs to the group that lists its `ec.source`, or the part of `ec.source` before ` (`, so `brenda (wc=0, origin=1)` is in the group that lists `brenda` and `combined (sd=0.10, n=2)` in the group that lists `combined`. Entries of `sources` are matched case-insensitively, against the whole label and against the part before ` (`. A group with `match_okp = true` also takes the kcats whose `ec.source` equals the configured OpenKineticsPredictor method (`CataPro` in the example, one of the methods named in the template), matched in the same way. When a label matches several groups, the first matching group applies in Python and the last matching group in MATLAB. A kcat in no group takes `sigma0_log_default`. The tiers depend on the source labels of the model, so no tier set applies to every model.
- **`max_growth_weight`**. The combined score is `(rmse_flux + w * rmse_max_growth) / (w + 1)`. At `2`, the growth-rate error counts double against the flux error, which suits growth rates measured on many carbon sources and fluxes measured mainly on one.
- **`prior_penalty_weight`**. Adds `w * mean(((log k - log k0) / sigma0)^2)` to the score, a charge for moving a kcat that is scaled by the trust in its prior. Without the term the fit is flat along many directions: several different kcat vectors fit equally well, and the search returns an arbitrary point that does not reproduce with another seed. The default of `0.03` keeps large corrections in the same direction and within a few fold of each other across seeds, at a small cost in fit. A value of `0` scores on the fit alone. The suitable strength depends on the model and the data, since it scales with `sigma0_log` and with the objective. `tunePriorPenaltyWeight` (Python `tune_prior_penalty_weight`) runs `cmaesKcatTuning` for each of `candidates` (default `0`, `0.01`, `0.03`, `0.1`) at each of `seeds` (default `0` and `1`) and reports the fit cost against the reproducibility across seeds. It costs one full tuning run per candidate and seed, which makes it an occasional calibration.
- **`tie_isozymes`**. Several ecModel reactions are one enzymatic reaction split over isozyme copies. When copies share a prior value and a source, no condition can distinguish them, so an untied search can assign them a difference without biological meaning. Tying gives such copies one shared kcat.
- **`max_generations`, `rmse_threshold`**. The stopping conditions: at most `max_generations` CMA-ES generations, or earlier once the best RMSE reaches `rmse_threshold`. A negative `rmse_threshold` never stops the search early.

## Screen which kcats the data can inform

The screen perturbs every tunable kcat up and down by a factor (`fold`, default `2`), moving isozyme copies together as `tie_isozymes` sets, and records how much the fit changes. No tuning happens.

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
model = load_ec_model(adapter=adapter)  # models/ecModel.yml by default

screen = screen_kcat_leverage(model, adapter=adapter, n_proc=8)
screen.drop(columns="_positions").head(20)
```
:::
::::

The result is a table with one row per kcat or tied group, ranked by leverage weighted by trust: the reaction ID (`rxnId`, Python `rxn_id`), the number of isozyme copies, the source group, the current value, the leverage, and `cumLeverageShare` (Python `cum_leverage_share`), the running fraction of the total combined ranking value (leverage weighted by trust) carried by the row and all rows above it. Leverage is the largest change of the plain RMSE caused by one of the two perturbations. A hidden column (`positions`, Python `_positions`) holds the indices into `ec.rxns` that `selectTunableMask` needs.

The top rows are what a curator can look at first, whether or not a tuning search follows. In one study on ecYeastGEM (not reproduced from the repository), a few kcats carried most of what a tuning run can achieve, and they tended to be implausible database values.

The screen costs one simulation per condition and per kcat group (two probes per group plus a baseline), which is comparable to the budget of a full tuning run. On the `full_ecModel` tutorial the screen runs 8413 simulations (4206 kcat groups, two probes each, and a baseline). With `nProc` and `n_proc` set to 8, the Python screen took 2.8 h. In MATLAB a simulation took 3.6 s with eight processes, an estimate of 8.4 h for the full screen. Both runs used Gurobi; the difference between the two was not investigated. `nProc` (Python `n_proc`) parallelises it as it does the tuning; in MATLAB, values above 1 need the Parallel Computing Toolbox.

## Check the assignments behind the top kcats

`reviewKcatAssignment` (Python `review_assignment`) flags source-level problems of the assignment: a value without a kcat row for its EC number, one number reused across many unrelated reactions, the maximum of an EC number standing in for a distribution, an implausible magnitude, or a curated value that repeats what the database says. The corrections belong in the database or fuzzy-matching step in [Gathering kcats](gathering-kcats.md) that produced the value. A correction there reaches every model built from the same data, which a value moved by the tuner does not.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
% One struct per EC code queried while gathering kcats, summarising the
% kcat database (usually BRENDA) the assignment came from. For all EC
% codes of BRENDA: ecStatsFromBrenda(KCATcell, SAcell, KCATmedianCell).
ecStats = containers.Map('KeyType', 'char', 'ValueType', 'any');
ecStats('1.1.1.1') = struct('nKcat', 12, 'kcatMax', 340, 'kcatMedian', 45, ...
                            'values', [340 45 12], 'nSa', 0);

findings = reviewKcatAssignment(ecModel.ec.rxns, ecModel.ec.kcat, ...
    ecModel.ec.source, ecModel.ec.eccodes, 'ecStats', ecStats);
writetable(findings, 'findings.tsv', 'FileType', 'text', 'Delimiter', '\t')
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy.gather_kcats.review import EcStats, review_assignment, findings_tsv

# One EcStats per EC code queried while gathering kcats, summarising
# whatever kcat database (usually BRENDA) the assignment came from.
ec_stats = {
    "1.1.1.1": EcStats(n_kcat=12, kcat_max=340.0, kcat_median=45.0,
                       values=frozenset({340.0, 45.0, 12.0}), n_sa=0),
    # ...
}

findings = review_assignment(
    model.ec.rxns, model.ec.kcat, model.ec.source, model.ec.eccodes,
    ec_stats=ec_stats,
)
print(findings_tsv(findings))
```
:::
::::

Each finding names a reaction, its checks (`no-ec-evidence`, `repeated-value`, `ec-maximum`, `magnitude`, `custom-duplicate`) and a `detail` in words. Checks that need `ecStats` are skipped when it is absent. Isozyme copies that the assignment could not distinguish, the grouping of `tie_isozymes`, are reported once. Standard fallbacks (`standard-fallback`) and tied groups (`tied-isozymes`) are deliberate choices and are reported when `include` lists them.

Findings are ranked by `leverage` when it is given: the per-kcat effect from the screen, expanded from tie groups to the individual positions of `ec.rxns` through the position column of the screen. Without `leverage` the findings stay in input order. `coverage` (a share of the total leverage of the flagged rows) or `top` (a number of rows) truncates the report. `coverage` adapts to the model, since it keeps as many rows as carry that share of the flagged leverage, where a fixed `top` does not. In the same study the checks flagged around 1,900 of 4,834 kcats before truncation, which is too long a report to read. Stricter check thresholds do not shorten it as well as truncation by leverage, since looking odd (what the checks measure) and mattering (what leverage measures) are unrelated, so a stricter threshold removes high-leverage entries as readily as low-leverage ones.

## Tune

`cmaesKcatTuning` builds the tunable set with `selectTunableMask`, which keeps the fewest highest-ranked kcats whose combined leverage reaches `targetImpactShare` (Python `target_impact_share`, default `0.9`) of the total. The cutoff is relative to the achievable improvement of the model, so the same value means a comparable set on another model. A given `screen` avoids a second screening run; without `screen`, `cmaesKcatTuning` computes one. `tunableMask` (Python `tunable_mask`) fixes the set by hand and takes precedence.

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

result = cmaes_kcat_tuning(
    model, adapter=adapter, screen=screen, n_proc=8, seed=0,
)

save_ec_model(model, "ecModel_tuned.yml", adapter=adapter)
```
:::
::::

After the call, every tunable kcat of the ecModel holds the best value that CMA-ES found, and the kcat constraints are applied. Python changes `model` in place; MATLAB copies structs on assignment, so the output `ecModel` has to be captured. The other options are `popsize` (the CMA-ES population size, default `4 + floor(3*log(n))` for `n` free parameters), `nProc` and `seed`. The remaining settings come from the `[evotune]` table. The API reference lists the remaining options (`verbose`, `evoData` and `modelAdapter` in MATLAB; `okp_method`, `bio_rxn`, `params` and `evotune_data` in Python).

Growth that needs special handling for the organism, such as forced anaerobic conditions or a protein pool scaled with a condition-specific biomass composition, is set with functions. In Python these are the arguments `make_anaerobic` and `change_protein_biomass`, which default to `None`; `tutorials/full_ecModel/code/anaerobic.py` in the geckopy repository has an example. In MATLAB the `[matlab]` table of `model_adapter.toml` names the functions with the keys `make_model_anaerobic` and `change_protein_biomass`.

## Read the result

`result` is an `EvotuneResult` in Python and a struct in MATLAB, with these fields (Python name first):

- `rmse_trace`, `objective_trace` (MATLAB `rmseTrace`, `objectiveTrace`): the best plain-fit RMSE so far and the best optimised objective so far, per generation. They are identical when `prior_penalty_weight` is 0. A trace that is flat for many generations before the end indicates a stalled run.
- `new_kcat`, `old_kcat`, `rxns`, `groups` (MATLAB `newKcat`, `oldKcat`, `rxns`, `groups`): the tuned and prior kcats of the searched set as parallel arrays, with the trust tier of each kcat. Tied isozyme copies share one value in `new_kcat`.
- `converged`: whether `rmse_threshold` was reached before `max_generations`.
- `n_generations` (MATLAB `nGenerations`): the number of generations that ran.

The final RMSE alone does not show whether a tuned kcat can be trusted:

1. **Number and size of the changes.** A result that moves nearly every kcat by a little has not identified anything. `n_changed` (MATLAB `nChanged`) counts the kcats that differ from the prior by more than a relative tolerance (default 0.02). The module `geckopy.kcat_tuning.evotune.parsimony` also has `fold_change` and `source_movement`; `parsimony_frontier` and `best_parsimonious` (MATLAB `parsimonyFrontier`, `bestParsimonious`) trade the number of changed kcats against the fit.
2. **Impact share.** `parsimony.impact_share` reports the fraction of the total achievable improvement that the changed kcats carry. It separates few, large and consequential changes from sparsity. It is unweighted, unlike the trust-weighted `cum_leverage_share` of the screen.
3. **Reproducibility.** A run with another `seed` should give large corrections (beyond about two-fold) in the same direction and within a small factor of each other. Otherwise the search has found a flat direction, and `prior_penalty_weight` is the first setting to adjust.
4. **Generalisation.** Data that were not fitted score the tuned and the untuned model. A large improvement on the fitted conditions without an improvement elsewhere indicates overfitting to a thin dataset.

`new_kcat` and `old_kcat` hold thousands of numbers, most of them unchanged, which a reviewer cannot read. In Python, `result.corrections()` turns them into one `Correction` row per changed kcat (reaction, EC code, source, prior and tuned value, fold change), ranked by leverage, which differs from the order of the distance a kcat moved. Parameters that the data cannot see are free to drift furthest and are the least reliable, so they sort to the bottom. MATLAB has no counterpart of `corrections`; `result.oldKcat` and `result.newKcat` hold the values.

```python
from geckopy.kcat_tuning import annotate_from_model, corrections_tsv

# screen is the table from "Screen which kcats the data can inform" above; reuse
# it rather than recomputing leverage.
# The screen has one row per tie group; every isozyme copy of a group takes
# the leverage of its group, through the positions column.
leverage_by_rxn = {
    model.ec.rxns[pos]: row["leverage"]
    for _, row in screen.iterrows() for pos in row["_positions"]
}
leverage = [leverage_by_rxn.get(r, 0.0) for r in result.rxns]

annotations = annotate_from_model(model, result.rxns)
rows = result.corrections(
    leverage=leverage, names=annotations["names"], ec_codes=annotations["ec_codes"],
)
open("corrections.tsv", "w").write(corrections_tsv(rows))
```

`cumulative_share` of a row is the running fraction of the total leverage that the list has accounted for. The total is summed over the searched kcats, and each isozyme copy carries the leverage of its group, so a tied group counts once per copy. The reading can stop once the value stops climbing. This is the tuning-time counterpart of `review_assignment`: the review flags the kcats that need curation before a run, and the corrections list the kcats that the run changed and how far each change can be trusted.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| `ImportError` that names the `evotune` extra | The package `cma` is not installed | Run `pip install geckopy[evotune]` |
| Error that `evotune_data` has neither `flux_data` nor `max_grate` | Neither `evotuneFluxData.tsv` nor `evotuneMaxGrowth.tsv` is in `<project>/data/` | Add one of the files, or pass the loaded data |
| Error `No tunable kcats` | `ec.kcat` is not positive anywhere, or `tunableMask` excludes every kcat with a value | Assign kcats first, or widen the mask |
| Error `Only 1 free parameter(s) after masking and tying` | The mask and `tie_isozymes` leave fewer than two free parameters | Widen `tunableMask` or raise `targetImpactShare` |
| Most kcats take `sigma0_log_default` | The labels in `source_groups` do not match the `ec.source` entries of the model | List the labels that occur in `ec.source` (for example `ec_tree`, `combined` or `custom`) in `source_groups` |
| Large corrections differ in direction between seeds | The fit is flat along these kcats | Raise `prior_penalty_weight`, calibrated with `tunePriorPenaltyWeight` |

## See also

- [Growth-rate tuning](growth-rate-tuning.md), the iterative single-target tuning of kcats.
- [Kcat assignment](../gecko4-kcat-assignment.md) and [Applying kcats](applying-kcats.md), where the kcats and sources used here come from.
- [API reference](../api/index.md), every function in both toolboxes.
