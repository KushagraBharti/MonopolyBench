"""Opus review check: does a LaTeX table snippet contain every value in its source CSV?

Usage: python3 -I table_fidelity.py <csv> <tex> [--ratio-cols c1,c2 --pct-cols c3 --dp 2 --pct-dp 1]

The check reads each data row of the snippet (split on \\\\ and &), strips LaTeX markup and
thousands separators, and matches it to a CSV row. Numeric CSV cells must appear as typed
values. Ratio and percent columns may be rounded; both half-even (Python format) and
half-up renderings are accepted, and the script reports which one was used. String cells
are compared case-insensitively after removing LaTeX escapes. Prints the unmatched rows
and cells; it is a detector for manual review, not a proof of semantic correctness.
"""
import argparse
import csv
import re
from decimal import ROUND_HALF_UP, Decimal

p = argparse.ArgumentParser()
p.add_argument("csv")
p.add_argument("tex")
p.add_argument("--ratio-cols", default="")
p.add_argument("--pct-cols", default="")
p.add_argument("--dp", type=int, default=2)
p.add_argument("--pct-dp", type=int, default=1)
p.add_argument("--skip-cols", default="")
a = p.parse_args()
ratio = set(filter(None, a.ratio_cols.split(",")))
pct = set(filter(None, a.pct_cols.split(",")))
skip = set(filter(None, a.skip_cols.split(",")))
rows = list(csv.DictReader(open(a.csv, newline="")))
tex = open(a.tex, encoding="utf-8").read()
tex = re.sub(r"(?<!\\)%.*", "", tex)


def clean(cell: str) -> str:
    c = re.sub(r"\\(num|text\w*|emph|mbox|makecell|multicolumn\{\d+\}\{[^}]*\}|path|detokenize)", "", cell)
    c = re.sub(r"\\(,|thinspace|\$|_|%|&)", lambda m: {"\\_": "_", "\\%": "%", "\\&": "&"}.get(m.group(0), ""), c)
    c = re.sub(r"\\[a-zA-Z]+\*?(\[[^]]*\])?", " ", c)
    c = re.sub(r"[{}~$]", " ", c)
    return " ".join(c.split()).replace(",", "")


body = []
for raw in re.split(r"\\\\", tex):
    cells = [clean(x) for x in raw.split("&")]
    if len(cells) >= 2:
        body.append(cells)


def renderings(col: str, val: str) -> dict[str, str]:
    if col in pct:
        d = Decimal(val) * 100
        q = Decimal(1).scaleb(-a.pct_dp)
        return {"half_even": f"{float(val) * 100:.{a.pct_dp}f}", "half_up": str(d.quantize(q, ROUND_HALF_UP))}
    if col in ratio:
        q = Decimal(1).scaleb(-a.dp)
        return {"half_even": f"{float(val):.{a.dp}f}", "half_up": str(Decimal(val).quantize(q, ROUND_HALF_UP))}
    return {"exact": val}


bool_map = {"true": {"yes", "true", "✓", "y"}, "false": {"no", "false", "", "—", "n"}}
unmatched_rows, rule_hits = [], {}
for r in rows:
    best, best_miss = None, None
    for cells in body:
        flat = [x.lower() for x in cells]
        miss = []
        for col, val in r.items():
            if col in skip or val is None:
                continue
            opts = renderings(col, val)
            if val.lower() in bool_map:
                ok = any(f in bool_map[val.lower()] for f in flat)
            else:
                ok = any(o.lower() in flat or any(o.lower() == t for f in flat for t in f.split()) for o in opts.values())
            if not ok:
                miss.append(f"{col}={val}")
            elif len(opts) > 1:
                for name, o in opts.items():
                    if any(o == f or o in f.split() for f in flat):
                        rule_hits[name] = rule_hits.get(name, 0) + 1
        if best_miss is None or len(miss) < len(best_miss):
            best, best_miss = cells, miss
    if best_miss:
        unmatched_rows.append((dict(r), best_miss, best))
print(f"{a.csv}: {len(rows)} CSV rows, {len(body)} snippet rows; rows with unmatched cells: {len(unmatched_rows)}")
print("rounding-rule hits:", rule_hits)
for r, miss, cells in unmatched_rows[:12]:
    print("  MISS", miss, "| nearest snippet row:", cells[:8])
