# Choose a kcat tuning

After the kcats are assigned and the protein pool is set, an ecModel can grow more slowly than the organism. A kcat tuning raises the kcats that limit growth until the ecModel reaches the maximum growth rate of the organism. The result is a tuned ecModel, a list of the changed kcats, and curated values for the changed kcats that the literature supports.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `sensitivityTuning` | `sensitivity_tuning` | standard kcat tuning: raises the kcat that limits growth most, one at a time, until the model reaches a growth rate |
| `cmaesKcatTuning` | `cmaes_kcat_tuning` | advanced kcat tuning: fits many kcats at once to measured growth rates and exchange fluxes, see [Tune kcats against experimental data](advanced-tuning.md) |
| `loadKcatSource` | `load_kcat_source` | reads the rows of a kcat source file in `data/kcats` for the reactions of an ecModel |
| `setKcatForReactions` | `set_kcat_for_reactions` | sets `ec.kcat` of reactions by hand |
| `applyKcatConstraints` | `apply_kcat_constraints` | writes `ec.kcat` into the enzyme constraints of the reactions |

## Setup

The examples need an ecModel with assigned kcats (`assignKcats`, see [Choose the kcat sources](kcat-sources.md)) and a set protein pool (`setProtPoolSize`, see [Set the protein pool](protein-pool.md)), in the variable `ecModel` (MATLAB) or `ec_model` (Python). The model adapter of the project defines `bio_rxn` and `gR_exp` (Python `gr_exp`); in MATLAB it is the default adapter (`ModelAdapterManager.setDefault`), and in Python it is attached to the model by `load_ec_model(adapter=...)`. The uptake of the carbon source is unconstrained.

## Signs that the model needs a kcat tuning

Maximise growth with flux balance analysis (FBA), with the uptake of the carbon source unconstrained (see [Basic model operations](basic-model-operations.md)). If the growth rate is far below the maximum growth rate of the organism (`gR_exp` in the model adapter, Python `gr_exp`), the enzyme constraints are too tight. Before kcats are changed, check the two other causes of a low growth rate:

- The conventional GEM, with the same exchange bounds, reaches the maximum growth rate. If it does not, the stoichiometry or the bounds of the GEM limit growth, and the GEM is corrected first.
- Ptot, f and sigma of the protein pool are realistic for the organism (see [Set the protein pool](protein-pool.md)).

If both hold, some kcats are too low for the enzymes that carry most of the flux, and a kcat tuning raises them.

## Standard or advanced kcat tuning

| Property | Standard: `sensitivityTuning` | Advanced: `cmaesKcatTuning` |
| --- | --- | --- |
| Data it needs | one maximum growth rate (`gR_exp` in the model adapter, or the option `desiredGrowthRate`) | maximum growth rates (`evotuneMaxGrowth.tsv`), exchange fluxes (`evotuneFluxData.tsv`), or both, measured in one or more conditions |
| What it changes | `ec.kcat` of the reactions it selects, and their enzyme constraints | `ec.kcat` of the kcats with the largest effect on the fit to the data, and their enzyme constraints |
| Which kcats | one reaction per iteration: the reaction with the largest use of the most used enzyme | the top kcats of a screen, up to 90 % of the weighted effect on the fit (option `targetImpactShare`) |
| How much | the kcat is multiplied by `foldChange` (default 10) per iteration; a kcat that is selected again is multiplied again | any value between `min(0.01, k0/100)` and `max(10000, 100*k0)` per s, where `k0` is the kcat before tuning |
| When it stops | the growth rate reaches the target, or growth stops rising | the best root-mean-square error (RMSE) reaches `rmse_threshold` (default 0.2), or after `max_generations` (default 150) generations |
| Cost in time | one FBA per iteration | one FBA per data row for each kcat vector that is scored: two per kcat in the screen, plus `popsize` per generation in the search; runs in parallel with `nProc` |
| Settings | the options of the function | the `[evotune]` table of `model_adapter.toml`, plus `targetImpactShare`, `popsize`, `seed` and `nProc` |

