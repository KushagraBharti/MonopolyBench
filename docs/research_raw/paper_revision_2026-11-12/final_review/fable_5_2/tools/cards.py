"""Match every quotation card used in the integrated paper against its source field."""
import json, re
from lib import *

A = ["manuscript.tex"] + [f"sections/{n}.tex" for n in ("scientific_introduction", "study", "finance", "negotiation", "conduct", "interpretation", "supplement")]
body = " ".join((INT / a).read_text() for a in A)
used = re.findall(r"\\TranscriptQuote\{([^}]*)\}", body)
decl = {}
for f in ("transcript_quotes", "opus_quotes", "fable_quotes", "additional_quotes", "integration_quotes"):
    t = (INT / f"sections/{f}.tex").read_text()
    for m in re.finditer(r"\\DeclareTranscriptQuote\{([^}]*)\}\{([^}]*)\}\{((?:[^{}]|\{[^{}]*\})*)\}", t):
        decl[m.group(1)] = (m.group(2), m.group(3))


def detex(s):
    s = re.sub(r"\\textnormal\{\[\\ldots\]\}", "[...]", s)
    for a, b in (("\\$", "$"), ("\\char34{}", '"'), ("\\textasciitilde{}", "~"), ("\\%", "%"), ("\\&", "&"), ("\\_", "_"), ("\\#", "#"), ("\\{", "{"), ("\\}", "}")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", re.sub(r"\\par\b", " ", s)).strip()


out = []
for q in used:
    meta, text = decl[q]
    m = re.search(r"G(\d+) d(\d+)", meta)
    g, d = int(m.group(1)), int(m.group(2))
    _, rs = load(g)
    r = rs[d]
    fa = r.get("final_action") or {}
    if "private note" in meta:
        src = fa.get("private_thought") or ""
    elif "public message" in meta:
        src = fa.get("public_message") or ""
    elif "assistant content" in meta:
        src = r["attempts"][-1].get("assistant_content") or ""
    else:
        src = reasoning(r)
    src = re.sub(r"\s+", " ", src).strip()
    parts = [p.strip() for p in detex(text).split("[...]")]
    ok = all(p in src for p in parts)
    full = "full field" in meta
    out.append({"id": q, "meta": meta, "system_matches": who(r) in meta, "spans_found": ok, "labelled_full_field": full,
                "full_field_exact": (detex(text) == src) if full else None})
(HERE.parent / "data/cards.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(len(out), "cards used;", sum(o["spans_found"] for o in out), "found in source;", sum(o["system_matches"] for o in out), "with matching system;",
      sum(1 for o in out if o["labelled_full_field"]), "labelled full field, of which exact:", sum(1 for o in out if o["full_field_exact"]))
for o in out:
    if not o["spans_found"] or not o["system_matches"] or o["full_field_exact"] is False:
        print("CHECK", o)
