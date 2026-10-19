# Building an empty ecModel

Building an ecModel expands a conventional GEM so enzyme constraints can be
added to it later. Reversible reactions split into forward and backward
copies, because enzyme kinetics depend on direction; reactions catalyzed by
isozymes split into one reaction per isozyme, because each has a different
kinetics and molecular weight; and the protein pool, together with enzyme
pseudo-metabolites that draw from it, is added to the network. The result
is an **empty ecModel**: enzyme constraints are not yet applied, only the
structure that will carry them.

This page assumes a project and model adapter already exist; see
[Getting started](getting-started.md).

## Functions on this page

| MATLAB | Python | |
|---|---|---|
| `ModelAdapterManager.setDefault` | *(explicit argument instead)* | make an adapter the default for the session |
| `loadConventionalGEM` | `load_conventional_gem` | load the starting GEM from the path in the adapter |
| `makeEcModel` | `make_ec_model` | build the empty ecModel, full or light |
| `getComplexData` / `applyComplexData` | `get_complex_data` / `apply_complex_data` | add enzyme complex subunit stoichiometry |
| `saveEcModel` / `loadEcModel` | `save_ec_model` / `load_ec_model` | round-trip the ecModel through YAML |

## Set the default model adapter

Most GECKO functions need the model adapter.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

Set a default with `ModelAdapterManager` instead of passing it to every
call. The default then applies to every GECKO function for the rest of
that MATLAB session, unless another adapter is given explicitly:

```matlab
adapterLocation = fullfile(findGECKOroot, 'tutorials', ...
    'full_ecModel', 'YeastGEMAdapter.m');
ModelAdapterManager.setDefault(adapterLocation);
```

Retrieve the default explicitly when needed, for example when simulating
several ecModels in the same session:

```matlab
ModelAdapter = ModelAdapterManager.getDefault();
params = ModelAdapter.getParameters();
```

The rest of this guide assumes a default model adapter is set.

**Reset the default after editing the adapter.** If the model adapter file
changes, for example after editing `YeastGEMAdapter.m`, set it as default
again:

```matlab
ModelAdapterManager.setDefault(adapterLocation);
```
:::
:::{tab-item} 🐍 Python
:sync: python

geckopy has no global default adapter: every function that needs one takes
it as an explicit argument. Load it once and pass it, or its `.params`
attribute, to each call:

```python
from pathlib import Path
from geckopy import ModelAdapter

adapter = ModelAdapter.from_folder(Path("GECKO/tutorials/full_ecModel"))
params = adapter.params
```

If the adapter file changes, reload it by calling `from_folder` again;
there is no separate "set as default" step to repeat.
:::
::::

## Load the conventional GEM

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

If the model's location is set in the adapter (`obj.params.convGEM`):

```matlab
model = loadConventionalGEM();
```

Both YAML and XML files are supported. To load a model at a different
location, or without a model adapter, use the RAVEN function directly, for
XML:

```matlab
model = importModel('path/to/modelFile.xml');
```

or YAML:

```matlab
model = readYAMLmodel('path/to/modelFile.yml');
```

**Convert from the COBRA Toolbox format if needed.** GECKO loads models
through RAVEN by default. A model loaded through the COBRA Toolbox
(recognizable by a `model.rules` field) needs converting to the RAVEN
format (recognizable by a `model.metComps` field) first, with
`ravenCobraWrapper()`.

