# Compare *k*{sub}`cat` sources

`kcatEvidence` (Python `kcat_evidence`) shows, for selected reactions, the *k*{sub}`cat` that every *k*{sub}`cat` source file of the project gives, next to the *k*{sub}`cat` of the ecModel and, for a tuned *k*{sub}`cat`, the *k*{sub}`cat` before tuning. `kcatsForReactions` (Python `kcats_for_reactions`) does this for a few reactions, and also computes the EC-tree estimate and predicts the *k*{sub}`cat`s with one or several OpenKineticsPredictor (OKP) methods, without changing the source files of the project. The result is a table that shows how far a tuned *k*{sub}`cat` is from each source, and which source a curator can compare it with.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `kcatEvidence` | `kcat_evidence` | reads the source files in `data/kcats` for the selected reactions and returns the long table `evidence` and the table `summary` with one row per reaction |
| `kcatsForReactions` | `kcats_for_reactions` | `kcatEvidence` for a few reactions, with the EC-tree estimate and optional OKP predictions |
| `kcatsFromOKP` | `kcats_from_okp` | the option `jobTag` (Python `job_tag`) keeps a prediction for a few reactions apart from the prediction for all reactions |
| `sensitivityTuning` | `sensitivity_tuning` | the option `evidence` adds the `summary` table of `kcatEvidence` for the tuned reactions to the output (`tunedKcats.evidence`, Python `TunedKcatsResult.evidence`) |

## Setup

