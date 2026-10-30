"""Existing stock plus legal financing allows a build under a claimed house lock."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import HERE, prefix


def main():
    game = units(3)
    engine, decision, packet, provenance = prefix(3, 364)
    before = engine.get_snapshot()
    actor = decision["player_id"]
    target = packet["initial_prompt"]["payload"]["game_state"]["you"]
    later = next(p for p in game[365][0]["initial_prompt"]["payload"]["game_state"]["others"] if p["player_id"] == actor)
    assert target["cash"] == later["cash"] == 43
    assert target["holdings"] == later["holdings"]
    assert before["bank"]["houses_remaining"] == 1
    steps = []
    for name, args in [
        ("mortgage_property", {"space_key": "KENTUCKY_AVENUE"}),
        ("mortgage_property", {"space_key": "ATLANTIC_AVENUE"}),
        ("build_houses_or_hotel", {"build_plan": [{"space_key": "PARK_PLACE", "kind": "HOUSE", "count": 1}]}),
    ]:
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        steps.append({"action": action, "events": events})
    after = engine.get_snapshot()
    cash = next(p["cash"] for p in after["players"] if p["player_id"] == actor)
    assert cash == 83
    assert engine.state.board[37].houses == 4
    assert after["bank"]["houses_remaining"] == 0
    message = game[363][0]["applied_action_record"]["action"]["public_message"]
    recipient_memory = packet["initial_prompt"]["payload"]["game_state"]["memory"]["public_timeline_last_20"]
    assert any(row.get("message") == message for row in recipient_memory)
    report = {**provenance, "initial_snapshot": before, "recorded_chosen_action": packet["applied_action_record"],
              "adjacent_forecast_source": game[365][1], "adjacent_forecast": game[365][0]["applied_action_record"],
              "public_framing_source": game[363][1], "speaker_complete_attempts": game[363][0]["attempts"],
              "recipient_initial_prompt": packet["initial_prompt"], "recipient_complete_attempts": packet["attempts"],
              "recipient_exposure": message, "prior_recipient_applied_action_source": game[362][1],
              "prior_recipient_applied_action": game[362][0]["applied_action_record"],
              "steps": steps, "final_snapshot": after,
              "claim": "At actual d364, cash43 and one bank house allow mortgageKY110,mortgageAtlantic130,ParkPlacefourthhouse200,ending83. No stock release is required. The initial menu omits building because cash is insufficient before financing.",
              "limits": "Local legal management sequence; no subsequent dice, changed debt, fictional inventory, opponent action or winner claim. Complete available speaker363/recipient364bundles read; no explicit deceptive-intent self-report or recipient uptake identified. The cash-only58shortfall is true; the additional-stock necessity implication is false under that reading. Recipient already chose retention at362beforemessage; other influence remains unidentified. Canonical Chance22 is delivered only as ambiguous CHANCE. Both applied private and provider text interpret it as the last Chance before Park Place, so this is an underspecified-observation interpretation rather than a clean knowledge test.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g03_reachable_build_check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "canonical_prefix_equal": True, "before_cash": 43,
                      "after_cash": cash, "bank_before": 1, "bank_after": 0, "claim": report["claim"]}))


if __name__ == "__main__":
    main()
