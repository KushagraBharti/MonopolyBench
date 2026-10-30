"""Read original G9 budgets, actual builds and rents for downstream adjudication."""

import hashlib
import json
import math
import re
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def main():
    game = units(9)
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s for s in board["spaces"]}
    sources = []
    for suffix in [75, 79, 85, 86, 131, 147, 159, 160, 183, 189, 191, 192, 194, 195, 196, 197, 202, 203, 204, 209, 220]:
        unit, source = game[suffix]
        gs = unit["initial_prompt"]["payload"]["game_state"]
        events = [e for e in unit["canonical_event_segment"] if e["type"] in {"CASH_CHANGED", "RENT_PAID", "PROPERTY_UNMORTGAGED", "HOUSE_BUILT", "TRADE_ACCEPTED"}]
        action = unit["applied_action_record"]["action"]
        sources.append({"suffix": suffix, **source, "payload": unit["initial_prompt"]["payload"], "action": action, "events": events})
        print(suffix, json.dumps({"cash": gs["you"]["cash"], "action": action, "events": [{"seq": e["seq"], "type": e["type"], "payload": e["payload"]} for e in events]}, ensure_ascii=False))
    bounds = []
    for suffix in [183, 194, 197, 220]:
        you = game[suffix][0]["initial_prompt"]["payload"]["game_state"]["you"]
        holdings = you["holdings"]["owned"]
        assert not any(h["hotel"] for h in holdings)
        mortgages = sum(spaces[h["space_key"]]["price"] // 2 for h in holdings if not h["mortgaged"])
        salvage = sum(h["houses"] * (board["house_cost_by_group"].get(spaces[h["space_key"]].get("group"), 0) // 2) for h in holdings)
        bounds.append({"suffix": suffix, "cash": you["cash"], "clear_deed_mortgages_after_sales": mortgages, "house_salvage": salvage, "full_bound": you["cash"] + mortgages + salvage, "titles": len(holdings)})
    print("BOUNDS", json.dumps(bounds))
    print("FLOAT_CEIL", json.dumps({str(p): {"product": p * 1.1, "ceil": math.ceil(p * 1.1)} for p in [50, 60, 90, 100, 140, 200]}))
    assert [b["full_bound"] for b in bounds[:3]] == [913, 1171, 1171]
    assert game[191][0]["applied_action_record"]["action"]["args"]["space_key"] == "TENNESSEE_AVENUE"
    assert game[192][0]["applied_action_record"]["action"]["action"] == "build_houses_or_hotel"
    result = {"sources": sources, "house_only_full_bounds": bounds,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": "Exact delivered states and canonical applied flows. House-only upper bounds, not stepwise liquidation replay. No intent, causally changed behavior or alternate winner inferred."}
    (HERE / "g09_public_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
