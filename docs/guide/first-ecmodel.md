# Build an ecModel

These steps build an enzyme-constrained model (ecModel) from a conventional genome-scale metabolic model (GEM) with the default settings of GECKO and geckopy. At the end, the project folder holds an ecModel with *k*{sub}`cat`s and a protein pool, which reaches the growth rate of the organism, saved as a YAML file. Each step links to the page that describes the other options of that step.

<!-- workflow-place -->
:::::{dropdown} Place in the workflow

The diagram orders the functions of this page within the [workflow](workflow.md). Boxes with a dashed outline are optional steps, a dotted arrow is an optional path, and a diamond is a choice. Rounded boxes with a dotted outline are the context, other pages or the model to start from, and a click on one opens its page.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```{mermaid}
:align: left

---
config:
  flowchart:
    useMaxWidth: false
---
flowchart TB
  classDef opt stroke-dasharray: 5 4
  classDef ctx fill:transparent,stroke-dasharray: 2 3
  PV(["Start: Installation"]):::ctx
  S1["<b>1. Create a project</b><br/>createGECKOproject<br/>fill model_adapter.toml"]
  S2["<b>2. Make the ecModel</b><br/>ModelAdapterManager.setDefault<br/>loadConventionalGEM<br/>makeEcModel"]
  S3["<b>3. Assign kcats</b><br/>getECfromGEM, then getECfromDatabase<br/>findMetSmiles<br/>updateKcatSources<br/>assignKcats"]
  S4["<b>4. Set the protein pool</b><br/>setProtPoolSize"]
  S5["<b>5. Check the growth rate</b><br/>solveLP"]
  S6["<b>6. Tune kcats and fit sigma</b><br/>sensitivityTuning (no change when growth reaches the target)<br/>sigmaFitter when growth is above the target"]
  S7["<b>7. Save the ecModel</b><br/>saveEcModel"]
  PV --> S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7
  EV(["Tune kcats with evotune<br/>in place of step 6, with measured fluxes<br/>or several growth rates"]):::ctx
  S5 -.-> EV -.-> S7
  ND(["A decision page of the guide, to change a default"]):::ctx
  NP(["Next: Constrain enzymes with proteomics (optional)"]):::ctx
  NA(["Next: Analyse an ecModel"]):::ctx
  S7 -.-> ND
  S7 --> NP
  S7 --> NA
  click PV href "../installation/index.html"
  click EV href "evotune.html"
  click ND href "index.html"
  click NP href "proteomics.html"
  click NA href "analysis.html"
```
:::
:::{tab-item} 🐍 Python
:sync: python

