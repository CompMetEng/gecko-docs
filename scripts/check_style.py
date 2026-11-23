#!/usr/bin/env python3
"""Report the prose patterns that craft/skills/writing/references/docs-prose.md discourages.

Usage: check_style.py [PATH ...] [--summary] [--strict]

A PATH that is a site directory (it has a docs/ folder) is scanned page by page with all
pattern families; the Markdown pages under docs/ are scanned, not docs/api/ and not
generated pages. A PATH that is a Markdown file is scanned with the general families only,
which hold for every text (README, pull request drafts, comments). A Python or MATLAB file is scanned in its docstrings or its leading help block with the same families. Code blocks, inline code,
link targets and directive lines are ignored. Prints one line per
page and pattern family as ``S warning path:line N x family: first match``. A pattern is
a heuristic: one hit can be correct, a family that recurs on a page is a reason to rewrite
the page. ``--summary`` prints the rate per 1000 words of every family over the site and
the pages with the highest rates. The exit code is 0 unless ``--strict`` is given and there
is a finding.
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

EM_DASH = chr(0x2014)
EN_DASH = chr(0x2013)

INTENSIFIERS = (
    "actually|genuine(?:ly)?|really|exactly|simply|just|entirely|completely|essentially|"
    "effectively|basically|clearly|obviously|quite|very|truly|merely|fundamentally"
)
EVALUATIVE = (
    "easy|easily|simple|obvious|important|key|crucial|critical|useful|robust|powerful|"
    "comprehensive|straightforward|seamless(?:ly)?|elegant|convenient|painful|sensible"
)
FIGURATIVE = (
    r"travels?|lands?|buys?|hooks?|traps?|silently|quietly|loses|"
    r"sits? (?:in|on|at|inside|where)|lives? (?:in|on|at|inside)|"
    r"fold(?:s|ed|ing)? into|housekeeping|(?:on|from) the \w+ side|routes?"
)
INFLATED = r"utili[sz]\w*|leverag\w+|facilitat\w+|foster\w*|showcas\w+|underscor\w+"

# Family name -> (pattern, flags). Each match counts once.
FAMILIES: dict[str, re.Pattern[str]] = {
    "second person": re.compile(r"\b(?:you|your|yours|yourself)\b", re.I),
    "first person plural": re.compile(r"\b(?:we|our|ours|us)\b(?! recommend)", re.I),
    "contraction": re.compile(r"\b\w+(?:n't|'re|'ve|'ll|'d)\b|\b(?:it|that|there|what|here|let)'s\b", re.I),
    "intensifier": re.compile(rf"\b(?:{INTENSIFIERS})\b", re.I),
    "evaluative word": re.compile(rf"\b(?:{EVALUATIVE})\b", re.I),
    "figurative verb": re.compile(rf"\b(?:{FIGURATIVE})\b", re.I),
    "inflated verb": re.compile(rf"\b(?:{INFLATED})\b", re.I),
    "contrast scaffolding": re.compile(
        r"\bnot (?:just|only|merely|simply)\b|\bnot an? [^.;:,]{1,60}\bbut\b|\bnot [^.;:,]{1,40}, but\b"
        r"|\brather than\b|\binstead of\b",
        re.I,
    ),
    "and not": re.compile(
        r"\b(?:and|but) not (?:a|an|the|by|in|to|for|as|on|of|with|its|their|from|at)\b"
        r"|, not (?:a|an|the|by|in|to|for|as|on|of|with|its|their|from|at)\b",
        re.I,
    ),
    "restriction word": re.compile(r"\bonly\b", re.I),
    "passive instruction": re.compile(
        r"\b(?:is|are) (?:set|checked|inspected|closed|opened|added|run|restricted|excluded|compared) "
        r"(?:first|before|afterwards)\b",
        re.I,
    ),
    "evaluative tail": re.compile(
        r", (?:which is why|which means|making|ensuring|allowing|thereby|so that)\b"
        r"|\bThis is (?:what|why)\b|\bThat is why\b",
    ),
    "labelled opener": re.compile(
        r"\b(?:the )?(?:practical consequence|catch|upshot|takeaway|bottom line|short version|key point|trick)\s*:",
        re.I,
    ),
    "reference to the document": re.compile(
        r"\bthis (?:page|section|chapter)\b|\bin this (?:guide|tutorial)\b"
        r"|\b(?:as )?(?:shown|mentioned|noted|described|discussed|listed|given) (?:above|below|earlier)\b"
        r"|\b(?:table|example|code|list|figure) (?:above|below)\b",
        re.I,
    ),
    "directive to the reader": re.compile(
        r"\b(?:make sure|be careful|be aware|keep in mind|bear in mind|do not forget|remember (?:that|to))\b", re.I
    ),
    "copula avoidance": re.compile(r"\b(?:serves? as|acts? as|functions? as|boasts?)\b", re.I),
    "generic attribution": re.compile(
        r"\b(?:generally|commonly|typically|in practice|arguably|potentially|perhaps|presumably|it appears that)\b", re.I
    ),
    "american spelling": re.compile(
        r"\b(?:behavior\w*|colors?|normaliz\w+|artifacts?|analyz\w+|optimiz\w+|initializ\w+|"
        r"visualiz\w+|standardiz\w+|organiz\w+|modeling|modeled|centers?|catalyz\w+)\b",
        re.I,
    ),
    "italic emphasis": re.compile(r"(?<![\*\w])\*(?!\*)[^*\s][^*]*?(?<!\*)\*(?!\*)"),
    "latin abbreviation": re.compile(r"\b(?:e\.g\.|i\.e\.|etc\.)", re.I),
    "percent spacing": re.compile(r"\d%"),
    "history word": re.compile(
        r"\b(?:previously|no longer|used to|formerly|obsolete|legacy|historical(?:ly)?)\b|\(was:", re.I
    ),
    "section number": re.compile(r"§\s?\d"),
    "negative definition": re.compile(r"\bNeither (?:is|of|implementation)\b|\b(?:is|are) not (?:a|an|the) ", re.I),
    "vague quantifier": re.compile(
        r"\b(?:a handful|a large (?:share|number)|a number of|much of|largely|predominantly|a couple of)\b", re.I
    ),
    "slash alternative": re.compile(r"\b[A-Za-z]{3,}/[A-Za-z]{3,}\b"),
    "dash": re.compile(rf"{EM_DASH}|(?<!\d){EN_DASH}|{EN_DASH}(?!\d)"),
}

# Families that hold for documentation pages only; the others hold for every text.
DOCS_ONLY = {
    "second person", "first person plural", "heading form", "box title", "bold",
    "italic emphasis", "section number", "table header", "long table cell",
}

HEADING_WORDS = re.compile(r"^(?:\d+(?:\.\d+)*\s+)?(?:what|why|how|when|which|where|who|is|are|do|does|can)\b", re.I)
HEADING_CONTRAST = re.compile(r"\bnot\b|\bvs\.?\b|\bversus\b|\?$", re.I)
GENERIC_BOX = re.compile(r"^(?:what can go wrong|if you read nothing else|heads up|gotcha)$", re.I)

SKIP_FILES = {"docs/matlab-vs-python.md"}
SKIP_PREFIXES = ("docs/api/", "docs/_build/", "docs/_")


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Lines of prose with code, inline code, link targets and directive syntax removed."""
    out = []
    in_code = False
    for i, raw in enumerate(text.splitlines(), 1):
        stripped = raw.lstrip()
        if stripped.startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        if re.match(r":{3,}(?:\{|\s*$)", stripped) and not re.match(r":{3,}\{(?:note|warning|tip|important|admonition)\}", stripped):
            continue
        if re.match(r":\w[\w-]*:", stripped) or stripped.startswith(("<!--", "---", "|-", "| -", "|:-")):
            continue
        line = re.sub(r"`[^`]*`", "`x`", raw)
        line = re.sub(r"\]\([^)]*\)", "]", line)
        line = re.sub(r"\{[a-z-]+\}`[^`]*`", "", line)
        out.append((i, line))
    return out


