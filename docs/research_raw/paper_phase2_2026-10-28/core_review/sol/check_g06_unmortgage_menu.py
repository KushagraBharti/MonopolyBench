"""Check alleged bankruptcy-deed redemption restriction at its exact prefix."""

import copy
import hashlib
import json
from pathlib import Path

from check_build_and_hotel_access import HERE, prefix


def main():
    engine, decision, packet, provenance = prefix(6, 221)
    options = decision["post_turn"]["options"]
    assert 32 in options["unmortgageable_space_indices"]
    assert 39 in options["unmortgageable_space_indices"]
    assert "unmortgage_property" in [action["action"] for action in decision["legal_actions"]]
    branches = []
    for key, expected_cost in [("NORTH_CAROLINA_AVENUE", 165), ("BOARDWALK", 221)]:
        branch = copy.deepcopy(engine)
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": "unmortgage_property", "args": {"space_key": key}}
        _, events, _, _ = branch.apply_action(action)
        assert not any(event["type"] == "ACTION_REJECTED" for event in events)
        charges = [event["payload"]["delta"] for event in events if event["type"] == "CASH_CHANGED" and event["payload"].get("reason") == "UNMORTGAGE"]
        assert charges == [-expected_cost]
        branches.append({"action": action, "events": events, "cost": expected_cost})
    report = {**provenance, "original_delivered_payload": packet["initial_prompt"]["payload"], "recorded_action": packet["applied_action_record"],
              "offered_options": options, "branches": branches,
              "claim": "unmortgageable_space_keys means deeds eligible to be unmortgaged. Both NCA and BW are explicitly offered and legal at this prefix; no special bankruptcy-transfer redemption restriction exists here.",
              "limits": "Two separate local in-memory actions only; no rollout or claim redemption strategically preferable. BWcharged221ratherthanquoted220 is engine-applied arithmetic, not a benchmark change.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g06_unmortgage_menu_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "canonical_prefix_equal": True, "costs": [branch["cost"] for branch in branches], "claim": report["claim"], "limits": report["limits"]}))


if __name__ == "__main__":
    main()
