# GECKO release notes

## 4.0.0b3 — 2026-11-23

Changes since 4.0.0b2. GECKO 4.0.0b3 requires RAVEN 3.0.0b3, which has the `experiments` functions that GECKO calls, and `GECKOInstaller` checks for them.

A `model_adapter.toml` written for 4.0.0b2 needs manual changes. Remove the keys `okp.method`, `[kcat_sources.okp_<x>] method`, `match_okp`, `[evotune.sigma0_log_source]` and `kcat_aggregate_brenda`, which are errors now. Set `gr_exp`, `[uniprot] id` and `[kegg] id`, which have no default. `showAdapterParams` lists the values the adapter resolves to.

### Changes that alter results or raise errors

Changes for GECKO 3 users, each also on the [GECKO 3 → GECKO 4](https://gecko-docs.readthedocs.io/en/latest/gecko3-to-gecko4.html) page ([#33](https://github.com/CompMetEng/GECKO/pull/33)):

- `updateProtPool`, `mergeDLKcatAndFuzzyKcats`, `applyCustomKcats` and the adapter template `adapterTemplate.m` moved to `src/deprecated` and warn. `truncateValues` is removed.
- `bayesianSensitivityTuning`, its helpers `abc_max`, `getrSample` and `updateprior`, `getcarbonnum` and `findMaxValue` raise `GECKO:removedFunction` and name the replacement. `runDLKcat` and `writeDLKcatInput` warn and then raise an error that names `kcatsFromDLKcat`.
- `collectKcats` and `assignKcats` raise `collectKcats:legacyCustomKcats` on a project with `data/customKcats.tsv` only; `convertCustomKcats` converts it.
- A GECKO 3 adapter class warns `GECKO:deprecatedAdapterClass`; `model_adapter.toml` configures GECKO and geckopy, and `convertAdapterToToml` converts a class.
- `[uniprot] id` and `[kegg] id` are empty by default (were the identifiers of *Saccharomyces cerevisiae*). `loadDatabases` raises `loadDatabases:noUniprotID` when `data/uniprot.tsv` is missing, and an empty KEGG identifier skips KEGG with a warning.
- `loadDatabases` and `getECfromDatabase` always split a gene cell of `uniprot.tsv` with several names into one row per name; the option `splitGeneCells` is removed ([#36](https://github.com/CompMetEng/GECKO/pull/36)).

Changes in the model adapter ([#34](https://github.com/CompMetEng/GECKO/pull/34)):

- `[kcat_sources.okp] methods` is the only setting that names OpenKineticsPredictor methods; `okp.method`, `[kcat_sources.okp_<x>] method`, `match_okp`, `[evotune.sigma0_log_source]` and `kcat_aggregate_brenda` are removed. The default method is KinForm-H alone (was CataPro).
- Evotune source groups are `[evotune.source_groups.<name>]` tables with `sources` and `sigma0_log`.
- A BRENDA call without an aggregation reads `[kcat_sources.brenda] aggregation`, the median for the default preset.
- `gr_exp` has no default, and unknown or malformed keys in `model_adapter.toml` are errors. `showAdapterParams` lists every parameter with its value and origin.
- `getKcatAcrossIsozymes` is now `fillKcatsFromIsozymes`; the old name is a stub that warns and forwards.

Functions that now raise an error or warn where they continued before ([#33](https://github.com/CompMetEng/GECKO/pull/33)):

- `setProtPoolSize` without `prot_pool_exchange` (`setProtPoolSize:noPoolExchange`), `sigmaFitter` with a growth rate of 0 or below (`sigmaFitter:growthRate`), `getConcControlCoeffs` after a first solve that is not optimal, `ecFSEOF` without a range to scan (`ecFSEOF:noRange`), `cmaesKcatTuning` and `screenKcatLeverage` without evotune data (`evotune:noData`), and `flexibilizeEnzConcs` on an infeasible input (`flexibilizeEnzConcs:infeasible`).
- `getComplexData` without a taxonomic id warns and returns an empty result.
- A `[kcat_sources.<name>]` table overrides only the keys it sets of the preset, where it replaced them.

The scoring of the evotune functions and the experimental data ([#38](https://github.com/CompMetEng/GECKO/pull/38)):

- `parseGECKOargs` is removed and every function uses RAVEN's `parseRAVENargs`; the error identifiers change from `parseGECKOargs:*` to `parseRAVENargs:*`.
- `loadFluxData` and `fillCarbonNum` are removed; `addCarbonNum` and `getcarbonnum` raise `GECKO:removedFunction`. `constrainFluxData`, `loadEvotuneData` and `evotuneScore` call the experiments functions of RAVEN.
- The experimental data are `fluxData.tsv`, `maxGrowth.tsv` and `zeroFlux.tsv` with the column `weight`. The evotune functions take `experimentData` (was `evoData`), and `evotuneScore` returns the carbon weights as its fourth output.
- The scoring maximises the biomass reaction of the adapter, whatever the objective of the model is.

Changes in results of gathered kcats ([#32](https://github.com/CompMetEng/GECKO/pull/32)): `ec.source` has one format. `setKcatForReactions` writes the origin `manual` (was `setKcatForReactions`), and `sensitivityTuning` and `cmaesKcatTuning` keep the origin of the kcats they change and add the tuning method.

### Added

- `kcatEvidence` shows, for selected reactions, the kcat of every source next to the kcat of the ecModel; `kcatsForReactions` gets the kcats of every source for a few reactions, and `kcatsFromOKP` has the option `jobTag` ([#37](https://github.com/CompMetEng/GECKO/pull/37)).
- `getEnzymeUsage` reports the demand ratio of the usage over the measured concentrations ([#29](https://github.com/CompMetEng/GECKO/pull/29)).
- `getIsozymeCoverage`, `zeroUnmeasuredIsozymes` and the option `zerosAsMeasured` of `loadProtData`; an abundance of 0 is read as not measured by default ([#30](https://github.com/CompMetEng/GECKO/pull/30)).
- `parseKcatSource` and `formatKcatSource` read and write the provenance of `ec.source` ([#32](https://github.com/CompMetEng/GECKO/pull/32)).
- `kcatsFromDLKcat` takes `via` (`'okp'`, `'file'`, `'docker'`), so the presets `gecko_median` and `gecko_classic` no longer need Docker; `relaxEnzConcs`; the option `restrictTo` of `constrainEnzConcs`; the option `method` of `getConcControlCoeffs` ([#33](https://github.com/CompMetEng/GECKO/pull/33)).

### Fixes

- `downloadUniProt` keeps unreviewed entries by default, as `uniprot.reviewed = false`, and `loadAdapterParams` keeps the default of an empty adapter value ([#33](https://github.com/CompMetEng/GECKO/pull/33)).
- The tutorials `full_ecModel` and `light_ecModel` are rewritten for GECKO 4 ([#33](https://github.com/CompMetEng/GECKO/pull/33)).

### Repository

GECKO is licensed under the GNU General Public License v3, as RAVEN. Help texts, comments and the README describe the code literally ([#31](https://github.com/CompMetEng/GECKO/pull/31)).
