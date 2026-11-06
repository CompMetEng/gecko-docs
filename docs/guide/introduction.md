# Introduction to ecModels

<!-- docs-site: concept-page -->

An enzyme-constrained model (ecModel) is a genome-scale metabolic model (GEM) in which the capacity of each enzyme limits the rate of the reactions that the enzyme catalyses. GECKO builds an ecModel by expanding a conventional GEM with enzyme data: the molecular weight (MW) and the turnover number (kcat) of each enzyme, and a limit on the total protein mass that the enzymes use. Readers of the GECKO 3 protocol find the differences to GECKO 4 in [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md).

## Conventional GEMs and enzyme constraints

A conventional GEM reconstructs the known metabolic reactions of an organism as a system of equations whose variables are reaction rates. The stoichiometric matrix (S-matrix) holds the stoichiometric coefficient of each metabolite in each reaction. Constraint-based methods impose bounds on the reaction rates and search the solution space, the set of all metabolic states that the model allows. Each added constraint shrinks the solution space and can sharpen the predictions of the model.

The most common constraints come from condition-dependent measurements, such as nutrient uptake rates. Constraints on the catalytic capacity of enzymes add a different kind of information. Several methods integrate such constraints into conventional models: metabolism and expression models, resource balance analysis, expression and thermodynamics flux, pcModel, flux balance analysis with molecular crowding, MOMENT, GECKO, sMOMENT and ECMpy. GECKO builds an ecModel by expanding the GEM of an organism and can in principle convert models of any size. This documentation addresses genome-scale GEMs.

## The GECKO framework

GECKO converts a conventional GEM with the relation

$$ v \le k_{cat} \times e $$

where $v$ is the rate of an enzymatic reaction, $k_{cat}$ is the turnover number of the enzyme that catalyses it, and $e$ is the concentration of the enzyme. The minimum enzyme usage for a reaction rate is $v / k_{cat}$, and the enzyme mass that the rate requires is $v \times MW / k_{cat}$, where $MW$ is the molecular weight of the enzyme.

Each enzyme is a pseudometabolite (`prot_<id>`) that the reactions it catalyses consume. The coefficient of the enzyme in a reaction is

$$ -\frac{MW}{k_{cat}} $$

with $k_{cat}$ in 1/h and, for a subunit of an enzyme complex, multiplied by the number of copies of the subunit. MW and kcat form one coefficient, which is the protein cost of the reaction: the protein mass that one unit of flux requires. A single coefficient avoids a coefficient so small that it falls below the numerical tolerance of a solver. The S-matrix of an ecModel is larger than that of the conventional GEM, and the model predicts enzyme usage together with reaction rates. `ec.kcat` stores the kcat in 1/s, and `applyKcatConstraints` (Python: `apply_kcat_constraints`) converts it to 1/h when it writes the coefficient.

### Enzyme usage reactions

A full ecModel has one usage reaction per enzyme, `usage_prot_<id>`, and one protein pool exchange, `prot_pool_exchange`. Both run forward. The pool exchange produces the pseudometabolite `prot_pool`, and its upper bound is the total protein budget that `setProtPoolSize` (Python: `set_prot_pool_size`) calculates from `p_tot`, `f` and `sigma`. Each usage reaction takes protein mass from the pool and produces the enzyme pseudometabolite. The usage of an enzyme is the positive flux of its usage reaction.

Without proteomics data, the usage reactions are limited by the pool alone. A measured concentration of an enzyme sets the upper bound of its usage reaction (see [Proteomics integration](proteomics-integration.md)). For ecModels made with GECKO 3, in which both reactions run in reverse, see [Upgrade a GECKO 3 project](../gecko3-upgrade-project.md).

### Structure of ecModel.ec

The enzyme data are in the field `ecModel.ec` (Python: `ec_model.ec`) of the model.

