# Enzyme usage and bottlenecks

A full ecModel simulation reports the amount of each enzyme that a flux distribution uses, and which enzyme would raise the objective most if more of it were available. These are three questions with three answers. The usage of every enzyme is ranked for a solved flux distribution, the enzymes that limit the objective are ranked independently of any particular solution, and the flux distribution with the smallest total enzyme mass is found.

:::{warning}
`getEnzymeUsage` / `enzyme_usage`, `getPfbaEnzymes` / `pfba_enzymes` and `getEnzymeBottlenecks` require a full ecModel; see [GECKO light and full ecModels](gecko-light.md).
:::

## Functions

| MATLAB | Python | Note |
|---|---|---|
| `getEnzymeUsage` | `enzyme_usage` | absolute and capacity usage of every enzyme, from a flux distribution |
| `reportEnzymeUsage` | `report_enzyme_usage` | rank that usage data into top-N and high-capacity tables |
| `getEnzymeBottlenecks` | `get_enzyme_bottlenecks` | rank enzymes by the gain of the objective when their usage bound is raised |
| `getPfbaEnzymes` | `pfba_enzymes` | the flux distribution that uses the least enzyme mass at a given objective |

## Setup

A full ecModel, built as described in [Building an empty ecModel](building-ec-model.md), with the constraints of the simulation applied (see [Simulation and analysis](simulation-and-analysis.md)). The usage reactions `usage_prot_<id>` run forward, so the flux through them is not negative (see [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md)).

## Absolute and capacity usage

The usage of an enzyme is read in two ways from a solved model:

- **Absolute usage**, the flux through its `usage_prot_<id>` reaction, in mg/gDCW.
- **Capacity usage**, absolute usage divided by the upper bound of that reaction, the fraction of the available enzyme that the solution uses. The upper bound is not always the concentration recorded in `ec.concs`; it can be a flexibilized value (see [Relaxing overconstrained proteomics](relaxing-constraints.md)).

Enzyme usage is most informative when the total protein pool constraint is limiting, because it shows how the model allocates a scarce resource across the catalysed reactions. Usage is computed from any solved flux distribution, then ranked into the two summary tables:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'obj', 'r_1714', 1);
ecModel = setParam(ecModel, 'lb', params.bioRxn, 0.25);
sol = solveLP(ecModel, 1);
usageData   = getEnzymeUsage(ecModel, sol.x);
usageReport = reportEnzymeUsage(ecModel, usageData);
usageReport.topAbsUsage
```
:::
:::{tab-item} 🐍 Python
:sync: python

`r_1714` (glucose exchange) follows the cobrapy exchange-reaction convention (negative = uptake), so maximising it minimises uptake magnitude:

```python
from cobra.flux_analysis import pfba
from geckopy import enzyme_usage, report_enzyme_usage

