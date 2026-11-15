"""Document/data correspondence checks. Does not execute agents or the engine."""
import hashlib
import json
import re
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
REPO = PACKAGE.parents[2]
manifest = json.loads((PACKAGE / "data/transcript_manifest.json").read_text())
fields = manifest["fields"]
quotes = {q["id"]: q for q in manifest["quotes"]}
used = re.findall(r"\\TranscriptQuote\{([^}]+)\}", (HERE/"conduct.tex").read_text())
assert len(used) == len(set(used))
sources = {}
for qid in used:
    for excerpt in quotes[qid]["excerpts"]:
        field = fields[excerpt["field_id"]]
        text = field["text"]
        assert hashlib.sha256(text.encode()).hexdigest() == field["field_sha256"]
        start, stop = excerpt["span"]
        assert text[start:stop] == excerpt["text"]
        path = REPO/field["source"]
        if path not in sources:
            raw = path.read_bytes()
            assert hashlib.sha256(raw).hexdigest() == field["source_sha256"]
            sources[path] = raw
        raw = sources[path]
        if field.get("jsonl_line_1based"):
            obj = json.loads(raw.splitlines()[field["jsonl_line_1based"]-1])
        else:
            obj = json.loads(raw)
        for key in field["json_pointer"].lstrip("/").split("/"):
            key = key.replace("~1", "/").replace("~0", "~")
            obj = obj[int(key)] if isinstance(obj, list) else obj[key]
        assert obj == text, qid
assert (HERE/"transcript_quotes.tex").read_bytes() == (PACKAGE/"sections/transcript_quotes.tex").read_bytes()
baseline = json.loads((PACKAGE/"baseline_source_hashes.json").read_text())
changed = [p for p,h in baseline.items() if hashlib.sha256((REPO/p).read_bytes()).hexdigest()!=h]
assert not changed, changed
log = (HERE/"build/manuscript.log").read_text()
bad = [line for line in log.splitlines() if any(s in line for s in
       ["Overfull", "Missing character", "undefined", "LaTeX Warning", "Package natbib Warning"])]
assert not bad, bad
doc = pymupdf.open(HERE/"manuscript.pdf")
outside = []
for pn,page in enumerate(doc,1):
    for b in page.get_text("dict")["blocks"]:
        for line in b.get("lines",[]):
            for span in line["spans"]:
                box = pymupdf.Rect(span["bbox"])
                if not page.rect.contains(box): outside.append([pn,span["text"]])
assert not outside, outside
pdftext = " ".join(p.get_text() for p in doc)
assert len(re.findall(r"Transcript \d+\.",pdftext)) == 7
report = {"scope":"Document and retained-source correspondence; no new engine or controlled evaluation",
          "pages":len(doc),"transcripts":7,"quote_cards_checked":len(used),
          "original_files_checked":len(sources),"protected_baseline_files":len(baseline),
          "baseline_mismatches":changed,"build_diagnostics":bad,"out_of_page_spans":outside,
          "pdf_sha256":hashlib.sha256((HERE/'manuscript.pdf').read_bytes()).hexdigest()}
(HERE/'qa/verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
