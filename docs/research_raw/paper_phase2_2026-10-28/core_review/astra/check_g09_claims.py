"""G9 original accounting and menu-to-financing sequence diagnostics."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 9]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    b = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / b[0]["source_run"]
    events = rows(run / "events.jsonl")
    assert len(events) == 1550 and events[-1]["type"] == "GAME_ENDED"

    def action(n):
        return b[n]["applied_action_record"]["action"]

    def state(n):
        return b[n]["initial_prompt"]["payload"]["game_state"]

    def person(n, player=None):
        s = state(n)
        return next(p for p in [s["you"], *s["others"]]
                    if p["player_id"] == (player or s["you"]["player_id"]))

    assert sum(action(n)["action"] == "counter_trade" for n in range(147, 160)) == 11
    assert person(159)["cash"] == 553 and person(160)["cash"] == 228
    assert person(162)["cash"] == 357 and person(163)["cash"] == 417
    assert action(160)["args"]["build_plan"] == [
        {"count": 1, "kind": "HOUSE", "space_key": "VIRGINIA_AVENUE"},
        {"count": 1, "kind": "HOUSE", "space_key": "ST_CHARLES_PLACE"}]
    branches = []
    for n, expected, target in [(86, 7, "PARK_PLACE"), (103, 42, "BOARDWALK"),
                                (114, 42, "BOARDWALK"), (125, 42, "BOARDWALK")]:
        menu = b[n]["initial_prompt"]["payload"]["action_state"]
        assert "build_houses_or_hotel" not in menu["available_actions"]
        assert "mortgage_property" in menu["available_actions"]
        engine, decision = restore(run, b[n]["decision_id"])
        decision, funding = apply(engine, decision, "mortgage_property", {"space_key": "WATER_WORKS"})
        _, build = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
            {"space_key": target, "kind": "HOUSE", "count": 1}]})
        assert next(p.cash for p in engine.state.players if p.player_id == "p2") == expected
        branches.append({"decision": n, "funding": funding, "build": build, "remaining_cash": expected})
    engine, decision = restore(run, b[179]["decision_id"])
    decision, funding = apply(engine, decision, "mortgage_property", {"space_key": "NORTH_CAROLINA_AVENUE"})
    _, build = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
        {"space_key": "STATES_AVENUE", "kind": "HOUSE", "count": 1},
        {"space_key": "VIRGINIA_AVENUE", "kind": "HOUSE", "count": 1}]})
    assert next(p.cash for p in engine.state.players if p.player_id == "p1") == 14
    branches.append({"decision": 179, "funding": funding, "build": build, "remaining_cash": 14})
    for n in [194, 195]:
        assert json.loads(b[n]["attempts"][0]["assistant_content"])["name"] == "declare_bankruptcy"
        assert action(n)["action"] == "mortgage_property"
    assert "immediately" in action(197)["private_thought"]
    assert person(194, "p2")["cash"] == 48 and person(198, "p2")["cash"] == 1219
    recipient_flows = [e["payload"]["delta"] for e in b[197]["canonical_event_segment"]
                       if e["type"] == "CASH_CHANGED" and e["payload"]["player_id"] == "p2"]
    assert recipient_flows == [1171]
    fees = [e["payload"]["delta"] for n in [202, 203, 204] for e in b[n]["canonical_event_segment"]
            if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "UNMORTGAGE"]
    assert fees == [-100, -100, -111]
    assert person(184)["jail_turns"] == 2 and person(184)["get_out_of_jail_cards"] == 1
    assert all(b[n]["initial_prompt"]["payload"]["action_state"]["available_actions"] == ["roll_for_doubles"]
               for n in [172, 180])
    assert "pay_jail_fine" in b[188]["initial_prompt"]["payload"]["action_state"]["available_actions"]
    assert "Financing the light-blue" in action(191)["public_message"]
    assert action(191)["args"]["space_key"] == "TENNESSEE_AVENUE"
    assert set(p["space_key"] for p in action(192)["args"]["build_plan"]) == {
        "ORIENTAL_AVENUE", "VERMONT_AVENUE", "CONNECTICUT_AVENUE"}
    assert action(129)["action"] == action(137)["action"] == "reject_trade"
    assert "Brown monopoly" in action(129)["public_message"]
    assert state(215)["bank"]["houses_remaining"] == 1 and state(216)["bank"]["houses_remaining"] == 0
    assert all(not p["resolution"]["fallback_used"] for p in b.values())
    opus = [p for p in b.values() if p["player_id"] == "p1"]
    assert all([a["outcome"] for a in p["attempts"]] == ["refused", "valid"] for p in opus)
    assert person(220)["cash"] == 54
    profiles_source = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert profiles_source["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [r for r in profiles_source["units"] if r["game"] == 9]
    selected = {r["decision_id_zero_based_suffix"] for c in rows(HERE.parent / "candidate_catalog.jsonl")
                if c["catalog_id"].startswith("public-G09") for r in c["source_entry"]["decision_refs"]}
    selected |= {86, 103, 114, 125, 128, 129, 137, 151, 153, 154, 156, 158, 160,
                 179, 183, 184, 186, 188, 191, 192, 194, 195, 196, 197, 199, 209, 213, 215, 216, 220}
    result = {"game": 9, "checks": "passed", "scope": "Selected original channels and exact local financing, not all provider bundles reread",
              "financing_branches": branches, "branch_limits": "Real management decisions and legal immediate sequences; no improved strategy or winner inference.",
              "terminal_ceilings": [check(9, 183, 913), check(9, 194, 1171), check(9, 220, 824)],
              "recipient_bankruptcy_cash": recipient_flows, "later_orange_redemptions": fees,
              "opus_refused_then_valid": len(opus), "profiles": profiles,
              "originals": {n: b[n] for n in sorted(selected)},
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "event_sha256": digest, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g09_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "profiles": profiles,
                      "terminal_ceilings": [913, 1171, 824], "opus_valid_recoveries": len(opus)}))


if __name__ == "__main__":
    main()