ec_model.objective = "r_1714"
ec_model.reactions.get_by_id(params.bio_rxn).lower_bound = 0.25
sol = pfba(ec_model)
usage = enzyme_usage(ec_model, sol.fluxes)
report = report_enzyme_usage(ec_model, usage)
print(report.top_abs_usage.head(10))
```
:::
::::

`reportEnzymeUsage` / `report_enzyme_usage` returns two tables and a total:

- `topAbsUsage` / `top_abs_usage`, the top-N enzymes by absolute usage. The option `topAbsUsage` (Python: `top_abs_usage`) sets N, default 10, and 0 or `Inf` lists all enzymes. `.head(10)` in Python takes the top ten rows of the table.
- `highCapUsage` / `high_cap_usage`, every enzyme above a capacity-usage threshold, not limited to a top-N count. The option `highCapUsage` (Python: `high_cap_usage`) sets the threshold, default 0.9.
- `totalUsageFlux` / `total_usage_flux`, the current upper bound of the protein pool exchange, the denominator of the percentage column.

In `topAbsUsage` / `top_abs_usage`, enzymes whose reactions carry no flux are skipped after the top-N cut, so fewer than N enzymes can be listed. `highCapUsage` / `high_cap_usage` skips them in Python and lists them in MATLAB. An enzyme that catalyses several reactions with flux appears as a combined row marked `===`, followed by one row per reaction.

An ecModel without individual concentrations in `ec.concs` shows an empty `highCapUsage` / `high_cap_usage` table: every enzyme draws from the shared protein pool through a usage reaction with the default upper bound of 1000 mg/gDCW, and capacity usage rarely comes close to that bound. Once individual concentrations constrain the usage reactions of some enzymes (see [Proteomics integration](proteomics-integration.md)), their upper bounds reflect the measured availability, and the capacity usage of those enzymes can approach or reach the threshold.

### Example output

The top ten enzyme usages at a fixed growth rate of 0.25 /h, minimising glucose uptake:

| Protein | Absolute usage (mg/gDCW) | % of pool | kcat (s⁻¹) | Source | Reaction |
|---|---|---|---|---|---|
| P23641 | 8.7 | 7.0 | 12.3 | Standard | Phosphate transport |
| P0CD90 | 5.0 | 4.0 | 12.3 | Standard | Water diffusion |
| Q12233 | 4.7 | 3.8 | 120 | Custom | ATP synthase |
| P36148 | 4.4 | 3.5 | 0.0918 | BRENDA | Glycerol-3-phosphate acyltransferase (16:0), ER membrane |
| P05694 | 3.6 | 2.9 | 0.33 | BRENDA | 5-Methyltetrahydropteroyltriglutamate-homocysteine S-methyltransferase |
| P07256 | 3.3 | 2.7 | 50.8 | DLKcat | Ubiquinol:ferricytochrome c reductase |
| P32895 | 3.3 | 2.6 | 0.66 | BRENDA | Phosphoribosylpyrophosphate synthetase |
| P00163 | 2.9 | 2.3 | 50.8 | DLKcat | Ubiquinol:ferricytochrome c reductase |
| P33312 | 2.8 | 2.3 | 0.000667 | BRENDA | 2,5-Diamino-6-ribosylamino-4(3H)-pyrimidinone 5-phosphate reductase (NADPH) |
| P07257 | 2.7 | 2.1 | 50.8 | DLKcat | Ubiquinol:ferricytochrome c reductase |

Two entries (P23641, P0CD90) carry the standard $k_{cat}$ value, the fallback that GECKO assigns to reactions without a gene association or without any kcat, as a median per subsystem or over all kcats (see [Applying kcat values](applying-kcats.md) and [Kcat assignment](../gecko4-kcat-assignment.md)). A standard $k_{cat}$ near the top of the usage ranking means that the model's estimate of the cost of that enzyme is a fallback, so a literature or BRENDA value for it supersedes a placeholder that carries a large weight in the result.

## Ranking bottlenecks by gain of the objective

Usage shows what the current solution spends its enzyme budget on. A heavily used enzyme can have spare capacity, and a lightly used enzyme at its bound can be the reason that the objective cannot rise. `getEnzymeBottlenecks` / `get_enzyme_bottlenecks` answers that question directly. It solves the model, and for each enzyme that runs at its usage bound (`upperBound` above 0 and `capUsage` at least 1 - 1e-6) it raises the upper bound of the `usage_prot_<id>` reaction by `foldChange` (default 2, greater than 1; Python: `fold_change`) and solves again. The enzymes are ranked by `objectiveGain`, the rise of the objective after that solve. An enzyme that is not at its bound has `objectiveGain` 0 without a solve, because raising a bound that does not bind cannot change the optimum.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
bottlenecks = getEnzymeBottlenecks(ecModel, 'top', 10);
```

Returns a table with one row per enzyme, sorted by descending `objectiveGain`, with the columns `uniprot`, `gene`, `objectiveGain`, `shadowPrice`, `flux`, `capUsage`, `upperBound` and `multipleActive`. The table property `UserData.nResolved` holds the number of enzymes that were solved again, and `UserData.activeConstraints` the number of active capacity constraints.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import get_enzyme_bottlenecks

