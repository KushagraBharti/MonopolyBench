"""Test a recorded zero-stock liquidity forecast using legal own management only."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import HERE, prefix


def main():
    game = units(3)
    engine, decision, packet, provenance = prefix(3, 451)
    actor = decision["player_id"]
    before = engine.get_snapshot()
    assert next(p["cash"] for p in before["players"] if p["player_id"] == actor) == 94
    assert before["bank"]["houses_remaining"] == 0
    forecast_state = game[449][0]["initial_prompt"]["payload"]["game_state"]
    forecast_target = next(p for p in forecast_state["others"] if p["player_id"] == actor)
    management_target = packet["initial_prompt"]["payload"]["game_state"]["you"]
    assert forecast_target["cash"] == management_target["cash"] == 94
    assert forecast_target["holdings"] == management_target["holdings"]
    assert forecast_state["bank"] == packet["initial_prompt"]["payload"]["game_state"]["bank"]
    red_indices = {21, 23, 24}
    steps = []
    for _ in range(8):
        red = [s for s in engine.state.board if s.index in red_indices]
        maximum = max(s.houses for s in red)
        chosen = min((s for s in red if s.houses == maximum), key=lambda s: s.index)
        assert chosen.houses > 0
        key = {21: "KENTUCKY_AVENUE", 23: "INDIANA_AVENUE", 24: "ILLINOIS_AVENUE"}[chosen.index]
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": "sell_houses_or_hotel",
                  "args": {"sell_plan": [{"space_key": key, "kind": "HOUSE", "count": 1}]}}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        steps.append({"action": action, "events": events})
    intermediate = engine.get_snapshot()
    assert next(p["cash"] for p in intermediate["players"] if p["player_id"] == actor) == 694
    action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": "mortgage_property",
              "args": {"space_key": "KENTUCKY_AVENUE"}}
    _, events, decision, _ = engine.apply_action(action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
    steps.append({"action": action, "events": events})
    after = engine.get_snapshot()
    cash = next(p["cash"] for p in after["players"] if p["player_id"] == actor)
    assert cash == 804
    source = game[449]
    report = {**provenance, "initial_snapshot": before, "same_holdings_cash_jail_sample": game[450][1],
              "forecast_source": source[1], "forecast_applied_action": source[0]["applied_action_record"],
              "recorded_prefix_action": packet["applied_action_record"], "steps": steps, "after_sales": intermediate,
              "final_snapshot": after, "reachable_cash": cash,
              "claim": "At the actual post-jail management opportunity, unchanged94cash and assets can legally raise804by8redhousesalesand1mortgage, exceeding700. The earlier recorded forecast that only600redsalvage remains omits unlocked mortgages.",
              "limits": "No alternate dice, no invented debt or payment, no hotel stock relaxation, no future play. This does not claim the historical safe jail roll instead landed on Virginia, nor optimality of liquidating without a debt.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g03_hotel_liquidity_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "canonical_prefix_equal": True, "cash_before": 94,
                      "cash_after_red_sales": 694, "cash_after_one_mortgage": cash, "steps": len(steps), "claim": report["claim"], "limits": report["limits"]}))


if __name__ == "__main__":
    main()
