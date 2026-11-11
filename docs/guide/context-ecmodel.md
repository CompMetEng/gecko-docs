# Make a context-specific ecModel

A context-specific GEM describes the metabolism of one tissue, cell line or strain. It is made from a generic GEM with a method such as ftINIT (`ftINIT` in RAVEN, `ftinit` in raven-toolbox). At the end of this page, you have an ecModel of that context, trimmed from a generic ecModel, with a protein pool for the context.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `getSubsetEcModel` | `get_subset_ec_model` | trim a generic ecModel to the reactions and genes of a context-specific GEM |
| `setProtPoolSize` | `set_prot_pool_size` | set the upper bound of the protein pool exchange |

## Setup

The examples use the generic ecModel and the model adapter parameters `params`, loaded as in the setup of [Analyse an ecModel](analysis.md#setup). The other names in the examples are placeholders for values of your project:

| MATLAB | Python | Value |
| --- | --- | --- |
| `contextGEM` | `context_gem` | a context-specific GEM, made from the same GEM (and the same version) as the ecModel |
| `PtotContext` | `p_tot_context` | total protein content of the context, in g/gDCW |

## Choose the order

There are two ways to get an ecModel of a context:

| Order | What it needs | Result |
| --- | --- | --- |
| make the context-specific GEM, then build an ecModel from it | the full ecModel workflow per context | each context has its own kcat assignment |
| build one generic ecModel, then trim it with `getSubsetEcModel` | the generic ecModel and the context-specific GEM | all contexts have the kcats of the generic ecModel |

The second way builds the enzyme data once, which saves time when many contexts are made from one generic model, and gives all contexts the same kcats. The rest of this page describes the second way. For the first way, follow [Build an ecModel](first-ecmodel.md) with the context-specific GEM as the GEM of the project.

## Trim the generic ecModel

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

The upper bound of `prot_pool_exchange` is copied from the generic ecModel. Call `setProtPoolSize` with the total protein content of the context when it is different ([Set the protein pool](protein-pool.md)). Without the values `f` and `sigma`, `setProtPoolSize` reads them from the model adapter.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| `getSubsetEcModel` raises an error that lists reactions | the context-specific GEM was made from another GEM or another version of it | Make the context-specific GEM from the GEM of the ecModel |
| Warning that the ecModel is constrained by protein concentrations | the generic ecModel has measured enzyme concentrations as usage bounds | Trim an ecModel without proteomics constraints, and add the proteomics data of the context afterwards ([Constrain enzymes with proteomics](proteomics.md)) |

## See also

- [Analyse an ecModel](analysis.md): the analyses to run on the context-specific ecModel, and the shared setup.
- [Set the protein pool](protein-pool.md): `Ptot`, `f` and `sigma` of the protein pool.
- [API reference](../api/index.md) and [MATLAB vs Python](../matlab-vs-python.md): the signature of each function in the table.
