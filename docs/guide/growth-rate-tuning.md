# Growth-rate tuning

A draft ecModel with active enzyme constraints usually predicts a growth rate far below what the organism reaches, because a maximum constraint has not yet been imposed on the protein pool and because some kcat values are uncertain or too low. Diagnosing which of the two limits growth, tuning the model against known physiological data until it reaches a realistic growth rate, and saving the result gives a functional ecModel.

The maximum constraint of the protein pool is calculated as:

$$ \sigma \times f \times P_{tot} $$

where sigma is the average in vivo saturation of every enzyme in the model, f is the mass fraction occupied by metabolic enzymes in the total proteome, and $P_{tot}$ is the total protein mass in grams per gram cell dry weight. When one or more factors are unknown, a default of 0.5 for each gives a default maximum constraint of $0.5 \times 0.5 \times 0.5 = 0.125$.

:::{admonition} When no physiological data are available
:class: note

Tuning requires physiological data, particularly growth rate. Without it, for example in large-scale reconstruction across many cell lines, the result is a draft ecModel: it may not simulate realistic fluxes, because the upper bound of the protein pool is undefined, but it can still compare cellular parameters such as protein costs. Even with no experimental data, a functional ecModel is reachable by assuming an arbitrary protein pool value and increasing low kcat values until simulations become reasonable.
:::

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `solveLP` | `Model.optimize` | runs FBA and predicts a growth rate |
| `setProtPoolSize` | `set_prot_pool_size` | sets the upper bound of the protein pool exchange reaction from Ptot, f and sigma |
| `sensitivityTuning` | `sensitivity_tuning` | iteratively raises the kcats that limit growth most |
| `sigmaFitter` | `fit_sigma` | fits sigma to the experimental growth rate |
| `setKcatForReactions` | `set_kcat_for_reactions` | sets a curated kcat value for specific reactions |
| `applyKcatConstraints` | `apply_kcat_constraints` | transfers the kcat values to the stoichiometric matrix |
| `saveEcModel` | `save_ec_model` | saves the functional ecModel |

## Setup

An ecModel with assigned kcats, the protein pool constraint of [Applying kcats](applying-kcats.md#constrain-the-protein-pool-exchange-reaction) and a model adapter with `gR_exp` (Python `gr_exp`), the experimental maximum growth rate. The code assumes the `full_ecModel` tutorial: `ecModel` (MATLAB) or `ec_model` (Python) is the ecModel and `params` holds the parameters of the model adapter.

## Simulate growth rate

Microorganisms reach their maximum growth rate when nutrient supply is not limiting, so the uptake of the carbon source is first set to be unconstrained:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'lb', params.c_source, -1000);
```

Or referring directly to the glucose exchange reaction in the *S. cerevisiae* ecModel:

```matlab
ecModel = setParam(ecModel, 'lb', 'r_1714', -1000);
```
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy/cobrapy has no `setParam` wrapper: bounds are attributes on the `cobra.Reaction` object itself.

```python
ec_model.reactions.get_by_id(params.c_source).lower_bound = -1000
```

Or directly:

```python
ec_model.reactions.get_by_id("r_1714").lower_bound = -1000
```
:::
::::

The glucose exchange reaction, for example, is defined as `glucose[e] <=>`. A positive, forward flux represents dissipation from the system, so a negative flux signifies uptake into the cytoplasm, and a negative lower bound allows uptake. The direction of a reaction is queried with:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
constructEquations(ecModel, 'r_1714');
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
print(ec_model.reactions.get_by_id("r_1714").reaction)
```
:::
::::

