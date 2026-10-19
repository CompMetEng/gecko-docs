# Simulation and analysis

Both light and full ecModels share a conventional GEM's underlying
structure, an S-matrix with vectors of lower and upper bounds, so any method
that works on a conventional GEM also works on an ecModel, in both languages,
regardless of whether it is a light or full one. This page covers the simulation and analysis tasks specific to
ecModels; ordinary FBA, media, and solver setup are covered in
[Getting started](getting-started.md) and apply unchanged. An ecModel is
also usable in other constraint-based toolboxes; SBML is the most portable
exchange format for that, and [ecModel YAML format](yaml-format.md) covers
the format this documentation otherwise uses.

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `setProtPoolSize` | `set_prot_pool_size` | change the protein pool constraint, including turning it off with `Inf` |
| `setParam(..., 'obj', ...)` | `model.objective = ...` | choose the objective: maximize growth, or minimize protein pool usage |
| `mapRxnsToConv` | `map_rxns_to_conv` | map an ecModel flux distribution back onto its starting conventional GEM |
| `getAllowedBounds` / `ecFVA` | `flux_variability_analysis` / `ec_fva` | flux variability, with `ecFVA` mapping the ranges back to the conventional GEM |
| `randomSampling` | `random_sampling` | draw feasible flux vectors and report their distribution |
| `getSubsetEcModel` | `get_subset_ec_model` | trim a generic ecModel down to a context-specific gene/reaction set |

## The protein pool constraint at different growth rates

An ecModel without proteomics integration is a convenient way to study how
the total protein pool constraint affects metabolism as growth rate changes.
At low growth rates, metabolic activity is low and enzymes are usually
available in excess; at high growth rates, activity is high, and fluxes can
become limited by how much enzyme is available at all.

Comparing a normal ecModel against a copy whose protein pool is unconstrained
(`Inf`) isolates that effect, since the unconstrained copy behaves like a
conventional GEM with respect to protein availability:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel_infProt = setProtPoolSize(ecModel, Inf);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import math

from geckopy import set_prot_pool_size

set_prot_pool_size(ec_model_inf, p_tot=math.inf)
```

An `EcModel` is a `cobra.Model`, so cobrapy's methods apply to it directly.
:::
::::

Simulating exchange fluxes across a range of growth rates on both models
shows the difference directly: the unconstrained copy cannot predict the
shift from respiration to fermentation at high growth rate (the Crabtree
effect in yeast), because nothing in it ever runs short of enzyme. Plotting
that comparison needs project-specific code (`plotCrabtree` /
`plot_crabtree` in the `full_ecModel` tutorial bundled with each toolbox,
not part of the general API), since it depends on which exchange reactions
and which reference dataset a given model uses.

:::{admonition} Example output
:class: note
Tuning $k_{cat}$ values (see [Growth-rate tuning](growth-rate-tuning.md))
matters for this comparison too: an ecModel with untuned kcats can fail to
reach realistic growth rates even with the protein pool constraint in place.
In one such comparison, only 13 kcat values needed tuning before the model
exhibited the Crabtree effect: yeast switched from respiration to
fermentation once the protein pool became fully used. The simulated switch
came slightly later than the experimental one (around 0.2 /h simulated vs.
around 0.28 /h observed), suggesting a single enzyme was dominating the
constraint too early; inspecting the top enzyme usages (see [Enzyme usage
and bottlenecks](enzyme-usage-and-bottlenecks.md)) is the way to check that.
:::

## Choosing the objective function

Maximizing growth is the usual objective for FBA on a conventional GEM,
particularly for microbes, and it remains relevant for an ecModel. A second
objective becomes useful once growth is known: minimizing total protein pool
usage, on the assumption that a cell is more likely to use its enzyme
resources efficiently than not.

Maximize growth first:

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

Then fix growth at (99% of, to avoid rounding issues) that value and switch
the objective to minimizing protein pool usage:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'lb', params.bioRxn, 0.99*abs(sol.f));
ecModel = setParam(ecModel, 'obj', 'prot_pool_exchange', 1);
sol = solveLP(ecModel);
fprintf('Minimum protein pool usage: %.2f mg/gDCW\n', abs(sol.f))
```
:::
:::{tab-item} 🐍 Python
:sync: python

cobrapy's dict-form objective takes a coefficient per reaction, so
minimizing `prot_pool_exchange` is a negative weight in an otherwise
ordinary (maximizing) objective:

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

This gives a flux distribution with growth at least 99% of the maximum for
that condition, using enzyme resources as efficiently as the model allows.

:::{admonition} Example output
:class: note
```
Growth rate that is reached: 0.4121 /hour
Minimum protein pool usage: 123.75 mg/gDCW
```
:::

## Comparing flux distributions of different models

