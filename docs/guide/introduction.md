# Introduction to ecModels

<!-- docs-site: concept-page -->

An enzyme-constrained model (ecModel) is a genome-scale metabolic model (GEM) in which the amount of each enzyme limits the rate of the reactions that the enzyme catalyses. GECKO and geckopy build an ecModel from a conventional GEM. They add the molecular weight (MW) and the turnover number (kcat) of each enzyme, and a limit on the total mass of enzyme that the model can use.

## Conventional GEMs

A conventional GEM describes the metabolic reactions of an organism as a system of linear equations. The stoichiometric matrix (S-matrix) holds the coefficient of each metabolite in each reaction, and the variables are the reaction rates (fluxes). Bounds on the fluxes, for example a measured uptake rate of glucose, limit the set of flux distributions that the model allows (the solution space). Constraint-based methods such as flux balance analysis search this space.

A conventional GEM has no limit on the rate of a reaction other than its bounds, so a pathway with many reactions costs the model nothing more than a short pathway. An ecModel adds the protein cost of each reaction.

## The enzyme constraint

The rate $v$ of a reaction is at most the turnover number of its enzyme times the amount of the enzyme:

$$ v \le k_{cat} \cdot e $$

The enzyme mass that a flux $v$ needs is therefore at least $v \cdot MW / k_{cat}$. In a full ecModel each enzyme is a pseudometabolite, `prot_<id>`, where `<id>` is the UniProt identifier of the enzyme. Each reaction consumes the pseudometabolites of its enzyme with the coefficient

$$ -\frac{n \cdot MW}{3600 \cdot k_{cat}} $$

where $MW$ is the molecular weight of the enzyme in g/mol, $k_{cat}$ is the kcat of the reaction in 1/s, and $n$ is the number of copies of the subunit in the enzyme complex (1 for an enzyme of one subunit). The factor 3600 converts the kcat to 1/h. With fluxes in mmol/gDCW/h, one unit of flux then uses the enzyme mass of the coefficient in mg/gDCW. MW and kcat form one coefficient, which is the protein cost of the reaction. `applyKcatConstraints` (Python: `apply_kcat_constraints`) writes these coefficients from `ec.kcat`, `ec.mw` and `ec.rxnEnzMat`. A reaction with kcat 0 gets no enzyme coefficient and has no protein cost.

A reaction that more than one enzyme can catalyse (isozymes) is split into one reaction per isozyme in a full ecModel, so each copy has one enzyme and one kcat. A reversible reaction, except an exchange reaction, is split into a forward and a reverse reaction, so these fluxes are positive.

## The protein pool

Each enzyme pseudometabolite is made by its usage reaction, `usage_prot_<id>`, which takes protein mass from the pseudometabolite `prot_pool`. The flux of the usage reaction is the mass of the enzyme that the solution uses, in mg/gDCW:

$$ e_i = \sum_j \frac{n_{ij} \cdot MW_i}{3600 \cdot k_{cat,j}} \, v_j $$

The reaction `prot_pool_exchange` produces `prot_pool`, so its flux is the sum of all enzyme usages. Its upper bound is the protein pool, which `setProtPoolSize` (Python: `set_prot_pool_size`) sets to

$$ \sum_i e_i \le P_{tot} \cdot f \cdot \sigma \cdot 1000 $$

The three parameters are in `model_adapter.toml`:

| Parameter | Key | Meaning | Default |
| --- | --- | --- | --- |
| $P_{tot}$ | `p_tot` | total protein content of the cell, in g protein/gDCW | 0.5 |
| $f$ | `f` | mass fraction of the total protein that the enzymes of the model account for | 0.5 |
| $\sigma$ | `sigma` | average saturation of the enzymes in vivo, between 0 and 1 | 0.5 |

The factor 1000 converts g/gDCW to mg/gDCW. `calculateFfactor` (Python: `calculate_f_factor`) calculates $f$ from proteomics or PAXdb data, and `sigmaFitter` (Python: `fit_sigma`) selects the $\sigma$ at which the model reaches a given growth rate. [Set the protein pool](protein-pool.md) describes how to choose the three values.

A measured concentration adds a second limit to an enzyme: `constrainEnzConcs` (Python: `constrain_enz_concs`) sets the upper bound of its usage reaction to the measured value. The usage reaction still takes its mass from the pool, so the measured enzymes count toward the protein pool as well (see [Constrain enzymes with proteomics](proteomics.md)).

## Enzyme data in the model

The enzyme data of an ecModel are in the field `ec` of the model (MATLAB: `ecModel.ec`, Python: `ec_model.ec`).

| Field | Content | One entry per |
| --- | --- | --- |
| `rxns` | reaction identifiers that correspond to the reactions of the model | reaction (each isozyme has its own entry) |
| `kcat` | kcat in 1/s; 0 marks a reaction without a kcat | reaction |
| `source` | the source of the kcat | reaction |
| `notes` | notes that functions add, for example the kcat before tuning | reaction |
| `eccodes` | EC numbers | reaction |
| `genes` | the genes that code for the enzymes | enzyme |
| `enzymes` | UniProt identifiers of the enzymes | enzyme |
| `mw` | molecular weights in g/mol | enzyme |
| `sequence` | amino acid sequences | enzyme |
| `concs` | measured enzyme concentrations, NaN when not measured | enzyme |
| `rxnEnzMat` (Python: `rxn_enz_mat`) | matrix that maps reactions to enzymes, with the number of copies of each subunit | reaction and enzyme |

`makeEcModel` (Python: `make_ec_model`) creates the structure with the enzyme data from UniProt (and KEGG, for genes that UniProt does not match), and `assignKcats` (Python: `assign_kcats`) fills `kcat` and `source`. [ecModel YAML format](yaml-format.md) describes how a file stores the structure.

## Full and light ecModels

A full ecModel has one pseudometabolite and one usage reaction per enzyme, so it can be constrained with the concentration of each enzyme and reports the usage of each enzyme. A light ecModel has no pseudometabolite per enzyme: each reaction takes protein directly from `prot_pool`, with the lowest protein cost of its isozymes. It is smaller, and it cannot use proteomics data or report the usage of an enzyme (see [Choose the ecModel structure](ecmodel-structure.md)).

## Kcat values

The kcat values determine how much protein each reaction costs, so they determine the predictions of an ecModel. Measured kcats come from databases such as [BRENDA](https://www.brenda-enzymes.org/), which covers few enzymes of most organisms. GECKO fills the reactions without a measured kcat with values estimated from other measurements of the same EC number, or predicted from the enzyme sequence and the substrate structure by the methods of the OpenKineticsPredictor service. [Choose the kcat sources](kcat-sources.md) describes the sources and the presets that combine them.

Most measured kcats are in vitro values, and predicted kcats are estimates. A new ecModel can therefore grow more slowly than the organism. [Choose a kcat tuning](kcat-tuning.md) describes how to find and correct the kcats that limit growth.

## Limitations

- An ecModel has more reactions and metabolites than its GEM, so simulations take longer. A light ecModel reduces this.
- The enzyme constraint describes the capacity of each enzyme at a given kcat and saturation. Regulation such as allosteric control and post-translational modification is not part of the model.
- The predictions depend on the kcat values, which are uncertain for most reactions, in particular for enzyme complexes. Measured growth rates, fluxes and proteomics data are needed to test an ecModel.

## See also

- [Build an ecModel](first-ecmodel.md): the steps from a conventional GEM to an ecModel with the default settings.
- [Installation](../installation/index.md): install GECKO or geckopy.
- [Citations](../references.md): the publications of GECKO and of the methods it uses.
