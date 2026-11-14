# Choose a kcat tuning

After the kcats are assigned and the protein pool is set, an ecModel can grow more slowly than the organism. A kcat tuning changes the kcats that limit growth so that the ecModel fits measured data. GECKO has two tunings: `sensitivityTuning` (Python `sensitivity_tuning`) reaches one maximum growth rate, and evotune (`cmaesKcatTuning`, Python `cmaes_kcat_tuning`) fits measured growth rates and exchange fluxes of one or more conditions. This page compares the two, and describes the checks that apply to the result of both: a tuned kcat against its source, and a curated value kept in `custom.tsv`. Each tuning has its own page: [Tune kcats with sensitivityTuning](standard-tuning.md) and [Tune kcats with evotune](evotune.md).

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
  PV(["Previous: Set the protein pool"]):::ctx
  DA{"Measured data"}
  ST(["Tune kcats with sensitivityTuning"]):::ctx
  AT(["Tune kcats with evotune"]):::ctx
  CK["check tuned kcats against their source<br/>loadKcatSource<br/>setKcatForReactions, applyKcatConstraints"]:::opt
  KC(["Set custom kcats<br/>to keep a curated kcat"]):::ctx
  PV --> DA
  DA -->|one maximum growth rate| ST
  DA -->|measured fluxes or several growth rates| AT
  ST -.-> CK
  AT -.-> CK
  CK -.-> KC
  click PV href "protein-pool.html"
  click ST href "standard-tuning.html"
  click AT href "evotune.html"
  click KC href "custom-kcats.html"
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
  PV(["Previous: Set the protein pool"]):::ctx
  DA{"Measured data"}
  ST(["Tune kcats with sensitivity_tuning"]):::ctx
  AT(["Tune kcats with evotune"]):::ctx
  CK["check tuned kcats against their source<br/>load_kcat_source<br/>set_kcat_for_reactions, apply_kcat_constraints"]:::opt
  KC(["Set custom kcats<br/>to keep a curated kcat"]):::ctx
  PV --> DA
  DA -->|one maximum growth rate| ST
  DA -->|measured fluxes or several growth rates| AT
  ST -.-> CK
  AT -.-> CK
  CK -.-> KC
  click PV href "protein-pool.html"
  click ST href "standard-tuning.html"
  click AT href "evotune.html"
  click KC href "custom-kcats.html"
