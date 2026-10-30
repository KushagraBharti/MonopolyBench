"""G11 original accounting, constructive liquidation and proposition checks."""

import hashlib
import json
import re
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import LEDGER, ROOT, apply, restore, rows
from monopoly_engine.engine import HOUSE_COST_BY_GROUP

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 11]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    b = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / b[0]["source_run"]
    events = rows(run / "events.jsonl")
    assert len(events) == 2310 and events[-1]["payload"]["winner_player_id"] == "p2"

    def action(n):
        return b[n]["applied_action_record"]["action"]

    def state(n):
        return b[n]["initial_prompt"]["payload"]["game_state"]

    def reasoning(n):
        return "\n".join(c["message"].get("reasoning") or "" for a in b[n]["attempts"]
                         for c in (a.get("raw_response") or {}).get("choices", []))

    def holdings(n, pid):
        g = state(n)
        return next(p["holdings"]["owned"] for p in [g["you"], *g["others"]] if p["player_id"] == pid)

    assert {p["space_key"]: p["houses"] for p in holdings(123, "p2") if p["houses"]} == {
        "PARK_PLACE": 2, "BOARDWALK": 3}
    assert [a["outcome"] for a in b[159]["attempts"]] == ["illogical", "valid"]
    assert {p["space_key"] for p in holdings(149, "p3")} >= {"ST_JAMES_PLACE", "TENNESSEE_AVENUE", "NEW_YORK_AVENUE"}
    assert sum(p["houses"] for p in holdings(150, "p3")) == 2
    engine, decision = restore(run, b[150]["decision_id"])
    decision, rail = apply(engine, decision, "mortgage_property", {"space_key": "SHORT_LINE"})
    _, orange = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
        {"space_key": "ST_JAMES_PLACE", "kind": "HOUSE", "count": 1}]})
    assert next(p.cash for p in engine.state.players if p.player_id == "p3") == 42

    # A redemption activates its own square without increasing the multiplier
    # of an already active sibling. All assertions concern the actual prefix.
    engine, decision = restore(run, b[181]["decision_id"])
    owner = next(p for p in engine.state.players if p.player_id == "p4")
    before = [engine._calculate_rent(engine.state.board[i], owner, 10) for i in [12, 5]]
    decision, ww = apply(engine, decision, "unmortgage_property", {"space_key": "WATER_WORKS"})
    _, prr = apply(engine, decision, "unmortgage_property", {"space_key": "PENNSYLVANIA_RAILROAD"})
    after = [engine._calculate_rent(engine.state.board[i], owner, 10) for i in [12, 5]]
    assert before == after == [100, 50]
    assert owner.cash == 530
    assert "Claude's recent action confirms" in reasoning(192)
    assert any("rolling again" in (p.get("message") or "") for p in state(192)["memory"]["public_timeline_last_20"])
    assert action(188)["action"] == "end_turn" and b[189]["player_id"] == "p4"
    assert 140 + 150 == 290 and "$300 in available mortgages" in action(215)["public_message"]
    # Preserve the transient false provider proposition and its correction.
    r = reasoning(256)
    first, corrected = "accepting would complete my pink monopoly", "Accepting the trade would not complete my pink monopoly"
    assert r.index(first) < r.index(corrected) and action(256)["action"] == "reject_trade"
    assert "I missed St. Charles" in action(257)["public_message"] and action(258)["action"] == "reject_trade"
    assert action(267)["action"] == "propose_trade" and "Joke trade" in action(267)["private_thought"]
    assert json.loads(b[267]["attempts"][-1]["assistant_content"])["name"] == "end_turn"
    assert "cannot pay Baltic hotel $450" in action(272)["private_thought"]
    assert state(272)["you"]["cash"] == 445
    assert min(state(n)["bank"]["houses_remaining"] for n in b) > 0
    assert "bank already has 15 houses" in action(241)["private_thought"]

    # Reproduce the actual successful seven-mortgage payment without invoking
    # any hotel sale or inventing a recipient agreement.
    engine, decision = restore(run, b[292]["decision_id"])
    payment_steps = []
    for n in range(292, 299):
        assert action(n)["action"] == "mortgage_property"
        decision, step = apply(engine, decision, "mortgage_property", action(n)["args"])
        payment_steps.append(step)
    assert next(p.cash for p in engine.state.players if p.player_id == "p4") == 23
    assert all(engine.state.board[i].hotel for i in [1, 3])
    assert sum(e["payload"]["amount"] for s in payment_steps for e in s["events"]
               if e["type"] == "RENT_PAID") == 2000

    # Final hotel estate: attain the nominal upper bound by legal operations.
    # Greedy liquidation is not presumed maximal; equality proves it here.
    engine, decision = restore(run, b[325]["decision_id"])
    actor = "p4"
    owned = [s for s in engine.state.board if s.owner_id == actor]
    components = {"cash": 293,
                  "building_salvage": sum((5 if s.hotel else s.houses) * HOUSE_COST_BY_GROUP.get(s.group, 0) // 2 for s in owned),
                  "unlocked_mortgages": sum(s.price // 2 for s in owned if not s.mortgaged)}
    assert components == {"cash": 293, "building_salvage": 250, "unlocked_mortgages": 210}
    nominal = sum(components.values())
    assert nominal == 753 < 1100
    steps, running, maximum = [], 293, 293
    while decision and decision["decision_type"] == "LIQUIDATION_DECISION" and decision["player_id"] == actor:
        options = decision["liquidation"]["options"]
        if options["mortgageable_space_indices"]:
            s = engine.state.board[min(options["mortgageable_space_indices"])]
            key = re.sub(r"[^A-Za-z0-9]+", "_", s.name).strip("_").upper()
            name, args = "mortgage_property", {"space_key": key}
        elif options["sellable_building_space_indices"]:
            s = engine.state.board[min(options["sellable_building_space_indices"])]
            key = re.sub(r"[^A-Za-z0-9]+", "_", s.name).strip("_").upper()
            name, args = "sell_houses_or_hotel", {"sell_plan": [{"space_key": key, "kind": "HOTEL" if s.hotel else "HOUSE", "count": 1}]}
        else:
            break
        decision, step = apply(engine, decision, name, args)
        steps.append(step)
        for e in step["events"]:
            if e["type"] == "CASH_CHANGED" and e["payload"]["player_id"] == actor:
                running += e["payload"]["delta"]
                maximum = max(maximum, running)
        assert len(steps) < 40
    assert maximum == nominal
    assert next(p for p in engine.state.players if p.player_id == actor).bankrupt
    selected = {r["decision_id_zero_based_suffix"] for c in rows(HERE.parent / "candidate_catalog.jsonl")
                if c["catalog_id"].startswith("public-G11") for r in c["source_entry"]["decision_refs"]}
    selected |= {99, 104, 105, 122, 145, 148, 149, 150, 159, 172, 176, 177, 181, 182, 188, 192, 215, 219,
                 225, 241, 255, 256, 257, 258, 267, 272, 278, 283, 292, 298, 303, 305, 306, 316, 325}
    all_profiles = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert all_profiles["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [r for r in all_profiles["units"] if r["game"] == 11]
    opus = [p for p in b.values() if p["player_id"] == "p3"]
    assert all([a["outcome"] for a in p["attempts"]] == ["refused", "valid"] for p in opus)
    assert not any(p["resolution"]["fallback_used"] for p in b.values())
    result = {"game": 11, "checks": "passed", "scope": "Selected originals and exact local branches, not every provider bundle reread",
              "orange_financing_at150": [rail, orange], "sibling_rents_before_after": [before, after],
              "redemptions": [ww, prr], "successful2000_payment": payment_steps,
              "gemini_ceiling": check(11, 225, 1064), "opus_ceiling": check(11, 228, 306),
              "final_hotel_ceiling": {"components": components, "maximum": maximum, "steps": steps},
              "profiles": profiles, "opus_refused_then_valid": len(opus),
              "limits": "Local legal feasibility and actual flows only. No inferred assent, persuasion, uniquely identified intent, or alternate winner.",
              "originals": {n: b[n] for n in sorted(selected)},
              "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
              "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                                for u in units if int(u["decision_id"][-6:]) in selected},
              "event_sha256": digest, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g11_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "profiles": profiles, "terminal_ceilings": [1064, 306, 753], "opus": len(opus)}))


if __name__ == "__main__":
    main()
