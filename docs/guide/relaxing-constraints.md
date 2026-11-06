# Relaxing overconstrained proteomics

Constraining individual enzyme concentrations from [proteomics integration](proteomics-integration.md) can leave the ecModel unable to reach its intended growth rate: measurement error in the proteomics data and uncertainty in the $k_{cat}$ values compound, and the model is more constrained than the cell. The usage bounds of the enzymes that limit growth are raised until the target growth rate is reachable. Two algorithms in both toolboxes and a third in geckopy answer the same question (which enzyme bounds are relaxed, and by how much), and they differ in the result they give.

:::{warning}
All functions below apply to full ecModels; see [GECKO light and full ecModels](gecko-light.md).
:::

<!-- workflow-place -->
:::::{dropdown} Place in the workflow

The diagram orders the functions of this page within the [workflow](workflow.md). Dashed boxes are optional and dotted boxes are neighbouring pages.

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
  PV(["Previous: Proteomics integration"]):::ctx
  PV --> D{"Growth reaches the target?"}
  D -->|no, gradual| FX["flexibilizeEnzConcs"]
  D -->|no, fast| GR["relaxProteomicsGreedy"]
  NX(["Next: Simulation and analysis"]):::ctx
  D -->|yes| NX
  FX --> NX
  GR --> NX
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
  PV(["Previous: Proteomics integration"]):::ctx
  PV --> D{"Growth reaches the target?"}
  D -->|no, gradual| FX["flexibilize_enz_concs"]
  D -->|no, fast| GR["relax_proteomics_greedy"]
  D -->|no, smallest total amount| SA["relax_enz_concs"]
  NX(["Next: Simulation and analysis"]):::ctx
  D -->|yes| NX
  FX --> NX
  GR --> NX
  SA --> NX
```
:::
::::
:::::

## Functions

| MATLAB | Python | Note |
|---|---|---|
| `flexibilizeEnzConcs` | `flexibilize_enz_concs` | gradual relaxation ranked by control coefficient, with a tighten-back pass |
| `relaxProteomicsGreedy` | `relax_proteomics_greedy` | single-shot relaxation ranked by shadow price |
| not available | `relax_enz_concs` | smallest total relaxation that reaches the target, found in one LP |
| `getComplexFamilies` | `complex_families` | groups the enzymes of multi-subunit reactions into complexes |

## Setup

The ecModel has `ec.concs` filled and applied as bounds on the `usage_prot_<id>` reactions (`fillEnzConcs` and `constrainEnzConcs`, see [Proteomics integration](proteomics-integration.md)), and an intended growth rate is known. An enzyme with a concentration of 0 (see [Measured zeros](proteomics-integration.md#measured-zeros-and-unmeasured-enzymes)) is not raised by `flexibilizeEnzConcs`, because the upper bound is raised as a factor of the concentration. The function warns and lists the enzymes (MATLAB warning `flexibilizeEnzConcs:measuredZero`, Python: logged warning). `relaxProteomicsGreedy` treats such an enzyme as any other enzyme with a bound below the default and can set its bound back to the default. `flexibilizeEnzConcs` reads the growth rate from `gR_exp` of the model adapter when `expGrowth` is not given (Python: `gr_exp` and `exp_growth`).

## Choice of algorithm

`flexibilizeEnzConcs` / `flexibilize_enz_concs` follows the procedure of the published GECKO pipeline. An iteration computes the control coefficient (the change in growth rate over the change in the enzyme concentration) of every measured enzyme whose usage runs at more than 75 % of its upper bound, and raises the usage upper bound of the enzyme with the largest coefficient. On the k-th selection of the same enzyme the upper bound is `original_concentration * (1 + fold_change * k)`. The loop ends when the target growth rate is reached. A tighten-back pass then finds the flux distribution that minimises protein pool usage at the target growth rate (within a band of 0.25 % growth either side), sets each relaxed bound to the usage in that distribution, and restores the original concentration where the usage is lower. The pass is skipped when the loop stopped on an iteration limit, and the target growth rate is then not reached. The result stays as close to the measured proteomics as the target growth rate allows. Computing the control coefficients re-solves the LP once per candidate enzyme, on every iteration.

`relaxProteomicsGreedy` / `relax_proteomics_greedy` is not part of the published GECKO pipeline (see [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md)). It solves the model once, reads the shadow price of every `prot_<id>` mass-balance constraint from the LP dual, selects the still-constrained enzyme with the largest absolute shadow price and raises its usage upper bound to the default of 1000 in one step. It repeats until the target growth rate is reached. There is no tighten-back pass, so it tends to relax more than the target requires. Each step costs one solve; the control-coefficient algorithm costs one solve per candidate, which matters when one or two enzymes dominate the infeasibility.

| Aspect | `flexibilizeEnzConcs` / `flexibilize_enz_concs` | `relaxProteomicsGreedy` / `relax_proteomics_greedy` |
|---|---|---|
| Selection signal | largest control coefficient (one re-solve per candidate) | largest absolute shadow price (read from one solve) |
| Relaxation step | gradual: the usage upper bound moves by a fold change that compounds on repeated selection of the same enzyme | the usage upper bound is set to the default (1000) |
| Tighten-back | yes, a final pass drops each relaxation that the flux distribution does not need | no, every relaxed enzyme stays unconstrained |
| Result stringency | tight, close to the proteomics data | loose, tends to relax more than necessary |
| Relaxes the protein pool itself | yes, when no single enzyme helps further | no |
| Non-convergence | returns a partial result with a warning | returns a partial result with a warning when the eligible candidates run out first; raises an error when the iteration cap is reached while candidates remain |

`flexibilizeEnzConcs` / `flexibilize_enz_concs` keeps the result closest to the measured proteomics. `relaxProteomicsGreedy` / `relax_proteomics_greedy` gives a fast answer when the infeasibility is dominated by one or two enzymes, and its result is a looser bound on what the data support.

## Gradual relaxation with tighten-back

The usage upper bound of the enzyme with the largest control coefficient is raised, with a fold change of 10 per iteration, until the intended growth rate (0.1 /h) is reached or no enzyme limits growth any more. The tighten-back pass then finds the flux distribution that minimises protein pool usage at the target growth rate (within a band of 0.25 % growth either side), sets each raised bound to the usage in that distribution, and restores the original concentration where the usage is lower. When the loop stopped on an iteration limit, the pass is skipped, the relaxed bounds stay and the target growth rate is not reached. The call is:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, flexEnz] = flexibilizeEnzConcs(ecModel, 0.1, 10);
```