```{mermaid}
:align: left

---
config:
  flowchart:
    useMaxWidth: false
---
flowchart TB
  classDef opt stroke-dasharray: 5 4
  classDef ctx fill:transparent,stroke-dasharray: 2 3
  PV(["Start: Installation"]):::ctx
  S1["<b>1. Create a project</b><br/>geckopy init<br/>fill model_adapter.toml"]
  S2["<b>2. Make the ecModel</b><br/>ModelAdapter.from_folder<br/>load_conventional_gem<br/>make_ec_model"]
  S3["<b>3. Assign kcats</b><br/>load_uniprot_tsv, load_kegg_tsv<br/>fill_eccodes_from_gem, then fill_eccodes_from_database<br/>find_met_smiles<br/>update_kcat_sources<br/>assign_kcats"]
  S4["<b>4. Set the protein pool</b><br/>set_prot_pool_size"]
  S5["<b>5. Check the growth rate</b><br/>model.slim_optimize"]
  S6["<b>6. Tune kcats and fit sigma</b><br/>sensitivity_tuning (no change when growth reaches the target)<br/>fit_sigma when growth is above the target"]
  S7["<b>7. Save the ecModel</b><br/>save_ec_model"]
  PV --> S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7
  EV(["Tune kcats with evotune<br/>in place of step 6, with measured fluxes<br/>or several growth rates"]):::ctx
  S5 -.-> EV -.-> S7
  ND(["A decision page of the guide, to change a default"]):::ctx
  NP(["Next: Constrain enzymes with proteomics (optional)"]):::ctx
  NA(["Next: Analyse an ecModel"]):::ctx
  S7 -.-> ND
  S7 --> NP
  S7 --> NA
  click PV href "../installation/index.html"
  click EV href "evotune.html"
  click ND href "index.html"
  click NP href "proteomics.html"
  click NA href "analysis.html"
```
:::
::::
:::::

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `createGECKOproject` | `geckopy init` | create a project folder with a template `model_adapter.toml` |
| `ModelAdapterManager.setDefault` | `ModelAdapter.from_folder` | read `model_adapter.toml` of the project |
| `loadConventionalGEM` | `load_conventional_gem` | load the GEM that `conv_gem` names |
| `makeEcModel` | `make_ec_model` | add the enzymes and the protein pool to the GEM |
| `loadDatabases` (called by `makeEcModel` and `getECfromDatabase`) | `load_uniprot_tsv`, `load_kegg_tsv` | read the UniProt and KEGG data of the organism |
| `getECfromGEM`, `getECfromDatabase` | `fill_eccodes_from_gem`, `fill_eccodes_from_database` | fill the EC numbers of the reactions |
| `findMetSmiles` | `find_met_smiles` | find the SMILES of the metabolites in PubChem |
| `updateKcatSources` | `update_kcat_sources` | make the *k*{sub}`cat` source files that the preset needs |
| `assignKcats` | `assign_kcats` | select one *k*{sub}`cat` per reaction and apply it |
| `setProtPoolSize` | `set_prot_pool_size` | set the upper bound of the protein pool |
| `setParam` | `reaction.lower_bound`, `model.objective` | set a bound or the objective |
| `solveLP` | `model.slim_optimize` | solve the model |
| `sensitivityTuning` | `sensitivity_tuning` | raise the *k*{sub}`cat`s that limit growth (standard *k*{sub}`cat` tuning) |
| `sigmaFitter` | `fit_sigma` | fit the saturation factor $\sigma$ to the growth rate |
| `saveEcModel` | `save_ec_model` | save the ecModel as YAML in `models` |

## Setup

GECKO or geckopy must be installed (see [Installation](../installation/index.md)). The steps need an internet connection: the UniProt data of the organism, the BRENDA files and the SMILES of the metabolites are downloaded the first time they are used. The starting GEM is a curated model in SBML or YAML format.

## 1. Create a project

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
createGECKOproject('name', 'ecMyModel', 'path', pwd);
```

`createGECKOproject` creates the folder `ecMyModel` with the subfolders `code`, `data`, `models` and `output`, and the template `model_adapter.toml`. It then changes the current folder of MATLAB to `ecMyModel`.
:::
:::{tab-item} 🐍 Python
:sync: python

```bash
geckopy init ecMyModel
```

`geckopy init` creates the folder `ecMyModel` with the subfolders `data`, `models` and `output`, the template `model_adapter.toml`, and `adapter.py` for organism-specific code. The current folder does not change.
:::
::::

Copy the GEM into `models`, then set the parameters of the organism in `model_adapter.toml`. `conv_gem`, `org_name`, `gr_exp`, `c_source` and `bio_rxn` have no default value; the functions that tune *k*{sub}`cat`s or fit $\sigma$ need `gr_exp`. `[uniprot] id` has no default either, and an empty `[kegg] id` means that KEGG is not used; set both for the organism. The example holds the values for [yeast-GEM](https://github.com/SysBioChalmers/yeast-GEM), in which `r_1714` is the glucose exchange and `r_4041` the biomass reaction:

```toml
conv_gem = "models/yeast-GEM.yml"
org_name = "saccharomyces cerevisiae"

sigma = 0.5      # average enzyme saturation
p_tot = 0.5      # total protein content [g protein/gDCW]
f = 0.5          # fraction of the protein that the enzymes of the model account for
gr_exp = 0.41    # growth rate without limitation of the nutrient uptake [1/h]

c_source = "r_1714"
bio_rxn = "r_4041"
enzyme_comp = "cytoplasm"

[uniprot]
type = "proteome"
id = "UP000002311"
gene_id_field = "gene_oln"
reviewed = false

