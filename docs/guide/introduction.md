# Introduction to ecModels

<!-- docs-site: concept-page -->

Genome-scale metabolic models (GEMs) let you explore metabolism
mathematically, and have accelerated work in biotechnology, biomedicine and
fundamental biology. A conventional GEM reconstructs all known metabolic
reactions of an organism into a computational format: a system of equations
whose variables are reaction rates, represented in a stoichiometric matrix
(S-matrix) that holds the stoichiometric coefficient of each metabolite in
each reaction.

Constraint-based methods solve that system by imposing bounds on reaction
rates and searching for solutions within the resulting solution space, the
set of all metabolic states the model allows. Adding more constraints shrinks
the solution space and can sharpen the model's predictions.

The most common constraints come from condition-dependent measurements, such
as nutrient uptake rates. Constraints on the catalytic capacity of enzymes
add a different kind of information: several methods integrate such
constraints into conventional models, including metabolism and expression
models, resource balance analysis, expression and thermodynamics flux,
pcModel, flux balance analysis with molecular crowding, MOMENT, GECKO,
sMOMENT and ECMpy. Among these, GECKO builds enzyme-constrained models
(ecModels) by expanding a conventional GEM for a given organism. GECKO can in
principle convert models of any size, though this documentation focuses on
genome-scale GEMs.

## The GECKO framework

GECKO converts a conventional GEM into an enzyme-constrained version. The
conversion rests on the relation:

$$ v \le k_{cat} \times e $$

where $v$ is the rate of an enzymatic reaction, $k_{cat}$ is the turnover
number of the enzyme that catalyzes it, and $e$ is the enzyme's
concentration. The minimum enzyme usage for a given reaction rate is
therefore $v / k_{cat}$, and the enzyme mass required is $v \times MW /
k_{cat}$, where $MW$ is the enzyme's molecular weight.

Each enzyme is added to the model as a pseudo-substrate of the reaction it
catalyzes, so the model tracks both the turnover number and the molecular
weight of every enzyme it constrains.

### Enzyme usage reactions

GECKO adds enzyme usage reactions to the model. Without proteomics data, all
protein mass is drawn from a shared total protein pool. When quantitative
data are available for an enzyme, that value constrains the reactions the
enzyme catalyzes directly, and its mass is subtracted from the protein pool
(see [Proteomics integration](proteomics-integration.md)).

Earlier GECKO versions carried $k_{cat}$ and molecular weight as separate
coefficients in the metabolic and enzyme usage reactions. Current GECKO
combines them into a single stoichiometric coefficient:

$$ -\frac{MW}{k_{cat}} $$

This reduces the chance that a reaction's enzyme usage coefficient becomes so
small that it falls below a solver's numeric tolerance and causes solver
issues. The combined term is also the quantity referred to as protein cost:
the protein mass an enzymatic reaction requires per unit of flux. Compared
with a conventional GEM, the S-matrix is larger, and the model can predict
enzyme usage alongside reaction rates.

## Full and light ecModels

GECKO can build two different ecModel layouts from the same conventional
GEM. A **full** ecModel adds one pseudo-metabolite and one usage reaction per
enzyme, so it can represent and constrain each enzyme's concentration
individually. A **light** ecModel instead folds the protein cost of an
enzyme directly into the stoichiometry of the reaction it catalyzes, with no
per-enzyme bookkeeping: it is smaller and much faster to simulate, but cannot
represent individual enzyme concentrations, so proteomics integration and
per-enzyme usage or bottleneck analysis are only available on a full
ecModel.

Choosing between the two, and what each gives up, is covered on its own page:
see [GECKO light vs. full ecModels](gecko-light.md).

## Predicted kcat values

Because $k_{cat}$ values dominate ecModel performance, their availability and
accuracy matter more than almost anything else in the reconstruction.
Measured $k_{cat}$ values come from public databases such as BRENDA, but
coverage is far from complete, especially for less-studied organisms, which
historically limited ecModel reconstruction to relatively few species.

