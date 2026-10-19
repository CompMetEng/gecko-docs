# Enzyme usage and bottlenecks

A full ecModel simulation reports something a conventional GEM cannot: how
much of each enzyme a flux distribution actually uses, and which enzyme
would help the objective most if more of it were available. These are two
different questions with two different answers, and this page covers both:
usage from a given solution, and bottleneck ranking independent of any
particular solution.

:::{warning}
Every function on this page requires a full ecModel; see [GECKO light vs.
full ecModels](gecko-light.md).
:::

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `getEnzymeUsage` | `enzyme_usage` | absolute and capacity usage of every enzyme, from a flux distribution |
| `reportEnzymeUsage` | `report_enzyme_usage` | rank that usage data into top-N and high-capacity tables |
| `getEnzymeBottlenecks` | `get_enzyme_bottlenecks` | rank enzymes by shadow price, independent of usage |
| `getPfbaEnzymes` | `pfba_enzymes` | the flux distribution that uses the least enzyme mass at a given objective |

## Absolute and capacity usage

An enzyme's usage can be read two ways from a solved model:

- **Absolute usage**, the flux through its `usage_prot_<id>` reaction, in
  mg/gDCW.
- **Capacity usage**, absolute usage divided by that reaction's upper bound,
  the fraction of the enzyme's available supply the solution actually uses.
  That upper bound is not necessarily the concentration recorded in
  `ec.concs`; it can be a flexibilized value (see [Relaxing
  overconstrained proteomics](relaxing-constraints.md)).

Enzyme usage is most informative when the total protein pool constraint is
actually limiting, because it shows how the model allocates a scarce
resource across every catalyzed reaction. Compute it from any solved flux
distribution, then rank it into the two summary tables:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'obj', 'r_1714', 1);
ecModel = setParam(ecModel, 'lb', params.bioRxn, 0.25);
sol = solveLP(ecModel, 1);
usageData   = getEnzymeUsage(ecModel, sol.x);
usageReport = reportEnzymeUsage(ecModel, usageData);
usageReport.topAbsUsage
```
:::
:::{tab-item} 🐍 Python
:sync: python

`r_1714` (glucose exchange) follows the ordinary cobrapy exchange-reaction
convention (negative = uptake), so maximizing it still minimizes uptake
magnitude:

```python
from cobra.flux_analysis import pfba
from geckopy import enzyme_usage, report_enzyme_usage

ec_model.objective = "r_1714"
ec_model.reactions.get_by_id(params.bio_rxn).lower_bound = 0.25
sol = pfba(ec_model)
usage = enzyme_usage(ec_model, sol.fluxes)
report = report_enzyme_usage(ec_model, usage)
print(report.top_abs_usage.head(10))
```
:::
::::

`reportEnzymeUsage` / `report_enzyme_usage` returns two tables and a total:
`topAbsUsage` / `top_abs_usage` (the top-N enzymes by absolute usage;
`.head(10)` in Python takes the top ten rows), `highCapUsage` /
`high_cap_usage` (every enzyme above a capacity-usage threshold, not
limited to a top-N count), and `totalUsageFlux` / `total_usage_flux` (the
protein pool exchange's current upper bound, used as the denominator for
the percentage column). An ecModel without individual concentrations in
`ec.concs` will typically show an empty `highCapUsage` /
`high_cap_usage` table: every enzyme draws from the shared protein pool
through a usage reaction with the generous default upper bound of 1000
mg/gDCW, so capacity usage rarely comes close to that bound. Once
individual concentrations constrain some enzymes' usage reactions (see
[Proteomics integration](proteomics-integration.md)), their upper bounds
reflect measured availability instead, and capacity usage for those
enzymes can approach or reach the threshold.

### Example output

The top ten enzyme usages at a fixed growth rate of 0.25 /h, minimizing
glucose uptake:

| Protein | Absolute usage (mg/gDCW) | % of pool | kcat (s⁻¹) | Source | Reaction |
|---|---|---|---|---|---|
| P23641 | 8.7 | 7.0 | 12.3 | Standard | Phosphate transport |
| P0CD90 | 5.0 | 4.0 | 12.3 | Standard | Water diffusion |
| Q12233 | 4.7 | 3.8 | 120 | Custom | ATP synthase |
| P36148 | 4.4 | 3.5 | 0.0918 | BRENDA | Glycerol-3-phosphate acyltransferase (16:0), ER membrane |
| P05694 | 3.6 | 2.9 | 0.33 | BRENDA | 5-Methyltetrahydropteroyltriglutamate-homocysteine S-methyltransferase |
| P07256 | 3.3 | 2.7 | 50.8 | DLKcat | Ubiquinol:ferricytochrome c reductase |
| P32895 | 3.3 | 2.6 | 0.66 | BRENDA | Phosphoribosylpyrophosphate synthetase |
| P00163 | 2.9 | 2.3 | 50.8 | DLKcat | Ubiquinol:ferricytochrome c reductase |
| P33312 | 2.8 | 2.3 | 0.000667 | BRENDA | 2,5-Diamino-6-ribosylamino-4(3H)-pyrimidinone 5-phosphate reductase (NADPH) |
| P07257 | 2.7 | 2.1 | 50.8 | DLKcat | Ubiquinol:ferricytochrome c reductase |

Two entries (P23641, P0CD90) carry the standard $k_{cat}$ value, the
fallback GECKO assigns to reactions lacking a matched, organism-specific
value (see [Applying kcat values](applying-kcats.md)). A standard $k_{cat}$
near the top of the usage ranking means the model's estimate of that
enzyme's cost is itself a fallback rather than a measurement, so a
literature or BRENDA value for it, if one becomes available, would
supersede a placeholder that carries outsized weight in the result.

## Ranking bottlenecks by shadow price

Usage tells you what the current solution is spending its enzyme budget on.
It does not tell you which enzyme is actually limiting the objective: a
heavily used enzyme might have spare capacity left, while a lightly used one
sitting at its bound could be the reason the objective cannot go any higher.
`getEnzymeBottlenecks` / `get_enzyme_bottlenecks` answers that second
question directly, by solving the model and ranking every enzyme by the
absolute shadow price of its `prot_<id>` mass-balance constraint, how much
the objective would improve if that enzyme had more capacity, independent
of how much of it the current solution happens to use.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
bottlenecks = getEnzymeBottlenecks(ecModel, 'top', 10);
```