The relaxed levels are bounds of the affected `usage_prot_<id>` reactions. `ecModel.ec.concs` is unchanged and keeps the measured values from `fillEnzConcs`. `flexEnz` has the fields `uniprotIDs`, `oldConcs`, `flexConcs`, `ratioIncr` and `frequence`, sorted by descending `ratioIncr`. The entry `prot_pool` is added when the protein pool exchange was relaxed.

Output in the `full_ecModel` tutorial, whose proteomics and flux data reach 0.0129 /h before the relaxation (the last lines; eight enzymes are relaxed):

```
Protein P46367 UB adjusted. Grow: 0.032826
No (more) limiting enzymes have been found. Attempting to increase protein pool exchange...
Protein pool exchange was also not limiting. Inability to reach growth rate is not related to
enzyme constraints. Maximum growth rate is 0.032826.
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import flexibilize_enz_concs

flex_result = flexibilize_enz_concs(ec_model, exp_growth=0.1, fold_change=10.0)
```

`flexibilize_enz_concs` mutates `ec_model` in place and returns a `FlexEnzResult` with the parallel arrays `uniprot_ids`, `old_concs`, `flex_concs`, `ratio_incr` and `frequence`, the equivalent of `flexEnz` in MATLAB. `ec_model.ec.concs` is unchanged. In the `full_ecModel` tutorial, the function relaxes eight enzymes, logs `protein pool was not limiting either. Maximum growth reachable: 0.0328262` and leaves the model at 0.0327 /h, the same values as in MATLAB.
:::
::::

The enzymes in the result are the modified ones. Flexibilizing a concentration is a response to imprecise protein measurement. When the same enzyme is flexibilized repeatedly, its $k_{cat}$ may cause the shortfall; check the $k_{cat}$ and consider a custom value (see [Applying kcat values](applying-kcats.md) and [Tuning against experimental data](tuning-against-experimental-data.md)). An enzyme that is selected more often than `iterPerEnzyme` (Python: `iter_per_enzyme`, default 5) stops the loop with a warning.

:::{admonition} Many enzymes flexibilized
:class: tip

If the result contains many enzymes, lower-quality proteomics data is the likely cause, and constraining individual enzyme levels sharply reduces the solution space. The total protein amount should stay realistic, and low-quality concentrations should be filtered out before loading (`loadProtData` / `load_prot_data` has several filtering parameters, such as a maximum relative standard deviation). With stricter filtering, the highest-certainty enzyme levels are constrained directly, and the other enzymes draw from the overall protein pool.
:::

### Target growth rate beyond the enzyme constraints

Flexibilization does not always reach the target growth rate. When no limiting enzyme is left, the function raises the protein pool exchange and, if the growth rate does not rise either, reports the maximum growth rate that it reached. The shortfall is then not caused by the enzyme constraints. Applying the same exchange flux constraints to the conventional GEM, with no enzyme constraints, confirms this:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
model = constrainFluxData(model, fluxData);
sol = solveLP(model);
fprintf('Growth rate that is reached: %f /hour\n', abs(sol.f))
```

Output in the `full_ecModel` tutorial:

```
Growth rate that is reached: 0.088037 /hour
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints

