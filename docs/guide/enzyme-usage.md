# Enzyme usage and bottlenecks

A flux distribution of a full ecModel gives the amount of each enzyme that it uses. At the end of this page, you have the usage of each enzyme in a solution, the enzymes that run at their limit, the enzymes that limit the objective, and the flux distribution that uses the least enzyme mass.

:::{note}
The functions on this page need a full ecModel. A light ecModel has no `usage_prot_<id>` reactions, and the functions raise an error on it ([Choose the ecModel structure](ecmodel-structure.md)).
:::

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `getEnzymeUsage` | `enzyme_usage` | absolute and capacity usage of each enzyme in a flux distribution |
| `reportEnzymeUsage` | `report_enzyme_usage` | tables of the enzymes with the highest absolute usage and with a high capacity usage |
| `getEnzymeBottlenecks` | `get_enzyme_bottlenecks` | rank the enzymes by the rise of the objective when their usage bound is raised |
| `getConcControlCoeffs` | `get_conc_control_coeffs` | rise of the objective per mg/gDCW of added enzyme |
| `getPfbaEnzymes` | `pfba_enzymes` | the flux distribution with the smallest total enzyme usage at the optimum |

## The choice

Each enzyme draws its protein through a usage reaction `usage_prot_<id>`, which runs forward. Its flux is the usage of the enzyme in mg/gDCW. After `makeEcModel`, every usage reaction draws from the shared protein pool (`prot_pool_exchange`) and has an upper bound of 1000 mg/gDCW, so the pool is the only enzyme constraint that can bind. `constrainEnzConcs` changes the usage reaction of each enzyme with a measured concentration: it no longer draws from the pool, and its upper bound is the measured concentration ([Constrain enzymes with proteomics](proteomics.md)).

| Question | Analysis | Useful when |
| --- | --- | --- |
| Which enzymes take most of the protein pool? | absolute usage (`getEnzymeUsage`, `reportEnzymeUsage`) | always; most useful when the protein pool limits the solution |
| Which enzymes run at their measured concentration? | capacity usage (`getEnzymeUsage`, `reportEnzymeUsage`) | enzymes have measured concentrations as upper bounds |
| Which enzymes limit the objective, and by how much? | bottleneck ranking (`getEnzymeBottlenecks`) | enzymes have upper bounds that bind |
| How much does the objective rise per unit of added enzyme? | control coefficients (`getConcControlCoeffs`) | as for the bottleneck ranking |
| What is the smallest proteome that reaches the optimum? | `getPfbaEnzymes` | a flux distribution with the least enzyme mass is wanted |

Usage describes one flux distribution. An LP often has several optimal flux distributions, and their enzyme usage can differ. `getPfbaEnzymes` selects one of them by a stated rule (least enzyme mass), so compute the usage from its solution when you compare conditions.

An enzyme with a high usage does not have to limit the objective, and an enzyme with a low usage that runs at its bound can. The bottleneck ranking answers that question: it raises the bound of one enzyme at a time and solves again. If no enzyme has a bound that binds, which is the normal case without proteomics data, the ranking and the control coefficients are 0 for all enzymes, and the protein pool limits the objective.

## Compute the enzyme usage

`getEnzymeUsage` reads the flux of each usage reaction from a flux distribution. The example fixes the growth rate, minimises the protein pool usage, and reports the enzymes:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'lb', params.bioRxn, growthRate);
ecModel = setParam(ecModel, 'obj', 'prot_pool_exchange', -1);
sol = solveLP(ecModel);
usageData   = getEnzymeUsage(ecModel, sol.x);
usageReport = reportEnzymeUsage(ecModel, usageData);
usageReport.topAbsUsage
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import enzyme_usage, report_enzyme_usage

