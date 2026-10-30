"""Peer-informed G16 checks with independently restored canonical prefixes."""

import hashlib
import json
import re
from pathlib import Path

from check_additional_economics import units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def main():
    game = units(16)
    engine, decision, packet, provenance = prefix(16, 602)
    actor = decision["player_id"]
    before = engine.get_snapshot()
    assert before["bank"]["houses_remaining"] == 32
    steps = []
    estate = []
    for _ in range(40):
        if next(p["bankrupt"] for p in engine.get_snapshot()["players"] if p["player_id"] == actor):
            break
        options = decision["liquidation"]["options"]
        sellable = options["sellable_building_space_indices"]
        mortgageable = options["mortgageable_space_indices"]
        if sellable:
            space = engine.state.board[sellable[0]]
            name = "sell_houses_or_hotel"
            key = re.sub(r"[^A-Z0-9]+", "_", space.name.upper()).strip("_")
            args = {"sell_plan": [{"space_key": key, "kind": "HOTEL" if space.hotel else "HOUSE", "count": 1}]}
        elif mortgageable:
            name = "mortgage_property"
            space = engine.state.board[mortgageable[0]]
            args = {"space_key": re.sub(r"[^A-Z0-9]+", "_", space.name.upper()).strip("_")}
        else:
            raise AssertionError("No further action before expected automatic elimination")
        action = {"schema_version": "v1", "decision_id": decision["decision_id"], "action": name, "args": args}
        _, events, decision, _ = engine.apply_action(action)
        assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
        estate.extend(e for e in events if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY_CASH" and e["payload"]["delta"] > 0)
        steps.append({"action": action, "events": events, "bank": engine.get_snapshot()["bank"]})
    assert len(estate) == 1 and estate[0]["payload"]["delta"] == 1393
    proceeds = [e["payload"]["delta"] for step in steps for e in step["events"] if e["type"] == "CASH_CHANGED" and e["payload"]["player_id"] == actor and e["payload"]["delta"] > 0]
    assert sum(proceeds) == 1105

    # Track the two deeds' owner and level through canonical event segments.
    # Inherited buildings retain level on PROPERTY_TRANSFERRED; no invented build.
    owner = {37: None, 39: None}
    level = {37: 0, 39: 0}
    built = []
    sold = []
    developed_rents = []
    all_sources = []
    for number, (unit, source) in sorted(game.items()):
        for event in unit["canonical_event_segment"]:
            payload = event["payload"]
            space = payload.get("space_index")
            if space not in owner:
                continue
            kind = event["type"]
            if kind == "PROPERTY_PURCHASED":
                owner[space] = payload["player_id"]
            elif kind == "PROPERTY_TRANSFERRED":
                owner[space] = payload["to_player_id"]
            elif kind == "HOUSE_BUILT":
                level[space] += payload["count"]
                if owner[space] == "p2":
                    built.append({"suffix": number, "source": source, "event": event})
            elif kind == "HOUSE_SOLD":
                level[space] -= payload["count"]
                if owner[space] == "p2":
                    sold.append({"suffix": number, "source": source, "event": event})
            elif kind == "HOTEL_BUILT":
                level[space] = 5
            elif kind == "HOTEL_SOLD":
                level[space] = 4
            elif kind == "RENT_PAID" and payload["to_player_id"] == "p2" and level[space] > 0:
                developed_rents.append({"suffix": number, "event": event})
        if number in {274, 275, 602}:
            all_sources.append({"suffix": number, **source, **{k: unit[k] for k in ["initial_prompt", "attempts", "resolution", "applied_action_record", "canonical_event_segment"]}})
    assert sum(row["event"]["payload"]["count"] for row in built) == 3
    assert sum(row["event"]["payload"]["count"] for row in sold) == 3
    assert not developed_rents
    report = {"liquidation": {**provenance, "before": before, "recorded_declaration": packet["applied_action_record"], "steps": steps, "estate_cash": estate[0], "after": engine.get_snapshot()},
              "sources": all_sources, "opus_dark_blue_builds": built, "opus_dark_blue_sales": sold,
              "opus_developed_dark_blue_paid_rent": developed_rents, "construction_cost": 600, "salvage": 300,
              "limits": "Targets and expected quantities peer-informed; exact replay and event accounting independently implemented. d274/275 returned reasoning and applied actions read: d275 explicitly acknowledges19cash risk and chooses further building with sale/mortgage backup. This is a changed reserve choice, not identified forgetting. Complete stored bundles are preserved for references, but initial-prompt histories and all attempt fields have not all been semantically read for274/275/602. d602 applied-private total1393is correct; extractor1233omits160unlockedLBmortgages. Debt2000already exceeds full reachable1393, so the local liquidation ends at automatic bankruptcy; no later dice, changed inventory, alternate winner, or ex-ante optimality inference.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g16_liquidity_and_development_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"prefix_events": provenance["prefix_events"], "steps": len(steps), "accessible": 1393,
                      "builds": built, "sales": sold, "developed_paid_rent": developed_rents}, ensure_ascii=False))


if __name__ == "__main__":
    main()