Growth is set as the objective, the flux distribution is predicted and the growth rate is printed:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
sol = solveLP(ecModel);
bioRxnIdx = getIndexes(ecModel, params.bioRxn, 'rxns');
fprintf('Growth rate: %f /hour\n', sol.x(bioRxnIdx))
```

Output in the `full_ecModel` tutorial:

```
Growth rate: 0.116494 /hour
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.objective = params.bio_rxn
sol = ec_model.optimize()
print(f"Growth rate: {sol.fluxes[params.bio_rxn]:.4f} /hour")
```

Setting `.objective` to a reaction id maximizes it by default; there is no separate "set objective coefficient" call, and no reaction-index lookup, since `sol.fluxes` is a pandas Series indexed by reaction id.
:::
::::

:::{admonition} Example output
:class: note

In the `full_ecModel` tutorial, the growth rate right after applying enzyme constraints is about 0.12 h^-1. Because nutrient uptake is not limiting, this is the maximum the ecModel can reach. A rate substantially below 0.41 h^-1, the experimentally observed maximum growth rate of this organism (`params.gR_exp` in MATLAB, `params.gr_exp` in Python), indicates that the model needs tuning.
:::

Three reasons can leave the predicted growth rate below the experimental maximum, and a systematic check distinguishes them: the stoichiometry of the metabolic network is not fully correct; the protein pool exchange reaction is too tightly constrained; or the kcat values assigned to reactions are too low.

## Network stoichiometry

The growth rate in the conventional GEM, without enzyme constraints, is predicted under the same exchange flux constraints:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
model = loadConventionalGEM();
model = setParam(model, 'lb', params.c_source, -1000);
model = setParam(model, 'obj', params.bioRxn, 1);
sol = solveLP(model);
bioRxnIdx = getIndexes(model, params.bioRxn, 'rxns');
fprintf('Growth rate: %f /hour\n', sol.x(bioRxnIdx))
```

Output in the `full_ecModel` tutorial:

```
Growth rate: 19.944241 /hour
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import load_conventional_gem

model = load_conventional_gem(adapter)
model.reactions.get_by_id(params.c_source).lower_bound = -1000
model.objective = params.bio_rxn
sol = model.optimize()
print(f"Growth rate: {sol.fluxes[params.bio_rxn]:.4f} /hour")
```
:::
::::

If the conventional GEM also cannot reach the maximum growth rate, the stoichiometry or the constraints of the starting GEM contain errors that should be resolved before an ecModel is reconstructed from it.

:::{admonition} Example output
:class: note

Without a constraint on carbon uptake, the conventional GEM in the `full_ecModel` tutorial reaches a growth rate of about 19.9 h^-1. This growth rate is biologically unrealistic given the unconstrained carbon uptake, but it confirms that the stoichiometry of the conventional GEM can reach 0.41 h^-1, so the enzyme constraints cause the shortfall above.
:::

## Protein pool constraint

