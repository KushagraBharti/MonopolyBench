"""Exact local diagnostics nominated by complete G11 common bundles.

No hypothetical agreement or changed future trajectory is a model prediction.
"""

import hashlib
import json
from pathlib import Path

from check_additional_economics import ROOT, units
from check_build_and_hotel_access import prefix

HERE = Path(__file__).resolve().parent


def player(engine, actor):
    return next(p for p in engine.get_snapshot()["players"] if p["player_id"] == actor)


def step(engine, decision, name, args=None):
    action = {"schema_version": "v1", "decision_id": decision["decision_id"],
              "action": name, "args": args or {}}
    _, events, following, _ = engine.apply_action(action)
    assert not any(e["type"] == "ACTION_REJECTED" for e in events), events
    if following is None:
        _, advanced, following, _ = engine.advance_until_decision(max_steps=100_000)
        events.extend(advanced)
    return following, {"action": action, "events": events}


def trade_check():
    engine, decision, packet, provenance = prefix(11, 121)
    before = engine.get_snapshot()
    assert decision["player_id"] == "p1"
    assert [engine.state.board[i].owner_id for i in [21, 23, 24]] == ["p3", "p1", "p3"]
    decision, proposal = step(engine, decision, "propose_trade", {
        "to_player_id": "p3",
        "offer": {"cash": 0, "properties": ["ST_JAMES_PLACE"], "get_out_of_jail_cards": 0},
        "request": {"cash": 0, "properties": ["KENTUCKY_AVENUE", "ILLINOIS_AVENUE"], "get_out_of_jail_cards": 0},
    })
    assert decision["player_id"] == "p3"
    _, acceptance = step(engine, decision, "accept_trade")
    assert [engine.state.board[i].owner_id for i in [21, 23, 24]] == ["p1"] * 3
    assert player(engine, "p1")["cash"] == 534
    return {**provenance, "source": units(11)[121][1], "before": before,
            "recorded_action": packet["applied_action_record"],
            "conditional_steps": [proposal, acceptance], "after": engine.get_snapshot(),
            "limit": "Complete121bundle read. A legal bilateral exchange can give p1 red completion; the recipient acceptance here is an artificial conditional diagnostic, not the historical response or a prediction of willingness, fair price, mutual completion or optimality."}


def reserve_check():
    engine, decision, packet, provenance = prefix(11, 66)
    assert player(engine, "p2")["cash"] == 263
    decision, build = step(engine, decision, "build_houses_or_hotel", {
        "build_plan": [{"space_key": "PARK_PLACE", "count": 1, "kind": "HOUSE"}],
    })
    assert player(engine, "p2")["cash"] == 63
    decision, end = step(engine, decision, "end_turn")
    assert decision["decision_type"] == "BUY_OR_AUCTION_DECISION"
    assert engine.state.board[8].owner_id is None
    assert player(engine, "p2")["cash"] == 263
    _, purchase = step(engine, decision, "buy_property")
    assert engine.state.board[8].owner_id == "p2"
    assert player(engine, "p2")["cash"] == 163
    return {**provenance, "source": units(11)[66][1],
            "recorded_action": packet["applied_action_record"],
            "branch": [build, end, purchase], "after": engine.get_snapshot(),
            "limit": "Complete066bundle read. One legal200house leaves63, then the same historical next4+5roll passesGO200 and still permits Vermont100, leaving163. This is an executed local changed-build branch through one bank purchase, not a future rent/winner/optimality result. Full067providerbundle unread."}


def jail_check():
    results = {}
    for name in ["pay_jail_fine", "roll_for_doubles"]:
        engine, decision, packet, provenance = prefix(11, 219)
        following, record = step(engine, decision, name)
        actor = player(engine, "p2")
        assert actor["cash"] == 830
        assert actor["position"] == 17
        assert not actor["in_jail"]
        assert following["decision_type"] == "POST_TURN_ACTION_DECISION"
        results[name] = {**provenance, "step": record, "actor_after": actor,
                         "following": following, "board_after": engine.get_snapshot()["board"]}
    assert results["pay_jail_fine"]["actor_after"] == results["roll_for_doubles"]["actor_after"]
    assert results["pay_jail_fine"]["board_after"] == results["roll_for_doubles"]["board_after"]
    engine_source = ROOT / "python/packages/engine/src/monopoly_engine/engine.py"
    return {"source": units(11)[219][1], "recorded_action": packet["applied_action_record"],
            "branches": results, "engine_source_sha256": hashlib.sha256(engine_source.read_bytes()).hexdigest(),
            "rule_source": "engine.py roll_for_doubles branch passes rolled_double=False to movement, resetting doubles_count; jail-exit doubles do not earn a bonus turn. pay_jail_fine uses ordinary _roll_and_move instead.",
            "limit": "Complete219bundle read. ReceivedPAY conflicts with content/providerROLL. Both exact-prefix branches draw the historical nondouble5+2, pay50 and collect100, giving equal actor and board state at the next management decision. No realized50loss from the mismatch; successful-double alternatives are not simulated, and upstream mechanism remains unidentified."}


def main():
    report = {"trade": trade_check(), "reserve": reserve_check(), "jail": jail_check(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "g11_sample_boundary_checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"red_completion_conditional": True, "house_then_vermont_cash": 163,
                      "both_jail_branches_cash": 830}))


if __name__ == "__main__":
    main()
