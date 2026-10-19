# Getting started

:::{admonition} Based on the Nature Protocols pipeline
:class: note
This Guide follows the structure of the published GECKO 3.0 Nature
Protocols pipeline (Chen et al., 2024; see [Citations](../references.md)),
adapted to reflect the current GECKO 4 codebase rather than reproducing the
paper's numbered steps exactly. Where GECKO 4 changed or added behavior,
the relevant page says so; see [GECKO 3 →
GECKO 4](../gecko3-to-gecko4.md) for the full list.
:::

An ecModel reconstruction starts from a curated conventional genome-scale
metabolic model (GEM) and a **model adapter**: a file that collates the
organism-specific data and parameters every later step reads. Creating a
project scaffolds both the folder layout and a template model adapter to
fill in.

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `createGECKOproject` | `geckopy init` | scaffold a new project folder |
| `ModelAdapter` (classdef) | `ModelAdapter.from_folder` | define and load the model adapter |
| `loadDatabases('kegg')` | `geckopy kegg-download` | download KEGG data for identifier conversion |

## Start a new project

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
createGECKOproject();
```

A dialog prompts for a location and creates the new folder there.
`createGECKOproject` creates four subfolders: `code` and `data` hold custom
code and data used during reconstruction and analysis; `models` and `output`
hold reconstructed ecModels and simulation results.
:::
:::{tab-item} 🐍 Python
:sync: python

```bash
geckopy init myproject
```

`init` is a subcommand of the `geckopy` command-line tool installed
alongside the package (see [Installation](../installation/index.md)). The
generated `model_adapter.toml` always includes the Bayesian kcat-tuning
hyperparameter section described in
[Tuning against experimental data](tuning-against-experimental-data.md),
commented out at its default values; no separate flag is needed to add it.

`geckopy init` creates the subfolders `data`, `models` and `output`, which
hold data used during reconstruction, reconstructed ecModels and simulation
results. It writes `adapter.py`, the equivalent of a custom `code` folder,
directly in the project root.
:::
::::

Store the starting GEM under `models`; other locations work too, but
keeping it there makes the project self-contained. The folder that contains
the model adapter is called the **adapter folder** throughout this guide.

`data` files use the same formats (TSV, JSON) in both languages, so a
project's `data` folder built with one toolbox can be reused with the other.
[Files in the data folder](data-folder-files.md) lists every file that
belongs there and where it gets populated.

## The model adapter

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

The model adapter is a class that inherits the `ModelAdapter` base class.
Parameters are assigned in its constructor, and organism-specific behavior
that a plain value cannot express (for example a non-standard way to
identify spontaneous reactions) is added by overriding a method of the base
class.

```matlab
classdef ecYeastGEMAdapter < ModelAdapter
    methods
        function obj = ecYeastGEMAdapter()
            obj.params.path = fullfile(findGECKOroot, 'tutorials', 'full_ecModel');
            obj.params.convGEM = fullfile(obj.params.path, 'models', 'yeast-GEM.xml');
            obj.params.org_name = 'saccharomyces cerevisiae';

            obj.params.sigma = 0.5;
            obj.params.Ptot = 0.5;
            obj.params.f = 0.5;
            obj.params.gR_exp = 0.41;

            obj.params.c_source = 'r_1714';
            obj.params.bioRxn = 'r_4041';
            obj.params.enzyme_comp = 'cytoplasm';

            obj.params.uniprot.type = 'proteome';
            obj.params.uniprot.ID = 'UP000002311';
            obj.params.uniprot.geneIDfield = 'gene_oln';
            obj.params.uniprot.reviewed = true;

            obj.params.kegg.ID = 'sce';
            obj.params.kegg.geneID = 'kegg';

            obj.params.complex.taxonomicID = 559292;
        end
    end
end
```
:::
:::{tab-item} 🐍 Python
:sync: python

The model adapter is a `model_adapter.toml` file, loaded with
`ModelAdapter.from_folder(path)`. The values are those of the
`full_ecModel` tutorial:

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

`geckopy init` also scaffolds an `adapter.py` stub next to the TOML file,
for organism-specific behavior that cannot be expressed as a plain value
(the MATLAB equivalent is overriding a method of the `ModelAdapter` base
class).
Most projects only edit the TOML file and leave `adapter.py` untouched.
:::
::::

If a parameter cannot be defined, because the information is absent or not
relevant, comment it out (MATLAB) or omit the key (Python). For an organism
not on KEGG:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
% obj.params.kegg.ID = '';
```
:::
:::{tab-item} 🐍 Python
:sync: python

```toml
# [kegg]
# id = ""
```
:::
::::

### Querying UniProt and KEGG

The UniProt database is the source of enzyme molecular weights and amino
acid sequences and is essential; KEGG can assign EC number annotations and
is useful but optional. The query parameters must select data that identify
genes with the same style of identifier as the starting GEM: a mismatch
here means enzyme data cannot be matched to model genes later.

:::{warning} Proteome over taxonomy
UniProt data can be identified either by proteome or by taxonomy. Proteome
is preferred, because it avoids redundant matches between gene and protein
identifiers.
:::

