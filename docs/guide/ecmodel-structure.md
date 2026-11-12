# Choose the ecModel structure

`makeEcModel` turns a conventional genome-scale metabolic model (GEM) into an enzyme-constrained model (ecModel) without kcats: reversible reactions are split by direction, the enzymes of each reaction are recorded in the `ec` structure, and the protein pool is added. The result is a full or a light ecModel without kcats, a list of the genes that have no protein data, and, for an organism in the Complex Portal, the subunit stoichiometry of the enzyme complexes.

## Functions

| MATLAB | Python | Note |
|---|---|---|
| `ModelAdapterManager.setDefault` | `ModelAdapter.from_folder` | read `model_adapter.toml` of the project |
| `loadDatabases` | `load_uniprot_tsv`, `load_kegg_tsv` | read `data/uniprot.tsv` and `data/kegg.tsv`, and download a missing file |
| `loadConventionalGEM` | `load_conventional_gem` | load the GEM named by `conv_gem` in the model adapter |
| `makeEcModel` | `make_ec_model` | build a full or a light ecModel |
| `getComplexData` | `get_complex_data` | download complex stoichiometries from the Complex Portal |
| `applyComplexData` | `apply_complex_data` | write the subunit stoichiometry of matching complexes to `ec.rxnEnzMat` |

## Setup

The project folder has a `model_adapter.toml` (see [Build an ecModel](first-ecmodel.md)). The build reads these adapter keys, described in [Model adapter parameters](model-adapter-parameters.md):

- `conv_gem`: path of the conventional GEM.
- `enzyme_comp`: name of the compartment (an entry of `model.compNames`) that receives the protein pseudometabolites.
- `uniprot.id`, `uniprot.type`, `uniprot.gene_id_field`, `uniprot.reviewed`: the UniProt query that gives `data/uniprot.tsv`.
- `kegg.id`, `kegg.gene_id`: the KEGG organism and field that give `data/kegg.tsv`.
- `complex.taxonomic_id`: the taxonomy identifier for the Complex Portal.

The data files are described in [Files in the data folder](data-folder-files.md).

## Full or light ecModel

Both structures add the enzyme cost of a reaction as protein mass drawn from the protein pool. They differ in how isozymes and single enzymes appear in the model:

| Property | Full ecModel | Light ecModel |
|---|---|---|
| Isozymes | each isozyme gets its own copy of the reaction (`_EXP_1`, `_EXP_2`, ...) | the reaction is not copied; `ec.rxns` has one row per isozyme, with the prefix `001_`, `002_`, ... |
| Enzymes in the model | one pseudometabolite `prot_<UniProt>` and one reaction `usage_prot_<UniProt>` per enzyme | none |
| Enzyme cost of a reaction | the reaction consumes its enzymes; the enzymes draw on `prot_pool` | the reaction consumes `prot_pool` directly, with the cost of the isozyme with the smallest ratio of molecular weight (MW) to kcat |
| Size of the model | larger than the conventional GEM by the isozyme copies and one reaction per enzyme | the irreversible conventional GEM plus `prot_pool_exchange` |
| Needed for | proteomics constraints, enzyme usage and bottleneck analysis | |

A light ecModel cannot be turned into a full one, or the reverse; the choice is made when `makeEcModel` runs, and it is stored in the ecModel (`ec.geckoLight` in MATLAB, `ec.gecko_light` in Python, `gecko_light` in the YAML file).

Build a full ecModel unless the size of the full model makes the simulations too slow and no task in the next table is needed. These tasks need the per-enzyme pseudometabolites and usage reactions of a full ecModel:

