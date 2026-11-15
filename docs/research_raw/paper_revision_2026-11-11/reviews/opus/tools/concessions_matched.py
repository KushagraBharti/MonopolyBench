"""Reproduce the 199 cash concessions and re-split the comparison cell by whether the offer requests a deed.
Concession: an author's offer whose non-cash terms equal that author's previous offer in the same thread and whose
net cash to the recipient is larger. Existing-record arithmetic on the frozen 920-row rebuild. Run with python3 -I from repo root."""
import collections, json, pathlib, hashlib
ROOT = pathlib.Path.cwd(); REV = ROOT / "docs/research_raw/paper_revision_2026-11-11"
src = REV / "full_drafts/opus/data/offers_rebuilt.json"; offers = json.loads(src.read_text())
by_thread = collections.defaultdict(list)
for r in offers: by_thread[(r["game"], r["thread"])].append(r)
nonc = lambda r: (tuple(sorted(r["author_gives"]["properties"])), r["author_gives"].get("jail", 0),
                  tuple(sorted(r["author_asks"]["properties"])), r["author_asks"].get("jail", 0))
net = lambda r: r["author_gives"]["cash"] - r["author_asks"]["cash"]
conc = []
for k, rows in by_thread.items():
    rows.sort(key=lambda r: r["stage"])
    for i, r in enumerate(rows):
        prev = [p for p in rows[:i] if p["author"] == r["author"]]
        if prev and nonc(prev[-1]) == nonc(r) and net(r) > net(prev[-1]) and r["accept_legal"]:
            conc.append(r)
R = lambda r: r["response"].split("_")[0]
def t(rows):
    c = collections.Counter(R(r) for r in rows); return f'{c["accept"]}/{len(rows)} accepted, {c["counter"]} countered, {c["reject"]} rejected'
out = {"source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(), "n_concessions": len(conc),
       "by_cell": {c: t([r for r in conc if r["cell"] == c]) for c in ("Author only", "Recipient only", "Both", "Neither")},
       "neither_requests_deed": t([r for r in conc if r["cell"] == "Neither" and r["author_asks"]["properties"]]),
       "neither_no_deed_request": t([r for r in conc if r["cell"] == "Neither" and not r["author_asks"]["properties"]]),
       "author_only_no_opus_recipient": t([r for r in conc if r["cell"] == "Author only" and r["recipient_model"] != "Opus"]),
       "neither_requests_deed_no_opus_recipient": t([r for r in conc if r["cell"] == "Neither" and r["author_asks"]["properties"] and r["recipient_model"] != "Opus"]),
       "threads": {c: len({(r["game"], r["thread"]) for r in conc if r["cell"] == c}) for c in ("Author only", "Neither")}}
p = REV / "reviews/opus/data/concessions_matched.json"; p.write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