| Field | Content | One entry per |
| --- | --- | --- |
| `rxns` | reaction identifiers that correspond to `model.rxns` | reaction (isozymes have separate entries) |
| `kcat` | turnover number in 1/s; 0 marks a reaction without kcat | reaction |
| `source` | where the kcat comes from | reaction |
| `notes` | notes that downstream functions set | reaction |
| `eccodes` | EC numbers | reaction |
| `genes` | the genes that code for the enzymes | enzyme |
| `enzymes` | UniProt identifiers of the enzymes | enzyme |
| `mw` | molecular weights | enzyme |
| `sequence` | amino acid sequences | enzyme |
| `concs` | enzyme concentrations from proteomics | enzyme |
| `rxnEnzMat` (Python: `rxn_enz_mat`) | matrix that maps reactions to enzymes, with the number of copies of each subunit | reaction and enzyme |

`makeEcModel` (Python: `make_ec_model`) creates the structure, and the later steps of the workflow fill `kcat`, `source`, `eccodes` and `concs`. [ecModel YAML format](yaml-format.md) describes how a file stores the structure, and [Project format 4](../gecko4-project-format.md) describes the project folder and the ecModel format that `saveEcModel` writes.

## Full and light ecModels

GECKO builds two ecModel layouts from the same conventional GEM. A full ecModel has one pseudometabolite and one usage reaction per enzyme, so it constrains the concentration of each enzyme. A light ecModel writes the protein cost of an enzyme into the stoichiometry of the reaction that the enzyme catalyses and has no pseudometabolite or usage reaction per enzyme. It is smaller and faster to simulate, and it cannot represent individual enzyme concentrations. Proteomics integration, enzyme usage analysis and bottleneck analysis need a full ecModel. [GECKO light and full ecModels](gecko-light.md) describes both layouts and what each gives up.

## Workflow

The workflow from a conventional GEM to an analysed ecModel has six steps. Each step has its own page.

1. Build: `makeEcModel` expands the GEM with enzyme information from UniProt and KEGG, using the parameters of the model adapter (see [Getting started](getting-started.md) and [Building an empty ecModel](building-ec-model.md)).
2. Gather kcats: `kcatsFromBrenda`, `kcatsFromECTree`, `kcatsFromHomologs`, `kcatsFromDLKcat` and `kcatsFromOKP` write one kcat source file per source in `data/kcats` (see [Gathering kcats](gathering-kcats.md)).
3. Assign kcats: `assignKcats` determines one kcat per reaction from the source files, in the order that `model_adapter.toml` sets, and constrains the reactions (see [Kcat assignment](../gecko4-kcat-assignment.md) and [Applying kcats](applying-kcats.md)).
4. Constrain with proteomics: `fillEnzConcs`, `levelComplexConcs` and `constrainEnzConcs` set the usage bounds of measured enzymes, and `flexibilizeEnzConcs` or `relaxProteomicsGreedy` loosen bounds that keep the model from its growth rate (see [Proteomics integration](proteomics-integration.md) and [Relaxing overconstrained proteomics](relaxing-constraints.md)). `levelComplexConcs` gives the subunits of a multi-subunit complex one abundance. The least abundant subunit then does not cap the complex.
5. Tune: `sensitivityTuning` raises single kcats until the model reaches a target growth rate, and the `evotune` functions fit many kcats against measured growth rates and fluxes (see [Growth-rate tuning](growth-rate-tuning.md) and [Tuning against experimental data](tuning-against-experimental-data.md)).
6. Simulate: flux balance analysis, flux variability analysis, sampling, flux scanning, enzyme usage analysis and bottleneck analysis run on the ecModel (see [Simulation and analysis](simulation-and-analysis.md) and [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md)).

## Predicted kcat values

