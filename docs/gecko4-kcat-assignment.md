# Kcat assignment

<!-- docs-site: concept-page -->

GECKO 4 assigns the kcat of each reaction from kcat source files, in an order that `model_adapter.toml` sets. `collectKcats` determines the kcats and does not change the model. `assignKcats` applies the decisions and the kcat constraints. [Gathering kcats](guide/gathering-kcats.md) describes how the sources are gathered, and [Applying kcats](guide/applying-kcats.md) the steps after the assignment.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `collectKcats` | `collect_kcats` | determines one kcat per reaction and writes `output/<model id>_kcatDecisions.tsv` |
| `assignKcats` | `assign_kcats` | applies the decisions and the kcat constraints. Kcats that the model had are replaced |
| `updateKcatSources` | `update_kcat_sources` | gathers the source files that the configuration needs and that are missing or outdated |
| `kcatAssignmentConfig` | `kcat_assignment_config` | returns the settings with the preset expanded into stages |
| `parseKcatSource` | `parse_kcat_source` | splits an entry of `ec.source` into its origin, detail, tuning methods and prior |
| `formatKcatSource` | `format_kcat_source` | writes an entry of `ec.source` from these parts |

## Sources

A source is the name of a file in `data/kcats` (`custom`, `ec_tree`, `homologs`, `dlkcat`, `okp_<method>`), or one of the BRENDA quality tiers `database_exact`, `database_top` and `database_bottom`, which read `brenda.tsv`. In a stage, `okp` stands for the OpenKineticsPredictor methods of `[kcat_sources.okp] methods`, which default to all methods that have combination parameters.

| Source | Content |
| --- | --- |
| `custom` | curated kcats of the project |
| `brenda.tsv` | BRENDA kcats matched by EC number and substrate, with the origin of the match (1 to 6). A stage reads it through the tiers `database_exact`, `database_top` and `database_bottom`, not as `brenda` |
| `ec_tree` | the median of all wild-type BRENDA measurements of the EC number, shrunk towards the median of its 3-digit EC class, its 2-digit EC class and the global median (weight `n/(n+k)` for `n` measurements, `k = 5`) |
| `homologs` | the kcat of measured homologs that act on the same substrate, found with DIAMOND (at least 40 % identity and 80 % coverage of both sequences) |
| `dlkcat` | DLKcat predictions |
| `okp_<method>` | OpenKineticsPredictor predictions, with the similarity to the training sequences of the method |

## Stages

A stage determines the kcat of the reactions that are still open. The action `select` takes the first listed source that has a value. The action `combine` takes all listed sources that have a value, corrects each for the bias of the source and weights it by 1 divided by its error variance. The error variance depends on the evidence of the source for the reaction: for the EC tree the measurements of the EC number and of its EC class, for an OKP method the similarity of the enzyme to the training sequences of the method. The parameters are in `kcatCombineParams.tsv` of the BRENDA files. `model.ec.source` reads `combined (sd=<log10 sd>, n=<sources>)` for a combined value.

After the stages, `collectKcats` applies `data/customKcats.tsv` when a stage lists `custom` and `data/kcats/custom.tsv` does not exist. With `isozymes = true`, a reaction without a kcat in a full ecModel takes one from its isozymes. With `standard = true`, the remaining reactions get the standard kcat.

## Presets

`[kcat_assignment] preset` defines the stages. The default is `brenda_ec_tree`.

| Preset | Stages |
| --- | --- |
| `brenda_ec_tree` | custom kcats; the BRENDA median of the measurements of the organism on the substrate of the reaction (origin 1, no EC wildcards); the EC tree; then the OKP methods combined for the reactions that the earlier stages left open |
| `ec_tree_homologs` | custom kcats; the BRENDA value of the organism; the EC tree and the homologs combined; then the OKP methods combined |
| `ec_tree_okp` | custom kcats; the BRENDA value of the organism; the EC tree, the homologs and the OKP methods combined; then the OKP methods combined |
| `okp` | custom kcats; then the OKP methods combined |
| `gecko_median` | custom kcats; the BRENDA median of matches without EC wildcards (origin 1 to 4); DLKcat; then the other BRENDA matches (matches with EC wildcards, origin 3 to 6, and matches from specific activities without a wildcard, origin 5 and 6) |
| `gecko_classic` | as `gecko_median` with the BRENDA maximum and the specific-activity matches above DLKcat (origin up to 6), the order of the GECKO 3 tutorial |

The tutorial `full_ecModel` uses `gecko_classic`. A project lists the stages in `[[kcat_assignment.stage]]` tables in place of a preset:

```toml
[kcat_assignment]
isozymes = true
standard = true

[[kcat_assignment.stage]]
action = "select"
sources = ["custom", "database_top", "ec_tree"]
criteria = "max"
top_origin_limit = 1
```

A stage has the options `action` (default `select`), `sources`, `criteria` (default `max`), `top_origin_limit` (default 4), `bottom_origin_limit` (default 6) and `wildcard_limit` (default 3).

