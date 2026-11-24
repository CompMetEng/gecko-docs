# Find engineering targets

Flux scanning with enforced objective function (FSEOF) finds the reactions whose flux changes with the production of a compound. `ecFSEOF` returns reaction and gene targets for the production of a compound by an ecModel, each with a suggested action: over-express, knock down or knock out.

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
  PV(["Start: a functional or relaxed ecModel"]):::ctx
  TS["production reaction<br/>and carbon source uptake"]
  FS["ecFSEOF"]
  PV --> TS --> FS
  click PV href "first-ecmodel.html"
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
  PV(["Start: a functional or relaxed ecModel"]):::ctx
  TS["production reaction<br/>and carbon source uptake"]
  FS["ec_fseof"]
  PV --> TS --> FS
  click PV href "first-ecmodel.html"
```
:::
::::
:::::

## Functions

| MATLAB | Python | Note |
| --- | --- | --- |
| `ecFSEOF` | `ec_fseof` | flux scanning with enforced objective function on an ecModel |

## Setup

The examples use the ecModel and the model adapter parameters `params`, loaded as in the setup of [Analyse an ecModel](analysis.md#setup). The biomass reaction is read from the model adapter. Set the bounds of the condition, such as the medium and the uptake rate of the carbon source, before the scan ([Basic model operations](basic-model-operations.md)).

The other names in the examples are placeholders for values of the project:

| MATLAB | Python | Value |
| --- | --- | --- |
| `prodTargetRxn` | `prod_target_rxn` | identifier of the production reaction, for example the exchange reaction of the product |
| `csRxn` | `cs_rxn` | identifier of the uptake reaction of the carbon source |

The examples load the ecModel of the `full_ecModel` tutorial and use ethanol (`r_1761`) as the product and glucose (`r_1714`) as the carbon source:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
adapter  = ModelAdapterManager.setDefault('ecMyModel');
params   = adapter.getParameters();
ecModel  = loadEcModel();        % models/ecModel.yml
ecModel  = setParam(ecModel, 'obj', params.bioRxn, 1);
prodTargetRxn = 'r_1761';
csRxn         = 'r_1714';
```
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ModelAdapter, load_ec_model

adapter = ModelAdapter.from_folder("ecMyModel")
params = adapter.params
ec_model = load_ec_model("ecModel.yml", adapter=adapter)
ec_model.objective = params.bio_rxn
prod_target_rxn = "r_1761"
cs_rxn = "r_1714"
```
:::
::::

## Target selection

`ecFSEOF` first finds the production at maximum growth and the maximum production. It then fixes the production reaction at `nSteps` (Python: `n_steps`, default 16) evenly spaced values from the first to 90 % of the second. At each value it maximises growth and then minimises the total flux. A reaction is a target when the absolute Pearson correlation between its absolute flux and the enforced production is at least `corrThreshold` (Python: `correlation_threshold`, default 0.9). The scan covers the reactions with a gene rule, except those that use the standard enzyme ([Choose the *k*{sub}`cat` sources](kcat-sources.md)). The `usage_prot_*` reactions take part in the scan and are left out of the result.

Each target reaction gets an action from the slope of its absolute flux:

| Slope | Absolute flux at the last step | Action |
| --- | --- | --- |
| positive | any | `OE` (over-express) |
| negative | at most 1e-8 | `KO` (knock out) |
| negative | above 1e-8 | `KD` (knock down) |

A gene gets one action from its target reactions. When these reactions have one action, the gene keeps it, also when the gene is essential. When they have different actions, the gene gets `OE` if one of them is `OE`, otherwise `KO` if the gene is not essential, otherwise `KD`. A gene is essential when growth is infeasible or below 1e-8 with the usage reactions of its enzymes fixed at 0 and the production fixed at the last value of the scan.

When the production at maximum growth is equal to 90 % of the maximum production, there is no range to scan, and the function raises an error.

## Run the scan

The output is the first eight gene targets:

::::{tab-set}
:::{tab-item} Ⓜ️ MATLAB
:sync: matlab

```matlab
fseof = ecFSEOF(ecModel, prodTargetRxn, csRxn, 'nSteps', 16, 'outputFile', true);
fseof.geneTargets(1:8, :)
```

```text
WARNING: Carbon source lower bound was set to -1000, but the uptake rate after
model optimization is -27.8831.
ecFSEOF results stored at:
...ecMyModel/output
ans =
  8x5 cell array
    {'YOL086C'}    {'ADH1' }    {[1.0066]}    {'OE'}    {0x0 double }
    {'YLR044C'}    {'PDC1' }    {[0.9967]}    {'OE'}    {'essential'}
    {'YAL038W'}    {'CDC19'}    {[0.9599]}    {'OE'}    {0x0 double }
    ...
    ...
    {'YDR454C'}    {'GUK1' }    {[0.6004]}    {'OE'}    {'essential'}
