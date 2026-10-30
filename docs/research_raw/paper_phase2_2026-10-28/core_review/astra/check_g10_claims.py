"""Read-only G10 settlement, recovery, access, and terminal-threshold checks."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 10]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    b = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / b[0]["source_run"]
    events = rows(run / "events.jsonl")
    assert len(events) == 1402 and events[-1]["payload"]["winner_player_id"] == "p2"

    def action(n):
        return b[n]["applied_action_record"]["action"]

    def state(n):
        return b[n]["initial_prompt"]["payload"]["game_state"]

    def person(n, pid=None):
        s = state(n)
        return next(p for p in [s["you"], *s["others"]]
                    if p["player_id"] == (pid or s["you"]["player_id"]))

    assert person(39)["cash"] == 404 and person(43)["cash"] == 154
    assert person(44)["cash"] == 414
    assert json.loads(b[39]["attempts"][0]["assistant_content"])["name"] == "end_turn"
    assert action(39)["action"] == "propose_trade"
    assert "Don't send it. End turn." in action(39)["private_thought"]
    trade_flows = [e["payload"]["delta"] for n in [40, 43] for e in b[n]["canonical_event_segment"]
                   if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "TRADE_CASH"
                   and e["payload"]["player_id"] == "p3"]
    assert trade_flows == [-250, 260] and sum(trade_flows) == 10
    assert sum(action(n)["action"] == "counter_trade" for n in range(72, 78)) == 4
    assert [action(n)["action"] for n in range(87, 93)] == [
        "propose_trade", "reject_trade", "propose_trade", "counter_trade", "counter_trade", "accept_trade"]
    assert "Do not sell TN/NY" in action(92)["private_thought"]
    assert person(104, "p1")["cash"] == 654 and person(105)["cash"] == 404
    assert [a["outcome"] for a in b[106]["attempts"]] == ["illogical", "valid"]
    plans = [json.loads(a["parsed_tool_call"]["arguments"])["build_plan"] for a in b[106]["attempts"]]
    totals = [Counter({}) for _ in plans]
    for total, plan in zip(totals, plans, strict=True):
        for item in plan:
            total[item["space_key"]] += item["count"]
    assert totals[0] == totals[1] and sum(totals[0].values()) == 9
    engine, decision = restore(run, b[106]["decision_id"])
    _, recovery = apply(engine, decision, "build_houses_or_hotel", {"build_plan": plans[1]})
    assert next(p.cash for p in engine.state.players if p.player_id == "p1") == 64

    assert person(181, "p1")["position"] == "PACIFIC_AVENUE"
    assert any(d["space_key"] == "PACIFIC_AVENUE" for d in person(181, "p4")["holdings"]["owned"])
    assert person(188)["cash"] == 232 and "only $300" in action(188)["private_thought"]
    fees = [e["payload"]["delta"] for n in [189, 190] for e in b[n]["canonical_event_segment"]
            if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "UNMORTGAGE"]
    assert fees == [-122, -122]
    # No invented post-auction management slot: the next actual p4 management
    # follows the railroad debt. Off-group collateral cannot fund one green house.
    p4_management = [n for n, p in b.items() if n > 170 and p["player_id"] == "p4"
                     and p["initial_prompt"]["payload"]["action_state"]["decision_type"] == "POST_TURN_ACTION_DECISION"]
    assert p4_management == [187] and person(187)["cash"] == 28
    engine, decision = restore(run, b[187]["decision_id"])
    funding = []
    for key in ["MEDITERRANEAN_AVENUE", "ATLANTIC_AVENUE"]:
        decision, step = apply(engine, decision, "mortgage_property", {"space_key": key})
        funding.append(step)
    assert next(p.cash for p in engine.state.players if p.player_id == "p4") == 188 < 200

    engine, decision = restore(run, b[194]["decision_id"])
    owner = next(p for p in engine.state.players if p.player_id == "p2")
    before = [engine._calculate_rent(engine.state.board[i], owner, 7) for i in [6, 8, 9]]
    assert before == [400, 400, 450]
    _, hotels = apply(engine, decision, "build_houses_or_hotel", action(194)["args"])
    after = [engine._calculate_rent(engine.state.board[i], owner, 7) for i in [6, 8, 9]]
    assert after == [550, 550, 600]
    assert person(194, "p3")["cash"] == 459 and person(196, "p3")["cash"] == 509
    assert before[2] <= 509 < after[2]
    assert next(p for p in engine.state.players if p.player_id == "p3").position == 2
    assert "space 17" in action(196)["private_thought"]
    all_profiles = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert all_profiles["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [r for r in all_profiles["units"] if r["game"] == 10]
    selected = {r["decision_id_zero_based_suffix"] for c in rows(HERE.parent / "candidate_catalog.jsonl")
                if c["catalog_id"].startswith("public-G10") for r in c["source_entry"]["decision_refs"]}
    selected |= {34, 39, 40, 43, 88, 92, 104, 106, 110, 125, 126, 127, 171, 181,
                 186, 187, 188, 189, 190, 193, 194, 196, 198}
    opus = [p for p in b.values() if p["player_id"] == "p4"]
    assert all([a["outcome"] for a in p["attempts"]] == ["refused", "valid"] for p in opus)
    assert not any(p["resolution"]["fallback_used"] for p in b.values())
    result = {"game": 10, "checks": "passed", "scope": "Selected originals and exact local branches; not a complete provider-channel reread",
              "kentucky_cash_flows": trade_flows, "recovery_allocation_totals": totals,
              "interleaved_recovery": recovery, "next_p4_management": p4_management,
              "off_group_funding_at187": funding, "unmortgage_fees": fees,
              "inherited_light_blue_upgrade": {"before": before, "after": after, "actual_landings_cash": 509, "applied": hotels},
              "branch_limits": "Legal immediate sequences and rent-schedule comparison on the realized landing only; no alternate winner or later trajectory.",
              "terminal_ceilings": [check(10, 188, 692), check(10, 193, 648), check(10, 198, 509)],
              "profiles": profiles, "opus_refused_then_valid": len(opus),
              "originals": {n: b[n] for n in sorted(selected)},
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "event_sha256": digest, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g10_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "profiles": profiles, "terminal_ceilings": [692, 648, 509],
                      "opus_refused_then_valid": len(opus), "kentucky_cash_flows": trade_flows}))


if __name__ == "__main__":
    main()
