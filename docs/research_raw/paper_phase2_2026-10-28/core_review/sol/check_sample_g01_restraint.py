"""Local feasible-sale sequences at a sampled restraint decision; no future play."""

import copy
import hashlib
import json
import re
from pathlib import Path

from check_build_and_hotel_access import HERE, prefix


def liquidate(engine, decision):
    actor = decision["player_id"]
    steps = []
    while True:
        options = decision["post_turn"]["options"]
        keys = {space.index: re.sub(r"[^A-Za-z0-9]+", "_", space.name).strip("_").upper() for space in engine.state.board}
        if options["sellable_building_space_indices"]:
            index = min(options["sellable_building_space_indices"])
            name, args = "sell_houses_or_hotel", {"sell_plan": [{"space_key": keys[index], "kind": "HOUSE", "count": 1}]}
        elif options["mortgageable_space_indices"]:
            index = min(options["mortgageable_space_indices"])
            name, args = "mortgage_property", {"space_key": keys[index]}
        else:
            break
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(event["type"] == "ACTION_REJECTED" for event in events)
        steps.append({"action": action, "events": events})
    cash = next(player["cash"] for player in engine.get_snapshot()["players"] if player["player_id"] == actor)
    return {"cash": cash, "steps": steps}


def main():
    engine, decision, packet, provenance = prefix(1, 426)
    original = engine.get_snapshot()
    assert next(player["cash"] for player in original["players"] if player["player_id"] == "p4") == 488
    baseline = liquidate(copy.deepcopy(engine), copy.deepcopy(decision))
    assert baseline["cash"] == 1418
    action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": "build_houses_or_hotel", "args": {"build_plan": [{"space_key": "ATLANTIC_AVENUE", "kind": "HOUSE", "count": 1}]}}
    _, build_events, next_decision, _ = engine.apply_action(action)
    assert not any(event["type"] == "ACTION_REJECTED" for event in build_events)
    after_build = liquidate(engine, next_decision)
    assert after_build["cash"] == 1343
    report = {**provenance, "original_applied_action": packet["applied_action_record"], "initial_snapshot": original,
              "full_liquidation_without_build": baseline, "one_feasible_house": {"action": action, "events": build_events},
              "full_liquidation_after_build": after_build,
              "claim": "The sampled END preserves1418 accessible total liquidation; one legal150house reduces it75to1343. Local budget arithmetic only; no future rent, opponent action, persuasion or winner intervention.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "sample_g01_restraint_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "canonical_prefix_equal": True, "before": baseline["cash"], "after_one_house": after_build["cash"], "claim": report["claim"]}))


if __name__ == "__main__":
    main()
