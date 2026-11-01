# Migrate

Migration pages answer two questions: what changes when a workflow moves from GECKO 3 to GECKO 4, and what differs when a workflow moves between MATLAB and Python.

| Page | Content |
| --- | --- |
| [GECKO 3 to GECKO 4](gecko3-to-gecko4.md) | the changes that pass without an error, the changes that raise one, new, removed and renamed functions, and how to stay on GECKO 3 |
| [Project format 4](gecko4-project-format.md) | the project folder, `model_adapter.toml`, kcat source files and the ecModel format |
| [Upgrade a GECKO 3 project](gecko3-upgrade-project.md) | the steps of `upgradeGECKOproject` and `upgradeEcModel` |
| [Kcat assignment](gecko4-kcat-assignment.md) | kcat source files, stages and presets of `collectKcats` and `assignKcats` |
| [GECKO and geckopy](gecko-to-geckopy.md) | what each implementation has, and where they answer the same question differently |

```{toctree}
:hidden:

gecko3-to-gecko4
gecko4-project-format
gecko3-upgrade-project
gecko4-kcat-assignment
gecko-to-geckopy
```
