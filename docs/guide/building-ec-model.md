# Building an empty ecModel

Building an ecModel expands a conventional GEM so that enzyme constraints can be added to it later. Reversible reactions split into forward and backward copies, because enzyme kinetics depend on direction. Reactions catalysed by isozymes split into one reaction per isozyme, because each has its own kinetics and molecular weight. The protein pool, together with the enzyme pseudo-metabolites that draw from it, is added to the network. The result is an **empty ecModel**: the structure that carries the enzyme constraints exists, and no constraints are applied yet. The empty ecModel is saved as a YAML file at the end.

## Functions

| MATLAB | Python | Note |
|---|---|---|
| `ModelAdapterManager.setDefault` | `ModelAdapter.from_folder` | load the model adapter of the project; MATLAB keeps it as the default of the session |
| `loadConventionalGEM` | `load_conventional_gem` | load the starting GEM from the path in the adapter |
| `makeEcModel` | `make_ec_model` | build the empty ecModel, full or light |
| `getComplexData` / `applyComplexData` | `get_complex_data` / `apply_complex_data` | add enzyme complex subunit stoichiometry |
| `saveEcModel` / `loadEcModel` | `save_ec_model` / `load_ec_model` | round-trip the ecModel through YAML |

## Setup

The project folder with `model_adapter.toml` and the starting GEM exist (see [Getting started](getting-started.md)). `createGECKOproject` (MATLAB) and `geckopy init` (Python) create the folder. The adapter sets the path of the GEM (`conv_gem`), the compartment of the protein pseudo-metabolites (`enzyme_comp`, a compartment name), the UniProt and KEGG parameters and, for the complex data, `complex.taxonomic_id`. [Model adapter parameters](model-adapter-parameters.md) describes them. The examples use the `full_ecModel` tutorial of GECKO, and its data files are described in [Files in the data folder](data-folder-files.md).

`makeEcModel` reads `data/uniprot.tsv` and `data/kegg.tsv` of the project and downloads a missing file when the identifier is not empty (`uniprot.id` and `kegg.id`, defaults 559292 and `sce`). An empty `uniprot.id` prints a warning, and the download is still attempted. An empty `kegg.id` prints a warning and skips the KEGG download. `make_ec_model` reads `data/uniprot.tsv` and raises a `FileNotFoundError` when it is missing, and it loads `data/kegg.tsv` when that file exists.

In Python, `geckopy uniprot-download` takes the UniProt identifier and the output path, for example `geckopy uniprot-download 559292 data/uniprot.tsv`. The option `--id-type` sets the field of the UniProt query (default `taxonomy_id`; `proteome` for a proteome identifier such as `UP000002311`), and `--gene-id-field` sets the gene identifier field (default `gene_oln`). `geckopy kegg-download eco data/kegg.tsv` creates `data/kegg.tsv`, a comma-delimited file that `make_ec_model` loads under that name.

## Set the default model adapter

Most GECKO functions need the model adapter.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

Set a default with `ModelAdapterManager` to avoid passing the adapter to every call. `ModelAdapterManager.setDefault` takes the project folder, its `model_adapter.toml` or the file of an adapter class. The default then applies to every GECKO function for the rest of that MATLAB session, unless another adapter is given explicitly:

```matlab
adapterLocation = fullfile(findGECKOroot, 'tutorials', 'full_ecModel');
ModelAdapterManager.setDefault(adapterLocation);
```

Retrieve the default explicitly when needed, for example when simulating several ecModels in the same session:

```matlab
ModelAdapter = ModelAdapterManager.getDefault();
params = ModelAdapter.getParameters();
```

The rest of this guide assumes a default model adapter is set.

The adapter is read when it is set. After a change in `model_adapter.toml`, set it as default again:

```matlab
ModelAdapterManager.setDefault(adapterLocation);
```
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy has no session-wide default adapter. An `EcModel` carries its adapter as `model.adapter`, which functions use when no adapter is passed. Load the adapter once and pass it, or its `.params` attribute, to each call:

```python
from pathlib import Path
from geckopy import ModelAdapter

adapter = ModelAdapter.from_folder(Path("GECKO/tutorials/full_ecModel"))
params = adapter.params
```

