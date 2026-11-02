# Getting started

The reconstruction of an ecModel starts from a curated conventional genome-scale metabolic model (GEM) and a model adapter, the file that collects the organism-specific data and parameters that every later step reads. The steps below create a project folder with the starting GEM and a filled model adapter, and set the UniProt and KEGG parameters of the organism.

:::{admonition} Based on the Nature Protocols pipeline
:class: note
This guide follows the structure of the published GECKO 3.0 Nature Protocols pipeline (Chen et al., 2024; see [Citations](../references.md)) and describes GECKO 4. The differences from GECKO 3 are in [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md).
:::

<!-- workflow-place -->
:::::{dropdown} Place in the workflow

The diagram orders the functions of this page within the [workflow](workflow.md). Dashed boxes are optional and dotted boxes are neighbouring pages.

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
  A1["createGECKOproject<br/>Fill model_adapter.toml"] --> A2["loadDatabases('kegg')"]:::opt
  NX(["Next: Building an empty ecModel"]):::ctx
  A2 --> NX
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
  A1["geckopy init<br/>Fill model_adapter.toml"] --> A2["geckopy kegg-download"]:::opt
  NX(["Next: Building an empty ecModel"]):::ctx
  A2 --> NX
```
:::
::::
:::::

## Functions

| MATLAB | Python | |
|---|---|---|
| `createGECKOproject` | `geckopy init` | scaffold a new project folder with a template `model_adapter.toml` |
| `ModelAdapterManager.setDefault` | `ModelAdapter.from_folder` | load the model adapter of a project |
| `loadDatabases('kegg')` | `geckopy kegg-download` | download KEGG data for identifier conversion |

## Setup

GECKO (MATLAB) or geckopy (Python) must be installed (see [Installation](../installation/index.md)). The starting GEM is a curated model in a format that the toolbox reads. The example parameters are those of the `full_ecModel` tutorial, which uses [yeast-GEM](https://github.com/SysBioChalmers/yeast-GEM); the data files of that tutorial are described in [Files in the data folder](data-folder-files.md).

## Start a new project

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
createGECKOproject();
```

Two dialogs ask for the name of the project and for the location where `createGECKOproject` creates its folder. The options `name` and `path` replace the dialogs, as in `createGECKOproject('name', 'myproject', 'path', pwd)`. A folder that already exists at the location is not overwritten; the function prints a warning instead.

`createGECKOproject` creates four subfolders: `code` and `data` hold custom code and data that the reconstruction and the analysis use, and `models` and `output` hold the reconstructed ecModels and the results of simulations. It writes the template `model_adapter.toml` in the project folder, with the project name in its first line, placeholders for the GEM and the organism, and the defaults of the other parameters. The option `'adapterFormat','class'` writes an adapter class `<name>Adapter.m` instead (see [Project format 4](../gecko4-project-format.md)).
:::
:::{tab-item} 🐍 Python
:sync: python

```bash
geckopy init myproject
```

`init` is a subcommand of the `geckopy` command-line tool that is installed with the package (see [Installation](../installation/index.md)). The command stops with an error when the folder exists and is not empty.

`geckopy init` creates the subfolders `data`, `models` and `output`, which hold data for the reconstruction, the reconstructed ecModels and the results of simulations. It writes `adapter.py`, the counterpart of the `code` folder, in the project root, and the template `model_adapter.toml`. In the template, `conv_gem` and `org_name` are set to placeholders, and every other parameter is a comment line with its default value.
:::
::::

The template of both toolboxes has a section `[evotune]` with the hyperparameters of the CMA-ES kcat tuning (see [Tuning against experimental data](tuning-against-experimental-data.md)) and a section `[kcat_assignment]` for the kcat assignment (see [Kcat assignment](../gecko4-kcat-assignment.md)). The template of `geckopy init` lists the parameters of these sections as comments. The template of `createGECKOproject` sets `preset = "brenda_ec_tree"` and the other values of both sections.

The starting GEM is stored under `models`. Other locations work, and `models` keeps the project self-contained. The folder that contains the model adapter is called the adapter folder.

The files in `data` have the same formats (TSV, JSON) in both languages, so a `data` folder that one toolbox filled is usable in the other. [Files in the data folder](data-folder-files.md) lists every file that belongs there and where it is created.

## The model adapter

The model adapter is the file `model_adapter.toml`, which GECKO and geckopy read. Paths in it are relative to the project folder. A parameter that the file leaves out gets the default that is listed in `src/model_adapter/adapterParameters.tsv` of GECKO, and a key that is not in the list is an error in both toolboxes. [Model adapter parameters](model-adapter-parameters.md) describes every parameter. The values here are those of the `full_ecModel` tutorial, without the sections for kcat assignment and kcat tuning:

```toml
conv_gem = "models/yeast-GEM.yml"
org_name = "saccharomyces cerevisiae"

sigma = 0.5
p_tot = 0.5
f = 0.5
gr_exp = 0.41

c_source = "r_1714"
bio_rxn = "r_4041"
enzyme_comp = "cytoplasm"

[kegg]
id = "sce"
gene_id = "kegg"

[uniprot]
type = "proteome"
id = "UP000002311"
gene_id_field = "gene_oln"
reviewed = true

[complex]
taxonomic_id = 559292
```

The adapter is loaded from the project folder:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
adapter = ModelAdapterManager.setDefault(projectPath);
params = adapter.getParameters();
```

`ModelAdapterManager.setDefault` takes the project folder or the path of `model_adapter.toml`, and returns a `TomlAdapter`. The parameters are fields of `params` with the MATLAB names from `adapterParameters.tsv`, for example `params.Ptot` for `p_tot` and `params.uniprot.ID` for `uniprot.id`. Organism-specific behaviour that a value cannot express, for example a non-standard way to identify spontaneous reactions, is set in the sections `[spontaneous]` and `[matlab]` of the file, or in a subclass of `TomlAdapter`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ModelAdapter

adapter = ModelAdapter.from_folder("myproject")
params = adapter.params
```

`ModelAdapter.from_folder` reads `model_adapter.toml` from the folder. `adapter.py` of the project is not loaded by `from_folder`. A subclass of `ModelAdapter` in that file, for organism-specific behaviour that a value cannot express, is imported and instantiated explicitly, as in `MyAdapter.from_folder("myproject")`. Most projects edit the TOML file and leave `adapter.py` unchanged.
:::
::::

A GECKO 3 adapter class keeps working in MATLAB, and `convertAdapterToToml` writes it as `model_adapter.toml` (see [Upgrade a GECKO 3 project](../gecko3-upgrade-project.md)).

A parameter that cannot be defined, because the information is absent or not relevant, is set to an empty string when it has a non-empty default. The default of `kegg.id` is `sce`, so a model of an organism that is not in KEGG has

```toml
[kegg]
id = ""
```

### Querying UniProt and KEGG

The UniProt database is the source of the molecular weights and the amino acid sequences of the enzymes and is essential. KEGG can assign EC number annotations and is optional. The query parameters select data with the same style of gene identifier as the starting GEM. A mismatch means that enzyme data cannot be matched to the genes of the model.

:::{admonition} UniProt proteome and taxonomy identifiers
:class: warning

UniProt data are identified by proteome or by taxonomy. The proteome is preferred, because it avoids redundant matches between gene and protein identifiers.
:::

