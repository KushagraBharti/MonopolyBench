"""Verify the built document against its sources.  Runs no game, engine or model call.

1. Every quotation in ``data/quote_manifest.json`` is re-read from the canonical
   ``decisions.jsonl`` by file hash, line and JSON pointer; span text and field
   hash must match.
2. Every quotation used in the manuscript appears in the text of the built PDF.
3. LaTeX log diagnostics (overfull boxes, undefined references, missing glyphs).
4. Page checks: blank pages and text near the page edge.
5. Frozen inputs: the files listed in ``../../baseline_manifest.json`` are unchanged,
   and git reports no change under the tracked engine, prompt, contract and
   saved-game paths.
6. Main-text word count, excluding the abstract, quotations, tables, captions,
   source notes, references and appendices.
7. Every ``\\fact{}`` key used exists; numbers typed directly into prose are listed
   for inspection.
Results go to ``qa/document_checks.json``.  They establish correspondence between
the document and the records.  They do not validate any interpretation.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[4]
QA = HERE / "qa"
QA.mkdir(exist_ok=True)
MAIN = ["introduction", "setting", "own", "rival", "talk", "discussion"]


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
    cache, hashes, n = {}, {}, 0
    for q in manifest:
        if q["source"] not in cache:
            raw = (REPO / q["source"]).read_bytes()
            hashes[q["source"]] = hashlib.sha256(raw).hexdigest()
            cache[q["source"]] = raw.splitlines()
        assert hashes[q["source"]] == q["source_sha256"], q["id"]
        rec = json.loads(cache[q["source"]][q["jsonl_line_1based"] - 1])
        assert rec["phase"] == "decision_resolved" and int(rec["decision_id"].rsplit("-", 1)[1]) == q["decision"], q["id"]
        field = pointer(rec, q["json_pointer"])
        assert hashlib.sha256(field.encode()).hexdigest() == q["field_sha256"], q["id"]
        for sp in q["spans"]:
            s, e = sp["span"]
            assert field[s:e] == sp["text"], q["id"]
        if q.get("full_field"):
            assert field.strip() == q["spans"][0]["text"], q["id"]
        n += 1
    delivered = [q for q in manifest if q.get("delivered_to")]
    return {"quotes_rechecked_against_source": n, "source_files": len(hashes),
            "public_messages_with_receipt_check": len(delivered),
            "all_found_in_recipient_prompt": all(q["first_recipient_prompt_containing_message"] is not None for q in delivered)}


def tex_sources() -> dict[str, str]:
    files = {name: (HERE / "sections" / f"{name}.tex").read_text() for name in MAIN + ["appendix"]}
    files["manuscript"] = (HERE / "manuscript.tex").read_text()
    files["tables"] = (HERE / "sections" / "tables.tex").read_text()
    return files


def rendered_presence(files) -> dict:
    text = "\n".join(files.values())
    cards = re.findall(r"\\TranscriptQuote\{([^}]+)\}", text)
    inline = re.findall(r"\\InlineQuote\{([^}]+)\}", text)
    manifest = {q["id"]: q for q in json.loads((HERE / "data/quote_manifest.json").read_text())["quotes"]}
    doc = pymupdf.open(HERE / "manuscript.pdf")
    pdf = norm("\n".join(p.get_text() for p in doc))
    missing, split = [], []
    for qid in cards + inline:
        for sp in manifest[qid]["spans"]:
            t = norm(sp["text"])
            if t in pdf:
                continue
            # a quotation that runs across a page break or around a float is extracted in two pieces
            ok = any(t[:i] in pdf and t[i:] in pdf for i in range(8, len(t) - 8))
            (split if ok else missing).append(qid)
    assert not missing, missing
    return {"cards_used": len(cards), "inline_used": len(set(inline)), "all_used_quotes_present_in_pdf": True,
            "quotes_found_in_two_pieces_across_a_page_or_float": sorted(set(split)),
            "manifest_quotes_not_used": sorted(set(manifest) - set(cards) - set(inline)),
            "cards_used_twice": sorted({q for q in cards if cards.count(q) > 1})}


def log_diagnostics() -> dict:
    log = (HERE / "build/manuscript.log").read_text(errors="replace")
    pat = ("Overfull", "Missing character", "undefined", "LaTeX Warning", "Package natbib Warning", "Undefined fact", "Undefined quote")
    return {"diagnostic_lines": [line for line in log.splitlines() if any(t in line for t in pat)]}


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
                    if (b.x0 < rect.x0 + 20 or b.x1 > rect.x1 - 20 or b.y0 < rect.y0 + 15 or b.y1 > rect.y1 - 15) and span["text"].strip():
                        outside.append([n, span["text"][:40]])
    sizes = sorted({round(s["size"], 1) for p in doc for b in p.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"] if s["text"].strip()})
    first_ref = next((n for n, p in enumerate(doc, 1) if "References" in p.get_text()), None)
    return {"pages": doc.page_count, "blank_pages": blank, "text_near_page_edge": outside[:20],
            "smallest_font_pt": sizes[0], "references_start_page": first_ref, "pdf_sha256": sha(HERE / "manuscript.pdf")}


def frozen() -> dict:
    base = json.loads((HERE.parents[1] / "baseline_manifest.json").read_text())
    changed = [p for p, h in base.items() if not (REPO / p).exists() or sha(REPO / p) != h]
    git = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "--", "saved_games", "contracts", "python", "frontend", "scripts"],
                         capture_output=True, text=True, check=True).stdout.strip().splitlines()
    four = json.loads((HERE.parents[2] / "paper_revision_2026-11-11" / "four_draft_hashes.json").read_text()) if (HERE.parents[2] / "paper_revision_2026-11-11" / "four_draft_hashes.json").exists() else {}
    return {"baseline_manifest_sha256": sha(HERE.parents[1] / "baseline_manifest.json"), "baseline_files": len(base), "baseline_changed": changed,
            "git_changes_under_tracked_engine_prompt_contract_and_saved_game_paths": git}


def strip_tex(s: str) -> str:
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\begin\{(table|figure|longtable|promptbox|tabular|tabularx)\}.*?\\end\{\1\}", " ", s, flags=re.S)
    s = re.sub(r"\\TranscriptQuote\{[^}]*\}", " ", s)
    s = re.sub(r"\\InlineQuote\{[^}]*\}", " ", s)
    s = re.sub(r"\\IncidentSource\{.*?\}\n", " ", s, flags=re.S)
    s = re.sub(r"\\(fact|ref|cite|label|input)\{[^}]*\}", " N ", s)
    s = re.sub(r"\\IncidentTitle\{[^}]*\}", " ", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?", " ", s)
    s = re.sub(r"[{}$~\\]", " ", s)
    return s


WORD = r"[A-Za-z0-9][A-Za-z0-9'’.,\-]*"


def word_counts(files) -> dict:
    out = {name: len(re.findall(WORD, strip_tex(files[name]))) for name in MAIN}
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", files["manuscript"], re.S).group(1)
    out["abstract"] = len(re.findall(WORD, strip_tex(abstract)))
    out["main_prose_total_excluding_abstract"] = sum(out[n] for n in MAIN)
    out["appendix_prose"] = len(re.findall(WORD, strip_tex(files["appendix"])))
    out["method"] = "authored prose in the six main section files; excludes abstract, quotation cards and inline quotations, tables, figure and table captions, incident source notes, references and appendices"
    return out


def fact_checks(files) -> dict:
    facts = json.loads((HERE / "data/facts.json").read_text())
    used = re.findall(r"\\fact\{([^}]+)\}", "\n".join(files[n] for n in MAIN + ["appendix", "manuscript"]))
    missing = sorted({k for k in used if k not in facts})
    assert not missing, missing
    typed = {}
    for name in MAIN + ["appendix"]:
        body = re.sub(r"\\(fact|ref|cite|label|input|TranscriptQuote|InlineQuote|includegraphics|path|url|texttt)\{[^}]*\}", " ", files[name])
        body = re.sub(r"(?<!\\)%.*", "", body)
        typed[name] = len(re.findall(r"(?<![A-Za-z])\d[\d,]*(?:\.\d+)?", body))
    return {"fact_citations": len(used), "distinct_fact_keys": len(set(used)), "undefined_fact_keys": missing,
            "numbers_typed_directly_by_file": typed,
            "note": "numbers typed directly are incident amounts, turn and decision indexes, seeds and definitions; each incident amount is asserted in analysis/b5_incidents.py"}


def style_checks(files) -> dict:
    authored = "\n".join(files[n] for n in MAIN + ["appendix"]) + files["manuscript"]
    authored = re.sub(r"(?<!\\)%.*", "", authored)
    return {"em_dashes_in_authored_source": authored.count("—") + authored.count("---"),
            "incidents_main": len(re.findall(r"\\IncidentTitle", "\n".join(files[n] for n in MAIN))),
            "incidents_appendix": len(re.findall(r"\\IncidentTitle", files["appendix"]))}


def main() -> None:
    files = tex_sources()
    report = {"quotes": check_quotes(), "rendered": rendered_presence(files), "log": log_diagnostics(), "pages": page_checks(),
              "frozen": frozen(), "words": word_counts(files), "facts": fact_checks(files), "style": style_checks(files),
              "scope": "Correspondence of the document to canonical records and build hygiene. Not a validation of interpretations."}
    (QA / "document_checks.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    assert not report["log"]["diagnostic_lines"], "LaTeX diagnostics present"
    assert not report["pages"]["blank_pages"], "blank pages"
    assert not report["frozen"]["baseline_changed"], "baseline files changed"
    assert not report["frozen"]["git_changes_under_tracked_engine_prompt_contract_and_saved_game_paths"], "tracked artifacts changed"
    assert report["style"]["incidents_main"] + report["style"]["incidents_appendix"] == 8
    assert report["style"]["em_dashes_in_authored_source"] == 0


if __name__ == "__main__":
    main()
