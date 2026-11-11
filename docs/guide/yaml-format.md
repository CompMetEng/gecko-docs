# ecModel YAML format

<!-- docs-site: concept-page -->

An ecModel is stored as one YAML file that holds the metabolic model and the enzyme data of `ec`. `saveEcModel` and `loadEcModel` (Python: `save_ec_model` and `load_ec_model`) write and read this file. GECKO (MATLAB) and geckopy (Python) use the same format, so a file saved by one toolbox loads in the other. No other ecModel format keeps the `ec` fields.

The file is the RAVEN and cobrapy YAML layout (`writeYAMLmodel` and `readYAMLmodel` of RAVEN, `write_yaml_model` and `read_yaml_model` of raven-toolbox) with the sections `gecko_light`, `ec-rxns` and `ec-enzymes` for the enzyme data. The sections `metaData`, `gecko_light`, `ec-rxns` and `ec-enzymes` are not part of the cobra schema, and cobrapy ignores them.

## File layout

The file is an ordered mapping (`!!omap`) that is written as a list of single-key entries. Each metabolite, reaction and gene is an `!!omap` of single-key items. The sections follow in this order:

| Section | Content |
| --- | --- |
| `metaData` | provenance: model identifier, name, date, authors, and the keys `gecko_format` and `generator` |
| `metabolites` | list of metabolites |
| `reactions` | list of reactions, including the protein reactions of the ecModel |
| `genes` | list of genes. A model without genes has `- genes: []` |
| `compartments` | mapping of compartment identifier to compartment name |
| `gecko_light` | `true` for a light ecModel, `false` for a full ecModel |
| `ec-rxns` | list with the kcat, source and enzymes of every row of `ec.rxns` |
| `ec-enzymes` | list with the molecular weight, sequence and concentration of every enzyme |

The writers add `gecko_light`, `ec-rxns` and `ec-enzymes` when the model has an `ec` structure. A file with one of `ec-rxns` and `ec-enzymes` and without the other is an error in geckopy, and `load_ec_model` raises a `ValueError` when `ec-rxns` or `ec-enzymes` is missing or empty. The readers also accept `id`, `name`, `version` and `gecko_light` at the top level of the file.

The metaData section and the first metabolite of `ecYeastGEM.yml` in the `full_ecModel` tutorial, abridged. This file has no `gecko_format`, `generator` or `description` key:

```yaml
!!omap
- metaData: !!omap
  - id: yeastGEM_develop
  - name: The Consensus Genome-Scale Metabolic Model of Yeast
  - date: "2026-02-26"
  - defaultLB: -1000.0
  - defaultUB: 1000.0
  - givenName: Eduard
  - familyName: Kerkhoven
  - email: eduardk@chalmers.se
  - organization: Chalmers University of Technology
  - taxonomy: taxonomy/559292
  - note: Saccharomyces cerevisiae - strain S288C
- metabolites:
  - !!omap
    - id: s_0001
    - name: (1->3)-beta-D-glucan
    - compartment: ce
    - charge: 0.0
    - formula: C6H10O5
    - annotation: !!omap
      - bigg.metabolite: 13BDglcn
      - chebi: CHEBI:37671
      - kegg.compound: C00965
      - metanetx.chemical: MNXM6492
      - sbo: SBO:0000247
      - smiles:
        - C(C1C(C(C(C(O1)O)O)O)O)O
    - deltaG: 10000000.0
```

## Metadata

`metaData` holds the identifier and name of the model and provenance. The keys are written in this order, and a key whose value is empty is left out.

| Key | Content |
| --- | --- |
| `id`, `name` | identifier and name of the model. `blankID` and `blankName` are written when the model has none |
| `version` | version of the model, when it has one |
| `date` | date of the model when it has one, otherwise the date of writing, as `yyyy-mm-dd` |
| `defaultLB`, `defaultUB` | default bounds of the model |
| `givenName`, `familyName`, `authors`, `email`, `organization`, `taxonomy`, `note`, `sourceUrl` | authorship and origin |
| other keys of the model annotation | written in alphabetical order after the keys above |

`saveEcModel` and `save_ec_model` add three keys to `metaData` of the file:

| Key | Content |
| --- | --- |
| `description` | `Enzyme-constrained model of <id>`, written when the model has no description. GECKO also treats a note as a description, and geckopy checks the key `description` |
| `gecko_format` | the ecModel format of the file, written as text. The value is `4`, as `project_format` in `model_adapter.toml` |
| `generator` | the release that wrote the file: `GECKO <version>` from GECKO and `geckopy <version>` from geckopy |

```yaml
  - description: Enzyme-constrained model of yeastGEM_develop
  - gecko_format: "4"
  - generator: GECKO <version>
```

The key `geckopy_version` of earlier geckopy releases is not written, and both save functions remove an existing one. `readYAMLmodel` reads `gecko_format`, `generator` and `description` into `ecModel.annotation`, where `description` becomes `annotation.note`. geckopy keeps `metaData` in `ec_model.notes["metaData"]`.