To find a UniProt proteome dataset, search [uniprot.org/proteomes](https://www.uniprot.org/proteomes) for the organism. If several proteome datasets exist for the organism, a [reference proteome](https://www.uniprot.org/proteomes?facets=proteome_type%3A1&query=%2A) is preferred. The UniProt page of one protein of the proteome shows under "Names & Taxonomy - Gene names" whether its gene identifiers have the same style as the starting GEM.

*Saccharomyces cerevisiae* has 93 UniProt proteomes, and one of them is the reference proteome for strain S288c (`UP000002311`). A protein in that proteome has the gene identifier `YFL026W`, which matches the style of yeast-GEM. UniProt labels this style "Ordered locus name", and the API field is `gene_oln`. The model adapter accordingly sets `uniprot.type` to `proteome`, `uniprot.id` to `UP000002311` and `uniprot.gene_id_field` to `gene_oln`.

The taxonomy is the alternative when no proteome fits. The identifier from the [taxonomy browser](https://www.uniprot.org/taxonomy/) should be as specific as possible. For *S. cerevisiae*, the taxonomy identifier 4932 covers 322 strains and 53,526 proteins in total, and 559292 refers to strain S288c alone, with 6,735 proteins. In that case `uniprot.type` is `taxonomy` and `uniprot.id` is `559292`.

For KEGG, `kegg.id` is the three- or four-letter species identifier from the [KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html); for *Homo sapiens* it is `hsa`. The genome entry page (for example [genome.jp/entry/hsa](https://www.genome.jp/entry/hsa)) links to the list of KEGG genes and shows which gene identifier KEGG links to its genes. The KEGG genes of *H. sapiens* are numbered sequentially, which does not match the identifiers of human-GEM. The section "Other DBs" of the same page lists Ensembl gene identifiers (for example `ENSG00000236362`), so `kegg.gene_id` for human-GEM is `Ensembl`.

## Handling unusual identifier formats

If an organism is in UniProt and no `uniprot.gene_id_field` matches the gene identifiers of the model, a conversion table at `data/uniprotConversion.tsv` has columns of model genes and UniProt identifiers.

The *Escherichia coli* model iML1515 has gene identifiers of the style `b0008`. UniProt does not have this style as a field, and KEGG links both identifiers. `uniprotConversion.tsv` is built from KEGG data (this needs a loaded model adapter; see [Building an empty ecModel](building-ec-model.md#set-the-default-model-adapter)):

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
DB = loadDatabases('kegg');
fID = fopen(fullfile(params.path, 'data', 'uniprotConversion.tsv'), 'w');
output = transpose([DB.kegg.keggGene, DB.kegg.uniprot]);
fprintf(fID, '%s\t%s\n', 'genes', 'uniprot');
fprintf(fID, '%s\t%s\n', output{:});
fclose(fID);
```

`loadDatabases('kegg')` takes the KEGG species from `kegg.id` of the adapter, so the adapter of iML1515 sets `kegg.id = "eco"` for this tab.
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy downloads KEGG data with the `geckopy` command-line tool, which has no Python function. The command writes a comma-delimited file without a header row, with the columns `uniprot`, `gene`, `kegg_gene` and further columns for EC numbers, molecular weights, pathways and sequences:

```bash
geckopy kegg-download eco data/kegg.tsv
```

`make_ec_model` loads the file as `data/kegg.tsv`, so the command saves it under that name although the delimiter is a comma. The two relevant columns are written as `uniprotConversion.tsv`. The file has no header row, so `pandas.read_csv` receives the column names:

```python
import pandas as pd

columns = ["uniprot", "gene", "kegg_gene", "ec", "mw", "pathway", "sequence"]
kegg = pd.read_csv(params.path / "data" / "kegg.tsv", header=None, names=columns)
kegg[["kegg_gene", "uniprot"]].rename(columns={"kegg_gene": "genes"}).to_csv(
    params.path / "data" / "uniprotConversion.tsv", sep="\t", index=False,
)
```
:::
::::

Other organisms can need another source for the conversion table. For human-GEM, a conversion table is part of the starting GEM, and the `light_ecModel` tutorial (`protocol.m` and `protocol.py`) converts it to `uniprotConversion.tsv`.

If an organism is in neither UniProt nor KEGG, the database files are built manually. `data/kegg.tsv` and `data/uniprot.tsv` of the `full_ecModel` tutorial are templates for the column layout. Artificial UniProt and KEGG identifiers work in these files, and the molecular weight and the sequence of each protein must be accurate for the rest of the reconstruction.

:::{admonition} Example output
:class: note

A new project has empty `data`, `models` and `output` subfolders (MATLAB also creates `code`) and a template `model_adapter.toml`. After the model adapter is filled in, MATLAB `loadDatabases` creates `data/uniprot.tsv` and `data/kegg.tsv` with queries of UniProt and KEGG. In Python, `geckopy uniprot-download` and `geckopy kegg-download` create the two files. When no UniProt or KEGG parameters are identified for the organism, `data/uniprotConversion.tsv`, `data/kegg.tsv` and `data/uniprot.tsv` are built by hand, as described above.
:::

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| Error that names a key of `model_adapter.toml` | the key is not in `adapterParameters.tsv`, or it is misspelled | Correct the key. A parameter that GECKO uses and geckopy does not use goes in `[matlab.params]` |
| UniProt or KEGG data of another organism | `uniprot.id` or `kegg.id` is not set, and the default (`559292`, `sce`) applies | Set the identifiers of the organism, or set `kegg.id = ""` |
| `geckopy init` stops with an error | the folder exists and is not empty | Use another folder name |
| Enzymes do not match the genes of the model | the gene identifier style of UniProt or KEGG differs from the starting GEM | Choose another `uniprot.gene_id_field` or `kegg.gene_id`, or build `data/uniprotConversion.tsv` |

## See also

- [Files in the data folder](data-folder-files.md), every file that a `data` folder can hold, and where it is used.
- [Model adapter parameters](model-adapter-parameters.md), every model adapter parameter in both languages.
- [Project format 4](../gecko4-project-format.md), the project folder and `model_adapter.toml`.
- [Building an empty ecModel](building-ec-model.md), the next step: loading the conventional GEM and expanding it into an ecModel.
- [API reference](../api/index.md), every function in both toolboxes.
- [MATLAB vs Python](../matlab-vs-python.md), what each toolbox has.
