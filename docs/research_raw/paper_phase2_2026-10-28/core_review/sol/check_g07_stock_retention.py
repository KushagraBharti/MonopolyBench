"""Stock predicates around the actual chosen hold in common sample81.

One alternative Sol upgrade is applied legally at its exact prefix. Opponent
operations are validator diagnostics only, not actions taken outside its turn.
"""

import hashlib
import json
from pathlib import Path

from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def validate(engine, player, method, plan):
    try:
        result = getattr(engine, method)(player, plan)
        return {"passes": True, "result": result}
    except ValueError as exc:
        return {"passes": False, "error": str(exc)}


def main():
    engine, decision, packet, provenance = prefix(7, 329)
    before = engine.get_snapshot()
    opponent = next(p for p in engine.state.players if p.player_id == "p3")
    sale = [{"space_index": 14, "kind": "HOTEL", "count": 1}]
    old_sale = validate(engine, opponent, "_validate_sell_plan", sale)
    own_upgrade = validate(engine, opponent, "_validate_build_plan", [{"space_index": 11, "kind": "HOTEL", "count": 1}])
    assert not old_sale["passes"] and own_upgrade["passes"]
    assert engine.state.bank.houses_remaining == 2
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": "build_houses_or_hotel", "args": {
                  "build_plan": [{"space_key": "ST_JAMES_PLACE", "kind": "HOTEL", "count": 1}]}}
    _, events, following, _ = engine.apply_action(action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
    assert engine.state.bank.houses_remaining == 6
    new_sale = validate(engine, opponent, "_validate_sell_plan", sale)
    assert new_sale["passes"]
    assert next(p["cash"] for p in engine.get_snapshot()["players"] if p["player_id"] == "p4") == 55
    # Separately restore the next actual p3 management opportunity. Do not
    # infer that an out-of-turn validator pass was itself executable at329.
    later, later_decision, later_packet, later_provenance = prefix(7, 330)
    assert later_decision["player_id"] == "p3"
    assert later_packet["decision_type"] == "POST_TURN_ACTION_DECISION"
    assert "build_houses_or_hotel" in later_packet["initial_prompt"]["payload"]["action_state"]["available_actions"]
    later_action = {"schema_version": "v1", "decision_id": later_decision["decision_id"],
                    "action": "build_houses_or_hotel", "args": {
                        "build_plan": [{"space_key": "ST_CHARLES_PLACE", "kind": "HOTEL", "count": 1}]}}
    _, later_events, _, _ = later.apply_action(later_action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in later_events), later_events
    assert later.state.bank.houses_remaining == 6
    assert next(p["cash"] for p in later.get_snapshot()["players"] if p["player_id"] == "p3") == 430
    report = {**provenance, "recorded_action": packet["applied_action_record"], "before": before,
              "opponent_hotel_sale_before": old_sale, "opponent_own_hotel_upgrade_predicate": own_upgrade,
              "legal_sol_alternative": action, "events": events, "after": engine.get_snapshot(),
              "following_decision": following, "opponent_hotel_sale_after": new_sale,
              "next_actual_management": {**later_provenance, "recorded_action": later_packet["applied_action_record"],
                                         "legal_alternative": later_action, "events": later_events,
                                         "after": later.get_snapshot()},
              "limits": "Complete329original bundle read. Actual actor is Solp4, notp1. ChosenEND retained bank2; a legal100Solorangehotel instead leaves55 and bank6, changing opponent Virginia hotel-sale validator from rejected to accepted. That329opponent check is conditional, not an action taken during Sol's turn. After Astra's access objection, a separate exact actual330prefix verifies p3POST_TURN management before fatal339: StCharleshotel100 is legal, leaves430andbank6.330fullproviderbundle unread. This establishes an intervening management opportunity and conditional stock workaround, not escape from future debt, optimality or winner effect. No changed later trajectory was replayed. Realized339liquidation forbids buying hotels and its440accessiblebound remains valid.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g07_stock_retention_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "sale_before": old_sale,
                      "sale_after": new_sale, "opponent_own_upgrade": own_upgrade}))


if __name__ == "__main__":
    main()
