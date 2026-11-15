"""Check the built PDF against the data: quotations, key numbers, references.

Reads manuscript.pdf, build/manuscript.log, sections/*.tex and data/*.json.
Writes qa/verification.json. Exits non-zero on any failure.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

D = Path(__file__).resolve().parents[1]
pdf = pymupdf.open(D / "manuscript.pdf")
pages = [p.get_text() for p in pdf]
text = "\n".join(pages)


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")
    s = s.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'").replace("\u2018", "'")
    s = re.sub(r"-\n", "", s)  # soft hyphenation at line ends
    return re.sub(r"\s+", "", s)


NT = norm(text)
fails: list[str] = []
out: dict = {"pages": pdf.page_count}

# ---------------------------------------------------------------- displayed quotations
src = "\n".join((D / f"sections/{n}.tex").read_text() for n in
                ("introduction", "design", "finance", "bargaining", "conduct", "discussion", "appendix"))
used_cards = set(re.findall(r"\\TranscriptQuote\{([^}]+)\}", src))
used_inline = set(re.findall(r"\\InlineQuote\{([^}]+)\}", src))
manifest = json.loads((D / "data/quote_manifest.json").read_text())["quotes"]
by_id = {q["id"]: q for q in manifest}
reading = {f"nec-g{r['game']}-d{r['decision']}": r["span"]
           for r in json.loads((D / "data/necessary_text_reading.json").read_text())["rows"]}
checked = 0
for qid in sorted(used_cards | used_inline):
    if qid in reading:
        parts = [reading[qid]]
    else:
        base = qid[:-7] if qid.endswith("-inline") else qid
        if base not in by_id:
            fails.append(f"unknown quotation id {qid}")
            continue
        parts = by_id[base]["text"].split(" [...] ")
    for part in parts:
        if norm(part) not in NT:
            fails.append(f"quotation not found in PDF text: {qid}: {part[:60]}")
    checked += 1
out["quotations_checked_in_pdf"] = checked
out["cards"] = len(used_cards)
out["inline_quotes"] = len(used_inline)
out["manifest_quotes_verified_against_records"] = len(manifest)

# ---------------------------------------------------------------- key numbers tied to data
O = json.loads((D / "data/offers_analysis.json").read_text())
F = json.loads((D / "data/finance_analysis.json").read_text())
P = json.loads((D / "data/provenance.json").read_text())
cv = O["composition_versions"]
rs = O["resampling"]
expect = []
for ver in cv:
    for f in ("swap", "cash_bid"):
        a, b = cv[ver][f]["proposer_only"], cv[ver][f]["neither"]
        expect += [f"{a['R']}/{a['n']}", f"{b['R']}/{b['n']}"]
expect += [f"{cv['all']['swap']['gap_pp']:.1f}", f"{cv['without_grok_authored']['swap']['gap_pp']:.1f}",
           f"{cv['without_conflicting_grok_openings']['swap']['gap_pp']:.1f}"]
for ver in rs:
    for f in rs[ver]:
        t = rs[ver][f]["two_stage"]
        expect += [f"{t['p2.5']:+.1f}", f"{t['p97.5']:+.1f}"]
std = O["swap_gap_standardised_by_proposer"]
expect += [f"{std['proposer_only']:.1f}", f"{std['neither']:.1f}"]
sp = O["semantic_population"]
expect += [f"{sp['rival_consequence_agreed']} of the {sp['rows']}", "34 of 48", "29 of 45"]
expect += [f"{F['paid']} of the {F['episodes']}", "128 of 131", "Sixty-seven payments" if F["paid_one_action"] == 67 else "MISMATCH",
           f"{round(100 * F['median_debt_to_bound_paid'])}\\%".replace("\\", ""), "\\$51,997".replace("\\", "")]
expect += [str(s) for s in P["seeds_in_block_order"]]
expect += ["50,918", "24,506", "1,604", "1,068", "139", "2,054", "6,989", "8,679"]
missing = [e for e in expect if norm(e) not in NT]
out["numbers_checked"] = len(expect)
if missing:
    fails.append(f"numbers not found in PDF: {missing}")

# ---------------------------------------------------------------- data invariants restated in prose
assert F["tiers"] == {"A": {"episodes": 62, "paid": 62}, "B": {"episodes": 53, "paid": 52}, "N": {"episodes": 16, "paid": 14}}
assert P["necessary_reading"]["paid_by_category"] == {"explicit": 13, "open_check": 1}
assert P["necessary_reading"]["paid_by_channel"] == {"note": 9, "provider": 5}
assert P["replay_totals"]["artifact_passed"] == 20 and P["replay_totals"]["state_passed"] == 20
assert P["g18_inheritance_terms_found"] == []

# ---------------------------------------------------------------- build log
log = (D / "build/manuscript.log").read_text(errors="replace")
warn = re.findall(r"(LaTeX Warning:.*|Overfull \\hbox.*|Missing character.*|undefined)", log)
out["log_warnings"] = warn
if warn:
    fails.append(f"build log warnings: {warn[:5]}")
for bad in ("??", "[?]"):
    if bad in text:
        fails.append(f"unresolved marker {bad!r} in PDF text")
out["failures"] = fails
(D / "qa/verification.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "log_warnings"}, indent=1, ensure_ascii=False))
sys.exit(1 if fails else 0)
