"""Check that every quotation card used in replacement_prose.tex appears in the rendered PDF text.
Run from repo root with a Python that has PyMuPDF:
  /tmp/monopoly-astra-rewrite-venv/bin/python -I docs/research_raw/paper_revision_2026-11-11/reviews/opus/tools/check_render.py"""
import json, pathlib, re, fitz
REV = pathlib.Path("docs/research_raw/paper_revision_2026-11-11"); O = REV / "reviews/opus"
def norm(s):
    for a, b in [("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u00ad", ""), ("\ufb01", "fi"), ("\ufb02", "fl"), ("\u2013", "-"), ("\u2014", "-")]:
        s = s.replace(a, b)
    s = re.sub(r"-\s*\n\s*", "-", s); return re.sub(r"\s+", " ", s).strip()
T = norm(" ".join(p.get_text() for p in fitz.open(O / "replacement_prose.pdf"))); Tn = T.replace("- ", "-")
fab = {q["id"]: q for q in json.loads((REV / "full_drafts/fable_5_2/data/quote_manifest.json").read_text())["quotes"]}
opus = json.loads((REV / "full_drafts/opus/data/new_quote_manifest.json").read_text())
opus = {q["id"]: q for q in (opus if isinstance(opus, list) else opus.get("quotes", [])) if isinstance(q, dict)}
used = sorted(set(re.findall(r"\\Q\{([^}]+)\}", (O / "replacement_prose.tex").read_text())))
res = {}
for qid in used:
    spans = [opus[qid]["excerpt"]] if qid in opus and qid not in fab else [s["text"] for s in fab[qid]["spans"]]
    res[qid] = all(norm(s) in T or norm(s).replace("- ", "-") in Tn for s in spans)
out = {"pdf": "reviews/opus/replacement_prose.pdf", "quotes_checked": len(used), "missing": [k for k, v in res.items() if not v], "per_quote": res}
(O / "data/replacement_quote_render_check.json").write_text(json.dumps(out, indent=1)); print(out["quotes_checked"], out["missing"])
