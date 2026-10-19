# Relaxing overconstrained proteomics

Constraining individual enzyme concentrations from
[proteomics integration](proteomics-integration.md) often leaves the ecModel
unable to reach its intended growth rate: measurement error in the
proteomics data and uncertainty in the $k_{cat}$ values compound, and the
model ends up more constrained than the real cell. Two functions loosen
those constraints until the target growth rate is reachable again. They ask
the same question, "which enzyme bounds should be relaxed, and by how much,
to restore feasible growth", but they answer it differently, and the two
are not interchangeable.

:::{warning}
Both functions apply to full ecModels only; see [GECKO light vs. full
ecModels](gecko-light.md).
:::

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `flexibilizeEnzConcs` | `flexibilize_enz_concs` | gradual, control-coefficient-ranked relaxation with a tighten-back pass |
| `relaxProteomicsGreedy` | `relax_proteomics_greedy` | single-shot, shadow-price-ranked relaxation |

## Two different algorithms

`flexibilizeEnzConcs` / `flexibilize_enz_concs` follows the original GECKO
procedure. At each iteration, it computes the control coefficient of every
still-constrained, measured enzyme (the change in growth rate over the
change in that enzyme's concentration) and increases the concentration of
whichever enzyme has the largest one, by a fold change that compounds each
time that same enzyme is picked again (its upper bound becomes
`original_concentration * (1 + fold_change * pick_count)`). It repeats
until the target growth rate is reached, then runs a tighten-back pass that
minimizes protein pool usage at the target growth rate and drops any
relaxation that turned out not to be needed. The result stays as close to
the measured proteomics as the target growth rate allows, at the cost of
speed: computing each control coefficient re-solves the LP once per
candidate enzyme, on every outer iteration.

`relaxProteomicsGreedy` / `relax_proteomics_greedy` is a GECKO 4 addition,
not part of the original Nature Protocols procedure, and answers the same
question with a different trade-off. It solves the model once to read every
enzyme's shadow price directly from the LP dual, picks the still-constrained
enzyme with the largest absolute shadow price on its mass-balance
constraint, and relaxes it fully back to the default upper bound in one
step, rather than gradually. It repeats until the target growth rate is
reached. There is no tighten-back pass, so it tends to relax more than
strictly necessary, but each step costs one solve rather than one solve per
candidate, which matters when the infeasibility is dominated by one or two
enzymes.

| Aspect | `flexibilizeEnzConcs` / `flexibilize_enz_concs` | `relaxProteomicsGreedy` / `relax_proteomics_greedy` |
|---|---|---|
| Selection signal | largest control coefficient (finite difference; one re-solve per candidate) | largest absolute shadow price (read directly from one solve) |
| Relaxation step | gradual: the usage upper bound moves by a fold change that compounds on repeat picks of the same enzyme | all at once: the usage upper bound jumps straight to the default (effectively unconstrained) |
| Tighten-back | yes, a refinement pass drops any relaxation the final flux distribution did not actually need | no, every relaxed enzyme stays unconstrained |
| Result stringency | tight, the minimal relaxation that is proteomics-faithful | loose, tends to relax more than necessary |
| Falls back to relaxing the protein pool itself | yes, when no single enzyme helps further | no |
| Non-convergence | returns a partial result with a warning | returns a partial result with a warning if eligible candidates run out first; raises an error if the iteration cap is hit while candidates still remain |

Use `flexibilizeEnzConcs` / `flexibilize_enz_concs` as the default when
staying close to the measured proteomics matters. Use
`relaxProteomicsGreedy` / `relax_proteomics_greedy` for a fast answer when
the infeasibility looks like it is dominated by one or two enzymes, and
accept that its result is a looser bound on what the data actually support.

## Gradual relaxation with tighten-back

Increase the concentration of the enzyme with the greatest control
coefficient, tenfold per iteration here, until the intended growth rate
(0.1 /h) is reached. Once reached, the adjusted enzyme levels are reduced
back down to the minimum concentration that still allows the same flux
distribution:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, flexEnz] = flexibilizeEnzConcs(ecModel, 0.1, 10);
```

The flexibilized levels show up as changed constraints on the affected
`usage_prot` reactions. `ecModel.ec.concs` itself is left unchanged and still
reflects the measured values from `fillEnzConcs`; only the bounds of
selected `usage_prot` reactions move.

Progress log for the `full_ecModel` tutorial (abridged):

```
Protein P37299 LB adjusted. Grow: 0.0097884
Protein Q03028 LB adjusted. Grow: 0.012172
Protein P24521 LB adjusted. Grow: 0.012897
Protein P00128 LB adjusted. Grow: 0.013333
[...]
Protein P32473 LB adjusted. Grow: 0.088025
Protein P07285 LB adjusted. Grow: 0.088895
Protein P12695 LB adjusted. Grow: 0.088899
Protein P36148 LB adjusted. Grow: 0.0889
No (more) limiting enzymes have been found. Attempting to increase protein pool exchange...
Protein pool exchange was also not limiting. Inability to reach growth rate is not related to
enzyme constraints. Maximum growth rate is 0.0889.
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import flexibilize_enz_concs

