"""Applied-flow and house-only liquidation checks for G14 source claims."""

import hashlib
import json
import re
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def main():
    game = units(14)
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s for s in board["spaces"]}
    sources = []
    for number in [93, 94, 137, 138, 139, 140, 161, 162, 209, 222, 225, 234]:
        unit, source = game[number]
        sources.append({"suffix": number, **source, "payload": unit["initial_prompt"]["payload"],
                        "action": unit["applied_action_record"], "events": unit["canonical_event_segment"]})
    first = game[94][0]
    events = first["canonical_event_segment"]
    assert [(e["payload"]["player_id"], e["payload"]["delta"]) for e in events if e["type"] == "CASH_CHANGED"] == [("p3", -200), ("p2", 200)]
    assert [(e["payload"]["space_index"], e["payload"]["to_player_id"]) for e in events if e["type"] == "PROPERTY_TRANSFERRED"] == [(3, "p2"), (1, "p3")]
    recipient = game[94][0]["applied_action_record"]["action"]["private_thought"]
    assert "keeps the brown group split" in recipient
    assert "completes my brown set" in game[93][0]["applied_action_record"]["action"]["private_thought"]
    later = game[139][0]
    cash = [(e["payload"]["player_id"], e["payload"]["delta"]) for e in later["canonical_event_segment"] if e["type"] == "CASH_CHANGED"]
    assert cash == [("p2", -100), ("p3", 100)]
    memory = game[140][0]["initial_prompt"]["payload"]["game_state"]["memory"]["public_timeline_last_20"]
    accepted_rows = [row for row in memory if row["event_type"] == "TRADE_ACCEPTED"]
    assert any("p3 gives $100" in row["action"] and "p2 gives MEDITERRANEAN_AVENUE" in row["action"] for row in accepted_rows)
    bounds = []
    for number, expected in [(209, 346), (222, 522), (234, 907)]:
        unit = game[number][0]
        you = unit["initial_prompt"]["payload"]["game_state"]["you"]
        holdings = you["holdings"]["owned"]
        assert not any(h["hotel"] for h in holdings)
        mortgages = sum(spaces[h["space_key"]]["price"] // 2 for h in holdings if not h["mortgaged"])
        salvage = sum(h["houses"] * (board["house_cost_by_group"].get(spaces[h["space_key"]].get("group"), 0) // 2) for h in holdings)
        bound = you["cash"] + mortgages + salvage
        debt = unit["initial_prompt"]["payload"]["action_state"]["scenario"]["owed_amount"]
        assert bound == expected and bound < debt
        estate = [e for e in unit["canonical_event_segment"] if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY_CASH" and e["payload"]["delta"] > 0]
        assert len(estate) == 1 and estate[0]["payload"]["delta"] == you["cash"]
        bounds.append({"suffix": number, "cash": you["cash"], "clear_deed_mortgages_after_sales": mortgages,
                       "house_salvage": salvage, "full_upper_bound": bound, "debt": debt, "estate_cash_event": estate[0]})
    report = {"sources": sources, "bounds": bounds, "delivered_reversed_counter_accept": accepted_rows,
              "limits": "Applied channels, state and canonical flows only, not complete provider bundles. G14d222 target was peer-informed. House-only full arithmetic upper bounds suffice to rule out self-liquidation payment; no counterfactual play. Complete transaction boundary separates split browns from transient ownership between two transfer events. Timeline misdescription is exposure, not identified reliance or causal confusion.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g14_public_economics_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"bounds": bounds, "accepted_memory": accepted_rows}, ensure_ascii=False))


if __name__ == "__main__":
    main()