ec_model.reactions.get_by_id(params.bio_rxn).lower_bound = growth_rate
ec_model.objective = "prot_pool_exchange"
ec_model.objective_direction = "min"
sol = ec_model.optimize()
usage = enzyme_usage(ec_model, sol.fluxes)
report = report_enzyme_usage(ec_model, usage)
report.top_abs_usage
```
:::
::::

The usage data has one entry per enzyme of `ec.enzymes` that has a usage reaction (an enzyme without one is left out with a warning):

| Field (MATLAB / Python) | Content | Unit |
| --- | --- | --- |
| `protID` / `prot_id` | UniProt identifier | |
| `absUsage` / `abs_usage` | absolute usage: the absolute flux of `usage_prot_<id>` | mg/gDCW |
| `UB` / `ub` | upper bound of `usage_prot_<id>`; after `flexibilizeEnzConcs` this can be above the measured concentration | mg/gDCW |
| `capUsage` / `cap_usage` | capacity usage: `absUsage / UB`, the fraction of the available enzyme that the solution uses | fraction |
| `fluxes` | the flux distribution that was given | |
| `measuredProtein`, `demandedProtein`, `demandRatio` (Python: `measured_protein`, `demanded_protein`, `demand_ratio`) | sum of the measured concentrations in `ec.concs`, sum of the absolute usage of the same enzymes, and their ratio | mg/gDCW; ratio |
| `measuredProteinActive`, `demandRatioActive` (Python: `measured_protein_active`, `demand_ratio_active`) | the same, over the measured enzymes with an absolute usage above 1e-7 mg/gDCW | mg/gDCW; ratio |

The option `zero` (Python: `include_zero`, default true) set to false leaves out the enzymes with zero usage. The demand fields are computed over all enzymes with a usage reaction, whatever its value.

For an enzyme without a measured concentration, `UB` is 1000 mg/gDCW, so its capacity usage is close to 0 and has no meaning. Use capacity usage only for enzymes with a measured concentration. When `UB` is 0, the capacity usage is NaN in Python and NaN or Inf in MATLAB.

A `demandRatio` above 1 means that the solution uses more of the measured enzymes than was measured. This happens when the usage bounds are above the measurements, for instance after `flexibilizeEnzConcs` ([Relax proteomics constraints](relaxing-proteomics.md)). A ratio at or below 1 does not exclude that one enzyme exceeds its measurement, because the sum is over all measured enzymes. Measured enzymes that carry no flux increase `measuredProtein`, so `demandRatioActive` shows a conflict among the active enzymes more clearly. The ratio is NaN when no concentration is measured.

## Read the usage report

`reportEnzymeUsage` returns:

| Field (MATLAB / Python) | Content | Option, default |
| --- | --- | --- |
| `topAbsUsage` / `top_abs_usage` | the enzymes with the highest absolute usage, with the usage as a percentage of the upper bound of `prot_pool_exchange`, the kcat, its source and the reaction | `topAbsUsage` (Python: `top_abs_usage`), 10; 0 or `Inf` lists all enzymes |
| `highCapUsage` / `high_cap_usage` | the enzymes with a capacity usage above the threshold, with the same columns and the capacity usage | `highCapUsage` (Python: `high_cap_usage`), 0.9 |
| `totalUsageFlux` / `total_usage_flux` | the upper bound of `prot_pool_exchange`, in mg/gDCW | |
| `demandRatio`, `demandRatioActive` (Python: `demand_ratio`, `demand_ratio_active`) | copied from the usage data | |

An enzyme that catalyses several reactions with flux has one row with the combined usage, marked `===` in the text columns, followed by one row per reaction. In `topAbsUsage`, enzymes whose reactions carry no flux are left out after the top N are selected, so the table can have fewer than N enzymes.

The `source` column shows where the kcat of the reaction came from. An enzyme near the top of `topAbsUsage` with the source `standard` has the standard kcat, a value that GECKO gives to reactions without a kcat from any source ([Choose the kcat sources](kcat-sources.md)). The usage of that enzyme depends on a value that is not specific to it; check the reaction for a measured kcat and put it in `data/kcats/custom.tsv` ([Choose a kcat tuning](kcat-tuning.md)).

## Rank the enzymes that limit the objective

`getEnzymeBottlenecks` solves the model with its current objective. For each enzyme whose usage is at its upper bound (upper bound above 0 and capacity usage at least 1 - 1e-6), it multiplies that bound by `foldChange` (Python: `fold_change`, default 2, must be greater than 1), solves again, and records the rise of the objective as `objectiveGain`. The enzymes are sorted by `objectiveGain`, highest first. An enzyme that is not at its bound gets 0 without a solve, because raising a bound that does not bind cannot change the optimum.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
bottlenecks = getEnzymeBottlenecks(ecModel, 'top', 10);
```