```

`rxnTargets` and `transportTargets` list the target reactions with identifier, name, slope, gene rule and equation, ordered by the product of slope and correlation; they have no action column. `geneTargets` has one row per gene of the target reactions: gene, short name, mean slope, action and essentiality. With `outputFile` set to `true`, the function writes `ecFSEOF_genes.tsv`, `ecFSEOF_rxns.tsv` and `ecFSEOF_transporter.tsv` to the `output` folder of the project. The function warns when the lower bound of `csRxn` is below the uptake at maximum growth, that is, when the uptake does not reach its bound.
:::
:::{tab-item} 🐍 Python
:sync: python

```python
from geckopy import ec_fseof

result = ec_fseof(ec_model, prod_target_rxn, cs_rxn, n_steps=16)
result.gene_targets.head(8)
```

```text
      gene   name     slope action essentiality     reactions
0  YOL086C   ADH1  1.006611     OE               r_2115_EXP_2
1  YLR044C   PDC1  0.996674     OE    essential  r_0959_EXP_2
2  YAL038W  CDC19  0.959863     OE               r_0962_EXP_1
3  YGR254W   ENO1  0.958580     OE    essential  r_0366_EXP_2
4  YKL152C   GPM1  0.958580     OE    essential  r_0893_EXP_2
5  YCR012W   PGK1  0.956892     OE    essential        r_0892
6  YJL052W   TDH1  0.956892     OE    essential  r_0486_EXP_2
7  YDR454C   GUK1  0.600435     OE    essential        r_0330
```

`result.targets` is one DataFrame with the reaction targets first and the transport targets after them (column `transport`), each group ordered by `score`, the product of the absolute slope and the absolute correlation. The column `target_type` holds the action of each reaction. `result.gene_targets` has one row per gene of the target reactions, with the columns `gene`, `name`, `slope` (mean absolute slope), `action`, `essentiality` and `reactions`, ordered by slope. `result.scan` holds the fluxes at each step. `ec_fseof` writes no files; `result.targets.to_csv(...)` writes the table. The biomass reaction is read from `ec_model.adapter`, or from the argument `bio_rxn`. When `cs_rxn` is given, the function logs a warning when the lower bound of `cs_rxn` is below the uptake at maximum growth.
:::
::::

## Troubleshooting

| Problem | Possible reason | Solution |
| --- | --- | --- |
| `ecFSEOF` or `ec_fseof` returns no targets | no reaction reaches `corrThreshold` (Python: `correlation_threshold`) | Lower the threshold, or check the bounds of the production and carbon source reactions |
| `ecFSEOF` raises `ecFSEOF:noRange`; `ec_fseof` raises a `ValueError` that says there is no range to scan | the production at maximum growth is equal to 90 % of the maximum production | Check the bounds of the production reaction and of the carbon source reaction |
| Warning about the lower bound of the carbon source | the uptake at maximum growth does not reach the lower bound of the carbon source reaction | Set the lower bound to the uptake rate of the condition |

## See also

- [Analyse an ecModel](analysis.md): the other analyses of an ecModel and the shared setup.
- [Enzyme usage and bottlenecks](enzyme-usage.md): the enzymes that a flux distribution uses and the enzymes that limit the objective.
- [API reference](../api/index.md) and [MATLAB vs Python](../matlab-vs-python.md): the signature of each function in the table.
