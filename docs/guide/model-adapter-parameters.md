# Model adapter parameters

The core `obj.params` entries in the MATLAB model adapter, and the
corresponding TOML key in the Python `model_adapter.toml` (dotted keys are
`[section]` tables). Example values come from the `full_ecModel` tutorial;
see [Getting started](getting-started.md) for the model adapter itself.

This table covers the parameters used across the main reconstruction
workflow. It omits two specialized groups: the CMA-ES kcat-tuning
hyperparameters (`obj.params.evotune.*` in MATLAB, `EvotuneParams` in
Python's `adapter.params`, covered by [Growth-rate
tuning](growth-rate-tuning.md)) and, Python-only, `OkpParams` for
OpenKineticsPredictor settings and the `kcat_aggregate_brenda` /
`kcat_aggregate_candidates` / `kcat_aggregate_isozymes` defaults that let an
adapter centrally override a kcat-matching function's aggregation choice.

| MATLAB parameter | Python (TOML) | Example | Explanation |
|-------------------|---------------|---------|-------------|
| `bioRxn` | `bio_rxn` | `r_4041` | Reaction identifier for the biomass or growth pseudo-reaction, whose flux is the growth rate in h^-1. |
| `c_source` | `c_source` | `r_1714` | Reaction identifier for the glucose exchange reaction (or other preferred carbon source). |
| `complex.taxonomicID` | `complex.taxonomic_id` | `559292` | Taxonomic identifier as available from the [Complex Portal](https://www.ebi.ac.uk/complexportal/home). |
| `convGEM` | `conv_gem` | `fullfile(obj.params.path, 'models', 'yeast-GEM.xml')` (MATLAB) / `"models/yeast-GEM.yml"` (Python) | Path to the starting conventional GEM file. |
| `enzyme_comp` | `enzyme_comp` | `cytoplasm` | Compartment name in which added enzymes are located; must match one of the ecModel's compartment names. |
| `f` | `f` | `0.5` | Fraction of enzymes in the ecModel relative to all proteins (g enzyme/g protein). `calculateFfactor()` (Python: `calculate_f_factor`) computes it from a proteomics dataset. |
| `gR_exp` | `gr_exp` | `0.41` | Reference (experimentally observed) maximum growth rate in h^-1, the default tuning target in [Growth-rate tuning](growth-rate-tuning.md#sensitivity-tuning-of-kcat-values). |
| `kegg.geneID` | `kegg.gene_id` | `kegg` | The gene identifier or database link from KEGG that corresponds to the ecModel genes; for human-GEM this is `Ensembl`. |
| `kegg.ID` | `kegg.id` | `sce` | Organism ID in the KEGG database, from the [KEGG organism list](https://www.genome.jp/kegg/catalog/org_list.html). |
| `org_name` | `org_name` | `saccharomyces cerevisiae` | Scientific name of the organism, used by `fuzzyKcatMatching` (Python: `fuzzy_kcat_matching`). |
| `path` | `path` | `fullfile(findGECKOroot, 'tutorials', 'full_ecModel')` (MATLAB) | Path to the directory holding all ecModel-specific content. In Python, `path` is set automatically to the folder passed to `ModelAdapter.from_folder()`, not written in the TOML file itself. |
| `Ptot` | `p_tot` | `0.5` | Total protein content in the cell (g protein/gDCW). |
| `sigma` | `sigma` | `0.5` | Average enzyme saturation factor sigma. |
| `uniprot.geneIDfield` | `uniprot.gene_id_field` | `gene_oln` | UniProt field with the gene identifiers used in the ecModel. Must be one of the "Returned Field" entries under "Names & Taxonomy". |
| `uniprot.ID` | `uniprot.id` | `UP000002311` | Identifier of the UniProt dataset (by taxonomy or proteome) with complete coverage of the ecModel genes. |
| `uniprot.type` | `uniprot.type` | `proteome` | Whether `uniprot.ID` is a taxonomy or a proteome identifier. |
| `uniprot.reviewed` | `uniprot.reviewed` | `true` | Whether only reviewed UniProt data is considered. Reviewed data has the highest confidence but may have low coverage for nonmodel organisms. |

## See also

- [Getting started](getting-started.md), where the model adapter is created
  and populated.
- [Files in the data folder](data-folder-files.md), the other project-wide
  reference table.
