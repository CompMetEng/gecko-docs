# API reference

GECKO ships as two implementations that build the **same** enzyme-constrained
metabolic models with the same algorithms:

- **GECKO**: the **MATLAB** toolbox, built on RAVEN.
  Functions use `camelCase` names.
- **geckopy**: the **Python** implementation, built on cobrapy. Functions use
  `snake_case` names.

The function help on these pages is extracted directly from the source of each
toolbox on the branch tracked by this site, so it stays in sync with the code.

## How these pages are organised

The reference is split into **two parallel trees**, one per language, each
organised by the toolbox's own module layout and each function shown with its
full help text:

- **MATLAB API (GECKO)**: one page per `src` category (`Build & edit ecModel`,
  `Gather kcats`, `Limit proteins`, …).
- **Python API (geckopy)**: one page per package, mirroring the same
  categories.
- **[MATLAB vs Python](../matlab-vs-python.md)**: a third page pairing every
  function that exists in both, generated at build time from both toolboxes'
  sources.

Every page opens with a *Functions* table you can scan, followed by the full
help for each function.

To move between the two implementations, use the
**[MATLAB vs Python](../matlab-vs-python.md)** table, which pairs every
function that exists in both (`camelCase` ↔ `snake_case`) and links to both
references.

## How the two compare

GECKO and geckopy build the same models with the same algorithms, and the two
implementations are developed together: most functions exist on both sides,
and the few that exist on only one are tracked on the
[MATLAB vs Python](../matlab-vs-python.md) page in both directions, not just
as gaps in geckopy. The differences between the two implementations are in
calling convention, not in what the functions compute:

| | GECKO (MATLAB) | geckopy (Python) |
|---|---|---|
| Naming | `camelCase` (`makeEcModel`) | `snake_case` (`make_ec_model`) |
| Returns | multiple outputs `[a,b] = f(...)` | one return value; the model is often mutated in place |
| Indexing | 1-based | 0-based |
| Missing data | often a silent default | usually raises |

:::{note} A note on the two docstring styles
geckopy's docstrings are NumPy-style, so they render as structured
parameter/return tables. GECKO's MATLAB help blocks use the toolbox's own
`Input:` / `Output:` convention, so they render as faithful help text rather
than typed tables. The content is the same; only the formatting differs.
:::

Use the navigation to browse either tree, or start from the
[MATLAB vs Python](../matlab-vs-python.md) table.

```{toctree}
:hidden:

matlab/index
python/index
../matlab-vs-python
```
