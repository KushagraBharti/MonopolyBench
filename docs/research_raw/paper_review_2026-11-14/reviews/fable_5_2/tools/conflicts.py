"""Named action in assistant content versus the applied tool call, for every liquidation decision. Read-only."""
import json, re, collections
from lib import *
C = collections.Counter
eps = json.loads((HERE.parent / "data" / "episodes_188.json").read_text())
paper = {(p["game"], p["first_decision"]): p for p in json.loads((INT / "data/liquidation_episodes.json").read_text())}

def named(content):
    if not content:
        return None
    names = re.findall(r'"name"\s*:\s*"([a-z_]+)"', content)
    names = [n for n in names if n in ("declare_bankruptcy", "mortgage_property", "sell_houses_or_hotel")]
    return names[-1] if names else None

rows = []
for e in eps:
    st, rs = load(e["game"])
    for k, d in enumerate(e["ds"]):
        r = rs[d]
        a = r["attempts"][-1]
        fa = r["final_action"]
        n = named(a.get("assistant_content"))
        rows.append(dict(game=e["game"], d=d, first=(k == 0), model=who(r), applied=fa["action"], named=n,
                         has_content=bool(a.get("assistant_content")), fallback=bool(r.get("fallback_used")),
                         payable=e["ustar"] >= e["debt"], outcome=paper[(e["game"], e["first"])]["outcome"],
                         note=fa.get("private_thought"), public=fa.get("public_message")))
print("liquidation decisions", len(rows))
print("has assistant content by model", C((r["model"], r["has_content"]) for r in rows))
print("named action present by model", C(r["model"] for r in rows if r["named"]))
conf = [r for r in rows if r["named"] and r["named"] != r["applied"]]
print("named != applied, all liquidation decisions:", len(conf), C(r["model"] for r in conf))
print("  direction", C((r["named"], r["applied"]) for r in conf))
print("  by payable", C((r["payable"], r["named"], r["applied"]) for r in conf))
print("  first decisions only", C((r["payable"], r["named"], r["applied"]) for r in conf if r["first"]))
for r in conf:
    print(f"   G{r['game']} d{r['d']} first={r['first']} {r['model']} payable={r['payable']} named={r['named']} applied={r['applied']} outcome={r['outcome']}")
grok = [r for r in rows if r["model"] == "Grok"]
print("Grok liquidation decisions", len(grok), "with named action", sum(1 for r in grok if r["named"]), "conflicts", sum(1 for r in grok if r["named"] and r["named"] != r["applied"]))
(HERE.parent / "data" / "liquidation_named_vs_applied.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
