"""Split first-management-turn outcomes of the 63 trade-completed groups by cause.

For each trade-completed colour-group episode (phase-1 Fable reducer output), take the owner's
POST_TURN_ACTION_DECISION records in the first actual management turn and classify the turn:
  built                      - a HOUSE/HOTEL build on that group was applied in that turn
  never_legal_in_window      - no build on that group was legal at any menu in that turn
  default_after_refusal      - no build; at least one decision in the turn ended in an engine
                               default whose chain contains a provider refusal (Opus condition)
  default_other              - no build; engine default without a refusal in the chain
  received_conflict          - no build; at least one decision in the turn is in Sol's list of
                               Grok content/tool-name conflicts
  valid_end                  - no build; every decision in the turn was a valid model-selected action
Read-only; no engine import. Run: python3 -I <this file> <repo_root>
"""
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(__file__).resolve().parent.parent / "exhibits"
EPIS = ROOT / "docs/research_raw/paper_phase1_2026-10-28/fable/fable_group_episodes_all_routes.jsonl"
CONFL = ROOT / "docs/research_raw/paper_phase2_2026-10-28/core_review/sol/received_name_conflict_audit.json"
COLLECTIONS = [ROOT / "saved_games/railway-research-12-games-2026-10-25", ROOT / "saved_games/railway-research-8-games-2026-10-26"]

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def game_dirs() -> dict[int, Path]:
    out = {}
    for coll in COLLECTIONS:
        for row in csv.DictReader((coll / "game-index.csv").open()):
            out[int(row["collection_game"])] = coll / row["package"] / "run"
    return out

def conflict_ids() -> set[str]:
    d = json.load(CONFL.open())
    ids = set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("decision_id",) and isinstance(v, str):
                    ids.add(v)
                walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d)
    return ids

def main() -> None:
    dirs = game_dirs()
    confl = conflict_ids()
    episodes = [json.loads(l) for l in EPIS.open()]
    trade = [e for e in episodes if e["route"] == "trade"]
    assert len(trade) == 63, len(trade)
    # per game: decision records (resolved ones carry attempts/final_action) and build events by turn
    cache = {}
    rows = []
    for e in trade:
        g = e["game"]
        if g not in cache:
            run = dirs[g]
            decs = {}
            for line in (run / "decisions.jsonl").open():
                r = json.loads(line)
                if "attempts" in r:
                    decs[r["decision_id"]] = r
            cache[g] = decs
        decs = cache[g]
        turn = e["first_mgmt_turn"]
        pid = e["player_id"]
        turn_decs = [r for r in decs.values() if r["player_id"] == pid and r["turn_index"] == turn and r["decision_type"] == "POST_TURN_ACTION_DECISION"]
        turn_decs.sort(key=lambda r: r["decision_id"])
        flags = []
        for r in turn_decs:
            fa = r.get("final_action") or {}
            default = (fa.get("private_thought") == "fallback") or bool(r.get("fallback_action")) and fa.get("private_thought") == "fallback"
            refused = any((a.get("raw_response") or {}).get("choices", [{}])[0].get("finish_reason") == "content_filter" or a.get("status") == "refused" or "refus" in json.dumps(a.get("validation") or a.get("status") or "").lower() for a in r.get("attempts", []))
            conflict = r["decision_id"] in confl
            flags.append({"decision_id": r["decision_id"][-10:], "applied": fa.get("name") or fa.get("tool_name") or fa.get("action") or (r.get("applied_action") or {}).get("name") if isinstance(r.get("applied_action"), dict) else fa.get("name") or fa.get("tool_name") or fa.get("action"), "default": default, "refused_in_chain": refused, "conflict": conflict, "response_condition": (r.get("sequence_meta") or {}).get("response_condition")})
        # classify by the turn-ending decision (last post-turn decision of the owner in that turn);
        # earlier decisions in the turn are reported as secondary flags only
        last = flags[-1] if flags else None
        if e["built_first_mgmt_turn"]:
            cause = "built"
        elif not e["legal_any_menu_that_turn"]:
            cause = "never_legal_in_window"
        elif last and last["default"] and last["refused_in_chain"]:
            cause = "default_after_refusal"
        elif last and last["default"]:
            cause = "default_other"
        elif last and last["conflict"]:
            cause = "received_conflict"
        else:
            cause = "valid_end"
        earlier_flags = {"earlier_default": any(f["default"] for f in flags[:-1]), "earlier_conflict": any(f["conflict"] for f in flags[:-1])}
        rows.append({"game": g, "player": pid, "model": e["model"], "group": e["group"], "first_mgmt_turn": turn, "entry_legal": e["entry_legal"], "legal_any_menu_that_turn": e["legal_any_menu_that_turn"], "built_first_mgmt_turn": e["built_first_mgmt_turn"], "first_mgmt_decision": e["first_mgmt_decision"][-10:], "n_postturn_decisions": len(turn_decs), "cause": cause, **earlier_flags, "decisions": flags, "winner": e["winner"]})
    # summary by model
    models = ["Sol", "Gemini", "Opus", "Grok"]
    causes = ["built", "never_legal_in_window", "default_after_refusal", "default_other", "received_conflict", "valid_end"]
    summary = {m: {c: 0 for c in causes} | {"groups": 0} for m in models}
    for r in rows:
        summary[r["model"]]["groups"] += 1
        summary[r["model"]][r["cause"]] += 1
    report = {"unit": "trade-completed colour-group episodes (63); first actual management turn of the owner", "causes": causes, "summary": summary, "rows": rows,
              "sources": {"episodes_sha256": sha256(EPIS), "conflict_audit_sha256": sha256(CONFL), "script_sha256": sha256(Path(__file__))},
              "limits": ["'valid_end' means every post-turn decision in that turn was a valid model-selected action; it does not establish a deliberate hold or its quality", "'default_after_refusal' is the Opus refusal-consumed-retry condition; 'received_conflict' uses Sol's 139 Grok conflict IDs and does not localize the cause", "never_legal_in_window includes cash, mortgage, stock and even-building reasons jointly; it is not a demand measure"]}
    json.dump(report, (OUT / "first_management_causes.json").open("w"), indent=1)
    with (OUT / "first_management_causes.csv").open("w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["model"] + ["groups"] + causes)
        for m in models: w.writerow([m, summary[m]["groups"]] + [summary[m][c] for c in causes])
    print(json.dumps(summary, indent=1))
    for r in rows:
        if r["cause"] != "built":
            print(r["game"], r["model"], r["group"], "turn", r["first_mgmt_turn"], r["cause"], [(f["decision_id"], f["applied"], f["response_condition"], f["default"], f["conflict"]) for f in r["decisions"]])

if __name__ == "__main__":
    main()
