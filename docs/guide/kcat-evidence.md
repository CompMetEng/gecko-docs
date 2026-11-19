# Compare the kcats of the sources for a reaction

`kcatEvidence` (Python `kcat_evidence`) shows, for selected reactions, the kcat that every kcat source file of the project gives, next to the kcat of the ecModel and, for a tuned kcat, the kcat before tuning. `kcatsForReactions` (Python `kcats_for_reactions`) does this for a few reactions, and also computes the EC-tree estimate and predicts the kcats with one or several OpenKineticsPredictor (OKP) methods, without changing the source files of the project. The result is a table that shows how far a tuned kcat is from each source, and which source a curator can compare it with.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `kcatEvidence` | `kcat_evidence` | reads the source files in `data/kcats` for the selected reactions and returns the long table `evidence` and the table `summary` with one row per reaction |
| `kcatsForReactions` | `kcats_for_reactions` | `kcatEvidence` for a few reactions, with the EC-tree estimate and optional OKP predictions |
| `kcatsFromOKP` | `kcats_from_okp` | the option `jobTag` (Python `job_tag`) keeps a prediction for a few reactions apart from the prediction for all reactions |
| `sensitivityTuning` | `sensitivity_tuning` | the option `evidence` adds the `summary` table of `kcatEvidence` for the tuned reactions to the output (`tunedKcats.evidence`, Python `TunedKcatsResult.evidence`) |

## Setup

