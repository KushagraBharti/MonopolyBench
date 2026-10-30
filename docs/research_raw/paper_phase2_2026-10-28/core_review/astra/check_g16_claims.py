"""Selected G16 accounting, source-language and legal liquidation checks.

No recorded action, model prompt or canonical artifact is changed. Source
selection is informed by the two extraction catalogs; verdicts are separate.
"""

import hashlib
import json
import re
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, apply, restore, rows
from monopoly_engine.engine import HOUSE_COST_BY_GROUP

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 16]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]
    events = rows(run / "events.jsonl")

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def state(n):
        return packets[n]["initial_prompt"]["payload"]["game_state"]

    def cash_events(n, player, reason):
        return [e for e in packets[n]["canonical_event_segment"] if e["type"] == "CASH_CHANGED"
                and e["payload"]["player_id"] == player and e["payload"]["reason"] == reason]

    # Mortgage-transfer costs and post-sale finance: the stated budget is
    # reachable cash, not permission to interrupt another player's turn.
    assert state(227)["you"]["cash"] == 663
    ny_budget = 663 - 220 - 10 - 111
    assert ny_budget == 322 >= 300
    assert "which you hold unmortgaged" in action(236)["public_message"]
    assert "I'll give you Marvin Gardens" in action(236)["public_message"]
    for n in (105, 168, 191):
        assert action(n)["action"] == "reject_trade"
        assert "orange" in action(n)["private_thought"].lower()
    assert "Park Place cost $350, not $190" in action(57)["public_message"]
    assert 380 / 2 == 190
    assert any(e["type"] == "PROPERTY_PURCHASED" and e["payload"]["space_index"] == 23
               for e in packets[91]["canonical_event_segment"])

    # Canonical HOTEL events carry the transition semantics; they need no
    # separate HOUSE_SOLD events to return inventory during an upgrade.
    assert state(98)["bank"]["houses_remaining"] == state(99)["bank"]["houses_remaining"] == 32
    assert (state(98)["bank"]["hotels_remaining"], state(99)["bank"]["hotels_remaining"]) == (12, 10)
    assert len([e for e in packets[98]["canonical_event_segment"] if e["type"] == "HOUSE_BUILT"]) == 8
    assert len([e for e in packets[98]["canonical_event_segment"] if e["type"] == "HOTEL_BUILT"]) == 2
    rent232 = [e for e in packets[232]["canonical_event_segment"] if e["type"] == "RENT_PAID"]
    assert [(e["payload"]["from_player_id"], e["payload"]["amount"]) for e in rent232] == [("p4", 28)]

    # Repeated private and public assertions are propositions, not evidence of
    # a stable policy or an enforced future commitment.
    repeated = {n: action(n)["public_message"] for n in (398, 399, 404, 408, 409, 416)}
    assert len(set(repeated[n] for n in (399, 404, 408, 409, 416))) == 1
    assert repeated[398] != repeated[399]
    assert action(385)["args"]["offer"]["cash"] == 400
    assert action(384)["args"]["request"]["cash"] == 475
    assert action(386)["action"] == "accept_trade"

    # Construction accounting excludes earlier unimproved monopoly rents.
    build_outlay = -sum(e["payload"]["delta"] for e in events if e["type"] == "CASH_CHANGED"
                        and e["payload"]["player_id"] == "p2" and e["payload"]["reason"] == "BUILD")
    salvage = sum(e["payload"]["delta"] for e in events if e["type"] == "CASH_CHANGED"
                  and e["payload"]["player_id"] == "p2" and e["payload"]["reason"] == "SELL_BUILDING")
    house_rent = [e for e in events if e["type"] == "RENT_PAID"
                  and e["payload"]["to_player_id"] == "p2"
                  and ((2132 < e["seq"] < 2398) or (2845 < e["seq"] < 2954))
                  and e["payload"]["space_index"] in (37, 39)]
    assert (build_outlay, salvage, len(house_rent)) == (600, 300, 0)
    assert [state(n)["you"]["cash"] for n in (274, 275, 276)] == [419, 219, 19]
    between = [e for e in events if 2131 <= e["seq"] <= 2137 and e["type"] == "CASH_CHANGED"]
    assert [e["payload"]["delta"] for e in between] == [-200, -200]
    seller_to_buyer_rent = [e for e in events if e["type"] == "RENT_PAID"
                           and e["payload"]["from_player_id"] == "p2"
                           and e["payload"]["to_player_id"] == "p3"
                           and e["payload"]["space_index"] in (37, 39) and e["seq"] > 2989]
    assert sum(e["payload"]["amount"] for e in seller_to_buyer_rent) == 775
    inheritance_finance = [e for n in (448, 449, 450, 451) for e in cash_events(n, "p3", "MORTGAGE")]
    assert sum(e["payload"]["delta"] for e in inheritance_finance) == 355
    assert cash_events(452, "p3", "UNMORTGAGE")[0]["payload"]["delta"] == -111

    # Exact branch for a hotel estate, proving attainability of the full bound.
    engine, decision = restore(run, packets[602]["decision_id"])
    actor = decision["player_id"]
    owned = [s for s in engine.state.board if s.owner_id == actor]
    initial = engine.get_snapshot()
    components = {
        "cash": state(602)["you"]["cash"],
        "building_salvage": sum((5 if s.hotel else s.houses) * HOUSE_COST_BY_GROUP.get(s.group, 0) // 2 for s in owned),
        "all_unmortgaged_capacity": sum(s.price // 2 for s in owned if not s.mortgaged),
    }
    assert components == {"cash": 288, "building_salvage": 375, "all_unmortgaged_capacity": 730}
    ceiling = sum(components.values())
    owed = decision["liquidation"]["owed_amount"]
    assert ceiling == 1393 < owed == 2000
    steps, branch, maximum, running = [], [], 288, 288
    while decision and decision["decision_type"] == "LIQUIDATION_DECISION" and decision["player_id"] == actor:
        options = decision["liquidation"]["options"]
        if options["mortgageable_space_indices"]:
            s = engine.state.board[min(options["mortgageable_space_indices"])]
            key = re.sub(r"[^A-Za-z0-9]+", "_", s.name).strip("_").upper()
            name, args = "mortgage_property", {"space_key": key}
        elif options["sellable_building_space_indices"]:
            s = engine.state.board[min(options["sellable_building_space_indices"])]
            key = re.sub(r"[^A-Za-z0-9]+", "_", s.name).strip("_").upper()
            name, args = "sell_houses_or_hotel", {"sell_plan": [{"space_key": key, "kind": "HOTEL" if s.hotel else "HOUSE", "count": 1}]}
        else:
            break
        step = {"name": name, "args": args, "offered_options": options, "bank_houses_before": engine.state.bank.houses_remaining}
        decision, result = apply(engine, decision, name, args)
        emitted = result["events"]
        steps.append(step)
        branch.extend(emitted)
        for e in emitted:
            if e["type"] == "CASH_CHANGED" and e["payload"]["player_id"] == actor:
                running += e["payload"]["delta"]
                maximum = max(maximum, running)
        assert len(steps) < 50
    assert maximum == ceiling
    assert next(p for p in engine.state.players if p.player_id == actor).bankrupt
    assert not any(e["type"] == "RENT_PAID" and e["payload"]["from_player_id"] == actor for e in branch)

    # Exposure records describe delivery, not persuasion or agreement.
    social = {}
    for n in (335, 338, 339, 341, 344, 348, 356, 357, 359, 360, 361, 383, 386):
        social[n] = {"action": action(n), "turn": packets[n]["turn_index"],
                     "recipient_memory": state(n)["memory"]["public_timeline_last_20"]}
    selected = {56, 57, 64, 90, 91, 95, 97, 98, 99, 105, 132, 133, 145, 159, 168, 191,
                197, 205, 207, 211, 224, 225, 226, 227, 232, 234, 236, 246, 247,
                274, 275, 291, 304, 305, 317, 319, 321, 328, 367, 377, 381, 384, 385,
                398, 399, 404, 408, 409, 416, 431, 436, 442, 444, 447, 448, 449, 450,
                451, 452, 463, 468, 496, 602} | set(social)
    report = {
        "scope": "Selected original-source checks and exact immediate liquidation branches; not a complete reread of all game attempts or a winner counterfactual.",
        "new_york_offer_cash_after_purchase_interest_redemption": ny_budget,
        "opus_build_outlay": build_outlay, "opus_building_salvage": salvage,
        "opus_paid_rent_during_own_building_windows": house_rent,
        "opus_sequential_build_balances": [419, 219, 19],
        "seller_to_buyer_dark_blue_rent": seller_to_buyer_rent,
        "inheritance_finance": inheritance_finance,
        "rent_after_d232": rent232,
        "repeated_messages": repeated,
        "grok_liquidation": check(16, 447, 628),
        "gemini_liquidation": {"components": components, "ceiling": ceiling, "owed": owed,
                               "initial": initial, "legal_steps": steps, "events": branch,
                               "maximum_cash_reached": maximum},
        "social_delivery_records": social,
        "selected_actions": {n: action(n) for n in sorted(selected)},
        "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
        "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                          for u in units if int(u["decision_id"][-6:]) in selected},
        "canonical_hashes": {str((run / n).relative_to(ROOT)): hashlib.sha256((run / n).read_bytes()).hexdigest()
                             for n in ("events.jsonl", "actions.jsonl", "run_config.json")},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g16_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("G16: construction600/salvage300/no house rent; seller pays buyer775; inheritance finance355; exact ceilings628/1393; prospective/ongoing-language sources retained.")


if __name__ == "__main__":
    main()
