# Analyse an ecModel

An ecModel has the structure of a conventional GEM, so every method for a conventional GEM runs on it. GECKO adds functions that take the enzyme constraints into account and map the results to the reactions of the conventional GEM. At the end of this page, you have chosen the analysis that answers your question, set the objective for it, and compared the result with the conventional GEM where the question needs that comparison.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `setParam(..., 'obj', ...)` and `solveLP` | `model.objective` and `model.optimize()` | set the objective and solve |
| `setProtPoolSize` | `set_prot_pool_size` | change the upper bound of the protein pool exchange |
| `mapRxnsToConv` | `map_rxns_to_conv` | map fluxes of the ecModel to the reactions of the conventional GEM |
| `ecFVA` | `ec_fva` | flux variability analysis, mapped to the reactions of the conventional GEM |
| `plotEcFVA` | (none) | plot the cumulative distribution of the flux ranges |
| `randomSampling` (RAVEN) | `random_sampling` (raven-toolbox) | draw flux vectors from the solution space |

## Setup

The examples use the model adapter parameters `params`, the ecModel, the conventional GEM that the ecModel was made from, and for some sections the flux data of `data/fluxData.tsv` ([Files in the data folder](data-folder-files.md)):

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
adapter  = ModelAdapterManager.setDefault(pwd);
params   = adapter.getParameters();
model    = loadConventionalGEM();
ecModel  = loadEcModel();        % models/ecModel.yml
fluxData = loadFluxData();       % data/fluxData.tsv
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ModelAdapter, load_conventional_gem, load_ec_model, load_flux_data

adapter = ModelAdapter.from_folder("ecMyModel")
params = adapter.params
model = load_conventional_gem(adapter)
ec_model = load_ec_model("ecModel.yml", adapter=adapter)
flux_data = load_flux_data(params.path / "data" / "fluxData.tsv")
```
:::
::::

[Find engineering targets](engineering-targets.md), [Make a context-specific ecModel](context-ecmodel.md) and [Enzyme usage and bottlenecks](enzyme-usage.md) use the same setup.

## Choose an analysis

| Question | Analysis | Needs | Result |
| --- | --- | --- | --- |
| How fast can the cell grow under these constraints? | maximise growth | the biomass reaction of the model adapter | the maximum growth rate and one flux distribution |
| Which flux distribution uses the least protein at this growth rate? | minimise `prot_pool_exchange` at fixed growth | a growth rate, measured or from the first objective | the minimum protein pool usage in mg/gDCW and its flux distribution |
| How far can each reaction vary? | `ecFVA` | the conventional GEM that the ecModel was made from | the minimum and maximum flux of each reaction of the conventional GEM |
| How are fluxes distributed over the solution space? | random sampling | a convergence check across independent chains | a matrix of flux vectors |
| Which reactions and genes to change to make a product? | `ecFSEOF`, see [Find engineering targets](engineering-targets.md) | a production reaction and the carbon source uptake reaction | reaction and gene targets with a suggested action |
| How do the fluxes compare with those of the conventional GEM? | `mapRxnsToConv` | the conventional GEM that the ecModel was made from | a flux vector in the reaction order of the conventional GEM |
| What does a tissue, cell line or strain do? | `getSubsetEcModel`, see [Make a context-specific ecModel](context-ecmodel.md) | a context-specific GEM made from the same GEM as the ecModel | a context-specific ecModel |

[Enzyme usage and bottlenecks](enzyme-usage.md) describes the analyses of single enzymes: which enzymes a solution uses, and which enzymes limit the objective.

For flux ranges, use `ecFVA`. A [convergence study of the samplers of raven-toolbox](https://raven-docs.readthedocs.io/en/latest/parameter-tuning/studies/sampling-convergence-calibration.html) found no setting that gave converged samples on yeast-GEM, a conventional GEM of about 4,100 reactions. The study did not test an ecModel.

## Set the objective

### Maximise growth

The biomass reaction of the model adapter is the objective. The protein pool exchange limits growth when its flux reaches the upper bound that `setProtPoolSize` sets ([Set the protein pool](protein-pool.md)).

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
sol = solveLP(ecModel);
maxGrowth = sol.f;
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.objective = params.bio_rxn
sol = ec_model.optimize()
max_growth = sol.objective_value
```
:::
::::

To see the effect of the protein pool constraint, solve a copy of the ecModel with an unlimited pool: `setProtPoolSize(ecModel, Inf)` in MATLAB, and in Python `set_prot_pool_size(ec_model_copy, p_tot=math.inf)` on a copy made with `ec_model.copy()`, because the Python function changes the model in place. Each enzyme usage reaction has an upper bound of 1000 mg/gDCW unless proteomics data constrain it, so the copy has no effective enzyme constraint. The `full_ecModel` tutorial of GECKO makes this comparison for yeast: its function `code/plotCrabtree.m` simulates the exchange fluxes over a range of growth rates and plots them against measured fluxes, and the tutorial runs it on the ecModel and on a copy with an unlimited pool.