```
:::
::::
:::::

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `sensitivityTuning` | `sensitivity_tuning` | raises the kcat that limits growth most, one at a time, until the model reaches a growth rate; see [Tune kcats with sensitivityTuning](standard-tuning.md) |
| `cmaesKcatTuning` | `cmaes_kcat_tuning` | evotune: fits many kcats at once to measured growth rates and exchange fluxes; see [Tune kcats with evotune](evotune.md) |
| `loadKcatSource` | `load_kcat_source` | reads the rows of a kcat source file in `data/kcats` for the reactions of an ecModel |
| `setKcatForReactions` | `set_kcat_for_reactions` | sets `ec.kcat` of reactions by hand |
| `applyKcatConstraints` | `apply_kcat_constraints` | writes `ec.kcat` into the enzyme constraints of the reactions |

## Setup

The examples need an ecModel with assigned kcats (`assignKcats`, see [Choose the kcat sources](kcat-sources.md)) and a set protein pool (`setProtPoolSize`, see [Set the protein pool](protein-pool.md)), in the variable `ecModel` (MATLAB) or `ec_model` (Python), tuned with one of the two tunings.

## Signs that the model needs a kcat tuning

Maximise growth with flux balance analysis (FBA), with the uptake of the carbon source unconstrained (see [Basic model operations](basic-model-operations.md)). If the growth rate is far below the maximum growth rate of the organism (`gR_exp` in the model adapter, Python `gr_exp`), the enzyme constraints are too tight. Before kcats are changed, check the two other causes of a low growth rate:

- The conventional GEM, with the same exchange bounds, reaches the maximum growth rate. If it does not, the stoichiometry or the bounds of the GEM limit growth, and the GEM is corrected first.
- Ptot, f and sigma of the protein pool are realistic for the organism (see [Set the protein pool](protein-pool.md)).

If both hold, some kcats are too low for the enzymes that carry most of the flux, and a kcat tuning raises them.

## sensitivityTuning or evotune

| Property | `sensitivityTuning` | evotune: `cmaesKcatTuning` |
| --- | --- | --- |
| Data it needs | one maximum growth rate (`gR_exp` in the model adapter, or the option `desiredGrowthRate`) | maximum growth rates (`evotuneMaxGrowth.tsv`), exchange fluxes (`evotuneFluxData.tsv`), or both, measured in one or more conditions |
| What it changes | `ec.kcat` of the reactions it selects, and their enzyme constraints | `ec.kcat` of the kcats with the largest effect on the fit to the data, and their enzyme constraints |
| Which kcats | one reaction per iteration: the reaction with the largest use of the most used enzyme | the top kcats of a screen, up to 90 % of the weighted effect on the fit (option `targetImpactShare`) |
| How much | the kcat is multiplied by `foldChange` (default 10) per iteration; a kcat that is selected again is multiplied again | any value between `min(0.01, k0/100)` and `max(10000, 100*k0)` per s, where `k0` is the kcat before tuning |
| When it stops | the growth rate reaches the target, or growth stops rising | the best root-mean-square error (RMSE) reaches `rmse_threshold` (default 0.2), or after `max_generations` (default 150) generations |
| Cost in time | one FBA per iteration | one FBA per data row for each kcat vector that is scored: two per kcat in the screen, plus `popsize` per generation in the search; runs in parallel with `nProc` |
| Settings | the options of the function | the `[evotune]` table of `model_adapter.toml`, plus `targetImpactShare`, `popsize`, `seed` and `nProc` |
| Protein pool afterwards | `sigmaFitter` lowers $\sigma$ when the growth rate ends above the target | $\sigma$ stays as set before the tuning; the measured growth rates are fitted by the kcats |

In a full ecModel, each iteration of `sensitivityTuning` selects the enzyme whose usage reaction carries the most flux and raises the kcat of the reaction that uses most of that enzyme; in a light ecModel, it raises the kcat of the reaction that draws most from the protein pool. `sensitivityTuning` also stops when an iteration raises growth by 1e-9 per h or less, when the model becomes infeasible, or when no enzyme usage carries flux; Python also stops after `max_iterations` (default 1000).

Evotune weights the effect of each kcat on the fit by the `sigma0_log` of its source, so a kcat from a less trusted source has a larger weight. Python also stops on a convergence criterion of the `cma` package. The `[evotune]` settings set the trust in each kcat source, the weight of growth against flux data, the penalty for moving a kcat, isozyme tying and the stopping rules.

The two tunings are alternatives. When the maximum growth rate of the organism is the sole measured value, use `sensitivityTuning` ([Tune kcats with sensitivityTuning](standard-tuning.md)). With measured growth rates on several carbon sources or measured exchange fluxes, evotune uses those data, and the trust in each kcat source limits how far each kcat moves ([Tune kcats with evotune](evotune.md)).

## Check a tuned kcat against its source

A tuning changes the kcats that limit the fit of the model. It does not check whether the value before tuning was wrong. For each tuned kcat, look up where the value before tuning came from, and search the literature for a measured value.

`ec.source` of a tuned reaction gives the origin of the kcat and the kcat before tuning (`prior`). When the source is a file in `data/kcats` (for example `brenda` or `ec_tree`), `loadKcatSource` returns the rows of that file for the reaction; the `detail` column of a BRENDA row holds the EC wildcard level and the origin of the match (see [BRENDA origin and wildcard levels](kcat-sources.md#brenda-origin-and-wildcard-levels)). `output/<model id>_kcatDecisions.tsv` lists the stage of the assignment that set each kcat (see [Choose the kcat sources](kcat-sources.md)).

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel.ec.source(strcmp(ecModel.ec.rxns, 'r_0079'))
kcatList = loadKcatSource(ecModel, 'brenda');
idx = strcmp(kcatList.rxns, 'r_0079');
table(kcatList.kcats(idx), kcatList.eccodes(idx), kcatList.detail(idx))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import load_kcat_source

print(ec_model.ec.source[ec_model.ec.rxns.index("r_0079")])
kcat_list, _ = load_kcat_source(ec_model, "brenda")
kcat_list[kcat_list["rxn_id"] == "r_0079"]
```
:::
::::

### Example: a kcat from a specific activity

