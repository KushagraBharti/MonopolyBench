"""Original G12 references and legal payment sequences at two declarations.

The declaration targets and expected maxima were peer-informed before this
independently implemented engine check. This is not a blind replication.
"""

import hashlib
import json
import re
from pathlib import Path

from check_additional_economics import ROOT, units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def pay_branch(game, suffix, operations, expected_cash):
    engine, decision, packet, provenance = prefix(game, suffix)
    actor = decision["player_id"]
    before = engine.get_snapshot()
    steps = []
    rent_paid = []
    for name, key in operations:
        args = {"sell_plan": [{"space_key": key, "kind": "HOUSE", "count": 1}]} if name == "sell_houses_or_hotel" else {"space_key": key}
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        rent_paid.extend(e for e in events if e["type"] == "RENT_PAID" and e["payload"]["from_player_id"] == actor)
        steps.append({"action": action, "events": events})
    after = engine.get_snapshot()
    target = next(p for p in after["players"] if p["player_id"] == actor)
    assert target["cash"] == expected_cash and not target["bankrupt"]
    assert len(rent_paid) == 1
    return {**provenance, "before": before, "original_action": packet["applied_action_record"], "steps": steps,
            "rent_paid": rent_paid, "after": after, "final_cash": expected_cash,
            "limits": "Stops immediately after legally paying the existing debt. No subsequent dice, opponent actions, optimality or winner branch."}


def main():
    game = units(12)
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s for s in board["spaces"]}
    sources = []
    for suffix in [25, 26, 32, 61, 146, 147, 148, 149, 150, 151, 157, 158, 161, 164, 165, 168, 169, 190, 195, 196, 197, 198, 249]:
        unit, source = game[suffix]
        gs = unit["initial_prompt"]["payload"]["game_state"]
        action = unit["applied_action_record"]["action"]
        events = [e for e in unit["canonical_event_segment"] if e["type"] in {"CASH_CHANGED", "RENT_PAID", "TRADE_ACCEPTED", "PROPERTY_TRANSFERRED", "HOUSE_BUILT"}]
        sources.append({"suffix": suffix, **source, "payload": unit["initial_prompt"]["payload"], "action": action, "events": events})
        print(suffix, json.dumps({"cash": gs["you"]["cash"], "action": action, "events": [{"seq": e["seq"], "type": e["type"], "payload": e["payload"]} for e in events]}, ensure_ascii=False))
    bounds = []
    for suffix in [190, 249]:
        you = game[suffix][0]["initial_prompt"]["payload"]["game_state"]["you"]
        holdings = you["holdings"]["owned"]
        assert not any(h["hotel"] for h in holdings)
        mortgages = sum(spaces[h["space_key"]]["price"] // 2 for h in holdings if not h["mortgaged"])
        salvage = sum(h["houses"] * (board["house_cost_by_group"].get(spaces[h["space_key"]].get("group"), 0) // 2) for h in holdings)
        bounds.append({"suffix": suffix, "cash": you["cash"], "clear_deed_mortgages_after_sales": mortgages, "house_salvage": salvage, "full_bound": you["cash"] + mortgages + salvage})
    assert [b["full_bound"] for b in bounds] == [748, 613]
    sell = "sell_houses_or_hotel"
    mortgage = "mortgage_property"
    branches = [
        pay_branch(12, 190, [(sell, "KENTUCKY_AVENUE"), (sell, "INDIANA_AVENUE"), (sell, "ILLINOIS_AVENUE"),
                             (mortgage, "ILLINOIS_AVENUE"), (mortgage, "INDIANA_AVENUE")], 8),
        pay_branch(12, 249, [(sell, "VIRGINIA_AVENUE"), (sell, "ST_CHARLES_PLACE"), (sell, "STATES_AVENUE"),
                             (sell, "VIRGINIA_AVENUE"), (sell, "ST_CHARLES_PLACE")], 43),
    ]
    # Test the actual CONTENT plan separately from the received tool call.
    # This is a local legality check, not a reconstruction of intended action.
    engine, decision, packet, provenance = prefix(12, 249)
    content = json.loads(packet["attempts"][0]["assistant_content"])
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": content["name"], "args": content["parameters"]}
    _, events, _, _ = engine.apply_action(action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
    assert engine.state.board[14].houses == 1
    assert next(p["cash"] for p in engine.get_snapshot()["players"] if p["player_id"] == decision["player_id"]) == 143
    content_check = {**provenance, "action": action, "events": events,
                     "after": engine.get_snapshot(), "legal": True}
    full249 = {"source": game[249][1],
               **{k: packet[k] for k in ["initial_prompt", "attempts", "resolution", "applied_action_record", "canonical_event_segment"]},
               "reading_scope": "Complete distinct readable prompt, content, returned provider reasoning, raw tool arguments and applied channels read; opaque encrypted material unavailable.",
               "finding": "Content requests a legal two-Virginia-house sale. Received tool declares bankruptcy, while its own private argument ultimately rejects bankruptcy and recognizes staged sales. Intermediate errors remain. Same-response inconsistency and legal survival are observed; uniform omitted-mortgage reasoning, hidden intent and upstream cause are not established."}
    report = {"sources": sources, "house_only_full_bounds": bounds, "legal_payment_branches": branches,
              "content_plan_check": content_check, "full_d249_bundle": full249,
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "limits": "Peer-informed targets independently checked in original applied flows and engine. Complete d249 available bundle read; other source rows are applied-flow checks, not complete provider readings. Local debt survivability does not imply an alternate winner."}
    (HERE / "g12_public_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print("BOUNDS", json.dumps(bounds))
    print("BRANCHES", json.dumps([{k: b[k] for k in ["prefix_events", "canonical_prefix_equal", "final_cash"]} for b in branches]))


if __name__ == "__main__":
    main()