The printed output comes from the ecModel of the `full_ecModel` tutorial project of GECKO (yeast-GEM), built once in MATLAB and once in Python. MATLAB and Python print the tables in different formats. The examples need an ecModel with assigned *k*{sub}`cat`s and source files in `data/kcats` (see [Choose the *k*{sub}`cat` sources](kcat-sources.md)), in the variable `ecModel` (MATLAB) or `ec_model` (Python). The sources are read as they are: a source file that is outdated is not gathered again. The OKP predictions need an API key (see [Choose the *k*{sub}`cat` sources](kcat-sources.md#prepare-the-inputs)) and use the daily prediction quota of the key.

## Select the reactions

A reaction is selected by one of three arguments, and a reaction that any of them selects is included. Without a selection, all reactions of `ec.rxns` are included. An argument that is given and empty, for example the enzymes of a relaxation that changed none, selects no reaction.

| MATLAB | Python | Selects |
| --- | --- | --- |
| `rxns` | `rxns` | names of `ec.rxns`, conventional reaction names (a reverse direction ends with `_REV`), indices, or a logical vector over `ec.rxns` |
| `enzymes` | `enzymes` | every reaction that one of the UniProt accessions catalyses, for example the enzymes that a proteomics relaxation changed (see [Relax proteomics constraints](relaxing-proteomics.md#check-the-kcats-of-the-relaxed-enzymes)) |
| `tunedKcats` | `tuned` | the reactions that `sensitivityTuning` tuned (the output `tunedKcats`, Python `TunedKcatsResult`) |

A conventional reaction name selects every `ec.rxns` row of the reaction, that is, all isozymes of the reaction in that direction. In a light ecModel, `tunedKcats` names the reactions by their conventional name, so it selects all rows of a tuned reaction.

## Show the *k*{sub}`cat`s after a tuning

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, tunedKcats] = sensitivityTuning(ecModel);
[evidence, summary] = kcatEvidence(ecModel, 'tunedKcats', tunedKcats);
summary(1:6, [1:6 9:end])
```

The tutorial ecModel of yeast tuned 26 *k*{sub}`cat`s. `summary` has one row per tuned reaction (here without the columns `enzymes` and `eccodes`):

```text
         ecRxn           kcat      tuned    fold     prior        origin       src_brenda    src_custom    src_ec_tree    src_okp_kinform_h
    ________________    _______    _____    ____    ________    ___________    __________    __________    ___________    _________________

    {'r_0005_EXP_3'}     33.451    true      10       3.3451    {'ec_tree'}      1.3782         NaN           3.3451           2.6606
    {'r_0109'      }     55.125    true     100      0.55125    {'ec_tree'}       0.294         NaN          0.55125           2.6506
    {'r_0157'      }     5.4102    true      10      0.54102    {'ec_tree'}        8.95         NaN          0.54102           2.9454
    {'r_0209'      }     3.9054    true      10      0.39054    {'ec_tree'}         3.8         NaN          0.39054           3.3459
    {'r_0220'      }      2.657    true      10       0.2657    {'ec_tree'}         6.3         NaN           0.2657           18.417
    {'r_0279'      }    0.86522    true      10     0.086522    {'ec_tree'}        0.87         NaN         0.086522           3.0441
```

```matlab
evidence(1:5, :)
```

`evidence` has one row per *k*{sub}`cat` of a source:

```text
         ecRxn           kcat       source                         substrate                             detail          assigned
    ________________    ______    __________    _______________________________________________    __________________    ________

    {'r_0005_EXP_3'}    1.3782    {'brenda'}    {'UDP-D-glucose'                              }    {'wc=0; origin=5'}     false
    {'r_0109'      }     0.294    {'brenda'}    {'acetyl-CoA; ATP; bicarbonate'               }    {'wc=0; origin=2'}     false
    {'r_0157'      }      8.95    {'brenda'}    {'ATP; L-alanine; tRNA(Ala)'                  }    {'wc=0; origin=2'}     false
    {'r_0209'      }       3.8    {'brenda'}    {'ATP; L-arginine; tRNA(Arg)'                 }    {'wc=0; origin=2'}     false
    {'r_0220'      }       6.3    {'brenda'}    {'ATP; L-aspartate; tRNA(Asp)'                }    {'wc=0; origin=2'}     false
```

```matlab
% the same summary, returned with the tuning:
[ecModel, tunedKcats] = sensitivityTuning(ecModel, 'evidence', true);
summary = tunedKcats.evidence;
```

:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcat_evidence, sensitivity_tuning

tuned = sensitivity_tuning(ec_model)
result = kcat_evidence(ec_model, tuned=tuned)
result.summary.drop(columns=["enzymes", "eccodes"]).head(6)
```

The tutorial ecModel of yeast tuned 26 *k*{sub}`cat`s. `summary` has one row per tuned reaction (here without the columns `enzymes` and `eccodes`):

```text
         ec_rxn       kcat  tuned       fold     prior   origin  src_brenda  src_custom  src_ec_tree  src_okp_kinform_h
0  r_0005_EXP_3  33.450611   True  10.000003  3.345060  ec_tree      1.3782         NaN     3.345061           2.660570
1        r_0109  55.124986   True  99.999974  0.551250  ec_tree      0.2940         NaN     0.551250           2.650591
2        r_0157   5.410244   True  10.000008  0.541024  ec_tree      8.9500         NaN     0.541024           2.945429
3        r_0209   3.905418   True   9.999994  0.390542  ec_tree      3.8000         NaN     0.390542           3.345931
4        r_0220   2.657027   True   9.999988  0.265703  ec_tree      6.3000         NaN     0.265703          18.417250
5        r_0279   0.865219   True  10.000003  0.086522  ec_tree      0.8700         NaN     0.086522           3.044074
```

```python
result.evidence.head(5)
```

`evidence` has one row per *k*{sub}`cat` of a source:

```text
         ec_rxn    kcat  source                     substrate          detail  assigned
0  r_0005_EXP_3  1.3782  brenda                 UDP-D-glucose  wc=0; origin=5     False
1        r_0109  0.2940  brenda  acetyl-CoA; ATP; bicarbonate  wc=0; origin=2     False
2        r_0157  8.9500  brenda     ATP; L-alanine; tRNA(Ala)  wc=0; origin=2     False
3        r_0209  3.8000  brenda    ATP; L-arginine; tRNA(Arg)  wc=0; origin=2     False
4        r_0220  6.3000  brenda   ATP; L-aspartate; tRNA(Asp)  wc=0; origin=2     False
```

```python
# the same summary, returned with the tuning:
tuned = sensitivity_tuning(ec_model, evidence=True)
tuned.evidence
```

:::
::::

The columns of `summary`:

| Column (Python) | Content |
| --- | --- |
| `ecRxn` (`ec_rxn`) | the row of `ec.rxns` |
| `kcat` | the *k*{sub}`cat` of the ecModel |
| `tuned`, `fold`, `prior` | whether the *k*{sub}`cat` has a tuning status in `ec.source`, `kcat / prior` (`NaN` without a positive prior), and the *k*{sub}`cat` before the first tuning (`NaN` without one) |
| `origin` | the origin of the *k*{sub}`cat` in `ec.source` |
| `enzymes`, `eccodes` | the enzymes and the EC numbers of the row, joined by `;` |
| `src_<source>` | the median of the *k*{sub}`cat`s that the source file `<source>` gives for the row; `NaN` when it gives none |

`evidence` has one row per *k*{sub}`cat` of a source, with the columns `ecRxn` (`ec_rxn`), `kcat`, `source`, `substrate`, `detail` and `assigned`. `assigned` is true when the *k*{sub}`cat` equals the *k*{sub}`cat` that was assigned to the reaction, that is, the *k*{sub}`cat` before tuning for a tuned reaction and the *k*{sub}`cat` of the ecModel for any other. The comparison allows a relative difference of $10^{-5}$, because `ec.source` stores the prior with six significant digits. Two sources with the same *k*{sub}`cat` are both marked. The column `detail` has the detail of the source file, for example the number of measurements and the EC level of an EC-tree value.

The tuned *k*{sub}`cat` and the sources are on one scale, so `fold` and the `src_` columns show which source the tuned *k*{sub}`cat` moves toward. A tuned *k*{sub}`cat` that is within the range of one source supports that source. A tuned *k*{sub}`cat` above all sources is a prompt to check the measurement or the enzyme, and is not evidence for the value itself.

## Get the *k*{sub}`cat`s for one reaction

`kcatsForReactions` selects reactions as `kcatEvidence` does, reads every source file, and computes the EC-tree estimate for the reactions from the BRENDA measurements, also when the project has an `ec_tree.tsv`: the computed estimate replaces the file in the table, so it is not outdated. The estimate depends on the EC number only, because BRENDA measurements have no direction. A reaction and its reverse direction (`_REV`) therefore get the same EC-tree value, and `detail` of the reverse direction ends with `direction=reverse`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[evidence, summary] = kcatsForReactions(ecModel, 'r_0005_EXP_3')
```

`summary` of `r_0005_EXP_3`, a reaction that `sensitivityTuning` tuned. The project has the OKP predictions of KinForm-H for all reactions:

```text
         ecRxn           kcat     tuned    fold    prior       origin            enzymes               eccodes           src_brenda    src_custom    src_ec_tree    src_okp_kinform_h
    ________________    ______    _____    ____    ______    ___________    _________________    ____________________    __________    __________    ___________    _________________

    {'r_0005_EXP_3'}    33.451    true      10     3.3451    {'ec_tree'}    {'Q04952;P06780'}    {'2.4.1.34;3.6.5.2'}      1.3782         NaN          3.3451            2.6606
```

`evidence` of the same reaction:

```text
         ecRxn           kcat          source              substrate              detail          assigned
    ________________    ______    _________________    _________________    __________________    ________

    {'r_0005_EXP_3'}    1.3782    {'brenda'       }    {'UDP-D-glucose'}    {'wc=0; origin=5'}     false
    {'r_0005_EXP_3'}    1.1771    {'okp_kinform_h'}    {'UDP-D-glucose'}    {'similarity=0'  }     false
    {'r_0005_EXP_3'}    2.6426    {'okp_kinform_h'}    {'UDP-D-glucose'}    {'similarity=0'  }     false
    {'r_0005_EXP_3'}    2.6785    {'okp_kinform_h'}    {'UDP-D-glucose'}    {'similarity=0'  }     false
    {'r_0005_EXP_3'}    2.7391    {'okp_kinform_h'}    {'UDP-D-glucose'}    {'similarity=0'  }     false
    {'r_0005_EXP_3'}    3.3451    {'ec_tree'      }    {0x0 char       }    {'n=1; depth=4'  }     true
```

```matlab
[evidence, summary] = kcatsForReactions(ecModel, {'r_0152', 'r_0152_REV'});
```

:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcats_for_reactions

result = kcats_for_reactions(ec_model, ["r_0005_EXP_3"])
result.summary
```

`summary` of `r_0005_EXP_3`, a reaction that `sensitivity_tuning` tuned. The project has the OKP predictions of KinForm-H for all reactions:

```text
         ec_rxn       kcat  tuned       fold    prior   origin        enzymes           eccodes  src_brenda  src_custom  src_ec_tree  src_okp_kinform_h
0  r_0005_EXP_3  33.450611   True  10.000003  3.34506  ec_tree  Q04952;P06780  2.4.1.34;3.6.5.2      1.3782         NaN     3.345061            2.66057
```

```python
result.evidence
```

`evidence` of the same reaction:

```text
         ec_rxn      kcat         source      substrate          detail  assigned
0  r_0005_EXP_3  1.378200         brenda  UDP-D-glucose  wc=0; origin=5     False
1  r_0005_EXP_3  1.177076  okp_kinform_h  UDP-D-glucose    similarity=0     False
2  r_0005_EXP_3  2.642639  okp_kinform_h  UDP-D-glucose    similarity=0     False
3  r_0005_EXP_3  2.678501  okp_kinform_h  UDP-D-glucose    similarity=0     False
4  r_0005_EXP_3  2.739118  okp_kinform_h  UDP-D-glucose    similarity=0     False
5  r_0005_EXP_3  3.345061        ec_tree                   n=1; depth=4      True
```

```python
result = kcats_for_reactions(ec_model, ["r_0152", "r_0152_REV"])
```

:::
::::

The tuned *k*{sub}`cat` of `r_0005_EXP_3` is 10 times the EC-tree estimate, which is the *k*{sub}`cat` before tuning, and is above the BRENDA *k*{sub}`cat` and the four predictions of KinForm-H.

## Predict the *k*{sub}`cat`s of a few reactions with OKP

The option `okp` submits the enzyme-substrate pairs of the selected reactions to OKP: `true` for the first method of `[kcat_sources.okp] methods`, a method name or a list of names, or `'all'` for every method that `kcatsFromOKP` accepts. `false` or an empty value submits nothing. CatPred and TurNup are not among the methods, because they read whole reactions. The function waits for each job to finish, and submits a new job on every call. A method that fails is reported and the other methods continue; the methods without predictions are listed at the end.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[evidence, summary] = kcatsForReactions(ecModel, 'r_0005_EXP_3', 'okp', 'all');
[evidence, summary] = kcatsForReactions(ecModel, 'r_0005_EXP_3', 'okp', {'KinForm-H', 'UniKP'});
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
result = kcats_for_reactions(ec_model, ["r_0005_EXP_3"], okp="all")
result = kcats_for_reactions(ec_model, ["r_0005_EXP_3"], okp=["KinForm-H", "UniKP"])
```
:::
::::

Each method submits one job and uses the daily prediction quota of the API key. The predictions of a method are written to `data/kcats/okp_<method>__query.tsv`, and the job, its input and its result to `data/OKP_job_<method>__query.txt`, `data/OKP_query_query.csv` and `data/OKP_output_<method>__query.csv`. These files are separate from the files `updateKcatSources` gathers for all reactions (`okp_<method>.tsv`, `data/OKP.csv`, `data/OKP_job_<method>.txt`, `data/OKP_output_<method>.csv`), which a query leaves as they are. A query file holds the predictions of the last query, and the next query of the method replaces it. The default sources of `kcatEvidence` and `kcatsForReactions` include the query files, so a default call shows the predictions of an earlier query for the same reactions. With `sources`, `kcatsForReactions` adds the query files of the methods that it asked for.

The option `jobTag` of `kcatsFromOKP` (Python `job_tag`) gives the same separation to a call of `kcatsFromOKP` with its own tag. `kcatsFromOKP(ecModel, 'method', 'UniKP', 'ecRxns', {'r_0005_EXP_3'}, 'jobTag', 'mine')` writes `okp_unikp__mine.tsv` and `data/OKP_query_mine.csv`. The tag is written in lower case, with each run of other characters than letters and digits as `_`, and it must have at least one letter or digit. `ecRxns` (Python `ec_rxns`) takes names of `ec.rxns`, indices or a logical (Python: boolean) vector.

## Save the table

`saveAs` of `kcatEvidence` (Python `save_as`) writes `summary` to a tab-separated file, for example to hand the *k*{sub}`cat`s of the tuned reactions to a curator.

## Troubleshooting

| Problem | Reason | Solution |
| --- | --- | --- |
| `Not reactions of model.ec` | a name in `rxns` or `tunedKcats` is neither a row of `ec.rxns` nor a conventional reaction | use the names of `ec.rxns` or the conventional name, including `_REV` for a reverse direction |
| `Not in model.ec.enzymes` | an accession in `enzymes` is not an enzyme of the ecModel | remove it; remove `prot_pool` from `flexEnz.uniprotIDs` (see [Relax proteomics constraints](relaxing-proteomics.md#check-the-kcats-of-the-relaxed-enzymes)) |
| a `src_` column is `NaN` for a reaction | the source file has no row for the reaction and its enzymes | gather the file again with `updateKcatSources`, or accept that the source has no value |
| rows of a source file are reported as not matching any reaction | the file was made from another ecModel | the message of `loadKcatSource` lists them; gather the file again |
| `kcatsForReactions` has no OKP column | the job failed, for example without an API key, or the reaction has no SMILES | the failure is reported for each method; fix the cause and call again |
| `src_ec_tree` is `NaN` | no BRENDA measurement for the EC number, or the reaction has no EC number | fill the EC numbers (see [Choose the *k*{sub}`cat` sources](kcat-sources.md#prepare-the-inputs)) |

## See also

- [Choose the *k*{sub}`cat` sources](kcat-sources.md), the source files and how `updateKcatSources` gathers them.
- [Choose a *k*{sub}`cat` tuning](kcat-tuning.md), the check of a tuned *k*{sub}`cat` against its source.
- [Tune *k*{sub}`cat`s with sensitivityTuning](standard-tuning.md), the tuning that returns `tunedKcats`.
- [Relax proteomics constraints](relaxing-proteomics.md), the methods that return the relaxed enzymes.
- [API reference](../api/index.md), every function in both toolboxes.