[kegg]
id = "sce"
gene_id = "kegg"
```

`[uniprot]` selects the UniProt data whose gene identifiers match those of the GEM, and `enzyme_comp` is the name of a compartment of the GEM. [Model adapter parameters](model-adapter-parameters.md) describes each parameter, and [Find the UniProt and KEGG parameters](ecmodel-structure.md#find-the-uniprot-and-kegg-parameters) describes how to find the values of an organism.

## 2. Make the ecModel

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
adapter = ModelAdapterManager.setDefault(pwd);
params = adapter.getParameters();
model = loadConventionalGEM();
[ecModel, noUniprot] = makeEcModel(model);
```

`pwd` is the project folder, which `createGECKOproject` made the current folder. `noUniprot` lists the genes that neither database matched.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ModelAdapter, load_conventional_gem, make_ec_model

adapter = ModelAdapter.from_folder("ecMyModel")
params = adapter.params
model = load_conventional_gem(adapter)
ec_model = make_ec_model(model, adapter)
```
:::
::::

`makeEcModel` downloads the UniProt and KEGG data of the organism into `data/uniprot.tsv` and `data/kegg.tsv` when these files do not exist, with the settings of `[uniprot]` and `[kegg]`. With an empty `kegg.id`, it prints a warning and uses no KEGG data. `uniprot.id` has no default; without it and without `data/uniprot.tsv`, the build raises an error.

The ecModel is a full ecModel: it has one pseudometabolite and one usage reaction per enzyme, and no *k*{sub}`cat`s yet. [Choose the ecModel structure](ecmodel-structure.md) describes the light ecModel, the matching of genes to UniProt and KEGG, and the data of enzyme complexes.

The model adapter holds the values that `model_adapter.toml` had when it was read (MATLAB: `ModelAdapterManager.setDefault`, Python: `ModelAdapter.from_folder`). After a change to the file, read it again with the same call.

## 3. Assign *k*{sub}`cat`s

The *k*{sub}`cat` sources of the default preset (`brenda_ec_tree`) read the EC numbers of the reactions and the SMILES of the substrates, so these are filled first.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = getECfromGEM(ecModel);
noEC = cellfun(@isempty, ecModel.ec.eccodes);
ecModel = getECfromDatabase(ecModel, 'ecRxns', noEC);
ecModel = findMetSmiles(ecModel);
updateKcatSources(ecModel);
[ecModel, decisions] = assignKcats(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import (
    assign_kcats, fill_eccodes_from_database, fill_eccodes_from_gem,
    find_met_smiles, load_uniprot_tsv, update_kcat_sources,
)
from geckopy.databases import load_kegg_tsv

uniprot_db = load_uniprot_tsv(params.path / "data" / "uniprot.tsv")
kegg_db = load_kegg_tsv(params.path / "data" / "kegg.tsv", kegg_id=params.kegg.id)
fill_eccodes_from_gem(ec_model)
no_ec = [rxn for rxn, ec in zip(ec_model.ec.rxns, ec_model.ec.eccodes) if not ec]
fill_eccodes_from_database(ec_model, uniprot_db, kegg_db=kegg_db, ec_rxns=no_ec)
find_met_smiles(ec_model)
print(update_kcat_sources(ec_model))
decisions, report = assign_kcats(ec_model)
```

`load_uniprot_tsv` and `load_kegg_tsv` read the files that `make_ec_model` downloaded; `load_kegg_tsv` returns `None` when `kegg.id` is empty and `data/kegg.tsv` does not exist. `assign_kcats` changes `ec_model` in place.
:::
::::

The EC numbers come from the annotation of the GEM, and from UniProt and KEGG for the reactions that the GEM does not annotate. `updateKcatSources` makes the *k*{sub}`cat` source files in `data/kcats` that the preset needs and prints a table with the status of each source. The BRENDA files are downloaded the first time they are used. `assignKcats` selects one *k*{sub}`cat` per reaction from the source files, applies the *k*{sub}`cat`s to the model, and writes the decision for each reaction to `output/<model id>_kcatDecisions.tsv`.