apply_flux_data_constraints(
    model, flux_data, bio_rxn=params.bio_rxn, c_source=params.c_source,
)
sol = model.optimize()
print(f"Growth rate that is reached: {sol.objective_value:.4f} /hour")
```
:::
::::

If the conventional GEM reaches the same ceiling, the exchange flux data are the overconstrained part; see [Proteomics integration](proteomics-integration.md) for the loose and strict choice on those constraints.

## Relaxation of complexes

When the concentrations were levelled with `levelComplexConcs` / `level_complex_concs` (see [Proteomics integration](proteomics-integration.md)), all subunits of a complex have one abundance and bind at once, so raising a single subunit does not raise growth. The option `perComplex` of `flexibilizeEnzConcs` (Python: `per_complex`, default false) treats every complex, as grouped by `getComplexFamilies` / `complex_families`, as one enzyme. Enzymes and complexes are ranked by the growth gained when all their usage upper bounds are raised together, every measured subunit of the selected complex is raised by the same factor, iterations are counted per complex, and the final pass keeps one factor per complex, which keeps levelled concentrations levelled. An upper bound is never lowered below its current value. The number of times that a complex was selected is recorded in `frequence` on its first subunit with a concentration above 0.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, flexEnz] = flexibilizeEnzConcs(ecModel, 'expGrowth', 0.1, ...
    'foldChange', 10, 'perComplex', true);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import flexibilize_enz_concs

flex_result = flexibilize_enz_concs(
    ec_model, exp_growth=0.1, fold_change=10.0, per_complex=True,
)
```
:::
::::

## Single-shot shadow-price relaxation

The usage bound of the enzyme with the largest absolute shadow price is raised to the default and the model is solved again, until the target growth rate is reached.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
result = relaxProteomicsGreedy(ecModel, 'minimalGrowth', 0.1);
```

`result.trace` has one row per relaxation step (`iteration`, `relaxedUniprot`, `growthBefore`, `growthAfter`, `shadowPrice`). `result.relaxed` maps each relaxed enzyme to its original `ecModel.ec.concs` value, which allows restoring it. `result.converged` is true when `result.finalGrowth` reaches `minimalGrowth`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import relax_proteomics_greedy

result = relax_proteomics_greedy(ec_model, minimal_growth=0.1)
```

Returns a `GreedyRelaxResult` with `.trace`, `.relaxed`, `.final_growth` and `.converged`.
:::
::::

## Relaxation by the smallest total amount

`relax_enz_concs` has no MATLAB counterpart. It sets the cap of every measured enzyme to `usage <= conc * (1 + x)` and finds, in one LP, the values of `x` with the smallest sum under the constraint that growth reaches `exp_growth`. The protein pool exchange may rise by a fold at `pool_weight` times the price of an enzyme fold. With `weight="relative"` (default) the summed fold increases are minimised; with `weight="absolute"` the mg/gDCW added. With `per_complex=True` the measured subunits of a complex share one `x`. It returns a `FlexEnzResult` as `flexibilize_enz_concs` does, with `frequence` 1 for every entry, and raises `ValueError` when no relaxation reaches `exp_growth`.

```python
from geckopy import relax_enz_concs

flex_result = relax_enz_concs(ec_model, exp_growth=0.1)
```

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| `relaxProteomicsGreedy` returns `converged = false` with a warning (Python: `converged=False`) | the eligible enzymes ran out before the target growth rate was reached | Apply the exchange flux constraints to the conventional GEM; the target may be unreachable for reasons other than enzyme constraints |
| `relaxProteomicsGreedy` raises an error (Python: `RuntimeError`) | `maxIterations` (Python: `max_iterations`, default 100) was reached while candidates remained | Raise `maxIterations`, or use `flexibilizeEnzConcs` |
| The ecModel is less constrained than the proteomics data require | `relaxProteomicsGreedy` has no tighten-back pass | Use `flexibilizeEnzConcs` / `flexibilize_enz_concs` |
| Warning that an enzyme or complex reached its iteration limit (MATLAB: "seems to be problematic") | the same enzyme or complex was selected more often than `iterPerEnzyme` allows | Check the $k_{cat}$ of the enzyme |
| `flexibilizeEnzConcs` warns about enzymes with a concentration of 0 and the growth rate is not reached | the enzymes have an upper bound of 0 that is never raised | Use `relaxProteomicsGreedy`, or load the proteomics data with `zerosAsMeasured` false |
| `flexibilize_enz_concs` raises `ValueError` | no enzyme has a measured concentration, or `exp_growth` is not given and `gr_exp` is not set | Run `fill_enz_concs` and `constrain_enz_concs`, or pass `exp_growth` |

## See also

- [Proteomics integration](proteomics-integration.md), where the constraints that are relaxed here come from.
- [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), which ranks capacity bottlenecks and leaves the constraints unchanged.
- [Applying kcat values](applying-kcats.md), for a repeatedly flexibilized enzyme that points to a $k_{cat}$ problem.
