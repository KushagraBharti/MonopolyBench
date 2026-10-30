"""G5 source adjudication and immediate legal-operation checks.

No provider calls, canonical edits, future rollouts or winner counterfactuals.
"""

import hashlib
import json
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 5]
    cache = {u["packet"]: rows(ROOT / u["packet"]) for u in units}
    packets = {int(u["decision_id"][-6:]): cache[u["packet"]][u["packet_line"] - 1] for u in units}
    run = ROOT / packets[0]["source_run"]
    events = rows(run / "events.jsonl")

    def action(n):
        return packets[n]["applied_action_record"]["action"]

    def payload(n):
        return packets[n]["initial_prompt"]["payload"]

    def state(n):
        return payload(n)["game_state"]

    def cash(n, player=None):
        s = state(n)
        return next(p["cash"] for p in [s["you"], *s["others"]]
                    if p["player_id"] == (player or s["you"]["player_id"]))

    def slim_event(e):
        return {k: e[k] for k in ["seq", "turn_index", "type", "payload"]}

    # The cash claim is conditional on the actual offered payment, not false.
    assert cash(106, "p4") + action(106)["args"]["offer"]["cash"] == 741
    assert "your Boardwalk" in action(92)["public_message"]
    assert "BOARDWALK" in {s["space_key"] for s in state(93)["you"]["holdings"]["owned"]}
    assert action(60)["action"] == "accept_trade"
    assert json.loads(packets[60]["attempts"][0]["assistant_content"])["name"] == "counter_trade"
    assert action(60)["private_thought"].startswith("Reject")
    assert (cash(60, "p2"), cash(61, "p2"), cash(65, "p2")) == (921, 571, 1371)
    assert packets[60]["turn_index"] == packets[64]["turn_index"] == 37
    between = [e for e in events if packets[60]["canonical_event_segment"][0]["seq"] <= e["seq"]
               <= packets[64]["canonical_event_segment"][-1]["seq"]]
    assert not any(e["type"] in ["DICE_ROLLED", "RENT_PAID"] for e in between)

    ny_offers = [n for n in packets if packets[n]["player_id"] == "p1"
                 and action(n)["action"] == "propose_trade"
                 and "NEW_YORK_AVENUE" in action(n)["args"]["request"]["properties"]]
    assert ny_offers == [104, 106, 123, 136, 147, 149, 167, 169, 243]
    assert action(151)["public_message"] not in [r["message"] for r in state(167)["memory"]["public_timeline_last_20"]]
    assert action(149)["public_message"] not in [r["message"] for r in state(167)["memory"]["public_timeline_last_20"]]
    assert action(159)["action"] == "pay_jail_fine"
    assert json.loads(packets[159]["attempts"][0]["assistant_content"])["name"] == "roll_for_doubles"
    assert any(e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "JAIL_FINE"
               and e["payload"]["delta"] == -50 for e in packets[159]["canonical_event_segment"])
    assert cash(155) == 1136 and cash(156, "p2") == 1072

    assert cash(177) == 692 and cash(178, "p3") == 642 and cash(178) == 1086
    assert action(177)["action"] == "accept_trade"
    assert cash(181) == 116 and cash(188, "p3") == 112
    assert action(197)["public_message"] in [r["message"] for r in state(199)["memory"]["public_timeline_last_20"]]
    assert action(219)["public_message"] in [r["message"] for r in state(220)["memory"]["public_timeline_last_20"]]
    assert "baiting" in action(220)["private_thought"]
    assert payload(218)["action_state"]["available_actions"] == ["start_auction"]

    fallbacks = {player: [n for n, p in packets.items() if p["player_id"] == player
                         and p["resolution"]["fallback_used"]] for player in ["p1", "p2", "p3", "p4"]}
    assert [len(fallbacks[p]) for p in fallbacks] == [14, 2, 0, 0]
    immediate_builds = {}
    for n in [235, 256, 281]:
        engine, decision = restore(run, packets[n]["decision_id"])
        raw = json.loads(packets[n]["attempts"][-1]["parsed_tool_call"]["arguments"])["build_plan"]
        interleaved = [{**entry, "count": 1} for layer in range(max(x["count"] for x in raw))
                       for entry in raw if entry["count"] > layer]
        _, result = apply(engine, decision, "build_houses_or_hotel", {"build_plan": interleaved})
        assert next(p.cash for p in engine.state.players if p.player_id == "p1") == cash(n) - 50 * sum(x["count"] for x in raw)
        immediate_builds[n] = result

    # Gemini's earlier 774 ceiling is contradicted by its executed later sequence.
    assert "774" in action(258)["private_thought"]
    assert cash(263) == 74 and cash(266) == 149
    assert 74 + 600 + 375 - 900 == 149
    assert len(state(272)["you"]["holdings"]["owned"]) == 7
    assert all(s["mortgaged"] for s in state(272)["you"]["holdings"]["owned"])
    assert len(state(274)["you"]["holdings"]["owned"]) == 17
    assert len(state(309)["you"]["holdings"]["owned"]) == 11
    assert not any(e["type"] == "HOTEL_BUILT" for e in events)

    bank_checks = {n: state(n)["bank"]["houses_remaining"]
                   for n in [287, 295, 298, 300, 302, 303, 304, 305, 306, 308]}
    assert bank_checks == {287: 11, 295: 8, 298: 6, 300: 5, 302: 5, 303: 2,
                           304: 1, 305: 1, 306: 0, 308: 0}
    engine, decision = restore(run, packets[306]["decision_id"])
    candidate = {"schema_version": "v1", "decision_id": decision["decision_id"],
                 "action": "build_houses_or_hotel", "args": {"build_plan": [
                     {"space_key": "ORIENTAL_AVENUE", "kind": "HOUSE", "count": 1}]}}
    assert cash(306) == 70
    errors_zero = engine.validate_action_for_decision(candidate, decision)
    assert errors_zero
    # Predicate probe only. This extra house is not a legal event or a trajectory.
    engine.state.bank.houses_remaining = 1
    one_house_validation = engine._validate_build_plan(
        next(p for p in engine.state.players if p.player_id == "p1"),
        [{"space_index": 6, "kind": "HOUSE", "count": 1}])
    assert one_house_validation["total_cost"] == 50

    # Sol's peer objection: zero stock blocks net expansion, not redistribution.
    # Restart the historical prefix; do not use the artificial inventory above.
    engine, decision = restore(run, packets[306]["decision_id"])
    decision, sibling_sale = apply(engine, decision, "sell_houses_or_hotel", {"sell_plan": [
        {"space_key": "VERMONT_AVENUE", "kind": "HOUSE", "count": 1}]})
    assert next(p.cash for p in engine.state.players if p.player_id == "p1") == 95
    decision, reallocated = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
        {"space_key": "ORIENTAL_AVENUE", "kind": "HOUSE", "count": 1}]})
    assert next(p.cash for p in engine.state.players if p.player_id == "p1") == 45
    assert [engine.state.board[i].houses for i in [6, 8, 9]] == [3, 2, 3]
    assert engine.state.bank.houses_remaining == 0

    aggregation = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert aggregation["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [u for u in aggregation["units"] if u["game"] == 5]
    assert {(u["player"], u["group"]): u["developed_rent_whole_game"] for u in profiles} == {
        ("p1", "LIGHT_BLUE"): 30, ("p2", "GREEN"): 2450,
        ("p2", "PINK"): 0, ("p3", "DARK_BLUE"): 0}
    rents = [slim_event(e) for e in events if e["type"] == "RENT_PAID"]
    oriental_sol = [e for e in rents if e["payload"]["space_index"] == 6 and e["payload"]["from_player_id"] == "p2"]
    assert [e["payload"]["amount"] for e in oriental_sol] == [12, 12, 12]
    selected = {n for c in rows(HERE.parent / "candidate_catalog.jsonl")
                if c["catalog_id"].startswith("public-G05")
                for r in c["source_entry"]["decision_refs"] for n in [r["decision_id_zero_based_suffix"]]}
    selected |= {35, 37, 61, 65, 111, 116, 195, 258, 266, 274, 300, 303, 304, 306}
    report = {
        "scope": "All 29 extraction entries and full Terra/public trajectories; selected original channels. Not every provider bundle reread.",
        "limits": "No optimality, causal persuasion, stable belief, or winner counterfactual. Zero rent is observed receipt, not failed investment.",
        "ny_offer_decisions": ny_offers, "bank_checks": bank_checks, "fallback_decisions": fallbacks,
        "immediate_interleaved_builds": immediate_builds,
        "stock_predicate": {"decision": 306, "cash": 70, "one_house_cost": 50,
                            "actual_zero_bank_errors": errors_zero, "artificial_one_house_validation": one_house_validation,
                            "qualification": "Artificial stock probe isolates legality; no extra house is introduced into any canonical or continued game."},
        "legal_reallocation": {"provenance": "Sol peer-nominated own-sale alternative; independently replayed here.",
                               "sale": sibling_sale, "build": reallocated,
                               "qualification": "No net house expansion. Eight houses remain, redistributed from Vermont to Oriental at25 net cost. No future rolls or benefits tested."},
        "terminal_ceilings": [check(5, 226, 586), check(5, 272, 149), check(5, 309, 799)],
        "profiles": profiles, "rent_events": rents, "oriental_sol_rents": oriental_sol,
        "originals": {n: {"action": action(n), "payload": payload(n), "attempts": packets[n]["attempts"],
                           "events": [slim_event(e) for e in packets[n]["canonical_event_segment"]]}
                      for n in sorted(selected)},
        "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
        "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                          for u in units if int(u["decision_id"][-6:]) in selected},
        "event_sha256": digest, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g05_claim_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "terminal_ceilings": [586, 149, 799], "profiles": profiles,
                      "fallback_counts": {p: len(v) for p, v in fallbacks.items()}, "bank_checks": bank_checks}))


if __name__ == "__main__":
    main()
