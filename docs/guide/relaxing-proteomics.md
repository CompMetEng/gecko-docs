# Relax proteomics constraints

Raise the usage bounds of the enzymes that keep an ecModel constrained with proteomics below the measured growth rate, until it reaches that growth rate. The result is an ecModel that reaches the growth rate, a list of the enzymes whose bounds were raised and by how much, and an indication of whether the shortfall comes from the proteomics data, the *k*{sub}`cat` values, the protein pool or the metabolic network.

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
  PV(["Previous: Constrain enzymes with proteomics"]):::ctx
  GR{"Growth reaches the measured growth rate?"}
  FX["flexibilizeEnzConcs (recommended)<br/>perComplex after levelling"]
  RG["relaxProteomicsGreedy"]
  RE["relaxEnzConcs<br/>compare with flexibilizeEnzConcs"]
  IN["inspect the result"]
  GM["constrainFluxData on the conventional GEM<br/>when no method reaches the target"]:::opt
  PV --> GR
  GR -->|no, keep the measured bounds| FX --> IN
  GR -->|no, enzymes at 0 limit growth| RG --> IN
  GR -->|no, independent of the order| RE --> IN
  IN -.-> GM
  NX(["Next: Analyse an ecModel"]):::ctx
  GR -->|yes| NX
  IN --> NX
  click PV href "proteomics.html"
  click NX href "analysis.html"
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
  PV(["Previous: Constrain enzymes with proteomics"]):::ctx
  GR{"Growth reaches the measured growth rate?"}
  FX["flexibilize_enz_concs (recommended)<br/>per_complex after levelling"]
  RG["relax_proteomics_greedy"]
  RE["relax_enz_concs<br/>compare with flexibilize_enz_concs"]
  IN["inspect the result"]
  GM["apply_flux_data_constraints on the conventional GEM<br/>when no method reaches the target"]:::opt
  PV --> GR
  GR -->|no, keep the measured bounds| FX --> IN
  GR -->|no, enzymes at 0 limit growth| RG --> IN
  GR -->|no, independent of the order| RE --> IN
  IN -.-> GM
  NX(["Next: Analyse an ecModel"]):::ctx
  GR -->|yes| NX
  IN --> NX
  click PV href "proteomics.html"
  click NX href "analysis.html"
