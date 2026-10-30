"""Original G20 checks, with local branches and no alternative-winner claim."""

import hashlib
import json
from pathlib import Path

from monopoly_engine.engine import HOUSE_COST_BY_GROUP

from check_final_liquidations import check
from check_g13_claims import ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl")
             if u["game"] == 20]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def state(n):
        return packets[n]["initial_prompt"]["payload"]["game_state"]

    def delivered(n, text):
        return [r for r in state(n)["memory"]["public_timeline_last_20"] if r.get("message") == text]

    assert 'private_thought' in action(1)["public_message"]
    assert delivered(4, action(1)["public_message"])
    assert "leaked private_thought" in action(4)["private_thought"]
    assert action(77)["action"] == "end_turn"
    assert "$400 stands for Illinois" in action(77)["public_message"]
    assert delivered(78, action(77)["public_message"])
    assert "$400 is too low" in action(78)["public_message"]
    assert "cash-starved" in action(95)["private_thought"]
    assert "let's not fund" in action(96)["public_message"]
    assert "Giving p3 the Brown monopoly" in action(141)["private_thought"]
    assert "Giving p3 the Brown monopoly" in action(143)["private_thought"]
    assert "cash to buy New York, unmortgage it, and build" in action(226)["public_message"]
    assert "five red houses" in action(235)["public_message"]
    assert HOUSE_COST_BY_GROUP["RED"] == 150

    # Actual offered price, accepted instead of the recorded counter. No consent is invented.
    engine, decision = restore(run, packets[235]["decision_id"])
    branch = []
    decision, result = apply(engine, decision, "accept_trade", {})
    branch.append(result)
    player = next(p for p in engine.state.players if p.player_id == "p3")
    assert player.cash == 97  # 507 - 400 - mandatory 10 transfer interest.
    for key in ("ORIENTAL_AVENUE", "B_O_RAILROAD", "ATLANTIC_AVENUE", "PARK_PLACE"):
        assert decision["player_id"] == "p3"
        decision, result = apply(engine, decision, "mortgage_property", {"space_key": key})
        branch.append(result)
    assert player.cash == 552
    decision, result = apply(engine, decision, "unmortgage_property", {"space_key": "NEW_YORK_AVENUE"})
    branch.append(result)
    assert player.cash == 441
    decision, result = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
        {"space_key": key, "kind": "HOUSE", "count": 1}
        for key in ("ST_JAMES_PLACE", "TENNESSEE_AVENUE", "NEW_YORK_AVENUE", "ST_JAMES_PLACE")
    ]})
    branch.append(result)
    assert player.cash == 41
    assert [engine.state.board[i].houses for i in (16, 18, 19)] == [2, 1, 1]

    # Original prompts preserve both mortgage flags. The public rendering lost them.
    flags = {}
    for n in range(296, 311):
        players = [state(n)["you"], *state(n)["others"]]
        p2 = next(p for p in players if p["player_id"] == "p2")
        found = {h["space_key"]: h["mortgaged"] for h in p2["holdings"]["owned"]
                 if h["space_key"] in {"INDIANA_AVENUE", "ILLINOIS_AVENUE"}}
        assert found == {"INDIANA_AVENUE": True, "ILLINOIS_AVENUE": True}
        flags[n] = found

    # Reproduce the actual multi-step liquidation, including both hotel downgrades.
    engine, decision = restore(run, packets[327]["decision_id"])
    player = next(p for p in engine.state.players if p.player_id == "p3")
    owned = [s for s in engine.state.board if s.owner_id == "p3"]
    salvage = sum((5 if s.hotel else s.houses) * HOUSE_COST_BY_GROUP.get(s.group, 0) // 2 for s in owned)
    mortgages = sum(s.price // 2 for s in owned if not s.mortgaged)
    assert (player.cash, salvage, mortgages) == (49, 700, 665)
    assert engine.state.bank.houses_remaining == 15
    liquidation = []
    for n in range(327, 337):
        assert decision["decision_id"] == packets[n]["decision_id"]
        a = action(n)
        decision, result = apply(engine, decision, a["action"], a["args"])
        liquidation.append(result)
    assert player.cash == 14 and not player.bankrupt
    assert all(not s.houses and not s.hotel and s.mortgaged for s in engine.state.board if s.owner_id == "p3")

    aggregation = json.loads((HERE / "development_aggregation_check.json").read_text())
    event_hash = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert aggregation["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == event_hash
    profiles = [u for u in aggregation["units"] if u["game"] == 20]
    green = next(u for u in profiles if u["player"] == "p4")
    assert (green["spend"], green["sale_proceeds"], green["developed_rent_whole_game"]) == (3200, 100, 2940)
    assert sum(u["spend"] for u in profiles if u["player"] == "p3") == 1700

    selected = {1, 4, 6, 36, 38, 40, 42, 44, 46, 69, 70, 71, 77, 78, 80, 82, 83,
                95, 96, 97, 98, 100, 107, 118, 119, 141, 143, 168, 172, 185, 186,
                187, 188, 208, 225, 226, 232, 233, 234, 235, 236, 263, 265, 272,
                273, 274, 291, 292, 293, 294, 295, 296, 299, 305, 306, 310, 322,
                325, *range(327, 337), 340, 342, 354}
    report = {
        "scope": "Complete extraction narrative and catalog; selected original action, prompt and attempt fields. No claim to reread all 355 original bundles.",
        "public_offer_delivery": delivered(78, action(77)["public_message"]),
        "public_note_delivery": delivered(4, action(1)["public_message"]),
        "financed_build235": {"recorded_action": action(235), "alternative": branch,
                              "limits": "Feasible local alternative to an actual offered price. This branch preserves both brown hotels and funds four orange houses. Six are feasible if both brown hotels are liquidated; see g20_sample_checks.json. No optimality, deceptive intent, recipient reliance, or later winner identified.",
                              "prior_scope_correction": "The original report said four houses, not the six-house target, without stating the preserve-brown-hotels constraint. Sol challenged that omission; Astra independently replayed the six-house route with brown liquidation, ending at91."},
        "original_mortgage_flags": flags,
        "actual_liquidation327": {"start_cash": 49, "salvage": salvage, "unlocked_and_existing_mortgages": mortgages,
                                   "total": 1414, "steps": liquidation, "end_cash": 14},
        "terminal_ceilings": [check(20, 274, 417), check(20, 310, 550), check(20, 354, 340)],
        "profiles_from_independent_event_fold": profiles,
        "originals": {n: {"action": action(n), "payload": packets[n]["initial_prompt"]["payload"],
                          "events": packets[n]["canonical_event_segment"]} for n in sorted(selected)},
        "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
        "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                          for u in units if int(u["decision_id"][-6:]) in selected},
        "canonical_event_sha256": event_hash,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g20_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"offered400_then_four_houses_cash": 41, "actual_liquidation_total": 1414,
                      "actual_liquidation_cash": 14, "terminal_ceilings": [417, 550, 340]}))


if __name__ == "__main__":
    main()
