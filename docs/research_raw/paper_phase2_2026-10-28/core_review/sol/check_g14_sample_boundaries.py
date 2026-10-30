"""Local recovery quantity and actual redemption calculations after G14 readings."""

import hashlib
import json
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def main():
    game = units(14)
    engine, decision, packet, provenance = prefix(14, 145)
    before = engine.get_snapshot()
    attempt = json.loads(packet["attempts"][0]["parsed_tool_call"]["arguments"])
    assert [entry["count"] for entry in attempt["build_plan"]] == [4, 4]
    assert packet["attempts"][0]["outcome"] == "illogical"
    plan = [{"space_key": key, "kind": "HOUSE", "count": 1}
            for _ in range(4) for key in ("BALTIC_AVENUE", "MEDITERRANEAN_AVENUE")]
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": "build_houses_or_hotel", "args": {"build_plan": plan}}
    _, events, _, _ = engine.apply_action(action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in events)
    assert sum(e["payload"]["count"] for e in events if e["type"] == "HOUSE_BUILT") == 8
    assert next(p["cash"] for p in engine.get_snapshot()["players"] if p["player_id"] == "p2") == 619
    actual, _, _, actual_provenance = prefix(14, 149)
    assert all(actual.state.board[i].houses == engine.state.board[i].houses == 4 for i in (1, 3))
    assert actual.state.bank.houses_remaining == engine.state.bank.houses_remaining == 14
    assert next(p["cash"] for p in actual.get_snapshot()["players"] if p["player_id"] == "p2") == 619
    actual_steps = [{"source": game[i][1], "action": game[i][0]["applied_action_record"]["action"],
                     "events": game[i][0]["canonical_event_segment"]} for i in range(145, 149)]
    assert all(len(step["action"]["args"]["build_plan"]) == 2 for step in actual_steps)
    redemption, _, redeem_packet, redeem_provenance = prefix(14, 162)
    owner = next(p for p in redemption.state.players if p.player_id == "p2")
    rents_before = {redemption.state.board[i].name: redemption._calculate_rent(redemption.state.board[i], owner, 7)
                    for i in (26, 29)}
    _, redeem_events, _, _ = redemption.apply_action(redeem_packet["applied_action_record"]["action"])
    rents_after = {redemption.state.board[i].name: redemption._calculate_rent(redemption.state.board[i], owner, 7)
                   for i in (26, 29)}
    assert rents_before == rents_after
    assert sorted(rents_before.values()) == [44, 48]
    interest = [e for e in game[161][0]["canonical_event_segment"]
                if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "MORTGAGE_INTEREST"]
    assert [e["payload"]["delta"] for e in interest] == [-13]
    assert 240 + 13 + 143 == 396
    report = {
        "recovery145": {**provenance, "source": game[145][1], "before": before,
                        "interleaved_original_allocation": action, "events": events,
                        "after": engine.get_snapshot(), "actual_four_decisions": actual_steps,
                        "actual149_prefix": actual_provenance},
        "redemption162": {**redeem_provenance, "source": game[162][1],
                          "applied": redeem_packet["applied_action_record"],
                          "clear_sibling_rents_before": rents_before, "clear_sibling_rents_after": rents_after,
                          "events": redeem_events, "transfer_interest_events": interest,
                          "total_activation_outflow": 396},
        "reading_scope": "All twelve G14 common bundles completely read.145full attempts and actual147/148actions/events inspected;147/148provider bundles unread.162applied note/menu/events and exact redemption inspected, full provider bundle unread.",
        "findings": "145retry resolves to two houses, not the original eight, in that decision. Four consecutive actual management decisions on global turn61 reach the original4/4target and619cash; a single interleaved original allocation also legally reaches those asset/cash/stock values. No global state/event equality or later trajectory asserted.162redemption activates Ventnor but does not raise already-clear Atlantic/Marvin rents.383outflow gloss at164omits13transferinterest, total396.",
        "limits": "No optimality, alternate receipts or winner result. Equal final investment target does not make current-decision recovery allocation-preserving.300equity mentioned by206is a partial component sum, not explicitly a maximum;60unlocked brown collateral is available in a fuller bound, so the partial statement alone is not a clean false proposition.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g14_sample_boundary_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"original_allocation_legal": True, "retry_houses": 2, "eventual_same_turn_houses": 8,
                      "cash_after": 619, "clear_sibling_rents_unchanged": True, "activation_total": 396}))


if __name__ == "__main__":
    main()
