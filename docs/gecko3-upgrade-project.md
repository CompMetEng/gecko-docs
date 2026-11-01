# Upgrade a GECKO 3 project

An existing GECKO 3 project is converted to [project format 4](gecko4-project-format.md) in one call that first lists its steps and then carries them out. The function is `upgradeGECKOproject` in MATLAB and `geckopy upgrade` (`upgrade_project`) in Python.

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `upgradeGECKOproject` | `geckopy upgrade`, `upgrade_project` | converts a project folder |
| `upgradeEcModel` | `upgrade_ec_model` | turns the protein reactions of one ecModel forward |
| `convertAdapterToToml` | | writes an adapter class as `model_adapter.toml`. `geckopy upgrade` lists the adapter class for conversion by hand |
| `convertCustomKcats` | `convert_custom_kcats` | writes `data/customKcats.tsv` as `data/kcats/custom.tsv` |

## Steps of the upgrade

`upgradeGECKOproject` carries out these steps for a project made with GECKO 3 or with an earlier GECKO 4:

1. Adapter: in MATLAB, an adapter class without `model_adapter.toml` gets one (`convertAdapterToToml`), and the methods that the class overrides are listed, because they need to be carried over by hand. The class stays. `geckopy upgrade` lists the adapter as a step to do by hand and skips steps 2 and 3 for such a project.
2. Custom kcats: `data/customKcats.tsv` becomes `data/kcats/custom.tsv` (`convertCustomKcats`). The kcats are those that `applyCustomKcats` gives the ecModel, including which of two entries for the same reaction applies. The column `stoicho` is not carried over, because the complex stoichiometry comes from `applyComplexData`.
3. Stored predictions: `data/DLKcat.tsv` and stored OpenKineticsPredictor results become kcat source files (`kcatsFromDLKcat`, and `kcatsFromOKP` with `'useStored'`). No prediction is run.
4. Saved ecModels: The ecModels in `models/*.yml` made with GECKO 3 get their protein usage and pool reactions turned forward (`upgradeEcModel`).
5. Project format: `project_format = 4` is written to `model_adapter.toml`.
6. Scripts: The lines of the `.m` files of the project that call renamed or replaced functions are listed and not changed.

Steps 2 and 3 need the full ecModel that the custom kcats and the predictions are for. Without it they are listed and skipped.

A file that is replaced or converted is first moved to `legacy/<yyyy-mm-dd>/`, at its place in the folder tree. A step that is done is left out, so the function can run again.

## Run the upgrade

The default of `upgradeGECKOproject` is a dry run. The report has one row per step, with the status `to do`, `done`, `skipped`, `failed` or `by hand`, and one row per script line.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
upgradeGECKOproject(projectPath)                                  % list the steps
upgradeGECKOproject(projectPath, 'dryRun', false, 'ecModel', ecModel)
```
:::
:::{tab-item} 🐍 Python
:sync: python

```bash
geckopy upgrade myproject                                    # list the steps
geckopy upgrade myproject --apply --ec-model models/ecModel.yml
```
:::
::::

`ecModel` (`--ec-model`) is the full ecModel for steps 2 and 3.

## Upgrade one ecModel

`upgradeEcModel` turns each protein usage reaction (`usage_prot_<id>`) and the pool exchange (`prot_pool_exchange`) that still runs in the GECKO 3 direction. The column of the S-matrix, the bounds and the objective coefficient of the reaction change sign. A reaction that is forward is left as it is, so a second call changes nothing. The `ecModel` format becomes 4. Flux values of the usage reactions and the pool exchange of an earlier solution have the opposite sign in the upgraded model.

`loadEcModel` calls `upgradeEcModel` on a GECKO 3 ecModel in the loaded model and prints a warning. `saveEcModel` stores the upgraded model.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| Steps 2 and 3 are `skipped` | no `ecModel` was given | Give the full ecModel the custom kcats and predictions are for |
| Step 1 lists methods | the adapter class overrides methods that the TOML file cannot hold | Move the code to a subclass of `TomlAdapter`, or to the `[matlab]` section |
| Script lines are listed | the script calls renamed functions | Change the lines by hand, with [Renamed functions](gecko3-to-gecko4.md#renamed-functions) |
| A kcat differs from the GECKO 3 model | the default kcat preset changed | Set `preset = "gecko_classic"` (see [Kcat assignment](gecko4-kcat-assignment.md)) |

## See also

- [GECKO 3 to GECKO 4](gecko3-to-gecko4.md)
- [Project format 4](gecko4-project-format.md)