### Minimise protein pool usage at fixed growth

`prot_pool_exchange` runs forward: its flux is the protein that the solution draws from the pool, a positive number in mg/gDCW. Fix growth at a value slightly below the maximum, for example 99 %, so that the second problem stays feasible within the tolerance of the solver. Then minimise the flux of `prot_pool_exchange`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

`solveLP` maximises the objective, so the coefficient -1 minimises the flux, and `sol.f` is the negative of the pool usage.

```matlab
ecModel = setParam(ecModel, 'lb', params.bioRxn, 0.99 * maxGrowth);
ecModel = setParam(ecModel, 'obj', 'prot_pool_exchange', -1);
sol = solveLP(ecModel);
poolUsage = -sol.f;   % mg/gDCW
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.reactions.get_by_id(params.bio_rxn).lower_bound = 0.99 * max_growth
ec_model.objective = "prot_pool_exchange"
ec_model.objective_direction = "min"
sol = ec_model.optimize()
pool_usage = sol.objective_value   # mg/gDCW
```
:::
::::

To use a measured growth rate instead of the maximum, call `constrainFluxData` with `maxMinGrowth` set to `'min'` (Python: `apply_flux_data_constraints` with `max_min_growth="min"`): the measured growth rate becomes the lower bound of the biomass reaction. [Constrain enzymes with proteomics](proteomics.md) describes the flux data file.

If `prot_pool_exchange` or the `usage_prot_*` reactions carry negative flux, the model has these reactions in the reverse direction. `upgradeEcModel` (Python: `upgrade_ec_model`) turns them forward, and `loadEcModel` (Python: `load_ec_model`) does this with a warning when it loads such a model ([GECKO 3 to GECKO 4](../gecko3-to-gecko4.md)).

## Compare the solution space with the conventional GEM

`ecFVA` groups the reactions of the ecModel by identifier without the suffixes `_REV` and `_EXP_<n>`, so that the isozyme copies and the reverse copy of a reaction form one group. For each group it minimises and maximises the combined flux, which takes two linear problems per group, the enzyme usage reactions and `prot_pool_exchange` included. The result has the reaction order of the conventional GEM and leaves out the enzyme usage reactions; for those, run a plain FVA on the ecModel (`getAllowedBounds` in RAVEN, `cobra.flux_analysis.flux_variability_analysis` in Python). The objective of the model is not used: each reaction varies within the bounds of the model, so set the bounds that define the condition (growth rate, uptake rates) on all models first. In MATLAB, a conventional GEM that does not match the ecModel raises its error only after all problems are solved.

The example gives the conventional GEM and the ecModel the same exchange constraints from `fluxData` (from `loadFluxData`, Python: `load_flux_data`) and compares the ranges:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
model   = constrainFluxData(model, fluxData, 1, 'max', 'loose');
ecModel = constrainFluxData(ecModel, fluxData, 1, 'max', 'loose');

[minFlux(:,1), maxFlux(:,1)] = ecFVA(model, model);
[minFlux(:,2), maxFlux(:,2)] = ecFVA(ecModel, model);
plotEcFVA(minFlux, maxFlux);
```

`ecFVA` runs in parallel when the Parallel Computing Toolbox is installed (option `runParallel`, default `true`). `plotEcFVA` takes one column per model, leaves out the reactions whose minimum and maximum are both 0, and plots the cumulative distribution of the ranges (`maxFlux - minFlux`) on a log scale, with the median of each model in the legend.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints, ec_fva

for m in (model, ec_model):
    apply_flux_data_constraints(
        m, flux_data, condition=0, max_min_growth="max",
        loose_strict_flux="loose", bio_rxn=params.bio_rxn, c_source=params.c_source,
    )

fva_gem = ec_fva(model, model)
fva_ec = ec_fva(ec_model, model)
ranges = (fva_ec["max_flux"] - fva_ec["min_flux"]).rename("ecModel").to_frame()
ranges["GEM"] = fva_gem["max_flux"] - fva_gem["min_flux"]
print(ranges.median())
```

`ec_fva` returns a DataFrame indexed by the reaction identifiers of the conventional GEM, with the columns `min_flux` and `max_flux`. The option `n_proc` sets the number of worker processes (default `cobra.Configuration().processes`). With the default solver GLPK, `ec_fva` is slow on a genome-scale ecModel; a commercial solver (`ec_model.solver = "gurobi"`, if you have a licence) or more worker processes shorten the run. geckopy has no counterpart of `plotEcFVA`.
:::
::::