TABLE_CELL_WORDS = 35


def table_hits(text: str) -> dict[str, list[tuple[int, str]]]:
    """Tables with an empty header cell, and table cells longer than TABLE_CELL_WORDS words."""
    hits: dict[str, list[tuple[int, str]]] = defaultdict(list)
    lines = text.splitlines()
    in_code = False
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped.startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code or not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if re.fullmatch(r"\|?[\s:|-]+\|?", nxt) and "-" in nxt and any(not c for c in cells):
            hits["table header"].append((i + 1, "empty header cell"))
        for c in cells:
            n = len(re.sub(r"`[^`]*`", "x", c).split())
            if n > TABLE_CELL_WORDS and not re.fullmatch(r"[\s:|-]*", c):
                hits["long table cell"].append((i + 1, f"{n} words"))
                break
    return hits


def scan_page(text: str, docs: bool = True) -> tuple[int, dict[str, list[tuple[int, str]]]]:
    """(word count, family -> [(line, matched text)]) for one page or file."""
    words = 0
    hits: dict[str, list[tuple[int, str]]] = defaultdict(list)
    bold = 0
    for i, line in prose_lines(text):
        heading = re.match(r"(#{1,6})\s+(.*)", line)
        box = re.match(r":{3,}\{(?:note|warning|tip|important|admonition)\}\s*(.*)", line.strip())
        if heading:
            title = heading.group(2).strip()
            if HEADING_WORDS.match(title) or HEADING_CONTRAST.search(title):
                hits["heading form"].append((i, title))
        elif box:
            if GENERIC_BOX.match(box.group(1).strip()) or box.group(1).strip().endswith(("?", ".")):
                hits["box title"].append((i, box.group(1).strip()))
            continue
        else:
            words += len(line.split())
            bold += len(re.findall(r"\*\*[^*]+\*\*", line))
        for name, pat in FAMILIES.items():
            for m in pat.finditer(line):
                hits[name].append((i, m.group(0)))
    if docs:
        for name, found in table_hits(text).items():
            hits[name].extend(found)
    if words and bold * 1000 / words > 5:
        hits["bold"].append((0, f"{bold} bold spans in {words} words"))
    if not docs:
        hits = defaultdict(list, {k: v for k, v in hits.items() if k not in DOCS_ONLY})
    return words, hits


