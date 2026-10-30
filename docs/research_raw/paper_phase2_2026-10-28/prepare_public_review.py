"""Prepare the user-authorized observable-behavior dataset for Sonnet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra"
FORBIDDEN_KEYS = {"private_thought", "your_private_thoughts_last_10", "thought",
                  "reasoning", "reasoning_details", "raw_response", "assistant_content"}


def scrub(value):
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items() if k not in FORBIDDEN_KEYS}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def project(packet, source):
    payload = packet["initial_prompt"]["payload"]
    action = packet["applied_action_record"]["action"]
    events = []
    for event in packet["canonical_event_segment"]:
        if event["type"] == "LLM_PRIVATE_THOUGHT":
            continue
        public_event = {k: event[k] for k in ("event_id", "seq", "turn_index", "actor", "type", "payload")}
        if event["type"] == "LLM_DECISION_RESPONSE":
            public_event["payload"] = {k: v for k, v in event["payload"].items() if k != "error"}
            public_event["payload"]["error_present"] = bool(event["payload"].get("error"))
        events.append(scrub(public_event))
    return {"version": "observable_review_v1", "game": packet["game"],
            "decision_id": packet["decision_id"], "turn_index": packet["turn_index"],
            "player_id": packet["player_id"], "model": packet["model"],
            "decision_type": packet["decision_type"],
            "applied_action": {k: scrub(action[k]) for k in ("action", "args", "public_message") if k in action},
            "observation": scrub(payload["game_state"]), "action_state": scrub(payload["action_state"]),
            "events": events,
            "attempt_metadata": [{"attempt_index": a["attempt_index_zero_based"], "outcome": a["outcome"],
                                  "response_condition": a["response_condition"],
                                  "validation_error_count": len(a["validation_errors"] or [])}
                                 for a in packet["attempts"]],
            "retry_used": packet["resolution"]["retry_used"],
            "fallback_used": packet["resolution"]["fallback_used"],
            "source_packet": source["path"], "source_packet_line": source["line"],
            "source_run": packet["source_run"], "source_lines": packet["source_lines"]}


def assert_public(value):
    if isinstance(value, dict):
        assert not (set(value) & FORBIDDEN_KEYS)
        assert value.get("type") != "LLM_PRIVATE_THOUGHT"
        for child in value.values():
            assert_public(child)
    elif isinstance(value, list):
        for child in value:
            assert_public(child)


def main():
    manifest = json.loads((SOURCE / "review_packet_manifest.json").read_text())
    games = {}
    total_events = private_events = decisions = public_messages = 0
    for entry in manifest["packets"]:
        for line_number, line in enumerate((ROOT / entry["path"]).read_text().splitlines(), 1):
            packet = json.loads(line)
            output = project(packet, {"path": entry["path"], "line": line_number})
            assert_public(output)
            total_events += len(packet["canonical_event_segment"])
            private_events += sum(e["type"] == "LLM_PRIVATE_THOUGHT" for e in packet["canonical_event_segment"])
            public_messages += sum(e["type"] == "LLM_PUBLIC_MESSAGE" for e in output["events"])
            assert len(output["events"]) == sum(e["type"] != "LLM_PRIVATE_THOUGHT"
                                                for e in packet["canonical_event_segment"])
            assert output["applied_action"].get("public_message") == packet["applied_action_record"]["action"].get("public_message")
            games.setdefault(packet["game"], []).append(output)
            decisions += 1
    assert decisions == 6989 and total_events == 50918 and len(games) == 20
    destination = HERE / "public_review"
    destination.mkdir(exist_ok=True)
    files = []
    for game, records in sorted(games.items()):
        target = destination / f"game-{game:02d}.jsonl"
        body = "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in records)
        target.write_text(body)
        files.append({"game": game, "path": str(target.relative_to(ROOT)), "decisions": len(records),
                      "sha256": hashlib.sha256(body.encode()).hexdigest()})
    report = {"version": "observable_review_v1", "user_authorized_scope": "Actions, public dialogue, legal options and financial records only",
              "decisions": decisions, "games": 20, "public_message_events": public_messages,
              "included_events": total_events - private_events, "excluded_private_note_events": private_events,
              "excluded_channels": ["model private notes and memory", "provider content and reasoning", "raw response files"],
              "semantic_review": "not_performed_by_this_preparation", "files": files}
    (destination / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "files"}))


if __name__ == "__main__":
    main()
