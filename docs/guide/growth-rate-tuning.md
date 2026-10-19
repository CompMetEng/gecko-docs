# Growth-rate tuning

A draft ecModel with active enzyme constraints usually predicts a growth
rate far below what the organism actually reaches, because a maximum
constraint has not yet been imposed on the protein pool, and because some
kcat values are uncertain or too low. This page diagnoses which of those
is the limiting factor and tunes the model against known physiological
data until it reaches a realistic growth rate. The result is a
**functional ecModel**.

The protein pool's maximum constraint is calculated as:

$$ \sigma \times f \times P_{tot} $$

where sigma is the average in vivo saturation of every enzyme in the
model, f is the mass fraction occupied by metabolic enzymes in the total
proteome, and $P_{tot}$ is the total protein mass in grams per gram cell
dry weight. When one or more factors are unknown, a default of 0.5 for
each gives a default maximum constraint of $0.5 \times 0.5 \times 0.5 =
0.125$.

:::{note} When no physiological data are available
Tuning requires physiological data, particularly growth rate. Without it,
for example in large-scale reconstruction across many cell lines, only
draft ecModels can be obtained: a draft may not simulate realistic fluxes,
because the protein pool's upper bound is undefined, but it can still
compare cellular parameters such as protein costs. Even with no
experimental data, a functional ecModel is reachable by assuming an
arbitrary protein pool value and increasing low kcat values until
simulations become reasonable.
:::

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `solveLP` | `Model.optimize` | run FBA and predict a growth rate |
| `sensitivityTuning` | `sensitivity_tuning` | iteratively raise the kcats that most limit growth |
| `setKcatForReactions` | `set_kcat_for_reactions` | apply a curated kcat value to specific reactions |
| `saveEcModel` | `save_ec_model` | save the functional ecModel |

## Simulate growth rate

Examine whether the ecModel reaches a realistic growth rate once enzyme
constraints are applied. Microorganisms reach their maximum growth rate
when nutrient supply is not limiting, so allow unconstrained uptake of the
carbon source first:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'lb', params.c_source, -1000);
```

Or referring directly to the glucose exchange reaction in the
*S. cerevisiae* ecModel:

```matlab
ecModel = setParam(ecModel, 'lb', 'r_1714', -1000);
```
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy/cobrapy has no `setParam` wrapper: bounds are attributes on the
`cobra.Reaction` object itself.

```python
ec_model.reactions.get_by_id(params.c_source).lower_bound = -1000
```

Or directly:

```python
ec_model.reactions.get_by_id("r_1714").lower_bound = -1000
```
:::
::::

The glucose exchange reaction, for example, is defined as `glucose[e] <=>`.
A positive, forward flux represents dissipation from the system, so a
negative flux signifies uptake into the cytoplasm; a negative lower bound
is therefore what allows uptake. Query the direction of a reaction with:

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

Set growth as the objective, predict the flux distribution and print the
growth rate:

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
Growth rate: 0.107203 /hour
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.objective = params.bio_rxn
sol = ec_model.optimize()
print(f"Growth rate: {sol.fluxes[params.bio_rxn]:.4f} /hour")
```

Setting `.objective` to a reaction id maximizes it by default; there is no
separate "set objective coefficient" call, and no reaction-index lookup,
since `sol.fluxes` is a pandas Series indexed by reaction id.
:::
::::

:::{note} Example output
In the `full_ecModel` tutorial, the growth rate right after applying enzyme
constraints is about 0.107 h^-1. Because nutrient uptake is not limiting,
this is the maximum the ecModel can reach. Being substantially below
0.41 h^-1, the experimentally observed maximum growth rate of this organism
(`params.gR_exp` in MATLAB, `params.gr_exp` in Python), indicates the model
needs tuning.
:::

Three reasons can leave the predicted growth rate below the experimental
maximum, and a systematic check distinguishes them: the metabolic
network's stoichiometry is not fully correct; the protein pool exchange
reaction is too tightly constrained; or kcat values assigned to reactions
are too low.

## Network stoichiometry limits growth rate

Predict the growth rate in the conventional GEM, without enzyme
constraints, under the same exchange flux constraints:

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
Growth rate: 19.718033 /hour
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

If the conventional GEM also cannot reach the maximum growth rate, the
starting GEM's stoichiometry or constraints contain errors that should be
resolved before reconstructing an ecModel from it.

