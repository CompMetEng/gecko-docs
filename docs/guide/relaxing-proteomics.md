# Relax proteomics constraints

Raise the usage bounds of the enzymes that keep an ecModel constrained with proteomics below the measured growth rate, until it reaches that growth rate. At the end, you have an ecModel that reaches the growth rate, a list of the enzymes whose bounds were raised and by how much, and an indication of whether the shortfall comes from the proteomics data, the kcats, the protein pool or the metabolic network.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `flexibilizeEnzConcs` | `flexibilize_enz_concs` | raises the bound of the most limiting enzyme step by step, then lowers the bounds that are not needed |
| `relaxProteomicsGreedy` | `relax_proteomics_greedy` | removes the bound of the enzyme with the largest shadow price, one enzyme at a time |
| no counterpart | `relax_enz_concs` | finds the smallest total relaxation in one linear program |
| `constrainFluxData` | `apply_flux_data_constraints` | applies the same exchange fluxes to the conventional GEM, for comparison |

## Setup

An ecModel with concentrations applied as bounds and the exchange fluxes of the same condition, as made in [Constrain enzymes with proteomics](proteomics.md). `flexibilizeEnzConcs` and `relaxProteomicsGreedy` start from a solution of the ecModel, so it must be feasible: apply the growth rate with `'max'`, not `'min'`. The target growth rate is the measured growth rate of the condition. Pass it explicitly: by default `flexibilizeEnzConcs` reads `gr_exp` from `model_adapter.toml`, which is the maximum growth rate and can differ from the growth rate of the condition.

## Choose a method

| Method | What it changes | Stopping rule | What it returns |
| --- | --- | --- | --- |
| `flexibilizeEnzConcs` | On each iteration, it computes the control coefficient (growth gained per mg/gDCW added) of every measured enzyme whose usage is above 75 % of its bound, and raises the bound of the enzyme with the largest coefficient to concentration × (1 + `foldChange` × k) on its k-th selection. After the loop, it minimises the protein pool usage at the target growth rate (± 0.25 %), sets each raised bound to the usage in that solution, and restores the measured concentration where the usage is lower. | The target is reached. Or no enzyme limits growth: the protein pool is then raised to the usage needed for the highest growth it allows, and that growth becomes the target. Or an enzyme is selected more than `iterPerEnzyme` times (default 5): the loop stops with a warning, the bounds are not lowered afterwards, and the target is not reached. | the ecModel and `flexEnz` |
| `flexibilizeEnzConcs` with `perComplex` | As above, but the measured subunits of a complex form one unit: they are ranked together, raised by the same factor and lowered by the same factor, so levelled concentrations stay levelled. | As above, counted per complex, with an additional limit on the total number of iterations. | the ecModel and `flexEnz` |
| `relaxProteomicsGreedy` | Solves the ecModel, takes the enzyme with the largest absolute shadow price of its `prot_<id>` metabolite among the enzymes with a usage bound below 1000, and sets that bound to 1000. Bounds are never lowered afterwards. | The target is reached (`converged` true). Or no candidate is left: a warning, and `converged` false. Or `maxIterations` (default 100) is reached while candidates are left: an error. | `result`; the MATLAB function does not return the ecModel |
| `relax_enz_concs` (Python only) | Writes the bound of every measured enzyme as concentration × (1 + x) and minimises the sum of the x values under growth ≥ target, in one linear program. The protein pool can be raised too, at `pool_weight` (default 1000) times the price of an enzyme. `weight="absolute"` minimises the mg/gDCW added instead. `per_complex=True` gives the measured subunits of a complex one x. | One solution. When no relaxation reaches the target, it raises `ValueError` and restores the bounds. | `FlexEnzResult`, as `flexibilize_enz_concs` |

