"""Selected original G3 checks and local legal branches, without provider calls."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 3]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]
    events = rows(run / "events.jsonl")

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def payload(n):
        return packets[n]["initial_prompt"]["payload"]

    def state(n):
        return payload(n)["game_state"]

    def cash(engine, actor):
        return next(p.cash for p in engine.state.players if p.player_id == actor)

    assert action(18)["args"]["offer"] == {"cash": 250, "get_out_of_jail_cards": 0, "properties": ["BOARDWALK"]}
    assert json.loads(packets[18]["attempts"][0]["assistant_content"])["name"] == "end_turn"
    assert not next(h for h in state(120)["you"]["holdings"]["owned"] if h["space_key"] == "KENTUCKY_AVENUE")["mortgaged"]
    assert action(181)["public_message"] in [r["message"] for r in state(182)["memory"]["public_timeline_last_20"]]
    assert "$580" in action(182)["private_thought"]
    assert state(195)["you"]["cash"] == 861
    assert "keep four houses rather than hotels" in action(74)["private_thought"]
    bids = [action(n)["args"]["bid_amount"] for n in range(247, 347) if action(n)["action"] == "bid_auction"]
    assert bids == list(range(30, 128))

    branches = {}
    engine, decision = restore(run, packets[176]["decision_id"])
    decision, step = apply(engine, decision, "build_houses_or_hotel", {
        "build_plan": [{"space_key": "ATLANTIC_AVENUE", "kind": "HOUSE", "count": 1}]})
    assert cash(engine, "p3") == 54
    branches["opus176_valid_chosen_hold_alternative"] = step

    engine, decision = restore(run, packets[354]["decision_id"])
    assert engine.state.bank.houses_remaining == 0
    decision, step = apply(engine, decision, "build_houses_or_hotel", {
        "build_plan": [{"space_key": "ORIENTAL_AVENUE", "kind": "HOTEL", "count": 1}]})
    assert cash(engine, "p4") == 986 and engine.state.bank.houses_remaining == 4
    branches["sol354_hotel_legal_with_empty_house_bank"] = step

    engine, decision = restore(run, packets[364]["decision_id"])
    steps = []
    for key in ["KENTUCKY_AVENUE", "ATLANTIC_AVENUE"]:
        decision, step = apply(engine, decision, "mortgage_property", {"space_key": key})
        steps.append(step)
    decision, step = apply(engine, decision, "build_houses_or_hotel", {
        "build_plan": [{"space_key": "PARK_PLACE", "kind": "HOUSE", "count": 1}]})
    steps.append(step)
    assert cash(engine, "p1") == 83 and engine.state.bank.houses_remaining == 0
    branches["recipient364_financed_park_without_released_buildings"] = steps

    prior = next(p for p in state(449)["others"] if p["player_id"] == "p1")
    assert prior["cash"] == state(451)["you"]["cash"] == 94
    assert prior["holdings"] == state(451)["you"]["holdings"]
    assert state(449)["bank"] == state(451)["bank"]
    engine, decision = restore(run, packets[451]["decision_id"])
    steps = []
    keys = {21: "KENTUCKY_AVENUE", 23: "INDIANA_AVENUE", 24: "ILLINOIS_AVENUE"}
    for _ in range(8):
        index = max(keys, key=lambda i: engine.state.board[i].houses)
        decision, step = apply(engine, decision, "sell_houses_or_hotel", {
            "sell_plan": [{"space_key": keys[index], "kind": "HOUSE", "count": 1}]})
        steps.append(step)
    assert cash(engine, "p1") == 694
    decision, step = apply(engine, decision, "mortgage_property", {"space_key": "KENTUCKY_AVENUE"})
    steps.append(step)
    assert cash(engine, "p1") == 804
    branches["recipient451_red_sales_and_unlocked_mortgage"] = steps

    engine, decision = restore(run, packets[582]["decision_id"])
    owner = next(p for p in engine.state.players if p.player_id == "p1")
    before = engine._calculate_rent(engine.state.board[5], owner, 10)
    steps = []
    for n in [582, 583]:
        original = action(n)
        decision, step = apply(engine, decision, original["action"], original["args"])
        step["reading_rent_after"] = engine._calculate_rent(engine.state.board[5], owner, 10)
        steps.append(step)
    assert before == 100 and all(s["reading_rent_after"] == 100 for s in steps)
    branches["gemini582583_sibling_rent_unchanged"] = {"reading_before": before, "steps": steps}

    hotel_holds, rich_grok = [], []
    for n, p in packets.items():
        game_state = state(n)
        if payload(n)["action_state"]["decision_type"] != "POST_TURN_ACTION_DECISION":
            continue
        if game_state["you"]["player_id"] == "p2" and game_state["you"]["cash"] >= 1000:
            rich_grok.append(n)
        if game_state["you"]["player_id"] != "p4":
            continue
        options = payload(n)["action_state"]["scenario"]["options"]
        light_blues = [h for h in game_state["you"]["holdings"]["owned"]
                      if h["space_key"] in {"ORIENTAL_AVENUE", "VERMONT_AVENUE", "CONNECTICUT_AVENUE"}]
        if (len(light_blues) == 3 and all(h["houses"] == 4 for h in light_blues)
                and any(h["space_key"] in options["buildable_space_keys"] for h in light_blues)):
            hotel_holds.append(n)
    green_builds = [e for e in events if e["type"] in {"HOUSE_BUILT", "HOTEL_BUILT"}
                    and e["payload"]["space_index"] in {31, 32, 34}]
    assert not green_builds
    redemptions = [e for e in events if e["type"] == "PROPERTY_UNMORTGAGED"
                   and 4267 <= e["seq"] <= 4290]
    assert len(redemptions) == 3
    aggregation = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert aggregation["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    selected = {18, 19, 29, 30, 73, 74, 89, 119, 120, 130, 140, 170, 176, 181, 182, 193, 194,
                195, 233, 240, 346, 353, 354, 362, 363, 364, 384, 385, 426, 449, 451, 468,
                505, 581, 582, 583, 601}
    report = {
        "scope": "Complete extraction narrative and 22 catalog entries; selected original channels and local branches, not all original bundles.",
        "limits": "Branches test immediate legal feasibility. No invented future landing, rent receipt, persuasion effect or winner counterfactual.",
        "branches": branches, "north_carolina_bids": bids,
        "grok_postturns_with_at_least_1000": rich_grok,
        "sol_four_house_postturns_with_a_light_blue_hotel_menu": hotel_holds,
        "terminal_ceilings": [check(3, 240, 552), check(3, 426, 1074), check(3, 601, 617)],
        "railroad_redemptions": redemptions, "green_builds": green_builds,
        "profiles": [u for u in aggregation["units"] if u["game"] == 3],
        "originals": {n: {"action": action(n), "payload": payload(n),
                          "events": packets[n]["canonical_event_segment"]} for n in sorted(selected)},
        "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
        "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                          for u in units if int(u["decision_id"][-6:]) in selected},
        "canonical_event_sha256": digest,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g03_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "grok_rich_postturns": len(rich_grok),
                      "sol_legal_hotel_postturns": len(hotel_holds), "terminal_ceilings": [552, 1074, 617]}))


if __name__ == "__main__":
    main()
