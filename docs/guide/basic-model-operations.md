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
sol.f
```

The growth rate (1/h) of the ecModel of the `full_ecModel` tutorial, with the bounds set above:

```text
ans =
    0.4081
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
sol = ec_model.optimize()
sol.objective_value
```

The growth rate (1/h) of the ecModel of the `full_ecModel` tutorial, with the bounds set above:

```text
0.4080842940317912
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

The exchange fluxes of the solution of `getPfbaEnzymes` for the ecModel of the `full_ecModel` tutorial, in mmol per gDCW and hour, and the flux of `prot_pool_exchange` in mg per gDCW and hour:

```text
EXCHANGE FLUXES:
r_1654	(ammonium exchange):	-2.6862
r_1672	(carbon dioxide exchange):	42.5781
r_1714	(D-glucose exchange):	-27.8831
r_1761	(ethanol exchange):	43.4316
r_1810	(L-glycine exchange):	0.033007
r_1814	(glycolaldehyde exchange):	2.6362e-05
r_1832	(H+ exchange):	11.2236
r_1861	(iron(2+) exchange):	-1.2814e-05
r_1992	(oxygen exchange):	-0.25758
r_2005	(phosphate exchange):	-0.11391
r_2020	(potassium exchange):	-0.0014813
r_2049	(sodium exchange):	-0.0016201
r_2056	(succinate exchange):	5.2536
r_2060	(sulphate exchange):	-0.056825
r_2100	(water exchange):	10.447
r_2111	(growth):	0.40808
r_4593	(chloride exchange):	-0.00052643
r_4594	(Cu2(+) exchange):	-0.00026893
r_4595	(Mn(2+) exchange):	-0.0011141
r_4596	(Zn(2+) exchange):	-0.00030525
r_4597	(Mg(2+) exchange):	-0.00050706
r_4600	(Ca(2+) exchange):	-8.8554e-05
prot_pool_exchange	(prot_pool_exchange):	122.4999
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

The nonzero exchange fluxes of the solution of `pfba_enzymes` for the ecModel of the `full_ecModel` tutorial, in mmol per gDCW and hour:

```text
r_1654    -2.686192
r_1672    42.578070
r_1714   -27.883064
r_1761    43.431601
r_1810     0.033007
r_1814     0.000026
r_1832    11.223602
r_1861    -0.000013
r_1992    -0.257581
r_2005    -0.113915
r_2020    -0.001481
r_2049    -0.001620
r_2056     5.253614
r_2060    -0.056825
r_2100    10.446978
r_4593    -0.000526
r_4594    -0.000269
r_4595    -0.001114
r_4596    -0.000305
r_4597    -0.000507
r_4600    -0.000089
Name: fluxes, dtype: float64
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
| Error `Invalid set of bounds for reaction(s)` from `setParam` (Python: `ValueError` from the bound setter) | the new lower bound is above the upper bound, or the reverse | change the other bound first: to raise both bounds, set the upper bound before the lower bound, and to lower both, the lower bound first (Python: set both at once with `Reaction.bounds = (lb, ub)`) |
| `sol.stat` is -1 and `sol.x` is empty (Python: `sol.status` is `infeasible`) | the bounds cannot be met together, for example a fixed growth rate above the growth that the protein pool allows | relax the fixed bounds one at a time to find the bound that makes the problem infeasible |
| Error from `getPfbaEnzymes` that a full ecModel is required (Python: `NotImplementedError`) | the ecModel is light and has no `usage_prot_<id>` reactions | use `solveLP(ecModel, 1)` (Python: `pfba`), or build a full ecModel |
| An ecModel read from an SBML file has no `ec` structure | `exportModel` and `cobra.io.write_sbml_model` do not write the `ec` fields | save the ecModel with `saveEcModel` (Python: `save_ec_model`) as YAML for further GECKO work |

## See also

- [Choose a *k*{sub}`cat` tuning](kcat-tuning.md)
- [Analyse an ecModel](analysis.md)
- [Enzyme usage and bottlenecks](enzyme-usage.md)
