"""Selected G15 original accounting and exact liquidation/redeeming checks."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, apply, restore, rows
from monopoly_engine.board import PROPERTY_RENT_TABLES

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 15]
    chosen = {52, 54, 56, 57, 89, 90, 91, 95, 96, 97, 98, 99, 100, 101,
              148, 149, 203, 206, 219, 220, 221, 226, 227, 234, 235, 236,
              237, 238, 243, 268, 269, 273, 274, 276}
    packets = {int(u["decision_id"][-6:]): rows(ROOT / u["packet"])[u["packet_line"] - 1]
               for u in units if int(u["decision_id"][-6:]) in chosen}
    assert len(packets) == len(chosen)
    run = ROOT / packets[273]["source_run"]
    events = rows(run / "events.jsonl")
    accepted = [e for e in events if e["type"] == "TRADE_ACCEPTED"]
    winner_trades = [e for e in accepted if "p1" in {e["payload"]["initiator_player_id"],
                                                     e["payload"]["counterparty_player_id"]}]
    assert not winner_trades and len(accepted) == 3

    def you(n):
        return packets[n]["initial_prompt"]["payload"]["game_state"]["you"]

    def amounts(n, reason, player):
        return [e for e in packets[n]["canonical_event_segment"] if e["type"] == "CASH_CHANGED"
                and e["payload"]["reason"] == reason and e["payload"]["player_id"] == player]

    assert you(52)["cash"] == you(54)["cash"] == you(56)["cash"] == 908
    assert you(57)["cash"] == 158 < 200
    assert "couldn't afford to build" in packets[52]["applied_action_record"]["action"]["public_message"]
    chairman = amounts(89, "ELECTED_CHAIRMAN_PAY_EACH_PLAYER_50", "p3") + amounts(90, "ELECTED_CHAIRMAN_PAY_EACH_PLAYER_50", "p3")
    assert [e["payload"]["delta"] for e in chairman] == [-50, -50, -50]
    houses91 = {s["space_key"]: s["houses"] for s in you(91)["holdings"]["owned"]}
    assert houses91["PARK_PLACE"] == 0 and houses91["BOARDWALK"] == 1 and you(91)["cash"] == 78
    mortgages = [e for n in [97, 98, 99] for e in amounts(n, "MORTGAGE", "p1")]
    assert [e["payload"]["delta"] for e in mortgages] == [75, 70, 70]
    orange = ["ST_JAMES_PLACE", "TENNESSEE_AVENUE", "NEW_YORK_AVENUE"]
    before101 = {s["space_key"]: s["houses"] for s in you(101)["holdings"]["owned"]}
    before149 = {s["space_key"]: s["houses"] for s in you(149)["holdings"]["owned"]}
    assert [before101[k] for k in orange] == [2, 3, 3] and you(101)["cash"] == 34
    assert [before149[k] for k in orange] == [3, 3, 3]
    opus_build_cost = -sum(e["payload"]["delta"] for e in events if e["type"] == "CASH_CHANGED"
                          and e["payload"]["player_id"] == "p3" and e["payload"]["reason"] == "BUILD")
    opus_salvage = sum(e["payload"]["delta"] for e in events if e["type"] == "CASH_CHANGED"
                      and e["payload"]["player_id"] == "p3" and e["payload"]["reason"] == "SELL_BUILDING")
    assert (opus_build_cost, opus_salvage) == (800, 300)
    assert sum(s["houses"] for s in you(221)["holdings"]["owned"]) == 1
    assert packets[219]["initial_prompt"]["payload"]["game_state"]["bank"]["houses_remaining"] == 11
    assert sum(s["houses"] for s in you(219)["holdings"]["owned"]) == 20
    assert amounts(219, "BUILD", "p1")[0]["payload"]["delta"] == -400
    own_house_stock_after_hotel = packets[220]["initial_prompt"]["payload"]["game_state"]["bank"]["houses_remaining"]
    assert own_house_stock_after_hotel == 31
    dark_build_cost = -sum(e["payload"]["delta"] for n in [234, 235, 236, 237] for e in amounts(n, "BUILD", "p1"))
    assert dark_build_cost == 1200 and you(238)["cash"] == 394
    assert packets[221]["turn_index"] == 89 and packets[234]["turn_index"] == 92
    endpoints = [check(15, 203, 761), check(15, 221, 645), check(15, 276, 280)]
    assert [r["owed"] for r in endpoints] == [800, 950, 450]
    assert PROPERTY_RENT_TABLES[16][4] == 750 > 645
    assert PROPERTY_RENT_TABLES[16][5] == 950
    engine, decision = restore(run, packets[273]["decision_id"])
    _, redemption = apply(engine, decision, "unmortgage_property", {"space_key": "SHORT_LINE"})
    owner = next(p for p in engine.state.players if p.player_id == "p4")
    assert owner.cash == 180 and engine._count_owned("p4", "RAILROAD") == 3
    assert engine.state.board[5].mortgaged and engine.state.board[15].mortgaged
    assert not engine.state.board[35].mortgaged
    assert engine._calculate_rent(engine.state.board[35], owner, 9) == 100
    assert not [e for e in events if e["type"] == "RENT_PAID" and e["seq"] > 1961 and e["payload"]["space_index"] == 35]
    report = {
        "scope": "Selected source checks, three exact endpoint liquidation sequences and exact-prefix redemption; not full original-attempt review or a repaired full game.",
        "winner_completed_trades": 0, "game_completed_trades": 3,
        "park_cash_statement": {"pre_cash": 908, "price": 750, "remaining": 158, "house_cost": 200,
                                 "interpretation": "Acceptance does not contradict the true immediate-cash inability to build. It exceeds the separately stated700 reservation limit."},
        "chairman_payments": chairman, "post_chairman_houses": houses91, "post_chairman_cash": 78,
        "orange_mortgages": mortgages, "orange_mortgage_total": 215,
        "orange_after_d100": [2, 3, 3], "all_three_houses_first_reached_d148": True,
        "opus_construction": {"outlay": 800, "salvage_received": 300, "cost_of_remaining_house": 200,
                              "loss_on_three_sold_houses": 300,
                              "limit": "Not total strategy profit/loss; rent receipts and inherited residual value are separate."},
        "hotel_conversion": {"decision": 219, "bank_before": 11, "bank_after": 31, "houses_released": 20,
                             "cost": 400, "stated_rationale": packets[219]["applied_action_record"]["action"]["private_thought"]},
        "dark_blue_followup": {"inherited_turn": 89, "build_turn": 92, "build_decisions": [234, 235, 236, 237],
                               "new_houses": 6, "cost": 1200, "final_levels": [3, 4]},
        "liquidation_checks": endpoints,
        "short_line_redemption": redemption,
        "short_line_interpretation": "The applied private note correctly expects100 on the redeemed railroad despite two other mortgaged rails; the110 expected fee is wrong by1. No subsequent paid Short Line rent. Actual terminal ceiling280 and unchanged-schedule no-redemption ceiling291 both fall below450; no alternative-winner claim.",
        "source_units": [u for u in units if int(u["decision_id"][-6:]) in chosen],
        "packet_sha256": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                           for u in units if int(u["decision_id"][-6:]) in chosen},
        "source_sha256": {str((run / n).relative_to(ROOT)): hashlib.sha256((run / n).read_bytes()).hexdigest()
                          for n in ["events.jsonl", "actions.jsonl", "run_config.json"]},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g15_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("G15 verified: no winner trades;215 mortgage finance;2/3/3 then3/3/3; three Chairman payments;761/645/280 ceilings; redeemed Short Line rent100.")


if __name__ == "__main__":
    main()
