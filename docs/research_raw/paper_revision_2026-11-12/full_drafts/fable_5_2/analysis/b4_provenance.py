"""Run map, stored replay reports and request configuration, read from saved files.

Reads ``game-index.csv``, per-run ``replay_report.json``,
``artifact_replay_report.json`` and ``state_replay_report.json``, saved call
intents, ``players.json`` and events.  Reads arena source at the recorded run
commits with ``git show`` (text only).  Executes no engine, replay or model.
"""
from __future__ import annotations

import collections
import csv
import glob
import json
import subprocess

from corpus import COLLECTIONS, MODELS, REPO, SEEDS, game_dirs, load_all, write_json


def git(*args) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True).stdout


def main() -> None:
    G = load_all()
    index = {}
    for coll in COLLECTIONS:
        for row in csv.DictReader(open(coll / "game-index.csv")):
            index[int(row["collection_game"])] = {**row, "collection": coll.name}
    assert sorted(index) == list(range(1, 21))

    games = []
    replay = {"artifact": collections.Counter(), "state": collections.Counter()}
    art_events = state_events = total_events = 0
    excluded_state = set()
    for n, g in G.items():
        run = g.run
        rep = json.loads((run / "replay_report.json").read_text())
        art = json.loads((run / "artifact_replay_report.json").read_text())
        sta = json.loads((run / "state_replay_report.json").read_text())
        assert art["comparison_scope"] == "full_event_artifact_stream" and art["excluded_event_types"] == []
        assert art["original_canonical_hash"] == art["replay_canonical_hash"]
        assert sta["original_canonical_hash"] == sta["replay_canonical_hash"]
        assert art["original_compared_event_count"] == art["original_event_count"] == len(g.events)
        replay["artifact"][art["status"]] += 1
        replay["state"][sta["status"]] += 1
        art_events += art["original_compared_event_count"]
        state_events += sta["original_compared_event_count"]
        total_events += len(g.events)
        excluded_state |= set(sta["excluded_event_types"])
        seed = rep["run_config_used"]["seed"]
        assert seed == SEEDS[g.block]
        # elimination order from events
        order = [g.model[e["payload"]["player_id"]] for e in g.events
                 if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "BANKRUPTCY"]
        order = list(dict.fromkeys(order))
        seat_order = [g.model[p] for p, _ in sorted(g.seat.items(), key=lambda kv: kv[1])]
        row = index[n]
        games.append({
            "game": n, "block": g.block, "seed": seed, "rotation": g.rotation, "seat_order": seat_order,
            "turns": g.turns, "events": len(g.events), "decisions": g.n_decisions,
            "winner": g.winner, "winner_seat": g.seat[g.winner_pid], "eliminated_in_order": order,
            "run_id": row["run_id"], "source_commit": row["git_sha"], "package": row["package"],
            "collection": row["collection"],
            "replay_report_finished_at": rep["finished_at"],
            "synthetic_clock": [rep["run_config_used"]["start_ts_ms"], rep["run_config_used"]["ts_step_ms"]],
            "max_turns": rep["run_config_used"]["max_turns"], "max_trade_exchanges": rep["run_config_used"]["max_trade_exchanges"],
            "state_compared_events": sta["original_compared_event_count"],
        })
        assert len(order) == 3 and g.winner not in order
    commits = sorted({r["source_commit"] for r in games})
    commit_info = {}
    for c in commits:
        src = git("show", f"{c}:python/packages/arena/src/monopoly_arena/player_config.py")
        i = src.index("def tool_choice_for_model")
        fn = src[i:src.index("\n\n\n", i)] if "\n\n\n" in src[i:] else src[i:i + 500]
        assert 'return "required" if model_id == "x-ai/grok-4.7" else "auto"' in fn
        commit_info[c] = {"date": git("log", "-1", "--format=%ad", "--date=iso-strict", c).strip(),
                          "subject": git("log", "-1", "--format=%s", c).strip(),
                          "games": [r["game"] for r in games if r["source_commit"] == c],
                          "tool_choice_function": fn.strip()}

    # request payloads actually sent, from saved call intents
    tc = collections.Counter()
    n_int = 0
    for coll in COLLECTIONS:
        for f in glob.glob(str(coll / "game-*" / "cloud" / "calls" / "*.intent.json")):
            pl = json.loads(open(f).read())["payload"]
            n_int += 1
            tc[(pl.get("model"), pl.get("tool_choice"), json.dumps(pl.get("reasoning"), sort_keys=True), pl.get("parallel_tool_calls"),
                "temperature" in pl, "top_p" in pl, "max_tokens" in pl)] += 1

    wins = collections.Counter(r["winner"] for r in games)
    seat_wins = collections.Counter(r["winner_seat"] for r in games)
    first_out = collections.Counter(r["eliminated_in_order"][0] for r in games)
    out = {
        "repository": git("remote", "get-url", "origin").strip(),
        "head_at_analysis": git("rev-parse", "HEAD").strip(),
        "data_commits": {"games_1_12": git("log", "-1", "--format=%H", "--", "saved_games/railway-research-12-games-2026-10-25/game-index.csv").strip(),
                         "games_13_20": git("log", "-1", "--format=%H", "--", "saved_games/railway-research-8-games-2026-10-26/game-index.csv").strip()},
        "run_source_commits": commit_info,
        "seeds": SEEDS,
        "games": games,
        "totals": {"events": total_events, "decisions": sum(r["decisions"] for r in games),
                   "attempts": sum(len(r["attempts"]) for g in G.values() for r in g.resolved.values()),
                   "turns_min": min(r["turns"] for r in games), "turns_max": max(r["turns"] for r in games)},
        "wins_by_system": {m: wins[m] for m in MODELS},
        "wins_by_seat": {s: seat_wins[s] for s in (1, 2, 3, 4)},
        "first_eliminated_by_system": {m: first_out[m] for m in MODELS},
        "decisions_by_system": {m: sum(1 for g in G.values() for r in g.resolved.values() if g.model[r["player_id"]] == m) for m in MODELS},
        "attempts_by_system": {m: sum(len(r["attempts"]) for g in G.values() for r in g.resolved.values() if g.model[r["player_id"]] == m) for m in MODELS},
        "replay": {
            "artifact_mode": {"report": "run/artifact_replay_report.json", "scope": "full_event_artifact_stream",
                              "canonicalization": "monopoly_engine.canonical_event_lines over the full event stream",
                              "excluded_event_types": [], "status": dict(replay["artifact"]), "events_compared": art_events},
            "state_mode": {"report": "run/state_replay_report.json", "scope": "engine_state_relevant_events",
                           "excluded_event_types": sorted(excluded_state), "status": dict(replay["state"]), "events_compared": state_events},
            "executed": "at run finalization on 25 and 26 October 2026 (stored reports); not rerun here",
        },
        "request_payloads": {"intent_files": n_int,
                             "by_model": [{"model": k[0], "tool_choice": k[1], "reasoning": json.loads(k[2]), "parallel_tool_calls": k[3],
                                           "temperature_set": k[4], "top_p_set": k[5], "max_tokens_set": k[6], "requests": v}
                                          for k, v in sorted(tc.items())]},
    }
    assert total_events == 50918 and art_events == 50918
    write_json("b4_provenance.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "games"}, indent=1))
    for r in games:
        print(r["game"], r["block"], r["seed"], r["seat_order"], r["turns"], r["winner"], r["winner_seat"], r["eliminated_in_order"], r["source_commit"][:8])


if __name__ == "__main__":
    main()