In a full ecModel, each iteration of the standard tuning selects the enzyme whose usage reaction carries the most flux and raises the kcat of the reaction that uses most of that enzyme; in a light ecModel, it raises the kcat of the reaction that draws most from the protein pool. The standard tuning also stops when an iteration raises growth by 1e-9 per h or less, when the model becomes infeasible, or when no enzyme usage carries flux; Python also stops after `max_iterations` (default 1000).

The advanced tuning weights the effect of each kcat on the fit by the `sigma0_log` of its source, so a kcat from a less trusted source has a larger weight. Python also stops on a convergence criterion of the `cma` package. The `[evotune]` settings set the trust in each kcat source, the weight of growth against flux data, the penalty for moving a kcat, isozyme tying and the stopping rules.

The two tunings are alternatives. When the maximum growth rate of the organism is the sole measured value, use the standard tuning. With measured growth rates on several carbon sources or measured exchange fluxes, the advanced tuning uses those data, and the trust in each kcat source limits how far each kcat moves.

## Run the standard tuning

`sensitivityTuning` reads the target growth rate and the biomass reaction from the model adapter, and sets growth as the objective. The protein pool must already be set (`setProtPoolSize`, see [Set the protein pool](protein-pool.md)), and the uptake of the carbon source unconstrained.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, tunedKcats] = sensitivityTuning(ecModel);
struct2table(tunedKcats)
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
              "source": tuned.source})
```

`sensitivity_tuning` changes `ec_model` in place and returns a `TunedKcatsResult`. It reads the target growth rate from `ec_model.adapter`. The options are keyword arguments.
:::
::::

| MATLAB | Python | Default | Meaning |
| --- | --- | --- | --- |
| `desiredGrowthRate` | `desired_growth_rate` | `gR_exp` of the model adapter (Python `gr_exp`) | growth rate at which the tuning stops |
| `foldChange` | `fold_change` | `10` | factor by which a selected kcat is multiplied |
| `protToIgnore` | `prot_to_ignore` | none | UniProt IDs of enzymes that are never selected |
| `verbose` | `verbose` | `true` | prints (Python: logs at `INFO`) the growth rate of each iteration |
| `modelAdapter` | | default model adapter | model adapter with the parameters; Python reads `ec_model.adapter` |
| | `max_iterations` | `1000` | maximum number of iterations |
| | `bio_rxn` | `bio_rxn` of the model adapter | biomass reaction that is set as the objective |

The output (`tunedKcats`, Python `TunedKcatsResult`) has one entry per tuned reaction: `rxns`, `rxnNames` (Python `rxn_names`), `enzymes` (joined by `;`), `oldKcat` and `newKcat` (Python `old_kcat`, `new_kcat`), and `source`, the kcat source before tuning. In a full ecModel, `ec.source` of a tuned reaction becomes `sensitivityTuning`, and `ec.notes` gets `preTuneKcat=<value> | source:<source>`. A reaction that an earlier run already tuned keeps the note of that run. In a light ecModel, `ec.source` and `ec.notes` do not change. In Python, `tuned.corrections()` returns the changes as a list of `Correction` rows, ordered by fold change.

After the standard tuning, `sigmaFitter` (Python `fit_sigma`) fits sigma so that the model reaches the target growth rate (see [Set the protein pool](protein-pool.md#fit-sigma-to-a-growth-rate)).

## Check a tuned kcat against its source

A tuning raises the kcats that limit growth in the model. It does not check whether the value before tuning was wrong. For each tuned kcat, look up where the value before tuning came from, and search the literature for a measured value.

The note of a tuned reaction gives the kcat and its source before tuning. When the source is a file in `data/kcats` (for example `brenda` or `ec_tree`), `loadKcatSource` returns the rows of that file for the reaction; the `detail` column of a BRENDA row holds the EC wildcard level and the origin of the match (see [BRENDA origin and wildcard levels](kcat-sources.md#brenda-origin-and-wildcard-levels)). `output/<model id>_kcatDecisions.tsv` lists the stage of the assignment that set each kcat (see [Choose the kcat sources](kcat-sources.md)).

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel.ec.notes(strcmp(ecModel.ec.rxns, 'r_0079'))
kcatList = loadKcatSource(ecModel, 'brenda');
idx = strcmp(kcatList.rxns, 'r_0079');
table(kcatList.kcats(idx), kcatList.eccodes(idx), kcatList.detail(idx))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import load_kcat_source

print(ec_model.ec.notes[ec_model.ec.rxns.index("r_0079")])
kcat_list, _ = load_kcat_source(ec_model, "brenda")
kcat_list[kcat_list["rxn_id"] == "r_0079"]
```
:::
::::

