# Executed examples

<!-- docs-site: concept-page -->

The [Guide examples](https://github.com/CompMetEng/gecko-docs/actions/workflows/examples.yml) workflow runs the code of four task pages, MATLAB and Python separately: [Basic model operations](basic-model-operations.md), [Analyse an ecModel](analysis.md), [Enzyme usage and bottlenecks](enzyme-usage.md) and [Find engineering targets](engineering-targets.md). It starts when a guide page, the example data, the runner or the workflow changes, when the GECKO or geckopy submodule moves, and once a week against the latest GECKO, geckopy and RAVEN. A run fails when a block raises an error or prints output that differs from the output shown beneath it. A block without an output block is run and not compared. The blocks of a page run in order in one session, so a block uses what the preceding blocks made. Reading a page starts at its Setup section.

## What runs

Each page of the set loads the tuned ecModel of the `full_ecModel` tutorial and its conventional GEM from the project folder `docs/data/ecMyModel`, which holds `model_adapter.toml`, `models/ecModel.yml`, `models/yeast-GEM.yml` and `data/fluxData.tsv`. The runner copies the folder to a scratch directory for every page, so a block that writes a file leaves nothing behind. MATLAB solves with the GLPK that comes with RAVEN and Python with the GLPK of cobrapy, the open-source solver that every reader has. The numbers are those of Gurobi to the digits shown, with two kinds of exception that the output blocks mark with `...`: the digits of a growth rate after the ninth place, and a value that a degenerate problem leaves open, such as the shadow price of an enzyme that carries no flux and the order of two genes with the same slope. A run of the whole set takes about three minutes in Python and about seven minutes in MATLAB, most of the MATLAB time in the `ecFSEOF` scan of [Find engineering targets](engineering-targets.md).

## What does not run

The other pages of the guide are not executed. Their output blocks come from one run by hand with the tutorial project and Gurobi, and the numbers on them are not checked again.

- [Build an ecModel](first-ecmodel.md), [Choose the ecModel structure](ecmodel-structure.md), [Choose the *k*{sub}`cat` sources](kcat-sources.md) and [Set the protein pool](protein-pool.md) start from the conventional GEM and the database files of the tutorial, which are more than 10 MB of UniProt, KEGG and SMILES tables. The steps build the ecModel and assign the *k*{sub}`cat` values. [Choose the ecModel structure](ecmodel-structure.md) also downloads the enzyme complexes from the Complex Portal.
- [Choose a *k*{sub}`cat` tuning](kcat-tuning.md), [Tune *k*{sub}`cat` values with sensitivityTuning](standard-tuning.md) and [Tune *k*{sub}`cat` values with evotune](evotune.md) start from the untuned ecModel with its protein pool, which the data folder of the executed pages does not hold, and tuning solves a long series of linear problems. Evotune runs for hours.
- [Constrain enzymes with proteomics](proteomics.md), [Relax proteomics constraints](relaxing-proteomics.md) and [Compare *k*{sub}`cat` sources](kcat-evidence.md) need the proteomics data and the *k*{sub}`cat` source files of the tutorial, and the relaxation solves a long series of linear problems.
- [Set custom *k*{sub}`cat` values](custom-kcats.md) edits `custom.tsv` with placeholder reaction identifiers that the tutorial ecModel does not contain.
- [Make a context-specific ecModel](context-ecmodel.md) needs a context-specific GEM, which the yeast tutorial does not have.
- [Experimental data](experimental-data.md) and [Model adapter parameters](model-adapter-parameters.md) show excerpts of project files, which depend on the project.

Some blocks of the four executed pages are marked as not run on their own page:

- The flux variability analysis of [Analyse an ecModel](analysis.md) solves two linear problems for each of the 4102 reactions of the conventional GEM, on the GEM and on the ecModel. With GLPK, Python takes about 21 minutes for the page, and MATLAB takes about 19 minutes and returns `NaN` for part of the reactions of the ecModel, so the median range of the ecModel is not a number.
- The sampling of [Analyse an ecModel](analysis.md) draws 1000 samples from the solution space of the ecModel, which took more than 15 minutes with Gurobi.
- The parsimonious FBA of the MATLAB tab of [Basic model operations](basic-model-operations.md), `solveLP(ecModel, 1)`, did not finish within ten minutes with GLPK. The Python tab runs `pfba` in seconds, and `getPfbaEnzymes` after it runs in MATLAB.
- The control coefficients of [Enzyme usage and bottlenecks](enzyme-usage.md) solve one linear problem for each of the 1145 enzymes with a usage reaction.