An ecModel's flux distribution cannot be compared directly against its
starting conventional GEM: building the ecModel changes the network
structure substantially (isozyme splitting, enzyme usage reactions), so the
two need to be mapped onto a common footing first.

Map an ecModel-derived flux distribution back onto its starting conventional
GEM, combining flux from isozymatic reactions and inverted reversible
reactions back into the single reaction they came from:

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

`map_rxns_to_conv` returns a `MapRxnsResult` bundling the same three arrays
under snake_case names.
:::
::::

The resulting `mappedFlux` / `mapped_flux` vector has the same length and
order as a flux vector from the conventional GEM directly, and can be
treated as any other conventional flux vector from that point on.

:::{warning}
The ecModel passed in must actually derive from the conventional GEM passed
alongside it: reactions are matched by identifier, with no check that the
underlying chemical reaction is still the same. Any stoichiometric change
made beyond the enzyme and proteomics constraints themselves, such as
flipping a reaction's directionality or adding a brand-new reaction, breaks
that correspondence without raising an error.
:::

## Evaluating the solution space

A major benefit of an ecModel over a conventional GEM is a smaller solution
space, which flux variability analysis (FVA) makes visible directly. FVA
works the same way on an ecModel as on any other constraint-based model. To
compare against a conventional GEM's own FVA result, `ecFVA` (Python:
`ec_fva`) maps the ranges straight to the conventional model's reaction ids.

Apply the same exchange flux constraints to three models with a shared basis
for comparison: an ecModel with proteomics integrated (see [Proteomics
integration](proteomics-integration.md)), the same ecModel without
proteomics, and the underlying conventional GEM:

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

`getAllowedBounds` runs plain FVA on the ecModel's own reaction set, without
mapping to the conventional model's reaction ids.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints
from geckopy.utilities import ec_fva

for m in (model, ec_model, ec_model_prot):
    apply_flux_data_constraints(
        m, flux_data,
        condition=0, max_min_growth="max", loose_strict_flux="loose",
    )