:::{note} Example output
Without a constraint on carbon uptake, the conventional GEM in the
`full_ecModel` tutorial reaches a growth rate of about 19.7 h^-1. This is
not biologically realistic on its own, given the unconstrained carbon
uptake, but it confirms that the conventional GEM's stoichiometry can reach
0.41 h^-1, so the shortfall above comes from the enzyme constraints, not
the network.
:::

## Too tight protein pool constraint

Confirm that the protein pool constraint from
[Applying kcats](applying-kcats.md#constrain-the-protein-pool-exchange-reaction)
is realistic: inspect the sigma, $P_{tot}$ and f parameters in the model
adapter, and adjust them if discrepancies show up. Regardless of whether
those parameters are realistic, the simplest way to test whether the
protein pool is what limits growth is to relax the pool usage reaction's
constraint entirely, releasing every enzyme constraint at once:

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

`set_prot_pool_size` narrows `prot_pool_exchange`'s upper bound to a
realistic budget; relaxing it back to unconstrained means raising that
upper bound back to geckopy's wide-open default (1000).
:::
::::

:::{tip} GECKO 4: direction of prot_pool_exchange
In GECKO 4 and geckopy, `prot_pool_exchange` is a forward reaction that
produces `prot_pool`, with a lower bound of 0 and an upper bound of 1,000
by default (see
[Building an empty ecModel](building-ec-model.md#box-1-extension-of-a-conventional-gem)).
Relaxing the protein pool therefore raises its upper bound, and minimizing
its usage is an ordinary minimization. The GECKO 3.0 protocol used the
opposite (negative-flux) direction, where relaxing lowered the lower bound
to -1,000 and minimizing usage required maximizing with coefficient `1`.
:::

With neither a protein pool nor a nutrient constraint, predict the lowest
protein pool usage that still supports the experimental maximum growth
rate:

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

**Objective coefficient sign.** `solveLP` maximizes the objective, so the
coefficient `-1` minimizes the flux through `prot_pool_exchange`.

Output in the `full_ecModel` tutorial:

```
Protein pool usage is: 446 mg/gDCW
```
:::
:::{tab-item} 🐍 Python
:sync: python

cobrapy separates the objective reaction from the optimization direction,
so minimizing `prot_pool_exchange` usage is a plain positive objective with
`objective_direction` set to `"min"`:

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

Set the predicted protein pool usage as the constraint on the protein pool
exchange reaction, then revert the objective function and growth rate
constraint used to find it:

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

This always yields an ecModel that reaches the intended growth rate,
assuming the conventional GEM can too, but it often sets the protein pool
usage to an unrealistic protein content. Increasing kcat values for some
reactions instead is the more biologically meaningful option, covered
next.

:::{note} Example output
Setting the upper bound of `prot_pool_exchange` to 1,000 mg/gDCW implies
the whole cell is 100% protein. While unrealistic, this often avoids
overconstraining. In the `full_ecModel` tutorial, the predicted protein
pool usage is 446 mg/gDCW. With f = 0.5, this implies the cell would
consist of 89.2% protein.
Assuming full enzyme saturation, a more realistic (lower) sigma would push
the simulated total protein content above 100%, which is why simply
releasing the protein pool constraint is not the recommended fix.
:::

## Sensitivity tuning of kcat values

Iteratively increasing the kcat values of enzymes that limit growth, until
the desired growth rate is reached, is the recommended approach over
relaxing the pool. At this stage the enzyme constraints are dominated by
the overarching protein pool constraint, so each deterministic iteration
identifies the most-limiting enzyme as the one demanding the largest
fraction of the protein pool, and raises its kcat; the raised value is the
one contributing most to overconstraining the model, not necessarily the
one furthest from its true in situ value.

First revert the protein pool constraint to a realistic value (see
[Applying kcats](applying-kcats.md#constrain-the-protein-pool-exchange-reaction)),
then tune and report the changes:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setProtPoolSize(ecModel);
[ecModel, tunedKcats] = sensitivityTuning(ecModel);
struct2table(tunedKcats)
```

`sensitivityTuning` returns the updated ecModel and the `tunedKcats`
structure, and with `verbose` at its default (`true`) prints the growth
rate of each iteration. It also handles light ecModels. Output for the
`full_ecModel` tutorial:

```
Iteration 1: Growth: 0.11421
Iteration 2: Growth: 0.18016
Iteration 3: Growth: 0.23412
Iteration 4: Growth: 0.27495
Iteration 5: Growth: 0.30635
Iteration 6: Growth: 0.33961
Iteration 7: Growth: 0.3718
Iteration 8: Growth: 0.39141
Iteration 9: Growth: 0.41193
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import sensitivity_tuning, set_prot_pool_size

set_prot_pool_size(ec_model)
tuning_result = sensitivity_tuning(ec_model)
```

`sensitivity_tuning` mutates `ec_model` in place, with no separate returned
model, and returns a `TunedKcatsResult` with a `.rxns` field (and the
previous/tuned values); with no explicit growth-rate argument it targets
`params.gr_exp` from the adapter. It is not available for light ecModels
(raises `NotImplementedError` if `ec_model.ec.gecko_light` is `True`). With
`verbose=True` (the default) it logs the growth rate of each iteration at
`INFO` level through the `logging` module.
:::
::::

Both toolboxes also provide a CMA-ES-based kcat tuning module
(`cmaesKcatTuning` in MATLAB, `cmaes_kcat_tuning` in Python), described in
[Tuning against experimental data](tuning-against-experimental-data.md).

The `tunedKcats`/`tuning_result` output documents which kcat values were
changed, with their previous value and the catalyzed reaction. Inspect it
to check whether any changed value was initially gathered incorrectly from
a kcat source.

:::{note} Many kcat values are changed during tuning
Some kcat values changing is expected, typically about 20 to 40. If a much
larger fraction changes, check the following before assuming the tuning
itself is at fault:

- No constraint is set on any nutrient uptake; only the protein pool
  should be limiting.
- The maximum growth rate specified as `gR_exp`/`gr_exp` in the model
  adapter is realistic.
- The starting GEM can simulate the intended growth rate on its own, to
  rule out the network stoichiometry as the limiting factor (see
  [Network stoichiometry limits growth rate](#network-stoichiometry-limits-growth-rate)
  above).
:::

:::{note} Example output
In the `full_ecModel` tutorial, iterative tuning raises the growth rate
from 0.114 h^-1 in the first iteration to 0.412 h^-1 in the ninth, above
the target of 0.41 h^-1.

The selected `ec.kcat` entries appear in the tuned kcat output (see
[Example tuned kcat output](#example-tuned-kcat-output) below).
`ec.source` still names the original source, so transferring the changes
into `data/customKcats.tsv` (see
[Applying kcats](applying-kcats.md#provide-custom-kcat-values)) keeps
them documented.
:::

### Example tuned kcat output

| rxns | rxnNames | enzymes | oldKcat | newKcat | source |
|------|----------|---------|---------|---------|--------|
| `r_0079` | 5'-Phosphoribosylformyl glycinamidine synthetase | P38972 | 0.05 | 5 | BRENDA |
| `r_0109` | Acetyl-CoA carboxylase, reaction | P48445; Q00955 | 1.23 | 12.3 | BRENDA |
| `r_0450` | Fructose-bisphosphate aldolase | P14540 | 32.5 | 325 | Custom |
| `r_0486_EXP_2` | Glyceraldehyde-3-phosphate dehydrogenase | P00360 | 29 | 290 | Custom |
| `r_0698` | Lanosterol synthase | P38604 | 0.001937 | 0.1937 | BRENDA |
| `r_1166_EXP_11` | Glucose transport | P38695 | 19.26 | 192.6 | DLKcat |

## Evaluate the tuned kcat values

Tuning changes values automatically, based only on which enzyme
overconstrains the ecModel, without regard to whether the original value
was itself unrealistic. Good evidence can exist that the tuned value
better reflects reality than the source it replaced, but not every tuned
value can be supported by literature data. The worked example below covers
one value from the table above, 5'-phosphoribosylformyl glycinamidine
synthetase (reaction `r_0079`), which tuning raised from 0.05 s^-1 to 5
s^-1, sourced originally from BRENDA; repeat this kind of check for each
value of interest.

Get the match details behind the original BRENDA value:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
rxnIdx = find(strcmp(kcatList_merged.rxns, 'r_0079'));
kcatList_merged.wildcardLvl(rxnIdx)
kcatList_merged.eccodes(rxnIdx)
kcatList_merged.origin(rxnIdx)
```
:::
:::{tab-item} 🐍 Python
:sync: python

kcat lists are `pandas.DataFrame`s in geckopy, one row per reaction, rather
than a struct of parallel arrays, so this is a row lookup:

```python
row = kcat_list_merged.loc[kcat_list_merged["rxn_id"] == "r_0079"].iloc[0]
print(row["wildcard_level"], row["eccode"], row["origin"])
```
:::
::::

This yields a wildcard level of 0, EC number 6.3.5.3 and origin 4 (any
organism, any substrate, specific-activity kcat).

Looking at the specific
[BRENDA entry](https://www.brenda-enzymes.org/enzyme.php?ecno=6.3.5.3), the
reported kcat of 0.05 comes from *E. coli* with NH3 as substrate. The usual
substrate is glutamine, so this value may not be a fair estimate for the
reaction in the ecModel. The original paper's abstract states that NH3 can
replace glutamine as a nitrogen donor, with a Km of 1 M and a turnover of 3
min^-1 (2% of the glutamine turnover); the same paper also reports a
specific activity with glutamine as substrate, a more reasonable value to
use here. Calculate the corresponding activity: the specific activity was
reported as 2.15 micromol/min/mg protein, which equals mmol/min/g protein,
so converting to mol/s/g protein and applying the enzyme's molecular weight
gives:

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

The converted kcat is 5.34, close to the value of 5 reached by
the tuning. Replace the value in the ecModel with the new
literature value, either documenting it in `customKcats.tsv` (see
[Applying kcats](applying-kcats.md#provide-custom-kcat-values)) or applying
it directly:

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
from geckopy import set_kcat_for_reactions

set_kcat_for_reactions(ec_model, ["r_0079"], 5.34)
```

`set_kcat_for_reactions` takes a list of reaction ids, even for a single
reaction, and one kcat value applied to all of them. With its default
`apply=True`, it also applies the new kcat to the S-matrix immediately, so
no separate call to `apply_kcat_constraints` is needed here (pass
`apply=False` to defer that, matching MATLAB's two-step
`setKcatForReactions` + `applyKcatConstraints`).
:::
::::

After repeating this for each tuned value, consider the results overall.
When convincing evidence shows the original value is more realistic than
the tuned one, key reactions or whole pathways may be missing from the
starting GEM's network stoichiometry; such issues, as in
[Network stoichiometry limits growth rate](#network-stoichiometry-limits-growth-rate)
above, are best resolved in the conventional GEM before it is used to
reconstruct an ecModel.

## Save the functional ecModel

The tuned ecModel can now simulate the physiological data it was tuned
against. Save it before moving on to
[proteomics integration](proteomics-integration.md) or
[simulation and analysis](simulation-and-analysis.md):

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

## Box 2: Selection of RAVEN toolbox functions

These operations work on both conventional GEMs and ecModels, in both
languages (RAVEN toolbox functions in MATLAB, cobrapy idioms in Python).

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

Set the objective to maximize flux through the biomass reaction:

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

Perform FBA, optimizing the objective:

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

Perform parsimonious FBA, optimizing the objective and minimizing the
total sum of flux:

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

:::::{tip} GECKO 4: enzyme-aware pFBA
Both languages also offer a variant that minimizes total *enzyme* usage
instead of total flux, the L1 norm of `usage_prot_*` fluxes rather than all
reaction fluxes. This is not part of the original Nature Protocols
procedure, and useful for the
[enzyme-usage inspection](enzyme-usage-and-bottlenecks.md) done during
simulation and analysis. It is not available for light ecModels, which
have no `usage_prot_*` reactions to minimize.

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

Inspect the nonzero fluxes:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

Through exchange reactions (this includes usage reactions for enzymes
constrained by their concentration, but not enzymes that draw from the
protein pool, since pool usage is itself the exchange reaction in that
case):

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

`sol.fluxes` is a pandas Series indexed by reaction id, so this is
ordinary pandas filtering. Through all reactions:

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

Export the results to a spreadsheet (this file does not carry content from
the `ec` structure, but is convenient for quickly finding reaction
identifiers):

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
exportToExcelFormat(ecModel, 'filename.xlsx');
```
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy has no dedicated spreadsheet exporter; write the solution directly
with pandas:

```python
sol.fluxes.to_excel("filename.xlsx")
```
:::
::::

Export the ecModel to an SBML file for use in other constraint-based
modeling software:

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

As on [Building an empty ecModel](building-ec-model.md#save-the-ecmodel),
this plain-cobrapy SBML export does not retain the `ec_model.ec` fields,
the same caveat as MATLAB's `exportModel`.
:::
::::

## See also

- [Applying kcats](applying-kcats.md), where the enzyme constraints tuned
  on this page come from.
- [Tuning against experimental data](tuning-against-experimental-data.md),
  a GECKO 4 / geckopy method that fits kcats to measured data directly,
  rather than iteratively relaxing the protein pool.
- [API reference](../api/index.md), every function in both toolboxes.
