"""Opus phase-1 tests, version opus_phase1_v1.

Most scenarios drive the REAL engine with scripted dice and hand-set positions, so the
event stream has true engine semantics. Expected values are written from the declared
rules before reading reducer output; they are not copied from the reducer or from peers.
Synthetic event streams cover cases the engine cannot easily reach (missing menus,
truncated records). The branch test checks that recorded-action prefix replay plus
event-fed memory reproduces a recorded decision exactly and that a new legal suffix
can be applied from there.

Run from repo root:
  PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python -m pytest -q -p no:cacheprovider \
      docs/research_raw/paper_phase1_2026-10-28/opus
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from opus_reduce import (game_dirs, load_board, load_jsonl, measure_access,  # noqa: E402
                         reduce_events)

from monopoly_engine import Engine  # noqa: E402
from monopoly_engine.board import SPACE_KEY_BY_INDEX as KEY  # noqa: E402

BOARD = load_board()
HERE = Path(__file__).resolve().parent
NONE = {"cash": 0, "properties": [], "get_out_of_jail_cards": 0}


def bundle(cash=0, *spaces):
    return {"cash": cash, "properties": [KEY[i] for i in spaces], "get_out_of_jail_cards": 0}


class Script:
    """Drive a live engine; record events, menus and chosen actions."""

    def __init__(self, n=2, rolls=(), active=None):
        self.g = Engine(seed=7, run_id="t", max_turns=None,
                        players=[{"player_id": f"p{i}", "name": f"P{i}"} for i in range(n)])
        self.players = [p.player_id for p in self.g.state.players]
        self.rolls = list(rolls)
        self.g._rng.roll_dice = lambda: self.rolls.pop(0)
        if active:
            self.g.state.active_player_id = active
        self.events, self.menus, self.resolved, self.d = [], {}, {}, None
        self.initial = None

    def p(self, pid):
        return next(x for x in self.g.state.players if x.player_id == pid)

    def own(self, pid, *spaces, mortgaged=(), houses=None):
        for i in spaces:
            self.g.state.board[i].owner_id = pid
        for i in mortgaged:
            self.g.state.board[i].mortgaged = True
        for i, h in (houses or {}).items():
            self.g.state.board[i].houses = h
            self.g.state.bank.houses_remaining -= h

    def _note(self, d):
        if d is None:
            return
        opts = (d.get("post_turn") or {}).get("options") or {}
        self.menus[d["decision_id"]] = {
            "available_actions": [a["action"] for a in d["legal_actions"]],
            "buildable_space_keys": [KEY[i] for i in opts.get("buildable_space_indices", [])],
        }

    def advance(self):
        if self.initial is None:
            self.initial = self.g.get_snapshot()
        _, ev, d, _ = self.g.advance_until_decision()
        self.events += ev
        self.d = d
        self._note(d)
        return d

    def do(self, name, **args):
        d = self.d
        self.resolved[d["decision_id"]] = {"final_action": {"action": name}}
        _, ev, nd, _ = self.g.apply_action({"schema_version": "v1", "decision_id": d["decision_id"],
                                            "action": name, "args": args})
        self.events += ev
        self.d = nd
        self._note(nd)
        return nd

    def reduce(self):
        return reduce_events(self.events, BOARD, self.players, initial=self.initial)

    def access(self, ep):
        return measure_access(ep, self.events, BOARD, self.menus, self.resolved)


def episodes(res, pid, group):
    return [e for e in res["episodes"] if e["player_id"] == pid and e["group"] == group]


# --------------------------------------------------------------------------- routes


def test_direct_purchase_completes_group_buildable_on_entry():
    s = Script(rolls=[(1, 2)])
    s.own("p0", 1)
    assert s.advance()["decision_type"] == "BUY_OR_AUCTION_DECISION"     # lands on Baltic (3)
    s.do("buy_property")
    s.do("build_houses_or_hotel", build_plan=[{"space_key": KEY[1], "kind": "HOUSE", "count": 1}])
    s.do("end_turn")
    res = s.reduce()
    (acq,) = [a for a in res["acquisitions"] if a["space_index"] == 3]
    assert (acq["route"], acq["price"], acq["to"]) == ("direct_purchase", 60, "p0")
    (ep,) = episodes(res, "p0", "BROWN")
    assert ep["completion_route"] == "direct_purchase"
    assert ep["constituent_routes"] == {"MEDITERRANEAN_AVENUE": "initial_state", "BALTIC_AVENUE": "direct_purchase"}
    m = s.access(ep)
    assert (m["same_turn_access"], m["entry_buildable"], m["built_in_first_mgmt_turn"]) == (True, True, True)
    assert res["ledger"].cash["p0"] == 1500 - 60 - 50


def test_auction_win_completes_group_with_auction_route():
    s = Script(rolls=[(1, 2)])
    s.own("p0", 1)
    s.advance()
    s.do("start_auction")
    s.do("bid_auction", bid_amount=10)      # p1 bids first (bidders start after initiator)
    s.do("bid_auction", bid_amount=20)      # p0
    s.do("drop_out")                        # p1
    s.do("end_turn")
    res = s.reduce()
    (acq,) = [a for a in res["acquisitions"] if a["space_index"] == 3]
    assert (acq["route"], acq["price"], acq["to"]) == ("auction", 20, "p0")
    assert episodes(res, "p0", "BROWN")[0]["completion_route"] == "auction"
    assert res["ledger"].cash == {"p0": 1480, "p1": 1500}


# --------------------------------------------------------------- trades and settlement


def test_counter_reverses_author_recipient_pays_interest_financing_creates_legality():
    s = Script(rolls=[(4, 6)])
    s.own("p0", 1)
    s.own("p1", 3, mortgaged=[3])
    s.p("p0").position = 10
    s.advance()                                                   # p0 lands on Free Parking
    s.do("propose_trade", to_player_id="p1", offer=bundle(100), request=bundle(0, 3))
    s.do("counter_trade", offer=bundle(0, 3), request=bundle(150))  # p1 now authors the terms
    s.do("accept_trade")                                          # p0 accepts p1's counter
    assert "build_houses_or_hotel" not in s.menus[s.d["decision_id"]]["available_actions"]
    s.do("unmortgage_property", space_key=KEY[3])                 # ceil(30 * 1.1) = 33
    s.do("build_houses_or_hotel", build_plan=[{"space_key": KEY[1], "kind": "HOUSE", "count": 1}])
    s.do("end_turn")
    res = s.reduce()
    (t,) = res["trades"]
    assert (t["thread_initiator"], t["final_offer_author"], t["accepting_player"]) == ("p0", "p1", "p0")
    assert t["settlement_matches_payload"]
    # Baltic mortgage value 30 -> recipient p0 pays ceil(3.0) = 3 interest.
    assert t["interest_paid"] == {"p0": 3, "p1": 0}
    assert t["cash_before"] == {"p0": 1500, "p1": 1500}
    assert t["cash_after"] == {"p0": 1500 - 150 - 3, "p1": 1650}
    assert t["mortgaged_deeds_moved"] == ["BALTIC_AVENUE"]
    (ep,) = episodes(res, "p0", "BROWN")
    assert (ep["completion_route"], ep["mortgaged_at_start"], ep["start_on_owner_turn"]) == ("trade", 1, True)
    m = s.access(ep)
    assert m["same_turn_access"] and m["entry_buildable"] is False
    assert m["buildable_any_menu_first_turn"] is True and m["built_in_first_mgmt_turn"] is True
    assert res["ledger"].cash["p0"] == 1347 - 33 - 50


def test_interest_rounds_up_on_odd_mortgage_value():
    # Park Place price 350 -> mortgage 175 -> interest ceil(17.5) = 18.
    s = Script(rolls=[(4, 6)])
    s.own("p1", 37, mortgaged=[37])
    s.p("p0").position = 10
    s.advance()
    s.do("propose_trade", to_player_id="p1", offer=bundle(200), request=bundle(0, 37))
    s.do("accept_trade")
    (t,) = s.reduce()["trades"]
    assert t["final_offer_author"] == "p0" and t["accepting_player"] == "p1"
    assert t["interest_paid"] == {"p0": 18, "p1": 0}
    assert t["cash_after"] == {"p0": 1500 - 200 - 18, "p1": 1700}


def test_loss_and_reacquisition_make_two_episodes():
    s = Script(rolls=[(4, 6)])
    s.own("p0", 1)
    s.own("p1", 3)
    s.p("p0").position = 10
    s.advance()
    s.do("propose_trade", to_player_id="p1", offer=bundle(100), request=bundle(0, 3))
    s.do("accept_trade")
    s.do("propose_trade", to_player_id="p1", offer=bundle(0, 3), request=bundle(120))
    s.do("accept_trade")
    s.do("propose_trade", to_player_id="p1", offer=bundle(130), request=bundle(0, 3))
    s.do("accept_trade")
    s.do("end_turn")
    res = s.reduce()
    eps = episodes(res, "p0", "BROWN")
    assert [e["end_reason"] for e in eps] == ["traded_away", "record_end"]
    assert eps[0]["end_seq"] < eps[1]["start_seq"]
    assert res["ledger"].cash == {"p0": 1500 - 100 + 120 - 130, "p1": 1500 + 100 - 120 + 130}


# ---------------------------------------------------------------- access and timing


def test_recipient_in_jail_gets_first_menu_only_after_leaving_jail():
    # p1 completes light blue on p0's turn, fails a doubles roll in jail, then pays the fine.
    s = Script(rolls=[(2, 3), (1, 2), (2, 3), (4, 6)])
    s.own("p0", 5, 9)
    s.own("p1", 6, 8)
    p1 = s.p("p1")
    p1.position, p1.in_jail, p1.jail_turns = 10, True, 0
    s.advance()                                                   # turn 0: p0 lands on own railroad
    s.do("propose_trade", to_player_id="p1", offer=bundle(0, 9), request=bundle(50))
    s.do("accept_trade")
    s.do("end_turn")
    assert s.advance()["decision_type"] == "JAIL_DECISION"        # turn 1: p1 in jail
    s.do("roll_for_doubles")                                      # (1,2) fails; no menu this turn
    s.advance()                                                   # turn 2: p0 to Just Visiting
    s.do("end_turn")
    assert s.advance()["decision_type"] == "JAIL_DECISION"        # turn 3
    s.do("pay_jail_fine")                                         # then rolls (4,6) to Free Parking
    assert s.d["decision_type"] == "POST_TURN_ACTION_DECISION"
    s.do("build_houses_or_hotel", build_plan=[{"space_key": KEY[6], "kind": "HOUSE", "count": 1}])
    s.do("end_turn")
    res = s.reduce()
    (ep,) = episodes(res, "p1", "LIGHT_BLUE")
    assert ep["completion_route"] == "trade" and ep["start_on_owner_turn"] is False
    m = s.access(ep)
    assert m["same_turn_access"] is False
    assert m["own_turns_without_access"] == 1 and m["no_access_turn_reasons"] == ["jail_stay"]
    assert [(j["chosen"], j["pay_fine_legal"]) for j in m["jail_decisions_before_access"]] == [
        ("roll_for_doubles", True), ("pay_jail_fine", True)]
    assert m["global_turn_delay"] == 3
    assert m["entry_buildable"] and m["built_in_first_mgmt_turn"]
    assert res["ledger"].cash["p1"] == 1500 - 50 - 50 - 50


def test_recipient_on_other_turn_declines_first_legal_menu():
    s = Script(rolls=[(4, 6), (4, 6)], active="p1")
    s.own("p0", 6, 8)
    s.own("p1", 9)
    s.p("p1").position = 0
    s.p("p0").position = 10
    s.advance()                                                   # turn 0 p1: 0 -> 10 visiting
    s.do("propose_trade", to_player_id="p0", offer=bundle(0, 9), request=bundle(60))
    s.do("accept_trade")                                          # p0 completes light blue on p1's turn
    s.do("end_turn")
    s.advance()                                                   # turn 1 p0: 10 -> 20, legal menu
    s.do("end_turn")                                              # declines to build
    res = s.reduce()
    (ep,) = episodes(res, "p0", "LIGHT_BLUE")
    m = s.access(ep)
    assert ep["start_on_owner_turn"] is False and m["same_turn_access"] is False
    assert (m["own_turns_without_access"], m["global_turn_delay"]) == (0, 1)
    assert m["entry_buildable"] is True and m["built_in_first_mgmt_turn"] is False
    assert m["legal_turns_skipped_before_first_build"] == 1 and m["built_in_episode"] is False


def test_sent_to_jail_reason_is_recorded():
    s = Script(rolls=[(4, 6), (4, 6), (2, 3), (4, 6)])
    s.own("p0", 5, 9, 15)
    s.own("p1", 6, 8)
    s.p("p1").position = 20
    s.p("p0").position = 0
    s.advance()                                                   # turn 0 p0: 0 -> 10
    s.do("propose_trade", to_player_id="p1", offer=bundle(0, 9), request=bundle(50))
    s.do("accept_trade")
    s.do("end_turn")
    s.advance()                                                   # turn 1 p1: 20 -> 30 Go To Jail
    s.advance()                                                   # turn 2 p0: 10 -> 15 own railroad
    s.do("end_turn")
    assert s.advance()["decision_type"] == "JAIL_DECISION"        # turn 3 p1
    s.do("pay_jail_fine")                                         # (4,6) -> 20
    res = s.reduce()
    (ep,) = episodes(res, "p1", "LIGHT_BLUE")
    m = s.access(ep)
    assert m["no_access_turn_reasons"] == ["sent_to_jail"]
    assert m["own_turns_without_access"] == 1 and m["entry_buildable"] is True


# ---------------------------------------------------------------------- bankruptcy


def test_creditor_bankruptcy_keeps_buildings_and_mortgage_without_interest_and_censors():
    s = Script(rolls=[(2, 4)], active="p1")
    s.own("p0", 6, 8, 9)
    s.own("p1", 1, 3, 5, mortgaged=[5], houses={1: 1, 3: 1})
    s.p("p1").cash = 0
    assert s.advance()["decision_type"] == "LIQUIDATION_DECISION"  # owes 12 on Oriental
    s.do("declare_bankruptcy")
    res = s.reduce()
    inh = {a["space_index"]: a for a in res["acquisitions"] if a["route"] == "creditor_inheritance"}
    assert sorted(inh) == [1, 3, 5] and all(a["to"] == "p0" and a["price"] == 0 for a in inh.values())
    assert (inh[1]["buildings_on_receipt"], inh[5]["mortgaged_on_receipt"]) == (1, True)
    assert not any(e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "MORTGAGE_INTEREST" for e in s.events)
    (ep,) = episodes(res, "p0", "BROWN")
    assert (ep["completion_route"], ep["buildings_at_start"], ep["end_reason"]) == ("creditor_inheritance", 2, "game_end")
    assert s.access(ep)["access"] == "censored_game_end"
    L = res["ledger"]
    assert (L.houses[1], L.mortgaged[5], L.bankrupt["p1"], L.bank_houses) == (1, True, True, 30)


def test_bank_bankruptcy_returns_deeds_silently_then_direct_reacquisition():
    s = Script(n=3, rolls=[(1, 3), (1, 2)], active="p1")
    s.own("p1", 1, 3, 5, mortgaged=[5], houses={1: 1, 3: 1})
    s.p("p1").cash = 0
    assert s.advance()["decision_type"] == "LIQUIDATION_DECISION"  # Income Tax
    s.do("declare_bankruptcy")
    assert not any(e["type"] in ("PROPERTY_PURCHASED", "PROPERTY_TRANSFERRED") for e in s.events)
    assert s.advance()["decision_type"] == "BUY_OR_AUCTION_DECISION"  # p2 lands on Baltic
    s.do("buy_property")
    s.do("end_turn")
    res = s.reduce()
    routes = [(a["space_index"], a["route"]) for a in res["acquisitions"]]
    assert routes == [(1, "returned_to_bank"), (3, "returned_to_bank"), (5, "returned_to_bank"), (3, "direct_purchase")]
    (ep,) = episodes(res, "p1", "BROWN")
    assert ep["end_reason"] == "bankrupt_to_bank"
    L = res["ledger"]
    assert (L.owner[1], L.owner[3], L.mortgaged[5], L.houses[1], L.bank_houses) == (None, "p2", False, 0, 32)


# ------------------------------------------------------- synthetic edge cases


def _ev(seq, typ, payload=None, turn=0, actor=None):
    return {"seq": seq, "type": typ, "turn_index": turn, "payload": payload or {},
            "actor": {"kind": "PLAYER" if actor else "ENGINE", "player_id": actor}}


def _synthetic(tail):
    base = [_ev(0, "TURN_STARTED"), _ev(1, "DICE_ROLLED", {"d1": 1, "d2": 2}, actor="p0"),
            _ev(2, "PROPERTY_PURCHASED", {"player_id": "p0", "space_index": 1, "price": 60}, actor="p0"),
            _ev(3, "PROPERTY_PURCHASED", {"player_id": "p0", "space_index": 3, "price": 60}, actor="p0")]
    return base + [dict(e, seq=4 + k) for k, e in enumerate(tail)]


def test_missing_menu_is_unknown_not_illegal():
    events = _synthetic([_ev(0, "LLM_DECISION_REQUESTED", {"decision_id": "x", "player_id": "p0",
                                                           "decision_type": "POST_TURN_ACTION_DECISION"})])
    res = reduce_events(events, BOARD, ["p0", "p1"])
    m = measure_access(res["episodes"][0], events, BOARD, {}, {})
    assert m["menu_missing"] is True and m["entry_buildable"] is None
    assert m["buildable_any_menu_first_turn"] is None


def test_record_end_without_access_is_censored_not_declined():
    events = _synthetic([_ev(0, "TURN_ENDED")])
    res = reduce_events(events, BOARD, ["p0", "p1"])
    m = measure_access(res["episodes"][0], events, BOARD, {}, {})
    assert m["access"] == "censored_record_end" and "entry_buildable" not in m


def test_zero_price_unowned_purchase_and_orphan_transfer_fail_loudly():
    with pytest.raises(ValueError, match="zero-price"):
        reduce_events([_ev(0, "PROPERTY_PURCHASED", {"player_id": "p0", "space_index": 1, "price": 0})], BOARD, ["p0"])
    with pytest.raises(ValueError, match="outside trade"):
        reduce_events([_ev(0, "PROPERTY_TRANSFERRED", {"from_player_id": "p0", "to_player_id": "p1",
                                                       "space_index": 1, "mortgaged": False})], BOARD, ["p0", "p1"])


def test_space_keys_match_engine_keys():
    assert {i: BOARD["key"][i] for i in BOARD["ownable"]} == {i: KEY[i] for i in BOARD["ownable"]}


# ---------------------------------------------------------------- real corpus anchors

RESULTS = HERE / "opus_results.json"
EPISODES = HERE / "opus_group_episodes.jsonl"
TRADES = HERE / "opus_trades.jsonl"


@pytest.mark.skipif(not EPISODES.exists(), reason="run opus_corpus.py first")
def test_corpus_jail_anchor_cases():
    eps = [json.loads(line) for line in EPISODES.open()]

    def find(game, model, group):
        (e,) = [x for x in eps if x["game"] == game and x["model"] == model and x["group"] == group
                and x["completion_route"] == "trade"]
        return e
    g6 = find(6, "Opus", "PINK")
    assert (g6["start_turn"], g6["first_mgmt_turn"], g6["built_in_first_mgmt_turn"]) == (74, 85, True)
    assert [j["chosen"] for j in g6["jail_decisions_before_access"]] == ["roll_for_doubles", "roll_for_doubles"]
    g8 = find(8, "Gemini", "DARK_BLUE")
    assert (g8["start_turn"], g8["first_mgmt_turn"]) == (77, 87)
    assert [j["chosen"] for j in g8["jail_decisions_before_access"]] == ["roll_for_doubles", "pay_jail_fine"]


@pytest.mark.skipif(not TRADES.exists(), reason="run opus_corpus.py first")
def test_corpus_game1_interest_settlement_anchor():
    trades = [json.loads(line) for line in TRADES.open()]
    (t,) = [x for x in trades if x["game"] == 1 and x["seq"] == 1989]
    opus = next(p for p, m in t["models"].items() if m == "Opus")
    grok = next(p for p, m in t["models"].items() if m == "Grok")
    assert (t["cash_before"][opus], t["cash_before"][grok]) == (68, 347)
    assert (t["cash_after"][opus], t["cash_after"][grok]) == (168, 229)
    assert t["interest_paid"][grok] == 18 and t["settlement_matches_payload"]


@pytest.mark.skipif(not RESULTS.exists(), reason="run opus_corpus.py first")
def test_corpus_totals_and_reconciliation():
    r = json.loads(RESULTS.read_text())
    assert (r["n_games"], r["events"], r["decisions"], r["trades"]) == (20, 50918, 6989, 113)
    assert r["snapshots_matched"] == r["snapshots_total"] and r["terminal_snapshot_matches"] == 20
    assert r["trade_settlements_matching_payload"] == 113 and r["reducer_issues"] == 0
    assert r["deed_routes"] == {"direct_purchase": 475, "auction": 72, "creditor_inheritance": 397,
                                "trade": 207, "returned_to_bank": 10}


# ------------------------------------------------- sandbox: exact prefix reset and branch


def _game1():
    gno, run, _ = game_dirs()[0]
    assert gno == 1
    return run


def test_prefix_replay_reproduces_recorded_observation_and_accepts_new_suffix():
    """Reset to recorded decision K by replaying actions; rebuild memory from events; branch.

    Verifies: (a) replayed prefix events equal the recorded events byte-for-byte after
    canonicalization; (b) the engine's pending decision at K has the recorded id; (c) the
    agent memory rebuilt from prefix events equals the memory in the recorded prompt for K;
    (d) a different legal action is accepted at K and the suffix diverges from the record;
    (e) the hidden RNG state is the recorded one: replaying the recorded action at K instead
    reproduces the next recorded events exactly.
    """
    from monopoly_arena.prompting import PromptMemory
    from monopoly_engine.replay import canonical_event_lines

    run = _game1()
    cfg = json.loads((run / "run_config.json").read_text())
    actions = load_jsonl(run / "actions.jsonl")
    events = load_jsonl(run / "events.jsonl")
    started = {r["decision_id"]: r for r in load_jsonl(run / "decisions.jsonl") if r["phase"] == "decision_started"}
    # choose a recorded buy decision late enough to have rich memory
    k = next(i for i, a in enumerate(actions) if i > 150 and a["action"]["action"] == "buy_property")

    def engine():
        return Engine(seed=cfg["seed"], players=cfg["players"], run_id=cfg["run_id"], max_turns=cfg["max_turns"],
                      max_trade_exchanges=cfg["max_trade_exchanges"], max_auction_actions=cfg["max_auction_actions"])

    def prefix(eng):
        out = []
        for a in actions[:k]:
            _, ev, d, _ = eng.advance_until_decision(max_steps=10_000)
            out += ev
            assert d["decision_id"] == a["decision_id"]
            _, ev, _, _ = eng.apply_action(a["action"], decision_meta=a.get("decision_meta"))
            out += ev
        _, ev, d, _ = eng.advance_until_decision(max_steps=10_000)
        return out + ev, d

    eng = engine()
    pre, d = prefix(eng)
    n = len(pre)
    assert canonical_event_lines(pre) == canonical_event_lines(events[:n])               # (a)
    assert d["decision_id"] == actions[k]["decision_id"]                                  # (b)
    mem = PromptMemory()
    for e in pre:
        mem.update(e)
    recorded = started[d["decision_id"]]["prompt_payload"]["game_state"]["memory"]
    assert mem.snapshot_for_player(d["player_id"]) == recorded                            # (c)
    alt = {"schema_version": "v1", "decision_id": d["decision_id"], "action": "start_auction", "args": {}}
    assert "start_auction" in [x["action"] for x in d["legal_actions"]]
    _, branch, _, _ = eng.apply_action(alt)
    assert canonical_event_lines(branch) != canonical_event_lines(events[n:n + len(branch)])  # (d)
    eng2 = engine()
    pre2, d2 = prefix(eng2)
    _, same, _, _ = eng2.apply_action(actions[k]["action"], decision_meta=actions[k].get("decision_meta"))
    _, more, _, _ = eng2.advance_until_decision(max_steps=10_000)
    tail = same + more
    assert canonical_event_lines(tail) == canonical_event_lines(events[n:n + len(tail)])    # (e)


def test_model_facing_memory_is_a_function_of_canonical_events_game1():
    """Every recorded prompt memory (public timeline + private notes) in game 1 equals
    PromptMemory rebuilt from canonical events up to that decision request."""
    from monopoly_arena.prompting import PromptMemory

    run = _game1()
    started = {r["decision_id"]: r for r in load_jsonl(run / "decisions.jsonl") if r["phase"] == "decision_started"}
    mem, checked = PromptMemory(), 0
    for e in load_jsonl(run / "events.jsonl"):
        mem.update(e)
        if e["type"] == "LLM_DECISION_REQUESTED":
            d = e["payload"]["decision_id"]
            assert mem.snapshot_for_player(e["payload"]["player_id"]) == \
                started[d]["prompt_payload"]["game_state"]["memory"], d
            checked += 1
    assert checked == len(started) == 486


SANDBOX = HERE / "opus_sandbox_checks.json"


@pytest.mark.skipif(not SANDBOX.exists(), reason="run opus_sandbox_checks.py first")
def test_sandbox_summary_all_games():
    r = json.loads(SANDBOX.read_text())
    assert r["memory_reconstruction"]["memory_equal"] == r["memory_reconstruction"]["decisions"] == 6989
    s = r["branch_summary"]
    assert (s["prefix_identical"], s["memory_equal_at_k"], s["recorded_suffix_reproduced"], s["branch_diverges"]) == (20, 20, 20, 20)
    # Uncapped termination is not guaranteed under a weak reference policy: one rollout did not end.
    assert s["rollout_terminal"] == 19