The methods also differ in the enzymes they can raise. `flexibilizeEnzConcs` raises a bound as a factor of the concentration, so an enzyme measured as 0 stays at 0 (the function warns and lists these enzymes). `flexibilizeEnzConcs` and `relax_enz_concs` act on enzymes with a concentration in `ec.concs`; an isozyme lowered by `zeroUnmeasuredIsozymes` has no concentration and is not raised. `relaxProteomicsGreedy` acts on every usage bound below 1000, including both cases.

Use `flexibilizeEnzConcs`, with `perComplex` when the concentrations were levelled with `levelComplexConcs`. Its result keeps the measured bound of every enzyme that the final solution does not need to raise. Use `relaxProteomicsGreedy` when enzymes with a bound of 0 limit growth; each enzyme that it relaxes has no bound of its own afterwards. In Python, `relax_enz_concs` gives a result that does not depend on the order in which enzymes become limiting; compare it with the result of `flexibilize_enz_concs`. An enzyme that both methods raise is limiting in the data; a conclusion that depends on an enzyme that only one method raises is uncertain.

## Relax with flexibilizeEnzConcs

`foldChange` (default 2) sets the step: with the defaults, the bound of an enzyme is 3, 5, 7, 9 and 11 times its concentration on its first to fifth selection. `iterPerEnzyme` set to 0 removes the limit per enzyme. The function changes only the usage bounds; `ec.concs` keeps the measured values.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, flexEnz] = flexibilizeEnzConcs(ecModel, 'expGrowth', fluxData.grRate(1));

% with complexes levelled by levelComplexConcs
[ecModel, flexEnz] = flexibilizeEnzConcs(ecModel, 'expGrowth', fluxData.grRate(1), ...
    'perComplex', true);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import flexibilize_enz_concs

flex_result = flexibilize_enz_concs(ec_model, exp_growth=float(flux_data.gr_rate[0]))

# with complexes levelled by level_complex_concs
flex_result = flexibilize_enz_concs(
    ec_model, exp_growth=float(flux_data.gr_rate[0]), per_complex=True,
)
```

The ecModel is changed in place. The progress messages are logged at the level INFO; `logging.basicConfig(level=logging.INFO)` shows them.
:::
::::

## Relax with relaxProteomicsGreedy

`enzymeSet` (Python: `enzyme_set`) limits the candidates to a list of UniProt identifiers. In MATLAB, the function returns only `result`, so apply the relaxed bounds to the ecModel yourself. In Python, the ecModel is changed in place.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
result = relaxProteomicsGreedy(ecModel, 'minimalGrowth', fluxData.grRate(1));
relaxedIds = {result.trace.relaxedUniprot};
ecModel = setParam(ecModel, 'ub', strcat('usage_prot_', relaxedIds), 1000);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import relax_proteomics_greedy

result = relax_proteomics_greedy(ec_model, minimal_growth=float(flux_data.gr_rate[0]))
```
:::
::::

## Relax with relax_enz_concs

`relax_enz_concs` is available in geckopy only; GECKO has no MATLAB counterpart. It changes the usage bounds and `prot_pool_exchange` in place and leaves `ec.concs` unchanged. An enzyme measured as 0 can be raised: its x is scaled by `floor` (default 1e-9 mg/gDCW), which makes it expensive with `weight="relative"`.

```python
from geckopy import relax_enz_concs

flex_result = relax_enz_concs(ec_model, exp_growth=float(flux_data.gr_rate[0]))
```

## Inspect the result

`flexEnz` (Python: `FlexEnzResult`) lists the relaxed enzymes, sorted by the ratio of the new bound to the old one, largest first. Its fields are `uniprotIDs`, `oldConcs`, `flexConcs`, `ratioIncr` and `frequence` (the number of times the enzyme was selected); Python uses `uniprot_ids`, `old_concs`, `flex_concs`, `ratio_incr` and `frequence`. An entry `prot_pool` is the protein pool exchange, with its old and new upper bound. The `result` of `relaxProteomicsGreedy` has `trace`, with one step per relaxed enzyme (`relaxedUniprot`, `growthBefore`, `growthAfter`, `shadowPrice`), `relaxed`, which maps each relaxed enzyme to its value in `ec.concs`, `finalGrowth` and `converged`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
disp(struct2table(flexEnz))
disp(struct2table(result.trace))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import pandas as pd