Against measured kcats hidden from the search, the EC tree was closer than the BRENDA median at origin 2, at origin 4 and with EC wildcards, and as close at origin 1 and 3. The EC tree combined with the OKP methods was slightly closer than the EC tree, and the OKP methods combined were as close. In ecModels, values combined with predictions set high-turnover enzymes such as ATP synthase too low. The default therefore uses predictions where measurements give no value.

## Provenance of a kcat

`ec.source` records where the kcat of each reaction came from. An entry has the form `<origin>[ (<detail>)][ | tuned=<method>[+<method>...] (prior=<value>)]`:

| Entry | Meaning |
| --- | --- |
| `brenda (wc=0, origin=1)` | a BRENDA match, with the number of EC levels that were wildcarded (`wc`) and the organism closeness of the match (`origin`) |
| `combined (sd=0.61, n=6)` | the combination of `n` sources, with the uncertainty `sd` in log10 units |
| `custom`, `standard`, `isozymes` | a curated kcat, the standard kcat, and the mean over the isozymes of the reaction |
| `manual` | a kcat that `setKcatForReactions` (Python `set_kcat_for_reactions`) set |
| `brenda (wc=0, origin=2) \| tuned=cmaes (prior=6.55)` | a kcat that tuning changed, with the kcat before the first tuning as `prior` |

The origin is the label of the kcat source in lower case with underscores (`brenda`, `ec_tree`, `okp_catapro`). The detail has the pairs `wc` and `origin` for a BRENDA match and `sd` and `n` for a combined value. The assignment writes a new origin and drops a tuning status. `sensitivityTuning` and `cmaesKcatTuning` (Python `sensitivity_tuning` and `cmaes_kcat_tuning`) keep the origin and detail of every kcat they change and add their method, `sensitivity` or `cmaes`, to the tuning status. The `prior` stays the kcat before the first tuning, and a second tuning with the same method adds nothing.

`parseKcatSource` and `formatKcatSource` read and write these entries. The parser returns the origin as it was written, the detail pairs (a number when the value is a plain decimal number, text otherwise), the tuning methods and the prior. An entry that does not follow the form is read as one origin without detail, so an entry that an earlier release wrote stays readable. The formatter writes the origin in lower case with underscores, a number with six significant digits and a prior only together with a tuning status. A detail pair without a value, with an infinite value or with a key that does not start with a letter is left out. An empty origin with a detail or a tuning status is written as `unknown`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
info = parseKcatSource('brenda (wc=0, origin=2) | tuned=cmaes (prior=6.55)');
info.origin   % 'brenda'
info.detail   % struct with wc = 0 and origin = 2
info.tuned    % {'cmaes'}
info.prior    % 6.55
text = formatKcatSource('brenda', struct('wc', 0, 'origin', 2), {'cmaes'}, 6.55);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import format_kcat_source, parse_kcat_source

info = parse_kcat_source("brenda (wc=0, origin=2) | tuned=cmaes (prior=6.55)")
info.origin   # 'brenda'
info.detail   # {'wc': 0.0, 'origin': 2.0}
info.tuned    # ('cmaes',)
info.prior    # 6.55
text = format_kcat_source("brenda", {"wc": 0, "origin": 2}, ["cmaes"], 6.55)
```
:::
::::

Functions that read `ec.source` use the origin. `getStandardKcat` and `removeStandardKcat` (Python `assign_standard_kcat` and `remove_standard_kcat`) treat a row as the standard kcat when its origin is `standard` and it has no tuning status, so a standard kcat that tuning changed is kept. The trust tiers of evotune group the kcats by the origin.

## Run the assignment

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
updateKcatSources(ecModel);                 % gather what the configuration needs
[ecModel, decisions] = assignKcats(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import assign_kcats, update_kcat_sources

update_kcat_sources(ec_model)                # gather what the configuration needs
decisions, report = assign_kcats(ec_model)   # changes ec_model in place
```
:::
::::

`updateKcatSources` has the option `dryRun`, which reports what would be gathered without gathering it. In MATLAB it checks the requirements first: Docker for a DLKcat run and an OpenKineticsPredictor API key for OKP. In Python a source with a missing requirement gets the status `failed`. A file is outdated when its header records other settings than `[kcat_sources.<name>]` asks for, or for `brenda` and `ec_tree` another BRENDA release than the files in use. `custom.tsv` and other files it cannot gather are left as they are.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| Error `kcatAssignment:config` | an empty preset, a criteria name in capitals, or a stage with a `sources` value of another type than list | Correct `[kcat_assignment]` |
| OKP sources are pending | the OpenKineticsPredictor job is still running | Call `updateKcatSources` again later |
| Kcats differ from a GECKO 3 model | the default preset is not the GECKO 3 order | Set `preset = "gecko_classic"` |
| Rows of a source file are not applied | the row fits no reaction, or part of an enzyme set | Read the report of `loadKcatSource` |

## See also

- [GECKO 3 to GECKO 4](gecko3-to-gecko4.md)
- [Project format 4](gecko4-project-format.md)
- [Gathering kcats](guide/gathering-kcats.md)