### Example: a kcat from a specific activity

The GECKO tutorial `full_ecModel` assigns the kcats of its yeast ecModel with the preset `gecko_classic`. In that ecModel, `sensitivityTuning` raised the kcat of `r_0079` (5'-phosphoribosylformyl glycinamidine synthetase, enzyme P38972). The kcat before tuning, 0.05 per s, came from a BRENDA match with wildcard level 0 and origin 4 (closest organism, any substrate; see [BRENDA origin and wildcard levels](kcat-sources.md#brenda-origin-and-wildcard-levels)) for EC 6.3.5.3.

[BRENDA](https://www.brenda-enzymes.org/enzyme.php?ecno=6.3.5.3) lists this kcat for *Escherichia coli* with NH4+ as the substrate. The reaction in the model uses glutamine. The paper that reports the value ([Schendel et al. 1989](https://doi.org/10.1021/bi00432a017)) states in its abstract that "NH3 can replace glutamine as a nitrogen donor with a Km = 1 M and a turnover of 3 min-1 (2% glutamine turnover)", so 0.05 per s is the kcat with ammonia as the nitrogen donor. According to the tutorial, the paper also reports a specific activity, which BRENDA lists; the tutorial uses 2.15 µmol/min/mg protein. A specific activity gives a kcat when it is multiplied by the molecular weight of the enzyme:

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

The committed tutorial model `tutorials/full_ecModel/models/ecYeastGEM.yml` holds this value for `r_0079`: `kcat: 5.3357625`, `source: setKcatForReactions`, `notes: preTuneKcat=0.05 | source:brenda`.

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
| Error that the FBA of the input model gives no valid result (MATLAB), or `ValueError` that the FBA of the input model is not optimal (Python) | The protein pool or the exchange bounds make the model infeasible | Check the exchange bounds and the protein pool (`setProtPoolSize`) |
| Warning that growth does not increase from increased kcats | An exchange bound or the protein pool limits growth | Check the bounds of the uptake reactions; check Ptot, f and sigma |
| Warning that no protein usage reaction carries flux, or that no reaction draws on the protein pool | The protein pool does not limit growth | Check the nutrient bounds and the stoichiometry of the GEM |
| Many kcats are tuned, or one kcat is raised several times | The target growth rate is too high, a nutrient uptake is constrained, or the GEM cannot reach the growth rate | Check `gR_exp`, the uptake bounds and the growth rate of the conventional GEM |
| Python `sensitivity_tuning` stops at `max_iterations` | Raising kcats alone does not reach the target growth rate | Check the target growth rate and the bounds |
| `ValueError` that `prot_to_ignore` has no usage reaction for a protein (Python, full ecModel) | The model has no usage reaction for this UniProt ID | Correct the ID |
| Error `sigmaFitter:growthRate` (Python: `ValueError`) | The target growth rate is not above 0 | Set `gR_exp` (Python `gr_exp`) in the model adapter, or give the growth rate |
| A curated kcat is gone after `assignKcats` | The value was set with `setKcatForReactions`, and `assignKcats` replaced it with the value from the kcat source files | Add the value to `custom.tsv` |

## See also

- [Tune kcats against experimental data](advanced-tuning.md), the advanced kcat tuning in detail.
- [Set the protein pool](protein-pool.md), Ptot, f, sigma and `sigmaFitter`.
- [Choose the kcat sources](kcat-sources.md) and [Set custom kcats](custom-kcats.md), where the kcats before tuning come from.
- [Basic model operations](basic-model-operations.md), bounds, objectives and FBA.
- [API reference](../api/index.md), every function in both toolboxes.
