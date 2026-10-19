# GECKO light vs. full ecModels

GECKO builds two different ecModel layouts from the same conventional GEM,
**full** and **light**. This page is the canonical explanation of the
difference: which one to choose, what light gives up, and how the two
compare in reconstruction time and simulation accuracy. Other pages link
here instead of re-explaining the choice.

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `makeEcModel(model, true)` | `make_ec_model(model, adapter, gecko_light=True)` | build a light ecModel instead of a full one |

Building either kind of ecModel from a conventional GEM is covered in
[Building an ecModel](building-ec-model.md); this page only covers the
`light` flag itself and what it changes.

## What full vs. light means

When a metabolic reaction is catalyzed by an enzyme, GECKO has to encode the
protein cost of that catalysis somewhere in the model. There are two ways to
do it:

- **Full ecModel.** For each enzyme, GECKO adds a dedicated pseudo-metabolite
  (`prot_<uniprot>`) and a dedicated usage reaction (`usage_prot_<uniprot>`).
  A reaction catalyzed by multiple isozymes is split into one copy per
  isozyme. This gives maximum bookkeeping flexibility: the solver can answer
  "how much of enzyme P00350 is being used right now?" directly. The cost is
  a much larger LP; a yeast-GEM full ecModel has around 8,000 reactions, and
  a Human-GEM full ecModel runs into the tens of thousands.
- **Light ecModel.** Skip the per-enzyme bookkeeping and use a single shared
  protein pool instead. Each catalyzed reaction gets one extra stoichiometric
  coefficient, $MW_{sum} / (k_{cat} \times 3600)$, against that pool.
  Isozymes are not split into separate reactions; instead, the kcat
  constraint step picks the lowest-cost isozyme (smallest $MW_{sum} /
  k_{cat}$) for each reaction and writes that single coefficient. The
  resulting LP stays close to the size of the starting GEM.

Light is the right choice for genome-scale models too large for the full
layout to solve in reasonable time, such as Human-GEM or Recon3D. For
smaller models, such as yeast or *E. coli*, full is usually fine.

| | Full | Light |
|---|---|---|
| Isozyme expansion | reactions split, one copy per isozyme (`_EXP_<N>` suffix) | reactions stay singular |
| Per-enzyme pseudo-metabolite `prot_<id>` | yes | no |
| Per-enzyme usage reaction `usage_prot_<id>` | yes | no |
| Shared protein pool | yes | yes, and it is the only enzyme constraint present |
| LP size | much larger than the starting GEM | close to the starting GEM |

## What light cannot do

Because a light ecModel has no per-enzyme pseudo-metabolites or usage
reactions, anything that depends on them is unavailable and raises an error
rather than returning a meaningless value, in both languages.

| Capability | MATLAB | Python |
|---|---|---|
| Proteomics integration | `constrainEnzConcs`, `flexibilizeEnzConcs` error on a light ecModel | `constrain_enz_concs`, `flexibilize_enz_concs` raise `ValueError` / `NotImplementedError` |
| Greedy proteomics relaxation | `relaxProteomicsGreedy` errors | `relax_proteomics_greedy` raises `NotImplementedError` |
| Per-enzyme usage / bottleneck analysis | `getEnzymeUsage`, `reportEnzymeUsage`, `getEnzymeBottlenecks`, `getPfbaEnzymes` all error | `enzyme_usage`, `report_enzyme_usage`, `get_enzyme_bottlenecks`, `pfba_enzymes` all raise `NotImplementedError` |
| Reading a single enzyme's flux, capacity usage, or shadow price | not applicable, no `usage_prot_<id>` reaction to read | `Enzyme.flux`, `Enzyme.cap_usage`, `Enzyme.upper_bound`, `Enzyme.shadow_price` all raise `NotImplementedError` |
| Setting an individual enzyme's concentration | not applicable | the `Kcats` concentration setter raises `NotImplementedError` |

See [Proteomics integration](proteomics-integration.md),
[Relaxing overconstrained proteomics](relaxing-constraints.md) and
[Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md) for what
these functions do on a full ecModel.

What still works the same way on a light ecModel: anything that reads
`ec.kcat` / `ec.mw` or edits the cobra LP directly without inspecting
per-enzyme metabolites. That includes BRENDA fuzzy matching, DLKcat I/O,
custom kcat overrides, assigning the standard kcat, and the kcat sensitivity
tuning loop (see [Gathering kcat values](gathering-kcats.md),
[Applying kcat values](applying-kcats.md) and
[Growth-rate tuning](growth-rate-tuning.md)).

## Reconstruction time and simulation accuracy

The comparison below builds a light and a full ecModel of yeast-GEM,
populated with kcat values from BRENDA fuzzy matching only, and runs FBA
with growth maximized on each:

| | Light | Full |
|---|---|---|
| ecModel reconstruction (s) | 39 | 41 |
| FBA (s) | 0.57 | 0.89 |
| Mapping fluxes (s) | 0.103 | 0.161 |
| Growth rate that is reached (/hour) | 0.0252 | 0.0252 |

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

The `plotlightVSfull` script of the `full_ecModel` tutorial prints this
comparison:

```
Comparison of duration light vs. full ecModel
ecModel reconstruction: 95% (39 vs 41 seconds)
FBA: 64% (0.57 vs 0.89 seconds)
Mapping fluxes: 64% (0.103 vs 0.161 seconds)
Growth rate that is reached: 0.0252 vs 0.0252
```
:::
::::

Reconstruction time does not differ much between the two, because both
require the same time-consuming BRENDA fuzzy matching step. FBA and flux
mapping back to the conventional GEM (see
[Simulation and analysis](simulation-and-analysis.md)) are substantially
faster on the light ecModel, which is where its size advantage shows up: it
matters most when many simulations are run, such as an extensive ecFVA scan
or many single-cell ecModels built from the same generic model.

The two ecModels reach the same growth rate here, and the flux distributions
they predict are near identical: the only reactions that deviate by more
than 0.1% between the two sit in lipid metabolism. Yeast-GEM's lipid
metabolism follows the SLIMEr formulation, where reactions for each possible
fatty-acyl-chain configuration are explicit and catalyzed by the same enzyme,
so the network has flexibility in which path it takes through lipid
metabolism while reaching the same overall acyl-chain distribution. That
flexibility comes from the conventional GEM itself and is unaffected by
whether the enzyme constraints are recorded per enzyme or pooled.

:::{tip}
When proteomics integration is not needed, a light ecModel gives comparable
predictions to a full one at a fraction of the simulation cost. When
proteomics integration, per-enzyme usage, or bottleneck ranking is needed,
build a full ecModel; there is no light equivalent for those.
:::

## See also

- [Building an ecModel](building-ec-model.md), where the `gecko_light` /
  `geckoLight` choice is made.
- [Proteomics integration](proteomics-integration.md) and
  [Relaxing overconstrained proteomics](relaxing-constraints.md), full-model
  only.
- [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md), full-model
  only.