The protein pool constraint from [Applying kcats](applying-kcats.md#constrain-the-protein-pool-exchange-reaction) is realistic when the sigma, $P_{tot}$ and f parameters in the model adapter are realistic; adjust the parameters if discrepancies show up. Regardless of those parameters, the simplest test of whether the protein pool limits growth is to relax the constraint of the pool usage reaction, which releases every enzyme constraint at once:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'ub', 'prot_pool_exchange', 1000);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.reactions.prot_pool_exchange.upper_bound = 1000
```

`set_prot_pool_size` narrows `prot_pool_exchange`'s upper bound to a realistic budget; relaxing it back to unconstrained means raising that upper bound back to geckopy's wide-open default (1000).
:::
::::

:::{admonition} GECKO 4: direction of prot_pool_exchange
:class: tip

In GECKO 4 and geckopy, `prot_pool_exchange` is a forward reaction that produces `prot_pool`, with a lower bound of 0 and an upper bound of 1,000 by default (see [Building an empty ecModel](building-ec-model.md#extension-of-a-conventional-gem)). Relaxing the protein pool therefore raises its upper bound, and minimizing its usage is an ordinary minimization. The GECKO 3 protocol used the opposite (negative-flux) direction, where relaxing lowered the lower bound to -1,000 and minimizing usage required maximizing with coefficient `1`; see [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md).
:::

With neither a protein pool nor a nutrient constraint, the lowest protein pool usage that still supports the experimental maximum growth rate is predicted:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'lb', 'r_4041', 0.41);
ecModel = setParam(ecModel, 'obj', 'prot_pool_exchange', -1);
sol = solveLP(ecModel);
protPoolIdx = strcmp(ecModel.rxns, 'prot_pool_exchange');
fprintf('Protein pool usage is: %.0f mg/gDCW\n', sol.x(protPoolIdx))
```

`solveLP` maximizes the objective, so the coefficient `-1` minimizes the flux through `prot_pool_exchange`.

Output in the `full_ecModel` tutorial:

```
Protein pool usage is: 407 mg/gDCW
```
:::
:::{tab-item} 🐍 Python
:sync: python

cobrapy separates the objective reaction from the optimisation direction, so minimizing `prot_pool_exchange` usage is a plain positive objective with `objective_direction` set to `"min"`:

```python
ec_model.reactions.get_by_id("r_4041").lower_bound = 0.41
ec_model.objective = "prot_pool_exchange"
ec_model.objective_direction = "min"
sol = ec_model.optimize()
pool_usage = sol.fluxes["prot_pool_exchange"]
print(f"Protein pool usage is: {pool_usage:.0f} mg/gDCW")
```
:::
::::

The predicted protein pool usage is set as the constraint on the protein pool exchange reaction, and the objective function and growth rate constraint that found it are reverted:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'ub', protPoolIdx, sol.x(protPoolIdx));
ecModel = setParam(ecModel, 'lb', 'r_4041', 0);
ecModel = setParam(ecModel, 'obj', 'r_4041', 1);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.reactions.prot_pool_exchange.upper_bound = pool_usage
ec_model.reactions.get_by_id("r_4041").lower_bound = 0
ec_model.objective = "r_4041"
ec_model.objective_direction = "max"
```
:::
::::

This yields an ecModel that reaches the intended growth rate whenever the conventional GEM can, but it often sets the protein pool usage to an unrealistic protein content. Increasing the kcat values of some reactions keeps the protein pool at the sigma, f and Ptot values of the model and is covered next.

:::{admonition} Example output
:class: note

Setting the upper bound of `prot_pool_exchange` to 1,000 mg/gDCW implies that the whole cell is 100 % protein. While unrealistic, this often avoids overconstraining. In the `full_ecModel` tutorial, the predicted protein pool usage is 407 mg/gDCW. With a total protein content (Ptot) of 500 mg/gDCW, this implies that the cell consists of 81.4 % protein. Assuming full enzyme saturation, a more realistic (lower) sigma would push the simulated total protein content above 100 %, so the recommended fix is a different one than releasing the protein pool constraint.
:::

## Sensitivity tuning of kcat values

Iteratively increasing the kcat values of the enzymes that limit growth until the desired growth rate is reached keeps the protein pool at the sigma, f and Ptot values of the model, which relaxing the pool does not. At this stage the enzyme constraints are dominated by the overarching protein pool constraint. Each deterministic iteration identifies the most limiting enzyme as the one that demands the largest fraction of the protein pool, and raises the kcat of the reaction that draws most on it. The raised value is the one that contributes most to overconstraining the model, which is not necessarily the one furthest from its true in situ value.

The protein pool constraint is first reverted to a realistic value (see [Applying kcats](applying-kcats.md#constrain-the-protein-pool-exchange-reaction)), then the kcats are tuned and the changes reported:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setProtPoolSize(ecModel);
[ecModel, tunedKcats] = sensitivityTuning(ecModel);
struct2table(tunedKcats)
```

`sensitivityTuning` returns the updated ecModel and the `tunedKcats` structure, and with `verbose` at its default (`true`) prints the growth rate of each iteration. It also handles light ecModels. Output for the `full_ecModel` tutorial:

```
Iteration 1: Growth: 0.12508
Iteration 2: Growth: 0.20879
Iteration 3: Growth: 0.23956
Iteration 4: Growth: 0.28248
Iteration 5: Growth: 0.31398
Iteration 6: Growth: 0.34943
Iteration 7: Growth: 0.38066
Iteration 8: Growth: 0.42157
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import sensitivity_tuning, set_prot_pool_size

set_prot_pool_size(ec_model)
tuning_result = sensitivity_tuning(ec_model)
```

`sensitivity_tuning` changes `ec_model` in place, with no separate returned model, and returns a `TunedKcatsResult` with the fields `rxns`, `rxn_names`, `enzymes`, `old_kcat`, `new_kcat` and `source`. It sets the growth objective from `params.bio_rxn` of the adapter and targets `params.gr_exp` when no growth rate is given. It also handles light ecModels. With `verbose=True` (the default) it logs the growth rate of each iteration at `INFO` level through the `logging` module.
:::
::::

The options are the same in both toolboxes (MATLAB name first):

