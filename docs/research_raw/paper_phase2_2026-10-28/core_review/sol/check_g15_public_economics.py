"""G15 applied-channel, transaction and house-only bound checks.

The d57/d89/d100/d273 targets were peer-informed. Other proposition/context
checks follow Sol's initial source judgments, retained separately.
"""

import hashlib
import json
import re
from pathlib import Path

from check_additional_economics import ROOT, units

HERE = Path(__file__).resolve().parent


def main():
    game = units(15)
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s for s in board["spaces"]}
    sources = []
    numbers = [52, 54, 56, 57, 73, 74, 76, 89, 90, 91, 97, 98, 99, 100, 101,
               105, 106, 122, 148, 166, 203, 209, 221, 234, 235, 236, 237, 268, 269, 273, 276]
    for number in numbers:
        unit, source = game[number]
        sources.append({"suffix": number, **source, "payload": unit["initial_prompt"]["payload"],
                        "action": unit["applied_action_record"], "events": unit["canonical_event_segment"]})
    post_buy = game[57][0]["initial_prompt"]["payload"]
    assert post_buy["game_state"]["you"]["cash"] == 158
    assert "build_houses_or_hotel" not in post_buy["action_state"]["available_actions"]
    assert "No monopoly" in game[76][0]["applied_action_record"]["action"]["private_thought"]
    assert "completes yellow" in game[73][0]["applied_action_record"]["action"]["private_thought"]
    assert "p4 paying for 2/3 yellow while I keep Ventnor" in game[122][0]["applied_action_record"]["action"]["private_thought"]
    assert game[106][0]["initial_prompt"]["payload"]["game_state"]["you"]["cash"] == 903
    assert "Cash stays $8" in game[106][0]["applied_action_record"]["action"]["private_thought"]
    chairman_events = game[89][0]["canonical_event_segment"] + game[90][0]["canonical_event_segment"]
    payments = [e for e in chairman_events if e["type"] == "CASH_CHANGED" and e["payload"].get("delta") == -50]
    assert len(payments) == 3
    after_chairman = game[91][0]["initial_prompt"]["payload"]["game_state"]["you"]
    assert after_chairman["cash"] == 78
    assert {h["space_key"]: h["houses"] for h in after_chairman["holdings"]["owned"]} == {"PARK_PLACE": 0, "BOARDWALK": 1}
    mortgage_events = [e for n in [97, 98, 99] for e in game[n][0]["canonical_event_segment"] if e["type"] == "PROPERTY_MORTGAGED"]
    # Amounts are in the corresponding cash events; retain canonical property rows too.
    mortgage_cash = [e["payload"]["delta"] for n in [97, 98, 99] for e in game[n][0]["canonical_event_segment"] if e["type"] == "CASH_CHANGED"]
    assert mortgage_cash == [75, 70, 70] and sum(mortgage_cash) == 215
    orange = [h for h in game[101][0]["initial_prompt"]["payload"]["game_state"]["you"]["holdings"]["owned"] if h["space_key"] in {"ST_JAMES_PLACE", "TENNESSEE_AVENUE", "NEW_YORK_AVENUE"}]
    assert [h["houses"] for h in orange] == [2, 3, 3]
    bounds = []
    for number, expected in [(203, 761), (221, 645), (276, 280)]:
        unit = game[number][0]
        you = unit["initial_prompt"]["payload"]["game_state"]["you"]
        holdings = you["holdings"]["owned"]
        assert not any(h["hotel"] for h in holdings)
        mortgages = sum(spaces[h["space_key"]]["price"] // 2 for h in holdings if not h["mortgaged"])
        salvage = sum(h["houses"] * (board["house_cost_by_group"].get(spaces[h["space_key"]].get("group"), 0) // 2) for h in holdings)
        bound = you["cash"] + mortgages + salvage
        debt = unit["initial_prompt"]["payload"]["action_state"]["scenario"]["owed_amount"]
        assert bound == expected and bound < debt
        bounds.append({"suffix": number, "you": you, "clear_mortgages_after_sales": mortgages,
                       "house_salvage": salvage, "full_upper_bound": bound, "debt": debt})
    redemption = [e for e in game[273][0]["canonical_event_segment"] if e["type"] == "CASH_CHANGED"]
    assert [e["payload"]["delta"] for e in redemption] == [-111]
    builds = [e for n in [234, 235, 236, 237] for e in game[n][0]["canonical_event_segment"] if e["type"] == "HOUSE_BUILT"]
    assert sum(e["payload"]["count"] for e in builds) == 6
    report = {"sources": sources, "chairman_payments": payments, "orange_finance_events": mortgage_events,
              "orange_finance_total": 215, "after_chairman": after_chairman, "house_only_bounds": bounds,
              "new_dark_blue_houses": builds, "short_line_redemption": redemption,
              "limits": "Applied channels, prompts/state and events checked, not complete provider bundles. Initial labels retained: C004's public pair phrase remains ambiguous, but d73 private explicitly states false yellow completion; d76 privately recognizes no monopoly. C007's d122 private explicitly refers to p4's set and keeps Ventnor as own blocker, resolving the public referent against the extractor. d106 adopts seller-role/8cash language despite receiving a seller's offer with903cash. No hidden intent, stable belief, normalized-response cause, optimality or alternate winner identified.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g15_public_economics_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"bounds": bounds, "chairman_payment_count": len(payments), "orange_finance": 215, "new_dark_blue_houses": 6}, ensure_ascii=False))


if __name__ == "__main__":
    main()
