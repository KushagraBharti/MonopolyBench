"""Decompose trade-completed groups that were buildable at entry but not built in
the owner's first management turn (the residual of the 34/42 statistic).

Usage: python3 -I deployment_residuals.py <repo_root> <out_json>

Reads (read-only):
  docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl
  docs/research_raw/paper_phase2_2026-10-28/core_review/sol/build_recovery_audit.json  (engine defaults)
  docs/research_raw/paper_phase2_2026-10-28/core_review/sol/received_name_conflict_audit.json
  saved_games/<collection>/game-*/run/decisions.jsonl (resolved records only)
For each residual episode it lists the owner's resolved management decisions in
that turn: applied action, build-plan targets, fallback flag, and whether the
decision is a recorded engine default or a received content/tool-name conflict.
It classifies mechanically; it does not judge whether a hold was wise.
"""
import hashlib
import json
import sys
from pathlib import Path

GROUP_KEYS = {
    "BROWN": {"MEDITERRANEAN_AVENUE", "BALTIC_AVENUE"},
    "LIGHT_BLUE": {"ORIENTAL_AVENUE", "VERMONT_AVENUE", "CONNECTICUT_AVENUE"},
    "PINK": {"ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE"},
    "ORANGE": {"ST_JAMES_PLACE", "TENNESSEE_AVENUE", "NEW_YORK_AVENUE"},
    "RED": {"KENTUCKY_AVENUE", "INDIANA_AVENUE", "ILLINOIS_AVENUE"},
    "YELLOW": {"ATLANTIC_AVENUE", "VENTNOR_AVENUE", "MARVIN_GARDENS"},
    "GREEN": {"PACIFIC_AVENUE", "NORTH_CAROLINA_AVENUE", "PENNSYLVANIA_AVENUE"},
    "DARK_BLUE": {"PARK_PLACE", "BOARDWALK"},
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    root = Path(sys.argv[1])
    ep_path = root / "docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl"
    rec_path = root / "docs/research_raw/paper_phase2_2026-10-28/core_review/sol/build_recovery_audit.json"
    con_path = root / "docs/research_raw/paper_phase2_2026-10-28/core_review/sol/received_name_conflict_audit.json"
    eps = [json.loads(l) for l in ep_path.read_text().splitlines() if l.strip()]
    rec = json.loads(rec_path.read_text())
    con = json.loads(con_path.read_text())
    defaults = {d["decision_id"] for d in rec["defaults"]}
    uneven = {d["decision_id"] for d in rec["uneven_rows"]}
    conflicts = {d["decision_id"] for d in con["all_named_conflicts"]}
    trade_eps = [e for e in eps if e["route"] == "trade"]
    assert len(trade_eps) == 63, len(trade_eps)
    entry = [e for e in trade_eps if e["entry_legal"]]
    assert len(entry) == 42, len(entry)
    resid = [e for e in entry if not e["built_first_management"]]
    run_dirs = {}
    for coll in ("railway-research-12-games-2026-10-25", "railway-research-8-games-2026-10-26"):
        for g in sorted(p for p in (root / "saved_games" / coll).glob("game-*") if p.is_dir()):
            run_dirs[len(run_dirs) + 1] = g / "run"
    out_rows = []
    hashes = {str(ep_path): sha(ep_path), str(rec_path): sha(rec_path), str(con_path): sha(con_path)}
    for e in resid:
        run = run_dirs[e["game"]]
        dpath = run / "decisions.jsonl"
        hashes[str(dpath)] = sha(dpath)
        decs = []
        for line in dpath.read_text().splitlines():
            d = json.loads(line)
            if d.get("phase") != "decision_resolved":
                continue
            if d["player_id"] != e["player_id"] or d["turn_index"] != e["first_management_turn"]:
                continue
            fa = d.get("final_action") or {}
            plan = (fa.get("args") or {}).get("build_plan") or []
            targets = sorted({p.get("space_key") for p in plan})
            decs.append({
                "decision_id": d["decision_id"], "decision_type": d["decision_type"], "applied_action": fa.get("action"),
                "build_targets": targets,
                "targets_this_group": bool(set(targets) & GROUP_KEYS[e["group"]]),
                "fallback_used": d.get("fallback_used"), "engine_default": d["decision_id"] in defaults,
                "uneven_rejection": d["decision_id"] in uneven, "received_name_conflict": d["decision_id"] in conflicts,
            })
        if any(x["engine_default"] for x in decs):
            cls = "engine_default_in_turn"
        elif any(x["received_name_conflict"] for x in decs):
            cls = "received_name_conflict_in_turn"
        elif any(x["applied_action"] == "build_houses_or_hotel" for x in decs):
            cls = "built_elsewhere_only"
        else:
            cls = "no_build_applied_without_default_or_name_conflict"
        out_rows.append({"game": e["game"], "player_id": e["player_id"], "model": e["model"], "group": e["group"],
                         "first_management_decision": e["first_management_decision"], "first_management_turn": e["first_management_turn"],
                         "classification": cls, "decisions": decs})
    summary = {}
    for r in out_rows:
        summary.setdefault(r["model"], {}).setdefault(r["classification"], 0)
        summary[r["model"]][r["classification"]] += 1
    doc = {"population": "trade-completed groups buildable at entry to the owner's first management turn but not built in it",
           "n_trade_groups": len(trade_eps), "n_entry_buildable": len(entry), "n_residual": len(out_rows),
           "summary_by_model": summary, "rows": out_rows, "input_sha256": hashes,
           "script_sha256": sha(__file__),
           "limits": "Mechanical classification of the owner's resolved decisions in that turn. 'no_build_applied_without_default_or_name_conflict' is a candidate chosen hold, not a verified preference; content of explanations not read here."}
    Path(sys.argv[2]).write_text(json.dumps(doc, indent=1))
    print(json.dumps({"n_residual": len(out_rows), "summary": summary}, indent=1))
    for r in out_rows:
        print(r["game"], r["model"], r["group"], r["classification"], [(x["decision_id"][-10:], x["applied_action"], x["build_targets"], x["engine_default"], x["received_name_conflict"]) for x in r["decisions"]])


if __name__ == "__main__":
    main()
