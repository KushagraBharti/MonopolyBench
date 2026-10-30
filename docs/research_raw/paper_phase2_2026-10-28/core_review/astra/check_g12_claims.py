"""G12 selected original claims; hypothetical acceptance is never predicted."""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 12]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    b = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / b[0]["source_run"]
    events = rows(run / "events.jsonl")
    assert len(events) == 2464 and events[-1]["payload"]["winner_player_id"] == "p2"

    def action(n):
        return b[n]["applied_action_record"]["action"]

    def state(n):
        return b[n]["initial_prompt"]["payload"]["game_state"]

    def player(n, pid=None):
        s = state(n)
        return next(p for p in [s["you"], *s["others"]] if p["player_id"] == (pid or s["you"]["player_id"]))

    assert [(e["payload"]["from_player_id"], e["payload"]["to_player_id"], e["payload"]["space_index"])
            for e in b[26]["canonical_event_segment"] if e["type"] == "PROPERTY_TRANSFERRED"] == [
                ("p2", "p1", 11), ("p1", "p2", 23)]
    branches = []
    for n, mortgage_keys, house_keys, expected in [
        (32, [], ["KENTUCKY_AVENUE"], 30),
        (30, ["PENNSYLVANIA_RAILROAD", "ELECTRIC_COMPANY"], ["KENTUCKY_AVENUE", "INDIANA_AVENUE"], 5),
        (109, ["PENNSYLVANIA_RAILROAD"], ["BOARDWALK"], 95),
    ]:
        engine, decision = restore(run, b[n]["decision_id"])
        steps = []
        if n in [30, 32]:
            decision, step = apply(engine, decision, "accept_trade", {})
            steps.append(step)
        assert decision["player_id"] == "p2" and decision["decision_type"] == "POST_TURN_ACTION_DECISION"
        for key in mortgage_keys:
            decision, step = apply(engine, decision, "mortgage_property", {"space_key": key})
            steps.append(step)
        _, step = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
            {"space_key": key, "kind": "HOUSE", "count": 1} for key in house_keys]})
        steps.append(step)
        assert next(p.cash for p in engine.state.players if p.player_id == "p2") == expected
        branches.append({"decision": n, "conditional_acceptance": n in [30, 32], "steps": steps, "remaining_cash": expected})
    assert "still can't build on Tennessee" in action(61)["public_message"]
    assert "only 3 houses" in action(146)["private_thought"]
    assert "same as $210" in action(148)["private_thought"]
    assert player(151)["cash"] == 285 and player(152)["cash"] == 495
    assert 285 + 210 + 300 == 795 < 800
    assert player(108)["cash"] == 883 and player(109, "p3")["cash"] == 733
    assert 861 - 300 - 16 == 545 < 560

    engine, decision = restore(run, b[190]["decision_id"])
    steps = []
    for key in ["KENTUCKY_AVENUE", "INDIANA_AVENUE", "ILLINOIS_AVENUE"]:
        decision, step = apply(engine, decision, "sell_houses_or_hotel", {"sell_plan": [
            {"space_key": key, "kind": "HOUSE", "count": 1}]})
        steps.append(step)
    for key in ["ILLINOIS_AVENUE", "INDIANA_AVENUE"]:
        decision, step = apply(engine, decision, "mortgage_property", {"space_key": key})
        steps.append(step)
    assert next(p.cash for p in engine.state.players if p.player_id == "p3") == 8
    assert not next(p.bankrupt for p in engine.state.players if p.player_id == "p3")
    assert sum(e["payload"]["amount"] for s in steps for e in s["events"] if e["type"] == "RENT_PAID") == 500
    assert "maximum liquidity is $408" in action(190)["private_thought"]
    prior = json.loads((HERE / "g12_channel_liquidation_check.json").read_text())
    assert prior["source_sha256"] == hashlib.sha256((ROOT / prior["source"]["packet"]).read_bytes()).hexdigest()
    assert prior["original_action"] == action(249)
    assert "accept_trade" not in b[228]["initial_prompt"]["payload"]["action_state"]["available_actions"]
    assert player(229, "p2")["cash"] == 50 and player(230, "p2")["cash"] == 19
    assert "pinks 2-2-3" in action(239)["private_thought"]
    assert action(239)["public_message"] == "Holding. Pinks stay as they are. Your roll, Claude."
    assert player(221)["cash"] == 0
    assert state(274)["bank"]["houses_remaining"] == 0
    assert state(291)["bank"]["houses_remaining"] == 1
    assert sum(p["houses"] for p in player(291)["holdings"]["owned"]) == 31
    assert "27 houses" in action(291)["public_message"]
    assert all(p["houses"] == 0 and not p["hotel"] for p in player(274, "p4")["holdings"]["owned"])
    selected = {r["decision_id_zero_based_suffix"] for c in rows(HERE.parent / "candidate_catalog.jsonl")
                if c["catalog_id"].startswith("public-G12") for r in c["source_entry"]["decision_refs"]}
    selected |= {26, 30, 32, 61, 108, 109, 146, 148, 150, 151, 190, 195, 196, 197, 227, 228, 229, 239, 274, 291, 343}
    all_profiles = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert all_profiles["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [r for r in all_profiles["units"] if r["game"] == 12]
    opus = [p for p in b.values() if p["player_id"] == "p2"]
    assert all([a["outcome"] for a in p["attempts"]] == ["refused", "valid"] for p in opus)
    assert not any(p["resolution"]["fallback_used"] for p in b.values())
    result = {"game": 12, "checks": "passed", "scope": "Selected originals and legal local branches; not every provider bundle reread",
              "financing_branches": branches, "sol190_debt_payment": steps,
              "grok249_previous_exact_check": {"path": str(HERE / "g12_channel_liquidation_check.json"), "sha256": hashlib.sha256((HERE / "g12_channel_liquidation_check.json").read_bytes()).hexdigest()},
              "gemini_final_ceiling": check(12, 343, 164), "profiles": profiles, "opus": len(opus),
              "limitations": "Acceptance diagnostics do not predict agreement. Funding availability does not prove optimality or alternative winners; false propositions do not identify intention.",
              "originals": {n: b[n] for n in sorted(selected)},
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "event_sha256": digest, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g12_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "profiles": profiles, "opus": len(opus), "sol190_survives_with": 8}))


if __name__ == "__main__":
    main()
