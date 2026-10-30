"""Independent phase-1 reproduction. Run with Python 3.10+ from any directory.

Reads only the two explicit October collection indexes. Every output is beside
this script. No canonical artifacts, prompts or games are modified.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import itertools
import json
from pathlib import Path
import re

from economics import reconstruct, measure_episode, space_key

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
COLLECTIONS = [ROOT / "saved_games/railway-research-12-games-2026-10-25",
               ROOT / "saved_games/railway-research-8-games-2026-10-26"]
NAMES = {"openai/gpt-6.1-sol": "Sol", "google/gemini-4-argon": "Gemini",
         "anthropic/claude-opus-5.5": "Opus", "x-ai/grok-4.7": "Grok"}


def read(path):
    return json.loads(path.read_text())


def rows(path):
    with path.open() as f:
        for line in f:
            yield json.loads(line)


def write_json(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def write_rows(name, data):
    with (OUT / name).open("w") as f:
        for item in data:
            f.write(json.dumps(item, sort_keys=True) + "\n")


def reasoning_inventory(raw):
    """Count only provider fields, never tool arguments or token counts as text."""
    fields, opaque = {}, []
    for ci, choice in enumerate(raw.get("choices") or []):
        message = choice.get("message") or {}
        for key in ("reasoning", "reasoning_content"):
            val = message.get(key)
            if isinstance(val, str) and val.strip():
                fields[f"choices.{ci}.message.{key}"] = len(val)
        for di, detail in enumerate(message.get("reasoning_details") or []):
            if not isinstance(detail, dict):
                continue
            for key in ("text", "summary"):
                val = detail.get(key)
                if isinstance(val, str) and val.strip() and "encrypted" not in str(detail.get("type", "")):
                    fields[f"choices.{ci}.message.reasoning_details.{di}.{key}"] = len(val)
            if detail.get("data"):
                opaque.append({"index": di, "type": detail.get("type"), "format": detail.get("format")})
    return {"text_fields_chars": fields, "opaque_fields": opaque,
            "has_text": bool(fields), "has_opaque": bool(opaque)}


def private_note_origin(action, fallback_used):
    if not action.get("private_thought"):
        return "absent_or_empty"
    return "deterministic_fallback" if fallback_used else "nonfallback_final_action"


def name_mismatch(attempt):
    content, tool = attempt.get("assistant_content"), attempt.get("parsed_tool_call") or {}
    if not isinstance(content, str) or not tool.get("name"):
        return None
    try:
        obj = json.loads(content)
        if not isinstance(obj, dict) or not isinstance(obj.get("name"), str):
            return None
        content_name, content_format = obj["name"], "json_object"
    except (ValueError, TypeError):
        # Retain a literal action-name mention in malformed content separately.
        # This reproduces the old regex count without calling it structured JSON.
        found = re.search(r'"name"\s*:\s*"([a-z_]+)"', content)
        if not found:
            return None
        content_name, content_format, obj = found.group(1), "malformed_json_name_match", None
    if content_name == tool["name"]:
        return None
    args = tool.get("arguments")
    try:
        args = json.loads(args) if isinstance(args, str) else args
    except ValueError:
        args = None
    other = obj.get("parameters", obj.get("arguments")) if obj else None
    if obj and other is None and "public_message" in obj:
        other = {k: v for k, v in obj.items() if k not in {"name", "type"}}
    if isinstance(other, str):
        try:
            other = json.loads(other)
        except ValueError:
            other = None

    def message_value(key):
        if isinstance(other, dict):
            return other.get(key)
        found = re.search(r'"' + key + r'"\s*:\s*"((?:[^"\\]|\\.)*)"', content)
        if found:
            try:
                return json.loads('"' + found.group(1) + '"')
            except ValueError:
                pass
        return None

    same = {}
    for key in ("public_message", "private_thought"):
        left, right = message_value(key), args.get(key) if isinstance(args, dict) else None
        same[key] = left.strip() == right.strip() if isinstance(left, str) and isinstance(right, str) else None
    return {"content_name": content_name, "tool_name": tool["name"], "content_format": content_format,
            "identical_arguments": other == args if isinstance(other, dict) and isinstance(args, dict) else None,
            "same_public_message_stripped": same["public_message"],
            "same_private_thought_stripped": same["private_thought"]}


def main():
    board_path = ROOT / "contracts/data/board.json"
    board = read(board_path)["spaces"]
    keys = {g: {s["index"]: space_key(s["name"]) for s in board
                if s["kind"] == "PROPERTY" and s["group"] == g}
            for g in {s["group"] for s in board if s["kind"] == "PROPERTY"}}
    games, episodes, trades, acquisitions, attempts, mismatches, sources, decision_inventory = [], [], [], [], [], [], [], []
    negotiation_events = []
    models = defaultdict(Counter)
    prompt_hashes, raw_file_agreement, response_conditions = Counter(), Counter(), Counter()
    artifact_differences, refusal_chains = [], Counter()
    max_public_memory = max_private_memory = 0
    dice = defaultdict(list)
    source_paths = {board_path, *OUT.glob("*.py")}
    for collection in COLLECTIONS:
        source_paths.add(collection / "game-index.csv")
        with (collection / "game-index.csv").open() as f:
            index_rows = list(csv.DictReader(f))
        for idx in index_rows:
            game = int(idx["collection_game"])
            run = collection / idx["package"] / "run"
            cfg, summary = read(run / "run_config.json"), read(run / "summary.json")
            names = {p["player_id"]: NAMES[p["openrouter_model_id"]] for p in cfg["players"]}
            events, actions = list(rows(run / "events.jsonl")), list(rows(run / "actions.jsonl"))
            result = reconstruct(events, names, board)
            terminal_path = sorted((run / "state").glob("*.json"))[-1]
            terminal = read(terminal_path)
            assert terminal["phase"] == "GAME_OVER", game
            assert result["owners"] == {s["index"]: s["owner_id"] for s in terminal["board"]
                                         if s["price"] is not None}, game
            assert result["cash"] == {pid: summary["players"][pid]["cash"] for pid in names}, game
            for filename in ["run_config.json", "summary.json", "events.jsonl", "actions.jsonl", "decisions.jsonl"]:
                source_paths.add(run / filename)
            source_paths.add(terminal_path)
            starts, resolved, menus, fallback_by_decision, decision_by_event = {}, {}, {}, {}, {}
            for d in rows(run / "decisions.jsonl"):
                did, model = d["decision_id"], names[d["player_id"]]
                if d["phase"] == "decision_started":
                    assert did not in starts
                    starts[did] = {"turn": d["turn_index"], "player_id": d["player_id"],
                                   "decision_type": d["decision_type"]}
                    action_state = d["prompt_payload"]["action_state"]
                    prompt_hashes[hashlib.sha256(d["prompt_messages"][0]["content"].encode()).hexdigest()] += 1
                    memory = d["prompt_payload"]["game_state"]["memory"]
                    max_public_memory = max(max_public_memory, len(memory["public_timeline_last_20"]))
                    max_private_memory = max(max_private_memory, len(memory["your_private_thoughts_last_10"]))
                    menus[did] = {"available_actions": action_state["available_actions"],
                                  "buildable_space_keys": action_state.get("scenario", {}).get("options", {}).get("buildable_space_keys", [])}
                    continue
                assert d["phase"] == "decision_resolved" and did not in resolved
                resolved[did] = d["final_action"]
                fallback_by_decision[did] = bool(d.get("fallback_used"))
                for eid in d.get("emitted_event_ids", []):
                    assert eid not in decision_by_event, (game, eid)
                    decision_by_event[eid] = did
                private_origin = private_note_origin(d["final_action"], bool(d.get("fallback_used")))
                decision_inventory.append({"game": game, "model": model, "decision_id": did,
                    "player_id": d["player_id"], "turn": d["turn_index"], "decision_type": d["decision_type"],
                    "final_action": d["final_action"]["action"], "fallback_used": bool(d.get("fallback_used")),
                    "final_private_note_origin": private_origin,
                    "final_public_message_nonempty": bool((d["final_action"].get("public_message") or "").strip()),
                    "attempt_count": len(d["attempts"]), "semantic_review": "pending"})
                models[model].update(decisions=1, retry_used_decisions=bool(d.get("retry_used")),
                                     deterministic_fallback_decisions=bool(d.get("fallback_used")))
                refused, texts, opaque = False, False, False
                valid_indexes = [i for i, a in enumerate(d["attempts"]) if a.get("outcome") == "valid"]
                selected_index = valid_indexes[-1] if valid_indexes else None
                if model == "Opus":
                    refusal_chains[" -> ".join(str(a.get("response_condition")) for a in d["attempts"])] += 1
                selected_text = False
                for ai, a in enumerate(d["attempts"]):
                    raw = a.get("raw_response") or {}
                    reasoning = reasoning_inventory(raw)
                    suffix = "" if ai == 0 else f"_retry{ai}"
                    path = run / "prompts" / f"decision_{did}{suffix}_response.json"
                    assert path.exists(), (game, did, ai)
                    disk_response = read(path)
                    raw_file_agreement["equal" if disk_response == a.get("raw_response") else "different"] += 1
                    if disk_response != a.get("raw_response"):
                        artifact_differences.append({"game": game, "decision_id": did, "attempt_index": ai,
                            "path": str(path.relative_to(ROOT)), "ledger_raw_response_is_null": a.get("raw_response") is None,
                            "file_error_type": disk_response.get("error_type"), "file_error": disk_response.get("error")})
                    choice = (raw.get("choices") or [{}])[0]
                    mismatch = name_mismatch(a)
                    attempt = {"game": game, "model": model, "decision_id": did, "attempt_index": ai,
                               "response_path": str(path.relative_to(ROOT)), "outcome": a.get("outcome"),
                               "response_condition": a.get("response_condition"),
                               "decision_fallback_used": bool(d.get("fallback_used")),
                               "requested_model": a.get("requested_model"), "returned_model": raw.get("model"),
                               "returned_provider": raw.get("provider"), "call_id": a.get("call_id"),
                               "finish_reason": choice.get("finish_reason"),
                               "native_finish_reason": choice.get("native_finish_reason"),
                               "validation_errors": a.get("validation_errors"),
                               "provider_reasoning": reasoning,
                               "reasoning_tokens_reported": (raw.get("usage") or {}).get("completion_tokens_details", {}).get("reasoning_tokens"),
                               "mismatch": mismatch, "semantic_review": "pending"}
                    attempt["selected_valid_attempt"] = ai == selected_index
                    response_conditions[a.get("response_condition")] += 1
                    selected_text |= ai == selected_index and reasoning["has_text"]
                    attempts.append(attempt)
                    models[model].update(attempts=1, refused_attempts=a.get("outcome") == "refused",
                                         attempts_with_provider_text=reasoning["has_text"],
                                         attempts_with_opaque_provider_data=reasoning["has_opaque"],
                                         refused_attempts_with_text=a.get("outcome") == "refused" and reasoning["has_text"])
                    refused |= a.get("outcome") == "refused"
                    texts |= reasoning["has_text"]
                    opaque |= reasoning["has_opaque"]
                    if mismatch:
                        mismatches.append({"game": game, "model": model, "decision_id": did,
                                           "attempt_index": ai, "applied_action": d["final_action"]["action"],
                                           "selected_valid_attempt": ai == selected_index,
                                           "fallback_used": d.get("fallback_used"), **mismatch})
                models[model].update(decisions_with_refused_attempt=refused, decisions_with_provider_text=texts,
                                     decisions_with_opaque_provider_data=opaque,
                                     selected_valid_attempts_with_text=selected_text,
                                     text_only_in_unselected_attempts_decisions=texts and not selected_text)
            requested = [e["payload"]["decision_id"] for e in events if e["type"] == "LLM_DECISION_REQUESTED"]
            assert requested == [a["decision_id"] for a in actions] == list(starts) == list(resolved), game
            assert all(resolved[a["decision_id"]] == a["action"] for a in actions), game
            action_by_id = {a["decision_id"]: a["action"]["action"] for a in actions}
            counts = Counter(e["type"] for e in events)
            for e in events:
                if e["type"] in {"TRADE_PROPOSED", "TRADE_COUNTERED", "TRADE_ACCEPTED", "TRADE_REJECTED", "TRADE_EXPIRED"}:
                    negotiation_events.append({"game": game, "event_id": e["event_id"], "seq": e["seq"],
                        "turn": e["turn_index"], "type": e["type"], "actor": e["actor"], "payload": e["payload"],
                        "decision_id": decision_by_event.get(e["event_id"]), "semantic_review": "pending"})
            first_build = next((e for e in events if e["type"] in {"HOUSE_BUILT", "HOTEL_BUILT"}), None)
            assert first_build is not None
            for row in result["group_episodes"]:
                row.update(game=game, model=names[row["player_id"]])
                row.update(measure_episode(row, events, menus, keys[row["group"]]))
                for pre in row["pre_management_decisions"]:
                    pre["applied_action"] = action_by_id[pre["decision_id"]]
                episodes.append(row)
            for row in result["trades"]:
                trades.append(dict(row, game=game, player_models=names))
            for row in result["deed_acquisitions"]:
                acquisitions.append(dict(row, game=game, model=names[row["to_player_id"]]))
            for pid, model in names.items():
                models[model].update(player_games=1, wins=pid == summary["winner_player_id"],
                    private_note_events=sum(e["type"] == "LLM_PRIVATE_THOUGHT" and e["payload"]["player_id"] == pid for e in events),
                    private_note_events_from_fallback=sum(e["type"] == "LLM_PRIVATE_THOUGHT" and e["payload"]["player_id"] == pid
                        and fallback_by_decision[e["payload"]["decision_id"]] for e in events),
                    private_note_events_nonfallback=sum(e["type"] == "LLM_PRIVATE_THOUGHT" and e["payload"]["player_id"] == pid
                        and not fallback_by_decision[e["payload"]["decision_id"]] for e in events),
                    public_message_events=sum(e["type"] == "LLM_PUBLIC_MESSAGE" and e["payload"]["player_id"] == pid for e in events),
                    public_message_events_nonempty=sum(e["type"] == "LLM_PUBLIC_MESSAGE" and e["payload"]["player_id"] == pid
                        and bool(e["payload"].get("message", "").strip()) for e in events),
                    rent_received=sum(e["payload"]["amount"] for e in events if e["type"] == "RENT_PAID" and e["payload"]["to_player_id"] == pid))
            games.append({"game": game, "run": str(run.relative_to(ROOT)), "seed": cfg["seed"],
                          "source_sha": idx["git_sha"], "treatment_fingerprint": cfg["treatment_fingerprint"],
                          "winner": names[summary["winner_player_id"]], "reason": summary["reason"],
                          "model_order": list(names.values()), "turns": summary["turn_count"],
                          "events": len(events), "decisions": len(actions), "event_types": counts,
                          "first_builder": names[first_build["payload"]["player_id"]],
                          "first_builder_won": first_build["payload"]["player_id"] == summary["winner_player_id"],
                          "config": {k: cfg[k] for k in ["treatment_version", "fallback_policy", "infrastructure_policy", "max_turns", "max_trade_exchanges", "max_auction_actions", "response_policy"]},
                          "player_configs": cfg["players"]})
            dice[cfg["seed"]].append([(e["payload"]["d1"], e["payload"]["d2"])
                                      for e in events if e["type"] == "DICE_ROLLED"])
    assert len(games) == 20 and len({g["game"] for g in games}) == 20
    for seed in dice:
        block = [g["model_order"] for g in games if g["seed"] == seed]
        assert len(block) == 4
        base = block[0]
        assert {tuple(x) for x in block} == {tuple(base[i:] + base[:i]) for i in range(4)}
        for left, right in itertools.combinations(dice[seed], 2):
            assert left[:min(len(left), len(right))] == right[:min(len(left), len(right))]
    for path in sorted(source_paths):
        sources.append({"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    trade_groups = [r for r in episodes if r["route"] == "trade"]
    group_totals = {}
    for model in NAMES.values():
        selected = [r for r in trade_groups if r["model"] == model]
        group_totals[model] = {"trade_groups": len(selected),
            "first_management_built": sum(r["built_first_management"] is True for r in selected),
            "entry_eligible": sum(r["entry_legal"] is True for r in selected),
            "entry_eligible_built": sum(r["entry_legal"] is True and r["built_first_management"] is True for r in selected),
            "eligible_during_window": sum(r["later_legal_in_window"] is True for r in selected),
            "without_access": sum(r["first_management_turn"] is None for r in selected),
            "all_group_routes": dict(Counter(r["route"] for r in episodes if r["model"] == model))}
    selected_mismatches = [m for m in mismatches if m["selected_valid_attempt"]]
    report = {"analysis_version": "sol_phase1_v1", "games": len(games), "seed_blocks": len(dice),
              "events": sum(g["events"] for g in games), "decisions": sum(g["decisions"] for g in games),
              "event_types": sum((Counter(g["event_types"]) for g in games), Counter()),
              "first_builder_wins": sum(g["first_builder_won"] for g in games),
              "trade_completion_sides": dict(Counter(t["completion_sides"] for t in trades)),
              "deed_routes": dict(Counter(a["route"] for a in acquisitions)),
              "group_routes": dict(Counter(r["route"] for r in episodes)),
              "trade_group_metrics": group_totals, "models": dict(models),
              "initial_system_prompt_sha256_counts": dict(prompt_hashes),
              "max_observed_public_memory_entries": max_public_memory,
              "max_observed_private_memory_entries": max_private_memory,
              "attempt_response_conditions": dict(response_conditions),
              "opus_decision_response_chains": dict(refusal_chains),
              "response_file_ledger_agreement": dict(raw_file_agreement),
              "response_file_ledger_differences": artifact_differences,
              "mismatch_attempts": len(mismatches),
              "selected_response_mismatches": {"total": len(selected_mismatches),
                  "structured_json": sum(m["content_format"] == "json_object" for m in selected_mismatches),
                  "exact_arguments_equal": sum(m["identical_arguments"] is True for m in selected_mismatches),
                  "stripped_public_message_equal": sum(m["same_public_message_stripped"] is True for m in selected_mismatches),
                  "stripped_public_and_private_equal": sum(m["same_public_message_stripped"] is True
                      and m["same_private_thought_stripped"] is True for m in selected_mismatches)},
              "checks": ["20 terminal ownership/cash reconciliations", "6989 ordered event/action/start/resolved identity joins",
                         "6989 exact resolved versus applied action comparisons", "5 blocks of 4 cyclic rotations", "30 common dice-prefix comparisons"],
              "semantic_review": "pending for all attempts; no exhaustive phase-2 behavior claim"}
    write_json("results.json", report)
    write_json("manifest.json", {"games": games, "sources": sources})
    write_rows("group_episodes.jsonl", episodes)
    write_rows("trade_settlements.jsonl", trades)
    write_rows("deed_acquisitions.jsonl", acquisitions)
    write_rows("attempt_inventory.jsonl", attempts)
    write_rows("decision_inventory.jsonl", decision_inventory)
    write_rows("negotiation_event_inventory.jsonl", negotiation_events)
    write_rows("response_mismatches.jsonl", mismatches)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