The printed output of the MATLAB examples comes from the ecModel of the `full_ecModel` tutorial of GECKO (yeast-GEM); the Python functions return the same columns as data frames. The examples need an ecModel with assigned kcats and source files in `data/kcats` (see [Choose the kcat sources](kcat-sources.md)), in the variable `ecModel` (MATLAB) or `ec_model` (Python). The sources are read as they are: a source file that is outdated is not gathered again. The OKP predictions need an API key (see [Choose the kcat sources](kcat-sources.md#prepare-the-inputs)) and use the daily prediction quota of the key.

## Select the reactions

A reaction is selected by one of three arguments, and a reaction that any of them selects is included. Without a selection, all reactions of `ec.rxns` are included. An argument that is given and empty, for example the enzymes of a relaxation that changed none, selects no reaction.

| MATLAB | Python | Selects |
| --- | --- | --- |
| `rxns` | `rxns` | names of `ec.rxns`, conventional reaction names (a reverse direction ends with `_REV`), indices, or a logical vector over `ec.rxns` |
| `enzymes` | `enzymes` | every reaction that one of the UniProt accessions catalyses |
| `tunedKcats` | `tuned` | the reactions that `sensitivityTuning` tuned (the output `tunedKcats`, Python `TunedKcatsResult`) |

A conventional reaction name selects every `ec.rxns` row of the reaction, that is, all isozymes of the reaction in that direction. In a light ecModel, `tunedKcats` names the reactions by their conventional name, so it selects all rows of a tuned reaction.

## Show the kcats after a tuning

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, tunedKcats] = sensitivityTuning(ecModel);
[evidence, summary] = kcatEvidence(ecModel, 'tunedKcats', tunedKcats);
% the same, returned with the tuning:
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
result.summary
# the same, returned with the tuning:
tuned = sensitivity_tuning(ec_model, evidence=True)
tuned.evidence
```
:::
::::

The tutorial ecModel of yeast tuned 26 kcats. The first rows of `summary` (MATLAB output, the columns `enzymes` and `eccodes` left out):

```text
           ecRxn             kcat         origin       tuned     prior      fold    src_brenda    src_custom    src_ec_tree    src_okp_kinform_h
    ____________________    _______    ____________    _____    ________    ____    __________    __________    ___________    _________________

    {'r_0005_EXP_3'    }     33.451    {'ec_tree' }    true       3.3451     10       1.3782          NaN          3.3451            2.6606
    {'r_0109'          }     55.125    {'ec_tree' }    true      0.55125    100        0.294          NaN         0.55125            2.6506
    {'r_0157'          }     5.4102    {'ec_tree' }    true      0.54102     10         8.95          NaN         0.54102            2.9454
    {'r_0209'          }     3.9054    {'ec_tree' }    true      0.39054     10          3.8          NaN         0.39054            3.3459
    {'r_0220'          }      2.657    {'ec_tree' }    true       0.2657     10          6.3          NaN          0.2657            18.417
    {'r_0279'          }    0.86522    {'ec_tree' }    true     0.086522     10         0.87          NaN        0.086522            3.0441
```

`summary` has one row per reaction:

| Column (Python) | Content |
| --- | --- |
| `ecRxn` (`ec_rxn`) | the row of `ec.rxns` |
| `enzymes`, `eccodes` | the enzymes and the EC numbers of the row, joined by `;` |
| `kcat`, `origin` | the kcat of the ecModel and its origin in `ec.source` |
| `tuned`, `prior`, `fold` | whether the kcat has a tuning status in `ec.source`, the kcat before the first tuning (`NaN` without one), and `kcat / prior` (`NaN` without a positive prior) |
| `src_<source>` | the median of the kcats that the source file `<source>` gives for the row; `NaN` when it gives none |

`evidence` has one row per kcat of a source, with the columns `ecRxn` (`ec_rxn`), `source`, `kcat`, `substrate`, `detail` and `assigned`. `assigned` is true when the kcat equals the kcat that was assigned to the reaction, that is, the kcat before tuning for a tuned reaction and the kcat of the ecModel for any other. The comparison allows a relative difference of $10^{-5}$, because `ec.source` stores the prior with six significant digits. Two sources with the same kcat are both marked. The column `detail` has the detail of the source file, for example the number of measurements and the EC level of an EC-tree value. The first rows of `evidence` of the tuning above:

```text
         ecRxn            source       kcat                        substrate                             detail          assigned
    ________________    __________    ______    _______________________________________________    __________________    ________

    {'r_0005_EXP_3'}    {'brenda'}    1.3782    {'UDP-D-glucose'                              }    {'wc=0; origin=5'}     false
    {'r_0109'      }    {'brenda'}     0.294    {'acetyl-CoA; ATP; bicarbonate'               }    {'wc=0; origin=2'}     false
    {'r_0157'      }    {'brenda'}      8.95    {'ATP; L-alanine; tRNA(Ala)'                  }    {'wc=0; origin=2'}     false
    {'r_0209'      }    {'brenda'}       3.8    {'ATP; L-arginine; tRNA(Arg)'                 }    {'wc=0; origin=2'}     false
```


The tuned kcat and the sources are on one scale, so `fold` and the `src_` columns show which source the tuned kcat moves toward. A tuned kcat that is within the range of one source supports that source. A tuned kcat above all sources is a prompt to check the measurement or the enzyme, and is not evidence for the value itself.

## Show the kcats of the enzymes that proteomics relaxation changed

`flexibilizeEnzConcs` and `relaxEnzConcs` (Python `flexibilize_enz_concs`, `relax_enz_concs`) return the enzymes whose measured concentration they relaxed. The reactions of those enzymes are the ones whose kcat may be too low, so they are selected by enzyme:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, flexEnz] = flexibilizeEnzConcs(ecModel);
[evidence, summary] = kcatEvidence(ecModel, 'enzymes', flexEnz.uniprotIDs);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcat_evidence

result = kcat_evidence(ec_model, enzymes=flexed_enzymes)
```
:::
::::

The first rows of `summary` for the 48 enzymes that `flexibilizeEnzConcs` relaxed in the tutorial (`tuned` is false, because these kcats were not tuned):

```text
         ecRxn               enzymes                eccodes            kcat       origin       tuned    prior    fold    src_brenda    src_custom    src_ec_tree    src_okp_kinform_h
    ________________    _________________    _____________________    ______    ___________    _____    _____    ____    __________    __________    ___________    _________________

    {'r_0001_EXP_2'}    {'P32891;P00044'}    {'1.1.2.4'          }    3.9075    {'ec_tree'}    false     NaN     NaN        4.185         NaN          3.9075             5.0797
    {'r_0001_EXP_4'}    {'P39976;P00044'}    {'1.1.2.4;1.1.99.40'}    3.9075    {'ec_tree'}    false     NaN     NaN        4.185         NaN          3.9075             5.0797
    {'r_0002_EXP_2'}    {'P46681;P00044'}    {'1.1.2.4;1.1.99.40'}    3.9075    {'ec_tree'}    false     NaN     NaN        4.185         NaN          3.9075             5.0797
    {'r_0004_EXP_2'}    {'P00044;P00175'}    {'1.1.2.3'          }    175.75    {'brenda' }    false     NaN     NaN       175.75         NaN          95.722             5.3818
    {'r_0091_EXP_2'}    {'P38858'       }    {'3.1.1.31'         }        10    {'custom' }    false     NaN     NaN         31.8          10          16.199             8.5428
```

In Python, `flexed_enzymes` is the list `flex_enz.uniprot_ids` of the `FlexEnzResult` that the relaxation function returned. `flexEnz.uniprotIDs` also lists `prot_pool` after `relaxEnzConcs` when the protein pool exchange was raised; remove it before the call, because `prot_pool` is a pseudo-enzyme that `ec.enzymes` does not list.

## Get the kcats for one reaction

`kcatsForReactions` selects reactions as `kcatEvidence` does, reads every source file, and computes the EC-tree estimate for the reactions from the BRENDA measurements, also when the project has an `ec_tree.tsv`: the computed estimate replaces the file in the table, so it is not outdated. The estimate depends on the EC number only, because BRENDA measurements have no direction. A reaction and its reverse direction (`_REV`) therefore get the same EC-tree value, and `detail` of the reverse direction ends with `direction=reverse`.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[evidence, summary] = kcatsForReactions(ecModel, 'MAR03905');
[evidence, summary] = kcatsForReactions(ecModel, {'MAR03905', 'MAR03905_REV'});
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import kcats_for_reactions

result = kcats_for_reactions(ec_model, ["MAR03905", "MAR03905_REV"])
```
:::
::::

The result for `r_0005_EXP_3`, a reaction that `sensitivityTuning` tuned (`summary`, then `evidence`; the project has the OKP predictions of KinForm-H for all reactions):

```text
         ecRxn               enzymes               eccodes            kcat       origin       tuned    prior     fold    src_brenda    src_custom    src_okp_kinform_h    src_ec_tree
    ________________    _________________    ____________________    ______    ___________    _____    ______    ____    __________    __________    _________________    ___________

    {'r_0005_EXP_3'}    {'Q04952;P06780'}    {'2.4.1.34;3.6.5.2'}    33.451    {'ec_tree'}    true     3.3451     10       1.3782         NaN             2.6606            3.3451
```

```text
         ecRxn               source           kcat         substrate              detail          assigned
    ________________    _________________    ______    _________________    __________________    ________

    {'r_0005_EXP_3'}    {'brenda'       }    1.3782    {'UDP-D-glucose'}    {'wc=0; origin=5'}     false
    {'r_0005_EXP_3'}    {'okp_kinform_h'}    1.1771    {'UDP-D-glucose'}    {'similarity=0'  }     false
    {'r_0005_EXP_3'}    {'okp_kinform_h'}    2.6426    {'UDP-D-glucose'}    {'similarity=0'  }     false
    {'r_0005_EXP_3'}    {'okp_kinform_h'}    2.6785    {'UDP-D-glucose'}    {'similarity=0'  }     false
    {'r_0005_EXP_3'}    {'okp_kinform_h'}    2.7391    {'UDP-D-glucose'}    {'similarity=0'  }     false
    {'r_0005_EXP_3'}    {'ec_tree'      }    3.3451    {0x0 char       }    {'n=1; depth=4'  }     true
```

The tuned kcat of 33.451 is 10 times the EC-tree estimate of 3.3451, the kcat before tuning, and is above the BRENDA kcat of 1.3782 and the four predictions of KinForm-H.

## Predict the kcats of a few reactions with OKP

The option `okp` submits the enzyme-substrate pairs of the selected reactions to OKP: `true` for the first method of `[kcat_sources.okp] methods`, a method name or a list of names, or `'all'` for every method that `kcatsFromOKP` accepts. `false` or an empty value submits nothing. CatPred and TurNup are not among the methods, because they read whole reactions. The function waits for each job to finish, and submits a new job on every call. A method that fails is reported and the other methods continue; the methods without predictions are listed at the end.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[evidence, summary] = kcatsForReactions(ecModel, 'MAR03905', 'okp', 'all');
[evidence, summary] = kcatsForReactions(ecModel, 'MAR03905', 'okp', {'KinForm-H', 'UniKP'});
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
result = kcats_for_reactions(ec_model, ["MAR03905"], okp="all")
result = kcats_for_reactions(ec_model, ["MAR03905"], okp=["KinForm-H", "UniKP"])
```
:::
::::

Each method submits one job and uses the daily prediction quota of the API key. The predictions of a method are written to `data/kcats/okp_<method>__query.tsv`, and the job, its input and its result to `data/OKP_job_<method>__query.txt`, `data/OKP_query_query.csv` and `data/OKP_output_<method>__query.csv`. These files are separate from the files `updateKcatSources` gathers for all reactions (`okp_<method>.tsv`, `data/OKP.csv`, `data/OKP_job_<method>.txt`, `data/OKP_output_<method>.csv`), which a query leaves as they are. A query file holds the predictions of the last query, and the next query of the method replaces it. The default sources of `kcatEvidence` and `kcatsForReactions` include the query files, so a default call shows the predictions of an earlier query for the same reactions. With `sources`, `kcatsForReactions` adds the query files of the methods that it asked for.

The option `jobTag` of `kcatsFromOKP` (Python `job_tag`) gives the same separation to a call of `kcatsFromOKP` with its own tag. `kcatsFromOKP(ecModel, 'method', 'UniKP', 'ecRxns', {'MAR03905'}, 'jobTag', 'mine')` writes `okp_unikp__mine.tsv` and `data/OKP_query_mine.csv`. The tag is written in lower case, with each run of other characters than letters and digits as `_`, and it must have at least one letter or digit. `ecRxns` (Python `ec_rxns`) takes names of `ec.rxns`, indices or a logical (Python: boolean) vector.

## Save the table

`saveAs` of `kcatEvidence` (Python `save_as`) writes `summary` to a tab-separated file, for example to hand the kcats of the tuned reactions to a curator.

## Troubleshooting

| Problem | Reason | Solution |
| --- | --- | --- |
| `Not reactions of model.ec` | a name in `rxns` or `tunedKcats` is neither a row of `ec.rxns` nor a conventional reaction | use the names of `ec.rxns` or the conventional name, including `_REV` for a reverse direction |
| `Not in model.ec.enzymes` | an accession in `enzymes` is not an enzyme of the ecModel | remove it; in MATLAB remove `prot_pool` from `flexEnz.uniprotIDs` |
| a `src_` column is `NaN` for a reaction | the source file has no row for the reaction and its enzymes | gather the file again with `updateKcatSources`, or accept that the source has no value |
| rows of a source file are reported as not matching any reaction | the file was made from another ecModel | the message of `loadKcatSource` lists them; gather the file again |
| `kcatsForReactions` has no OKP column | the job failed, for example without an API key, or the reaction has no SMILES | the failure is reported for each method; fix the cause and call again |
| `src_ec_tree` is `NaN` | no BRENDA measurement for the EC number, or the reaction has no EC number | fill the EC numbers (see [Choose the kcat sources](kcat-sources.md#prepare-the-inputs)) |

## See also

- [Choose the kcat sources](kcat-sources.md), the source files and how `updateKcatSources` gathers them.
- [Choose a kcat tuning](kcat-tuning.md), the check of a tuned kcat against its source.
- [Tune kcats with sensitivityTuning](standard-tuning.md), the tuning that returns `tunedKcats`.
- [Relax proteomics constraints](relaxing-proteomics.md), the methods that return the relaxed enzymes.
- [API reference](../api/index.md), every function in both toolboxes.