Returns a table with one row per enzyme: `uniprot`, `gene`, `shadowPrice`,
`flux`, `capUsage`, and `upperBound`, sorted by descending absolute shadow
price.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import get_enzyme_bottlenecks

bottlenecks = get_enzyme_bottlenecks(ec_model, top=10)
```

Returns a pandas DataFrame indexed by uniprot id with columns `gene`,
`shadow_price`, `flux`, `cap_usage`, `upper_bound`.
:::
::::

This is a GECKO 4 addition and not part of the original Nature Protocols
procedure. It ported in an unusual direction: it originated in an older,
unrelated Python `geckopy` package (Carrasco et al., 2023), was carried
forward into the current geckopy first, and only afterward ported into
MATLAB GECKO.

[Relaxing overconstrained proteomics](relaxing-constraints.md) applies the
same shadow-price idea for a different purpose:
`relaxProteomicsGreedy` / `relax_proteomics_greedy` uses it to pick which
proteomics constraint to loosen next, one relaxation step at a time, rather
than to produce a ranked snapshot of every enzyme at once.

## The most parsimonious proteome

Classical parsimonious FBA (pFBA) picks, among all flux distributions that
reach the objective's optimum, the one with the smallest total flux.
`getPfbaEnzymes` / `pfba_enzymes` is the enzyme-aware analogue: among the
same set of optimal flux distributions, it picks the one that uses the least
total enzyme mass, the smallest sum of `usage_prot_*` fluxes. For an
ecModel, that usually differs from classical pFBA's answer, since it
optimizes the proteome the flux distribution implies rather than the flux
magnitudes themselves.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
solution = getPfbaEnzymes(ecModel);
solution = getPfbaEnzymes(ecModel, 'fractionOfOptimum', 0.9);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import pfba_enzymes

solution = pfba_enzymes(ec_model)
solution = pfba_enzymes(ec_model, fraction_of_optimum=0.9)
```
:::
::::

`fractionOfOptimum` / `fraction_of_optimum` (default 1.0) fixes the
objective at that fraction of its optimal value before minimizing enzyme
usage; a value below 1.0 trades some objective value for potentially lower
total enzyme mass. Both implementations require `usage_prot_<id>` reactions
to be forward-only (`lb = 0`, the standard layout); a reaction flipped to
allow reverse flux is handled correctly in Python (its reverse variable is
included in the minimized sum automatically) but raises an error in MATLAB,
since minimizing raw flux there would not minimize `|flux|` for that
reaction.

## See also

- [Simulation and analysis](simulation-and-analysis.md), the flux
  distributions this page's usage and bottleneck data are computed from.
- [Relaxing overconstrained proteomics](relaxing-constraints.md), shadow
  prices used to pick which constraint to relax next.
- [GECKO light vs. full ecModels](gecko-light.md), why none of this page's
  functions work on a light ecModel.
