"""Per model: decisions containing an attempt rejected for uneven intermediate building, and how the
decision resolved (corrective retry success vs fallback). Read-only."""
import collections
from common import game_dirs, decisions, ALIAS
UNEVEN = "Uneven intermediate building"
c = collections.defaultdict(collections.Counter)
for g, run in game_dirs().items():
    st, rs = decisions(run)
    for did, r in rs.items():
        m = ALIAS[r["openrouter_model_id"]]
        att = r.get("attempts") or []
        idx = [i for i, a in enumerate(att) if any(UNEVEN in e for e in (a.get("validation_errors") or []))]
        if not idx:
            continue
        first = idx[0]
        cond = att[first].get("response_condition")
        c[m]["decisions_with_uneven_attempt"] += 1
        c[m][f"uneven_attempt_condition={cond}"] += 1
        final = (r.get("final_action") or {}).get("action")
        if r.get("fallback_used"):
            c[m]["resolved=fallback"] += 1
        else:
            c[m][f"resolved_valid={final}"] += 1
for m, v in sorted(c.items()):
    print(m, dict(sorted(v.items())))
