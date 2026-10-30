"""Opus phase-1 public-message attribution and within-thread exposure checks (opus_phase1_v1).

Uses only recorded prompts (decision_started prompt_payload) and canonical events.
1. Attribution: every distinct displayed public-timeline item that carries a message must
   match a canonical LLM_PUBLIC_MESSAGE by the same player in the same turn, produced by a
   decision whose applied action's primary event is the displayed event type.
2. Within-thread exposure: at every TRADE_RESPONSE decision, is the opening proposal's
   public message present in the responder's recorded public timeline? The action_state
   carries offer terms and exchange history but no messages.
Counts are availability facts, not conduct labels.

Run with the repo venv: python/.venv/bin/python docs/research_raw/paper_phase1_2026-10-28/opus/opus_exposure_checks.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from opus_reduce import HERE, game_dirs, load_jsonl  # noqa: E402

from monopoly_arena.prompting import PRIMARY_EVENT_BY_ACTION  # noqa: E402

MERGED = {"BUILDINGS_BUILT": {"build_houses_or_hotel"}, "BUILDINGS_SOLD": {"sell_houses_or_hotel"}}


def main():
    attribution, exposure = Counter(), Counter()
    for _, run, _ in game_dirs():
        events = load_jsonl(run / "events.jsonl")
        applied = {e["payload"]["decision_id"]: e["payload"]["action_name"]
                   for e in events if e["type"] == "LLM_DECISION_RESPONSE"}
        message_of = {e["payload"]["decision_id"]: e["payload"]["message"]
                      for e in events if e["type"] == "LLM_PUBLIC_MESSAGE"}
        sources = defaultdict(set)
        for e in events:
            if e["type"] == "LLM_PUBLIC_MESSAGE" and (e["payload"]["message"] or "").strip():
                sources[(e["payload"]["player_id"], e["turn_index"], e["payload"]["message"])].add(
                    applied[e["payload"]["decision_id"]])
        opening_for_request, last_response, opening = {}, None, None
        for e in events:
            if e["type"] == "LLM_DECISION_RESPONSE":
                last_response = e["payload"]["decision_id"]
            elif e["type"] == "TRADE_PROPOSED":
                opening = (e["payload"]["initiator_player_id"], message_of.get(last_response))
            elif e["type"] == "LLM_DECISION_REQUESTED" and e["payload"]["decision_type"] == "TRADE_RESPONSE_DECISION":
                opening_for_request[e["payload"]["decision_id"]] = opening
        seen = set()
        for row in load_jsonl(run / "decisions.jsonl"):
            if row["phase"] != "decision_started":
                continue
            timeline = row["prompt_payload"]["game_state"]["memory"]["public_timeline_last_20"]
            for it in timeline:
                if not it.get("message"):
                    continue
                key = (it["player_id"], it["turn_index"], it["message"], it["event_type"])
                if key in seen:
                    continue
                seen.add(key)
                acts = sources.get(key[:3])
                if not acts:
                    attribution["speaker_or_turn_mismatch"] += 1
                elif any(it["event_type"] in PRIMARY_EVENT_BY_ACTION.get(a, set()) | MERGED.get(it["event_type"], set())
                         or a in MERGED.get(it["event_type"], set()) for a in acts):
                    attribution["speaker_turn_action_match"] += 1
                else:
                    attribution["action_mismatch"] += 1
            if row["decision_type"] == "TRADE_RESPONSE_DECISION":
                op = opening_for_request.get(row["decision_id"])
                idx = row["prompt_payload"]["action_state"]["scenario"]["exchange_index"]
                bucket = "exchange_0" if idx == 0 else "exchange_1_4" if idx < 5 else "exchange_5_plus"
                if not op or not (op[1] or "").strip():
                    exposure[bucket + ":opening_message_empty"] += 1
                    continue
                visible = any(it.get("player_id") == op[0] and it.get("message") == op[1] for it in timeline)
                exposure[bucket + (":opening_visible" if visible else ":opening_not_visible")] += 1
    out = {"version": "opus_phase1_v1", "distinct_displayed_message_items": dict(attribution),
           "trade_response_opening_message_visibility": dict(exposure)}
    (HERE / "opus_exposure_checks.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
