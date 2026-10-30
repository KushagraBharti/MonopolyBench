"""Enumerate all elimination events and compute nominal self-financing uppers.

This is an arithmetic screen over canonical artifacts, not semantic review or
an alternate-game experiment. Peer reports supplied the expected denominator
and exceptional decisions before this independently implemented check.
"""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from check_additional_economics import ROOT, units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def g17_payment():
    engine, decision, packet, provenance = prefix(17, 234)
    actor = decision["player_id"]
    before = engine.get_snapshot()
    steps = []
    for name, key in [
        ("sell_houses_or_hotel", "BOARDWALK"), ("sell_houses_or_hotel", "PARK_PLACE"),
        ("sell_houses_or_hotel", "BOARDWALK"), ("sell_houses_or_hotel", "PARK_PLACE"),
        ("sell_houses_or_hotel", "BOARDWALK"), ("mortgage_property", "BALTIC_AVENUE"),
        ("mortgage_property", "PARK_PLACE"),
    ]:
        args = {"sell_plan": [{"space_key": key, "kind": "HOUSE", "count": 1}]} if name == "sell_houses_or_hotel" else {"space_key": key}
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        steps.append({"action": action, "events": events})
    after = engine.get_snapshot()
    you = next(p for p in after["players"] if p["player_id"] == actor)
    assert you["cash"] == 155 and not you["bankrupt"]
    assert not engine.state.board[39].mortgaged and engine.state.board[39].owner_id == actor
    assert sum(e["payload"]["amount"] for step in steps for e in step["events"] if e["type"] == "RENT_PAID" and e["payload"]["from_player_id"] == actor) == 550
    return {**provenance, "before": before, "recorded_action": packet["applied_action_record"],
            "steps": steps, "after": after, "limits": "Stops after paying the existing550rent. No future dice, additional trading, optimality or alternate winner."}


def main():
    board = json.loads((ROOT / "contracts/data/board.json").read_text())
    spaces = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s for s in board["spaces"]}
    rows = []
    for game in range(1, 21):
        for suffix, (unit, source) in sorted(units(game).items()):
            deaths = [e for e in unit["canonical_event_segment"] if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY"]
            if not deaths:
                continue
            assert len(deaths) == 1
            actor = unit["player_id"]
            assert deaths[0]["payload"]["player_id"] == actor
            payload = unit["initial_prompt"]["payload"]
            you = payload["game_state"]["you"]
            holdings = you["holdings"]["owned"]
            scenario = payload["action_state"]["scenario"]
            mortgages = sum(spaces[h["space_key"]]["price"] // 2 for h in holdings if not h["mortgaged"])
            salvage = sum((5 if h["hotel"] else h["houses"]) * (board["house_cost_by_group"].get(spaces[h["space_key"]].get("group"), 0) // 2) for h in holdings)
            upper = you["cash"] + mortgages + salvage
            applied = unit["applied_action_record"]["action"]
            rows.append({"game": game, "suffix": suffix, "decision_id": unit["decision_id"], **source,
                         "model": unit["model"], "player_id": actor, "decision_type": unit["decision_type"],
                         "applied_action": applied, "death_event": deaths[0], "holdings": holdings,
                         "entry_cash": you["cash"], "all_clear_deed_mortgages_after_full_sales": mortgages,
                         "nominal_building_salvage": salvage, "nominal_upper_bound": upper,
                         "owed": scenario["owed_amount"], "creditor": scenario.get("owed_to_player_id"),
                         "nominal_upper_covers_current_debt": upper >= scenario["owed_amount"]})
    assert len(rows) == 60
    counts = Counter(row["applied_action"]["action"] for row in rows)
    assert counts == {"declare_bankruptcy": 56, "mortgage_property": 4}
    non_ruled_out = {(r["game"], r["suffix"]) for r in rows if r["nominal_upper_covers_current_debt"]}
    assert non_ruled_out == {(7, 339), (12, 190), (12, 249), (17, 234)}
    automatic = {(r["game"], r["suffix"]) for r in rows if r["applied_action"]["action"] != "declare_bankruptcy"}
    assert automatic == {(7, 339), (9, 197), (18, 344), (19, 225)}
    payment = g17_payment()
    report = {"eliminations": rows, "counts_by_applied_action": dict(counts), "upper_below_debt": 56,
              "not_ruled_out_by_nominal_upper": sorted(non_ruled_out), "automatic_eliminations": sorted(automatic),
              "g17_234_legal_payment": payment,
              "local_proof_reports": {"G7d339": "build_and_hotel_access.json", "G12d190": "g12_public_claim_checks.json", "G12d249": "g12_public_claim_checks.json"},
              "limits": "All60canonicalBANKRUPTCYcashmarkers enumerated, not just56declarations. Nominal upper assumes all building levels sold and clear deeds mortgaged, so upper below current debt is a sufficient impossibility test without claiming accessibility. The four remaining decisions require local routes: three existing-debt payments are legal in named reports; G7hotel stock lock permits only440against750despite1310nominal. Current-debt payment feasibility does not identify rationality, intent, long-term survival, instructions violation or alternate winner. Source-entry counts and sampled decisions are not the denominator. No new games or provider calls.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "elimination_upper_bounds.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"n": len(rows), "counts": dict(counts), "upper_below": 56,
                      "exceptions": [{k: r[k] for k in ["game", "suffix", "entry_cash", "nominal_upper_bound", "owed"]} for r in rows if r["nominal_upper_covers_current_debt"]],
                      "g17_prefix": payment["prefix_events"], "g17_after_cash": 155}, ensure_ascii=False))


if __name__ == "__main__":
    main()
