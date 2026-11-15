"""Named-action scan over every resolved liquidation decision.

For each liquidation decision, the final attempt's assistant content is searched
for the three liquidation action names. A conflict is recorded when content
names one or more of these actions and none of them is the applied action.
The scan can only observe a conflict where assistant content names an action,
so its coverage differs by system. Read-only.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict

import lib

ACTIONS = ["mortgage_property", "sell_houses_or_hotel", "declare_bankruptcy"]
PAT = re.compile("|".join(ACTIONS))


def main() -> None:
    rows = []
    for g in range(1, 21):
        for idx, z in sorted(lib.decisions(g).items()):
            rz = z.get("decision_resolved")
            if not rz or rz.get("decision_type") != "LIQUIDATION_DECISION":
                continue
            model = lib.label(rz.get("player_name", ""))
            applied = rz["final_action"]["action"]
            att = rz["attempts"][-1] if rz.get("attempts") else {}
            m = lib.message_of(att) or {}
            content = m.get("content") or ""
            if not isinstance(content, str):
                content = json.dumps(content)
            named = sorted(set(PAT.findall(content)))
            rows.append({
                "game": g, "decision": idx, "model": model, "applied": applied,
                "fallback": bool(rz.get("fallback_used")),
                "has_content": bool(content.strip()),
                "named": named,
                "conflict": bool(named) and applied not in named,
            })
    per = defaultdict(Counter)
    for r in rows:
        c = per[r["model"]]
        c["liquidation_decisions"] += 1
        c["with_content"] += r["has_content"]
        c["content_names_action"] += bool(r["named"])
        c["conflicts"] += r["conflict"]
    conflicts = [r for r in rows if r["conflict"]]
    summary = {
        "liquidation_decisions": len(rows),
        "per_model": {k: dict(v) for k, v in per.items()},
        "conflicts": [(r["game"], r["decision"], r["model"], r["applied"], r["named"]) for r in conflicts],
        "method": "Substring scan of final-attempt assistant content for liquidation action names; read-only.",
    }
    lib.write_json("named_action_scan.json", {"summary": summary, "rows": rows})
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