```
:::
::::
:::::

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `flexibilizeEnzConcs` | `flexibilize_enz_concs` | raises the bound of the most limiting enzyme step by step, then lowers the bounds that the target does not need |
| `relaxProteomicsGreedy` | `relax_proteomics_greedy` | removes the bound of the enzyme with the largest shadow price, one enzyme at a time |
| `relaxEnzConcs` | `relax_enz_concs` | finds the smallest total relaxation in one linear program |
| `constrainFluxData` | `apply_flux_data_constraints` | applies the same exchange fluxes to the conventional GEM, for comparison |

## Setup

An ecModel with concentrations applied as bounds and the exchange fluxes of the same condition, as made in [Constrain enzymes with proteomics](proteomics.md). `flexibilizeEnzConcs` and `relaxProteomicsGreedy` start from a solution of the ecModel, so it must be feasible: apply the growth rate with `'max'`. The target growth rate is the measured growth rate of the condition. Pass it explicitly: by default `flexibilizeEnzConcs` reads `gr_exp` from `model_adapter.toml`, which is the maximum growth rate and can differ from the growth rate of the condition.

## Choose a method

| Method | Change to a bound | Enzymes it can raise | Solves | Returns |
| --- | --- | --- | --- | --- |
| `flexibilizeEnzConcs` | raised in steps, then lowered to the usage that the target needs | enzymes with a concentration above 0 | one per candidate enzyme on every iteration | the ecModel and `flexEnz` |
| `flexibilizeEnzConcs` with `perComplex` | as above, with one factor per complex | as above | one per iteration; one per candidate complex when the solver gives no reduced costs | the ecModel and `flexEnz` |
| `relaxProteomicsGreedy` | set to 1000, one enzyme per step | every enzyme with a usage bound below 1000 | one per relaxed enzyme | `result` and the ecModel |
| `relaxEnzConcs` | raised by the smallest sum of folds, in one linear program | enzymes with a concentration, including 0 | one | the ecModel and `flexEnz` |

`flexibilizeEnzConcs` raises a bound as a factor of the concentration, so an enzyme measured as 0 stays at 0; the function warns and lists these enzymes. An isozyme lowered by `zeroUnmeasuredIsozymes` has no concentration in `ec.concs`, and `relaxProteomicsGreedy` is the method that raises it. `flexibilizeEnzConcs` and `relaxEnzConcs` can raise the protein pool when enzymes do not suffice; `relaxProteomicsGreedy` leaves the pool unchanged.

Use `flexibilizeEnzConcs`, with `perComplex` when the concentrations were levelled with `levelComplexConcs`. Its result keeps the measured bound of every enzyme that the final solution does not need to raise. Use `relaxProteomicsGreedy` when enzymes with a bound of 0 limit growth; each enzyme that it relaxes has no bound of its own afterwards. `relaxEnzConcs` gives a result that does not depend on the order in which enzymes become limiting; compare it with the result of `flexibilizeEnzConcs`. Run each method on the same constrained ecModel: the examples keep `ecModel` (Python: `ec_model`) unchanged and relax a copy. An enzyme that both methods raise is limiting in the data; a conclusion that depends on an enzyme that one method raises and the other does not is uncertain.

## Relax with flexibilizeEnzConcs

On each iteration, `flexibilizeEnzConcs` computes the control coefficient (growth gained per mg/gDCW added) of every measured enzyme whose usage is above 75 % of its bound. It raises the bound of the enzyme with the largest coefficient to concentration × (1 + `foldChange` × k) on its k-th selection, or keeps the current bound when that is higher. With the default `foldChange` of 2, the bound is 3, 5, 7, 9 and 11 times the concentration on the first to fifth selection.

The loop stops in one of four cases:

- The target growth rate is reached.
- No enzyme limits growth. The function then raises the upper bound of `prot_pool_exchange` to the usage needed for the highest growth rate that the pool allows, and this growth rate becomes the target.
- An enzyme is selected more than `iterPerEnzyme` times (default 5; 0 removes the limit). The loop stops and prints a message (MATLAB: a printed line that starts with `WARNING:`, not a MATLAB warning; Python: a logged warning), and the target is not reached.
- The total number of iterations exceeds (`iterPerEnzyme` + 1) times the number of measured enzymes, with 1000 for `iterPerEnzyme` when it is 0. The loop stops and prints such a message, and the target is not reached.

In the first two cases, a final pass minimises the protein pool usage at the target growth rate (± 0.25 %), sets each raised bound to the usage in that solution, and restores the measured concentration where the usage is lower. The function also raises the upper bound of the biomass reaction to the target when it is lower. `ec.concs` keeps the measured values.

With `perComplex`, the measured subunits of a complex (as `getComplexFamilies` groups them, see [Level the concentrations of complexes](proteomics.md#level-the-concentrations-of-complexes)) form one unit. A unit is ranked by the growth gained when all its bounds are raised together: the sum, over the subunits whose usage is above 75 % of the bound, of the reduced cost of the usage reaction times its upper bound. The reduced cost does not include the price of the protein pool, which the shadow price of each `prot_<id>` metabolite includes. When no unit has a score above 0, for example when the solver gives no reduced costs, each candidate unit is tested with its bounds raised by `foldChange` and the protein pool open. The subunits of a unit are raised and lowered by the same factor, so levelled concentrations stay levelled. In a complex that was not levelled, the factor is the one that the most limiting subunit needs, and the bounds of the other subunits are raised by the same factor. The limit of `iterPerEnzyme` counts per complex.

When the ecModel has no solution before the relaxation, the function warns (MATLAB: `flexibilizeEnzConcs:infeasible`) and returns an empty result (MATLAB: a `flexEnz` structure with empty fields).

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[flexModel, flexEnz] = flexibilizeEnzConcs(ecModel, 'expGrowth', fluxData.grRate(1));

% with complexes levelled by levelComplexConcs
[flexModel, flexEnz] = flexibilizeEnzConcs(ecModel, 'expGrowth', fluxData.grRate(1), ...
    'perComplex', true);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import flexibilize_enz_concs

flex_model = ec_model.copy()
flex_result = flexibilize_enz_concs(flex_model, exp_growth=float(flux_data.gr_rate[0]))

# with complexes levelled by level_complex_concs
flex_model = ec_model.copy()
flex_result = flexibilize_enz_concs(
    flex_model, exp_growth=float(flux_data.gr_rate[0]), per_complex=True,
)
```

