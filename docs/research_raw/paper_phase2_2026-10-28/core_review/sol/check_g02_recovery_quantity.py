"""A recovered build decision need not preserve the rejected purchase quantity."""

import copy
import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import HERE, prefix


def balances(engine):
    state = engine.get_snapshot()
    return {"cash": next(player["cash"] for player in state["players"] if player["player_id"] == "p2"),
            "yellow_houses": {space["index"]: space["houses"] for space in state["board"] if space["index"] in {26, 27, 29}},
            "bank_houses": state["bank"]["houses_remaining"]}


def apply(engine, decision, name, args):
    action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
    _, events, following, _ = engine.apply_action(action)
    assert not any(event["type"] == "ACTION_REJECTED" for event in events)
    return events, following


def main():
    engine, decision, packet, provenance = prefix(2, 243)
    first = json.loads(packet["attempts"][0]["parsed_tool_call"]["arguments"])["build_plan"]
    assert [entry["count"] for entry in first] == [2, 2, 3]
    remaining = [entry["count"] for entry in first]
    interleaved = []
    while any(remaining):
        for index, entry in enumerate(first):
            if remaining[index]:
                interleaved.append({**entry, "count": 1})
                remaining[index] -= 1
    seven = copy.deepcopy(engine)
    seven_events, _ = apply(seven, decision, "build_houses_or_hotel", {"build_plan": interleaved})
    seven_result = balances(seven)
    assert seven_result["cash"] == 208 and seven_result["yellow_houses"] == {26: 2, 27: 2, 29: 3}
    actual_events, following = apply(engine, decision, "build_houses_or_hotel", packet["applied_action_record"]["action"]["args"])
    three_result = balances(engine)
    assert three_result["cash"] == 808
    next_packet, next_source = units(2)[244]
    next_events, _ = apply(engine, following, "build_houses_or_hotel", next_packet["applied_action_record"]["action"]["args"])
    six_result = balances(engine)
    assert six_result["cash"] == 358 and six_result["yellow_houses"] == {26: 2, 27: 2, 29: 2}
    report = {**provenance, "original_rejected_plan": first, "interleaved_original_plan": interleaved,
              "initial_validation_errors": packet["attempts"][0]["validation_errors"],
              "seven_house_local_branch": {"result": seven_result, "events": seven_events},
              "actual_corrective_three": {"result": three_result, "events": actual_events},
              "actual_following_three": {"source": next_source, "result": six_result, "events": next_events},
              "claim": "Corrective retry applies a legal three-house plan, not the initially requested seven. Following decision adds three, leaving six. The identical original seven purchases are legal and affordable if interleaved.",
              "limits": "Exact local-prefix legality and actual purchase quantities only. No future rents, optimality, persuasion, or winner effect tested.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g02_recovery_quantity_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "canonical_prefix_equal": True, "seven": seven_result, "actual_three_then_three": six_result, "claim": report["claim"], "limits": report["limits"]}))


if __name__ == "__main__":
    main()
