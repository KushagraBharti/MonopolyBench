"""Re-derive Grok content-versus-call action-name conflicts from canonical records (source read only).

Usage: python3 -I check_name_conflicts.py <repo_root> <out_json>
The content name is taken with a simple pattern: the first JSON "name" value in assistant content.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

repo, out_path = Path(sys.argv[1]), Path(sys.argv[2])
pkg = repo / "docs/research_raw/paper_rewrite_2026-11-10"
runs = {r["game"]: r["source_run"] for r in json.loads((pkg / "data/agenda_offers.json").read_bytes())}
ledger = {(c["game"], int(c["decision_id"].rsplit("-", 1)[1]))
          for c in json.loads((pkg / "data/resolution_conditions.json").read_bytes())["selected_grok_conflicts"]}
found, decisions, named, pairs = set(), 0, 0, Counter()
for g in sorted(runs):
    for line in (repo / runs[g] / "decisions.jsonl").read_bytes().splitlines():
        r = json.loads(line)
        if r["phase"] != "decision_resolved" or "grok" not in r["openrouter_model_id"]:
            continue
        decisions += 1
        valid = [a for a in r["attempts"] if a["outcome"] == "valid"]
        a = valid[-1] if valid else r["attempts"][-1]
        call = (a.get("parsed_tool_call") or {}).get("name")
        m = re.search(r'"name"\s*:\s*"([a-z_]+)"', a.get("assistant_content") or "")
        if m:
            named += 1
            if call and m.group(1) != call:
                found.add((g, int(r["decision_id"].rsplit("-", 1)[1])))
                pairs[f"{m.group(1)}->{call}"] += 1
out = {"grok_decisions": decisions, "selected_content_with_json_name": named, "name_conflicts": len(found),
       "retained_ledger": len(ledger), "in_both": len(found & ledger),
       "only_this_check": sorted(found - ledger), "only_ledger": sorted(ledger - found),
       "pairs": dict(pairs.most_common())}
out_path.write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "pairs"}))
