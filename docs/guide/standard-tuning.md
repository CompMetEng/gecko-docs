# Tune *k*{sub}`cat` values with sensitivityTuning

`sensitivityTuning` (Python `sensitivity_tuning`) raises the *k*{sub}`cat` values that limit growth, one at a time, until the ecModel reaches one target growth rate, the maximum growth rate of the organism. When the growth rate then ends above the target, `sigmaFitter` (Python `fit_sigma`) lowers the saturation factor $\sigma$ of the protein pool to match it. The result is a tuned ecModel and a list of the changed *k*{sub}`cat` values. [Choose a *k*{sub}`cat` tuning](kcat-tuning.md) compares this tuning with evotune, and describes how to check a tuned *k*{sub}`cat` against its source.

<!-- workflow-place -->
:::::{dropdown} Place in the workflow

The diagram orders the functions of this page within the [workflow](workflow.md). Boxes with a dashed outline are optional steps, a dotted arrow is an optional path, and a diamond is a choice. Rounded boxes with a dotted outline are the context, other pages or the model to start from, and a click on one opens its page.

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
  PV(["Previous: Choose a kcat tuning"]):::ctx
  ST["sensitivityTuning<br/>no change when growth reaches the target"]
  SF["sigmaFitter<br/>lowers sigma when growth is above the target"]:::opt
  CK(["Choose a kcat tuning:<br/>check a tuned kcat"]):::ctx
  PV --> ST -.-> SF
  ST -.-> CK
  NP(["Next: Constrain enzymes with proteomics (optional)"]):::ctx
  NA(["Next: Analyse an ecModel"]):::ctx
  ST --> NP
  ST --> NA
  SF --> NP
  SF --> NA
  click PV href "kcat-tuning.html"
  click CK href "kcat-tuning.html"
  click NP href "proteomics.html"
  click NA href "analysis.html"
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
  PV(["Previous: Choose a kcat tuning"]):::ctx
  ST["sensitivity_tuning<br/>no change when growth reaches the target"]
  SF["fit_sigma<br/>lowers sigma when growth is above the target"]:::opt
  CK(["Choose a kcat tuning:<br/>check a tuned kcat"]):::ctx
  PV --> ST -.-> SF
  ST -.-> CK
  NP(["Next: Constrain enzymes with proteomics (optional)"]):::ctx
  NA(["Next: Analyse an ecModel"]):::ctx
  ST --> NP
  ST --> NA
  SF --> NP
  SF --> NA
  click PV href "kcat-tuning.html"
  click CK href "kcat-tuning.html"
  click NP href "proteomics.html"
  click NA href "analysis.html"
```
:::
::::
:::::

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `sensitivityTuning` | `sensitivity_tuning` | raises the *k*{sub}`cat` that limits growth most, one at a time, until the model reaches a growth rate |
| `sigmaFitter` | `fit_sigma` | fits $\sigma$ so that the model reaches the target growth rate, and sets the protein pool with it; after the tuning, it lowers $\sigma$ when the growth rate is above the target |

## Setup

The examples need an ecModel with assigned *k*{sub}`cat` values (`assignKcats`, see [Choose the *k*{sub}`cat` sources](kcat-sources.md)) and a set protein pool (`setProtPoolSize`, see [Set the protein pool](protein-pool.md)), in the variable `ecModel` (MATLAB) or `ec_model` (Python). The model adapter of the project defines `bio_rxn` and `gR_exp` (Python `gr_exp`); in MATLAB it is the default adapter (`ModelAdapterManager.setDefault`), and in Python it is attached to the model by `load_ec_model(adapter=...)`. The uptake of the carbon source is unconstrained.

## Run sensitivityTuning

`sensitivityTuning` reads the target growth rate and the biomass reaction from the model adapter, and sets growth as the objective. The protein pool must already be set (`setProtPoolSize`, see [Set the protein pool](protein-pool.md)), and the uptake of the carbon source unconstrained.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, tunedKcats] = sensitivityTuning(ecModel);
head(struct2table(tunedKcats), 5)
```

The output in the `full_ecModel` tutorial has one line for each iteration, then the first five tuned reactions:

```text
Iteration 1: Growth: 0.12264
Iteration 2: Growth: 0.14288
Iteration 3: Growth: 0.17898
Iteration 4: Growth: 0.18977
Iteration 5: Growth: 0.20102
Iteration 6: Growth: 0.21066
Iteration 7: Growth: 0.22559
Iteration 8: Growth: 0.23202
Iteration 9: Growth: 0.24004
Iteration 10: Growth: 0.24851
Iteration 11: Growth: 0.25702
Iteration 12: Growth: 0.26489
Iteration 13: Growth: 0.27324
Iteration 14: Growth: 0.28187
Iteration 15: Growth: 0.29095
Iteration 16: Growth: 0.30322
Iteration 17: Growth: 0.31673
Iteration 18: Growth: 0.32726
Iteration 19: Growth: 0.33858
Iteration 20: Growth: 0.3494
Iteration 21: Growth: 0.36002
Iteration 22: Growth: 0.37092
Iteration 23: Growth: 0.38319
Iteration 24: Growth: 0.39368
Iteration 25: Growth: 0.40475
Iteration 26: Growth: 0.41643
          rxns                        rxnNames                       enzymes         oldKcat    newKcat      source
    ________________    ____________________________________    _________________    _______    _______    ___________
    {'r_0005_EXP_3'}    {'1,3-beta-glucan synthase'        }    {'Q04952;P06780'}     3.3451    33.451     {'ec_tree'}
    {'r_0109'      }    {'acetyl-CoA carboxylase, reaction'}    {'P48445;Q00955'}    0.55125    55.125     {'ec_tree'}
    {'r_0157'      }    {'alanyl-tRNA synthetase'          }    {'P40825'       }    0.54102    5.4102     {'ec_tree'}
    {'r_0209'      }    {'arginyl-tRNA synthetase'         }    {'Q05506'       }    0.39054    3.9054     {'ec_tree'}
    {'r_0220'      }    {'Aspartyl-tRNA synthetase'        }    {'P04802'       }     0.2657     2.657     {'ec_tree'}
```

The options are name-value pairs (`sensitivityTuning(ecModel, 'foldChange', 5)`) or positional in the order `desiredGrowthRate, modelAdapter, foldChange, protToIgnore, verbose`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import logging

import pandas as pd
from geckopy import sensitivity_tuning

logging.basicConfig(level=logging.INFO)  # shows the growth rate of each iteration

tuned = sensitivity_tuning(ec_model)
pd.DataFrame({"rxn": tuned.rxns, "enzymes": tuned.enzymes,
              "old_kcat": tuned.old_kcat, "new_kcat": tuned.new_kcat,
              "source": tuned.source}).head(5)
```

The output in the `full_ecModel` tutorial has one line for each iteration, then the first five tuned reactions:

```text
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 1, growth = 0.122635
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 2, growth = 0.142882
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 3, growth = 0.178984
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 4, growth = 0.189773
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 5, growth = 0.201023
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 6, growth = 0.210656
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 7, growth = 0.225593
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 8, growth = 0.232018
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 9, growth = 0.240037
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 10, growth = 0.248511
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 11, growth = 0.257019
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 12, growth = 0.26489
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 13, growth = 0.273242
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 14, growth = 0.281868
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 15, growth = 0.290947
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 16, growth = 0.303218
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 17, growth = 0.316729
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 18, growth = 0.327261
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 19, growth = 0.338582
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 20, growth = 0.349404
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 21, growth = 0.360019
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 22, growth = 0.370918
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 23, growth = 0.383186
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 24, growth = 0.393678
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 25, growth = 0.404747
INFO:geckopy.kcat_tuning.sensitivity_tuning:sensitivity_tuning: iteration 26, growth = 0.416428
            rxn        enzymes  old_kcat   new_kcat   source
