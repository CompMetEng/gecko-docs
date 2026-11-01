# GECKO and geckopy

<!-- docs-site: concept-page -->

GECKO (MATLAB) and geckopy (Python) build and analyse enzyme-constrained models with the same algorithms, read the same project folder and exchange ecModels in the same YAML format. The two implementations correspond in objects and algorithms. They differ in some names, in some functions and in some behaviour.

[MATLAB and Python](matlab-vs-python.md) pairs every function that exists on both sides and links each to its API entry.

## Implementations

- **GECKO** is built on the RAVEN toolbox and the COBRA Toolbox. An ecModel is a RAVEN struct with the field `ec`. The release number is in `version.txt`.
- **geckopy** is built on [cobrapy](https://cobrapy.readthedocs.io/en/latest/) and [raven-toolbox](https://github.com/CompMetEng/raven-toolbox). An ecModel is an `EcModel`, a subclass of `cobra.Model`, with the attribute `ec`. The release number is in `pyproject.toml`.
- **Project and model files** are shared. Both read the project from `model_adapter.toml` and write `gecko_format` to the saved model (see [Project format 4](gecko4-project-format.md)).

## Corresponding objects

| Aspect | GECKO (MATLAB) | geckopy (Python) |
|---|---|---|
| Model | RAVEN struct with the field `ec` | `EcModel(cobra.Model)` with the attribute `ec` |
| Enzyme access | index into the arrays of `ecModel.ec` | `Enzyme` proxy: `model.enzymes.get_by_id("P00350")` |
| Adapter | `TomlAdapter`, or a `ModelAdapter` class | `ModelAdapter.from_folder`, parameters validated as `ModelParameters` |
| Default adapter | `ModelAdapterManager.getDefault()` | none; `adapter` argument or `model.adapter` |
| Results | `[model, result] = f(model, ...)` | a function changes the model in place and returns one value, a dataclass where MATLAB returns several |
| Tables | structs, cell arrays and MATLAB tables | `pandas.DataFrame` |
| Names | `camelCase` | `snake_case` |
| Indexing | 1-based | 0-based |
| Web access | `webread` | `requests` |
| ecModel file | `saveEcModel` writes YAML or SBML, `loadEcModel` reads YAML | `save_ec_model` and `load_ec_model` use YAML |

## Names that differ in more than case

The table is a selection; [MATLAB and Python](matlab-vs-python.md) lists all pairs.

| MATLAB | geckopy |
|---|---|
| `applyECcodes` | `copy_ec_to_gem` |
| `constrainFluxData` | `apply_flux_data_constraints` |
| `getECfromDatabase` | `fill_eccodes_from_database` |
| `getECfromGEM` | `fill_eccodes_from_gem` |
| `evotuneScore` | `evotune_distance` |
| `getEcRxnKeys` | `ec_rxn_keys` |
| `assignKcatValues` | `apply_kcat_list` |
| `getKcatAcrossIsozymes` | `fill_kcats_from_isozymes` |
| `getStandardKcat` | `assign_standard_kcat` |
| `getEnzymeUsage` | `enzyme_usage` |
| `getComplexFamilies` | `complex_families` |
| `getPfbaEnzymes` | `pfba_enzymes` |
| `sigmaFitter` | `fit_sigma` |
| `reviewKcatAssignment` | `review_assignment` |
| `upgradeGECKOproject` | `upgrade_project`, command `geckopy upgrade` |
| `createGECKOproject` | command `geckopy init` |
| `writeOpenKineticsPredictorInput` | `build_okp_input_csv` in `geckopy.gather_kcats.open_kinetics_predictor` |
| `readOpenKineticsPredictorOutput` | `parse_okp_output` in `geckopy.gather_kcats.open_kinetics_predictor` |

## Functions of one implementation

### GECKO

| MATLAB | Reason |
|---|---|
| `ModelAdapterManager` | geckopy has no global default adapter. |
| `plotEcFVA` | A plot is drawn from the DataFrame that `ec_fva` returns, with matplotlib or seaborn. |
| `updateProtPool` | `setProtPoolSize` and `set_prot_pool_size` supersede it. |
| `convertAdapterToToml` | geckopy adapters are configured by `model_adapter.toml`, so there is no adapter class to convert. |

`ecTreeEstimate` and `kcatAssignmentConfig` have a counterpart in geckopy (`ECTree.estimate` and `kcat_assignment_config` in `geckopy.gather_kcats`) that `geckopy` does not export.

### geckopy

| Group | Examples |
|---|---|
| Result and data types | `TunedKcatsResult`, `FlexEnzResult`, `BrendaData`, `PhylDist`, `FluxData`, `Enzyme` |
| Build steps of `make_ec_model` | `geckopy.ec_model.pipeline.add_protein_usage_reactions` and the other steps that `makeEcModel` runs inline |
| Algorithms | `relax_enz_concs` (least total fold increase of the enzyme bounds in one linear program), `level_complex_abundances` (one abundance per complex), `sweep_tunable_mask_size` and `recommend_target_impact_share` (share of kcats that `cmaes_kcat_tuning` tunes) |

## Differences in behaviour

The scenarios of the [raven-gecko-parity](https://github.com/CompMetEng/raven-gecko-parity) repository run both implementations on the same input and compare the results. The ledger of that repository records two differences as checkpoints, and further differences in the notes of single rows.

- **`ecFSEOF` and `ec_fseof`** return the same target reactions on ecTestGEM. On the ecYeastGEM of the tutorial the order of targets differs in 27 positions, and the set of targets depends on the solver pair, because the pFBA solution that the regression uses is not unique. On ecYeastGEM 9.1.1 the order is the same.
- **`upgradeGECKOproject` and `upgrade_project`** differ for a project that has an adapter class and no `model_adapter.toml`. `upgradeGECKOproject` converts the class. `upgrade_project` lists the adapter for conversion by hand, because an adapter class is MATLAB code, and then skips the conversion of the custom kcats and the stored predictions.
- **`sigmaFitter` and `fit_sigma`** scan the same grid of 0.01 steps. `sigmaFitter` returns the smallest sigma within a relative 1e-9 of the smallest error, and `fit_sigma` takes the first grid point with the smallest error, so solver rounding noise on a growth plateau can move its result to a later grid point. `fit_sigma` with `method="bisect"` returns a continuous sigma.
- **`saveEcModel` and `save_ec_model`** write files that differ in charge, SBO terms, gene names and the subsystem of the protein usage reactions, because the models in memory differ in these fields; the layout of the files agrees.

## See also

- [MATLAB and Python](matlab-vs-python.md), the full function pairing.
- [GECKO 3 to GECKO 4](gecko3-to-gecko4.md), the changes between the two major versions.
- [Installation](installation/index.md)
