"""Read-only exact source checks of G5 direction, cash and terminal claims."""

import hashlib
import json
import re
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def main():
    game = units(5)
    selected = [34, 35, 36, 60, 64, 92, 93, 104, 106, 107, 155, 159, 187, 195, 199, 200, 219, 220, 221, 222, 223, 226, 272, 273, 274, 275, 309]
    sources = []
    for suffix in selected:
        unit, source = game[suffix]
        payload = unit["initial_prompt"]["payload"]
        gs = payload["game_state"]
        sources.append({"suffix": suffix, **source, "applied": unit["applied_action_record"], "payload": payload,
                        "events": unit["canonical_event_segment"]})
        print(suffix, json.dumps({"you_cash": gs["you"]["cash"], "holdings": len(gs["you"]["holdings"]["owned"]),
                                 "others_cash": {player["player_id"]: player["cash"] for player in gs["others"]},
                                 "action": unit["applied_action_record"]["action"],
                                 "economic_events": [{"seq": event["seq"], "type": event["type"], "payload": event["payload"]} for event in unit["canonical_event_segment"] if event["type"] in {"CASH_CHANGED", "RENT_PAID", "PROPERTY_TRANSFERRED", "PROPERTY_PURCHASED"}]}, ensure_ascii=False))
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", space["name"].upper()).strip("_"): space for space in board["spaces"]}
    bounds = []
    for suffix, expected in [(226, 586), (309, 799)]:
        unit, source = game[suffix]
        you = unit["initial_prompt"]["payload"]["game_state"]["you"]
        owned = you["holdings"]["owned"]
        assert not any(holding["hotel"] for holding in owned)
        cash = you["cash"]
        mortgages = sum(spaces[holding["space_key"]]["price"] // 2 for holding in owned if not holding["mortgaged"])
        house_value = sum(holding["houses"] * (board["house_cost_by_group"].get(spaces[holding["space_key"]].get("group"), 0) // 2) for holding in owned)
        assert cash + mortgages + house_value == expected
        bounds.append({"decision_suffix": suffix, "cash": cash, "all_clear_deed_capacity": mortgages, "house_salvage": house_value, "full_bound": expected, "titles": len(owned), "source": source})
    # A prospective balance, not a claim about the current balance.
    cash = next(player["cash"] for player in game[106][0]["initial_prompt"]["payload"]["game_state"]["others"] if player["player_id"] == "p4")
    offer = game[106][0]["applied_action_record"]["action"]["args"]["offer"]["cash"]
    assert cash == 266 and offer == 475 and cash + offer == 741
    assert game[159][0]["applied_action_record"]["action"]["action"] == "pay_jail_fine"
    fines = [event for event in game[159][0]["canonical_event_segment"] if event["type"] == "CASH_CHANGED" and event["payload"].get("reason") == "JAIL_FINE"]
    assert len(fines) == 1 and fines[0]["payload"]["delta"] == -50
    report = {"sources": sources, "house_only_full_bounds": bounds, "prospective_balance": {"cash": cash, "offer": offer, "post_trade_if_accepted": cash + offer},
              "g05_d159_fine_events": fines, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": "Applied flows and delivered-state arithmetic. Bounds do not simulate legal liquidation steps; both estates have houses only. No intent or counterfactual winner claim."}
    (HERE / "g05_public_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("BOUNDS", json.dumps(bounds))


if __name__ == "__main__":
    main()
