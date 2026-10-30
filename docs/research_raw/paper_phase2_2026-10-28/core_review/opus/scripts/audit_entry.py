"""Print a catalog entry's claim fields and the original applied messages/state for its referenced
decisions (read-only). Usage: audit_entry.py CATALOG_ID [CATALOG_ID ...]"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import game_dirs, decisions, action_state, ALIAS

CR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cat = {json.loads(l)["catalog_id"]: json.loads(l) for l in open(os.path.join(CR, "candidate_catalog.jsonl")) if l.strip()}


def owned(p):
    return ",".join(h["space_key"][:10] + (f"{h['houses']}h" if h["houses"] else "") + ("H" if h["hotel"] else "") + ("~" if h["mortgaged"] else "")
                    for h in p["holdings"]["owned"])


for cid in sys.argv[1:]:
    e = cat[cid]
    se = e.get("source_entry") or {}
    print("=" * 100)
    print(cid, "|", se.get("title"))
    for k in ("quotes", "financial_evidence", "observed_conduct"):
        print(k.upper() + ":", json.dumps(se.get(k))[:900])
    g = e.get("game")
    run = game_dirs()[g]
    st, rs = decisions(run)
    refs = sorted(set(int(r["decision_id"][-6:]) for r in se.get("decision_refs", []) if r.get("decision_id")))
    qrefs = sorted(set(int(q["decision_id"][-6:]) for q in (se.get("quotes") or []) if isinstance(q, dict) and q.get("decision_id")))
    if os.environ.get("QUOTED_ONLY") and qrefs:
        refs = qrefs
    for n in refs:
        k = [x for x in st if x.endswith(f"dec-{n:06d}")]
        if not k:
            continue
        s = st[k[0]]; r = rs.get(k[0], {})
        a, gs = action_state(s)
        fa = (r.get("final_action") or {})
        msg = fa.get("public_message") or (fa.get("args") or {}).get("public_message")
        priv = fa.get("private_thought") or (fa.get("args") or {}).get("private_thought")
        print(f"-- d{n} {s['player_id']} {ALIAS[s['openrouter_model_id']]} {s['decision_type'][:12]} pos={gs['you']['position']} cash={gs['you']['cash']} act={fa.get('action')}")
        print("   pub:", (msg or "")[:500])
        if priv:
            print("   priv:", priv[:400])
        print("   you:", owned(gs["you"]))
        for o in gs["others"]:
            print(f"   {o['player_id']} @{o['position']} ${o['cash']}:", owned(o))