`writeYAMLmodel` and `write_yaml_model` write the metadata that the model holds and do not add `gecko_format` and `generator`. A file without `gecko_format` was written by GECKO 3 or by a writer that does not set the key.

## Metabolites, reactions, genes and compartments

The entries have these keys, in this order. A key is left out when its value is empty or, for numbers, NaN.

| Section | Keys |
| --- | --- |
| `metabolites` | `id`, `name`, `compartment` (compartment identifier), `charge`, `formula`, `annotation`, `inchis`, `deltaG`, `metFrom`, `notes` |
| `reactions` | `id`, `name`, `metabolites`, `lower_bound`, `upper_bound`, `gene_reaction_rule`, `objective_coefficient`, `subsystem`, `annotation`, `references`, `rxnFrom`, `deltaG`, `confidence_score`, `notes` |
| `genes` | `id`, `name`, `annotation`, `protein` |

- `metabolites` of a reaction maps the metabolite identifier to its stoichiometric coefficient, sorted by identifier. A reaction without metabolites has `metabolites: !!omap []`.
- `objective_coefficient` is written for reactions with a non-zero coefficient.
- `subsystem` is a list, also for one subsystem.
- `annotation` maps a cross-reference key to a string, or to a list for several values. The key `smiles` of a metabolite and `ec-code` of a reaction hold a list also for one value. The keys are sorted alphabetically.
- Numbers have at least one decimal (`1000.0`). A string that YAML reads as a number, boolean, null or date is written in double quotes.
- `compartments` is a flat mapping, for example `c: cytoplasm`.

