"""Verify the built document against its sources.  Runs no game, engine or model call.

Checks performed:
1. Every quotation in ``data/quote_manifest.json`` is re-read from the canonical
   ``decisions.jsonl`` by file hash, line and JSON pointer; the span text and the
   field hash must match.
2. Every quotation used in the manuscript appears in the text of the built PDF.
3. LaTeX log diagnostics (overfull boxes, undefined references, missing glyphs).
4. Page geometry: blank pages and text outside the page box.
5. Files frozen by ``baseline_hashes.json`` are unchanged.
6. Main-text prose word count, excluding quotations, tables, captions and references.
The results are written to ``qa/document_checks.json``.  They establish
correspondence between the document and the records, not the validity of any
interpretation.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[4]
QA = HERE / "qa"
QA.mkdir(exist_ok=True)
MAIN = ["introduction", "setting", "attention", "liquidity", "conversion", "default", "discussion"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return "".join(c.casefold() for c in text if c.isalnum())


def pointer(obj, ptr: str):
    for key in ptr.lstrip("/").split("/"):
        obj = obj[int(key)] if isinstance(obj, list) else obj[key]
    return obj


def check_quotes() -> dict:
    manifest = json.loads((HERE / "data/quote_manifest.json").read_text())["quotes"]
    cache: dict[str, list[bytes]] = {}
    hashes: dict[str, str] = {}
    out = []
    for q in manifest:
        path = REPO / q["source"]
        if q["source"] not in cache:
            raw = path.read_bytes()
            hashes[q["source"]] = hashlib.sha256(raw).hexdigest()
            cache[q["source"]] = raw.splitlines()
        assert hashes[q["source"]] == q["source_sha256"], q["id"]
        rec = json.loads(cache[q["source"]][q["jsonl_line_1based"] - 1])
        assert rec["phase"] == "decision_resolved"
        assert int(rec["decision_id"].rsplit("-", 1)[1]) == q["decision"], q["id"]
        field = pointer(rec, q["json_pointer"])
        assert hashlib.sha256(field.encode()).hexdigest() == q["field_sha256"], q["id"]
        for sp in q["spans"]:
            s, e = sp["span"]
            assert field[s:e] == sp["text"], q["id"]
        if q.get("full_field"):
            assert field.strip() == q["spans"][0]["text"], q["id"]
        out.append(q["id"])
    return {"quotes_rechecked_against_source": len(out), "source_files": len(hashes)}


def tex_sources() -> dict[str, str]:
    files = {name: (HERE / "sections" / f"{name}.tex").read_text() for name in MAIN + ["appendix"]}
    files["manuscript"] = (HERE / "manuscript.tex").read_text()
    return files


def used_quotes(files: dict[str, str]) -> tuple[list[str], list[str]]:
    text = "\n".join(files.values())
    return re.findall(r"\\TranscriptQuote\{([^}]+)\}", text), re.findall(r"\\InlineQuote\{([^}]+)\}", text)


def rendered_presence(cards: list[str], inline: list[str]) -> dict:
    manifest = {q["id"]: q for q in json.loads((HERE / "data/quote_manifest.json").read_text())["quotes"]}
    doc = pymupdf.open(HERE / "manuscript.pdf")
    pdf = norm("\n".join(p.get_text() for p in doc))
    missing = []
    for qid in cards + inline:
        assert qid in manifest, ("quote not in manifest", qid)
        for sp in manifest[qid]["spans"]:
            if norm(sp["text"]) not in pdf:
                missing.append(qid)
    unused = sorted(set(manifest) - set(cards) - set(inline))
    dup = sorted({q for q in cards if cards.count(q) > 1})
    assert not missing, missing
    return {"cards_used": len(cards), "inline_used": len(inline), "all_used_quotes_present_in_pdf": True, "manifest_quotes_not_used": unused, "cards_used_twice": dup}


def log_diagnostics() -> dict:
    log = (HERE / "build/manuscript.log").read_text(errors="replace")
    pat = ("Overfull", "Missing character", "undefined", "LaTeX Warning", "Package natbib Warning", "Undefined fact", "Undefined quote")
    lines = [line for line in log.splitlines() if any(t in line for t in pat)]
    return {"diagnostic_lines": lines}


def page_checks() -> dict:
    doc = pymupdf.open(HERE / "manuscript.pdf")
    blank, outside = [], []
    for n, page in enumerate(doc, 1):
        if len(page.get_text().strip()) < 30:
            blank.append(n)
        rect = page.rect
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    b = pymupdf.Rect(span["bbox"])
                    if b.x0 < rect.x0 + 20 or b.x1 > rect.x1 - 20 or b.y0 < rect.y0 + 15 or b.y1 > rect.y1 - 15:
                        if span["text"].strip():
                            outside.append([n, span["text"][:40]])
    return {"pages": doc.page_count, "blank_pages": blank, "text_near_page_edge": outside[:20], "pdf_sha256": sha(HERE / "manuscript.pdf")}


def frozen_files() -> dict:
    base = json.loads((HERE.parents[1] / "baseline_hashes.json").read_text())
    changed = [p for p, h in base.items() if not (REPO / p).exists() or sha(REPO / p) != h]
    return {"baseline_files": len(base), "changed": changed}


def strip_tex(s: str) -> str:
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\begin\{(table|figure|longtable|promptbox|tabular|tabularx)\}.*?\\end\{\1\}", " ", s, flags=re.S)
    s = re.sub(r"\\TranscriptQuote\{[^}]*\}", " ", s)
    s = re.sub(r"\\InlineQuote\{[^}]*\}", " ", s)
    s = re.sub(r"\\IncidentSource\{.*?\}\n", " ", s, flags=re.S)
    s = re.sub(r"\\(fact|ref|cite|label)\{[^}]*\}", " N ", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?", " ", s)
    s = re.sub(r"[{}$~\\]", " ", s)
    return s


def word_counts(files: dict[str, str]) -> dict:
    out = {}
    for name in MAIN:
        out[name] = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.\-]*", strip_tex(files[name])))
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", files["manuscript"], re.S).group(1)
    out["abstract"] = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.\-]*", strip_tex(abstract)))
    out["main_prose_total_excluding_abstract"] = sum(out[n] for n in MAIN)
    return out


def style_checks(files: dict[str, str]) -> dict:
    prose = "\n".join(strip_tex(files[n]) for n in MAIN + ["appendix"]) + strip_tex(files["manuscript"])
    return {
        "em_dashes_in_authored_prose": prose.count("—") + prose.count("---"),
        "incidents": len(re.findall(r"\\IncidentTitle", "\n".join(files[n] for n in MAIN))),
        "facts_cited": len(re.findall(r"\\fact\{", "\n".join(files.values()))),
    }


def main() -> None:
    files = tex_sources()
    cards, inline = used_quotes(files)
    report = {
        "quotes": check_quotes(),
        "rendered": rendered_presence(cards, inline),
        "log": log_diagnostics(),
        "pages": page_checks(),
        "frozen": frozen_files(),
        "words": word_counts(files),
        "style": style_checks(files),
        "scope": "Correspondence of the document to canonical records and build hygiene. Not a validation of interpretations.",
    }
    (QA / "document_checks.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    assert not report["log"]["diagnostic_lines"], "LaTeX diagnostics present"
    assert not report["pages"]["blank_pages"], "blank pages"
    assert not report["frozen"]["changed"], "frozen files changed"
    assert report["style"]["incidents"] == 8


if __name__ == "__main__":
    main()