The GECKO tutorial `full_ecModel` builds an ecModel of yeast-GEM. With the preset `gecko_classic`, the order of the GECKO 3 tutorial, `sensitivityTuning` raised the kcat of `r_0079` (5'-phosphoribosylformyl glycinamidine synthetase, enzyme P38972). The kcat before tuning, 0.05 per s, came from a BRENDA match with wildcard level 0 and origin 4 (closest organism, any substrate; see [BRENDA origin and wildcard levels](kcat-sources.md#brenda-origin-and-wildcard-levels)) for EC 6.3.5.3.

[BRENDA](https://www.brenda-enzymes.org/enzyme.php?ecno=6.3.5.3) lists this kcat for *Escherichia coli* with NH4+ as the substrate. The reaction in the model uses glutamine. The paper that reports the value ([Schendel et al. 1989](https://doi.org/10.1021/bi00432a017)) states in its abstract that "NH3 can replace glutamine as a nitrogen donor with a Km = 1 M and a turnover of 3 min-1 (2% glutamine turnover)", so 0.05 per s is the kcat with ammonia as the nitrogen donor. The paper also reports a specific activity, which BRENDA lists; the tutorial uses 2.15 µmol/min/mg protein. A specific activity gives a kcat when it is multiplied by the molecular weight of the enzyme:

- 2.15 µmol/min/mg is 2.15 mmol/min/g;
- divided by 1000, it is 0.00215 mol/min/g;
- divided by 60, it is 3.583e-5 mol/s/g;
- multiplied by the molecular weight of P38972, 148905 g/mol (`ec.mw`), it is 5.336 per s.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
sa = 2.15;                                   % umol/min/mg protein
mw = ecModel.ec.mw(strcmp(ecModel.ec.enzymes, 'P38972'));   % g/mol
kcat = sa / 1000 / 60 * mw                   % 1/s
ecModel = setKcatForReactions(ecModel, 'r_0079', kcat);
ecModel = applyKcatConstraints(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import set_kcat_for_reactions

sa = 2.15                                    # umol/min/mg protein
mw = ec_model.ec.mw[ec_model.ec.enzymes.index("P38972")]   # g/mol
kcat = sa / 1000 / 60 * mw                   # 1/s
set_kcat_for_reactions(ec_model, ["r_0079"], kcat, apply=True)
```
:::
::::

The tutorial keeps this value as the row of `r_0079` in `tutorials/full_ecModel/data/kcats/custom.tsv`, so that `assignKcats` applies it (see [Keep a curated kcat](#keep-a-curated-kcat)).

When a measured value supports the kcat before tuning and contradicts the tuned one, the network of the conventional GEM may lack a reaction or a pathway; correct the GEM first.

## Keep a curated kcat

`assignKcats` replaces every kcat of the model with the values selected from the files in `data/kcats`. A value set with `setKcatForReactions` is therefore lost at the next `assignKcats`. To keep it, add it to `data/kcats/custom.tsv`, which every preset reads first (see [Set custom kcats](custom-kcats.md)). A row for `r_0079`, with the columns `rxn`, `enzymes`, `kcat`, `source` and `note`:

```text
rxn	enzymes	kcat	source	note
r_0079	P38972	5.3357625	custom	specific activity 2.15 umol/min/mg, MW 148905 g/mol
```

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| A curated kcat is gone after `assignKcats` | The value was set with `setKcatForReactions`, and `assignKcats` replaced it with the value from the kcat source files | Add the value to `custom.tsv` |
| A tuned kcat is far from every measured value of its enzyme | The tuning compensated for another error: a wrong kcat of another reaction, a missing reaction in the GEM, or a wrong protein pool | Check the kcat against its source, and the GEM and the protein pool, before keeping the tuned value |
| A tuning gives an error or stops early | A cause that is specific to the tuning | See the troubleshooting of [sensitivityTuning](standard-tuning.md#troubleshooting) or of [evotune](evotune.md#troubleshooting) |

## See also

- [Tune kcats with sensitivityTuning](standard-tuning.md) and [Tune kcats with evotune](evotune.md), the two tunings.
- [Set the protein pool](protein-pool.md), Ptot, f, sigma and `sigmaFitter`.
- [Choose the kcat sources](kcat-sources.md) and [Set custom kcats](custom-kcats.md), where the kcats before tuning come from.
- [Basic model operations](basic-model-operations.md), bounds, objectives and FBA.
- [API reference](../api/index.md), every function in both toolboxes.