The result is a table sorted by `objectiveGain`. `bottlenecks.Properties.UserData.nResolved` is the number of enzymes that were solved again, and `UserData.activeConstraints` the number of active capacity constraints.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import get_enzyme_bottlenecks

ec_model.objective = params.bio_rxn
bottlenecks = get_enzyme_bottlenecks(ec_model, top=10)
```

The result is a DataFrame indexed by UniProt identifier. `bottlenecks.attrs["n_resolved"]` and `bottlenecks.attrs["active_constraints"]` hold the same two numbers as in MATLAB.
:::
::::

| Column (MATLAB / Python) | Content |
| --- | --- |
| `uniprot` (Python: the index), `gene` | the enzyme |
| `objectiveGain` / `objective_gain` | objective after raising the bound minus the objective before; 0 for enzymes not at their bound, for gains below 1e-10 and for solves that are not optimal |
| `shadowPrice` / `shadow_price` | the dual value of the `prot_<id>` metabolite, for reference |
| `flux` | flux of the usage reaction, in mg/gDCW |
| `capUsage` / `cap_usage` | flux divided by the upper bound; NaN when the upper bound is 0 |
| `upperBound` / `upper_bound` | upper bound of the usage reaction, in mg/gDCW |
| `multipleActive` / `multiple_active` | true when another capacity constraint is active at the same optimum: another enzyme at its bound, or `prot_pool_exchange` at its upper bound |

The shadow price is not used for the order. Enzyme-constrained models often have a degenerate optimum, where several constraints are active and the solver gives the dual value to one of them; the shadow price then depends on the solver and not on the model. Where `multipleActive` is true, the shadow price says little about the single enzyme. `objectiveGain` is computed from a new solve, so it does not depend on the dual values.

`getEnzymeBottlenecks` maximises the objective. In Python, `objective_gain` is the improvement in the direction of the objective, so it is positive for a maximised objective that rises and for a minimised objective that falls.

When no enzyme is at its usage bound, the function gives a warning that no single enzyme limits the objective (MATLAB identifier `getEnzymeBottlenecks:noEnzymeAtBound`; Python: a logged warning). Every `objectiveGain` is then 0, and the warning states whether the protein pool exchange is at its bound.

## Compute control coefficients

`getConcControlCoeffs` raises the upper bound of the usage reaction of each enzyme by `foldChange` (default 2), solves again, and divides the rise of the objective by the rise of the bound. The result is a rise of the objective per mg/gDCW of enzyme (for growth: per hour per mg/gDCW). It is not normalised to a relative (dimensionless) control coefficient. `flexibilizeEnzConcs` uses it to select the enzymes to relax ([Relax proteomics constraints](relaxing-proteomics.md)).

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[evaluated, controlCoeffs] = getConcControlCoeffs(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import get_conc_control_coeffs

evaluated, control_coeffs = get_conc_control_coeffs(ec_model)
```

The option `method="shadow_price"` reads the coefficients from the reduced costs of one solve and checks each nonzero value with one extra solve. MATLAB has only the method of the default, `"finite_difference"`.
:::
::::

Both outputs follow the order of the option `proteins`, which is `ec.enzymes` by default. The option `limit` (default 0) selects the enzymes whose usage divided by the upper bound is above that value; with 0, every enzyme with usage is evaluated.

