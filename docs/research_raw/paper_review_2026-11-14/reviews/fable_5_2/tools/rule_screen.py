"""Keyword screen (not validated coding) for two rule beliefs in liquidation decisions:
 (1) the creditor pays 10% on inherited mortgaged deeds, (2) bankruptcy needs prior liquidation.
Reads applied notes and provider-returned text of all 338 liquidation decisions."""
import json, re, collections
from lib import *
eps = json.loads((HERE.parent / "data" / "episodes_188.json").read_text())
P1 = re.compile(r"(10\s?%|ten percent|interest|transfer fee)", re.I)
CTX = re.compile(r"(inherit|bankrupt|creditor|encumber|receives? it|hand[s]? (p\d|them))", re.I)
P2 = re.compile(r"(before bankruptcy is valid|reject bankruptcy|must liquidate|liquidat\w+ (all|both|everything) .{0,40}before (declaring )?bankrupt|don.t declare while)", re.I)
hits1, hits2 = [], []
for e in eps:
    st, rs = load(e["game"])
    for d in e["ds"]:
        r = rs[d]
        note = (r["final_action"].get("private_thought") or "")
        prov = reasoning(r) or ""
        for ch, txt in (("note", note), ("provider", prov)):
            for sent in re.split(r"(?<=[.!?])\s+|\n+", txt):
                if P1.search(sent) and CTX.search(sent):
                    hits1.append((e["game"], d, who(r), ch, e["ustar"] >= e["debt"], r["final_action"]["action"], sent.strip()[:230]))
                if P2.search(sent):
                    hits2.append((e["game"], d, who(r), ch, e["ustar"] >= e["debt"], r["final_action"]["action"], sent.strip()[:230]))
def show(name, hits):
    decs = {(g, d) for g, d, *_ in hits}
    print(name, "sentences", len(hits), "decisions", len(decs), "by model", collections.Counter(m for (g, d, m) in {(g, d, m) for g, d, m, *_ in hits}))
    seen = set()
    for h in hits:
        k = (h[0], h[1], h[3])
        if k in seen: continue
        seen.add(k)
        print(f"   G{h[0]} d{h[1]} {h[2]} [{h[3]}] payable={h[4]} applied={h[5]} :: {h[6]}")
show("(1) interest on inherited mortgaged deeds", hits1)
show("(2) liquidation required before bankruptcy", hits2)
