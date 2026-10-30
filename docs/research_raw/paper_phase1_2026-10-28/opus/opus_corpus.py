"""Run the Opus phase-1 reducer over the 20 October games and write derived data.

Usage (repo root): python3 docs/research_raw/paper_phase1_2026-10-28/opus/opus_corpus.py
Outputs go only to this directory. Read-only with respect to saved games.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from opus_reduce import (HERE, MODEL_LABEL, Ledger, game_dirs, load_board, load_jsonl,  # noqa: E402
                         measure_access, menu_from_started, reduce_events, sha256)

VERSION = "opus_phase1_v1"


def dice_stream(events):
    """Raw dice pairs tagged with their use: movement, jail doubles attempt, card utility rent."""
    out, last_action = [], None
    for e in events:
        if e["type"] == "TURN_STARTED":
            last_action = None
        elif e["type"] == "LLM_DECISION_RESPONSE":
            last_action = e["payload"]["action_name"]
        elif e["type"] == "DICE_ROLLED":
            p = e["payload"]
            use = p.get("reason") or ("jail_doubles_attempt" if last_action == "roll_for_doubles" else "movement")
            out.append((p["d1"], p["d2"], use, e["actor"]["player_id"]))
            last_action = None
    return out


def main():
    board = load_board()
    ownable = set(board["ownable"])
    games, all_trades, all_eps, all_acq, snap_rows, hashes = [], [], [], [], [], []
    dice_by_seed = defaultdict(list)
    for gno, run, row in game_dirs():
        events = load_jsonl(run / "events.jsonl")
        decisions = load_jsonl(run / "decisions.jsonl")
        cfg = json.loads((run / "run_config.json").read_text())
        label = {p["player_id"]: MODEL_LABEL[p["openrouter_model_id"]] for p in cfg["players"]}
        order = [a["player_id"] for a in sorted(cfg["seat_assignment"], key=lambda a: a["turn_order"])]
        players = list(label)
        menus, resolved = {}, {}
        for d in decisions:
            if d["phase"] == "decision_started":
                menus[d["decision_id"]] = menu_from_started(d)
            elif d["phase"] == "decision_resolved":
                resolved[d["decision_id"]] = d
        res = reduce_events(events, board, players, keep_projections=True)
        # Snapshot reconciliation: every saved snapshot must equal the folded state at some event boundary.
        seen = {proj for _, proj in res["projections"]}
        snaps = sorted((run / "state").glob("*.json"))
        matched = 0
        unmatched = []
        for path in snaps:
            proj = Ledger.project_snapshot(json.loads(path.read_text()), ownable)
            if proj in seen:
                matched += 1
            else:
                unmatched.append(path.name)
        # terminal folded state must equal a saved snapshot of the final turn
        terminal = res["projections"][-1][1]
        final_projs = {Ledger.project_snapshot(json.loads(p.read_text()), ownable)
                       for p in (run / "state").glob(f"turn_{events[-1]['turn_index']:04d}*.json")}
        snap_rows.append({"game": gno, "snapshots": len(snaps), "matched": matched, "unmatched": unmatched[:5]})
        winner = next(e["payload"]["winner_player_id"] for e in events if e["type"] == "GAME_ENDED")
        first_build = next((e for e in events if e["type"] in ("HOUSE_BUILT", "HOTEL_BUILT")), None)
        seed = cfg["seed"]
        dice_by_seed[seed].append((gno, dice_stream(events)))
        for t in res["trades"]:
            t.update(game=gno, models={q: label[q] for q in t["parties"]})
            gained = {q: sorted({g for o, g in map(tuple, t["groups_after"]) if o == q}
                                - {g for o, g in map(tuple, t["groups_before"]) if o == q}) for q in t["parties"]}
            t["new_groups"] = gained
            t["completion_sides"] = sum(bool(v) for v in gained.values())
            all_trades.append(t)
        for a in res["acquisitions"]:
            a.update(game=gno, to_model=label.get(a["to"]), from_model=label.get(a["from"]))
            all_acq.append(a)
        for ep in res["episodes"]:
            ep.update(game=gno, model=label[ep["player_id"]], winner=ep["player_id"] == winner)
            ep.update(measure_access(ep, events, board, menus, resolved))
            # episodes born and ended by the game-ending bankruptcy have no possible use
            ep["created_by_final_bankruptcy"] = (ep["completion_route"] == "creditor_inheritance" and
                                                 ep["end_reason"] == "game_end" and
                                                 ep["start_turn"] == events[-1]["turn_index"])
            all_eps.append(ep)
        hashes.append({"game": gno, "events_sha256": sha256(run / "events.jsonl"),
                       "decisions_sha256": sha256(run / "decisions.jsonl"), "run": str(run.relative_to(HERE.parents[3]))})
        games.append({
            "game": gno, "seed": seed, "models_in_turn_order": [label[p] for p in order],
            "winner": label[winner], "winner_seat": order.index(winner),
            "first_builder": label[first_build["payload"]["player_id"]] if first_build else None,
            "first_builder_won": bool(first_build) and first_build["payload"]["player_id"] == winner,
            "events": len(events), "decisions": len(resolved), "turns": events[-1]["turn_index"] + 1,
            "issues": res["issues"],
            "terminal_matches_snapshot": terminal in final_projs,
        })
    # Dice: compare within seed block
    dice_rows = []
    for seed, lst in sorted(dice_by_seed.items()):
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                (ga, a), (gb, b) = lst[i], lst[j]
                n = min(len(a), len(b))
                raw_equal = all(a[k][:2] == b[k][:2] for k in range(n))
                use_diff = [k for k in range(n) if a[k][2] != b[k][2]]
                dice_rows.append({"seed": seed, "games": [ga, gb], "compared_draws": n, "raw_pairs_equal": raw_equal,
                                  "first_use_difference_draw": use_diff[0] if use_diff else None,
                                  "draws_with_different_use": len(use_diff)})
    write(games, all_trades, all_eps, all_acq, snap_rows, dice_rows, hashes)


def write(games, trades, eps, acq, snap_rows, dice_rows, hashes):
    out = HERE
    with open(out / "opus_trades.jsonl", "w") as fh:
        for t in trades:
            fh.write(json.dumps(t, sort_keys=True) + "\n")
    with open(out / "opus_group_episodes.jsonl", "w") as fh:
        for ep in eps:
            fh.write(json.dumps(ep, sort_keys=True) + "\n")
    summary = summarize(games, trades, eps, acq, snap_rows, dice_rows)
    summary["source_hashes"] = hashes
    summary["games"] = games
    summary["snapshot_reconciliation"] = snap_rows
    summary["dice_pairs"] = dice_rows
    (out / "opus_results.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("games", "snapshot_reconciliation", "dice_pairs", "source_hashes")}, indent=1))


def summarize(games, trades, eps, acq, snap_rows, dice_rows):
    s = {"version": VERSION, "n_games": len(games)}
    s["events"] = sum(g["events"] for g in games)
    s["decisions"] = sum(g["decisions"] for g in games)
    s["wins"] = dict(Counter(g["winner"] for g in games))
    s["first_builder_wins"] = sum(g["first_builder_won"] for g in games)
    s["first_builder_exceptions"] = [(g["game"], g["first_builder"], g["winner"]) for g in games if not g["first_builder_won"]]
    s["reducer_issues"] = sum(len(g["issues"]) for g in games)
    s["terminal_snapshot_matches"] = sum(g["terminal_matches_snapshot"] for g in games)
    s["snapshots_total"] = sum(r["snapshots"] for r in snap_rows)
    s["snapshots_matched"] = sum(r["matched"] for r in snap_rows)
    s["deed_routes"] = dict(Counter(a["route"] for a in acq))
    s["trades"] = len(trades)
    s["trade_settlements_matching_payload"] = sum(t["settlement_matches_payload"] for t in trades)
    s["trade_completion_sides"] = dict(Counter(t["completion_sides"] for t in trades))
    s["trades_final_author_not_thread_initiator"] = sum(t["final_offer_author"] != t["thread_initiator"] for t in trades)
    s["trades_with_mortgage_interest"] = sum(any(t["interest_paid"].values()) for t in trades)
    s["mortgage_interest_total"] = sum(sum(t["interest_paid"].values()) for t in trades)
    s["episode_completion_routes"] = dict(Counter(e["completion_route"] for e in eps))
    s["episode_provenance_mix_for_trade_completed"] = dict(Counter(e["provenance_mix"] for e in eps if e["completion_route"] == "trade"))
    s["inheritance_episodes_created_by_final_bankruptcy"] = sum(e["created_by_final_bankruptcy"] for e in eps)
    s["episodes_with_buildings_at_start"] = dict(Counter(e["completion_route"] for e in eps if e["buildings_at_start"]))
    # Trade-completed group deployment table by model
    per = defaultdict(Counter)
    for e in eps:
        if e["completion_route"] != "trade":
            continue
        c = per[e["model"]]
        c["trade_groups"] += 1
        c["observed_access"] += e["access"] == "observed"
        c["censored"] += e["access"] != "observed"
        c["same_turn_access"] += e["same_turn_access"]
        c["built_first_mgmt_turn"] += bool(e.get("built_in_first_mgmt_turn"))
        c["entry_buildable"] += bool(e.get("entry_buildable"))
        c["entry_buildable_built"] += bool(e.get("entry_buildable")) and bool(e.get("built_in_first_mgmt_turn"))
        c["buildable_any_menu_first_turn"] += bool(e.get("buildable_any_menu_first_turn"))
        c["legal_turns_skipped_before_first_build"] += e.get("legal_turns_skipped_before_first_build", 0)
        c["groups_with_skipped_legal_turn"] += e.get("legal_turns_skipped_before_first_build", 0) > 0
        c["never_built_while_held"] += not e.get("built_in_episode")
        c["built_in_episode"] += bool(e.get("built_in_episode"))
        c["mortgaged_at_start"] += e["mortgaged_at_start"] > 0
        c["own_turns_without_access_sum"] += e["own_turns_without_access"]
        c["groups_with_delayed_access"] += e["own_turns_without_access"] > 0
        c["jail_decisions_before_access"] += len(e["jail_decisions_before_access"])
    s["trade_group_deployment_by_model"] = {m: dict(c) for m, c in sorted(per.items())}
    tot = Counter()
    for c in per.values():
        tot.update(c)
    s["trade_group_deployment_total"] = dict(tot)
    # All non-terminal group episodes, by completion route (inheritance at the final bankruptcy excluded)
    byroute = defaultdict(Counter)
    for e in eps:
        if e["created_by_final_bankruptcy"]:
            continue
        c = byroute[e["completion_route"]]
        c["episodes"] += 1
        c["observed_access"] += e["access"] == "observed"
        c["buildings_at_start"] += e["buildings_at_start"] > 0
        c["built_first_mgmt_turn"] += bool(e.get("built_in_first_mgmt_turn"))
        c["entry_buildable"] += bool(e.get("entry_buildable"))
        c["built_in_episode"] += bool(e.get("built_in_episode"))
        c["groups_with_skipped_legal_turn"] += e.get("legal_turns_skipped_before_first_build", 0) > 0
    s["nonterminal_episodes_by_route"] = {k: dict(v) for k, v in sorted(byroute.items())}
    s["missing_menus_any_episode"] = sum(e.get("missing_menus_before_first_build", 0) for e in eps) + sum(bool(e.get("menu_missing")) for e in eps)
    s["no_access_turn_reasons_trade_groups"] = dict(Counter(r for e in eps if e["completion_route"] == "trade"
                                                            for r in e["no_access_turn_reasons"]))
    s["jail_choice_before_access_trade_groups"] = dict(Counter(
        (j["chosen"], j["pay_fine_legal"]) for e in eps if e["completion_route"] == "trade"
        for j in e["jail_decisions_before_access"]).most_common()) if eps else {}
    s["jail_choice_before_access_trade_groups"] = {f"{k[0]}|pay_legal={k[1]}": v for k, v in Counter(
        (j["chosen"], j["pay_fine_legal"]) for e in eps if e["completion_route"] == "trade"
        for j in e["jail_decisions_before_access"]).items()}
    s["dice_pairs_raw_equal"] = sum(r["raw_pairs_equal"] for r in dice_rows)
    s["dice_pairs_total"] = len(dice_rows)
    s["dice_pairs_with_use_difference"] = sum(r["draws_with_different_use"] > 0 for r in dice_rows)
    return s


if __name__ == "__main__":
    main()