The default preset takes *k*{sub}`cat`s from BRENDA measurements of the organism and from the measurements of the same EC number in other organisms. For the reactions that these leave without a *k*{sub}`cat`, it takes the predictions of the OpenKineticsPredictor (OKP) method KinForm-H. OKP is a web service that needs an API key, set as the environment variable `OKP_API_KEY` or in the file `data/okpApiKey.txt` (a key is generated at [predictor.openkinetics.org](https://predictor.openkinetics.org/)). The first call of `updateKcatSources` submits the OKP job and reports the source `okp_kinform_h` as `pending`; a later call fetches the result. Call `updateKcatSources` again until no source is `pending`, then run `assignKcats`. A source file that does not exist is skipped by `assignKcats`, and a reaction without a *k*{sub}`cat` from any source gets a *k*{sub}`cat` from an isozyme or the standard *k*{sub}`cat` (`getStandardKcat`, Python: `assign_standard_kcat`).

[Choose the *k*{sub}`cat` sources](kcat-sources.md) describes the presets and the treatment of reactions without a *k*{sub}`cat`, and [Set custom *k*{sub}`cat`s](custom-kcats.md) describes curated *k*{sub}`cat`s.

## 4. Set the protein pool

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setProtPoolSize(ecModel);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import set_prot_pool_size

set_prot_pool_size(ec_model)
```
:::
::::

`setProtPoolSize` sets the upper bound of `prot_pool_exchange` to $P_{tot} \cdot f \cdot \sigma \cdot 1000$ mg/gDCW, with the values of `p_tot`, `f` and `sigma` in `model_adapter.toml`. [Set the protein pool](protein-pool.md) describes how to choose the three values.

## 5. Check the growth rate

The growth rate of the ecModel is compared with `gr_exp`, the growth rate of the organism without a limitation of the nutrient uptake. The uptake of the carbon source is therefore opened (the uptake is a negative flux of the exchange reaction), and the biomass reaction is the objective.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ecModel = setParam(ecModel, 'lb', params.c_source, -1000);
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
sol = solveLP(ecModel);
growth = sol.x(strcmp(ecModel.rxns, params.bioRxn))
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
ec_model.reactions.get_by_id(params.c_source).lower_bound = -1000
ec_model.objective = params.bio_rxn
growth = ec_model.slim_optimize()
print(growth)
```
:::
::::

[Basic model operations](basic-model-operations.md) describes bounds, objectives and the inspection of a solution.

## 6. Tune *k*{sub}`cat`s and fit sigma

This step uses `sensitivityTuning`, which needs one growth rate, `gr_exp`. With measured growth rates of several conditions or measured exchange fluxes, use evotune in place of this step ([Tune *k*{sub}`cat`s with evotune](evotune.md)), without `sigmaFitter`. When the growth rate is lower than `gr_exp`, `sensitivityTuning` raises the *k*{sub}`cat`s that limit growth; when the model already reaches `gr_exp`, it changes no *k*{sub}`cat`. Each step multiplies a *k*{sub}`cat` by 10, so the growth rate after tuning is often above `gr_exp`. A *k*{sub}`cat` tuning only raises *k*{sub}`cat`s, so when the growth rate is above `gr_exp`, `sigmaFitter` lowers the saturation factor $\sigma$ until the growth rate matches `gr_exp`, and sets the protein pool with that value.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
[ecModel, tunedKcats] = sensitivityTuning(ecModel);
ecModel = setParam(ecModel, 'obj', params.bioRxn, 1);
sol = solveLP(ecModel);
if sol.x(strcmp(ecModel.rxns, params.bioRxn)) > params.gR_exp
    [ecModel, sigma] = sigmaFitter(ecModel, 'makePlot', false);
end
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import fit_sigma, sensitivity_tuning

tuned_kcats = sensitivity_tuning(ec_model)
ec_model.objective = params.bio_rxn
if ec_model.slim_optimize() > params.gr_exp:
    sigma = fit_sigma(ec_model).sigma
```

`sensitivity_tuning` and `fit_sigma` change `ec_model` in place.
:::
::::

`sensitivityTuning` selects the enzyme with the highest usage, multiplies the *k*{sub}`cat` of the reaction that uses the most of this enzyme by 10, and repeats this until the model reaches `gr_exp`. `tunedKcats` lists each changed reaction with its *k*{sub}`cat` before and after tuning, and `ec.source` of the reaction keeps the origin of the *k*{sub}`cat`, with the *k*{sub}`cat` before tuning as `prior`. [Choose a *k*{sub}`cat` tuning](kcat-tuning.md) compares the two tunings and describes how to check a tuned *k*{sub}`cat`, [Tune *k*{sub}`cat`s with sensitivityTuning](standard-tuning.md) describes the options of this step, and [Set the protein pool](protein-pool.md#sigma-and-kcat-tuning) describes when to change $\sigma$ and when the *k*{sub}`cat`s.

## 7. Save the ecModel

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
saveEcModel(ecModel, 'ecMyModel.yml');
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import save_ec_model

save_ec_model(ec_model, "ecMyModel.yml")
```
:::
::::

The file is written to the `models` folder of the project. [ecModel YAML format](yaml-format.md) describes the format, which GECKO and geckopy both read. An ecModel can also be exported as SBML (MATLAB: `saveEcModel` with a file name that ends in `.xml`, Python: `cobra.io.write_sbml_model`), for use in other constraint-based tools; the SBML file does not keep the `ec` fields, so GECKO and geckopy cannot continue from it.

## Next

- [Choose the ecModel structure](ecmodel-structure.md): build a light ecModel, match the genes of the GEM to UniProt and KEGG, and add the subunit composition of enzyme complexes.
- [Choose the *k*{sub}`cat` sources](kcat-sources.md): select another preset and compare presets before they are applied.
- [Set custom *k*{sub}`cat`s](custom-kcats.md): give reactions curated *k*{sub}`cat`s from the literature or from measurements.
- [Set the protein pool](protein-pool.md): calculate $f$ from proteomics data and set the protein pool of a condition.
- [Choose a *k*{sub}`cat` tuning](kcat-tuning.md): choose between `sensitivityTuning` and evotune, and check the tuned *k*{sub}`cat`s.
- [Tune *k*{sub}`cat`s with sensitivityTuning](standard-tuning.md): the options of the tuning of step 6.
- [Tune *k*{sub}`cat`s with evotune](evotune.md): fit *k*{sub}`cat`s to growth rates and exchange fluxes of one or more conditions.
- [Constrain enzymes with proteomics](proteomics.md): limit each measured enzyme to its measured concentration.
- [Relax proteomics constraints](relaxing-proteomics.md): loosen the proteomics constraints that prevent the measured growth rate.
- [Analyse an ecModel](analysis.md): simulate with other objectives, calculate flux ranges and sample solutions.
- [Enzyme usage and bottlenecks](enzyme-usage.md): report which enzymes a solution uses and which limit the objective.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| `makeEcModel` stops with an error that names `params.enzyme_comp` | `enzyme_comp` names no compartment of the GEM | Set `enzyme_comp` to a compartment name of the GEM, for example `cytoplasm` |
| `noUniprot` lists most genes of the GEM | the gene identifiers of the UniProt data do not match those of the GEM | Set `[uniprot]` as described in [Choose the ecModel structure](ecmodel-structure.md), delete `data/uniprot.tsv` and make the ecModel again |
| `updateKcatSources` reports the source `okp_kinform_h` as `failed`, with "No OpenKineticsPredictor API key found" | no OKP API key is set | Set `OKP_API_KEY` or write the key in `data/okpApiKey.txt`, then call `updateKcatSources` again |
| `updateKcatSources` reports a source as `pending` | the OKP job is still running | Call `updateKcatSources` again later |
| The growth rate does not change when the lower bound of `c_source` is changed | `makeEcModel` reverses a reaction with a negative lower bound and an upper bound of 0, so uptake through that exchange reaction is a positive flux in the ecModel | Set the upper bound of the exchange reaction |
| `sensitivityTuning` warns that the growth rate does not increase | the bound of an uptake reaction limits growth | Check the bounds of the uptake reactions |

## See also

- [Introduction to ecModels](introduction.md): the enzyme constraint and the protein pool.
- [Files in the data folder](data-folder-files.md): the files that the steps write in `data`.
- [*K*{sub}`cat` assignment](../gecko4-kcat-assignment.md): the sources, stages and presets of `assignKcats`.
- [API reference](../api/index.md): the signatures of the functions in both toolboxes.
