"""Verify every displayed quotation against its original record field.

For each \\TranscriptQuote used in the manuscript prose:
  1. load the original field (source file hash, JSONL line, JSON pointer, field hash);
  2. check that each manifest excerpt equals the field's span exactly;
  3. check that the label says "full field" exactly when the excerpt is the whole field;
  4. decode the TeX definition and compare it with the excerpt(s);
  5. check that the excerpt text is present in the rendered PDF.
For the four new G2 quotes, also check that each public message is present in
the counterparty's next delivered request (exposure, not belief).
Writes qa/quote_checks.json. No engine or model is called.
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


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKC", t)
    return "".join(c.casefold() for c in t if c.isalnum())


_cache = {}


def field_value(f):
    path = REPO / f["source"]
    if path not in _cache:
        _cache[path] = path.read_bytes()
    raw = _cache[path]
    assert hashlib.sha256(raw).hexdigest() == f["source_sha256"], path
    obj = json.loads(raw.splitlines()[f["jsonl_line_1based"] - 1]) if f.get("jsonl_line_1based") else json.loads(raw)
    for k in f["json_pointer"].lstrip("/").split("/"):
        k = k.replace("~1", "/").replace("~0", "~")
        obj = obj[int(k)] if isinstance(obj, list) else obj[k]
    assert hashlib.sha256(obj.encode()).hexdigest() == f["field_sha256"], f["json_pointer"]
    return obj


def tex_decode(s: str) -> str:
    s = s.replace(r"\textnormal{[\ldots]}", " ").replace(r"\textasciitilde{}", "~").replace(r"\char34{}", '"')
    s = s.replace(r"\par", " ").replace(r"\$", "$").replace(r"\_", "_").replace(r"\&", "&").replace(r"\%", "%")
    s = s.replace(r"\{", "{").replace(r"\}", "}").replace(r"\#", "#").replace(r"\^{}", "^")
    return s


def definitions():
    defs = {}
    for name in ("transcript_quotes.tex", "opus_quotes.tex", "fable_quotes.tex", "new_quotes.tex"):
        for line in (HERE / "sections" / name).read_text().splitlines():
            m = re.match(r"\\DeclareTranscriptQuote\{([^}]+)\}\{([^}]*)\}\{(.*)\}\s*$", line)
            if m:
                defs[m.group(1)] = (m.group(2), m.group(3), name)
    return defs


def manifests():
    q = {}
    tm = json.loads((HERE / "data/inherited/transcript_manifest.json").read_text())
    for x in tm["quotes"]:
        q[x["id"]] = [(tm["fields"][s["field_id"]], s["span"], s["text"]) for s in x["excerpts"]]
    for x in json.loads((HERE / "data/inherited/opus_quote_manifest.json").read_text())["quotes"]:
        q[x["id"]] = [(x, x["span_codepoints"], x["excerpt"])]
    for x in json.loads((HERE / "data/inherited/fable_quote_manifest.json").read_text())["quotes"]:
        q[x["id"]] = [(x, s["span"], s["text"]) for s in x["excerpts"]]
    for x in json.loads((HERE / "data/new_quote_manifest.json").read_text())["quotes"]:
        assert x["id"] not in q
        q[x["id"]] = [(x, x["span_codepoints"], x["excerpt"])]
    return q


def delivery_checks():
    """Check that each new G2 public message appears in the counterparty's next request."""
    path = REPO / "saved_games/railway-research-12-games-2026-10-25/game-02-102turns-270aabe8/run/decisions.jsonl"
    started = {}
    resolved = {}
    for line in path.read_text().splitlines():
        o = json.loads(line)
        idx = int(o["decision_id"].rsplit("-", 1)[1])
        (started if o["phase"] == "decision_started" else resolved)[idx] = o
    out = []
    for idx, recipient in ((119, "p3"), (120, "p1"), (121, "p3")):
        msg = resolved[idx]["final_action"]["public_message"]
        nxt = min(i for i, s in started.items() if i > idx and s["player_id"] == recipient)
        tl = started[nxt]["prompt_payload"]["game_state"]["memory"]["public_timeline_last_20"]
        present = any((e.get("message") or "") == msg for e in tl)
        out.append({"decision": idx, "recipient": recipient, "next_request_decision": nxt, "message_in_timeline": present})
    return out


def main():
    prose = "\n".join(p.read_text() for p in sorted((HERE / "sections").glob("*.tex"))
                      if p.name not in {"transcript_quotes.tex", "opus_quotes.tex", "fable_quotes.tex", "new_quotes.tex"})
    used = re.findall(r"\\TranscriptQuote\{([^}]+)\}", prose)
    assert len(used) == len(set(used)), "repeated quote card"
    titles = re.findall(r"\\TranscriptTitle\{([^}]+)\}", prose)
    defs, man = definitions(), manifests()
    pdf = pymupdf.open(HERE / "manuscript.pdf")
    pdf_norm = norm("\n".join(p.get_text() for p in pdf))
    results = []
    for qid in used:
        label, body, src = defs[qid]
        spans = man[qid]
        exact, full_any = True, False
        for f, (a, b), text in spans:
            val = field_value(f)
            exact &= val[a:b] == text
            full_any |= text.strip() == val.strip()
        label_ok = ("full field" in label) == (len(spans) == 1 and full_any)
        decoded_ok = norm(tex_decode(body)) == norm("".join(t for _, _, t in spans))
        rendered = all(norm(t) in pdf_norm for _, _, t in spans)
        results.append({"id": qid, "definition_file": src, "spans": len(spans), "exact_span": exact,
                        "label": label, "label_consistent": label_ok, "tex_matches_excerpt": decoded_ok, "rendered_in_pdf": rendered})
    report = {"scope": "Quotation correspondence only; no engine, game or model call.",
              "incident_titles": titles, "incident_count": len(titles), "quotes_checked": len(results),
              "all_exact": all(r["exact_span"] for r in results), "all_labels_consistent": all(r["label_consistent"] for r in results),
              "all_tex_match": all(r["tex_matches_excerpt"] for r in results), "all_rendered": all(r["rendered_in_pdf"] for r in results),
              "new_quote_delivery": delivery_checks(), "pdf_sha256": hashlib.sha256((HERE / "manuscript.pdf").read_bytes()).hexdigest(),
              "quotes": results}
    (HERE / "qa" / "quote_checks.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print(json.dumps({k: v for k, v in report.items() if k != "quotes"}, indent=1))
    bad = [r for r in results if not (r["exact_span"] and r["label_consistent"] and r["tex_matches_excerpt"] and r["rendered_in_pdf"])]
    for r in bad:
        print("PROBLEM", r)


if __name__ == "__main__":
    main()