print(pd.DataFrame({
    "uniprot": flex_result.uniprot_ids,
    "old": flex_result.old_concs,
    "new": flex_result.flex_concs,
    "ratio": flex_result.ratio_incr,
    "selected": flex_result.frequence,
}))
print(pd.DataFrame([vars(step) for step in result.trace]))
```
:::
::::

## Interpret a large relaxation

A relaxation corrects for errors in the concentrations, and its size points to where the error is:

- **Many enzymes relaxed.** The proteomics data have many uncertain values. Filter them more strictly with `loadProtData` (for example a lower `maxRSD`), so that the uncertain enzymes draw from the protein pool without a bound of their own.
- **One enzyme selected many times**, or `flexibilizeEnzConcs` stops with the warning that the enzyme "seems to be problematic". Its kcat can be too low for this condition. Check the kcat against its source (see [Choose a kcat tuning](kcat-tuning.md) and [Choose the kcat sources](kcat-sources.md)).
- **The protein pool is raised.** Ptot × f × sigma is smaller than the protein that the condition needs, for example when sigma was fitted to another condition (see [Set the protein pool](protein-pool.md)).
- **No method reaches the target.** `flexibilizeEnzConcs` reports that the protein pool exchange was also not limiting, `relaxProteomicsGreedy` returns `converged` false, or `relax_enz_concs` raises `ValueError`. The enzyme constraints do not limit growth: the metabolic network or the exchange fluxes do. Apply the same exchange fluxes to the conventional GEM. If it does not reach the growth rate either, check the exchange fluxes of `fluxData.tsv` and the network.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
model = loadConventionalGEM();
model = constrainFluxData(model, 'fluxData', fluxData, 'condition', 1);
sol = solveLP(model);
fprintf('Growth rate of the GEM: %g /h\n', sol.f)
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints, load_conventional_gem

model = load_conventional_gem(ec_model.adapter)
apply_flux_data_constraints(
    model, flux_data, condition=0, bio_rxn=params.bio_rxn, c_source=params.c_source,
)
print(f"Growth rate of the GEM: {model.slim_optimize():g} /h")
```
:::
::::

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| `flexibilizeEnzConcs` warns about enzymes with a concentration of 0 and does not reach the target | a bound of 0 cannot be raised by a factor | Use `relaxProteomicsGreedy`, or load the data with `zerosAsMeasured` false |
| `flexibilize_enz_concs` returns an empty result with a warning | the ecModel has no solution before the relaxation | Apply the growth rate with `'max'`; check the exchange fluxes |
| `flexibilize_enz_concs` raises `ValueError` | no enzyme has a concentration, or `exp_growth` is not given and `gr_exp` is not set | Run `fill_enz_concs` and `constrain_enz_concs`; pass `exp_growth` |
| `relaxProteomicsGreedy` raises an error (Python: `RuntimeError`) | `maxIterations` was reached while candidates were left | Raise `maxIterations`, or use `flexibilizeEnzConcs` |
| The MATLAB ecModel does not grow faster after `relaxProteomicsGreedy` | the function does not return the ecModel | Set the usage bounds of the enzymes in `result.trace` to 1000, as in the example |
| The growth rate after `flexibilizeEnzConcs` is slightly below the target | the final pass minimises the pool usage within 0.25 % of the target growth rate | The difference is within 0.25 % of the target |
| The relaxed ecModel is much less constrained than the data | `relaxProteomicsGreedy` removes each bound completely | Use `flexibilizeEnzConcs` |

## See also

- [Constrain enzymes with proteomics](proteomics.md), where the bounds come from.
- [Enzyme usage and bottlenecks](enzyme-usage.md), to find the enzymes that limit growth without changing the bounds.
- [Choose a kcat tuning](kcat-tuning.md), for an enzyme whose kcat is too low.
