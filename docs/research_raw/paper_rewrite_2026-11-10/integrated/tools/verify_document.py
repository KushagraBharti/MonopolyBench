"""Verify presentation and source correspondence, without executing gameplay."""

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw
from prepare_quote_labels import FULL_FIELDS, FULL_FIELDS_BY_FILE, relabel

HERE = Path(__file__).resolve().parents[1]
BASE = HERE.parent
REPO = BASE.parents[2]
QA = HERE / "qa"
QA.mkdir(exist_ok=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text):
    text = unicodedata.normalize("NFKC", text)
    # Compare words and numbers across PDF line wrapping and typography.
    return "".join(c.casefold() for c in text if c.isalnum())


sources = {}


def original_field(field):
    path = REPO / field["source"]
    if path not in sources:
        raw = path.read_bytes()
        sources[path] = raw
    raw = sources[path]
    assert hashlib.sha256(raw).hexdigest() == field["source_sha256"], path
    if field.get("jsonl_line_1based"):
        obj = json.loads(raw.splitlines()[field["jsonl_line_1based"] - 1])
    else:
        obj = json.loads(raw)
    for key in field["json_pointer"].lstrip("/").split("/"):
        key = key.replace("~1", "/").replace("~0", "~")
        obj = obj[int(key)] if isinstance(obj, list) else obj[key]
    assert hashlib.sha256(obj.encode()).hexdigest() == field["field_sha256"]
    return obj


sections = [p for p in sorted((HERE / "sections").glob("*.tex"))
            if p.name not in {"transcript_quotes.tex", "opus_quotes.tex", "fable_quotes.tex"}]
prose = "\n".join(p.read_text() for p in sections)
used = re.findall(r"\\TranscriptQuote\{([^}]+)\}", prose)
assert len(used) == len(set(used)), "Repeated quote cards"
cards = re.findall(r"\\TranscriptTitle\{([^}]+)\}", prose)
assert len(cards) == 8, cards
quote_map = {}
manifest = json.loads((HERE / "data/transcript_manifest.json").read_text())
for q in manifest["quotes"]:
    quote_map[q["id"]] = [(manifest["fields"][s["field_id"]], s["span"], s["text"])
                           for s in q["excerpts"]]
for q in json.loads((HERE / "data/opus_quote_manifest.json").read_text())["quotes"]:
    assert q["id"] not in quote_map
    quote_map[q["id"]] = [(q, q["span_codepoints"], q["excerpt"])]
for q in json.loads((HERE / "data/fable_quote_manifest.json").read_text())["quotes"]:
    assert q["id"] not in quote_map
    quote_map[q["id"]] = [(q, s["span"], s["text"]) for s in q["excerpts"]]

for qid in FULL_FIELDS:
    spans = quote_map[qid]
    assert len(spans) == 1
    field, (start, stop), excerpt = spans[0]
    actual = original_field(field)
    assert excerpt.strip() == actual.strip(), qid

doc = pymupdf.open(HERE / "manuscript.pdf")
pdftext = "\n".join(p.get_text() for p in doc)
normalized_pdf = normalize(pdftext)
checked_quotes = []
for qid in used:
    spans = quote_map[qid]
    for field, (start, stop), excerpt in spans:
        actual = original_field(field)
        assert actual[start:stop] == excerpt, qid
        assert normalize(excerpt) in normalized_pdf, ("Missing rendered quote", qid)
        if qid in FULL_FIELDS:
            assert excerpt.strip() == actual.strip(), ("Not a full field", qid)
    checked_quotes.append({"id": qid, "exact_original_spans": len(spans),
                           "rendered_excerpt_present": True})

protected = json.loads((BASE / "baseline_source_hashes.json").read_text())
changed = [p for p, h in protected.items() if sha(REPO / p) != h]
assert not changed, changed
frozen = json.loads((BASE / "reviews/astra/review_source_hashes.json").read_text())
# The root review froze all four independent manuscript packages before integration.
assert isinstance(frozen, dict)
frozen_checks = 0
for p, h in frozen.items():
    if not isinstance(h, str):
        continue
    candidate = REPO / p
    if not candidate.exists():
        candidate = BASE / p
    assert candidate.exists(), p
    assert sha(candidate) == h, p
    frozen_checks += 1

log = (HERE / "build/manuscript.log").read_text()
diagnostics = [line for line in log.splitlines() if any(term in line for term in
               ("Overfull", "Missing character", "undefined", "LaTeX Warning", "Package natbib Warning"))]
assert not diagnostics, diagnostics
outside, launches, blank_pages = [], [], []
for pn, page in enumerate(doc, 1):
    if len(page.get_text().strip()) < 30:
        blank_pages.append(pn)
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                box = pymupdf.Rect(span["bbox"]) * page.rotation_matrix
                if not page.rect.contains(box):
                    outside.append([pn, span["text"]])
    for link in page.get_links():
        if link["kind"] == pymupdf.LINK_LAUNCH:
            launches.append([pn, link])
assert not outside, outside
assert not launches, launches
assert not blank_pages, blank_pages

for leaf, item in json.loads((HERE / "source_manifest.json").read_text()).items():
    assert sha(BASE / item["source"]) == item["sha256"], item["source"]
    if leaf in FULL_FIELDS_BY_FILE:
        assert (HERE / leaf).read_text() == relabel(
            (BASE / item["source"]).read_text(), FULL_FIELDS_BY_FILE[leaf])
    elif leaf == "references.bib":
        # Prefer the inspected paper-body title; the abstract metadata is singular.
        expected = (BASE / item["source"]).read_text().replace(
            "title = {{A Unified Arena for LLM Agents across Diverse Eurogame}},",
            "title = {{A Unified Arena for LLM Agents across Diverse Eurogames}},")
        assert (HERE / leaf).read_text() == expected
    elif leaf not in {"preamble.tex", "supplemental.bib"}:
        assert sha(HERE / leaf) == item["sha256"], leaf

renders = QA / "render"
renders.mkdir(exist_ok=True)
for first in range(0, len(doc), 6):
    sheet = Image.new("RGB", (1260, 1800), "#dddddd")
    draw = ImageDraw.Draw(sheet)
    for offset in range(6):
        index = first + offset
        if index >= len(doc):
            break
        pix = doc[index].get_pixmap(matrix=pymupdf.Matrix(0.6, 0.6), alpha=False)
        pic = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        pic.thumbnail((400, 840))
        x, y = (offset % 3) * 420, (offset // 3) * 900
        draw.text((x + 8, y + 8), f"Page {index + 1}", fill="black")
        sheet.paste(pic, (x + 8, y + 30))
    sheet.save(renders / f"contact_{first+1:02d}_{min(first+6,len(doc)):02d}.png")

(QA / "manuscript_text.txt").write_text(pdftext)
report = {
    "scope": "Document and original-source correspondence. No model, engine, game or controlled evaluation executed.",
    "pages": len(doc), "main_incidents": cards, "quote_cards_checked": len(used),
    "quote_span_count": sum(len(quote_map[q]) for q in used),
    "original_files_checked": len(sources), "protected_baseline_files": len(protected),
    "frozen_draft_files_checked": frozen_checks, "changed_protected_files": changed,
    "diagnostics": diagnostics, "outside_text_spans": outside,
    "launch_actions": launches, "blank_pages": blank_pages,
    "quotes": checked_quotes, "pdf_sha256": sha(HERE / "manuscript.pdf"),
    "script_sha256": sha(Path(__file__)),
}
(QA / "document_checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "quotes"}, indent=2))