| Task | MATLAB | Python |
|---|---|---|
| Constrain enzymes with proteomics | `constrainEnzConcs` raises an error, so the functions that relax these constraints have nothing to act on; `relaxProteomicsGreedy` and `getIsozymeCoverage` raise an error themselves | `constrain_enz_concs` raises a `ValueError`; the flux, bound, shadow price and concentration setter of `Enzyme` raise a `NotImplementedError` |
| Enzyme usage and bottlenecks | `getEnzymeUsage`, `getEnzymeBottlenecks` and `getPfbaEnzymes` raise an error | `enzyme_usage` and `pfba_enzymes` raise a `NotImplementedError`; `get_enzyme_bottlenecks` raises a `KeyError`, because the `prot_<UniProt>` constraints it reads do not exist |
| Fill kcats from other isozymes | `getKcatAcrossIsozymes` raises an error | `fill_kcats_from_isozymes` raises a `NotImplementedError` |
| Add reactions to an ecModel | `addNewRxnsToEC` raises an error | `add_new_rxns_to_ec` raises a `NotImplementedError` |
| Convert `customKcats.tsv` to `custom.tsv` | `convertCustomKcats` raises an error | `convert_custom_kcats` raises a `ValueError` |

On a light ecModel, `assignKcats` and `collectKcats` skip the step that fills kcats from other isozymes. A `custom.tsv` written from a full ecModel applies to a light ecModel too. `applyKcatConstraints`, `getStandardKcat`, `applyComplexData`, `sensitivityTuning` and `getSubsetEcModel` work on both structures.

The tutorial script `tutorials/full_ecModel/code/plotlightVSfull.m` of GECKO builds a light and a full ecModel of yeast-GEM with the same kcats, maximises growth in both, and plots the two flux distributions mapped to the reactions of the GEM.

## Build the ecModel

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
ModelAdapterManager.setDefault('path/to/project');
model = loadConventionalGEM();

% Full ecModel
[ecModel, noUniprot] = makeEcModel(model);

% Light ecModel
[ecModel, noUniprot] = makeEcModel(model, 'geckoLight', true);
```

`makeEcModel` needs a model in RAVEN format. It raises an error for a model with the field `rules` or `modelID`, which a model loaded with the COBRA Toolbox has; convert such a model with `ravenCobraWrapper`.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ModelAdapter, load_conventional_gem, make_ec_model

adapter = ModelAdapter.from_folder("path/to/project")
model = load_conventional_gem(adapter)

# Full ecModel
ec_model = make_ec_model(model, adapter)

# Light ecModel
ec_model = make_ec_model(model, adapter, gecko_light=True)
```

`make_ec_model` returns a new `EcModel` and leaves `model` unchanged. It raises a `ValueError` when it is called on an ecModel whose `ec` is already filled.
:::
::::

The ecModel has no kcats yet: `ec.kcat` is 0 for every row, and no metabolic reaction consumes an enzyme (full ecModel) or `prot_pool` (light ecModel). [Choose the kcat sources](kcat-sources.md) fills the kcats and applies them.

## Steps of makeEcModel

`makeEcModel` (Python: `make_ec_model`) runs these steps in order:

| Step | Full | Light |
|---|---|---|
| Remove the gene associations of pseudo-reactions: reactions whose name contains `pseudoreaction`, and the reactions listed in `data/pseudoRxns.tsv` | yes | yes |
| Reverse the reactions with a lower bound below 0 and an upper bound of 0 | yes | yes |
| Split each reversible reaction, except exchange reactions, into a forward reaction and a reverse reaction with the suffix `_REV` | yes | yes |
| Split each reaction with isozymes (`or` in the gene rule) into one reaction per isozyme, with the suffix `_EXP_<n>` | yes | no |
| Create `ec` and fill the genes, UniProt identifiers, molecular weights and sequences from `data/uniprot.tsv`, and from `data/kegg.tsv` for genes that UniProt does not match | yes | yes |
| Record which enzymes each reaction needs in `ec.rxnEnzMat` (Python: `ec.rxn_enz_mat`), with 1 for every subunit | yes | yes |
| Add a pseudometabolite `prot_<UniProt>` for every enzyme | yes | no |
| Add the pseudometabolite `prot_pool` | yes | yes |
| Add a reaction `usage_prot_<UniProt>` for every enzyme, from `prot_pool` to `prot_<UniProt>`, with bounds 0 and 1000 | yes | no |
| Add `prot_pool_exchange`, which produces `prot_pool`, with bounds 0 and 1000 | yes | yes |

