"""Append hand-authored negative-control reviews (authoring/sample_gXX.jsonl) to ../negative_control_reviews.jsonl.
Reference fields (model, decision_type, applied action, attempt chain, fallback) are filled from the canonical
decision record; judgment fields must come from the author. Validates sample membership and no duplicates."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from common import game_dirs, decisions, ALIAS

HERE = os.path.dirname(os.path.abspath(__file__))
OP = os.path.dirname(HERE)
CR = os.path.dirname(OP)
sample = {json.loads(l)["decision_id"]: json.loads(l) for l in open(os.path.join(CR, "public_unflagged_sample.jsonl")) if l.strip()}
out = os.path.join(OP, "negative_control_reviews.jsonl")
done = set()
if os.path.exists(out):
    done = {json.loads(l)["decision_id"] for l in open(out) if l.strip()}
REQ = ["suffix", "judgment", "categories", "notes", "newly_noticed_case", "counterexample_to", "peer_informed"]
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
g = rows[0]["game"]
st, rs = decisions(game_dirs()[g])
new = []
for r in rows:
    for k in REQ:
        assert k in r, (k, r)
    did = [d for d in sample if sample[d]["game"] == g and d.endswith(r["suffix"])]
    assert len(did) == 1, r["suffix"]
    did = did[0]
    assert did not in done, did
    s, res = st[did], rs.get(did) or {}
    fa = res.get("final_action") or {}
    rec = dict(decision_id=did, game=g, player_id=s["player_id"], model=ALIAS[s["openrouter_model_id"]],
               decision_type=s["decision_type"], applied_action=fa.get("action"),
               attempt_chain=[f"{a.get('response_condition')}:{a.get('outcome')}" for a in res.get("attempts") or []],
               fallback=bool(res.get("fallback_used")),
               reading_status="read full canonical decision (observation, legal menu, every attempt incl. assistant content and returned provider summary, applied action, events) plus 3 prior and 2 following decisions (scripts/sample_view.py)",
               judgment=r["judgment"], categories=r["categories"], notes=r["notes"],
               newly_noticed_case=r["newly_noticed_case"], counterexample_to=r["counterexample_to"],
               peer_informed=r["peer_informed"], reviewer="Opus (claude-opus-5-5)", stage="independent_initial", date="2026-10-29")
    new.append(rec)
with open(out, "a") as f:
    for rec in new:
        f.write(json.dumps(rec) + "\n")
print("appended", len(new), "total", len(done) + len(new))