| MATLAB | Python | Default | Meaning |
| --- | --- | --- | --- |
| `desiredGrowthRate` | `desired_growth_rate` | `params.gR_exp` (Python `params.gr_exp`) | growth rate at which the tuning stops |
| `foldChange` | `fold_change` | `10` | factor by which each iteration raises a kcat |
| `protToIgnore` | `prot_to_ignore` | none | UniProt IDs whose enzymes are not picked as the limiting enzyme |
| `verbose` | `verbose` | `true` | reports the growth rate of each iteration |
| `modelAdapter` | | default model adapter | model adapter that supplies the parameters (Python reads `ec_model.adapter`) |
| | `max_iterations` | `1000` | upper limit of the iterations |
| | `bio_rxn` | `params.bio_rxn` | biomass reaction set as the objective |

MATLAB accepts the options as name-value pairs (`sensitivityTuning(ecModel, 'foldChange', 5)`) or positionally (`sensitivityTuning(ecModel, desiredGrowthRate, modelAdapter, foldChange, protToIgnore, verbose)`); a call uses one of the two forms. Python takes keyword arguments. The tuning stops with a warning when an iteration raises the growth rate by less than 1e-9, which indicates that the uptake or pool constraints limit growth and that the kcats do not.

Both toolboxes also provide a CMA-ES-based kcat tuning (`cmaesKcatTuning` in MATLAB, `cmaes_kcat_tuning` in Python), described in [Tuning against experimental data](tuning-against-experimental-data.md).