The upper bound of `prot_pool_exchange` stays 1000 until [Set the protein pool](protein-pool.md) sets it.

The identifiers that these steps add must be new, so `makeEcModel` raises an error when a metabolite identifier of the GEM starts with `prot_`, or when a reaction identifier starts with `usage_prot_` or `prot_pool`, or ends with `_REV` or `_EXP_<digits>`.

## Match genes to UniProt and KEGG

`makeEcModel` matches each gene of the model to a row of `data/uniprot.tsv`, on the field set by `uniprot.gene_id_field`. When `data/uniprotConversion.tsv` exists, the genes are first converted to UniProt identifiers with that table, and the match is on the UniProt identifier. A gene that UniProt does not match is looked up in `data/kegg.tsv`, on the field set by `kegg.gene_id`. For a gene found in KEGG, `ec.enzymes` gets the UniProt accession of the KEGG row, or the KEGG gene identifier when the row has no accession; a warning lists these genes.

A gene that matches in neither file has no enzyme in the ecModel. A subunit of a complex without a match is left out of the complex, and the other subunits still give the reaction its enzyme cost. A reaction, or in a full ecModel an isozyme copy of a reaction, whose genes all have no match has an empty row in `ec.rxnEnzMat` and no enzyme cost. In a light ecModel, such an isozyme is left out when the isozyme with the smallest cost is selected.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

`noUniprot`, the second output of `makeEcModel`, lists the genes that match neither file, and a warning gives their number.

`makeEcModel` downloads a missing `data/uniprot.tsv` or `data/kegg.tsv` through `loadDatabases`, with the `[uniprot]` and `[kegg]` values of the adapter.
:::
:::{tab-item} 🐍 Python
:sync: python

`make_ec_model` returns no list. It logs a warning with the number of genes that match neither file and the first five, and adds a note under `rxn.notes["geckopy_warning"]` to every reaction that has such a gene.

`make_ec_model` downloads a missing `data/uniprot.tsv` or `data/kegg.tsv` with the `[uniprot]` and `[kegg]` values of the adapter, through `load_uniprot_tsv` and `load_kegg_tsv`. It raises a `FileNotFoundError` when `data/uniprot.tsv` is missing and `uniprot.id` is empty. The arguments `uniprot_db` and `kegg_db` take databases loaded beforehand.

The commands `geckopy uniprot-download` and `geckopy kegg-download` download the same files, with identifiers and options given on the command line; they do not read the adapter.
:::
::::

In both languages, a file that exists is not downloaded again: after a change of `uniprot.id`, delete `data/uniprot.tsv` before the build.

