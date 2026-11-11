# GECKO 3 to GECKO 4

GECKO 4 keeps the ecModel structure of GECKO 3 (`ecModel.ec`, the `MW/kcat` coefficient) and changes the direction of the protein reactions, how a project is configured, and how kcats are gathered and assigned. GECKO 3.0 is the version described in the published Nature Protocols pipeline (see [Citations](references.md)). The sections below follow the risk of a wrong result for a GECKO 3 script or project. geckopy implements the GECKO 4 behaviour described here.

:::{admonition} Changes that pass without an error
:class: important

A GECKO 3 script keeps running after each change in this box and returns a different result.

- The protein pool exchange and the enzyme usage reactions run forward, so bounds and fluxes of `prot_pool_exchange` and `usage_prot_*` have the opposite sign ([PR #419](https://github.com/SysBioChalmers/GECKO/pull/419)).
- `fuzzyKcatMatching` divides a BRENDA kcat by the coefficient of the substrate the kcat was measured on. GECKO 3 divided by the smallest coefficient in the reaction.
- `assignKcats` and `collectKcats` use the preset `brenda_ec_tree` when `model_adapter.toml` sets no other.
- `calculateFfactor` averages each protein over the samples in which it is measured.
- `sigmaFitter` returns the smallest sigma within a tolerance of the smallest error, and the returned ecModel has the protein pool of that sigma (see below the first table).
- `flexibilizeEnzConcs` keeps an upper bound that is higher than the new bound, and stops after a total number of iterations.

:::

## Changes by consequence

### Results that change without an error

| Change | GECKO 3 | GECKO 4 | Action |
| --- | --- | --- | --- |
| Direction of protein reactions | `usage_prot_<id>` and `prot_pool_exchange` run in reverse and carry negative flux | both run forward, and the usage of an enzyme is the positive flux of its usage reaction | Reverse the sign of bounds and fluxes read from these reactions. `upgradeEcModel` turns a GECKO 3 ecModel (see [Upgrade a GECKO 3 project](gecko3-upgrade-project.md)) |
| Substrate of a BRENDA kcat | the kcat is divided by the smallest coefficient in the reaction | the kcat is divided by the coefficient of the substrate that matched | Rebuild the kcat list. Reactions that are not written per the measured substrate get a lower kcat |
| Default kcat assignment | `selectKcatValue` (`assignKcatValues` in GECKO 4) merges a DLKcat list and a BRENDA list | `assignKcats` determines the kcat from the kcat source files in `data/kcats` with the preset `brenda_ec_tree` | Set `preset = "gecko_classic"` in `[kcat_assignment]` to keep the GECKO 3 order (see [Kcat assignment](gecko4-kcat-assignment.md)) |
| Protein fraction `f` | `calculateFfactor` averages over all samples, so a protein missing in one sample is left out of both totals | the average is over the samples in which the protein is measured | Recalculate `f` when the proteomics file has missing values |
| Enzyme bounds of `flexibilizeEnzConcs` | the new upper bound of an enzyme replaces the old bound, also when the old bound is higher; the iterations have no total limit | an upper bound is never lowered, and the iterations have a total limit (see below the table) | Check the warnings and `flexEnz` |
| File name of `loadConventionalGEM` | `.xml` is appended to every name | a name ending in `.yml` is loaded as YAML; `.xml` is appended to a name without `.xml` or `.yml` | none |
| Sigma fit | `sigmaFitter` returns the sigma with the smallest error, and an ecModel whose protein pool is set for sigma 1 | it returns the smallest sigma within a tolerance of the smallest error (see below the table), and an ecModel whose protein pool is set for that sigma | Refit when the growth rate is flat over a range of sigma; a script that called `setProtPoolSize` after `sigmaFitter` gets the same pool |

`flexibilizeEnzConcs` stops and prints a message after a total of (`iterPerEnzyme` + 1) × (number of measured enzymes) iterations, with 1000 for `iterPerEnzyme` when it is 0. On an infeasible input model, it warns with the identifier `flexibilizeEnzConcs:infeasible` and returns `flexEnz` with empty fields. `sigmaFitter` returns the smallest sigma whose growth rate differs from the target by at most the smallest difference plus 1e-9 times the growth rate at the smallest difference; geckopy `fit_sigma` has no tolerance in its default grid.

### Changes that raise an error

The changes in this table, and calls of removed functions (see [Removed](#removed)), stop a GECKO 3 script.

| Change | Condition | Action |
| --- | --- | --- |
| `loadProtData` checks the replicate count | the sum of `replPerCond` differs from the number of replicate columns of the file | Correct `replPerCond` |
| `loadEcModel` checks the ecModel format | `gecko_format` in the file is higher than 4 | Update GECKO |
| Adapter keys | `model_adapter.toml` has a key that is not in `adapterParameters.tsv` | Remove or rename the key, or place a key that GECKO uses and geckopy does not use under `[matlab.params]` |
| Options of `assignKcats` and `upgradeGECKOproject` | an option name that the function does not have | Correct the option name |
| `runDLKcat`, `writeDLKcatInput` | every call in MATLAB: the functions are deprecated and raise an error (geckopy `run_dlkcat` and `write_dlkcat_input` warn and still run) | Use `kcatsFromDLKcat(ecModel, 'via', 'docker')` |
| `sigmaFitter` raises `sigmaFitter:growthRate` | the target growth rate is not above 0 | Give a growth rate above 0 |
| `setProtPoolSize` raises `setProtPoolSize:noPoolExchange` | the model has no `prot_pool_exchange` (GECKO 3 left the model unchanged) | Give an ecModel made by `makeEcModel` |
| `getConcControlCoeffs` raises `getConcControlCoeffs:infeasible` | the model has no optimal solution | Make the model feasible first |
| `collectKcats` and `assignKcats` raise `collectKcats:legacyCustomKcats` | a stage lists `custom`, `data/kcats/custom.tsv` does not exist, and `data/customKcats.tsv` does | Run `convertCustomKcats(ecModel)` |

### Changes of the project

A GECKO 3 project is configured by an adapter class and keeps its kcats in `data/DLKcat.tsv`, `data/customKcats.tsv` and in the variables of the script. A GECKO 4 project is configured by `model_adapter.toml`, keeps each kcat source in its own file in `data/kcats`, and records the ecModel format in the saved model. `assignKcats` writes its decisions to `output/<model id>_kcatDecisions.tsv`, with column names in `snake_case` (`ec_rxn`, `spread_log10`, `sd_log10`); the table that `collectKcats` returns keeps `camelCase` names. [Project format 4](gecko4-project-format.md) describes the files, and [Upgrade a GECKO 3 project](gecko3-upgrade-project.md) the steps that convert a project.

Functions with name-value arguments also take them positionally, in the GECKO 3 order: `loadEcModel(filename, modelAdapter)` and `loadEcModel('filename', filename)` are equivalent. A call uses one of the two forms for all its optional arguments.

### Adapter classes

A GECKO 3 adapter class keeps working. It sets `obj.params` with the MATLAB names of [Model adapter parameters](guide/model-adapter-parameters.md), and `ModelAdapterManager.setDefault` takes the path of its `.m` file. `convertAdapterToToml` writes the parameters of a class as `model_adapter.toml` and lists the methods that the class overrides and the file cannot express. The option `'adapterFormat','class'` of `createGECKOproject` creates a project with a class; both the option and adapter classes as project format are deprecated (see [Deprecated](#deprecated)).

A class that needs code beyond the file can read its parameters from the file in the constructor:

```matlab
obj.params = loadAdapterParams(fullfile(projectPath, 'model_adapter.toml'));
```

In geckopy, a subclass of `ModelAdapter` overrides `get_spontaneous_reactions`, `get_uniprot_compatible_genes`, `get_uniprot_ids_from_table`, `get_kegg_compatible_genes`, `get_brenda_db_folder` or `get_phyl_dist_path`. It is instantiated explicitly; `from_folder` does not discover it.

## New functions

The table lists a selection.

| Group | Functions |
| --- | --- |
| Kcat sources | `kcatsFromBrenda`, `kcatsFromECTree`, `kcatsFromHomologs`, `kcatsFromDLKcat`, `kcatsFromOKP`, `saveKcatSource`, `loadKcatSource`, `getEcRxnKeys` |
| Kcat assignment | `collectKcats`, `assignKcats`, `updateKcatSources`, `kcatAssignmentConfig`, `convertCustomKcats` |
| Databases | `fetchBrendaAsset`, `loadBrendaMeasurements`, `resolveKcatAggregation` |
| Project and model upgrade | `upgradeGECKOproject`, `upgradeEcModel`, `convertAdapterToToml` |
| Adapter | `TomlAdapter`, `readAdapterToml`, `writeAdapterToml`, `loadAdapterParams` |
| Kcat tuning | `cmaesKcatTuning`, `screenKcatLeverage`, `selectTunableMask`, `reviewKcatAssignment`, `tunePriorPenaltyWeight`, `loadEvotuneData` |
| Proteomics | `levelComplexConcs`, `getComplexFamilies`, and the option `perComplex` of `flexibilizeEnzConcs` |
| Analysis | `getEnzymeBottlenecks`, `relaxProteomicsGreedy`, `relaxEnzConcs`, and the option `method` of `getConcControlCoeffs` |

`getEnzymeBottlenecks` solves the model again after raising the usage bound of each enzyme that runs at its bound, and ranks the enzymes by the rise of the objective. The shadow price is reported and does not enter the order.

`relaxProteomicsGreedy` returns `[result, model]`, with the relaxed model as second output. `relaxEnzConcs` raises the enzyme bounds with the least total fold increase in one linear program.

`levelComplexConcs` gives the subunits of a multi-subunit complex one abundance. The complex is then not capped by its least abundant subunit. It runs after `fillEnzConcs` and before `constrainEnzConcs`.

kcat prediction goes through the hosted OpenKineticsPredictor (OKP) service, through `kcatsFromOKP`. The default OKP method (`[okp] method`) is KinForm-H, and the `okp` stage of the presets uses the methods of `[kcat_sources.okp] methods`, by default KinForm-H alone; GECKO 4 pre-releases used CataPro and eight methods. `kcatsFromDLKcat` uses its DLKcat method unless `data/DLKcat.tsv` exists, or the option `'via', 'docker'` selects a local run in the Docker image. The DLKcat Docker context is not part of the GECKO repository (`src/dlkcat-gecko` is removed).

## Removed

| Removed | Replacement |
| --- | --- |
| BRENDA files in `databases/` | `fetchBrendaAsset` downloads the files of the toolbox-assets release `brenda-2026.1-1` into `databases/brenda-2026.1-1` on first use. A project keeps its own files in `data/brenda` |
| `truncateValues` | none; no function of GECKO 4 calls it |
| `findMaxValue` | none; geckopy keeps a port as `find_max_value` |
| `bayesianSensitivityTuning` and its helpers `abc_max`, `getcarbonnum`, `getrSample`, `updateprior` (Bayesian ABC-SMC tuning of light ecModels); `anaerobicModel_GECKO` and `changeMedia` of the same folder are now in `tutorials/full_ecModel/code` | `cmaesKcatTuning`, the advanced kcat tuning, with the data files `data/evotune*.tsv` (see [Tune kcats against experimental data](guide/advanced-tuning.md)). A stub in `src/deprecated` raises an error that names it. |
| `submitOpenKineticsPredictor`, `fetchOpenKineticsPredictor`, `writeOpenKineticsPredictorInput`, `readOpenKineticsPredictorOutput` (public in GECKO 4 pre-releases) | `kcatsFromOKP` |

## Deprecated

`updateProtPool`, `applyCustomKcats`, `runDLKcat`, `writeDLKcatInput`, `readDLKcatOutput` and the option `'adapterFormat', 'class'` of `createGECKOproject` print a deprecation warning. Adapter classes still load without a warning. Everything in the table is removed in a future release.

| Deprecated | Replacement |
| --- | --- |
| `updateProtPool` | `setProtPoolSize` with the protein content of the condition. From GECKO 3.2.0 measured enzymes draw from the protein pool, and `updateProtPool` raises an error on such an ecModel |
| `applyCustomKcats` | `convertCustomKcats` writes `data/customKcats.tsv` as `data/kcats/custom.tsv`, which `collectKcats` and `assignKcats` read |
| `runDLKcat`, `writeDLKcatInput` (raise an error), `readDLKcatOutput` (still reads the file) | `kcatsFromDLKcat` with `'via', 'docker'` or `'via', 'file'` |
| Adapter classes as project format: `createGECKOproject(..., 'adapterFormat', 'class')` and `adapterTemplate.m` | `model_adapter.toml`. Existing adapter classes still load, and `convertAdapterToToml` converts them |

## Renamed functions

The old name of each function in the table calls the new function and prints a deprecation warning. The old names are in `src/deprecated` and are removed in a future release.

| GECKO 3 name | GECKO 4 name | Reason |
| --- | --- | --- |
| `startGECKOproject` | `createGECKOproject` | |
| `copyECtoGEM` | `applyECcodes` | |
| `enzymeUsage` | `getEnzymeUsage` | |
| `pfbaEnzymes` | `getPfbaEnzymes` | |
| `addCarbonNum` | `fillCarbonNum` | |
| `updateGECKOdoc` | `buildGECKOdoc` | |
| `selectKcatValue` | `assignKcatValues` | the function writes `ecModel.ec.kcat` |
| `mergeDLKcatAndFuzzyKcats` | `mergeKcats` | merges kcat lists of any number of sources |

geckopy names a counterpart in `snake_case`; the prefix `get` is dropped for some (`enzyme_usage` for `getEnzymeUsage`, `pfba_enzymes` for `getPfbaEnzymes`) and kept by others (`merge_kcats` for `mergeKcats`). The counterpart of `createGECKOproject` is the command `geckopy init`, and the counterpart of `upgradeGECKOproject` is `geckopy upgrade`. [MATLAB and Python](matlab-vs-python.md) lists the full mapping.

## Staying on GECKO 3

The last GECKO 3 release is v3.2.5.

::::{tab-set}
:::{tab-item} MATLAB (git)

```bash
git clone https://github.com/SysBioChalmers/GECKO
cd GECKO
git checkout v3.2.5
```

Run `GECKOInstaller.install` in MATLAB.
:::
:::{tab-item} MATLAB (ZIP)

Download the v3.2.5 archive from the [GitHub releases page](https://github.com/SysBioChalmers/GECKO/releases/tag/v3.2.5), extract it and run `GECKOInstaller.install`.
:::
:::{tab-item} MATLAB (Add-On)

The Add-On manager distributes the latest release. Uninstall the Add-On (`GECKOInstaller.uninstall`, or the Add-On manager) and install v3.2.5 with git or the ZIP archive.
:::
::::

[Installation](installation/index.md) describes the installation methods.

## Earlier versions

GECKO 1 ([Sánchez et al., 2017](references.md#gecko-1)) and GECKO 2 ([Domenzain et al., 2022](references.md#gecko-2)) share one ecModel structure, which differs from GECKO 3 and GECKO 4:

- Enzyme and kcat information is spread over several model fields. From GECKO 3, `ecModel.ec` (Python: `ec_model.ec`) collects it.
- Enzymes enter the S-matrix as `1/kcat`, with the molecular weight in the protein exchange reactions. From GECKO 3 the coefficient is `MW/kcat` (see [Choose the ecModel structure](guide/ecmodel-structure.md)).
- The YAML format of GECKO 3 and GECKO 4 retains the full model content. GECKO 1 and GECKO 2 have no such format.

Functions of GECKO 3 and GECKO 4 do not work on a GECKO 1 or GECKO 2 ecModel, and the reverse. geckopy supports GECKO 4 ecModels.

The last GECKO 2 release is [2.0.3](https://github.com/SysBioChalmers/GECKO/releases/tag/v2.0.3), and the [`gecko2` branch](https://github.com/SysBioChalmers/GECKO/tree/gecko2) takes fixes for it. The GECKO 1 release is cited in [Citations](references.md#gecko-1).

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| Deprecation warning | the script calls a GECKO 3 name | Use the GECKO 4 name from Renamed functions |
| Warning when `loadEcModel` loads a model | the ecModel was saved by GECKO 3 and its protein reactions run in reverse | `loadEcModel` upgrades the loaded model. Run `saveEcModel` to store the upgraded model |
| An enzyme usage flux is negative | the model was not upgraded | Run `upgradeEcModel` |
| Error that names a key of `model_adapter.toml` | the key is not in `adapterParameters.tsv` | Place a key that GECKO uses and geckopy does not use under `[matlab.params]` |
| A rebuilt ecModel has other kcats than the GECKO 3 model | the default preset and the substrate of BRENDA kcats changed | Use `preset = "gecko_classic"` and compare the output of `collectKcats` |

## See also

- [Project format 4](gecko4-project-format.md)
- [Upgrade a GECKO 3 project](gecko3-upgrade-project.md)
- [Kcat assignment](gecko4-kcat-assignment.md)
- [GECKO and geckopy](gecko-to-geckopy.md)
