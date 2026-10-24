# ecModel YAML format

<!-- docs-site: concept-page -->

This page defines the YAML format GECKO and geckopy use to save and load
ecModels. It is reference material, not a task: both toolboxes read and
write the same file, so there is no MATLAB-vs-Python distinction to draw
here.

## It is the cobrapy YAML format, plus a few GECKO keys

There is no bespoke ecModel format. An ecModel is saved as exactly the YAML
that cobrapy writes (`cobra.io.save_yaml_model`), with a handful of
GECKO-specific top-level keys added alongside it for the data cobra does not
model: $k_{cat}$ values, the enzyme list (molecular weight, sequence,
concentration), and the reaction-enzyme coupling matrix.

RAVEN handles the I/O on the MATLAB side and geckopy delegates to
raven-toolbox on the Python side; both call into cobrapy for the cobra-shaped
portion and parse the GECKO `ec-rxns` / `ec-enzymes` / `gecko_light`
sections into the ecModel's `ec` substructure (`model.ec` in MATLAB,
`EcModel.ec` in Python). Two consequences follow:

- Any cobrapy-aware tool (Escher, Memote, plain cobrapy) loads the file and
  ignores the extra `ec-*` keys, reading it as an ordinary conventional
  model.
- GECKO (MATLAB) and geckopy (Python) write and read the exact same format,
  so an ecModel built in one toolbox loads directly in the other with no
  translation step.

## Design goals

1. **Identical to cobrapy.** The cobra-shaped portion of the file is exactly
   what `cobra.io.model_to_dict` / `model_from_dict` round-trips; there is no
   custom parser or schema for that part.
2. **Round-trippable between MATLAB and Python.** RAVEN's `writeYAMLmodel`
   and `readYAMLmodel`, and raven-toolbox's equivalents, emit and accept the
   same format.
3. **Backward compatible.** Both toolboxes also load the legacy MATLAB/RAVEN
   layout (see the last section below). Empty strings and NaN values can be
   omitted on write; a reader fills in the documented default on load.

## Top-level structure

The file is one YAML mapping. It holds the following keys:

| Key | Required? | Owner | What it holds |
|---|---|---|---|
| `id` | yes | cobra | Model id |
| `name` | optional | cobra | Human-readable name |
| `version` | optional | cobra | cobra schema version (omit if unused) |
| `compartments` | optional | cobra | Mapping of compartment id to name |
| `metabolites` | yes | cobra | List of metabolite entries (see below) |
| `reactions` | yes | cobra | List of reaction entries (see below) |
| `genes` | yes | cobra | List of gene entries (see below) |
| `ec-rxns` | yes for an ecModel | raven-toolbox / RAVEN | Per-reaction ec data (see below) |
| `ec-enzymes` | yes for an ecModel | raven-toolbox / RAVEN | Per-enzyme ec data (see below) |
| `gecko_light` | optional | raven-toolbox / RAVEN | Boolean flag, defaults to `false` |
| `metaData` | optional | raven-toolbox / RAVEN | Free-form provenance: version, date, author, taxonomy, note |

A tool that understands only the cobra side (cobrapy, Escher, Memote, and
similar) ignores the GECKO-specific keys (`ec-rxns`, `ec-enzymes`,
`gecko_light`, `metaData`) without raising an error, so the same file loads
there as a plain cobra model, minus the enzyme-constraint layer.

## Cobra-shaped section

This part of the file is exactly the schema `cobra.io.dict.model_to_dict`
produces, with a few conventions:

- `compartments` is a flat mapping (`{c: cytosol, e: extracellular}`), not a
  list.
- `metabolites`, `reactions`, and `genes` are lists of plain mappings, one
  per entry.
- A reaction's `metabolites` field is a flat mapping from metabolite id to
  stoichiometric coefficient.
- `annotation` is a mapping from key to a list of strings. A metabolite's
  SMILES string lives at `annotation: {smiles: ["..."]}`.

Example metabolite:

```yaml
- id: s_0001
  name: "(1->3)-beta-D-glucan"
  compartment: ce
  formula: C6H10O5
  charge: 0
  annotation:
    bigg.metabolite: ["13BDglcn"]
    chebi: ["CHEBI:37671"]
    kegg.compound: ["C00965"]
    metanetx.chemical: ["MNXM6492"]
    sbo: ["SBO:0000247"]
    smiles: ["C(C1C(C(C(C(O1)O)O)O)O)O"]
```

Example reaction:

```yaml
- id: r_0001
  name: "(R)-lactate:ferricytochrome-c 2-oxidoreductase"
  metabolites:
    s_0027: -1.0
    s_0556: 1.0
  lower_bound: 0
  upper_bound: 1000
  gene_reaction_rule: "(YDL174C and YML054C) or (YEL024W and YML054C)"
  subsystem: "Oxidative phosphorylation"
  annotation:
    ec-code: ["1.1.2.4"]
    kegg.reaction: ["R00196"]
```

