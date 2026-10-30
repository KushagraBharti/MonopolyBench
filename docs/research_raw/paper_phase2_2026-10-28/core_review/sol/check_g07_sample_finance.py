"""Local rival-development financing diagnostic nominated by common sample76."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import ROOT, units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def main():
    game = units(7)
    engine, decision, packet, provenance = prefix(7, 183)
    actor = decision["player_id"]
    before = engine.get_snapshot()
    assert next(p["cash"] for p in before["players"] if p["player_id"] == actor) == 719
    steps = []
    plan = [{"space_key": key, "kind": "HOUSE", "count": 1}
            for _ in range(3) for key in ["ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE"]]
    for name, args in [
        ("mortgage_property", {"space_key": "READING_RAILROAD"}),
        ("mortgage_property", {"space_key": "PENNSYLVANIA_RAILROAD"}),
        ("build_houses_or_hotel", {"build_plan": plan}),
    ]:
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        steps.append({"action": action, "events": events})
    after = engine.get_snapshot()
    cash = next(p["cash"] for p in after["players"] if p["player_id"] == actor)
    assert cash == 19
    assert [engine.state.board[i].houses for i in [11, 13, 14]] == [3, 3, 3]
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    assert board["property_rent_tables"]["16"][3] == 550
    trade = game[62][0]
    flows = [e for e in trade["canonical_event_segment"] if e["type"] in {"CASH_CHANGED", "PROPERTY_TRANSFERRED"}]
    assert [(e["payload"]["player_id"], e["payload"]["delta"]) for e in flows if e["type"] == "CASH_CHANGED"] == [("p3", -300), ("p1", 300)]
    timeline = game[77][0]["initial_prompt"]["payload"]["game_state"]["memory"]["public_timeline_last_20"]
    wrong = next(row for row in timeline if row["event_type"] == "TRADE_ACCEPTED" and row["turn_index"] == 30)
    assert "p3 gives SHORT_LINE; p1 gives $300 + WATER_WORKS" in wrong["action"]
    report = {**provenance, "sample76_source": game[182][1],
              "recorded_forecast": game[182][0]["applied_action_record"],
              "recorded183_action": packet["applied_action_record"],
              "before": before, "steps": steps, "after": after,
              "sample72_source": game[302][1], "sample72_recorded_action": game[302][0]["applied_action_record"],
              "correct_st_james_three_house_rent": 550,
              "sample82_reversed_history_source": game[77][1], "actual_trade_source": game[62][1],
              "actual_trade_flows": flows, "delivered_reversed_history": wrong,
              "limits": "The common182bundle is fully read;183adjacent applied record and exact prefix are checked, not its complete provider bundle. Two legal railroad mortgages finance nine interleaved pink houses at183, leaving19.719cash alone cannot buy900; a literal no-reachable-development ceiling would be false. The note may refer to cash-only financing preference, so intent and semantic scope remain separate. No future dice/rent/winner or optimality counterfactual.302applied500StJamesrent is wrong against current board550; historical house-level accuracy is separate.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g07_sample_finance_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "cash_after": cash, "pinks": [3, 3, 3]}))


if __name__ == "__main__":
    main()