**Warnings when the model loads.** Not every GEM in SBML format strictly
follows the L3V1 FBCv2 standard; the
[SBML Validator](https://sbml.bioquant.uni-heidelberg.de/validator_servlet/) reports
what is wrong. In most cases the model still loads despite the warning. If
it is later exported to SBML again, RAVEN avoids re-writing the same
invalid content, so cycling through `importModel`, `exportModel` and
`importModel` brings the loaded GEM closer to valid SBML.
:::
:::{tab-item} 🐍 Python
:sync: python

If the model's location is set in the adapter (`params.conv_gem`):

```python
from geckopy import load_conventional_gem

model = load_conventional_gem(adapter)
```

This returns a plain `cobra.Model`. There is no RAVEN/COBRA format
distinction to manage: cobrapy is the native format throughout geckopy, so
no conversion step is needed. To load a model at a different location or
without an adapter, use cobrapy directly:

```python
import cobra

model = cobra.io.read_sbml_model("path/to/modelFile.xml")
```

or, for a YAML file in the RAVEN/GECKO schema, raven-toolbox's reader
(installed automatically with geckopy):

```python
from raven_toolbox.io import read_yaml_model

model = read_yaml_model("path/to/modelFile.yml")
```
:::
::::

## Choose full or light, then build

A full ecModel expands isozymes into separate reactions and adds each
enzyme as its own pseudo-metabolite, which lets it be constrained
individually, for example from proteomics data. A light ecModel skips both:
it keeps only the lowest-cost isozyme per reaction and folds the protein
pool directly into enzymatic reactions, which makes it smaller and faster
to simulate. The two are not interconvertible, and the choice affects
everything downstream of this page. See
[GECKO light vs. full ecModels](gecko-light.md) for the tradeoffs.

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

`makeEcModel` may warn about how gene associations are specified in the
starting GEM. The warning does not prevent creation of the ecModel, and can
be ignored once the gene associations are confirmed correct.

**Genes without a UniProt match.** `noUniprot` lists model genes with no
UniProt match. If it contains many genes, for example more than ten,
reconsider whether a different UniProt taxonomy or proteome identifier
(see [Getting started](getting-started.md#querying-uniprot-and-kegg)) fits
better.
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

UniProt data loads automatically from `params.path / "data" /
"uniprot.tsv"`. Pass a pre-loaded `uniprot_db=` to use a different file or
to avoid re-reading it across multiple calls. Pass a pre-loaded `kegg_db=`
for the KEGG fallback described below; `None` (the default) skips it,
matching MATLAB's behavior when no KEGG database is loaded.

**Genes without a UniProt match.** `make_ec_model` returns only the built
`EcModel`, not a second `noUniprot`-style list. Unmatched genes are logged
as a warning summary and recorded on the affected reactions themselves, in
`reaction.notes["geckopy_warning"]`. As in MATLAB, many unmatched genes are
a reason to reconsider the UniProt taxonomy or proteome identifier.
:::
::::

**GECKO 4: a KEGG fallback for genes UniProt cannot match.** Not part of
the original protocol: when a KEGG database is also loaded, the build
(`makeEcModel`; Python: `make_ec_model`) consults it for genes that UniProt
could not match, before giving up on them. `ec.enzymes` receives the
UniProt accession carried on the matching KEGG row, or the bare KEGG gene id
if that row has no accession of its own (flagged in a separate warning,
since a bare KEGG id is not a standard UniProt accession). This can shrink
the list of genes without a UniProt match without any adapter changes.

The result is an empty ecModel either way: the model structure changes to
allow enzyme constraints (see
[the ec structure](applying-kcats.md#the-ec-structure)), but no constraints
are applied yet.

## Apply enzyme complex stoichiometry (optional)

Building the ecModel assigns single-subunit stoichiometry to every enzyme
complex in `ec.rxnEnzMat` (Python: `ec.rxn_enz_mat`). In reality subunit
copy numbers vary. GECKO can add this information from the
[Complex Portal](https://www.ebi.ac.uk/complexportal/complex/organisms),
using the taxonomic identifier in the model adapter parameter
`complex.taxonomicID` (Python: `complex.taxonomic_id`); the Complex Portal
covers only a limited set of taxonomic identifiers.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
complexInfo = getComplexData();
[ecModel, foundComplex, proposedComplex] = ...
    applyComplexData(ecModel, complexInfo);
```

`getComplexData` takes no input parameters; the required parameters come
from the default model adapter, a pattern shared by several other GECKO
functions. `foundComplex` and `proposedComplex` list the complexes with a
full match and the proposed complexes.

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

`apply_complex_data` mutates `ec_model` in place; there are no
`foundComplex`/`proposedComplex` return values yet. Proposed complexes are
logged as warnings, and the number of full and proposed matches is logged
at INFO level as `apply_complex_data: N full match(es), M proposed.`. The
keyword argument `min_match_to_propose` (default 0.75) sets the minimum
fraction of matching genes for a partial match to be proposed. To (re)download the
Complex Portal data first, use `get_complex_data`, which takes the adapter
explicitly, since Python functions generally take the adapter or its
parameters as an argument rather than reading a global default:

```python
from geckopy import get_complex_data

get_complex_data(adapter)
```
:::
::::

Complex data is integrated for a reaction only when its ecModel gene
association fully (100%) matches a Complex Portal complex. If no full match
exists, complexes with a partial match are proposed (MATLAB: in
`proposedComplex`; Python: in the log): either at least 75% of the
reaction's ecModel genes match a Complex Portal complex, or a Complex Portal
complex contains more subunits than the genes associated with the reaction.
Inspect the proposed complexes and consider whether curating the ecModel
gene association is appropriate; this may need further literature study.

:::{note} Example output
In the `full_ecModel` tutorial, applying Complex Portal data finds 206
complexes with a full match and 17 proposed complexes. One proposed match: reaction `r_0505_EXP_2` could match complex CPX-1293,
the mitochondrial 2-oxoglutarate dehydrogenase complex. In the ecModel this
reaction is annotated with proteins P20967 (KGD1, subunit E1), P19262
(KGD2, subunit E2) and P09624 (LPD1, subunit E3), while CPX-1293 also
includes P19955 (YMR31), the 37S ribosomal protein. Literature confirms
that P19955, also called KGD4 or subunit E4, is an essential subunit for a
stable complex, so the starting GEM's gene association for reaction
`r_0505` could be curated to include it, which would give a full match.
:::

:::{note} Complex data is missing for some or all complexes
The Complex Portal does not contain every complex; some are missing in
most organisms. Complex information is not critical for GECKO, since
uncertainty in kcat values is a larger source of error than uncertainty in
complex stoichiometry, so skipping this step and keeping the default
stoichiometry of one for every subunit is a reasonable option. It is also
possible to complement `ComplexPortal.json` manually with complex
information from other databases or the literature.
:::

## Save the ecModel

The ecModel can be saved at any point in the procedure. Only YAML retains
the full `ec` fields, so use it whenever the ecModel needs to be
modified further.

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

`saveEcModel` writes to the adapter folder automatically; the more generic
`writeYAMLmodel` writes anywhere. `loadEcModel` or the generic
`readYAMLmodel` read the model back:

```matlab
saveEcModel(ecModel, 'ecModel.yml');
writeYAMLmodel(ecModel, 'C:\path\to\ecModel.yml');
ecModel = loadEcModel('ecModel.yml');
ecModel = readYAMLmodel('C:\path\to\ecModel.yml');
```

For constraint-based analysis in other software, SBML (with an XML
extension) is often more suitable. `saveEcModel` writes SBML too, when
`filename` ends in `.xml` rather than `.yml`; `exportModel` and
`importModel` do the same for an arbitrary path. Either way, the file does
not retain the `ecModel.ec` fields, so an SBML-saved ecModel cannot be
loaded back into MATLAB for further GECKO functions:

```matlab
saveEcModel(ecModel, 'ecModelFull.xml');
exportModel(ecModel, 'C:\path\to\ecModelFull.xml');
ecModel = importModel('C:\path\to\ecModelFull.xml');
```
:::
:::{tab-item} 🐍 Python
:sync: python

`save_ec_model` writes YAML, either in the adapter folder or at an
arbitrary path; `load_ec_model` reads it back:

```python
from geckopy import load_ec_model, save_ec_model

save_ec_model(ec_model, "ecModel.yml", adapter=adapter)
save_ec_model(ec_model, r"C:\path\to\ecModel.yml")
ec_model = load_ec_model("ecModel.yml", adapter=adapter)
ec_model = load_ec_model(r"C:\path\to\ecModel.yml")
```

geckopy provides no separate SBML export for ecModels: YAML is the only
format that round-trips the `ec` fields. Because `ec_model` is a
`cobra.Model`, plain cobrapy SBML I/O still works for interoperating with
other tools, with the same caveat as MATLAB's `exportModel`: it does not
retain the `ec` fields.

```python
import cobra

cobra.io.write_sbml_model(ec_model, r"C:\path\to\ecModelFull.xml")
model = cobra.io.read_sbml_model(r"C:\path\to\ecModelFull.xml")
```
:::
::::

## Box 1: Extension of a conventional GEM

Converting a conventional GEM into an empty ecModel runs up to twelve
operations in order. Four are skipped for light ecModels, which is exactly
what makes a light ecModel smaller: it never gets the per-isozyme reaction
splits or the per-enzyme pseudo-metabolites and usage reactions that make a
full ecModel expensive to simulate.

:::{dropdown} All twelve steps, full vs. light
:open:

| # | Operation | Full | Light |
|---|---|:---:|:---:|
| 1 | Remove gene associations from pseudo-reactions (name contains `pseudoreaction`, or listed in `data/pseudoRxns.tsv`) | ✅ | ✅ |
| 2 | Invert irreversible reactions that carry only negative flux (lower bound < 0, upper bound = 0) | ✅ | ✅ |
| 3 | Determine which reactions are reversible from their bounds (MATLAB stores this as the ecModel field `rev`; geckopy has no separate reversibility vector) | ✅ | ✅ |
| 4 | Split reversible reactions into forward and reverse copies (`_REV` suffix on the reverse copy; exchange reactions keep their original, still-reversible form) | ✅ | ✅ |
| 5 | Split isozyme-catalyzed reactions (`or` in the gene-reaction rule) into one reaction per isozyme (`_EXP_1`, `_EXP_2`, …) | ✅ | -- |
| 6 | Build an empty `ec` structure (Python: an `EcData` instance) | ✅ | ✅ |
| 7 | Add enzyme MW and sequence to `ec`, from UniProt via the model adapter | ✅ | ✅ |
| 8 | Record reaction-enzyme associations in `ec.rxnEnzMat` (Python: `ec.rxn_enz_mat`) | ✅ | ✅ |
| 9 | Add each enzyme as a `prot_<uniprot ID>` pseudo-metabolite | ✅ | -- |
| 10 | Add the protein pool pseudo-metabolite | ✅ | ✅ |
| 11 | Add `usage_prot_<uniprot ID>` reactions for each enzyme pseudo-metabolite | ✅ | -- |
| 12 | Add the `prot_pool` exchange reaction | ✅ | ✅ |

Step 5's new reaction identifiers: reaction `r_0001` catalyzed by two
isozymes becomes `r_0001_EXP_1` and `r_0001_EXP_2`; a backward reaction
`r_0001_REV` becomes `r_0001_REV_EXP_1` and `r_0001_REV_EXP_2`. Light
ecModels keep the original identifiers throughout, since this step is
skipped. Step 9's example: *S. cerevisiae* enolase gene YHR174W, UniProt
identifier P00925, appears as pseudo-metabolite `prot_P00925`. Step 11's
identifiers are `usage_` followed by the enzyme metabolite identifier, for
example `usage_prot_P00925`. See [the ec
structure](applying-kcats.md#the-ec-structure) for what step 6
populates later, and [GECKO light vs. full
ecModels](gecko-light.md) for why the four full-only steps matter.
:::

:::{tip} GECKO 4: usage and pool exchange reactions already run forward
Steps 11 and 12 above describe the original GECKO 3.0 protocol, where both
the `usage_prot_*` reactions and the `prot_pool_exchange` reaction carry a
*negative* flux (`bounds = (-1000, 0)`): protein flows out of `prot_pool`
into each enzyme, and out of the model at `prot_pool_exchange`. Current
GECKO has already flipped both to the more intuitive *forward* direction
(`bounds = (0, 1000)`;
[PR #419](https://github.com/SysBioChalmers/GECKO/pull/419)): `usage_prot_*`
consumes `prot_pool` to produce `prot_<enzyme>`, and `prot_pool_exchange`
supplies `prot_pool` in the first place. Every dependent function was
updated to match (MATLAB function names): `setProtPoolSize`,
`addNewRxnsToEC`, `getStandardKcat`, `constrainEnzConcs`,
`flexibilizeEnzConcs`, `updateProtPool`, `getConcControlCoeffs`,
`getSubsetEcModel`, `getEnzymeUsage`, `reportEnzymeUsage` and
`sensitivityTuning`. geckopy implements this same
forward convention throughout, since it targets current GECKO rather than
the GECKO 3.0 protocol. This changes which bound relaxes a constraint and
which objective coefficient minimizes usage; see the worked example in
[Growth-rate tuning](growth-rate-tuning.md#too-tight-protein-pool-constraint).
:::

## See also

- [Gathering kcats](gathering-kcats.md), the next step: sourcing kcat
  values from BRENDA, DLKcat or OpenKineticsPredictor.
- [GECKO light vs. full ecModels](gecko-light.md), the tradeoffs between
  the two ecModel structures.
- [API reference](../api/index.md), every function in both toolboxes.
