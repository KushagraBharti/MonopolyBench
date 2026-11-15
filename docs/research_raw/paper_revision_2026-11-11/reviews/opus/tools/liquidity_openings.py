"""Opening-offer liquidity checks. Existing-record arithmetic on the frozen 920-row offer rebuild.
Run from repo root: python3 -I docs/research_raw/paper_revision_2026-11-11/reviews/opus/tools/liquidity_openings.py"""
import collections, json, pathlib, hashlib, statistics
ROOT = pathlib.Path.cwd(); REV = ROOT / "docs/research_raw/paper_revision_2026-11-11"
src = REV / "full_drafts/opus/data/offers_rebuilt.json"
offers = json.loads(src.read_text())
legal = [r for r in offers if r["accept_legal"]]
asks_deed = lambda r: len(r["author_asks"]["properties"]) > 0
R = lambda r: r["response"].split("_")[0]
band = lambda c: "lt100" if c < 100 else ("100-299" if c < 300 else "300plus")
out = {"source": str(src.relative_to(ROOT)), "sha256": hashlib.sha256(src.read_bytes()).hexdigest()}
def cell(rows):
    c = collections.Counter(R(r) for r in rows); n = len(rows)
    return {"n": n, "reject": c["reject"], "counter": c["counter"], "accept": c["accept"], "reject_pct": round(100*c["reject"]/n,1) if n else None}
res = {}
for scope in ("All", "All_but_Opus", "Sol", "Gemini", "Grok", "Opus"):
    sel = lambda r: scope == "All" or (scope == "All_but_Opus" and r["recipient_model"] != "Opus") or r["recipient_model"] == scope
    for st in ("opening", "later"):
        rows = [r for r in legal if sel(r) and r["opening"] == (st == "opening") and asks_deed(r)]
        for bd in ("lt100", "100-299", "300plus"):
            res[f"{scope}|{st}|{bd}"] = {"completion_request": cell([r for r in rows if r["cell"] == "Author only" and band(r["recipient_cash"]) == bd]),
                                        "other_deed_request": cell([r for r in rows if r["cell"] == "Neither" and band(r["recipient_cash"]) == bd])}
out["cells"] = res
# targeting at openings: share of opening requests reaching holders under $100
tg = {}
for scope in ("All", "All_but_Opus", "Sol", "Gemini", "Grok", "Opus"):
    sel = lambda r: scope == "All" or (scope == "All_but_Opus" and r["recipient_model"] != "Opus") or r["recipient_model"] == scope
    op = [r for r in legal if sel(r) and r["opening"] and asks_deed(r)]
    cr = [r for r in op if r["cell"] == "Author only"]; od = [r for r in op if r["cell"] == "Neither"]
    tg[scope] = {"completion_openings_to_lt100": f'{sum(r["recipient_cash"]<100 for r in cr)}/{len(cr)}',
                 "other_deed_openings_to_lt100": f'{sum(r["recipient_cash"]<100 for r in od)}/{len(od)}'}
out["opening_targeting"] = tg
# opening completion requests: cash offered to the holder by holder band
nc = collections.defaultdict(list)
for r in legal:
    if r["opening"] and r["cell"] == "Author only":
        nc[band(r["recipient_cash"])].append(r["recipient_cash_after"] - r["recipient_cash"])
out["opening_completion_request_net_cash_to_holder"] = {k: {"n": len(v), "median": statistics.median(v)} for k, v in nc.items()}
p = REV / "reviews/opus/data/liquidity_openings.json"; p.write_text(json.dumps(out, indent=1)); print("wrote", p.relative_to(ROOT))