def docstrings(path: Path) -> list[str]:
    """Docstrings of a Python file or the leading help block of a MATLAB file."""
    import ast

    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix == ".py":
        out = []
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                doc = ast.get_docstring(node, clean=False)
                if doc:
                    out.append(doc)
        return out
    block: list[str] = []
    started = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("%"):
            started = True
            block.append(stripped.lstrip("%")[1:] if stripped.lstrip("%").startswith(" ") else stripped.lstrip("%"))
        elif started:
            break
    return ["\n".join(block)] if block else []


def site_pages(site: Path) -> list[Path]:
    pages = []
    for p in sorted((site / "docs").rglob("*.md")):
        rel = str(p.relative_to(site)).replace("\\", "/")
        if rel in SKIP_FILES or rel.startswith(SKIP_PREFIXES):
            continue
        pages.append(p)
    return pages


def run(site: Path, summary: bool = False, files: list[Path] | None = None) -> tuple[list[str], int]:
    lines: list[str] = []
    total_words = 0
    totals: Counter[str] = Counter()
    per_page: list[tuple[float, str, int, int]] = []
    findings = 0
    for p in files if files is not None else site_pages(site):
        rel = str(p.relative_to(site)).replace("\\", "/") if files is None else str(p)
        words, hits = scan_page(p.read_text(encoding="utf-8"), docs=files is None)
        total_words += words
        n = 0
        for name, found in hits.items():
            totals[name] += len(found)
            n += len(found)
            line_no, text = found[0]
            where = f"{rel}:{line_no}" if line_no else rel
            lines.append(f"S warning {where} {len(found)} x {name}: {text}")
            findings += 1
        if words:
            per_page.append((n * 1000 / words, rel, n, words))
    if summary:
        lines.append(f"\n{total_words} words of prose in {len(per_page)} pages")
        for name, count in totals.most_common():
            lines.append(f"  {count:5d}  {count * 1000 / max(total_words, 1):5.2f} per 1000 words  {name}")
        lines.append("\nPages by hits per 1000 words")
        for rate, rel, n, words in sorted(per_page, reverse=True)[:15]:
            lines.append(f"  {rate:5.1f}  {n:4d} hits  {words:6d} words  {rel}")
    return lines, findings


def run_docstrings(path: Path) -> tuple[list[str], int]:
    """Scan the docstrings of a Python file or the help block of a MATLAB file, general families only."""
    totals: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for doc in docstrings(path):
        _, hits = scan_page(doc, docs=False)
        for name, found in hits.items():
            totals[name].extend(found)
    lines = [f"S warning {path} {len(found)} x {name}: {found[0][1]}" for name, found in totals.items()]
    return lines, len(lines)


def main(argv: list[str]) -> int:
    args = argv[1:]
    summary = "--summary" in args
    strict = "--strict" in args
    args = [a for a in args if not a.startswith("--")] or ["."]
    findings = 0
    for arg in args:
        path = Path(arg).resolve()
        if path.is_file() and path.suffix in (".py", ".m"):
            lines, n = run_docstrings(path)
        elif path.is_file():
            lines, n = run(path.parent, summary, files=[path])
        elif (path / "docs").is_dir():
            lines, n = run(path, summary)
        else:
            print(f"{path} is neither a Markdown file nor a site with a docs/ folder", file=sys.stderr)
            return 2
        for line in lines:
            print(line)
        findings += n
    print(f"{findings} finding(s)")
    return 1 if strict and findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
