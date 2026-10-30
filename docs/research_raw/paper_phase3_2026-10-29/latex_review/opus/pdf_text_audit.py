"""Opus review check: does a rendered PDF preserve every source sentence?

Usage (from the repository root):
  uv run --with pymupdf python -I <this> <pdf> <source.md> [<source.md> ...] [--log <file.log>] [--out <json>]

The check compares sentences, not layout. Markdown links keep their text, emphasis markers
are removed, and both sides are reduced to lowercase alphanumerics. This makes the
comparison independent of hyphenation, line breaks, dashes and LaTeX quotes. A miss is a
candidate for manual inspection, not automatically a defect: a deliberate cross-reference
or an escaped symbol may differ from the source. Read-only; writes only the --out JSON.
"""

import argparse
import json
import re
import unicodedata
from pathlib import Path

import pymupdf

p = argparse.ArgumentParser()
p.add_argument("pdf", type=Path)
p.add_argument("sources", nargs="+", type=Path)
p.add_argument("--log", type=Path)
p.add_argument("--out", type=Path)
a = p.parse_args()


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    s = s.replace("τ", "tau")
    return re.sub(r"[^a-z0-9$%]", "", s)


def md_sentences(text: str) -> list[str]:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`#>|]", " ", text)
    out = []
    for block in re.split(r"\n\s*\n", text):
        block = " ".join(block.split())
        for s in re.split(r"(?<=[.!?:])\s+(?=[A-Z0-9\"“(\[])", block):
            if len(norm(s)) >= 12 and not set(s) <= set("-: |"):
                out.append(s)
    return out


doc = pymupdf.open(a.pdf)
pages = [pg.get_text() for pg in doc]
full = norm(" ".join(pages))
dollars_pdf = re.findall(r"\$\s?[0-9][0-9,]*", " ".join(pages))
report = {"pdf": str(a.pdf), "pages": len(doc), "sources": {}}
for src in a.sources:
    text = src.read_text(encoding="utf-8")
    sents = md_sentences(text)
    missing = [s for s in sents if norm(s) not in full]
    dollars_src = re.findall(r"\$[0-9][0-9,]*", text)
    report["sources"][str(src)] = {
        "sentences": len(sents),
        "missing": len(missing),
        "missing_sentences": missing,
        "dollar_amounts_in_source": len(dollars_src),
        "dollar_amounts_absent_from_pdf": sorted(
            {d for d in dollars_src if norm(d) not in full}
        ),
    }
report["dollar_tokens_in_pdf"] = len(dollars_pdf)
sizes = [
    s["size"]
    for pg in doc
    for b in pg.get_text("dict")["blocks"]
    if "lines" in b
    for ln in b["lines"]
    for s in ln["spans"]
    if s["text"].strip()
]
report["smallest_text_pt"] = min(sizes) if sizes else None
report["pages_with_replacement_char"] = [
    i + 1 for i, t in enumerate(pages) if "�" in t
]
if a.log:
    log = a.log.read_text(errors="replace")
    report["log"] = {
        "missing_character": sorted(set(re.findall(r"Missing character: There is no (\S+)", log))),
        "undefined_refs": len(re.findall(r"Reference `[^']+' on page \d+ undefined", log)),
        "undefined_citations": len(re.findall(r"Citation `[^']+' on page \d+ undefined", log)),
        "overfull_hbox": len(re.findall(r"Overfull \\hbox", log)),
        "overfull_over_1pt": len(
            [x for x in re.findall(r"Overfull \\hbox \(([0-9.]+)pt", log) if float(x) > 1]
        ),
        "underfull_hbox": len(re.findall(r"Underfull \\hbox", log)),
        "float_too_large": len(re.findall(r"Float too large", log)),
        "rerun": "Rerun to get" in log,
    }
summary = {
    k: (v["sentences"], v["missing"], v["dollar_amounts_absent_from_pdf"])
    for k, v in report["sources"].items()
}
print(json.dumps({"pages": len(doc), "summary": summary,
                  "smallest_text_pt": report["smallest_text_pt"],
                  "replacement_char_pages": report["pages_with_replacement_char"],
                  "log": report.get("log")}, indent=1))
if a.out:
    a.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
