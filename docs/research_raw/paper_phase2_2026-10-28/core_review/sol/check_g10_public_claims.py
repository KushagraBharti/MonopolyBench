"""Check G10 original references, mixed-asset flows and terminal upper bounds."""

import hashlib
import json
import re
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def main():
    game = units(10)
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s for s in board["spaces"]}
    sources = []
    for suffix in [20, 21, 37, 39, 40, 43, 49, 50, 59, 77, 92, 104, 106, 110, 112, 113, 125, 126, 127, 181, 183, 184, 188, 193, 198]:
        unit, source = game[suffix]
        gs = unit["initial_prompt"]["payload"]["game_state"]
        action = unit["applied_action_record"]["action"]
        events = [e for e in unit["canonical_event_segment"] if e["type"] in {"CASH_CHANGED", "RENT_PAID", "TRADE_ACCEPTED", "PROPERTY_TRANSFERRED", "HOUSE_BUILT", "HOTEL_BUILT"}]
        sources.append({"suffix": suffix, **source, "payload": unit["initial_prompt"]["payload"], "action": action, "events": events})
        print(suffix, json.dumps({"cash": gs["you"]["cash"], "position": gs["you"]["position"], "other_cash_position": {p["player_id"]: [p["cash"], p["position"]] for p in gs["others"]}, "action": action, "events": [{"seq": e["seq"], "type": e["type"], "payload": e["payload"]} for e in events]}, ensure_ascii=False))
    bounds = []
    for suffix in [188, 193, 198]:
        you = game[suffix][0]["initial_prompt"]["payload"]["game_state"]["you"]
        holdings = you["holdings"]["owned"]
        assert not any(h["hotel"] for h in holdings)
        mortgages = sum(spaces[h["space_key"]]["price"] // 2 for h in holdings if not h["mortgaged"])
        salvage = sum(h["houses"] * (board["house_cost_by_group"].get(spaces[h["space_key"]].get("group"), 0) // 2) for h in holdings)
        bounds.append({"suffix": suffix, "cash": you["cash"], "clear_deed_mortgages_after_sales": mortgages, "house_salvage": salvage, "full_bound": you["cash"] + mortgages + salvage, "titles": len(holdings)})
    print("BOUNDS", json.dumps(bounds))
    target = next(p for p in game[181][0]["initial_prompt"]["payload"]["game_state"]["others"] if p["player_id"] == "p1")
    assert target["position"] == "PACIFIC_AVENUE"
    assert not any(h["space_key"] == "PACIFIC_AVENUE" for h in target["holdings"]["owned"])
    assert bounds[0]["house_salvage"] == 300
    assert game[40][0]["applied_action_record"]["action"]["action"] == "accept_trade"
    result = {"sources": sources, "house_only_full_bounds": bounds, "pacific_location_target": target,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": "Original delivered states and applied flows only. Liquidation upper bounds with houses, no stepwise replay or future outcome branch. No recipient uptake, honesty or optimal strategy inferred."}
    (HERE / "g10_public_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
