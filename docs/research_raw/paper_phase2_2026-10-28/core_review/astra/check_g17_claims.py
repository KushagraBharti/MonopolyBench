"""Selected original G17 checks, with local legal alternatives only."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 17]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]
    events = rows(run / "events.jsonl")

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def state(n):
        return packets[n]["initial_prompt"]["payload"]["game_state"]

    def cash_events(n, reason):
        return [e for e in packets[n]["canonical_event_segment"]
                if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == reason]

    assert action(132)["args"]["request"]["cash"] == 80
    assert action(138)["args"]["offer"]["cash"] == 200
    assert [(e["payload"]["player_id"], e["payload"]["delta"]) for e in cash_events(139, "TRADE_CASH")] == [("p1", -200), ("p2", 200)]
    assert "needs $300" in action(190)["private_thought"]
    assert cash_events(191, "BUILD")[0]["payload"]["delta"] == -150
    assert state(191)["you"]["cash"] == 198
    finance = [e for n in (200, 201, 202) for e in cash_events(n, "MORTGAGE")]
    assert sum(e["payload"]["delta"] for e in finance) == 330
    assert state(200)["you"]["cash"] == 504
    assert state(203)["you"]["cash"] == 834
    assert cash_events(203, "BUILD")[0]["payload"]["delta"] == -700
    assert state(204)["you"]["cash"] == 134
    grok_finance = [e for n in (212, 213, 214, 215) for e in cash_events(n, "MORTGAGE")]
    assert sum(e["payload"]["delta"] for e in grok_finance) == 305

    # The saved first menu is not the full feasible liquidation sequence.
    engine, decision = restore(run, packets[234]["decision_id"])
    assert decision["player_id"] == "p3"
    assert decision["liquidation"]["options"]["mortgageable_space_indices"] == [3]
    actor = next(p for p in engine.state.players if p.player_id == "p3")
    owned = [s for s in engine.state.board if s.owner_id == "p3"]
    assert not any(s.hotel for s in owned)
    upper = actor.cash + sum(s.houses * 100 for s in owned) + sum(s.price // 2 for s in owned if not s.mortgaged)
    assert upper == 905
    initial = engine.get_snapshot()
    steps = []
    for key in ("BOARDWALK", "PARK_PLACE", "BOARDWALK", "PARK_PLACE", "BOARDWALK"):
        decision, result = apply(engine, decision, "sell_houses_or_hotel",
                                 {"sell_plan": [{"space_key": key, "kind": "HOUSE", "count": 1}]})
        steps.append(result)
    assert actor.cash == 500
    assert set(decision["liquidation"]["options"]["mortgageable_space_indices"]) == {3, 37, 39}
    decision, result = apply(engine, decision, "mortgage_property", {"space_key": "BALTIC_AVENUE"})
    steps.append(result)
    assert actor.cash == 530
    decision, result = apply(engine, decision, "mortgage_property", {"space_key": "PARK_PLACE"})
    steps.append(result)
    assert actor.cash == 155 and not actor.bankrupt
    assert any(e["type"] == "RENT_PAID" and e["payload"]["amount"] == 550 for e in result["events"])
    assert engine.state.board[39].owner_id == "p3" and not engine.state.board[39].mortgaged

    # Two house sales are sufficient at d388. No later turn is simulated.
    engine2, decision2 = restore(run, packets[388]["decision_id"])
    actor2 = next(p for p in engine2.state.players if p.player_id == "p4")
    assert actor2.cash == 16
    decision2, two_sales = apply(engine2, decision2, "sell_houses_or_hotel",
                                {"sell_plan": [{"space_key": key, "kind": "HOUSE", "count": 1}
                                               for key in ("ORIENTAL_AVENUE", "VERMONT_AVENUE")]})
    assert actor2.cash == 16 and not actor2.bankrupt
    assert [engine2.state.board[i].houses for i in (6, 8, 9)] == [1, 1, 2]
    assert any(e["type"] == "RENT_PAID" and e["payload"]["amount"] == 50 for e in two_sales["events"])

    profiles = {}
    for player, group_indices in (("p1", (21, 23, 24)), ("p3", (37, 39)), ("p4", (6, 8, 9))):
        cost = -sum(e["payload"]["delta"] for e in events if e["type"] == "CASH_CHANGED"
                    and e["payload"]["player_id"] == player and e["payload"]["reason"] == "BUILD")
        salvage = sum(e["payload"]["delta"] for e in events if e["type"] == "CASH_CHANGED"
                      and e["payload"]["player_id"] == player and e["payload"]["reason"] == "SELL_BUILDING")
        # Their only own construction in this game is in the indicated group.
        assert all(e["payload"]["space_index"] in group_indices for e in events
                   if e["type"] in {"HOUSE_BUILT", "HOTEL_BUILT"} and e["payload"]["player_id"] == player)
        first = min(e["seq"] for e in events if e["type"] == "HOUSE_BUILT" and e["payload"]["player_id"] == player)
        rent = [e for e in events if e["type"] == "RENT_PAID" and e["payload"]["to_player_id"] == player
                and e["payload"]["space_index"] in group_indices and e["seq"] > first]
        profiles[player] = {"own_build_spend": cost, "salvage": salvage, "group_paid_rent_after_first_build": rent,
                            "receipt_sum": sum(e["payload"]["amount"] for e in rent)}
    assert {p: (r["own_build_spend"], r["salvage"], r["receipt_sum"]) for p, r in profiles.items()} == {
        "p1": (750, 375, 90), "p3": (1000, 0, 0), "p4": (600, 300, 0)}

    tennessee_bids = [(n, packets[n]["player_id"], action(n)["args"]["bid_amount"])
                      for n in range(159, 183) if action(n)["action"] == "bid_auction"]
    short_line_bids = [action(n)["args"]["bid_amount"] for n in range(269, 361)]
    assert short_line_bids == list(range(1, 93))
    assert {packets[n]["turn_index"] for n in range(268, 362)} == {92}
    assert action(361)["action"] == "drop_out"

    selected = {69, 78, 79, 107, 132, 138, 139, 156, 159, 163, 172, 182, 186, 187, 188,
                190, 191, 199, 200, 201, 202, 203, 209, 210, 211, 212, 213, 214, 215,
                216, 234, 254, 255, 256, 267, 268, 269, 361, 369, 370, 372, 380, 381,
                388, 390, 394, 396, 397, 398}
    source = {n: {"action": action(n), "initial_payload": packets[n]["initial_prompt"]["payload"],
                  "canonical_event_segment": packets[n]["canonical_event_segment"]} for n in sorted(selected)}
    text138 = [c["message"].get("reasoning") for a in packets[138]["attempts"]
               for c in (a.get("raw_response") or {}).get("choices", []) if c["message"].get("reasoning")]
    assert len(text138) == 1 and "still willing to accept $225" in text138[0]
    report = {"scope": "Selected source checks; exact local alternatives at234 and388; no later branch or winner counterfactual.",
              "gemini_liquidation": {"full_upper_bound": upper, "initial": initial, "legal_payment_steps": steps,
                                     "cash_after_paying550": 155, "unmortgaged_boardwalk_capacity_remaining": 200},
              "grok_two_house_sale_alternative": two_sales,
              "final_unavoidable_ceilings": [check(17, 267, 293), check(17, 398, 476)],
              "profiles": profiles, "sol_finance": finance, "grok_finance": grok_finance,
              "tennessee_bids": tennessee_bids, "short_line_bids": short_line_bids,
              "opus138_returned_reasoning": text138, "selected_originals": source,
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "canonical_hashes": {str((run / n).relative_to(ROOT)): hashlib.sha256((run / n).read_bytes()).hexdigest()
                                   for n in ("events.jsonl", "actions.jsonl", "run_config.json")},
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g17_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("G17: Gemini can pay550 and retain155 plus unencumbered Boardwalk; two-house sale legal; finance330/305; profiles750/375/90,1000/0/0,600/300/0.")


if __name__ == "__main__":
    main()