GECKO addresses this gap with DLKcat, a deep-learning model that predicts
$k_{cat}$ values for a given enzyme-substrate pair. Predicted values have
been shown to substantially improve ecModel reconstruction across hundreds of
yeast and fungal species, and in principle let GECKO assign a $k_{cat}$ value
to every enzymatic reaction, turning any conventional GEM into an ecModel
even without experimental kinetic data. See
[Gathering kcat values](gathering-kcats.md) for how to run DLKcat and combine
its output with values collected from BRENDA.

## Applications

GECKO's main use is converting a conventional GEM into an ecModel, which
substantially reduces the solution space and the flux variability ranges of
subsequent simulations. That reduction improves the prediction of phenotypes
such as overflow metabolism and batch growth in microbes, phenotypes a
conventional GEM cannot capture unless the relevant enzymatic, transport, or
exchange reactions (such as oxygen uptake) are constrained by hand.

An ecModel also enables calculations that have no equivalent in a
conventional GEM: pathway protein costs, flux control coefficients, and
enzyme usage or bottleneck analysis (see
[Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md)). These
quantities can guide and help interpret metabolic engineering strategies for
overproduction of a target metabolite.

Any constraint-based method that works on a conventional GEM also works on an
ecModel, because GECKO only expands the S-matrix with additional
pseudo-metabolites and pseudo-reactions and keeps the system linear. This
includes flux balance analysis (FBA), flux variability analysis (FVA), flux
scanning based on enforced objective flux, and context-specific
reconstruction methods such as tINIT (see
[Simulation and analysis](simulation-and-analysis.md)).

## Comparison with other methods

Enzyme constraints can also be added by other methods, such as sMOMENT and
ECMpy, with broadly similar applications.

- **sMOMENT** adds a protein pool pseudo-metabolite to metabolic reactions
  and an exchange reaction for it, producing a model similar to a GECKO light
  ecModel. sMOMENT is Python-based and cannot construct a full ecModel.
- **ECMpy** keeps the protein pool constraint outside the S-matrix rather
  than adding enzymes into reactions, giving a smaller model. Its constraint
  is harder to use directly in constraint-based simulation tools built for
  conventional GEMs.

GECKO differs from these methods in its capability for proteomics data
integration and in the reach of the ecModel structures it produces, which
stay close enough to a conventional GEM that virtually any analysis developed
for conventional GEMs applies unchanged. Its deep learning-predicted enzyme
kinetics (DLKcat) also give it wider parameter coverage than methods that
rely only on measured kinetics.

## Limitations

- ecModels are much larger than their starting GEM, so large-scale
  simulations cost substantially more to run. Light ecModels address this by
  disabling per-enzyme bookkeeping (see [GECKO light vs. full
  ecModels](gecko-light.md)); the trade-off is between individual
  enzyme-level prediction (and proteomics integration) and computational
  speed.
- Shrinking the solution space improves predictions on average, but can also
  widen the gap from experimental observations where the applied constraints
  are themselves uncertain. $k_{cat}$ values, whether measured or predicted
  by DLKcat, can be inaccurate, particularly for enzyme complexes, and almost
  all available kinetic data reflect in vitro measurements that may not match
  in vivo behavior. GECKO provides ways to test an ecModel against known
  phenotype data and to identify which constraints to revisit (see
  [Growth-rate tuning](growth-rate-tuning.md) and
  [Tuning against experimental data](tuning-against-experimental-data.md)),
  but experimental data stay necessary for a high-quality reconstruction.
- Even with enzyme constraints in place, an ecModel cannot predict every
  phenotype, because constraints such as allosteric regulation and
  post-translational modification are not represented. Integrating those
  processes could shrink the solution space further and improve prediction
  accuracy beyond what enzyme constraints alone provide.

## Where to go next

[Installation](../installation/index.md) covers setting up GECKO or
geckopy. [Getting started](getting-started.md) then scaffolds a project and
loads a first model, and [Building an ecModel](building-ec-model.md) walks
through expanding a conventional GEM into ecModel structure.