Many genes without a match mean that the UniProt query or the gene identifier field does not fit the gene identifiers of the GEM. Compare a few gene identifiers of the GEM with the gene column of `data/uniprot.tsv`, then change `uniprot.id`, `uniprot.type` or `uniprot.gene_id_field`, or add `data/uniprotConversion.tsv` (see [Find the UniProt and KEGG parameters](#find-the-uniprot-and-kegg-parameters)).

## Find the UniProt and KEGG parameters

`data/uniprot.tsv` gives the molecular weight and the sequence of each enzyme, and a GEM without it has no enzyme data. `data/kegg.tsv` is optional: it fills genes that UniProt does not match, and EC numbers. The query must return gene identifiers in the same style as the genes of the GEM.

- **UniProt proteome or taxonomy.** `uniprot.id` has no default: without it and without `data/uniprot.tsv`, the build raises an error that names the key (MATLAB: `loadDatabases:noUniprotID`). With `uniprot.type = "proteome"`, `uniprot.id` is a proteome identifier from [UniProt proteomes](https://www.uniprot.org/proteomes); choose the reference proteome when the organism has several proteomes. With `uniprot.type = "taxonomy"`, `uniprot.id` is a taxonomy identifier; choose the most specific one, for example the strain (559292 for *S. cerevisiae* S288C) in place of the species (4932). A proteome gives fewer duplicate matches between genes and proteins. `uniprot.reviewed = true` restricts the query to Swiss-Prot entries; the default `false` also includes unreviewed entries (`geckopy uniprot-download`: the option `--reviewed-only` restricts it).
- **UniProt gene identifier field.** `uniprot.gene_id_field` is the UniProt field whose values match the genes of the GEM. The page of one protein on uniprot.org shows its gene names under "Names & Taxonomy"; for yeast-GEM, which uses identifiers such as `YFL026W` ("Ordered locus names"), the field is `gene_oln`.
- **KEGG organism code.** `kegg.id` is the code from the [KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html), for example `sce` or `hsa`. The default is empty: the build then downloads no KEGG file, prints a warning and uses no KEGG data, which is the setting for an organism that is not in KEGG.
- **KEGG gene identifier.** With `kegg.gene_id = "kegg"`, the genes are matched on the KEGG gene identifier. Another value is read from the "Other DBs" links of each KEGG gene entry, for example `Ensembl` for the gene identifiers of Human-GEM. A KEGG entry without a UniProt link is not written to `data/kegg.tsv`.

When no UniProt field matches the gene identifiers, `data/uniprotConversion.tsv` maps them: a header row, then one row per gene with the gene identifier and the UniProt identifier, tab-separated. `data/kegg.tsv` has both identifiers in its first and third columns (UniProt, gene, KEGG gene, comma-separated, no header), which gives the table for an organism whose GEM uses KEGG gene identifiers, such as *E. coli* iML1515 with `b0008`:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
params = ModelAdapterManager.getDefault().getParameters();
DB = loadDatabases('kegg');
fID = fopen(fullfile(params.path, 'data', 'uniprotConversion.tsv'), 'w');
fprintf(fID, '%s\t%s\n', 'genes', 'uniprot');
output = transpose([DB.kegg.keggGene, DB.kegg.uniprot]);
fprintf(fID, '%s\t%s\n', output{:});
fclose(fID);
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
import pandas as pd

data = adapter.params.path / "data"
columns = ["uniprot", "gene", "kegg_gene", "ec", "mw", "pathway", "sequence"]
kegg = pd.read_csv(data / "kegg.tsv", header=None, names=columns)
kegg[["kegg_gene", "uniprot"]].rename(columns={"kegg_gene": "genes"}).to_csv(
    data / "uniprotConversion.tsv", sep="\t", index=False,
)
```
:::
::::

For an organism in neither UniProt nor KEGG, write `data/uniprot.tsv` (and, if needed, `data/kegg.tsv`) by hand, with the columns of the files of the `full_ecModel` tutorial. The identifiers can be invented, but the molecular weights and sequences must be correct, because the enzyme costs and the kcat predictions use them.

## Add the stoichiometry of enzyme complexes

`makeEcModel` gives every subunit of an enzyme complex the stoichiometry 1. The [Complex Portal](https://www.ebi.ac.uk/complexportal/complex/organisms) has curated subunit stoichiometries for a limited set of organisms; the link lists them. For an organism in the list, set `complex.taxonomic_id` to its taxonomy identifier and add the data. For another organism, keep the stoichiometry of 1, or write `data/ComplexPortal.json` from other databases or the literature.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
complexInfo = getComplexData();
[ecModel, foundComplex, proposedComplex] = applyComplexData(ecModel, complexInfo);
```

`getComplexData` reads the taxonomy identifier from the adapter, or takes it as the argument `taxonomicID`; 0 downloads the complexes of all organisms. Without a taxonomy identifier, it warns and returns an empty structure. It writes `data/ComplexPortal.json`. `applyComplexData` without `complexInfo` reads that file, and runs `getComplexData` when the file does not exist. `foundComplex` and `proposedComplex` are tables, and the number of each is printed.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import apply_complex_data, get_complex_data

json_path = adapter.params.path / "data" / "ComplexPortal.json"
get_complex_data(adapter.params.complex.taxonomic_id, write_to=json_path)
apply_complex_data(ec_model, path=json_path)
```

`get_complex_data` takes the taxonomy identifier (0 for all organisms) and returns the complexes; `write_to` saves them. Without a taxonomy identifier (`None`), it logs a warning and returns an empty list. `apply_complex_data` changes `ec_model` in place, logs the number of full and proposed matches, and logs each proposed complex as a warning. When at least one complex matches and `apply=True` (the default), it runs `apply_kcat_constraints` afterwards.
:::
::::

A complex is applied to a reaction when its proteins and the enzymes of the reaction are the same set. For a reaction with more than one enzyme and no exact match, a complex is proposed, not applied, in two cases: the complex contains all enzymes of the reaction and more subunits; or the complex contains at least 75 % (and less than 100 %) of the enzymes of the reaction and has no more subunits than the reaction has enzymes, so it can contain subunits that the reaction lacks (Python: the keyword `min_match_to_propose`, default 0.75). A reaction can have a proposal for each case, so two rows in `proposedComplex` (Python: two warnings). Read the proposed complexes: a missing subunit in the gene rule of the GEM can be the reason, and a curated gene rule then gives an exact match in the next build.

The stoichiometry changes `ec.rxnEnzMat` (Python: `ec.rxn_enz_mat`). The enzyme cost in the reactions follows from it when the kcats are applied, so add the complex data before the kcats are assigned.

## Troubleshooting

| Problem | Possible reason | Solution |
|---|---|---|
| Error that identifiers in `model.mets` or `model.rxns` are not allowed | the GEM has identifiers that start with `prot_`, `usage_prot_` or `prot_pool`, or end with `_REV` or `_EXP_<digits>` | rename those identifiers in the GEM |
| Error that the compartment cannot be found in `model.compNames` | `enzyme_comp` differs from every compartment name of the GEM | set `enzyme_comp` to a name from `model.compNames`; a compartment identifier gives the same error |
| Error that none of the proteins in `uniprot.tsv` or `kegg.tsv` match the genes (Python: `ValueError`) | the UniProt and KEGG parameters do not fit the gene identifiers | see [Match genes to UniProt and KEGG](#match-genes-to-uniprot-and-kegg) |
| MATLAB error that the model was likely loaded with the COBRA Toolbox | the model has the field `rules` or `modelID` | load it with `importModel`, or convert it with `ravenCobraWrapper` |
| An error that names a light ecModel (Python: `NotImplementedError` or `ValueError`) | the function needs a full ecModel | build a full ecModel |
| Warning that no taxonomic identifier is specified, and no complex data | `complex.taxonomic_id` is not set; `getComplexData` returns an empty structure (Python: `get_complex_data` returns an empty list) | set it in `model_adapter.toml`, or give it as an argument |
| Error that no data could be gathered from the Complex Portal | the Complex Portal has no complexes for this taxonomy identifier | skip the complex data |
| The rows of `ec.rxns` do not match `model.rxns` in a light ecModel | the rows have the prefix `001_`, `002_`, ... | remove the first four characters |

## See also

- [Introduction to ecModels](introduction.md), for the enzyme constraint that both structures encode.
- [Choose the kcat sources](kcat-sources.md), the next step.
- [Constrain enzymes with proteomics](proteomics.md) and [Enzyme usage and bottlenecks](enzyme-usage.md), which need a full ecModel.
- [ecModel YAML format](yaml-format.md), for `gecko_light` and the `ec` fields in the saved file.