To find a UniProt proteome dataset, search
[uniprot.org/proteomes](https://www.uniprot.org/proteomes) for the organism.
If several proteome datasets exist for the same organism, prefer a
[reference proteome](https://www.uniprot.org/proteomes?facets=proteome_type%3A1&query=%2A).
Then open the UniProt page for one of its proteins and check, under "Names &
Taxonomy - Gene names", that its gene identifiers use the same style as the
starting GEM.

For example, *Saccharomyces cerevisiae* has 93 UniProt proteomes, one of
which is the reference proteome for strain S288c (`UP000002311`). A protein
in that proteome carries the gene identifier `YFL026W`, which matches the
style used in yeast-GEM; UniProt labels this style "Ordered locus name",
returned by the API field `gene_oln`. The model adapter accordingly sets
`uniprot.type` to `proteome`, `uniprot.ID` (Python: `uniprot.id`) to
`UP000002311` and `uniprot.geneIDfield` (Python: `uniprot.gene_id_field`) to
`gene_oln`.

Taxonomy is the alternative when no proteome fits: the
[taxonomy browser](https://www.uniprot.org/taxonomy/) identifier should be
as specific as possible. For *S. cerevisiae* the taxonomy identifier 4932
covers 322 strains and 53,526 proteins in total, while 559292 refers to
strain S288c alone, at 6,735 proteins. In that case `uniprot.type` is
`taxonomy` and `uniprot.ID` (Python: `uniprot.id`) is `559292`.

For KEGG, choose the three- or four-letter species identifier (`kegg.ID`;
Python: `kegg.id`)
from the
[KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html); for
*Homo sapiens* this is `hsa`. Then check which gene identifier KEGG links to
its genes, on the genome entry page (for example
[genome.jp/entry/hsa](https://www.genome.jp/entry/hsa)), which links to the
list of KEGG genes. For *H. sapiens* those genes are numbered sequentially,
which does not match the identifiers used in human-GEM; the "Other DBs"
section of the same page instead lists Ensembl gene identifiers (for
example `ENSG00000236362`). `kegg.geneID` (Python: `kegg.gene_id`) for
human-GEM is therefore `Ensembl`, not `KEGG`.

## Handling unusual identifier formats

If an organism is in UniProt but no `uniprot.geneIDfield` (Python:
`uniprot.gene_id_field`) matches the model's gene identifiers, build a conversion table at
`data/uniprotConversion.tsv` with columns of model genes and UniProt
identifiers.

For example, the *Escherichia coli* model iML1515 uses gene identifiers
styled as `b0008`, which UniProt does not carry as a field, but KEGG links
both identifiers. Build `uniprotConversion.tsv` from KEGG data (this
requires a loaded model adapter; see
[Building an empty ecModel](building-ec-model.md#set-the-default-model-adapter)):

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
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy downloads KEGG data through the `geckopy` CLI rather than a Python
function, writing a header-less CSV with `uniprot`, `gene`, `kegg_gene` and
further EC, MW, pathway and sequence columns:

```bash
geckopy kegg-download eco data/kegg.csv
```

Select the two relevant columns and write them out as
`uniprotConversion.tsv`. The file has no header row, so the column names
must be supplied to `pandas.read_csv` rather than read from it:

```python
import pandas as pd

columns = ["uniprot", "gene", "kegg_gene", "ec", "mw", "pathway", "sequence"]
kegg = pd.read_csv(params.path / "data" / "kegg.csv", header=None, names=columns)
kegg[["kegg_gene", "uniprot"]].rename(columns={"kegg_gene": "genes"}).to_csv(
    params.path / "data" / "uniprotConversion.tsv", sep="\t", index=False,
)
```
:::
::::

Other organisms may need a different source for the conversion table. For
human-GEM, a conversion table ships with the starting GEM and is converted
to `uniprotConversion.tsv` in the `light_ecModel` tutorial's
`protocol.m`/`protocol.py`.

If an organism is in neither UniProt nor KEGG, the database files
themselves need to be built manually: use `data/kegg.tsv` and
`data/uniprot.tsv` from the `full_ecModel` tutorial as templates for their
column layout. Artificial UniProt and KEGG identifiers work in these
reconstructed files, but the molecular weight and sequence of each protein
must be accurate for the rest of the reconstruction to work.

:::{note} Example output
Scaffolding a project produces empty `data`, `models` and `output`
subfolders (MATLAB also creates `code`), plus a template model adapter file
named after the model and suffixed `Adapter.m` (MATLAB) or named
`model_adapter.toml` (Python). Populating
the model adapter, then querying UniProt and KEGG, fills `data/uniprot.tsv`
and `data/kegg.tsv`. If no UniProt or KEGG parameters could be identified
for the organism, `data/uniprotConversion.tsv`, `data/kegg.tsv` and
`data/uniprot.tsv` are constructed by hand instead, as described above.
:::

## See also

- [Files in the data folder](data-folder-files.md), every file a project's
  `data` folder can hold, and where it gets used.
- [Model adapter parameters](model-adapter-parameters.md), every model
  adapter parameter, in both languages.
- [Building an empty ecModel](building-ec-model.md), the next step: loading
  the conventional GEM and expanding it into an ecModel structure.
- [API reference](../api/index.md), every function in both toolboxes.
- [MATLAB vs Python](../matlab-vs-python.md), what each toolbox has.
