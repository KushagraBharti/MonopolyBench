"""Original G11 quantities, trade directions, referents and terminal arithmetic."""

import hashlib
import json
import re
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def main():
    game = units(11)
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s for s in board["spaces"]}
    sources = []
    for suffix in [104, 122, 138, 145, 147, 148, 149, 151, 154, 155, 156, 157, 158, 159, 163, 176, 181, 182, 187, 188, 203, 210, 215, 216, 225, 228, 255, 256, 257, 258, 267, 268, 325]:
        unit, source = game[suffix]
        gs = unit["initial_prompt"]["payload"]["game_state"]
        action = unit["applied_action_record"]["action"]
        events = [e for e in unit["canonical_event_segment"] if e["type"] in {"CASH_CHANGED", "RENT_PAID", "TRADE_ACCEPTED", "PROPERTY_TRANSFERRED", "HOUSE_BUILT", "BUILDINGS_SOLD", "DICE_ROLLED", "PLAYER_MOVED"}]
        sources.append({"suffix": suffix, **source, "payload": unit["initial_prompt"]["payload"], "action": action, "events": events})
        print(suffix, json.dumps({"cash": gs["you"]["cash"], "action": action, "events": [{"seq": e["seq"], "type": e["type"], "payload": e["payload"]} for e in events]}, ensure_ascii=False))
    offer = game[215][0]["applied_action_record"]["action"]["args"]["offer"]
    offer_mortgages = sum(spaces[key]["price"] // 2 for key in offer["properties"])
    assert offer_mortgages == 290
    print("OFFERED_COLLATERAL", json.dumps({"offer": offer, "mortgage_capacity": offer_mortgages}))
    bounds = []
    for suffix in [225, 228, 325]:
        you = game[suffix][0]["initial_prompt"]["payload"]["game_state"]["you"]
        holdings = you["holdings"]["owned"]
        mortgages = sum(spaces[h["space_key"]]["price"] // 2 for h in holdings if not h["mortgaged"])
        salvage = sum((h["houses"] + (5 if h["hotel"] else 0)) * (board["house_cost_by_group"].get(spaces[h["space_key"]].get("group"), 0) // 2) for h in holdings)
        bounds.append({"suffix": suffix, "cash": you["cash"], "mortgages_after_sales": mortgages, "building_salvage": salvage, "full_bound": you["cash"] + mortgages + salvage, "has_hotels": any(h["hotel"] for h in holdings)})
    assert [b["full_bound"] for b in bounds] == [1064, 306, 753]
    print("BOUNDS", json.dumps(bounds))
    print("POST_SWAP_ORANGES", json.dumps([h for h in game[149][0]["initial_prompt"]["payload"]["game_state"]["you"]["holdings"]["owned"] if h["space_key"] in {"ST_JAMES_PLACE", "TENNESSEE_AVENUE", "NEW_YORK_AVENUE"}]))
    result = {"sources": sources, "offered_collateral": {"offer": offer, "mortgages": offer_mortgages}, "liquidation_upper_bounds": bounds,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": "Original delivered states and applied flows; liquidation figures are full nominal upper bounds, not stepwise engine access checks, especially the hotel row. No full provider-channel reading implied, no model intent or recipient reliance inferred, no counterfactual future play."}
    (HERE / "g11_public_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
