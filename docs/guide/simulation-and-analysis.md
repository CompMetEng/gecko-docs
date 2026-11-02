# Simulation and analysis

Light and full ecModels have the structure of a conventional GEM, an S-matrix with vectors of lower and upper bounds, so a method for conventional GEMs also runs on an ecModel in both languages. The tasks below are specific to ecModels: the protein pool constraint is varied, growth and protein pool usage are optimised, fluxes are mapped to the conventional GEM, the solution space is compared by FVA and sampled, engineering targets are scanned, and an ecModel is trimmed to a context-specific one. Media and solver setup are those of any model (see [Choosing a solver](../installation/index.md#choosing-a-solver)). [ecModel YAML format](yaml-format.md) describes the file format that this documentation uses.

## Functions

| MATLAB | Python | |
|---|---|---|
| `setProtPoolSize` | `set_prot_pool_size` | change the protein pool constraint, including turning it off with `Inf` |
| `setParam(..., 'obj', ...)` | `model.objective = ...` | choose the objective: maximize growth, or minimize protein pool usage |
| `mapRxnsToConv` | `map_rxns_to_conv` | map an ecModel flux distribution back onto its starting conventional GEM |
| `constrainFluxData` | `apply_flux_data_constraints` | constrain exchange fluxes and growth rate from measured data |
| `getAllowedBounds` / `ecFVA` | `flux_variability_analysis` / `ec_fva` | flux variability, with `ecFVA` mapping the ranges back to the conventional GEM |
| `randomSampling` | `random_sampling` | draw feasible flux vectors and report their distribution |
| `ecFSEOF` | `ec_fseof` | flux scanning with enforced objective function, for metabolic engineering targets |
| `getSubsetEcModel` | `get_subset_ec_model` | trim a generic ecModel down to a context-specific gene and reaction set |

## The protein pool constraint at different growth rates

An ecModel without proteomics integration shows how the total protein pool constraint affects metabolism as the growth rate changes. At low growth rates, metabolic activity is low and enzymes are usually available in excess. At high growth rates, activity is high, and fluxes can be limited by the amount of enzyme.

A copy of the ecModel with an unconstrained protein pool (`Inf`) isolates that effect. The copy behaves like a conventional GEM with respect to protein availability:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel_infProt = setProtPoolSize(ecModel, Inf);
```
:::
:::{tab-item} 🐍 Python
:sync: python

`set_prot_pool_size` changes the model in place and returns the new bound, so the copy is made first:

```python
import math

from geckopy import set_prot_pool_size

ec_model_inf = ec_model.copy()
set_prot_pool_size(ec_model_inf, p_tot=math.inf)
```

An `EcModel` is a `cobra.Model`, so the methods of cobrapy apply to it directly.
:::
::::

Simulating the exchange fluxes over a range of growth rates on both models shows the difference. The copy with the unconstrained pool does not predict the shift from respiration to fermentation at high growth rate (the Crabtree effect in yeast), because no enzyme runs short in it. The comparison is plotted with project-specific code (`plotCrabtree` and `plot_crabtree` in the `full_ecModel` tutorial of each toolbox, outside the general API), because the plot depends on the exchange reactions and the reference dataset of the model.

:::{admonition} Example output
:class: note
The kcat values affect this comparison (see [Growth-rate tuning](growth-rate-tuning.md)): an ecModel with untuned kcats can fail to reach realistic growth rates with the protein pool constraint in place. In the comparison of the published GECKO 3 protocol, 13 kcat values needed tuning before the model showed the Crabtree effect: yeast switched from respiration to fermentation when the protein pool was fully used. The simulated switch occurred earlier than the experimental one (around 0.2 /h simulated and around 0.28 /h observed), which indicates that a single enzyme dominated the constraint too early. The top enzyme usages show whether this is the case (see [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md)).
:::

## Choosing the objective function

Maximising growth is the usual objective of FBA on a conventional GEM, particularly for microbes, and it applies to an ecModel. Once the growth rate is known, minimising the total protein pool usage is a second objective. It assumes that a cell uses its enzyme resources efficiently.

The protein pool exchange `prot_pool_exchange` runs forward, so its flux is the protein pool usage as a positive number. Growth is maximised first:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
sol = solveLP(ecModel);
fprintf('Growth rate that is reached: %.4f /hour\n', abs(sol.f))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.objective = params.bio_rxn
sol = ec_model.optimize()
print(f"Growth rate that is reached: {sol.fluxes[params.bio_rxn]:.4f} /hour")
```
:::
::::

:::{admonition} Example output
:class: note
Output in the `full_ecModel` tutorial, with the tuned kcats and the fitted sigma:

```
Growth rate that is reached: 0.4067 /hour
```
:::

Growth is then fixed at 99 % of that value, which avoids rounding issues, and the objective changes to minimising the protein pool usage:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

`solveLP` maximises the objective. The coefficient -1 in `setParam` minimises the flux of the reaction.

```matlab
ecModel = setParam(ecModel, 'lb', params.bioRxn, 0.99*abs(sol.f));
ecModel = setParam(ecModel, 'obj', 'prot_pool_exchange', -1);
sol = solveLP(ecModel);
fprintf('Minimum protein pool usage: %.2f mg/gDCW\n', abs(sol.f))
```
:::
:::{tab-item} 🐍 Python
:sync: python

The dict form of the objective in cobrapy takes a coefficient per reaction. Minimising `prot_pool_exchange` is a negative weight in a maximising objective:

```python
max_growth = sol.fluxes[params.bio_rxn]
ec_model.reactions.get_by_id(params.bio_rxn).lower_bound = 0.99 * max_growth
ec_model.objective = {
    ec_model.reactions.get_by_id("prot_pool_exchange"): -1.0,
}
sol = ec_model.optimize()
print(f"Minimum protein pool usage: {abs(sol.fluxes['prot_pool_exchange']):.2f} mg/gDCW")
```
:::
::::

Output in the `full_ecModel` tutorial (MATLAB), with the tuned kcats and the fitted sigma:

```
Minimum protein pool usage: 116.33 mg/gDCW
```

The flux distribution has a growth rate of at least 99 % of the maximum for the condition, and it uses the enzyme resources as efficiently as the model allows. The sign of `prot_pool_exchange` and of the `usage_prot_*` fluxes is the opposite in an ecModel from GECKO 3 until `upgradeEcModel` runs (see [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md)).

## Comparing flux distributions of different models

The flux distribution of an ecModel is not directly comparable to that of its starting conventional GEM. The construction of an ecModel changes the network (isozyme splitting, enzyme usage reactions), so both flux distributions are mapped to a common set of reactions.

`mapRxnsToConv` maps a flux distribution of the ecModel to the starting conventional GEM. It combines the fluxes of isozymatic reactions and of inverted reversible reactions into the reaction they came from:

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
mapped_flux, enz_usage_flux, usage_enz = (
    mapped.mapped_flux, mapped.enz_usage_flux, mapped.usage_enz,
)
```

`map_rxns_to_conv` returns a `MapRxnsResult` with the same three arrays under snake_case names.
:::
::::

`mappedFlux` (Python: `mapped_flux`) has the length and the order of a flux vector of the conventional GEM and is used as any other conventional flux vector. `enzUsageFlux` (Python: `enz_usage_flux`) holds the fluxes of the `usage_prot_*` reactions and of `prot_pool_exchange`, which are absent from `mappedFlux`, and `usageEnz` (Python: `usage_enz`) holds their labels (`pool` for the protein pool exchange). These fluxes are positive, because the usage reactions run forward.

:::{admonition} Reaction mapping to the conventional GEM
:class: warning

`mapRxnsToConv` matches reactions by identifier and does not check that the underlying chemical reaction is the same. A stoichiometric change beyond the enzyme and proteomics constraints, such as a flipped directionality or a new reaction, breaks the correspondence without an error. `mapRxnsToConv` raises an error when a reaction of the conventional GEM is missing from the ecModel.
:::

## Evaluating the solution space

An ecModel has a smaller solution space than a conventional GEM, which flux variability analysis (FVA) shows. FVA on an ecModel works as on any constraint-based model. `ecFVA` (Python: `ec_fva`) maps the ranges to the reaction identifiers of the conventional GEM, so the result is comparable to the FVA of the conventional GEM itself.

The same exchange flux constraints are applied to three models: an ecModel with proteomics integrated (see [Proteomics integration](proteomics-integration.md)), the same ecModel without proteomics, and the underlying conventional GEM:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModelProt = constrainFluxData(ecModelProt, fluxData, 1, 'max', 'loose');
ecModel     = constrainFluxData(ecModel, fluxData, 1, 'max', 'loose');
model       = constrainFluxData(model, fluxData, 1, 'max', 'loose');

minFlux = zeros(numel(model.rxns), 3);
maxFlux = minFlux;
[minFlux(:,1), maxFlux(:,1)] = ecFVA(model, model);
[minFlux(:,2), maxFlux(:,2)] = ecFVA(ecModel, model);
[minFlux(:,3), maxFlux(:,3)] = ecFVA(ecModelProt, model);
```

`getAllowedBounds` runs plain FVA on the reaction set of the ecModel, without mapping to the reaction identifiers of the conventional model. `ecFVA` runs in parallel when the Parallel Computing Toolbox is installed (option `runParallel`, default `true`).
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints
from geckopy.utilities import ec_fva

model.adapter = adapter
for m in (model, ec_model, ec_model_prot):
    apply_flux_data_constraints(
        m, flux_data,
        condition=0, max_min_growth="max", loose_strict_flux="loose",
    )

fva_bare = ec_fva(model, model)
fva_full = ec_fva(ec_model, model)
fva_prot = ec_fva(ec_model_prot, model)
```

`load_conventional_gem` returns a plain `cobra.Model` without the attribute `adapter`, which `apply_flux_data_constraints` reads for the biomass reaction, so the adapter is attached to it first. The ecModels carry their adapter. `bio_rxn` and `c_source` can be passed instead.

`ec_fva` returns a DataFrame indexed by the reaction identifiers of the conventional model, with the columns `min_flux` and `max_flux`, so no matrix is pre-allocated as in MATLAB. The option `n_proc` sets the number of worker processes (default `cobra.Configuration().processes`).

`ec_fva` solves two LPs per reaction and model, which is slow with the default open-source solver (GLPK); the run time is not measured here. A faster solver is configured first (`ec_model.solver = "gurobi"`, licence permitting) before the run at genome scale.
:::
::::

### Example output

The ranges are visualised as a cumulative distribution (`plotEcFVA` or a project-specific `plot_ec_fva` helper). In the published GECKO 3 protocol, the median flux variability of the ecModel is more than fourfold lower than that of the conventional GEM, and more than 15 % of the reactions of the conventional GEM have a high flux variability (around 1,000 mmol/gDCWh) that neither ecModel has:

| Model | Median flux variability |
|---|---|
| Conventional GEM | 3.104 |
| ecModel, no proteomics | 0.355 |
| ecModel, with proteomics | 0.00325 |

## Sampling the solution space

:::{admonition} Sampler choice
:class: tip

FVA reports the extremes that each reaction reaches one at a time. Flux sampling draws many feasible flux vectors and reports their distribution, which shows what the model does as well as what it can do. RAVEN, the base of GECKO, and raven-toolbox, the base of geckopy, offer two Markov-chain Monte Carlo samplers through the entry point for conventional GEMs: ACHR (Artificially Centered Hit-and-Run) and CHRR (Coordinate Hit-and-Run with Rounding). The call is `randomSampling(model, ..., 'method', 'achr'|'chrr')` in MATLAB and `random_sampling(model, method="achr"|"chrr")` in Python. The choice of the sampler matters for an ecModel.
:::

ACHR is the default. The documentation of the `chrr` method in both toolboxes (the help text of MATLAB `randomSampling` and the docstring of Python `random_sampling`) names CHRR for better mixing on thin, ill-conditioned polytopes such as enzyme-constrained models.

The [convergence study of raven-docs](https://github.com/edkerk/raven-docs/blob/main/docs/parameter-tuning/studies/sampling-convergence-calibration.md) measured both methods on a conventional GEM; it has no ecModel. At genome scale on yeast-GEM, the default settings of ACHR were not converged: the median Gelman-Rubin R-hat was 1.17 across four chains, and two in three reactions failed even the loose threshold of 1.1. CHRR converged on a small model (`e_coli_core`, 95 reactions: the worst R-hat dropped from 1.30 to 1.02) and took about 20 times longer there. A bounded probe at yeast-GEM scale measured roughly 80 minutes of fixed rounding cost per chain before the first sample, comparable to a full ACHR run of 300 samples. The probe had too few samples for a stable R-hat, so the convergence of CHRR at genome scale is untested.

:::{admonition} Sampled ranges at genome scale
:class: warning

The study concludes that no cheap, validated solution exists yet at that scale. The `chrr` call below is therefore not a validated recipe: sampled flux ranges from either method are provisional at genome scale until they are checked, for example by an R-hat close to 1 on the reactions of interest across independent chains. The fixed rounding cost per chain of CHRR is part of the time budget.
:::

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
solutions = randomSampling(ecModel, 1000, 'method', 'chrr');
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from raven_toolbox.analysis import random_sampling

result = random_sampling(ec_model, n_samples=1000, method="chrr")
```

`random_sampling` accepts any `cobra.Model`, an ecModel included, so no conversion is needed before sampling.
:::
::::

## Scanning for engineering targets

`ecFSEOF` (Python: `ec_fseof`) runs flux scanning with enforced objective function (FSEOF) on an ecModel. It enforces an increasing flux through a production reaction, maximises biomass at each step and then minimises the total flux (`ecFSEOF` calls `solveLP(model, 1)`; `ec_fseof` runs pFBA at each step), and classifies the reactions whose absolute flux correlates with the enforced flux as targets. A reaction is a target when the absolute correlation is at least `corrThreshold` (Python: `correlation_threshold`, default 0.9). The scan runs from the production at the optimum of biomass to 90 % of the maximum production. The reactions that draw enzyme usage (`usage_prot_*`) take part in the classification and are not reported. A target is over expressed (OE) when its flux increases with production, knocked out (KO) when it decreases and is at most 1e-8 at the last step, and knocked down (KD) when it decreases otherwise (MATLAB help of `ecFSEOF`). The function warns when the lower bound of the carbon source reaction is tighter than its uptake at maximum growth.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
fseof = ecFSEOF(ecModel, prodTargetRxn, csRxn);
fseof.geneTargets
```

`fseof.rxnTargets`, `fseof.transportTargets` and `fseof.geneTargets` are the lists of targets. The option `nSteps` sets the number of enforced production levels (default 16), and `outputFile` writes `ecFSEOF_rxns.tsv` and `ecFSEOF_genes.tsv` to the `output` folder of the project.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ec_fseof

result = ec_fseof(ec_model, prod_target_rxn, cs_rxn)
result.targets
```

`result.targets` is a DataFrame with the reaction targets first and the transport targets after them, with a boolean column `transport`. The option `n_steps` sets the number of enforced production levels (default 10).
:::
::::

## Context-specific models

ecModels of higher organisms, such as humans, start from a context-specific model that an omics-integration method such as tINIT builds. Contextualisation and enzyme constraints combine in two ways:

1. The generic model is contextualised first, and the result is converted to an ecModel.
2. A generic ecModel is reconstructed first and then contextualised.

The second path is faster. The contextualised ecModels that derive from one generic ecModel have the same kcat data, which matters for the reconstruction of hundreds of single-cell ecModels from one generic model.

`getSubsetEcModel` trims a generic ecModel to the gene and reaction set of a smaller, contextualised conventional model. Both models derive from the same starting GEM. A warning appears when a `usage_prot_*` reaction of the generic ecModel has an upper bound other than 1000, because the protein concentration constraints of the generic ecModel can be irrelevant in the subset:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecHT29 = getSubsetEcModel(ecModel, HT29);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import get_subset_ec_model

ec_ht29 = get_subset_ec_model(ec_model, ht29)
```

The function matches the canonical reaction identifiers and returns a new `EcModel`; `ec_model` is not changed.
:::
::::

### Example output

Contextualisation and enzyme constraints each lower the reachable growth rate, and the effects combine. The table gives the values of the published GECKO 3 protocol for the maximum growth rate of an unconstrained context-specific GEM, a generic ecModel, and a context-specific ecModel that derives from it:

| Model | Maximum growth rate (/hour) |
|---|---|
| HT29-GEM (context-specific, unconstrained) | 149.97 |
| ecHuman-GEM (generic ecModel) | 0.122 |
| ecHT29-GEM (context-specific ecModel) | 0.086 |

The growth rate of the unconstrained context-specific model (149.97 /h) has no biological meaning, because the carbon uptake is unconstrained. It shows that the stoichiometry of the network allows fast growth, so the lower growth rates of the ecModels result from the enzyme constraints and the contextualisation. A stoichiometric bottleneck is absent.

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| The sign of `prot_pool_exchange` or `usage_prot_*` fluxes is the opposite of the sign in the examples | the ecModel was made with GECKO 3 and these reactions run in reverse | Run `upgradeEcModel` (Python: `upgrade_ec_model`), or reload the model with `loadEcModel` |
| `mapRxnsToConv` raises "Not all reactions from model.rxns can be found in the ecModel" | the ecModel does not derive from the conventional GEM that was passed | Pass the GEM that `makeEcModel` started from |
| `ec_fva` runs for a long time | the default solver is GLPK | Configure a commercial solver, or set `n_proc` |
| `getSubsetEcModel` raises an error that lists reactions of the smaller model | the context-specific model and the ecModel derive from different starting GEMs | Contextualise the GEM that the ecModel is built from |

## See also

- [GECKO light and full ecModels](gecko-light.md), the runtime and accuracy trade-off between the two ecModel layouts.
- [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), the analyses of `getEnzymeUsage`, `getPfbaEnzymes` and `getEnzymeBottlenecks` that the usage reactions of a full ecModel allow.
- [Proteomics integration](proteomics-integration.md), the construction of the proteomics-constrained ecModel of the solution space comparison.
- [Growth-rate tuning](growth-rate-tuning.md), the kcat values that decide the growth rate of the simulation.
- [API reference](../api/index.md) and [MATLAB vs Python](../matlab-vs-python.md), the signature of every function in the table.