## `ec-rxns`: per-reaction ec data

A list with one entry per catalyzed reaction. When the build pipeline splits
a reaction across isozymes (`_EXP_<N>` suffix) or into forward/reverse pairs
(`_REV` suffix), each variant gets its own entry here.

| Field | Type | Required? | Notes |
|---|---|---|---|
| `id` | string | yes | Matches a model reaction id; may carry `_EXP_<N>` and/or `_REV` suffixes |
| `kcat` | number | yes | Turnover number in s⁻¹; `0` marks a reaction with no kcat assigned yet |
| `source` | string | optional | Where the kcat came from (`"brenda"`, `"dlkcat"`, `"manual"`, ...); default `""` |
| `notes` | string | optional | Free-form note; default `""` |
| `eccodes` | string or list | optional | One EC code as a string, or a list when several apply; default `""` |
| `enzymes` | mapping, enzyme id to stoichiometry | yes | Which enzymes catalyze this reaction, and the subunit count of each; every key must also appear in `ec-enzymes` |

Example:

```yaml
- id: r_0001_EXP_1
  kcat: 1500.0
  source: "brenda"
  eccodes: ["1.1.2.4", "1.1.99.40"]
  enzymes:
    P00045: 1
    P32891: 1
```

A reaction with no kcat assigned yet is written as `kcat: 0`, the sentinel
both toolboxes use for "unknown", so it round-trips back to `0` rather than
being inferred as an omission.

## `ec-enzymes`: per-enzyme ec data

A list with one entry per unique enzyme.

| Field | Type | Required? | Notes |
|---|---|---|---|
| `genes` | string | yes | Gene id; must match a `genes[].id` from the cobra section |
| `enzymes` | string | yes | Enzyme id, usually a UniProt accession |
| `mw` | number | optional | Molecular weight in Da; write NaN as `.nan`; default NaN |
| `sequence` | string | optional | Amino acid sequence; default `""` |
| `concs` | number | optional | Measured concentration in mmol/gDW, from proteomics; write NaN as `.nan`; default NaN |

The `standard` pseudo-gene, added when a reaction lacks a real gene
association (see [Applying kcat values](applying-kcats.md)), appears as
both `genes: "standard"` and `enzymes: "standard"`.

Example:

```yaml
- genes: "Q0045"
  enzymes: "P00401"
  mw: 58798.0
  sequence: "MVQRWLYSTNAKDIAVLY..."
```

## Sparse defaults

To keep files compact, a writer can omit any field that takes its documented
default (empty string, NaN); a reader fills the default back in on load. The
exception is a numeric value meant to stay explicit rather than be inferred
as an omission: a `mw` or `concs` that is deliberately unknown is written as
`.nan`, and a `kcat` with no value assigned is written as `0`, its own
sentinel (see the `ec-rxns` section above).

## Legacy MATLAB / RAVEN format

Older RAVEN/GECKO ecModels used a slightly different schema. Both GECKO and
geckopy load it: geckopy's loader normalizes it on read, and RAVEN's
`readYAMLmodel` auto-detects it. The schema differences are:

| Aspect | Legacy MATLAB / RAVEN | Current (cobrapy + GECKO keys) |
|---|---|---|
| `smiles` per metabolite | top-level metabolite key | under `annotation`, as `{smiles: ["..."]}` |
| Annotation values | scalar strings | list of strings |
| `metaData.geckoLight` | inside `metaData`, string `"true"` / `"false"` | top-level `gecko_light: <bool>` |
| `usage_prot_*` / `prot_pool_exchange` bounds | reverse direction (`lb=-1000, ub=0`) | forward direction (`lb=0, ub=1000`) |
| Outer `---` document marker | present | absent, cobra omits it |
| `metaData` provenance fields | inside `metaData` | inside `metaData` (unchanged) |

The model `id` itself stays nested under `metaData` in both the legacy and
the current format; it is not a schema difference between them. Normalizing
a legacy file moves any per-metabolite `smiles` field into `annotation`;
cobra tolerates the scalar-vs-list difference in annotation values on read. A
reader also flips any `usage_prot_*` / `prot_pool_exchange` reaction still
using the reverse-direction bounds to the current forward convention,
warning once. A legacy file written as a bare `---` sequence of single-key
maps (with no `!!omap`) is merged into one mapping by geckopy's reader. The
two layouts
hold the same information; both toolboxes' readers accept either one.

## See also

- [Proteomics integration](proteomics-integration.md), where `ec-enzymes`
  concentration values (`concs`) come from.
- [Building an ecModel](building-ec-model.md) and
  [Applying kcat values](applying-kcats.md), where `ec-rxns` and
  `ec-enzymes` are first populated.
- [API reference](../api/index.md), for the read/write functions themselves.