bottlenecks = get_enzyme_bottlenecks(ec_model, top=10)
```

Returns a pandas DataFrame indexed by uniprot id with the columns `gene`, `objective_gain`, `shadow_price`, `flux`, `cap_usage`, `upper_bound` and `multiple_active`. `bottlenecks.attrs["n_resolved"]` and `bottlenecks.attrs["active_constraints"]` hold the same two numbers.
:::
::::

The columns have these meanings:

| Column (MATLAB / Python) | Meaning |
|---|---|
| `objectiveGain` / `objective_gain` | objective after raising the bound minus the objective before; 0 for enzymes not at their bound, gains below 1e-10 and non-optimal solves; positive for an improvement of a maximised objective (sign note below) |
| `shadowPrice` / `shadow_price` | dual of the `prot_<id>` mass-balance constraint, reported for reference |
| `flux` | flux through the usage reaction |
| `capUsage` / `cap_usage` | absolute flux divided by the upper bound; NaN if the upper bound is 0 |
| `upperBound` / `upper_bound` | upper bound of the usage reaction |
| `multipleActive` / `multiple_active` | true when another capacity constraint is active at the same optimum: another enzyme at its bound, or `prot_pool_exchange` at its upper bound (within 1e-6 relative) |

`getEnzymeBottlenecks` maximises the objective. `get_enzyme_bottlenecks` reports the gain in the direction of the objective: for a minimised objective the gain is the objective of the unchanged model minus the objective after raising the bound, so a positive value is an improvement in both cases.

The shadow price does not enter the order. At a degenerate optimum, which is common in enzyme-constrained models, several constraints are active and the solver assigns the dual to one of them, so the dual depends on the basis. Where `multipleActive` is true, the dual is not informative about a single enzyme. Enzymes with equal `objectiveGain` (rounded to 9 decimals) keep their order in `ec.enzymes`.

When no enzyme is at its usage bound, a warning (MATLAB identifier `getEnzymeBottlenecks:noEnzymeAtBound`; Python: logged) states that no single enzyme limits the objective, every `objectiveGain` is 0 and the rows are in model order. The warning names the protein pool exchange when that is at its bound. `getEnzymeBottlenecks` raises an error on a light ecModel, when `foldChange` is not greater than 1 and when the solve is not optimal. `get_enzyme_bottlenecks` raises a `ValueError` when `fold_change` is not greater than 1 and a `RuntimeError` when the solve is not optimal.

The function is derived from `get_protein_bottlenecks` of the earlier geckopy package ([Carrasco et al., 2023](https://doi.org/10.1128/spectrum.01705-23)). [Relaxing overconstrained proteomics](relaxing-constraints.md) applies the shadow-price signal to a different task: `relaxProteomicsGreedy` / `relax_proteomics_greedy` uses it to pick the next proteomics constraint to loosen, one relaxation step at a time.

## The most parsimonious proteome

Classical parsimonious FBA (pFBA) picks, among all flux distributions that reach the optimum of the objective, the one with the smallest total flux. `getPfbaEnzymes` / `pfba_enzymes` is the enzyme-aware analogue: among the same set of optimal flux distributions, it picks the one with the smallest total enzyme mass, the smallest sum of `usage_prot_*` fluxes. For an ecModel, that usually differs from the answer of classical pFBA, since it optimises the proteome that the flux distribution implies, where classical pFBA optimises the flux magnitudes.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
solution = getPfbaEnzymes(ecModel);
solution = getPfbaEnzymes(ecModel, 'fractionOfOptimum', 0.9);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import pfba_enzymes

solution = pfba_enzymes(ec_model)
solution = pfba_enzymes(ec_model, fraction_of_optimum=0.9)
```
:::
::::

`fractionOfOptimum` / `fraction_of_optimum` (default 1.0) fixes the objective at that fraction of its optimal value, multiplied by 0.999999, before minimising enzyme usage; a value below 1.0 accepts a lower objective value in return for a lower total enzyme mass where one exists. The objective is the current objective of the model, or the reaction given by `rxnId` (Python: the argument `objective`). The MATLAB function returns a structure with the fields `x`, `enzymeUsage`, `objectiveValue` and `stat`; the Python function returns a `cobra.Solution`.

Both implementations require the `usage_prot_<id>` reactions to run forward (`lb = 0`, the layout of a GECKO 4 ecModel). A reaction that was changed to allow reverse flux is handled in Python (its reverse variable is included in the minimised sum) and raises an error in MATLAB, since minimising the raw flux there would not minimise `|flux|` for that reaction.

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| Warning that no enzyme is at its usage bound, and every `objectiveGain` is 0 | the objective is limited by the protein pool exchange or by constraints outside the enzymes | Read `multipleActive` and the usage tables; relax the pool, or inspect the exchange constraints |
| `multipleActive` is true for the top enzymes | several capacity constraints are active at the same optimum | Rank by `objectiveGain`; the shadow price does not identify a single enzyme here |
| `highCapUsage` is empty | no enzyme has a usage bound below 1000 mg/gDCW, or none runs above the threshold | Constrain enzymes with measured concentrations, or lower the threshold |
| An error that names light ecModels | the ecModel is a GECKO light ecModel, which has no `usage_prot_<id>` reactions | Use a full ecModel |
| `getPfbaEnzymes` raises an error about a negative lower bound | a `usage_prot_<id>` reaction allows reverse flux | Set the lower bound of the usage reactions to 0 |

## See also

- [Simulation and analysis](simulation-and-analysis.md), the flux distributions that the usage and bottleneck data are computed from.
- [Relaxing overconstrained proteomics](relaxing-constraints.md), where shadow prices pick the next constraint to relax.
- [GECKO light and full ecModels](gecko-light.md), why `getEnzymeUsage`, `getPfbaEnzymes` and `getEnzymeBottlenecks` do not work on a light ecModel.
