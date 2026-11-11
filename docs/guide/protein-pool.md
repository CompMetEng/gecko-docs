# Set the protein pool

The protein pool limits the total mass of enzymes that an enzyme-constrained model (ecModel) can use. The result is an ecModel whose `prot_pool_exchange` has an upper bound calculated from $P_{tot}$, $f$ and $\sigma$, with $\sigma$ fitted to the measured maximum growth rate after the kcats are tuned.

## Functions

| MATLAB | Python | Note |
|---|---|---|
| `setProtPoolSize` | `set_prot_pool_size` | set the upper bound of `prot_pool_exchange` from $P_{tot}$, $f$ and $\sigma$ |
| `calculateFfactor` | `calculate_f_factor` | calculate $f$ from `data/paxDB.tsv` or from proteomics data |
| `loadFluxData` | `load_flux_data` | read `data/fluxData.tsv`, which has a total protein content per condition |
| `sigmaFitter` | `fit_sigma` | fit $\sigma$ so that the ecModel reaches a growth rate |

## Setup

The ecModel has kcats applied (see [Choose the kcat sources](kcat-sources.md)). The adapter keys `sigma`, `p_tot`, `f` and `gr_exp` are described in [Model adapter parameters](model-adapter-parameters.md#model-and-protein-pool).

## The three parameters

`setProtPoolSize` (Python: `set_prot_pool_size`) sets the upper bound of `prot_pool_exchange` to

$$ P_{tot} \cdot f \cdot \sigma \cdot 1000 $$

in mg/gDCW, the same unit as the enzyme cost of the reactions.

| Parameter | TOML key (MATLAB name) | Meaning | Unit | Default |
|---|---|---|---|---|
| $P_{tot}$ | `p_tot` (`Ptot`) | total protein content of the cell | g protein per gDCW | 0.5 |
| $f$ | `f` | mass fraction of the total protein that the enzymes of the ecModel account for | g enzyme/g protein | 0.5 |
| $\sigma$ | `sigma` | average saturation of the enzymes: the fraction of their maximum rate at which the enzymes work in the cell | none, 0 to 1 | 0.5 |

With the three defaults, the bound is 0.5 × 0.5 × 0.5 × 1000 = 125 mg/gDCW.

## Choose where the values come from

| Value | Source | Needs | Section |
|---|---|---|---|
| $P_{tot}$, $f$, $\sigma$ | the model adapter | values from the literature, or the defaults | [Set the pool from the adapter](#set-the-pool-from-the-adapter) |
| $f$ | `calculateFfactor` with `data/paxDB.tsv` | a [PAXdb](https://pax-db.org) abundance file of the organism | [Calculate f](#calculate-f) |
| $f$ | `calculateFfactor` with proteomics data | absolute proteomics data, loaded with `loadProtData` | [Calculate f](#calculate-f) |
| $P_{tot}$ | `data/fluxData.tsv` | a measured total protein content for the condition | [Use the protein content of a condition](#use-the-protein-content-of-a-condition) |
| $\sigma$ | `sigmaFitter` | a measured maximum growth rate | [Fit sigma to a growth rate](#fit-sigma-to-a-growth-rate) |

$P_{tot}$ and $f$ are measured properties of the cell; set them from data when data exist. $\sigma$ has no direct measurement, so it is the parameter that is fitted.

## Set the pool from the adapter

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setProtPoolSize(ecModel);
ecModel = setProtPoolSize(ecModel, 'Ptot', 0.45, 'f', 0.4);
```

Each of `Ptot`, `f` and `sigma` that is not given is read from the model adapter (the default adapter, or the one given as `modelAdapter`). The arguments can also be given by position: `setProtPoolSize(ecModel, Ptot, f, sigma, modelAdapter)`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import set_prot_pool_size

set_prot_pool_size(ec_model)
set_prot_pool_size(ec_model, p_tot=0.45, f=0.4)
```

Each of `p_tot`, `f` and `sigma` that is not given is read from `ec_model.adapter.params`. The function changes `ec_model` in place and returns the bound it set. It raises a `ValueError` when the ecModel has no `prot_pool_exchange`, or when a value is missing and the ecModel has no adapter.
:::
::::

The values given as arguments are not written to `model_adapter.toml`. The next call without arguments uses the adapter values again.

## Calculate f

$f$ is the mass of the measured proteins that are enzymes of the ecModel (in `ec.enzymes`), divided by the mass of all measured proteins. The abundances can be in any unit that is proportional to mass, because the unit cancels in the ratio. The abundances of `data/paxDB.tsv` are numbers of molecules (parts per million), so `calculateFfactor` multiplies them by the molecular weight (MW) of the protein from `data/uniprot.tsv`. The abundances of proteomics data are summed as they are; `loadProtData` gives them in mg/gDCW.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

From `data/paxDB.tsv`:

```matlab
f = calculateFfactor(ecModel);
ecModel = setProtPoolSize(ecModel, 'f', f);
```

`calculateFfactor` maps the genes of `data/paxDB.tsv` to UniProt identifiers through `data/uniprot.tsv`. Without `data/paxDB.tsv`, it prints a warning and returns 0.5.

From proteomics data loaded with `loadProtData` (see [Constrain enzymes with proteomics](proteomics.md)):

```matlab
f = calculateFfactor(ecModel, 'protData', protData);
```

With several samples in `protData`, the abundance of a protein is averaged over the samples in which it is measured. The option `enzymes` replaces `ec.enzymes` as the list of proteins counted as enzymes.
:::
:::{tab-item} 🐍 Python
:sync: python

From `data/paxDB.tsv`:

```python
from geckopy import calculate_f_factor

f = calculate_f_factor(ec_model)
set_prot_pool_size(ec_model, f=f)
```

Without `prot_data`, `calculate_f_factor` reads `data/paxDB.tsv` of the project of `ec_model.adapter` and maps its genes to UniProt identifiers through `data/uniprot.tsv`. Without `data/paxDB.tsv`, it logs a warning and returns 0.5.

From proteomics data loaded with `load_prot_data` (see [Constrain enzymes with proteomics](proteomics.md)):

```python
f = calculate_f_factor(ec_model, prot_data)
```

With several samples, the abundance of a protein is averaged over the samples in which it is measured. The keyword `enzymes` replaces `ec.enzymes` as the list of proteins counted as enzymes.
:::
::::

Both functions return 0 when no measured protein is an enzyme of the ecModel (Python: with a warning). An $f$ of 0, or close to 0, means that the protein identifiers of the data do not match `ec.enzymes`.

## Use the protein content of a condition

`data/fluxData.tsv` has one row per condition, with the total protein content in the column `Ptot` (g/gDCW), the growth rate and the exchange fluxes. The file is described in [Files in the data folder](data-folder-files.md). To set the pool for one condition, give its $P_{tot}$:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
fluxData = loadFluxData();
ecModel = setProtPoolSize(ecModel, 'Ptot', fluxData.Ptot(1));
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import load_flux_data

flux_data = load_flux_data(ec_model.adapter.params.path / "data" / "fluxData.tsv")
set_prot_pool_size(ec_model, p_tot=float(flux_data.p_tot[0]))
```
:::
::::

`constrainFluxData` (Python: `apply_flux_data_constraints`) sets the exchange fluxes and the growth rate of a condition, and does not change the protein pool. [Constrain enzymes with proteomics](proteomics.md) uses $P_{tot}$ and $f$ of the same condition.

## Fit sigma to a growth rate

`sigmaFitter` (Python: `fit_sigma`) sets the protein pool for a series of $\sigma$ values, maximises the objective for each, and selects the $\sigma$ whose growth rate is closest to the target. The target is `gr_exp` of the adapter unless it is given. $P_{tot}$ and $f$ are read from the adapter unless they are given.

Before the scan, both functions set the bounds of the objective reaction to 0 and 1000, and these bounds stay on the returned ecModel. The objective must be the growth reaction. A $\sigma$ at which the model has no solution counts as growth 0. The returned ecModel has the protein pool set for the selected $\sigma$.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, sigma] = sigmaFitter(ecModel, 'makePlot', false);
```

`sigmaFitter` tests $\sigma$ = 0.01, 0.02, ..., 1 and calculates for each the error $100 \times |\mu_{target} - \mu| / \mu_{target}$ in percent. It selects the smallest $\sigma$ whose error is at most the smallest error plus $10^{-9} \times 100 \times \mu_{best} / \mu_{target}$, where $\mu_{best}$ is the growth rate at the $\sigma$ with the smallest error. This tolerance allows a difference in growth rate of a relative $10^{-9}$ of $\mu_{best}$, which keeps rounding differences of the solver from moving the result. When the target is above the growth rate at $\sigma$ = 1 and the growth rate is constant from some $\sigma$ on, the result is the first $\sigma$ of that plateau with every solver.

`sigmaFitter` raises the error `sigmaFitter:growthRate` when the target growth rate is not above 0. The options are `growthRate`, `Ptot`, `f`, `makePlot` (default `true`, a plot of the error against $\sigma$) and `modelAdapter`, as name-value pairs or by position in this order.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fit_sigma

fit = fit_sigma(ec_model)
print(fit.sigma)
```

`fit_sigma` changes `ec_model` in place and returns a `SigmaFitterResult` with `sigma`, and the arrays `sigma_grid`, `growth_grid` and `error_grid` (the error in percent) for a plot. The keywords `growth_rate`, `p_tot` and `f` replace the adapter values; a `growth_rate` that is not above 0 raises a `ValueError`. The keyword `method` selects the search:

- `method="grid"` (default) tests $\sigma$ = 1/n, 2/n, ..., 1 with n = `n_sigma_steps` (default 100, the same values as `sigmaFitter`) and selects the first $\sigma$ with the smallest error. It has no tolerance: when the growth rates on a plateau differ by rounding errors of the solver, the result can be a later $\sigma$ of the plateau.
- `method="bisect"` uses that the growth rate does not decrease when $\sigma$ increases. It searches the smallest $\sigma$ at which the growth rate reaches the target, to a resolution of $10^{-6}$, so the result is in general not a multiple of 0.01. When the growth rate at $\sigma$ 1 is below the target, it searches the smallest $\sigma$ at which the growth rate is within a relative $10^{-9}$ of the growth rate at $\sigma$ 1, the start of the plateau. The arrays of the result contain the $\sigma$ values that were tested.
:::
::::

A $\sigma$ of 1, or a plateau that ends below the target growth rate, means that a larger protein pool does not let the ecModel reach the target. The kcats or the nutrient constraints limit growth.

## Fit sigma or tune the kcats

$\sigma$ changes the protein pool for all enzymes by the same factor. Tuning changes the kcats of the enzymes that limit growth (see [Choose a kcat tuning](kcat-tuning.md)). The order is:

1. Set the pool with the adapter values of $P_{tot}$, $f$ and $\sigma$.
2. Tune the kcats. `sensitivityTuning` solves the model first and stops without a change when the growth rate is at or above the target. Otherwise it multiplies a kcat by `foldChange` (default 10) in each step until the growth rate reaches the target, so the growth rate after tuning is often above the target.
3. Fit $\sigma$. `sigmaFitter` selects the $\sigma$ at which the growth rate matches the target; after a tuning that ended above the target, this $\sigma$ is lower than the adapter value.

A $\sigma$ fitted before the tuning, to an ecModel with kcats that are too low, is close to 1, or is the start of a plateau below the target, and makes the pool compensate for the kcats.

A growth rate below the target can have three causes, checked in this order: the network (the conventional genome-scale metabolic model, GEM, does not reach the target either), the protein pool, and the kcats. To test the pool, remove its bound and compare the growth rate. The minimal protein pool usage at the target growth rate (see [Minimise protein pool usage at fixed growth](analysis.md#minimise-protein-pool-usage-at-fixed-growth)) shows how much enzyme mass the current kcats need. Setting the pool bound to that usage makes the ecModel reach the target, but that bound does not follow from $P_{tot}$, $f$ and $\sigma$; use it as a diagnostic and keep the pool calculated by `setProtPoolSize`.

A fitted $\sigma$ close to 1 means that the enzymes work at their maximum rate on average; check the kcats that limit growth in that case.

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| Error `setProtPoolSize:noPoolExchange` (Python: `ValueError`) that the model has no `prot_pool_exchange` | the model is a conventional GEM, or the reaction was removed after `makeEcModel` | build the ecModel with `makeEcModel` |
| `calculateFfactor` prints a warning and returns 0.5 | there is no `data/paxDB.tsv` and no `protData` was given | add the file, give `protData`, or keep the adapter value of $f$ |
| $f$ is 0 or close to 0 | the protein identifiers of the data do not match `ec.enzymes` | map the identifiers of the data to UniProt identifiers |
| Error `sigmaFitter:growthRate` (Python: `ValueError`) | the target growth rate, given or read from `gr_exp`, is not above 0 | set `gr_exp`, or give the growth rate |
| `fit_sigma` raises a `ValueError` that `model.adapter` is None | the ecModel has no adapter attached, and `growth_rate`, `p_tot` or `f` is not given | attach the adapter, or give `growth_rate`, `p_tot` and `f` |
| The fitted $\sigma$ is 1, or the error is large at every $\sigma$ | the kcats, the nutrient constraints or the network limit growth | see [Fit sigma or tune the kcats](#fit-sigma-or-tune-the-kcats) |
| The growth rate is free after `sigmaFitter` or `fit_sigma`, although its bounds were fixed before | both set the bounds of the objective reaction to 0 and 1000, and the returned ecModel keeps them | set the bounds of the growth reaction again |
| `sigmaFitter` and `fit_sigma` give different $\sigma$ values for the same ecModel | on a growth plateau, `fit_sigma` with `method="grid"` has no tolerance for rounding errors of the solver | use `method="bisect"`, or compare the growth rates in `fit.growth_grid` |

## See also

- [Introduction to ecModels](introduction.md), for the enzyme constraint and the role of the protein pool.
- [Choose a kcat tuning](kcat-tuning.md), when the growth rate stays below the target.
- [Constrain enzymes with proteomics](proteomics.md), for $P_{tot}$ and $f$ of a condition with measured enzyme levels.
