"""Adjacent-to-sample local reserve choice with reachable financed development."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import ROOT, units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def full_upper(engine, actor):
    costs = json.loads((ROOT / "contracts/data/board.json").read_text())["house_cost_by_group"]
    snapshot = engine.get_snapshot()
    cash = next(p["cash"] for p in snapshot["players"] if p["player_id"] == actor)
    mortgages = sum(s.price // 2 for s in engine.state.board if s.owner_id == actor and not s.mortgaged)
    houses = sum(s.houses * (costs[s.group] // 2) for s in engine.state.board if s.owner_id == actor and s.houses)
    assert not any(s.hotel for s in engine.state.board if s.owner_id == actor)
    return cash + mortgages + houses


def main():
    game = units(6)
    engine, decision, packet, provenance = prefix(6, 191)
    actor = decision["player_id"]
    before = engine.get_snapshot()
    old_upper = full_upper(engine, actor)
    assert old_upper == 800
    steps = []
    for name, args in [
        ("mortgage_property", {"space_key": "PACIFIC_AVENUE"}),
        ("build_houses_or_hotel", {"build_plan": [{"space_key": "KENTUCKY_AVENUE", "kind": "HOUSE", "count": 1}]}),
    ]:
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        steps.append({"action": action, "events": events})
    new_upper = full_upper(engine, actor)
    assert new_upper == 725
    report = {**provenance, "before": before, "recorded_action": packet["applied_action_record"],
              "adjacent_sample190_source": game[190][1], "steps": steps, "after": engine.get_snapshot(),
              "upper_before": old_upper, "upper_after": new_upper,
              "limits": "Original191applied note and adjacent sample190complete bundle read;191full provider bundle not read. One legal150house is reachable through a150Pacific mortgage and reduces nominal full liquidation equity by75. This tests the recorded reserve rationale against existing750/800orange rent thresholds, without inventing an actual debt, new dice, changed inventory, optimality or alternate winner. Bank8houses is not zero and does not alone establish a denied rival build.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g06_reserve_bound_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "before": old_upper, "after": new_upper}))


if __name__ == "__main__":
    main()
