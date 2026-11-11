# Analyse an ecModel

An ecModel has the structure of a conventional GEM, so every method for a conventional GEM runs on it. GECKO adds functions for the questions that the enzyme constraints raise. At the end of this page, you have chosen the analysis that answers your question, set the objective for it, and compared the result with the conventional GEM where the question needs that comparison.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `setParam(..., 'obj', ...)` and `solveLP` | `model.objective` and `model.optimize()` | set the objective and solve |
| `setProtPoolSize` | `set_prot_pool_size` | change the upper bound of the protein pool exchange |
| `mapRxnsToConv` | `map_rxns_to_conv` | map fluxes of the ecModel to the reactions of the conventional GEM |
| `ecFVA` | `ec_fva` | flux variability analysis, mapped to the reactions of the conventional GEM |
| `plotEcFVA` | (none) | plot the cumulative distribution of the flux ranges |
| `randomSampling` (RAVEN) | `random_sampling` (raven-toolbox) | draw flux vectors from the solution space |
| `ecFSEOF` | `ec_fseof` | flux scanning with enforced objective function, for engineering targets |
| `getSubsetEcModel` | `get_subset_ec_model` | trim a generic ecModel to the reactions and genes of a context-specific GEM |

## The choice

| Question | Analysis | Needs | Result |
| --- | --- | --- | --- |
| How fast can the cell grow under these constraints? | maximise growth | the biomass reaction of the model adapter | the maximum growth rate and one flux distribution |
| Which flux distribution uses the least protein at this growth rate? | minimise `prot_pool_exchange` at fixed growth | a growth rate, measured or from the first objective | the minimum protein pool usage in mg/gDCW and its flux distribution |
| How far can each reaction vary? | `ecFVA` | the conventional GEM that the ecModel was made from | the minimum and maximum flux of each reaction of the conventional GEM |
| How are fluxes distributed over the solution space? | random sampling | a convergence check across independent chains | a matrix of flux vectors |
| Which reactions and genes to change to make a product? | `ecFSEOF` | a production reaction and the carbon source uptake reaction | reaction and gene targets with a suggested action |
| How do the fluxes compare with those of the conventional GEM? | `mapRxnsToConv` | the conventional GEM that the ecModel was made from | a flux vector in the reaction order of the conventional GEM |
| What does a tissue, cell line or strain do? | `getSubsetEcModel` | a context-specific GEM made from the same GEM as the ecModel | a context-specific ecModel |

[Enzyme usage and bottlenecks](enzyme-usage.md) answers the questions about single enzymes: which enzymes a solution uses, and which enzymes limit the objective.

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

To see the effect of the protein pool constraint, solve a copy of the ecModel with an unlimited pool: `setProtPoolSize(ecModel, Inf)` in MATLAB, and in Python `set_prot_pool_size(ec_model_copy, p_tot=math.inf)` on a copy made with `ec_model.copy()`, because the Python function changes the model in place. Each enzyme usage reaction has an upper bound of 1000 mg/gDCW unless proteomics data constrain it, so the copy has no effective enzyme constraint.

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

An ecModel made with GECKO 3 has `prot_pool_exchange` and the `usage_prot_*` reactions in the reverse direction. `loadEcModel` (Python: `load_ec_model`) turns them forward with `upgradeEcModel` (Python: `upgrade_ec_model`) and gives a warning. A model in memory that was not loaded this way needs `upgradeEcModel` before the code above gives the right sign ([GECKO 3 to GECKO 4](../gecko3-to-gecko4.md)).

## Compare the solution space with the conventional GEM

`ecFVA` minimises and maximises the flux of each reaction of the conventional GEM. It combines the isozyme copies (`_EXP_<n>`) and the reverse copies (`_REV`) of a reaction into one flux, so the result has the reaction order of the conventional GEM. The objective of the model is not used: each reaction varies within the bounds of the model, so set the bounds that define the condition (growth rate, uptake rates) on all models first. `ecFVA` solves two linear problems per reaction of the conventional GEM. It does not report the enzyme usage reactions; run a plain FVA on the ecModel for those.

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

`ec_fva` returns a DataFrame indexed by the reaction identifiers of the conventional GEM, with the columns `min_flux` and `max_flux`. The option `n_proc` sets the number of worker processes (default `cobra.Configuration().processes`). geckopy has no counterpart of `plotEcFVA`.
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

## Find engineering targets

`ecFSEOF` scans the production of a compound. It first finds the production at maximum growth and the maximum production, then fixes the production reaction at evenly spaced values from the first to 90 % of the second. At each value it maximises growth and then minimises the total flux. A reaction is a target when the absolute Pearson correlation between its absolute flux and the enforced production is at least `corrThreshold` (Python: `correlation_threshold`, default 0.9). Only reactions with a gene rule are scanned, and not those that use the standard enzyme ([Choose the kcat sources](kcat-sources.md)). The `usage_prot_*` reactions take part in the scan and are left out of the result.

The action for a target follows the slope of its absolute flux:

| Slope | Absolute flux at the last step | Action (MATLAB) | Action (Python) |
| --- | --- | --- | --- |
| positive | any | `OE` (over-express) | `amplify` |
| negative | at most 1e-8 | `KO` (knock out) | `knockout` |
| negative | above 1e-8 | `KD` (knock down) | `knockdown` |

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
fseof = ecFSEOF(ecModel, prodTargetRxn, csRxn, 'nSteps', 16, 'outputFile', true);
fseof.geneTargets
```

The fields `rxnTargets`, `transportTargets` and `geneTargets` list the targets; reaction targets are ordered by the product of slope and correlation. A gene with several targets gets one action: `OE` if any of its reactions is `OE`, otherwise `KO` unless the gene is essential, otherwise `KD`. `geneTargets` also reports whether the gene is essential. With `outputFile` set to `true`, the function writes `ecFSEOF_genes.tsv`, `ecFSEOF_rxns.tsv` and `ecFSEOF_transporter.tsv` to the `output` folder of the project. The biomass reaction is read from the model adapter, and the function warns when the lower bound of `csRxn` is tighter than its uptake at maximum growth.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ec_fseof

result = ec_fseof(ec_model, prod_target_rxn, cs_rxn, n_steps=16)
result.targets
result.gene_targets
```

`result.targets` is one DataFrame with the reaction targets first and the transport targets after them (column `transport`), each group ordered by `score`, the product of the absolute slope and the absolute correlation. `result.scan` holds the fluxes at each step. `ec_fseof` does not test gene essentiality and does not write files; use `cobra.flux_analysis.single_gene_deletion` and `result.targets.to_csv(...)` for these. The biomass reaction is read from `ec_model.adapter`, or from the argument `bio_rxn`. The default `n_steps` is 10, and 16 in MATLAB.
:::
::::

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

## Make a context-specific ecModel

A context-specific GEM of a tissue, cell line or strain is made from a generic GEM with a method such as ftINIT (`ftINIT` in RAVEN, `ftinit` in raven-toolbox). There are two ways to get an ecModel of that context:

| Order | What it needs | Result |
| --- | --- | --- |
| make the context-specific GEM, then build an ecModel from it | the full ecModel workflow per context | each context has its own kcat assignment |
| build one generic ecModel, then trim it with `getSubsetEcModel` | the generic ecModel and the context-specific GEM | all contexts have the kcats of the generic ecModel |

The second way builds the enzyme data once, which saves time when many contexts are made from one generic model, and gives all contexts the same kcats.

`getSubsetEcModel` removes the genes that the context-specific GEM does not have, with the enzymes and reactions that depend on them, and then the reactions whose identifier (without `_REV` and `_EXP_<n>`) is not in the context-specific GEM. The `usage_prot_*` reactions of the remaining enzymes and `prot_pool_exchange` are kept, with their bounds. Both models must come from the same GEM: a reaction of the context-specific GEM that the ecModel does not have raises an error. The function warns when a `usage_prot_*` reaction of the generic ecModel has an upper bound other than 1000, because enzyme concentrations of the generic model may not apply to the context.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecContext = getSubsetEcModel(ecModel, contextGEM);
ecContext = setProtPoolSize(ecContext, PtotContext);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import get_subset_ec_model, set_prot_pool_size

ec_context = get_subset_ec_model(ec_model, context_gem)
set_prot_pool_size(ec_context, p_tot=p_tot_context)
```

`get_subset_ec_model` returns a new `EcModel`; `ec_model` is not changed.
:::
::::

The upper bound of `prot_pool_exchange` is copied from the generic ecModel. Call `setProtPoolSize` with the total protein content of the context when it is different ([Set the protein pool](protein-pool.md)).

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| The protein pool usage or the `usage_prot_*` fluxes have the opposite sign | the ecModel was made with GECKO 3 and was not loaded with `loadEcModel` | Run `upgradeEcModel` (Python: `upgrade_ec_model`) |
| `mapRxnsToConv` or `ecFVA` raises "Not all reactions from model.rxns can be found in the ecModel" | the conventional GEM is not the one that the ecModel was made from | Pass the GEM that `makeEcModel` started from |
| `getSubsetEcModel` raises an error that lists reactions | the context-specific GEM was made from another GEM or another version of it | Make the context-specific GEM from the GEM of the ecModel |
| The `ecFVA` ranges of the ecModel reach 1000 for many reactions | the condition bounds were not set, so only the default bounds limit the fluxes | Set the growth rate and the uptake rates before `ecFVA` |
| Independent sampling chains give different flux distributions | the chains have not converged | Increase `thinning` and the number of samples, and check again |
| `ecFSEOF` returns no targets | no reaction reaches `corrThreshold`, or the production at maximum growth is equal to 90 % of the maximum production, so the scan has one level | Lower `corrThreshold`, or check the bounds of the production and carbon source reactions |

## See also

- [Enzyme usage and bottlenecks](enzyme-usage.md): the enzymes that a solution uses and the enzymes that limit the objective.
- [Basic model operations](basic-model-operations.md): bounds, objectives and flux inspection.
- [Constrain enzymes with proteomics](proteomics.md): the flux data file and the proteomics-constrained ecModel.
- [Set the protein pool](protein-pool.md): the upper bound of `prot_pool_exchange`.
- [API reference](../api/index.md) and [MATLAB vs Python](../matlab-vs-python.md): the signature of each function in the table.
