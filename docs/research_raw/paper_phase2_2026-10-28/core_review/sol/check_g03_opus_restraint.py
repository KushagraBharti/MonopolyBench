"""One affordable Opus build versus a valid chosen END after a provider refusal."""

import hashlib
import json
from pathlib import Path

from check_build_and_hotel_access import HERE, prefix


def main():
    engine, decision, packet, provenance = prefix(3, 176)
    before = engine.get_snapshot()
    actual = packet["resolution"]
    assert actual["fallback_used"] is False
    assert actual["final_action"]["action"] == "end_turn"
    assert [a["outcome"] for a in packet["attempts"]] == ["refused", "valid"]
    actor = decision["player_id"]
    assert next(p["cash"] for p in before["players"] if p["player_id"] == actor) == 204
    action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": "build_houses_or_hotel",
              "args": {"build_plan": [{"space_key": "ATLANTIC_AVENUE", "kind": "HOUSE", "count": 1}]}}
    _, events, following, _ = engine.apply_action(action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
    after = engine.get_snapshot()
    cash = next(p["cash"] for p in after["players"] if p["player_id"] == actor)
    assert cash == 54
    result = {**provenance, "initial_snapshot": before, "original_attempts": packet["attempts"], "original_resolution": actual,
              "one_legal_build_action": action, "one_legal_build_events": events, "after_build": after, "following_decision": following,
              "claim": "Opus chose a valid END on its action-only retry; an affordable Atlantic house would have legally changed204cash to54. This is a chosen nonbuild, not an engine default.",
              "limits": "The retry's readable content and provider explanation are available but no applied private note. No future rents, liquidation optimization or winner counterfactual.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g03_opus_restraint_check.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "canonical_prefix_equal": True, "build_cash": cash, "actual": "valid END", "claim": result["claim"]}))


if __name__ == "__main__":
    main()
