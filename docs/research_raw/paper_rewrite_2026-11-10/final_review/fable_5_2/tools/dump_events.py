"""Print selected canonical events (source read only; no engine).

Usage: python3 -I dump_events.py <repo_root> <game> <types_csv|ALL> [turn_lo] [turn_hi] [player]
"""
import json
import sys
from pathlib import Path

repo, g, types = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
lo = int(sys.argv[4]) if len(sys.argv) > 4 else 0
hi = int(sys.argv[5]) if len(sys.argv) > 5 else 10 ** 9
who = sys.argv[6] if len(sys.argv) > 6 else None
pkg = repo / "docs/research_raw/paper_rewrite_2026-11-10"
runs = {r["game"]: r["source_run"] for r in json.loads((pkg / "data/agenda_offers.json").read_bytes())}
board = json.loads((repo / "contracts/data/board.json").read_bytes())
name = {s["index"]: s["name"] for s in board["spaces"]}
want = None if types == "ALL" else set(types.split(","))
SKIP = {"LLM_DECISION_REQUESTED", "LLM_DECISION_RESPONSE", "LLM_PUBLIC_MESSAGE", "LLM_PRIVATE_THOUGHT",
        "DICE_ROLLED", "TURN_STARTED", "TURN_ENDED"}
for line in (repo / runs[g] / "events.jsonl").read_bytes().splitlines():
    e = json.loads(line)
    if not lo <= e["turn_index"] <= hi:
        continue
    if want is None and e["type"] in SKIP:
        continue
    if want is not None and e["type"] not in want:
        continue
    p = dict(e["payload"])
    if who and who not in json.dumps(p) and (e["actor"] or {}).get("player_id") != who:
        continue
    if "space_index" in p:
        p["space"] = name.get(p["space_index"])
    for k in ("to", "from"):
        if isinstance(p.get(k), int):
            p[k + "_name"] = name.get(p[k])
    print(f"seq {e['seq']:5d} t{e['turn_index']:3d} {e['type']:24s} {json.dumps(p)[:330]}")
