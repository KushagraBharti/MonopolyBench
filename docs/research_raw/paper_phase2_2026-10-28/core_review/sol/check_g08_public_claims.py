"""Inspect original G8 applied flows and delivered budgets; no future rollout."""

import hashlib
import json
import re
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def main():
    game = units(8)
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", space["name"].upper()).strip("_"): space for space in board["spaces"]}
    sources = []
    selected = [75, 77, 90, 106, 113, 147, 154, 155, 156, 157, 158, 163, 167, 170, 171, 172, 184, 194, 196, 200, 203, 209, 210, 211, 220, 249, 257, 259, 262, 267, 271, 274, 275, 280, 287]
    for suffix in selected:
        unit, source = game[suffix]
        payload = unit["initial_prompt"]["payload"]
        gs = payload["game_state"]
        action = unit["applied_action_record"]["action"]
        events = [event for event in unit["canonical_event_segment"] if event["type"] in {"CASH_CHANGED", "RENT_PAID", "TRADE_ACCEPTED", "PROPERTY_TRANSFERRED", "HOUSE_BUILT", "PROPERTY_UNMORTGAGED"}]
        sources.append({"suffix": suffix, **source, "payload": payload, "action": action, "events": events})
        print(suffix, json.dumps({"cash": gs["you"]["cash"], "other_cash": {p["player_id"]: p["cash"] for p in gs["others"]}, "action": action,
                                 "events": [{"seq": event["seq"], "type": event["type"], "payload": event["payload"]} for event in events]}, ensure_ascii=False))
    bounds = []
    for suffix in [271, 280, 287]:
        unit, source = game[suffix]
        you = unit["initial_prompt"]["payload"]["game_state"]["you"]
        holdings = you["holdings"]["owned"]
        assert not any(holding["hotel"] for holding in holdings)
        mortgages = sum(spaces[h["space_key"]]["price"] // 2 for h in holdings if not h["mortgaged"])
        salvage = sum(h["houses"] * (board["house_cost_by_group"].get(spaces[h["space_key"]].get("group"), 0) // 2) for h in holdings)
        bounds.append({"suffix": suffix, "cash": you["cash"], "clear_mortgages_after_all_sales": mortgages, "house_salvage": salvage, "full_bound": you["cash"] + mortgages + salvage, "titles": len(holdings), "source": source})
    # No transient mid-settlement ownership is treated as a durable monopoly.
    owned = {h["space_key"] for p in [game[158][0]["initial_prompt"]["payload"]["game_state"]["you"], *game[158][0]["initial_prompt"]["payload"]["game_state"]["others"]] for h in p["holdings"]["owned"]}
    print("ALL_OWNED_BEFORE_NY_SALE", json.dumps(sorted(owned)))
    print("TERMINAL_BOUNDS", json.dumps(bounds))
    assert {"ST_CHARLES_PLACE", "STATES_AVENUE", "VIRGINIA_AVENUE"} <= owned
    assert [item["full_bound"] for item in bounds] == [308, 666, 309]
    assert game[209][0]["initial_prompt"]["payload"]["game_state"]["you"]["cash"] + 575 == 675
    assert game[203][0]["initial_prompt"]["payload"]["game_state"]["you"]["cash"] == 104
    assert game[163][0]["attempts"][0]["parsed_tool_call"]["name"] == "end_turn"
    report = {"sources": sources, "all_owned_before_d158": sorted(owned), "house_only_bounds": bounds,
              "d163_complete_returned_attempts": game[163][0]["attempts"],
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": "Original states and applied flows. House-only arithmetic is a full liquidation upper bound, not a stepwise engine replay. No provider intent or future winner counterfactual."}
    (HERE / "g08_public_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
