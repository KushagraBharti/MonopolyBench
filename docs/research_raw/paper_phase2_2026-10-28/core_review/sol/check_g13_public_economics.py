"""Check G13 source interpretations and a local trade-to-build branch.

C003/C008/C011/C016/C019 were peer-informed leads before source adjudication.
Other corrections were noticed in Sol's source pass. No future play is tested.
"""

import hashlib
import json
import math
import re
from pathlib import Path

from check_additional_economics import ROOT, units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def main():
    game = units(13)
    numbers = [60, 84, 85, 87, 105, 121, 151, 159, 167, 170, 172, 174, 180, 188, 189,
               195, 196, 197, 198, 199, 208, 209, 210, 213, 243, 250, 339, 344, 345, 355]
    sources = []
    for number in numbers:
        unit, source = game[number]
        sources.append({"suffix": number, **source, "payload": unit["initial_prompt"]["payload"],
                        "action": unit["applied_action_record"], "events": unit["canonical_event_segment"]})
    assert "buy Park Place" in game[60][0]["applied_action_record"]["action"]["public_message"]
    assert "gives p2 a monopoly" in game[105][0]["applied_action_record"]["action"]["private_thought"]
    card_event = next(e for e in game[85][0]["canonical_event_segment"] if e["type"] == "TRADE_ACCEPTED")
    assert card_event["payload"]["offer"]["get_out_of_jail_cards"] == 1
    before_card = game[85][0]["initial_prompt"]["payload"]["game_state"]["you"]["get_out_of_jail_cards"]
    assert before_card == 0
    assert game[87][0]["initial_prompt"]["payload"]["game_state"]["you"]["get_out_of_jail_cards"] == 1

    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    indexed = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): i for i, s in enumerate(board["spaces"])}
    assert indexed["B_O_RAILROAD"] == 25
    assert indexed["NORTH_CAROLINA_AVENUE"] - indexed["B_O_RAILROAD"] == 7
    assert indexed["B_O_RAILROAD"] - indexed["VIRGINIA_AVENUE"] == 11
    ways = {n: sum(a + b == n for a in range(1, 7) for b in range(1, 7)) for n in range(2, 13)}
    assert ways[11] == 2 and ways[9] == 4

    you = game[213][0]["initial_prompt"]["payload"]["game_state"]["you"]
    assert you["cash"] == 228
    assert [h["space_key"] for h in you["holdings"]["owned"] if not h["mortgaged"]] == ["KENTUCKY_AVENUE", "BOARDWALK"]
    terminal_bound = you["cash"] + 110 + 200
    assert terminal_bound == 538 and terminal_bound < 950
    redemption = []
    for number in [208, 209]:
        unit = game[number][0]
        charges = [e for e in unit["canonical_event_segment"] if e["type"] == "CASH_CHANGED" and e["payload"].get("delta", 0) < 0]
        assert len(charges) == 1 and charges[0]["payload"]["delta"] == -56
        redemption.append({"suffix": number, "before_cash": unit["initial_prompt"]["payload"]["game_state"]["you"]["cash"], "charge": charges[0]})
    assert [r["before_cash"] for r in redemption] == [1045, 989]
    assert game[210][0]["initial_prompt"]["payload"]["game_state"]["you"]["cash"] == 933
    assert math.ceil(50 * 1.1) == 56

    engine, decision, packet, provenance = prefix(13, 121)
    steps = []
    for name, args in [
        ("accept_trade", {}),
        ("build_houses_or_hotel", {"build_plan": [
            {"space_key": "ST_JAMES_PLACE", "kind": "HOUSE", "count": 1},
            {"space_key": "TENNESSEE_AVENUE", "kind": "HOUSE", "count": 1}]}),
    ]:
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        steps.append({"action": action, "events": events})
    after = engine.get_snapshot()
    opus = next(p for p in after["players"] if p["player_id"] == "p1")
    assert opus["cash"] == 24
    report = {"sources": sources, "card_transfer_event": card_event,
              "distances": {"BNO_to_NC": 7, "Virginia_to_BNO": 11, "Atlantic_to_Short_Line": 9},
              "dice_ways": ways, "terminal_argon_full_bound": 538, "light_blue_redemptions": redemption,
              "trade_build_branch": {**provenance, "recorded_action": packet["applied_action_record"], "steps": steps, "after": after},
              "limits": "Original applied-channel/state/event checks, not complete provider readings for these decisions. Exact local branch accepts the140counter and builds two100houses using existing84cash. No subsequent dice, induced agreement, optimality, or alternate winner. Public172's full compound says unmortgage AND build;254cash-only covers redemption, but not a200house too; additional collateral exists, so current cash is not the full feasible set.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g13_public_economics_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"branch_prefix": provenance["prefix_events"], "two_house_final_cash": opus["cash"],
                      "argon_full_bound": 538, "light_blue_before_cash": [r["before_cash"] for r in redemption]}))


if __name__ == "__main__":
    main()
