# GECKO 3 to GECKO 4

GECKO 4 keeps the ecModel structure of GECKO 3 (`ecModel.ec`, the `MW/kcat` coefficient) and changes the direction of the protein reactions, how a project is configured, and how kcats are gathered and assigned. GECKO 3.0 is the version described in the published Nature Protocols pipeline (see [Citations](references.md)). The sections below follow the risk of a wrong result for a GECKO 3 script or project. geckopy implements the GECKO 4 behaviour described here.

:::{admonition} Changes that pass without an error
:class: important

A GECKO 3 script keeps running after each change in this box and returns a different result.

- The protein pool exchange and the enzyme usage reactions run forward, so bounds and fluxes of `prot_pool_exchange` and `usage_prot_*` have the opposite sign ([PR #419](https://github.com/SysBioChalmers/GECKO/pull/419)).
- `fuzzyKcatMatching` divides a BRENDA kcat by the coefficient of the substrate the kcat was measured on. GECKO 3 divided by the smallest coefficient in the reaction.
- `assignKcats` and `collectKcats` use the preset `brenda_ec_tree` when `model_adapter.toml` sets no other.
- `calculateFfactor` averages each protein over the samples in which it is measured.
- `sigmaFitter` returns the smallest sigma whose percent error is within a relative 1e-9 of the smallest error. The 1e-9 tolerance is not part of GECKO 3. geckopy `fit_sigma` takes the first grid point with the smallest error (default `method="grid"`) or a continuous sigma (`method="bisect"`).
:::

## Changes by consequence

### Results that change without an error

| Change | GECKO 3 | GECKO 4 | Action |
| --- | --- | --- | --- |
| Direction of protein reactions | `usage_prot_<id>` and `prot_pool_exchange` run in reverse and carry negative flux | both run forward, and the usage of an enzyme is the positive flux of its usage reaction | Reverse the sign of bounds and fluxes read from these reactions. `upgradeEcModel` turns a GECKO 3 ecModel (see [Upgrade a GECKO 3 project](gecko3-upgrade-project.md)) |
| Substrate of a BRENDA kcat | the kcat is divided by the smallest coefficient in the reaction | the kcat is divided by the coefficient of the substrate that matched | Rebuild the kcat list. Reactions that are not written per the measured substrate get a lower kcat |
| Default kcat assignment | `selectKcatValue` (`assignKcatValues` in GECKO 4) merges a DLKcat list and a BRENDA list | `assignKcats` decides from the kcat source files in `data/kcats` with the preset `brenda_ec_tree` | Set `preset = "gecko_classic"` in `[kcat_assignment]` to keep the GECKO 3 order (see [Kcat assignment](gecko4-kcat-assignment.md)) |
| Protein fraction `f` | `calculateFfactor` averages over all samples, so a protein missing in one sample is left out of both totals | the average is over the samples in which the protein is measured | Recalculate `f` when the proteomics file has missing values |
| Sigma fit | `sigmaFitter` returns the sigma with the smallest error | it returns the smallest sigma whose percent error is within a relative 1e-9 of the smallest error (geckopy `fit_sigma`: no tolerance in the default grid) | Refit when the growth rate is flat over a range of sigma |

### Changes that raise an error

| Change | Condition | Action |
| --- | --- | --- |
| `loadProtData` checks the replicate count | the sum of `replPerCond` differs from the number of replicate columns of the file | Correct `replPerCond` |
| `loadEcModel` checks the ecModel format | `gecko_format` in the file is higher than 4 | Update GECKO |
| Adapter keys | `model_adapter.toml` has a key that is not in `adapterParameters.tsv` | Remove or rename the key, or place a key that GECKO uses and geckopy does not use under `[matlab.params]` |
| Options of `assignKcats` and `upgradeGECKOproject` | an option name that the function does not have | Correct the option name |

### Changes of the project

A GECKO 3 project is configured by an adapter class and keeps its kcats in `data/DLKcat.tsv`, `data/customKcats.tsv` and in the variables of the script. A GECKO 4 project is configured by `model_adapter.toml`, keeps each kcat source in its own file in `data/kcats`, and records the ecModel format in the saved model. [Project format 4](gecko4-project-format.md) describes the files, and [Upgrade a GECKO 3 project](gecko3-upgrade-project.md) the steps that convert a project.

Adapter classes keep working. Functions with name-value arguments also take them positionally, in the GECKO 3 order: `loadEcModel(filename, modelAdapter)` and `loadEcModel('filename', filename)` are equivalent. A call uses one of the two forms for all its optional arguments.

## New functions

The table lists a selection.

| Group | Functions |
| --- | --- |
| Kcat sources | `kcatsFromBrenda`, `kcatsFromECTree`, `kcatsFromHomologs`, `kcatsFromDLKcat`, `kcatsFromOKP`, `saveKcatSource`, `loadKcatSource`, `getEcRxnKeys` |
| Kcat assignment | `collectKcats`, `assignKcats`, `updateKcatSources`, `kcatAssignmentConfig`, `convertCustomKcats` |
| Databases | `fetchBrendaAsset`, `loadBrendaMeasurements`, `resolveKcatAggregation` |
| Project and model upgrade | `upgradeGECKOproject`, `upgradeEcModel`, `convertAdapterToToml` |
| Adapter | `TomlAdapter`, `readAdapterToml`, `writeAdapterToml`, `loadAdapterParams` |
| Proteomics | `levelComplexConcs`, `getComplexFamilies`, and the option `perComplex` of `flexibilizeEnzConcs` |
| Analysis | `getEnzymeBottlenecks`, `relaxProteomicsGreedy` |

`getEnzymeBottlenecks` solves the model again after raising the usage bound of each enzyme that runs at its bound, and ranks the enzymes by the rise of the objective. The shadow price is reported and does not enter the order.

`levelComplexConcs` gives the subunits of a multi-subunit complex one abundance. The complex is then not capped by its least abundant subunit. It runs after `fillEnzConcs` and before `constrainEnzConcs`.

kcat prediction goes through the hosted OpenKineticsPredictor service, in addition to a local DLKcat installation. The DLKcat Docker context is not part of the GECKO repository (`src/dlkcat-gecko` is removed).

## Removed

| Removed | Replacement |
| --- | --- |
| BRENDA files in `databases/` | `fetchBrendaAsset` downloads the files of the toolbox-assets release `brenda-2026.1-1` into `databases/brenda-2026.1-1` on first use. A project keeps its own files in `data/brenda` |

## Renamed functions

The old name of each function in the table calls the new function and prints a deprecation warning. Seven of the old names are in `src/deprecated`; `mergeDLKcatAndFuzzyKcats` is a wrapper of `mergeKcats` in `src/gather_kcats`. The old names are removed in a future release.

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
- Enzymes enter the S-matrix as `1/kcat`, with the molecular weight in the protein exchange reactions. From GECKO 3 the coefficient is `MW/kcat` (see [Building an empty ecModel](guide/building-ec-model.md)).
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
