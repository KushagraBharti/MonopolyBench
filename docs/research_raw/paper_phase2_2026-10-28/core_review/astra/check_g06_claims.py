"""Source adjudication for G6; immediate legal branches, no future play."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from check_final_liquidations import check
from check_g13_claims import LEDGER, ROOT, apply, restore, rows

HERE = Path(__file__).resolve().parent


def main():
    units = [u for u in rows(LEDGER) if u["game"] == 6]
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

    def person(n, player=None):
        s = state(n)
        return next(p for p in [s["you"], *s["others"]]
                    if p["player_id"] == (player or s["you"]["player_id"]))

    assert action(19)["action"] == "propose_trade"
    assert json.loads(packets[19]["attempts"][0]["assistant_content"])["name"] == "end_turn"
    assert "incorrect" in action(20)["private_thought"]
    assert action(19)["public_message"] in [r["message"] for r in state(20)["memory"]["public_timeline_last_20"]]
    assert action(20)["action"] == "accept_trade"
    assert action(45)["action"] == "start_auction"
    assert json.loads(packets[45]["attempts"][0]["assistant_content"])["name"] == "buy_property"
    assert action(50)["public_message"] in [r["message"] for r in state(52)["memory"]["public_timeline_last_20"]]
    assert action(74)["action"] == "propose_trade"
    assert json.loads(packets[74]["attempts"][0]["assistant_content"])["name"] == "end_turn"
    assert action(111)["action"] == "propose_trade"
    assert json.loads(packets[111]["attempts"][0]["assistant_content"])["name"] == "end_turn"

    # The declared preference still permits purchases while colors remain bank-held.
    engine, _ = restore(run, packets[70]["decision_id"])
    color_groups = {}
    for s in engine.state.board:
        if s.group in {"BROWN", "LIGHT_BLUE", "PINK", "ORANGE", "RED", "YELLOW", "GREEN", "DARK_BLUE"}:
            color_groups.setdefault(s.group, []).append(s)
    assert len(color_groups) == 8
    assert all(any(s.owner_id is None for s in group) for group in color_groups.values())

    # An affordable management-time financing route, not a future survival claim.
    assert person(173)["cash"] == 45
    engine, decision = restore(run, packets[173]["decision_id"])
    financing = []
    for key in ["MEDITERRANEAN_AVENUE", "VENTNOR_AVENUE", "MARVIN_GARDENS", "PACIFIC_AVENUE"]:
        decision, result = apply(engine, decision, "mortgage_property", {"space_key": key})
        financing.append(result)
    assert next(p.cash for p in engine.state.players if p.player_id == "p2") == 495
    decision, financed_build = apply(engine, decision, "build_houses_or_hotel", {"build_plan": [
        {"space_key": key, "kind": "HOUSE", "count": 1}
        for key in ["KENTUCKY_AVENUE", "INDIANA_AVENUE", "ILLINOIS_AVENUE"]]})
    assert next(p.cash for p in engine.state.players if p.player_id == "p2") == 45

    # The menu's unmortgageable keys name eligible redemptions, not a ban.
    redemptions = {}
    for key, cost in [("NORTH_CAROLINA_AVENUE", 165), ("BOARDWALK", 221)]:
        engine, decision = restore(run, packets[221]["decision_id"])
        before = next(p.cash for p in engine.state.players if p.player_id == "p1")
        _, result = apply(engine, decision, "unmortgage_property", {"space_key": key})
        assert next(p.cash for p in engine.state.players if p.player_id == "p1") == before - cost
        redemptions[key] = result

    bank = {n: state(n)["bank"]["houses_remaining"] for n in [148, 153, 160, 161, 166, 179, 187, 188, 211, 224, 226, 228]}
    assert bank == {148: 23, 153: 20, 160: 17, 161: 14, 166: 13, 179: 1,
                    187: 2, 188: 8, 211: 5, 224: 0, 226: 3, 228: 0}
    assert sum(s["houses"] for s in person(224, "p1")["holdings"]["owned"]) == 29
    assert sum(s["houses"] for s in person(228, "p1")["holdings"]["owned"]) == 32
    assert not any(e["type"] == "HOTEL_BUILT" for e in events)
    assert person(232)["cash"] == 91

    retry_decisions = Counter(p["player_id"] for p in packets.values() if len(p["attempts"]) > 1)
    first_outcomes = Counter((p["player_id"], p["attempts"][0]["outcome"])
                             for p in packets.values() if len(p["attempts"]) > 1)
    assert retry_decisions == {"p4": 67, "p1": 3, "p3": 1}
    assert not any(p["resolution"]["fallback_used"] for p in packets.values())
    aggregation = json.loads((HERE / "development_aggregation_check.json").read_text())
    digest = hashlib.sha256((run / "events.jsonl").read_bytes()).hexdigest()
    assert aggregation["event_source_hashes"][str((run / "events.jsonl").relative_to(ROOT))] == digest
    profiles = [u for u in aggregation["units"] if u["game"] == 6]
    assert {(u["player"], u["group"]): u["developed_rent_whole_game"] for u in profiles} == {
        ("p1", "LIGHT_BLUE"): 400, ("p1", "ORANGE"): 1300,
        ("p1", "PINK"): 0, ("p2", "RED"): 0, ("p4", "PINK"): 330}
    railroad_rents = [e for e in events if e["type"] == "RENT_PAID"
                     and e["payload"]["to_player_id"] == "p1"
                     and e["payload"]["space_index"] in [5, 15, 25, 35]]
    assert sum(e["payload"]["amount"] for e in railroad_rents) == 1900
    assert Counter(e["payload"]["amount"] for e in railroad_rents) == {100: 1, 200: 9}
    selected = {r["decision_id_zero_based_suffix"] for c in rows(HERE.parent / "candidate_catalog.jsonl")
                if c["catalog_id"].startswith("public-G06") for r in c["source_entry"]["decision_refs"]}
    selected |= {21, 67, 70, 84, 111, 112, 146, 173, 193, 221, 224, 228}
    result = {
        "scope": "All23 public catalog entries and full Terra/public trajectories; selected original channels, not every provider bundle reread.",
        "limits": "Applied path authoritative; local financing and redemption branches stop at the action. No causal persuasion or alternative winner.",
        "financing173": {"mortgages": financing, "build": financed_build},
        "redemption221": redemptions, "terminal_ceilings": [check(6, 154, 595), check(6, 220, 102), check(6, 232, 211)],
        "bank": bank, "profiles": profiles, "railroad_rents": railroad_rents,
        "retry_decisions": dict(retry_decisions),
        "retry_first_outcomes": [{"player": p, "outcome": o, "count": n} for (p, o), n in first_outcomes.items()],
        "originals": {n: {"action": action(n), "payload": payload(n), "attempts": packets[n]["attempts"],
                           "events": packets[n]["canonical_event_segment"]} for n in sorted(selected)},
        "source_units": [u for u in units if int(u["decision_id"][-6:]) in selected],
        "source_hashes": {u["packet"]: hashlib.sha256((ROOT / u["packet"]).read_bytes()).hexdigest()
                          for u in units if int(u["decision_id"][-6:]) in selected},
        "event_sha256": digest, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / "g06_claim_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "terminal_ceilings": [595, 102, 211], "bank": bank,
                      "retry_decisions": dict(retry_decisions), "profiles": profiles}))


if __name__ == "__main__":
    main()
