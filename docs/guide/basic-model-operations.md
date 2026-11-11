# Basic model operations

Operations on bounds, the objective and flux distributions that the other guide pages assume. They work on conventional GEMs and ecModels in both languages: RAVEN toolbox functions in MATLAB, cobrapy idioms in Python. At the end of the page a bound is changed, a flux distribution is computed and inspected, and the ecModel is exported.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `setParam` | `Reaction.upper_bound`, `Reaction.lower_bound`, `Model.objective` | sets bounds and the objective |
| `solveLP` | `Model.optimize` | runs FBA, or parsimonious FBA with the argument `1` in MATLAB |
| `getPfbaEnzymes` | `pfba_enzymes` | minimises the total enzyme usage |
| `printFluxes` | `Solution.fluxes` | prints the nonzero fluxes |
| `exportToExcelFormat` | `Series.to_excel` | writes the fluxes to a spreadsheet |
| `exportModel` | `cobra.io.write_sbml_model` | writes an SBML file |

## Setup

A loaded model (`ecModel` in MATLAB, `ec_model` in Python) and, for the objective, the model adapter parameters `params`.

## Set bounds and the objective

Set the upper bound of a reaction to ten:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'ub', 'r_0003', 10);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.reactions.get_by_id("r_0003").upper_bound = 10
```
:::
::::

Set the lower bound of a reaction to zero:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'lb', 'r_0003', 0);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.reactions.get_by_id("r_0003").lower_bound = 0
```
:::
::::

Set the objective to maximise flux through the biomass reaction:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.objective = params.bio_rxn
```
:::
::::

## Run flux balance analysis

Perform FBA, optimising the objective:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
sol = solveLP(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
sol = ec_model.optimize()
```
:::
::::

Perform parsimonious FBA, optimising the objective and minimising the total sum of flux:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
sol = solveLP(ecModel, 1);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from cobra.flux_analysis import pfba

sol = pfba(ec_model)
```
:::
::::

:::::{admonition} Enzyme-aware pFBA
:class: tip

`getPfbaEnzymes` (Python: `pfba_enzymes`) minimises the total enzyme usage, the L1 norm of the `usage_prot_*` fluxes, in place of the total flux of all reactions. [Enzyme usage and bottlenecks](enzyme-usage.md) uses it to find the flux distribution with the least enzyme mass. It is not available for light ecModels, which have no `usage_prot_*` reactions to minimise.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
sol = getPfbaEnzymes(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import pfba_enzymes

sol = pfba_enzymes(ec_model)
```
:::
::::
:::::

## Inspect fluxes

Inspect the nonzero fluxes:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

Through exchange reactions (reactions without substrates or without products, as `getExchangeRxns` defines them; the `usage_prot_<id>` reactions have the protein pool as substrate and the enzyme pseudometabolite as product, so the list contains `prot_pool_exchange` and no usage reaction):

```matlab
printFluxes(ecModel, sol.x)
```

Through all reactions:

```matlab
printFluxes(ecModel, sol.x, false)
```
:::
:::{tab-item} 🐍 Python
:sync: python

`sol.fluxes` is a pandas Series indexed by reaction id, so this is ordinary pandas filtering. Through all reactions:

```python
print(sol.fluxes[sol.fluxes != 0])
```

Restricted to exchange reactions:

```python
exchange_ids = [r.id for r in ec_model.exchanges]
print(sol.fluxes[exchange_ids][sol.fluxes[exchange_ids] != 0])
```
:::
::::

## Export results and models

Export the results to a spreadsheet. The file does not contain content from the `ec` structure and helps to find reaction identifiers quickly:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
exportToExcelFormat(ecModel, 'filename.xlsx');
```
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy has no dedicated spreadsheet exporter; write the solution directly with pandas:

```python
sol.fluxes.to_excel("filename.xlsx")
```
:::
::::

Export the ecModel to an SBML file for use in other constraint-based modelling software:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
exportModel(ecModel, 'filename.xml');
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import cobra

cobra.io.write_sbml_model(ec_model, "filename.xml")
```

As on [Build an ecModel](first-ecmodel.md#7-save-the-ecmodel), this plain-cobrapy SBML export does not retain the `ec_model.ec` fields, the same caveat as MATLAB's `exportModel`.
:::
::::

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| Warning `Reactions not present in model, will be ignored` from `setParam` (Python: `KeyError` from `get_by_id`) | no reaction of the ecModel has this identifier; `makeEcModel` adds the suffixes `_REV` and `_EXP_<n>` to split reactions | use the identifier of the ecModel, for example `r_0003_REV` for the reverse direction |
| Error `Invalid set of bounds for reaction(s)` from `setParam` (Python: `ValueError` from the bound setter) | the new lower bound is above the upper bound, or the reverse | change the other bound first, or set both bounds in one call with `setParam(ecModel, {'lb','ub'}, {rxn, rxn}, [lb ub])` (Python: `Reaction.bounds = (lb, ub)`) |
| `sol.stat` is -1 and `sol.x` is empty (Python: `sol.status` is `infeasible`) | the bounds cannot be met together, for example a fixed growth rate above the growth that the protein pool allows | relax the fixed bounds one at a time to find the bound that makes the problem infeasible |
| Error from `getPfbaEnzymes` that a full ecModel is required (Python: `NotImplementedError`) | the ecModel is light and has no `usage_prot_<id>` reactions | use `solveLP(ecModel, 1)` (Python: `pfba`), or build a full ecModel |
| An ecModel read from an SBML file has no `ec` structure | `exportModel` and `cobra.io.write_sbml_model` do not write the `ec` fields | save the ecModel with `saveEcModel` (Python: `save_ec_model`) as YAML for further GECKO work |

## See also

- [Choose a kcat tuning](kcat-tuning.md)
- [Analyse an ecModel](analysis.md)
- [Enzyme usage and bottlenecks](enzyme-usage.md)