The reactions of an ecModel have the identifiers of the build: `_REV` for the reverse direction and `_EXP_<n>` for an isozyme (see [Choose the ecModel structure](ecmodel-structure.md#what-makeecmodel-adds)). Once kcats are applied, the metabolites of a reaction include the enzymes (`prot_<id>`) with the coefficient `-MW/(kcat*3600)`:

```yaml
- reactions:
  - !!omap
    - id: r_0001_EXP_1
    - name: (R)-lactate:ferricytochrome-c 2-oxidoreductase
    - metabolites: !!omap
      - prot_P00045: -0.603312150972463
      - prot_P32891: -3.14331792797997
      - s_0025: -1.0
      - s_0709: -2.0
      - s_0710: 2.0
      - s_1399: 1.0
    - lower_bound: 0.0
    - upper_bound: 1000.0
    - gene_reaction_rule: YDL174C and YEL039C
    - subsystem:
      - Pyruvate metabolism
    - annotation: !!omap
      - bigg.reaction: D_LACDcm
      - ec-code:
        - 1.1.2.4
        - 1.1.99.-
      - kegg.pathway:
        - sce00620
        - sce00920
      - kegg.reaction: R00197
      - metanetx.reaction: MNXR138960
      - sbo: SBO:0000176
    - deltaG: 10000000.0
    - confidence_score: 2.0
```

## Protein reactions

The reactions `usage_prot_<enzyme>` and `prot_pool_exchange` run forward. `usage_prot_<enzyme>` converts `prot_pool` into `prot_<enzyme>`, and `prot_pool_exchange` supplies `prot_pool`. The flux of `usage_prot_<enzyme>` is the usage of the enzyme and is positive. The upper bound of `usage_prot_<enzyme>` is 1000 until `constrainEnzConcs` sets a measured concentration, and the upper bound of `prot_pool_exchange` is the protein pool size that `setProtPoolSize` sets.

```yaml
    - id: usage_prot_P00925
    - name: usage_prot_P00925
    - metabolites: !!omap
      - prot_P00925: 1.0
      - prot_pool: -1.0
    - lower_bound: 0.0
    - upper_bound: 1000.0
    - gene_reaction_rule: YHR174W
    - subsystem:
      - Protein usage
```

```yaml
    - id: prot_pool_exchange
    - name: prot_pool_exchange
    - metabolites: !!omap
      - prot_pool: 1.0
    - lower_bound: 0.0
    - upper_bound: 125.0
    - subsystem:
      - Protein usage
```

A light ecModel has `prot_pool` and `prot_pool_exchange` and no usage reactions (see [Choose the ecModel structure](ecmodel-structure.md)).

GECKO 3 defines both reactions in the reverse direction, with negative flux (see [GECKO 3 to GECKO 4](../gecko3-to-gecko4.md)). `loadEcModel` and `load_ec_model` turn the protein reactions of such an ecModel forward in the loaded model. A `usage_prot_<id>` reaction with a positive coefficient of `prot_pool`, and a `prot_pool_exchange` with a negative coefficient, change the sign of their stoichiometry, bounds and objective coefficient. `upgradeEcModel` (Python: `upgrade_ec_model`) applies the same rule to a model in memory and returns the reactions it turned. Both leave a forward model unchanged. The loaders warn with the number of reactions. The file stays as it is until `saveEcModel` stores the upgraded model, and `upgradeGECKOproject` upgrades all ecModel files of a project (see [Upgrade a GECKO 3 project](../gecko3-upgrade-project.md)). In MATLAB, `loadEcModel` turns the reactions and `readYAMLmodel` leaves them as they are.

A file with a `gecko_format` above 4 is an error (`loadEcModel:format` in MATLAB, a `ValueError` in geckopy) that asks for an update of the toolbox. `upgradeEcModel` sets `gecko_format` to 4 when the key is missing or lower, for a model that has `prot_pool`.

## `ec-rxns`: enzyme data per reaction

`ec-rxns` has one entry for every row of `ec.rxns`.

| Key | Content |
| --- | --- |
| `id` | the identifier in `ec.rxns`, a reaction identifier with `_REV` and `_EXP_<n>` where they apply |
| `kcat` | turnover number in s⁻¹. The value 0 marks a reaction without kcat |
| `source` | origin of the kcat, for example `brenda` or `custom`. The default is an empty string |
| `notes` | free text. The default is an empty string |
| `eccodes` | one EC code as a string, or a list for several codes. The default is an empty string |
| `enzymes` | mapping of enzyme identifier (`ec.enzymes`) to the number of subunit copies in the reaction. Every identifier is also in `ec-enzymes` |

In a light ecModel the `id` is the reaction identifier with the prefix `<nnn>_` (`001_`, `002_`, one per isozyme), and a reaction appears once per isozyme.

A reaction without enzymes has an empty `enzymes` entry or none; both are read as no enzymes.

```yaml
- ec-rxns:
  - !!omap
    - id: r_0001_EXP_1
    - kcat: 5.77
    - source: brenda
    - eccodes: 1.1.2.4
    - enzymes: !!omap
      - P00045: 1.0
      - P32891: 1.0
  - !!omap
    - id: r_0001_EXP_3
    - kcat: 5.77
    - source: brenda
    - eccodes:
      - 1.1.2.4
      - 1.1.99.40
    - enzymes: !!omap
      - P00045: 1.0
      - P39976: 1.0
```

## `ec-enzymes`: enzyme data per enzyme

`ec-enzymes` has one entry for every enzyme in `ec.enzymes`.

| Key | Content |
| --- | --- |
| `genes` | gene identifier of the enzyme, as in `genes`. GECKO leaves the key out for an enzyme without a gene |
| `enzymes` | enzyme identifier: a UniProt accession or, for a gene that KEGG alone matches, the KEGG gene identifier |
| `mw` | molecular weight in Da. The key is left out when unknown |
| `sequence` | amino acid sequence. The default is an empty string |
| `concs` | measured concentration in mg/gDCW (see [Constrain enzymes with proteomics](proteomics.md)). The key is left out when not measured |

The pseudo-enzyme `standard` has `standard` as gene and enzyme identifier (see [Choose the kcat sources](kcat-sources.md)).

```yaml
- ec-enzymes:
  - !!omap
    - genes: Q0080
    - enzymes: P00856
    - mw: 5822.0
    - sequence: MPQLVPFYFMNQLTYGFLLMITLLILFSQFFLPMILRLYVSRLFISKL
```

A missing `mw` or `concs` is read as NaN, a missing `kcat` as 0, and a missing `source`, `notes`, `eccodes` or `sequence` as an empty string.

## Files of earlier releases

Both toolboxes read files from earlier releases of GECKO and RAVEN. The differences to the current layout are normalised on load.

| Element | Earlier layout | Current layout |
| --- | --- | --- |
| `smiles` of a metabolite | key of the metabolite | list under `annotation` |
| EC codes of a reaction | key `eccodes` of the reaction | `ec-code` under `annotation` |
| Light flag | `geckoLight: "true"` in `metaData` | top-level `gecko_light` |
| Document start | `---` before `!!omap` | `!!omap` |
| Protein reactions | reverse direction | forward direction |

geckopy repairs an entry `enzymes: !!omap` without items and a value in double quotes with unescaped double quotes, as earlier GECKO and RAVEN releases wrote them, when reading the file fails. A file written as a list of single-key mappings without `!!omap` is merged into one mapping.

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| Error `loadEcModel:format`, or a `ValueError` that names the ecModel format | The file has a `gecko_format` above 4 | Update GECKO or geckopy |
| Warning that protein usage and pool reactions are in the GECKO 3 direction | The file was saved by GECKO 3 | The loaded model is upgraded. Run `saveEcModel` to store the upgraded model |
| `ValueError` that the YAML lacks `ec-rxns` and `ec-enzymes` | The file is a conventional model | Build the ecModel with `makeEcModel` |
| `ValueError` that ecModels are saved or loaded as YAML | The filename ends in `.xml` or `.sbml` | Use a `.yml` filename. `cobra.io.write_sbml_model` writes SBML without the `ec` fields |

## See also

- [Constrain enzymes with proteomics](proteomics.md), where the values of `concs` come from.
- [Choose the ecModel structure](ecmodel-structure.md) and [Choose the kcat sources](kcat-sources.md), where `ec-rxns` and `ec-enzymes` are populated.
- [Project format 4](../gecko4-project-format.md), for the ecModel format and the project folder.
- [API reference](../api/index.md), for the read and write functions.