flex_result = flexibilize_enz_concs(ec_model, exp_growth=0.1, fold_change=10.0)
```

`flexibilize_enz_concs` mutates `ec_model` in place and returns a
`FlexEnzResult` with parallel arrays (`uniprot_ids`, `old_concs`,
`flex_concs`, `ratio_incr`), the Python equivalent of MATLAB's `flexEnz`.
:::
::::

Inspect which enzymes were modified. Flexibilizing a concentration is a
reasonable response to imprecise protein measurement, but if the same enzyme
gets flexibilized repeatedly, its $k_{cat}$ may be the actual problem instead
of its measured concentration; check it and consider a custom $k_{cat}$
value (see [Applying kcat values](applying-kcats.md) and
[Tuning against experimental data](tuning-against-experimental-data.md)).

:::{tip} Many enzymes flexibilized
If the flexibilization result touches a large number of enzymes, lower-
quality proteomics data is the likely cause, and constraining individual
enzyme levels sharply reduces the solution space. Check that the total
protein amount stays realistic, and that low-quality concentrations were
filtered out before loading (`loadProtData` / `load_prot_data` exposes
several filtering parameters, such as a maximum relative standard
deviation). Being stricter about which concentrations are kept ensures only
the highest-certainty enzyme levels get constrained directly, while the rest
continue to draw from the overall protein pool.
:::

### Example output

Flexibilization is not always enough on its own to reach the target growth
rate. In the tutorial example, relaxing individual enzymes raises the
maximum growth rate to about 0.0889 /h, and relaxing the protein pool
exchange does not raise it further.

When even relaxing the protein pool exchange itself does not close the gap,
the shortfall is not caused by the enzyme constraints. Applying the same
exchange flux constraints to the conventional GEM, with no enzyme
constraints at all, confirms that directly:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
model = constrainFluxData(model, fluxData);
sol = solveLP(model);
fprintf('Growth rate that is reached: %f /hour\n', abs(sol.f))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints

apply_flux_data_constraints(model, flux_data)
sol = model.optimize()
print(f"Growth rate that is reached: {sol.objective_value:.4f} /hour")
```
:::
::::

If the conventional GEM reaches the same ceiling, the exchange flux data,
not the enzyme constraints, are the overconstrained part; see
[Proteomics integration](proteomics-integration.md) for the loose-vs-strict
choice on those constraints.

## Single-shot shadow-price relaxation

The alternative: solve once, relax the single worst-offending enzyme
completely, and repeat until the target growth rate is reached.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
result = relaxProteomicsGreedy(ecModel, 'minimalGrowth', 0.1);
```

`result.trace` has one row per relaxation step (`iteration`,
`relaxedUniprot`, `growthBefore`, `growthAfter`, `shadowPrice`).
`result.relaxed` maps each relaxed enzyme back to its original
`ecModel.ec.concs` value, so it can be restored later if needed.
`result.converged` is true only if `result.finalGrowth` reaches
`minimalGrowth`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import relax_proteomics_greedy

result = relax_proteomics_greedy(ec_model, minimal_growth=0.1)
```

Returns a `GreedyRelaxResult` with the same shape: `.trace`, `.relaxed`,
`.final_growth`, `.converged`.
:::
::::

:::{warning} What can go wrong
- **Running out of eligible candidates before convergence.** Both languages
  return a partial result with `converged=false` (`converged=False` in
  Python) and a warning, rather than erroring.
- **Exhausting the iteration cap while candidates still remain.** MATLAB
  raises an `error`; Python raises a `RuntimeError`. Both languages error
  regardless in this case, a stricter failure mode than `flexibilizeEnzConcs`
  / `flexibilize_enz_concs`, which never hard-errors on non-convergence.
- **Expecting a minimal relaxation.** `relaxProteomicsGreedy` /
  `relax_proteomics_greedy` has no tighten-back pass, so it typically leaves
  the ecModel less constrained than the proteomics data actually require.
  Use `flexibilizeEnzConcs` / `flexibilize_enz_concs` when that matters.
:::

## See also

- [Proteomics integration](proteomics-integration.md), where the constraints
  being relaxed here come from.
- [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), shadow
  prices used for a different purpose, ranking capacity bottlenecks rather
  than relaxing a constraint.
- [Applying kcat values](applying-kcats.md), for when a repeatedly
  flexibilized enzyme points to a $k_{cat}$ problem instead.