A smaller range in the ecModel than in the conventional GEM shows a reaction that the enzyme constraints restrict. A proteomics-constrained ecModel ([Constrain enzymes with proteomics](proteomics.md)) can be added as a third column.

## Sample the solution space

FVA gives the extremes of each reaction, one reaction at a time. A sampler draws flux vectors from the space that the bounds of the model define, so the samples depend on every bound that is set before the call (growth rate, uptake rates, enzyme bounds). The samplers are part of RAVEN (MATLAB) and raven-toolbox (Python), not of GECKO:

| `method` | Samples | Note |
| --- | --- | --- |
| `'achr'` (default) | points inside the solution space | Artificially Centered Hit-and-Run |
| `'chrr'` | points inside the solution space | Coordinate Hit-and-Run with Rounding; the help of both toolboxes states that it mixes better in thin, ill-conditioned spaces such as those of enzyme-constrained models |
| `'randomObjective'` (Python: `"random_objective"`) | corners of the solution space | each sample optimises a random objective of a few reactions; in MATLAB, the `usage_prot_*` reactions of an ecModel are not used as objectives |

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
samples = randomSampling(ecModel, 1000, 'method', 'chrr', 'seed', 1);
mappedSamples = mapRxnsToConv(ecModel, model, samples);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import map_rxns_to_conv
from raven_toolbox.analysis import random_sampling

result = random_sampling(ec_model, n_samples=1000, method="chrr", seed=1)
samples = result.samples[[r.id for r in ec_model.reactions]].T.to_numpy()
mapped_samples = map_rxns_to_conv(ec_model, model, samples).mapped_flux
```

`result.samples` has one sample per row and one reaction per column, so the matrix is transposed before mapping.
:::
::::

Run several chains with different seeds and compare them, for example with the R-hat statistic, before you use the samples. The [convergence study](https://raven-docs.readthedocs.io/en/latest/parameter-tuning/studies/sampling-convergence-calibration.html) describes the check and the settings it tested.

## Map fluxes to the conventional GEM

A flux vector of an ecModel has more reactions than one of the conventional GEM: isozyme copies, reverse copies and the enzyme usage reactions. `mapRxnsToConv` subtracts the flux of each reverse copy, adds the isozyme copies, and returns the fluxes in the reaction order of the conventional GEM. It also accepts a matrix with one flux vector per column, such as the samples above.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
sol = solveLP(ecModel);
[mappedFlux, enzUsageFlux, usageEnz] = mapRxnsToConv(ecModel, model, sol.x);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import map_rxns_to_conv

sol = ec_model.optimize()
mapped = map_rxns_to_conv(ec_model, model, sol.fluxes)
mapped.mapped_flux, mapped.enz_usage_flux, mapped.usage_enz
```
:::
::::

`enzUsageFlux` (Python: `enz_usage_flux`) holds the fluxes of the `usage_prot_*` reactions and of `prot_pool_exchange`, and `usageEnz` (Python: `usage_enz`) their labels: the protein identifier, or `pool` for the protein pool exchange. The function matches reactions by identifier only. A reaction of the conventional GEM that is missing from the ecModel raises an error, but a reaction that was changed in the ecModel after `makeEcModel` (another stoichiometry or direction) is mapped without a warning.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| `prot_pool_exchange` or the `usage_prot_*` reactions carry negative flux | the model has these reactions in the reverse direction and was not loaded with `loadEcModel` | Run `upgradeEcModel` (Python: `upgrade_ec_model`) |
| `mapRxnsToConv` or `ecFVA` raises "Not all reactions from model.rxns can be found in the ecModel" | the conventional GEM is not the one that the ecModel was made from | Pass the GEM that `makeEcModel` started from |
| The `ecFVA` ranges of the ecModel reach 1000 for many reactions | the condition bounds were not set, so only the default bounds limit the fluxes | Set the growth rate and the uptake rates before `ecFVA` |
| Independent sampling chains give different flux distributions | the chains have not converged | Increase `thinning` and the number of samples, and check again |

## See also

- [Enzyme usage and bottlenecks](enzyme-usage.md): the enzymes that a solution uses and the enzymes that limit the objective.
- [Find engineering targets](engineering-targets.md): flux scanning with `ecFSEOF` for the production of a compound.
- [Make a context-specific ecModel](context-ecmodel.md): trim a generic ecModel to a tissue, cell line or strain.
- [Basic model operations](basic-model-operations.md): bounds, objectives and flux inspection.
- [Constrain enzymes with proteomics](proteomics.md): the flux data file and the proteomics-constrained ecModel.
- [Set the protein pool](protein-pool.md): the upper bound of `prot_pool_exchange`.
- [API reference](../api/index.md) and [MATLAB vs Python](../matlab-vs-python.md): the signature of each function in the table.