0  r_0005_EXP_3  Q04952;P06780  3.345061  33.450611  ec_tree
1        r_0109  P48445;Q00955  0.551250  55.124986  ec_tree
2        r_0157         P40825  0.541024   5.410244  ec_tree
3        r_0209         Q05506  0.390542   3.905418  ec_tree
4        r_0220         P04802  0.265703   2.657027  ec_tree
```

`sensitivity_tuning` changes `ec_model` in place and returns a `TunedKcatsResult`. It reads the target growth rate from `ec_model.adapter`. The options are keyword arguments.
:::
::::

| MATLAB | Python | Default | Meaning |
| --- | --- | --- | --- |
| `desiredGrowthRate` | `desired_growth_rate` | `gR_exp` of the model adapter (Python `gr_exp`) | growth rate at which the tuning stops |
| `foldChange` | `fold_change` | `10` | factor by which a selected *k*{sub}`cat` is multiplied |
| `protToIgnore` | `prot_to_ignore` | none | UniProt IDs of enzymes that are never selected |
| `verbose` | `verbose` | `true` | prints (Python: logs at `INFO`) the growth rate of each iteration |
| `modelAdapter` | | default model adapter | model adapter with the parameters; Python reads `ec_model.adapter` |
| | `max_iterations` | `1000` | maximum number of iterations |
| | `bio_rxn` | `bio_rxn` of the model adapter | biomass reaction that is set as the objective |

The output (`tunedKcats`, Python `TunedKcatsResult`) has one entry per tuned reaction: `rxns`, `rxnNames` (Python `rxn_names`), `enzymes` (joined by `;`), `oldKcat` and `newKcat` (Python `old_kcat`, `new_kcat`), and `source`, the *k*{sub}`cat` source before tuning. `ec.source` of a tuned reaction keeps its origin and detail and gets the tuning status, for example `brenda (wc=0, origin=1) | tuned=sensitivity (prior=0.05)`, where the prior is the *k*{sub}`cat` before the first tuning (see [Provenance of a *k*{sub}`cat`](../gecko4-kcat-assignment.md#provenance-of-a-kcat)). A reaction that an earlier run already tuned keeps the prior of that run. In a light ecModel, every ec row of the tuned reaction gets the status. `ec.notes` does not change. In Python, `tuned.corrections()` returns the changes as a list of `Correction` rows, ordered by fold change.

When two enzymes, or two reactions of the selected enzyme, have equal values (within a relative $10^{-9}$), the one that is first in the model is selected, so MATLAB and Python select the same *k*{sub}`cat` values.

## Lower sigma after the tuning

`sensitivityTuning` multiplies a *k*{sub}`cat` by `foldChange` in each step, so the growth rate after tuning is often above the target. A *k*{sub}`cat` tuning only raises *k*{sub}`cat` values, so it cannot correct this; `sigmaFitter` (Python `fit_sigma`) then selects a $\sigma$ lower than the adapter value at which the growth rate matches the target, and sets the protein pool with that value. Fit $\sigma$ only when the growth rate is above the target: when the tuning stopped below the target (see [Troubleshooting](#troubleshooting)), `sigmaFitter` would raise $\sigma$ and make the pool compensate for *k*{sub}`cat` values that are too low ([Sigma and *k*{sub}`cat` tuning](protein-pool.md#sigma-and-kcat-tuning)).

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
params = ModelAdapterManager.getDefault().getParameters();
[ecModel, tunedKcats] = sensitivityTuning(ecModel);
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
sol = solveLP(ecModel);
if sol.x(strcmp(ecModel.rxns, params.bioRxn)) > params.gR_exp
    ecModel = sigmaFitter(ecModel, 'makePlot', false);
end
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fit_sigma, sensitivity_tuning

params = ec_model.adapter.params
tuned = sensitivity_tuning(ec_model)
ec_model.objective = params.bio_rxn
if ec_model.slim_optimize() > params.gr_exp:
    fit_sigma(ec_model)
```
:::
::::

[Set the protein pool](protein-pool.md#fit-sigma-to-a-growth-rate) describes the options of `sigmaFitter`.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| --- | --- | --- |
| Error that the FBA of the input model gives no valid result (MATLAB), or `ValueError` that the FBA of the input model is not optimal (Python) | The protein pool or the exchange bounds make the model infeasible | Check the exchange bounds and the protein pool (`setProtPoolSize`) |
| Warning that growth does not increase from increased *k*{sub}`cat` values | An exchange bound or the protein pool limits growth | Check the bounds of the uptake reactions; check Ptot, f and sigma |
| Warning that no protein usage reaction carries flux, or that no reaction draws on the protein pool | The protein pool does not limit growth | Check the nutrient bounds and the stoichiometry of the GEM |
| Many *k*{sub}`cat` values are tuned, or one *k*{sub}`cat` is raised several times | The target growth rate is too high, a nutrient uptake is constrained, or the GEM cannot reach the growth rate | Check `gR_exp`, the uptake bounds and the growth rate of the conventional GEM |
| Python `sensitivity_tuning` stops at `max_iterations` | Raising *k*{sub}`cat` values alone does not reach the target growth rate | Check the target growth rate and the bounds |
| `ValueError` that `prot_to_ignore` has no usage reaction for a protein (Python, full ecModel) | The model has no usage reaction for this UniProt ID | Correct the ID |
| Error `sigmaFitter:growthRate` (Python: `ValueError`) | The target growth rate is not above 0 | Set `gR_exp` (Python `gr_exp`) in the model adapter, or give the growth rate |
| Error `GECKO:grExpNotSet`: `gr_exp is not set in model_adapter.toml` | No growth rate is given, and `model_adapter.toml` does not set `gr_exp` | Set `gr_exp`, or give the growth rate |

## See also

- [Choose a *k*{sub}`cat` tuning](kcat-tuning.md), the choice between this tuning and evotune, and the check of a tuned *k*{sub}`cat` against its source.
- [Tune *k*{sub}`cat` values with evotune](evotune.md), the tuning against measured growth rates and fluxes of several conditions.
- [Set the protein pool](protein-pool.md), Ptot, f, sigma and `sigmaFitter`.
- [Set custom *k*{sub}`cat` values](custom-kcats.md), to keep a curated *k*{sub}`cat`.
- [API reference](../api/index.md), every function in both toolboxes.