The copy `flex_model` is changed in place, and `ec_model` keeps the bounds from the proteomics. The progress messages are logged at the level INFO; `logging.basicConfig(level=logging.INFO)` shows them.
:::
::::

## Relax with relaxProteomicsGreedy

`relaxProteomicsGreedy` is the relaxation of the earlier geckopy package ([Carrasco et al. 2023](https://doi.org/10.1128/spectrum.01705-23)). It solves the ecModel, takes the enzyme with the largest absolute shadow price of its `prot_<id>` metabolite among the enzymes with a usage bound below 1000, sets that bound to 1000, and solves again. It stops in one of three cases:

- The target is reached: `converged` is true.
- No candidate is left: a warning, and `converged` is false.
- `maxIterations` (default 100) relaxations are made, the target is not reached and candidates are left: an error.

`enzymeSet` (Python: `enzyme_set`) limits the candidates to a list of UniProt identifiers. The MATLAB function returns `result` and the relaxed ecModel; the Python function changes the ecModel in place and returns `result`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[result, greedyModel] = relaxProteomicsGreedy(ecModel, 'minimalGrowth', fluxData.grRate(1));
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import relax_proteomics_greedy

greedy_model = ec_model.copy()
result = relax_proteomics_greedy(greedy_model, minimal_growth=float(flux_data.gr_rate[0]))
```
:::
::::

## Relax with relaxEnzConcs

`relaxEnzConcs` writes the bound of every enzyme with a concentration as b × (1 + x), where b is the current upper bound (the concentration, or a higher bound from an earlier relaxation), and minimises the sum of the x values under growth ≥ target, in one linear program. A bound raised earlier is therefore never lowered.

- The protein pool can be raised too, at `poolWeight` (Python: `pool_weight`, default 1000) times the price of an enzyme.
- `weight` `'absolute'` minimises the mg/gDCW added; the default `'relative'` minimises the sum of the folds.
- `perComplex` (Python: `per_complex`) gives the measured subunits of a complex one x.
- An enzyme measured as 0 can be raised: its x is scaled by `floor` (default 1e-9 mg/gDCW), which makes it expensive with `'relative'`.
- When no relaxation reaches the target, the function raises the error `relaxEnzConcs:infeasible` (Python: `ValueError`), and the bounds of the ecModel are unchanged.

The function changes the usage bounds and `prot_pool_exchange`, raises the upper bound of the biomass reaction to the target when it is lower, leaves `ec.concs` unchanged, and returns `flexEnz` (Python: `FlexEnzResult`) with `frequence` 1 for every enzyme.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[lpModel, lpEnz] = relaxEnzConcs(ecModel, 'expGrowth', fluxData.grRate(1));
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import relax_enz_concs

lp_model = ec_model.copy()
lp_result = relax_enz_concs(lp_model, exp_growth=float(flux_data.gr_rate[0]))
```
:::
::::

## Inspect the result

`flexEnz` (Python: `FlexEnzResult`) lists the relaxed enzymes, sorted by the ratio of the new bound to the old one, largest first. Its fields are `uniprotIDs`, `oldConcs`, `flexConcs`, `ratioIncr` and `frequence` (the number of times the enzyme was selected); Python uses `uniprot_ids`, `old_concs`, `flex_concs`, `ratio_incr` and `frequence`. An entry `prot_pool` is the protein pool exchange, with its old and new upper bound. The `result` of `relaxProteomicsGreedy` has `trace`, with one step per relaxed enzyme (`relaxedUniprot`, `growthBefore`, `growthAfter`, `shadowPrice`), `relaxed`, which maps each relaxed enzyme to its value in `ec.concs`, `finalGrowth` and `converged`. The result of `relaxEnzConcs` has the fields of `flexEnz`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
disp(struct2table(flexEnz))
disp(struct2table(result.trace))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import pandas as pd

print(pd.DataFrame({
    "uniprot": flex_result.uniprot_ids,
    "old": flex_result.old_concs,
    "new": flex_result.flex_concs,
    "ratio": flex_result.ratio_incr,
    "selected": flex_result.frequence,
}))
print(pd.DataFrame([vars(step) for step in result.trace]))
```
:::
::::

## Interpret a large relaxation

A relaxation corrects for errors in the concentrations. The enzymes that are relaxed, and how much, show which part of the data or the ecModel limits growth:

- **Many enzymes relaxed.** The proteomics data have many uncertain values. Stricter filters in `loadProtData` (for example a lower `maxRSD`) remove the uncertain concentrations, and their enzymes then draw from the protein pool without a bound of their own.
- **One enzyme selected many times**, or `flexibilizeEnzConcs` stops with the warning that the enzyme "seems to be problematic". Its *k*{sub}`cat` can be too low for this condition. Check the *k*{sub}`cat` against its source (see [Check a tuned *k*{sub}`cat` against its source](kcat-tuning.md#check-a-tuned-kcat-against-its-source) and [Choose the *k*{sub}`cat` sources](kcat-sources.md)).
- **The protein pool is raised.** The pool from $P_{tot}$, $f$ and $\sigma$ is smaller than the protein that the condition needs, for example when sigma was fitted to another condition (see [Set the protein pool](protein-pool.md)).
- **No method reaches the target.** `flexibilizeEnzConcs` reports that the protein pool exchange was also not limiting, `relaxProteomicsGreedy` returns `converged` false, or `relaxEnzConcs` raises `relaxEnzConcs:infeasible`. The enzyme constraints do not limit growth: the metabolic network or the exchange fluxes do. Apply the same exchange fluxes to the conventional GEM. If it does not reach the growth rate either, check the exchange fluxes of `fluxData.tsv` and the network.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
model = loadConventionalGEM();
model = constrainFluxData(model, 'fluxData', fluxData, 'condition', 1);
sol = solveLP(model);
fprintf('Growth rate of the GEM: %g /h\n', sol.f)
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_flux_data_constraints, load_conventional_gem

model = load_conventional_gem(ec_model.adapter)
apply_flux_data_constraints(
    model, flux_data, condition=0, bio_rxn=params.bio_rxn, c_source=params.c_source,
)
print(f"Growth rate of the GEM: {model.slim_optimize():g} /h")
```
:::
::::

## Check the *k*{sub}`cat` values of the relaxed enzymes

A *k*{sub}`cat` that is too low makes an enzyme limit growth, and the relaxation then raises the bound of that enzyme. `kcatEvidence` (Python `kcat_evidence`) lists, for the reactions of the relaxed enzymes, the *k*{sub}`cat` of the ecModel next to the *k*{sub}`cat` of every source file (see [Compare *k*{sub}`cat` sources](kcat-evidence.md)):

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, flexEnz] = flexibilizeEnzConcs(ecModel);
[evidence, summary] = kcatEvidence(ecModel, 'enzymes', flexEnz.uniprotIDs);
summary(1:6, :)
```

In the tutorial, `flexibilizeEnzConcs` relaxed 48 enzymes. `summary` has one row per reaction of these enzymes. `tuned` is false, because these *k*{sub}`cat` values were not tuned:

```text
         ecRxn           kcat     tuned    fold    prior      origin            enzymes                eccodes           src_brenda    src_custom    src_ec_tree    src_okp_kinform_h
    ________________    ______    _____    ____    _____    ___________    _________________    _____________________    __________    __________    ___________    _________________

    {'r_0001_EXP_2'}    3.9075    false    NaN      NaN     {'ec_tree'}    {'P32891;P00044'}    {'1.1.2.4'          }       4.185         NaN          3.9075             5.0797
    {'r_0001_EXP_4'}    3.9075    false    NaN      NaN     {'ec_tree'}    {'P39976;P00044'}    {'1.1.2.4;1.1.99.40'}       4.185         NaN          3.9075             5.0797
    {'r_0002_EXP_2'}    3.9075    false    NaN      NaN     {'ec_tree'}    {'P46681;P00044'}    {'1.1.2.4;1.1.99.40'}       4.185         NaN          3.9075             5.0797
    {'r_0004_EXP_2'}    175.75    false    NaN      NaN     {'brenda' }    {'P00044;P00175'}    {'1.1.2.3'          }      175.75         NaN          95.722             5.3818
    {'r_0091_EXP_2'}        10    false    NaN      NaN     {'custom' }    {'P38858'       }    {'3.1.1.31'         }        31.8          10          16.199             8.5428
    {'r_0151'      }    1.3258    false    NaN      NaN     {'ec_tree'}    {'Q05911'       }    {'4.3.2.2'          }         2.9         NaN          1.3258             0.6294
```

:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcat_evidence

result = kcat_evidence(ec_model, enzymes=list(flex_result.uniprot_ids))
result.summary.drop(columns=["eccodes"]).head(6)
```

In the tutorial, `flexibilize_enz_concs` relaxed 48 enzymes. `summary` has one row per reaction of these enzymes. `tuned` is false, because these *k*{sub}`cat` values were not tuned:

```text
         ec_rxn        kcat  tuned  fold  prior   origin        enzymes  src_brenda  src_custom  src_ec_tree  src_okp_kinform_h
0  r_0001_EXP_2    3.907492  False   NaN    NaN  ec_tree  P32891;P00044       4.185         NaN     3.907492           5.079698
1  r_0001_EXP_4    3.907492  False   NaN    NaN  ec_tree  P39976;P00044       4.185         NaN     3.907492           5.079698
2  r_0002_EXP_2    3.907492  False   NaN    NaN  ec_tree  P46681;P00044       4.185         NaN     3.907492           5.079698
3  r_0004_EXP_2  175.750000  False   NaN    NaN   brenda  P00044;P00175     175.750         NaN    95.721999           5.381835
4  r_0091_EXP_2   10.000000  False   NaN    NaN   custom         P38858      31.800        10.0    16.198521           8.542798
5        r_0151    1.325842  False   NaN    NaN  ec_tree         Q05911       2.900         NaN     1.325842           0.629403
```

:::
::::

A *k*{sub}`cat` that is lower than the values of the other sources can be replaced by one of them in `custom.tsv` (see [Set custom *k*{sub}`cat` values](custom-kcats.md)), which removes the cause of the relaxation. A *k*{sub}`cat` within the range of the sources does not explain the relaxation, and the protein pool, the exchange fluxes and the measured concentrations remain to be checked. `flexEnz.uniprotIDs` also lists `prot_pool` after `relaxEnzConcs` when the protein pool exchange was raised; remove it before the call, because `prot_pool` is a pseudo-enzyme that `ec.enzymes` does not list.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| `flexibilizeEnzConcs` warns about enzymes with a concentration of 0 and does not reach the target | a bound of 0 cannot be raised by a factor | Use `relaxProteomicsGreedy`, or load the data with `zerosAsMeasured` false |
| `flexibilizeEnzConcs:infeasible` (Python: a logged warning) and an empty result | the ecModel has no solution before the relaxation | Apply the growth rate with `'max'`; check the exchange fluxes |
| `flexibilize_enz_concs` raises `ValueError` | no enzyme has a concentration, or `exp_growth` is not given and `gr_exp` is not set | Run `fill_enz_concs` and `constrain_enz_concs`; pass `exp_growth` |
| `relaxProteomicsGreedy` raises an error (Python: `RuntimeError`) | `maxIterations` relaxations were made without reaching the target, and candidates are left | Raise `maxIterations`, or use `flexibilizeEnzConcs` |
| The growth rate after `flexibilizeEnzConcs` is slightly below the target | the final pass minimises the pool usage within 0.25 % of the target growth rate | The difference is within 0.25 % of the target |
| The relaxed ecModel is much less constrained than the data | `relaxProteomicsGreedy` sets each relaxed bound to 1000 | Use `flexibilizeEnzConcs` |

## See also

- [Constrain enzymes with proteomics](proteomics.md), where the bounds come from.
- [Enzyme usage and bottlenecks](enzyme-usage.md), to find the enzymes that limit growth without changing the bounds.
- [Choose a *k*{sub}`cat` tuning](kcat-tuning.md), for an enzyme whose *k*{sub}`cat` is too low.
- [Compare *k*{sub}`cat` sources](kcat-evidence.md), the *k*{sub}`cat` values of every source for the reactions of the relaxed enzymes.