If the adapter file changes, reload it by calling `from_folder` again; there is no separate "set as default" step to repeat.
:::
::::

## Load the conventional GEM

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

If the location of the model is set in the adapter (the parameter `convGEM`, `conv_gem` in `model_adapter.toml`):

```matlab
model = loadConventionalGEM();
```

Both YAML and XML files are supported. To load a model at a different location, or without a model adapter, use the RAVEN function directly, for XML:

```matlab
model = importModel('path/to/modelFile.xml');
```

or YAML:

```matlab
model = readYAMLmodel('path/to/modelFile.yml');
```

GECKO loads models through RAVEN by default. A model loaded through the COBRA Toolbox (recognizable by a `model.rules` field) needs converting to the RAVEN format (recognizable by a `model.metComps` field) first, with `ravenCobraWrapper()`. `makeEcModel` stops with an error for a model that has the field `rules` or `modelID`.

Not every GEM in SBML format strictly follows the L3V1 FBCv2 standard; the [SBML Validator](https://sbml.bioquant.uni-heidelberg.de/validator_servlet/) reports what is wrong. In most cases the model still loads despite the warning. If it is later exported to SBML again, RAVEN avoids re-writing the same invalid content, so cycling through `importModel`, `exportModel` and `importModel` brings the loaded GEM closer to valid SBML.
:::
:::{tab-item} 🐍 Python
:sync: python

If the location of the model is set in the adapter (`params.conv_gem`):

```python
from geckopy import load_conventional_gem

model = load_conventional_gem(adapter)
```

This returns a `cobra.Model` with the solver tolerance of RAVEN (1e-9). The extension of the file selects the reader: `.yml` and `.yaml` through raven-toolbox, `.json` and `.mat` through cobrapy, and any other extension as SBML. Cobrapy is the native format throughout geckopy, so no conversion step is needed. To load a model at a different location or without an adapter, use cobrapy directly:

```python
import cobra

model = cobra.io.read_sbml_model("path/to/modelFile.xml")
```

or, for a YAML file in the RAVEN and GECKO schema, raven-toolbox's reader (installed automatically with geckopy):

```python
from raven_toolbox.io import read_yaml_model

model = read_yaml_model("path/to/modelFile.yml")
```
:::
::::

## Choose full or light, then build

A full ecModel expands isozymes into separate reactions and adds each enzyme as its own pseudo-metabolite, which allows each enzyme to be constrained individually, for example from proteomics data. A light ecModel does neither: it keeps the isozymes of a reaction as rows of `ec` and applies the lowest-cost isozyme to the shared protein pool, which makes it smaller and faster to simulate. The two layouts are not interconvertible, and the choice affects every later step. See [GECKO light and full ecModels](gecko-light.md) for the differences.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

Full ecModel:

```matlab
[ecModel, noUniprot] = makeEcModel(model);
```

Light ecModel:

```matlab
[ecModel, noUniprot] = makeEcModel(model, true);
```

The optional argument is `geckoLight`, also given as `makeEcModel(model, 'geckoLight', true)`.

`noUniprot` lists the model genes that match neither `data/uniprot.tsv` nor `data/kegg.tsv`. `makeEcModel` raises an error when no gene matches. If `noUniprot` contains many genes, for example more than ten, a different UniProt taxonomy or proteome identifier (see [The model adapter](getting-started.md#the-model-adapter)) may fit better.
:::
:::{tab-item} 🐍 Python
:sync: python

Full ecModel (`gecko_light` defaults to `False`):

```python
from geckopy import make_ec_model

ec_model = make_ec_model(model, adapter)
```

Light ecModel:

```python
ec_model = make_ec_model(model, adapter, gecko_light=True)
```

UniProt data loads automatically from `params.path / "data" / "uniprot.tsv"`. Pass a pre-loaded `uniprot_db=` to use a different file or to avoid re-reading it across multiple calls. KEGG data loads from `params.path / "data" / "kegg.tsv"` when that file exists; pass a pre-loaded `kegg_db=` to use another source. `make_ec_model` leaves the input `model` unchanged and returns the built `EcModel`.

`make_ec_model` returns the built `EcModel` and no list of unmatched genes. Unmatched genes are logged as a warning summary and recorded on the affected reactions in `reaction.notes["geckopy_warning"]`. As in MATLAB, many unmatched genes are a reason to reconsider the UniProt taxonomy or proteome identifier.
:::
::::

The build consults the KEGG data for genes that UniProt does not match. `ec.enzymes` receives the UniProt accession on the matching KEGG row, or the KEGG gene identifier when that row has no accession; the build warns that the bare KEGG gene identifier is used in `ec.enzymes` for these genes.

The result is an empty ecModel: the model structure allows enzyme constraints (see [the ec structure](applying-kcats.md#the-ec-structure)), and no constraints are applied yet.

## Apply enzyme complex stoichiometry (optional)

Building the ecModel assigns one copy of every subunit to each enzyme complex in `ec.rxnEnzMat` (Python: `ec.rxn_enz_mat`). In reality subunit copy numbers vary. GECKO adds this information from the [Complex Portal](https://www.ebi.ac.uk/complexportal/complex/organisms), using the taxonomic identifier in the model adapter parameter `complex.taxonomicID` (Python: `complex.taxonomic_id`); the Complex Portal covers a limited set of taxonomic identifiers.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
complexInfo = getComplexData();
[ecModel, foundComplex, proposedComplex] = ...
    applyComplexData(ecModel, complexInfo);
```

`getComplexData` takes the optional arguments `taxonomicID` and `modelAdapter`. Without them, the taxonomic identifier comes from the default model adapter, and the function writes `data/ComplexPortal.json` in the project folder. `applyComplexData` reads that file when called without `complexInfo`. `foundComplex` and `proposedComplex` are tables of the complexes with a full match and the proposed complexes.

MATLAB prints the number of full and proposed matches:

```
A total of 206 complex have full match, and 17 proposed.
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_complex_data

apply_complex_data(ec_model, path=params.path / "data" / "ComplexPortal.json")
```

`apply_complex_data` changes `ec_model` in place and returns `None`. Proposed complexes are logged as warnings, and the number of full and proposed matches is logged at INFO level as `apply_complex_data: N full match(es), M proposed.`. The keyword argument `min_match_to_propose` (default 0.75) sets the minimum fraction of matching genes for a partial match to be proposed. With `apply=True` (default) the function runs `apply_kcat_constraints` afterwards when at least one complex matched. To (re)download the Complex Portal data first, use `get_complex_data`, which takes the taxonomic identifier and returns the complexes. `write_to` stores them as `ComplexPortal.json`:

```python
from geckopy import get_complex_data

get_complex_data(
    params.complex.taxonomic_id,
    write_to=params.path / "data" / "ComplexPortal.json",
)
```
:::
::::

Complex data is integrated for a reaction when its ecModel gene association fully (100 %) matches a Complex Portal complex. `applyComplexData` changes `ec.rxnEnzMat`; the coefficients in the stoichiometric matrix follow from `applyKcatConstraints` (see [Applying kcat values](applying-kcats.md)). For a reaction with more than one enzyme and no full match, complexes with a partial match are proposed (MATLAB: in `proposedComplex`; Python: in the log). A complex is proposed when at least 75 % of the ecModel genes of the reaction match a Complex Portal complex that has no more subunits than the ecModel gene set, or when all genes match and the Complex Portal complex contains more subunits. Inspect the proposed complexes and consider whether curating the ecModel gene association is appropriate; this may need further literature study.

:::{note} Example output
In the `full_ecModel` tutorial, applying Complex Portal data finds 206 complexes with a full match and 17 proposed complexes. One proposed match: reaction `r_0505_EXP_2` could match complex CPX-1293, the mitochondrial 2-oxoglutarate dehydrogenase complex. In the ecModel this reaction is annotated with proteins P20967 (KGD1, subunit E1), P19262 (KGD2, subunit E2) and P09624 (LPD1, subunit E3), while CPX-1293 also includes P19955 (YMR31), the 37S ribosomal protein. Literature confirms that P19955, also called KGD4 or subunit E4, is an essential subunit for a stable complex, so the gene association of reaction `r_0505` in the starting GEM could be curated to include it, which would give a full match.
:::

:::{note} Complex data is missing for some or all complexes
The Complex Portal does not contain every complex; some are missing in most organisms. Uncertainty in kcat values is a larger source of error than uncertainty in complex stoichiometry, so skipping this step and keeping the default stoichiometry of one for every subunit is a reasonable option. `ComplexPortal.json` can be complemented manually with complex information from other databases or the literature.
:::

## Save the ecModel

The ecModel can be saved at any point in the procedure. YAML retains the full `ec` fields, so it is the format to use whenever the ecModel is modified further. The file structure is described in [ecModel YAML format](yaml-format.md).

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

`saveEcModel` writes to the `models` folder of the adapter folder and adds the keys `gecko_format` and `generator` to the file. The generic `writeYAMLmodel` writes anywhere and adds neither. `loadEcModel` or the generic `readYAMLmodel` read the model back. `loadEcModel` turns the protein reactions of an ecModel from GECKO 3 forward and stops for a file of a newer ecModel format:

```matlab
saveEcModel(ecModel, 'ecModel.yml');
writeYAMLmodel(ecModel, 'C:\path\to\ecModel.yml');
ecModel = loadEcModel('ecModel.yml');
ecModel = readYAMLmodel('C:\path\to\ecModel.yml');
```

For constraint-based analysis in other software, SBML (with an XML extension) is often more suitable. `saveEcModel` writes SBML too, when `filename` ends in `.xml`; `exportModel` and `importModel` do the same for an arbitrary path. Either way, the file does not retain the `ecModel.ec` fields, so an SBML-saved ecModel cannot be loaded back into MATLAB for further GECKO functions:

```matlab
saveEcModel(ecModel, 'ecModelFull.xml');
exportModel(ecModel, 'C:\path\to\ecModelFull.xml');
ecModel = importModel('C:\path\to\ecModelFull.xml');
```
:::
:::{tab-item} 🐍 Python
:sync: python

`save_ec_model` writes YAML, either in the `models` folder of the adapter folder or at an arbitrary path, and adds the keys `gecko_format` and `generator`; `load_ec_model` reads it back and turns the protein reactions of an ecModel from GECKO 3 forward:

```python
from geckopy import load_ec_model, save_ec_model

save_ec_model(ec_model, "ecModel.yml", adapter=adapter)
save_ec_model(ec_model, r"C:\path\to\ecModel.yml")
ec_model = load_ec_model("ecModel.yml", adapter=adapter)
ec_model = load_ec_model(r"C:\path\to\ecModel.yml")
```

When `ec_model.adapter` is set, `save_ec_model` uses it and the argument `adapter` can be omitted.

geckopy provides no separate SBML export for ecModels: YAML is the sole format that round-trips the `ec` fields, and `save_ec_model` raises a `ValueError` for another extension and for a model whose `ec` is empty. Because `ec_model` is a `cobra.Model`, plain cobrapy SBML I/O still works for interoperating with other tools, with the same limit as MATLAB's `exportModel`: it does not retain the `ec` fields.

```python
import cobra

cobra.io.write_sbml_model(ec_model, r"C:\path\to\ecModelFull.xml")
model = cobra.io.read_sbml_model(r"C:\path\to\ecModelFull.xml")
```
:::
::::

## Extension of a conventional GEM

Converting a conventional GEM into an empty ecModel runs up to twelve operations in order. Three are skipped for light ecModels: the split by isozyme, the enzyme pseudo-metabolites and the usage reactions. A light ecModel therefore stays close to the size of the conventional GEM.

:::{dropdown} All twelve steps, full and light
:open:

| # | Operation | Full | Light |
|---|---|:---:|:---:|
| 1 | Remove gene associations from pseudo-reactions (name contains `pseudoreaction`, or listed in `data/pseudoRxns.tsv`) | ✅ | ✅ |
| 2 | Invert irreversible reactions that run backwards (lower bound < 0, upper bound = 0) | ✅ | ✅ |
| 3 | Determine which reactions are reversible from their bounds; a reaction with a single metabolite (exchange type) is also marked reversible (MATLAB stores this as the ecModel field `rev`; geckopy has no separate reversibility vector) | ✅ | ✅ |
| 4 | Split reversible reactions into forward and reverse copies (`_REV` suffix on the reverse copy; exchange reactions keep their original, still-reversible form) | ✅ | ✅ |
| 5 | Split isozyme-catalysed reactions (`or` in the gene-reaction rule) into one reaction per isozyme (`_EXP_1`, `_EXP_2`, …) | ✅ | -- |
| 6 | Build an empty `ec` structure (Python: an `EcData` instance) | ✅ | ✅ |
| 7 | Add enzyme MW and sequence to `ec`, from UniProt via the model adapter, and from KEGG for genes that UniProt does not match | ✅ | ✅ |
| 8 | Record reaction-enzyme associations in `ec.rxnEnzMat` (Python: `ec.rxn_enz_mat`) | ✅ | ✅ |
| 9 | Add each enzyme as a `prot_<uniprot ID>` pseudo-metabolite | ✅ | -- |
| 10 | Add the protein pool pseudo-metabolite | ✅ | ✅ |
| 11 | Add `usage_prot_<uniprot ID>` reactions for each enzyme pseudo-metabolite, from `prot_pool` to the enzyme (bounds 0 and 1000) | ✅ | -- |
| 12 | Add the `prot_pool_exchange` reaction, which supplies `prot_pool` (bounds 0 and 1000) | ✅ | ✅ |

Step 5's new reaction identifiers: reaction `r_0001` catalysed by two isozymes becomes `r_0001_EXP_1` and `r_0001_EXP_2`; a backward reaction `r_0001_REV` becomes `r_0001_REV_EXP_1` and `r_0001_REV_EXP_2`. Light ecModels keep the original identifiers in the model, and the rows of `ec.rxns` carry the prefix `001_`, `002_` and so on, one per isozyme. Step 9's example: *S. cerevisiae* enolase gene YHR174W, UniProt identifier P00925, appears as pseudo-metabolite `prot_P00925`. Step 11's identifiers are `usage_` followed by the enzyme metabolite identifier, for example `usage_prot_P00925`. See [the ec structure](applying-kcats.md#the-ec-structure) for what step 6 populates later, and [GECKO light and full ecModels](gecko-light.md) for what the skipped steps change.
:::

:::{tip} Usage and pool exchange reactions run forward
`usage_prot_<id>` consumes `prot_pool` to produce `prot_<id>`, and `prot_pool_exchange` supplies `prot_pool`, both with bounds from 0 to 1000 at the build. An ecModel of GECKO 3 defines both reactions in the reverse direction with negative flux (see [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md)). The direction determines which bound relaxes a constraint and which objective coefficient minimises usage; the worked example is in [Growth-rate tuning](growth-rate-tuning.md#protein-pool-constraint).
:::

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| Error that the identifiers in `model.mets` or `model.rxns` are not allowed (Python: `ValueError`) | A metabolite identifier starts with `prot_`, or a reaction identifier starts with `usage_prot_` or `prot_pool` or ends with `_REV` or `_EXP_<digits>` | Rename the identifiers in the conventional GEM |
| Error that a compartment cannot be found in `model.compNames` | `enzyme_comp` differs from every compartment name of the model | Set `enzyme_comp` to a compartment name |
| Error that no protein in `uniprot.tsv` or `kegg.tsv` matches the genes | The UniProt or KEGG parameters do not fit the gene identifiers | Adjust `uniprot` and `kegg` in `model_adapter.toml` (see [Getting started](getting-started.md#the-model-adapter)) |
| `FileNotFoundError` for `uniprot.tsv` (Python) | The file is not in `data/` | Run `geckopy uniprot-download 559292 data/uniprot.tsv` with the identifier of the organism |
| `ValueError` that the model already has a populated `ec` (Python) | `make_ec_model` was called on an ecModel | Call it on the conventional GEM |
| Warning `No taxonomicID specified` from `getComplexData` | `complex.taxonomicID` is not set | Set it in `model_adapter.toml` or give `taxonomicID` |

## See also

- [Gathering kcats](gathering-kcats.md), the next step: sourcing kcat values from BRENDA, DLKcat or OpenKineticsPredictor.
- [GECKO light and full ecModels](gecko-light.md), the differences between the two ecModel structures.
- [ecModel YAML format](yaml-format.md), the structure of the saved file.
- [API reference](../api/index.md), every function in both toolboxes.