The two rankings differ in what they divide by. With the default `foldChange` of 2, the bound rises by the bound itself, so the control coefficient is `objectiveGain` divided by the upper bound. An enzyme with a small measured concentration therefore ranks higher by control coefficient than by `objectiveGain`. Use `objectiveGain` to find the enzyme whose doubling raises the objective most, and the control coefficient to find the enzyme where each added mg/gDCW raises the objective most. `getConcControlCoeffs` does not report whether other constraints are active.

## Find the flux distribution with the least enzyme mass

Parsimonious FBA (pFBA) selects, among the optimal flux distributions, the one with the smallest total flux. `getPfbaEnzymes` selects the one with the smallest sum of `usage_prot_*` fluxes, which is the total enzyme mass in mg/gDCW. It solves the model for the current objective (or for the reaction given by `rxnId`, Python: `objective`), keeps the objective at that optimum, and then minimises the sum of the usage fluxes.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
solution = getPfbaEnzymes(ecModel);
solution = getPfbaEnzymes(ecModel, 'fractionOfOptimum', 0.9);
usageData = getEnzymeUsage(ecModel, solution.x);
```

`solution` is the result of `solveLP` with the added fields `enzymeUsage` (the minimised sum of the usage fluxes, mg/gDCW) and `objectiveValue` (the value of the original objective). The help text of the function names the first field `getEnzymeUsage`; the field is `enzymeUsage`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import enzyme_usage, pfba_enzymes

solution = pfba_enzymes(ec_model)
solution = pfba_enzymes(ec_model, fraction_of_optimum=0.9)
usage = enzyme_usage(ec_model, solution.fluxes)
```

`solution` is a `cobra.Solution`.
:::
::::

`fractionOfOptimum` (Python: `fraction_of_optimum`, default 1.0) lets the objective fall from its optimum by `1 - fractionOfOptimum * 0.999999` times the absolute value of the optimum. This also holds for a negative optimum, such as a maximised uptake flux. A value below 1 accepts a lower objective for a smaller enzyme mass.

The usage reactions must have a lower bound of 0. MATLAB raises an error when a usage reaction allows reverse flux; Python includes the reverse flux in the minimised sum.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| Warning that no enzyme is at its usage bound, and every `objectiveGain` is 0 | no enzyme has a usage bound that binds; without proteomics data, only the protein pool can limit the objective | Read `topAbsUsage` for the enzymes that take most of the pool, or constrain enzymes with measured concentrations ([Constrain enzymes with proteomics](proteomics.md)) |
| `multipleActive` is true for the top enzymes | several capacity constraints are active at the same optimum | Use `objectiveGain`; the shadow price does not describe a single enzyme here |
| `highCapUsage` is empty | no enzyme has a measured concentration as its bound, or none is above the threshold | Constrain enzymes with measured concentrations, or lower `highCapUsage` |
| `demandRatio` is NaN | `ec.concs` has no measured concentration | Load proteomics data with `fillEnzConcs` |
| Error that names light ecModels | the ecModel is a light ecModel | Make a full ecModel |
| `getPfbaEnzymes` raises an error about a negative lower bound | a `usage_prot_<id>` reaction allows reverse flux | Set the lower bound of the usage reactions to 0 |
| The usage of the `usage_prot_*` reactions is negative | the ecModel was made with GECKO 3 and was not loaded with `loadEcModel` | Run `upgradeEcModel` (Python: `upgrade_ec_model`) |

## See also

- [Analyse an ecModel](analysis.md): objectives, flux variability and the other analyses of the flux distribution.
- [Constrain enzymes with proteomics](proteomics.md): the measured concentrations that give the enzymes their own bounds.
- [Relax proteomics constraints](relaxing-proteomics.md): `flexibilizeEnzConcs` and `relaxProteomicsGreedy`, which use control coefficients and shadow prices to select the constraints to relax.
- [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md): the direction of the usage reactions and the ranking rule of `getEnzymeBottlenecks`.
- [API reference](../api/index.md) and [MATLAB vs Python](../matlab-vs-python.md): the signature of each function in the table.
