"""Local legal hotel conversion beside a recorded choice to retain houses."""

import hashlib
import json
from pathlib import Path

from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def main():
    engine, decision, packet, provenance = prefix(5, 300)
    before = engine.get_snapshot()
    actor = decision["player_id"]
    assert before["bank"]["houses_remaining"] == 5
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": "build_houses_or_hotel",
              "args": {"build_plan": [{"space_key": "ST_CHARLES_PLACE", "kind": "HOTEL", "count": 1}]}}
    _, events, _, _ = engine.apply_action(action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
    after = engine.get_snapshot()
    you = next(p for p in after["players"] if p["player_id"] == actor)
    assert you["cash"] == 337
    assert after["bank"]["houses_remaining"] == 9
    assert engine.state.board[11].hotel
    assert packet["applied_action_record"]["action"]["action"] == "end_turn"
    assert not packet["resolution"]["fallback_used"]
    report = {**provenance, "original_complete_bundle": {k: packet[k] for k in ["initial_prompt", "attempts", "resolution", "applied_action_record", "canonical_event_segment"]},
              "before": before, "diagnostic_action": action, "events": events, "after": after,
              "claim": "At G5d300 a legal100hotel conversion would release4houses and leave337cash; the actual valid chosenEND retains24houses with an explicit house-retention rationale.",
              "limits": "No future play, optimality, actual denied rival build or winner effect. Bank already has5houses. Recorded motive and optional conversion do not establish binding supply denial. Complete available original bundle was read as common sample53; no available provider reasoning beyond applied private at this decision.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g05_hotel_restraint_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "cash_after": 337, "bank_before": 5, "bank_after": 9}))


if __name__ == "__main__":
    main()
