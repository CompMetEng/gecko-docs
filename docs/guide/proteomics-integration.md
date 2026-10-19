# Proteomics integration

Enzyme usage reactions let a full ecModel take proteomics data directly:
instead of drawing every enzyme's mass from the shared total protein pool,
individual enzymes with measured concentrations are constrained by those
measurements. The result is a proteome-constrained ecModel that reflects one
specific experimental condition rather than a generic protein budget.

:::{warning}
This page applies to full ecModels only. A light ecModel has no per-enzyme
usage reactions to constrain; see [GECKO light vs. full
ecModels](gecko-light.md).
:::

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `loadProtData` | `load_prot_data` | read `proteomics.tsv` into a proteomics data structure |
| `fillEnzConcs` | `fill_enz_concs` | populate `ec.concs` with the measured concentrations |
| `constrainEnzConcs` | `constrain_enz_concs` | apply those concentrations as bounds on `usage_prot_*` reactions |
| `calculateFfactor` + `setProtPoolSize` | `calculate_f_factor` + `set_prot_pool_size` | recompute the protein pool constraint for the remaining, unmeasured enzymes |
| `loadFluxData` | `load_flux_data` | read `fluxData.tsv` (exchange fluxes and growth rate for the same experiment) |
| `constrainFluxData` | `apply_flux_data_constraints` | apply those exchange flux and growth rate constraints |

## Constrain with proteomics data

Constraining individual enzyme concentrations usually overconstrains the
ecModel, because uncertainty now comes from two sources at once: the enzyme
levels and the $k_{cat}$ values. Proteomics data therefore need to be of high
quality, with low-certainty measurements discarded, or the resulting model
will fail to reach its intended growth rate.

Prepare the data before loading it:

- Provide protein concentrations in milligram per gram dry cell weight
  (mg/gDCW). Relative proteomics cannot supply this unit; loading it anyway
  produces a nonsensical ecModel.
- Store the data in `data/proteomics.tsv`, which can hold multiple
  experimental conditions as separate columns.
- Filter out low-certainty measurements: very low concentrations, proteins
  with high relative standard deviation across replicates, and proteins
  absent from most replicates.

:::{tip} Absolute quantitative data is not the only option
Proteomics measurements are not always performed with external standards for
absolute quantification. Label-free mass spectrometry is a powerful
alternative that needs neither expensive external standards nor stable
isotope labeling, and this kind of data has routinely been used with GECKO
ecModels.
:::

Integration follows four steps, the same shape as integrating $k_{cat}$
values: load the proteomics data, populate `ec.concs` with the
relevant concentrations, apply those concentrations as bounds on the
matching `usage_prot_*` reactions, and stop drawing the constrained enzymes
from the protein pool. Load the data first:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
% one experiment with three replicates
protData = loadProtData(3);

% two experiments with three replicates each
protData = loadProtData([3, 3]);
```

`loadProtData` also filters the dataset. When `protData` holds several
experiments, select which one to use (experiment 1 here):

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

`data_col` selects which experiment to use, 0-indexed (MATLAB's experiment
index is 1-indexed), so the first experiment is `data_col=0`:

```python
fill_enz_concs(ec_model, prot_data, data_col=0)
```
:::
::::

Introduce the concentrations as bounds on the model. Each `usage_prot_*`
reaction with a measured concentration receives that concentration as its
upper bound:

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

Raises `ValueError` on a light ecModel: light ecModels have no
`usage_prot_*` reactions to constrain.
:::
::::

:::{warning}
Enzyme concentrations must be in mg/gDCW. Relative proteomics data loaded
with the wrong units produces an ecModel with nonsensical constraints
instead of raising an error.
:::

Enzymes now constrained by a measured concentration should stop drawing from
the protein pool pseudo-metabolite. Because a proteomics experiment may
reflect a physiology different from the default assumption, recompute the
pool size from a sample-specific total protein content (for example 0.5
g/gDCW) instead of the adapter's default `Ptot` (Python: `p_tot`):

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
f = calculateFfactor(ecModel, 'protData', protData);
ecModel = setProtPoolSize(ecModel, 'Ptot', 0.5, 'f', f);
```

**`updateProtPool` served this purpose before GECKO 3.2.0.** Since 3.2.0,
every protein usage reaction draws from the pool regardless of whether it
also has a concentration constraint, which makes `updateProtPool` obsolete;
recompute the f-factor and call `setProtPoolSize` instead, as shown above.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import calculate_f_factor, set_prot_pool_size

f = calculate_f_factor(ec_model, prot_data)
set_prot_pool_size(ec_model, p_tot=0.5, f=f)
```

geckopy never implemented `updateProtPool`: it was already obsolete in
GECKO by the time of the port.
:::
::::

## Constrain with experimentally measured exchange fluxes

Because the integrated enzyme concentrations come from one particular
experiment, also constrain any exchange reaction for which that experiment
has measured data, such as glucose uptake, ethanol production, or CO2
exchange rate. `data/fluxData.tsv` can hold multiple experiments and as many
reaction fluxes as needed; a flux of zero blocks the corresponding exchange
reaction. Load it:

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

Two choices decide how the constraint gets applied:

1. **Loose vs. strict.** With loose constraints, the measured rate is set as
   the upper bound and the lower bound stays at zero (for a reaction with a
   negative rate, the lower bound gets the measured value and the upper
   bound stays at zero). With strict constraints, the lower and upper bounds
   are both set close to the measured value, for example at 95% and 105% of
   it. Strict constraints force the ecModel to follow the measured fluxes
   closely, but imprecision in either the fluxes or the enzyme concentrations
   can then make the model infeasible; loosen the constraint if that
   happens.
2. **Max vs. min growth.** With `max`, the measured growth rate is the upper
   bound, the ceiling the ecModel should reach; suitable when growth is the
   objective function. With `min`, the measured growth rate is the lower
   bound, the floor the ecModel must reach; suitable when the objective is
   minimizing protein pool usage instead (see [Simulation and
   analysis](simulation-and-analysis.md)).

Using loose constraints for the metabolic exchange fluxes and `max` for
growth makes the ecModel least likely to end up overconstrained. Apply the
first experiment's data and solve:

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

`condition` is 0-indexed (MATLAB's experiment index is 1-indexed), so the
first experiment is `condition=0`.
:::
::::

With `max` and loose constraints, FBA should reach a solution unless too
many exchange fluxes were pinned to zero. If the reachable growth rate falls
short of the intended one, the enzyme levels are overconstrained and need to
be made more flexible, covered on the next page.

## Example output

Applying strict measured exchange fluxes and a strict measured growth rate
to a proteomics-constrained ecModel can be considerably more restrictive
than the enzyme constraints alone: in one example, the growth rate reached
is 0.004578 /hour, against an intended 0.1 /hour. Applying the same flux constraints to the
conventional GEM (no enzyme constraints at all) distinguishes the two
possible causes: if the conventional GEM still falls short of 0.1 /hour, the
exchange flux data, not the enzyme constraints, are the bottleneck.

## See also

- [Relaxing overconstrained proteomics](relaxing-constraints.md), for when
  the ecModel cannot reach its intended growth rate after constraining.
- [GECKO light vs. full ecModels](gecko-light.md), why light ecModels cannot
  take proteomics data.
- [Simulation and analysis](simulation-and-analysis.md), choosing between
  maximizing growth and minimizing protein pool usage as the objective.