fva_bare = ec_fva(model, model)
fva_full = ec_fva(ec_model, model)
fva_prot = ec_fva(ec_model_prot, model)
```

`ec_fva` returns a DataFrame indexed by the conventional model's reaction
ids, with `min_flux` / `max_flux` columns, so there is no need to
pre-allocate a matrix as in MATLAB.

**Performance.** With the default open-source solver (GLPK), `ec_fva` at
yeast-GEM scale (around 4,000 canonical reactions times 3 models times 2 LPs
each) can take well over an hour. Configure a faster solver first
(`ec_model.solver = "gurobi"`, license permitting) before running this at
genome scale, or expect a long run.
:::
::::

### Example output

Visualizing the resulting ranges as a cumulative distribution
(`plotEcFVA` / a project-specific `plot_ec_fva` helper) makes the reduction
in solution space visible directly: the ecModel's median flux variability
runs more than fourfold lower than the conventional GEM's, and over 15% of
the conventional GEM's reactions carry very high flux variability (around
1,000 mmol/gDCWh) that is entirely absent from either ecModel:

| Model | Median flux variability |
|---|---|
| Conventional GEM | 3.104 |
| ecModel, no proteomics | 0.355 |
| ecModel, with proteomics | 0.00325 |

## Sample the solution space

:::{tip} Not part of the original protocol
FVA (above) reports the extremes each reaction can reach one at a time. Flux
sampling instead draws many feasible flux vectors and reports their
distribution, which is the more informative object when the question is
"what does this model actually do", not just "what can it do". Both GECKO's
underlying RAVEN and geckopy's underlying raven-toolbox expose two
Markov-chain Monte Carlo samplers, ACHR (Artificially Centered Hit-and-Run)
and CHRR (Coordinate Hit-and-Run with Rounding), through the same entry
point used for conventional GEMs (`randomSampling(model, ..., 'method',
'achr'|'chrr')` in MATLAB; `random_sampling(model, method="achr"|"chrr")`
in Python). For an ecModel, that choice is not neutral.
:::

**Why CHRR, not the ACHR default, for ecModels.** ACHR is the default
because it is cheaper and mixes adequately on a reasonably well-conditioned
polytope. An ecModel is usually not one. Every `usage_prot` reaction imposes
a capacity bound derived from a $k_{cat}$ and, once proteomics data is
integrated (see [Proteomics integration](proteomics-integration.md)), from a
measured concentration, a combination that tends to overconstrain the
model, meaning many of these bounds sit close to binding at once. Hundreds
of simultaneously near-binding constraints collapse the feasible polytope
into a thin, elongated region rather than a roughly ball-shaped one.

Hit-and-run mixing time scales with a polytope's aspect ratio, the ratio of
its longest to shortest axis. ACHR's step directions come from a set of
warmup points (one flux vector per reaction maximized and minimized), and
on an elongated polytope those directions cluster along the long axes; the
chain moves freely there while rarely crossing the thin ones. The
autocorrelation within a chain drops as usual, so the run looks converged,
but it has explored only a sliver of the true feasible set along the
enzyme-capacity-bound directions that make an ecModel a distinct model in
the first place. This is not a hypothetical failure mode: both toolboxes'
own documentation for the `chrr` method names it directly, MATLAB's
`randomSampling` help text and Python's `random_sampling` docstring each
describing CHRR as intended for better mixing on thin, ill-conditioned
polytopes such as enzyme-constrained models.

CHRR removes the dependency on the original aspect ratio rather than
working around it. Before sampling, it computes the maximum-volume
ellipsoid inscribed in the polytope once and substitutes a rounded
coordinate system built from it; the transformed polytope contains the unit
ball and sits inside a ball of bounded radius regardless of how thin the
original was (Haraldsdóttir et al., 2017). Coordinate hit-and-run then runs
on that rounded space, at the same per-step cost as ACHR once the one-time
rounding is paid. The result is mixing that no longer depends on how many
enzyme constraints happen to be near their limit.

**Practical takeaway is more limited than the mechanism above suggests.**
[raven-docs' convergence
study](https://github.com/edkerk/raven-docs/blob/main/docs/parameter-tuning/studies/sampling-convergence-calibration.md)
measured both methods on a conventional (non-enzyme-constrained) GEM, not
an ecModel, and its results argue against treating CHRR as a
default rather than for it. At genome scale on yeast-GEM, ACHR's default
settings are clearly unconverged (median Gelman-Rubin R-hat 1.17 across
four chains, two in three reactions failing even the loose 1.1 threshold).
CHRR fixes convergence convincingly on a small model (`e_coli_core`, 95
reactions: worst R-hat drops from 1.30 to 1.02) but costs about 20 times
longer there, and a bounded probe at yeast-GEM scale measured roughly 80
minutes of fixed, per-chain rounding cost before a single sample is drawn,
comparable to a full 300-sample ACHR run. That probe had too few samples
for a stable R-hat, so whether CHRR actually converges well at genome scale
is untested, not confirmed; the study's own conclusion is that no cheap,
validated fix exists yet at that scale, for a conventional GEM let alone an
ecModel with tighter constraints on top.

Treat sampled flux ranges from either method as provisional at genome
scale until they have been checked (for example, that R-hat on the
reactions of interest is close to 1 across independent chains), and budget
for CHRR's fixed per-chain cost explicitly if using it, rather than
reaching for it as an assumed drop-in fix.

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

`random_sampling` accepts any `cobra.Model`, an ecModel included, so no
conversion step is needed before sampling it.
:::
::::

## Context-specific models

ecModels reconstructed for higher organisms, such as humans, should not
start from the generic model directly, but from a context-specific model
built with an omics-integration method such as tINIT. There are two ways to
combine contextualization with enzyme-constraining:

1. Contextualize the generic model first, then convert the result to an
   ecModel.
2. Reconstruct a generic ecModel first, then contextualize that.

The second path is faster, and any contextualized ecModel derived from the
same generic ecModel carries the same $k_{cat}$ data, which matters when
reconstructing hundreds of single-cell ecModels from one generic model.

Trim a generic ecModel down to the gene and reaction set of a smaller,
already-contextualized conventional model (both must derive from the same
starting GEM):

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

Matches by canonicalized reaction id and returns a fresh `EcModel` without
mutating `ec_model`.
:::
::::

### Example output

Contextualization and enzyme constraints each shrink the reachable growth
rate on their own, and combine when applied together, for example comparing
maximum growth rates between an unconstrained context-specific GEM, a
generic ecModel, and a context-specific ecModel derived from it:

| Model | Maximum growth rate (/hour) |
|---|---|
| HT29-GEM (context-specific, unconstrained) | 149.97 |
| ecHuman-GEM (generic ecModel) | 0.122 |
| ecHT29-GEM (context-specific ecModel) | 0.086 |

The unconstrained context-specific model's growth rate (149.97 /h) is not
biologically meaningful on its own, since carbon uptake is unconstrained
there; it establishes only that the network stoichiometry allows fast
growth, so the much lower ecModel numbers come from the enzyme constraints
and the contextualization, not from a stoichiometric bottleneck.

## See also

- [GECKO light vs. full ecModels](gecko-light.md), for the runtime and
  accuracy trade-off between the two ecModel layouts.
- [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), what a
  full ecModel's enzyme usage reactions add on top of the analyses here.
- [Proteomics integration](proteomics-integration.md), constructing the
  proteomics-constrained ecModel used in the solution-space comparison above.
- [API reference](../api/index.md) and [MATLAB ↔ Python](../matlab-vs-python.md)
  for the full signature of every function on this page.