`tunedKcats` (Python `tuning_result`) documents which kcat values were changed, with their previous value, source and the catalysed reaction. It is inspected to check whether a changed value was gathered incorrectly from a kcat source. In a full ecModel, `ec.source` of a tuned reaction reads `sensitivityTuning`, and `ec.notes` holds the kcat before the tuning and its source (`preTuneKcat=<value> | source:<source>`). A reaction that an earlier run has tuned keeps the notes of that run. In a light ecModel, `ec.source` and `ec.notes` are not changed. Python `TunedKcatsResult.corrections()` returns the changes as the list of corrections that [Tuning against experimental data](tuning-against-experimental-data.md#read-the-result) describes.

:::{admonition} Many kcat values are changed during tuning
:class: note

Some kcat values changing is expected; the `full_ecModel` tutorial tunes 6. If a much larger fraction changes, check the following before assuming that the tuning itself is at fault:

- No constraint is set on any nutrient uptake; the protein pool should be the sole limit.
- The maximum growth rate specified as `gR_exp`/`gr_exp` in the model adapter is realistic.
- The starting GEM can simulate the intended growth rate on its own, to rule out the network stoichiometry as the limiting factor (see [Network stoichiometry](#network-stoichiometry) above).
:::

:::{admonition} Example output
:class: note

In the `full_ecModel` tutorial, iterative tuning raises the growth rate from 0.125 h^-1 in the first iteration to 0.422 h^-1 in the eighth, above the target of 0.41 h^-1.

The tuned `ec.kcat` entries appear in the tuned kcat output (see [Example tuned kcat output](#example-tuned-kcat-output) below). Transferring the changes into `data/kcats/custom.tsv` (see [Applying kcats](applying-kcats.md#provide-custom-kcat-values)) keeps them documented.
:::

### Example tuned kcat output

| rxns | rxnNames | enzymes | oldKcat | newKcat | source |
|------|----------|---------|---------|---------|--------|
| `r_0079` | 5'-phosphoribosylformyl glycinamidine synthetase | P38972 | 0.05 | 0.5 | brenda (wc=0, origin=4) |
| `r_0109` | acetyl-CoA carboxylase, reaction | P48445;Q00955 | 1.23 | 12.3 | brenda (wc=0, origin=2) |
| `r_0175_EXP_1` | aldehyde dehydrogenase (acetylaldehyde, NADP) | P40047 | 0.75 | 7.5 | brenda (wc=0, origin=2) |
| `r_0486_EXP_2` | glyceraldehyde-3-phosphate dehydrogenase | P00360 | 29 | 290 | custom |
| `r_0698` | lanosterol synthase | P38604 | 0.001937 | 0.1937 | brenda (wc=0, origin=5) |
| `r_1166_EXP_11` | glucose transport | P38695 | 19.26 | 192.6 | dlkcat |

## Evaluate the tuned kcat values

Tuning changes values automatically, based on which enzyme overconstrains the ecModel, without regard to whether the original value was itself unrealistic. Good evidence can exist that the tuned value reflects reality better than the source it replaced, but not every tuned value can be supported by literature data. The worked example covers one value from the example tuned kcat output, 5'-phosphoribosylformyl glycinamidine synthetase (reaction `r_0079`), which originates from BRENDA with a kcat of 0.05 s^-1 and which `sensitivityTuning` raises in the tutorial (to 0.5 s^-1). The same check is repeated for each value of interest.

The match details behind the original BRENDA value are in the kcat list that `kcatsFromBrenda` (Python `kcats_from_brenda`) returns, which is kept as `data/kcats/brenda.tsv`:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
rxnIdx = find(strcmp(kcatList_fuzzy.rxns, 'r_0079'));
kcatList_fuzzy.wildcardLvl(rxnIdx)
kcatList_fuzzy.eccodes(rxnIdx)
kcatList_fuzzy.origin(rxnIdx)
```
:::
:::{tab-item} 🐍 Python
:sync: python

kcat lists are `pandas.DataFrame`s in geckopy, one row per reaction, rather than a struct of parallel arrays, so this is a row lookup:

```python
row = kcat_list_fuzzy.loc[kcat_list_fuzzy["rxn_id"] == "r_0079"].iloc[0]
print(row["wildcard_level"], row["eccode"], row["origin"])
```
:::
::::

In the `full_ecModel` tutorial, which assigns the kcats with the preset `gecko_classic` (see [Kcat assignment](../gecko4-kcat-assignment.md)), this yields a wildcard level of 0 (no EC wildcard), EC number 6.3.5.3 and origin 4 (any organism, any substrate, kcat). The levels are defined in the help of `fuzzyKcatMatching`.

The specific [BRENDA entry](https://www.brenda-enzymes.org/enzyme.php?ecno=6.3.5.3) shows that the reported kcat of 0.05 comes from *E. coli* with NH4+ as substrate. The usual substrate is glutamine, so the value may not be a fair estimate for the reaction in the ecModel. The abstract of the original paper states that NH3 can replace glutamine as a nitrogen donor, with a Km of 1 M and a turnover of 3 min^-1 (2 % of the glutamine turnover). The same paper also reports a specific activity with glutamine as substrate, a more reasonable value to use here. The specific activity was reported as 2.15 micromol/min/mg protein, which equals mmol/min/g protein. Conversion to mol/s/g protein and multiplication with the molecular weight of the enzyme gives the kcat:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
convKcat = 2.15;
convKcat = convKcat / 1000;
convKcat = convKcat / 60;
enzMW = ecModel.ec.mw(strcmp(ecModel.ec.enzymes, 'P38972'));
convKcat = convKcat * enzMW
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
enz_idx = ec_model.ec.enzymes.index("P38972")
enz_mw = ec_model.ec.mw[enz_idx]
sa = 2.15  # umol/min/mg protein
conv_kcat = sa / 1000 / 60 * enz_mw
print(conv_kcat)
```
:::
::::

The converted kcat is 5.3358, rounded to 5.34. The value in the ecModel is replaced with the new literature value, either documented in `data/kcats/custom.tsv` (see [Applying kcats](applying-kcats.md#provide-custom-kcat-values)) or applied directly. `setKcatForReactions` (Python `set_kcat_for_reactions`) sets `ec.kcat` and `ec.source` (`setKcatForReactions`) of the reaction, and `applyKcatConstraints` (Python `apply_kcat_constraints`) transfers the new value to the stoichiometric matrix:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setKcatForReactions(ecModel, 'r_0079', 5.34);
ecModel = applyKcatConstraints(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_kcat_constraints, set_kcat_for_reactions

set_kcat_for_reactions(ec_model, ["r_0079"], 5.34)
apply_kcat_constraints(ec_model)
```

`set_kcat_for_reactions` takes a list of reaction ids, even for a single reaction. The `kcat` argument is one value applied to all matched reactions, or a sequence with one value per matched reaction or one value per id. With its default `apply=False` it changes `ec.kcat` and `ec.source`, as in MATLAB; `apply=True` also applies the new kcat to the S-matrix immediately.
:::
::::

After this is repeated for each tuned value, the results are considered overall. When convincing evidence shows that the original value is more realistic than the tuned one, reactions or whole pathways may be missing from the network stoichiometry of the starting GEM. Such issues, as in [Network stoichiometry](#network-stoichiometry) above, are best resolved in the conventional GEM before the ecModel is reconstructed from it.

## Fit the average saturation

`sigmaFitter` (Python `fit_sigma`) sets sigma so that the ecModel reaches the experimental growth rate, after the kcats are tuned. It sizes the protein pool for a series of sigma values from 0.01 to 1 in steps of 0.01 (`n_sigma_steps = 100` in Python), solves the model for each and keeps the value whose growth rate is closest to the target growth rate. `sigmaFitter` returns the smallest sigma whose percent error is within a relative 1e-9 of the smallest error, so a growth plateau is returned at its start on every solver. `fit_sigma` with the default `method="grid"` takes the first grid point with the smallest error and has no tolerance, so solver rounding noise on a plateau can move its pick to a later grid point. `fit_sigma` with `method="bisect"` finds a continuous sigma at 1e-6 resolution that is not on the grid and, for a target that growth cannot reach, the start of the plateau. The objective of the model must be growth. The bounds of the objective reaction are set to `[0, 1000]` before the scan and stay so on the returned model. The protein pool of the returned model is sized for the fitted sigma.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, sigma] = sigmaFitter(ecModel, 'makePlot', false);
```

`sigmaFitter` scans sigma from 0.01 to 1 in steps of 0.01. Ptot, f and the growth rate are read from the model adapter. The options `growthRate`, `Ptot`, `f`, `makePlot` (default `true`, a plot of the error against sigma) and `modelAdapter` are given as name-value pairs or positionally in this order; a call uses one of the two forms.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fit_sigma

fit = fit_sigma(ec_model)
print(fit.sigma)
```

`fit_sigma` changes `ec_model` in place and returns a `SigmaFitterResult` with the fields `sigma`, `sigma_grid`, `growth_grid` and `error_grid` (the absolute relative error in percent). The keyword arguments `growth_rate`, `p_tot` and `f` default to the values of the model adapter. With `method="grid"` (the default) it scans `n_sigma_steps` (default 100) sigma values `i / n` and takes the first with the smallest error; growth rates that differ by solver noise on a plateau can move the pick to a later grid point. With `method="bisect"` it uses the monotone growth in sigma to find sigma to a resolution of 1e-6 in about 20 solves, and for a growth rate that cannot be reached it returns the start of the plateau (growth within a relative 1e-9 of the growth at sigma 1). `sigma_fitter` is a deprecated alias of `fit_sigma` that raises a `DeprecationWarning`.
:::
::::

## Save the functional ecModel

The tuned ecModel can simulate the physiological data it was tuned against. It is saved before [proteomics integration](proteomics-integration.md) or [simulation and analysis](simulation-and-analysis.md):

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
saveEcModel(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import save_ec_model

save_ec_model(ec_model, "ecYeastGEM.yml", adapter=adapter)
```
:::
::::

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| Error that the FBA of the input model gives no valid result (`sensitivityTuning`), or `ValueError` that the FBA is not optimal (`sensitivity_tuning`) | The protein pool constraint or the exchange constraints make the model infeasible | Reduce the protein pool constraint with `setProtPoolSize` (Python `set_prot_pool_size`) and check the exchange constraints |
| Warning that growth does not increase from increased kcats | Uptake or pool constraints limit growth | Check the constraints on the uptake reactions; relax the protein pool as in [Protein pool constraint](#protein-pool-constraint) |
| Warning that no protein usage reaction carries flux, or that no reaction draws on the protein pool | The protein pool does not limit growth | Check the nutrient constraints and the network stoichiometry |
| `ValueError` that `prot_to_ignore` has no usage reaction for a protein | The UniProt ID is not an enzyme of the full ecModel | Correct the ID |
| Python `sensitivity_tuning` stops at `max_iterations` | The target growth rate is not reachable by raising kcats alone | Check the target growth rate and the constraints |
| `ValueError` that `model.adapter` is None | `fit_sigma` needs the adapter for `growth_rate`, `p_tot` or `f` | Attach an adapter or pass the three values |

`getPfbaEnzymes` and `pfba_enzymes` need a full ecModel; a light ecModel uses `solveLP(ecModel, 1)` or `pfba` for parsimonious FBA.

## See also

- [Applying kcats](applying-kcats.md), where the enzyme constraints tuned here come from.
- [Basic model operations](basic-model-operations.md), bounds, objectives, FBA and exports.
- [Tuning against experimental data](tuning-against-experimental-data.md), the fit of kcats to measured data with CMA-ES in both toolboxes.
- [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md), the changes of `sigmaFitter` and of the protein pool direction.
- [API reference](../api/index.md), every function in both toolboxes.