The kcat values determine the performance of an ecModel, and the availability and accuracy of kcat values limit the reconstruction. Measured kcat values come from public databases such as [BRENDA](https://www.brenda-enzymes.org/), and the coverage is incomplete, especially for less-studied organisms. This restricted the reconstruction of ecModels to relatively few species.

GECKO fills the gaps with predicted kcat values. DLKcat is a deep-learning model that predicts the kcat of an enzyme-substrate pair, and GECKO 4 also reads predictions from the OpenKineticsPredictor service. Predicted values let GECKO assign a kcat to every enzymatic reaction and turn a conventional GEM into an ecModel without experimental kinetic data. [Gathering kcats](gathering-kcats.md) describes the sources, and [Kcat assignment](../gecko4-kcat-assignment.md) the order in which `assignKcats` uses them.

## Applications

Converting a conventional GEM to an ecModel reduces the solution space and the flux variability ranges of later simulations. The first GECKO study showed an improved prediction of phenotypes such as overflow metabolism for a yeast GEM (Sanchez et al., 2017; see [References](../references.md)). A conventional GEM predicts these phenotypes when the relevant enzymatic, transport or exchange reactions (such as oxygen uptake) are constrained by hand.

An ecModel also supports calculations that a conventional GEM does not have: pathway protein costs, flux control coefficients, and enzyme usage and bottleneck analysis (see [Enzyme usage and bottlenecks](enzyme-usage-and-bottlenecks.md)). These quantities guide and help interpret metabolic engineering strategies for the overproduction of a target metabolite.

A constraint-based method for conventional GEMs also runs on an ecModel, because GECKO adds pseudometabolites and pseudoreactions to the S-matrix and the system stays linear. These methods include flux balance analysis (FBA), flux variability analysis (FVA), flux scanning with enforced objective function (`ecFSEOF`) and context-specific reconstruction methods such as tINIT (see [Simulation and analysis](simulation-and-analysis.md)).

## Comparison with other methods

sMOMENT ([Bekiaris and Klamt, 2020](https://doi.org/10.1186/s12859-019-3329-9)) and ECMpy ([Mao et al., 2022](https://doi.org/10.3390/biom12010065)) are other methods that add enzyme constraints.

- **sMOMENT** is a simplified version of MOMENT. It gives the same predictions as MOMENT with fewer variables and includes the enzyme constraints in the standard representation of a constraint-based model. The AutoPACMEN toolbox constructs sMOMENT models from stoichiometric models.
- **ECMpy** is a Python-based workflow that adds a constraint on the total enzyme amount to a GEM, takes the protein subunit composition of a reaction into account and calibrates the enzyme kinetic parameters automatically.

GECKO integrates proteomics data, and its ecModel structures stay close to a conventional GEM. Analyses developed for conventional GEMs apply unchanged. GECKO 4 reads predicted kcat values (see [Predicted kcat values](#predicted-kcat-values)).

## Limitations

- An ecModel is much larger than its starting GEM, so large-scale simulations take more time. A light ecModel omits the bookkeeping per enzyme (see [GECKO light and full ecModels](gecko-light.md)). The trade-off is between the prediction of individual enzymes, including proteomics integration, and computation time.
- A smaller solution space improves predictions on average, and it can widen the gap to experimental observations where the applied constraints are uncertain. The kcat values, measured or predicted by DLKcat, can be inaccurate, particularly for enzyme complexes, and almost all available kinetic data are in vitro measurements that can differ from in vivo behaviour. GECKO tests an ecModel against known phenotype data and identifies the constraints to revisit (see [Growth-rate tuning](growth-rate-tuning.md) and [Tuning against experimental data](tuning-against-experimental-data.md)). Experimental data remain necessary for a high-quality reconstruction.
- An ecModel does not predict every phenotype, because constraints such as allosteric regulation and post-translational modification are not represented. Integrating these processes could shrink the solution space further.

## See also

- [Installation](../installation/index.md), set up GECKO or geckopy.
- [Getting started](getting-started.md), scaffold a project and load a first model.
- [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md), the differences for readers of the GECKO 3 protocol.
