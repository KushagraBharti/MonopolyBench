"""Fable phase-1 independent event reducer (fable_phase1_v1).

Downstream research code. Reads the two October collection indexes read-only and
writes every output beside this file. It imports neither the engine nor any peer
reducer. Expected behaviours in the companion tests were specified from reading
engine.py (trade settlement, bankruptcy, purchase, jail, post-turn menus) before
the corpus was reduced, not from peers' output files.

Design choices that make this a cross-check rather than a copy of Sol's reducer:

* Acquisition route is classified from the engine's *paired cash event*
  (buy_property / auction_bid / none for creditor inheritance), then compared
  with an ownership-transition classifier. Two independent signals must agree.
* Every TRADE_ACCEPTED settlement is *predicted* from the accepted payload alone
  (cash, transfers, mortgaged flags, 10% mortgage-transfer interest, ordering)
  and compared with the events the engine actually emitted.
* Every bankruptcy block is predicted (cash sweep, marker, inherited deed set in
  board order or bank return) and compared with emitted events.
* Get-out-of-jail cards move in trades and bankruptcies without any event. They
  are tracked from events plus applied actions and compared with every saved
  decision observation, which quantifies that replay-surface gap.
* Own-turn access classes (management menu, jail without exit, sent to jail,
  bankrupted, game-ending turn) are derived per turn and checked against the
  engine's documented rule that jail and bankruptcy suppress the menu.
* Common-random-number horizon: the first draw at which the roller's seat, and
  the first at which the landing square, differ between rotations of a block.
* Group episodes for *all* routes with two deployment windows (first actual
  management menu; next own turn) plus buildings present at inheritance.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
COLLECTIONS = [
    ROOT / "saved_games/railway-research-12-games-2026-10-25",
    ROOT / "saved_games/railway-research-8-games-2026-10-26",
]
NAMES = {
    "openai/gpt-6.1-sol": "Sol",
    "google/gemini-4-argon": "Gemini",
    "anthropic/claude-opus-5.5": "Opus",
    "x-ai/grok-4.7": "Grok",
}
BUILD_EVENTS = {"HOUSE_BUILT", "HOTEL_BUILT"}
MANAGEMENT = "POST_TURN_ACTION_DECISION"
STARTING_CASH = 1500
BANK_HOUSES, BANK_HOTELS = 32, 12
JAIL_CARD = "GET_OUT_OF_JAIL_FREE"


def space_key(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name.strip()).strip("_").upper()


def mortgage_interest(price: int) -> int:
    """Engine: ceil(10% of mortgage value), mortgage value = price // 2."""
    return int(math.ceil((price // 2) * 0.1))


class Board:
    def __init__(self, spaces):
        self.spaces = spaces
        self.price = {s["index"]: s["price"] for s in spaces if s.get("price") is not None}
        self.key_to_index = {space_key(s["name"]): s["index"] for s in spaces}
        self.index_to_key = {v: k for k, v in self.key_to_index.items()}
        self.groups: dict[str, list[int]] = defaultdict(list)
        for s in spaces:
            if s["kind"] == "PROPERTY":
                self.groups[s["group"]].append(s["index"])
        self.group_of = {i: g for g, idx in self.groups.items() for i in idx}


class Tracker:
    """Fold economic state from events; independent of engine and peers."""

    def __init__(self, players, board: Board):
        self.board = board
        self.cash = {p: STARTING_CASH for p in players}
        self.owner = {i: None for i in board.price}
        self.mortgaged = {i: False for i in board.price}
        self.houses = {i: 0 for i in board.price}
        self.hotel = {i: False for i in board.price}
        self.jail_cards = {p: 0 for p in players}
        self.bankrupt = {p: False for p in players}

    def deeds_of(self, pid):
        return [i for i in sorted(self.owner) if self.owner[i] == pid]

    def groups_of(self, pid):
        return {g for g, idx in self.board.groups.items() if all(self.owner[i] == pid for i in idx)}

    def buildings_on(self, group):
        return sum(self.houses[i] + (5 if self.hotel[i] else 0) for i in self.board.groups[group])

    def apply(self, e):
        t, p = e["type"], e["payload"]
        if t == "CASH_CHANGED":
            self.cash[p["player_id"]] += p["delta"]
            if p["reason"] == "BANKRUPTCY":
                self.bankrupt[p["player_id"]] = True
            if p["reason"] == "BANKRUPTCY_ASSETS_TO_BANK":
                for i in self.deeds_of(p["player_id"]):
                    self.owner[i] = None
                    self.mortgaged[i] = False
                    self.houses[i] = 0
                    self.hotel[i] = False
        elif t == "PROPERTY_PURCHASED":
            self.owner[p["space_index"]] = p["player_id"]
        elif t == "PROPERTY_TRANSFERRED":
            self.owner[p["space_index"]] = p["to_player_id"]
        elif t == "PROPERTY_MORTGAGED":
            self.mortgaged[p["space_index"]] = True
        elif t == "PROPERTY_UNMORTGAGED":
            self.mortgaged[p["space_index"]] = False
        elif t == "HOUSE_BUILT":
            self.houses[p["space_index"]] += p["count"]
        elif t == "HOUSE_SOLD":
            self.houses[p["space_index"]] -= p["count"]
        elif t == "HOTEL_BUILT":
            self.houses[p["space_index"]] = 0
            self.hotel[p["space_index"]] = True
        elif t == "HOTEL_SOLD":
            self.hotel[p["space_index"]] = False
            self.houses[p["space_index"]] = 4
        elif t == "CARD_DRAWN" and p["card_id"] == JAIL_CARD:
            self.jail_cards[e["actor"]["player_id"]] += 1


# ---------------------------------------------------------------- routes


def route_by_paired_cash(events, i):
    """Classify PROPERTY_PURCHASED at index i by the engine's paired cash event.

    Direct purchase: next event CASH_CHANGED reason buy_property, same player,
    delta == -price. Auction: reason auction_bid. Creditor inheritance: price 0,
    no paired cash event, and a CASH_CHANGED reason BANKRUPTCY for a *different*
    player earlier in the same contiguous bankruptcy block. Anything else raises.
    """
    e = events[i]
    p = e["payload"]
    nxt = events[i + 1] if i + 1 < len(events) else None
    if nxt and nxt["type"] == "CASH_CHANGED" and nxt["payload"]["player_id"] == p["player_id"] \
            and nxt["payload"]["delta"] == -p["price"]:
        reason = nxt["payload"]["reason"]
        if reason == "buy_property":
            return "direct_purchase"
        if reason == "auction_bid":
            return "auction"
    if p["price"] == 0:
        j = i - 1
        while j >= 0 and events[j]["type"] == "PROPERTY_PURCHASED" and events[j]["payload"]["price"] == 0:
            j -= 1
        if j >= 0 and events[j]["type"] == "CASH_CHANGED" and events[j]["payload"]["reason"] == "BANKRUPTCY" \
                and events[j]["payload"]["player_id"] != p["player_id"]:
            return "creditor_inheritance"
    raise ValueError(f"Unclassifiable PROPERTY_PURCHASED at seq {e.get('seq')}: {p}")


def route_by_ownership(tracker: Tracker, e, in_auction: bool):
    p = e["payload"]
    prev = tracker.owner[p["space_index"]]
    if prev is not None:
        return "creditor_inheritance"
    return "auction" if in_auction else "direct_purchase"


# ------------------------------------------------------- trade settlement


def predict_settlement(accepted, tracker: Tracker):
    """Predict the event sequence the engine emits after TRADE_ACCEPTED.

    Returns (expected, offerer, acceptor, meta). Expected entries are
    (type, payload-subset) tuples in engine order: offer cash pair, request cash
    pair, offer transfers, request transfers, offerer interest, acceptor interest.
    Jail cards produce no event; they are reported in meta.
    """
    p = accepted["payload"]
    acceptor = accepted["actor"]["player_id"]
    parties = {p["initiator_player_id"], p["counterparty_player_id"]}
    assert acceptor in parties and len(parties) == 2
    offerer = next(x for x in parties if x != acceptor)
    offer, request = p["offer"], p["request"]
    b = tracker.board
    expected = []
    if offer["cash"]:
        expected.append(("CASH_CHANGED", {"player_id": offerer, "delta": -offer["cash"], "reason": "TRADE_CASH"}))
        expected.append(("CASH_CHANGED", {"player_id": acceptor, "delta": offer["cash"], "reason": "TRADE_CASH"}))
    if request["cash"]:
        expected.append(("CASH_CHANGED", {"player_id": acceptor, "delta": -request["cash"], "reason": "TRADE_CASH"}))
        expected.append(("CASH_CHANGED", {"player_id": offerer, "delta": request["cash"], "reason": "TRADE_CASH"}))
    offer_idx = [b.key_to_index[k] for k in offer["properties"]]
    request_idx = [b.key_to_index[k] for k in request["properties"]]
    for i in offer_idx:
        expected.append(("PROPERTY_TRANSFERRED", {"from_player_id": offerer, "to_player_id": acceptor,
                                                  "space_index": i, "mortgaged": tracker.mortgaged[i]}))
    for i in request_idx:
        expected.append(("PROPERTY_TRANSFERRED", {"from_player_id": acceptor, "to_player_id": offerer,
                                                  "space_index": i, "mortgaged": tracker.mortgaged[i]}))
    offerer_interest = sum(mortgage_interest(b.price[i]) for i in request_idx if tracker.mortgaged[i])
    acceptor_interest = sum(mortgage_interest(b.price[i]) for i in offer_idx if tracker.mortgaged[i])
    if offerer_interest:
        expected.append(("CASH_CHANGED", {"player_id": offerer, "delta": -offerer_interest, "reason": "MORTGAGE_INTEREST"}))
    if acceptor_interest:
        expected.append(("CASH_CHANGED", {"player_id": acceptor, "delta": -acceptor_interest, "reason": "MORTGAGE_INTEREST"}))
    meta = {"offerer": offerer, "acceptor": acceptor,
            "thread_initiator": p["initiator_player_id"], "thread_counterparty": p["counterparty_player_id"],
            "exchange_index": p["exchange_index"],
            "offer_cash": offer["cash"], "request_cash": request["cash"],
            "offer_properties": offer["properties"], "request_properties": request["properties"],
            "jail_cards_offerer_to_acceptor": offer["get_out_of_jail_cards"],
            "jail_cards_acceptor_to_offerer": request["get_out_of_jail_cards"],
            "offerer_interest": offerer_interest, "acceptor_interest": acceptor_interest}
    return expected, meta


def actual_settlement(events, i):
    """Events after TRADE_ACCEPTED at i that belong to its settlement."""
    out = []
    j = i + 1
    while j < len(events):
        e = events[j]
        if e["type"] == "PROPERTY_TRANSFERRED" or (
                e["type"] == "CASH_CHANGED" and e["payload"]["reason"] in {"TRADE_CASH", "MORTGAGE_INTEREST"}):
            out.append((e["type"], {k: e["payload"][k] for k in e["payload"]}))
            j += 1
        else:
            break
    return out, j


# --------------------------------------------------------------- bankruptcy


def predict_bankruptcy_block(events, i, tracker: Tracker):
    """Given CASH_CHANGED reason BANKRUPTCY at i, predict the surrounding block.

    Engine order: [BANKRUPTCY_CASH debtor, BANKRUPTCY_CASH creditor if any] (only if
    cash > 0), marker, then PROPERTY_PURCHASED price 0 for each debtor deed in board
    order to the creditor, or nothing then BANKRUPTCY_ASSETS_TO_BANK for the bank.
    Returns dict with predicted vs actual pieces. `tracker` must reflect state just
    before the first event of the block.
    """
    debtor = events[i]["payload"]["player_id"]
    cash_before = tracker.cash[debtor]
    deeds = tracker.deeds_of(debtor)
    # find creditor from preceding BANKRUPTCY_CASH pair or following purchases
    creditor = None
    k = i - 1
    sweep = []
    while k >= 0 and events[k]["type"] == "CASH_CHANGED" and events[k]["payload"]["reason"] == "BANKRUPTCY_CASH":
        sweep.insert(0, events[k]["payload"])
        k -= 1
    if sweep:
        assert sweep[0]["player_id"] == debtor and sweep[0]["delta"] == -cash_before, (events[i]["seq"], sweep, cash_before)
        if len(sweep) == 2:
            creditor = sweep[1]["player_id"]
            assert sweep[1]["delta"] == cash_before
    j = i + 1
    inherited = []
    while j < len(events) and events[j]["type"] == "PROPERTY_PURCHASED" and events[j]["payload"]["price"] == 0:
        inherited.append(events[j]["payload"])
        j += 1
    to_bank = j < len(events) and events[j]["type"] == "CASH_CHANGED" \
        and events[j]["payload"]["reason"] == "BANKRUPTCY_ASSETS_TO_BANK"
    if inherited:
        heirs = {x["player_id"] for x in inherited}
        assert len(heirs) == 1
        creditor = creditor or heirs.pop()
    return {
        "seq": events[i]["seq"], "turn": events[i]["turn_index"], "debtor": debtor,
        "cash_before": cash_before, "cash_swept_ok": (cash_before == 0) == (not sweep),
        "creditor": creditor, "to_bank": to_bank,
        "deeds_before": deeds, "inherited_indices": [x["space_index"] for x in inherited],
        "inherited_set_ok": [x["space_index"] for x in inherited] == (deeds if not to_bank else []),
        "buildings_inherited": sum(tracker.houses[i] + (5 if tracker.hotel[i] else 0) for i in deeds) if not to_bank else 0,
        "mortgaged_inherited": sum(tracker.mortgaged[i] for i in deeds) if not to_bank else 0,
        "jail_cards_moved": tracker.jail_cards[debtor],
        "block_end_exclusive": j + (1 if to_bank else 0),
    }


# ------------------------------------------------------------- turn access


def turn_table(events):
    """One row per TURN_STARTED: owner, access class, menus, flags."""
    starts = [i for i, e in enumerate(events) if e["type"] == "TURN_STARTED"]
    rows = []
    for n, s in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(events)
        seg = events[s:end]
        owner = None
        for e in seg:
            if e["actor"].get("kind") == "PLAYER":
                owner = e["actor"]["player_id"]
                break
            if e["type"] == "LLM_DECISION_REQUESTED":
                owner = e["payload"]["player_id"]
                break
        if owner is None:  # bankrupt player skipped: engine emits nothing; defensive
            continue
        types = [(e["type"], e["payload"]) for e in seg]
        first_decision = next((p["decision_type"] for t, p in types if t == "LLM_DECISION_REQUESTED"), None)
        started_in_jail = first_decision == "JAIL_DECISION" or (
            first_decision is None and any(t == "CASH_CHANGED" and p["reason"] == "BANKRUPTCY" and p["player_id"] == owner
                                           for t, p in types))
        moved = any(t == "PLAYER_MOVED" and e["actor"]["player_id"] == owner for (t, p), e in zip(types, seg))
        management = sum(1 for t, p in types if t == "LLM_DECISION_REQUESTED"
                         and p["decision_type"] == MANAGEMENT and p["player_id"] == owner)
        sent_to_jail = any(t == "SENT_TO_JAIL" and p["player_id"] == owner for t, p in types)
        bankrupt = any(t == "CASH_CHANGED" and p["reason"] == "BANKRUPTCY" and p["player_id"] == owner for t, p in types)
        game_end = any(t == "GAME_ENDED" for t, p in types)
        dice = [p for t, p in types if t == "DICE_ROLLED"]
        rows.append({
            "turn": events[s]["turn_index"], "owner": owner, "started_in_jail": started_in_jail,
            "jail_exit": started_in_jail and moved, "management_menus": management,
            "has_management": management > 0, "sent_to_jail": sent_to_jail,
            "bankrupt_in_turn": bankrupt, "game_end_turn": game_end,
            "dice_rolls": len(dice),
        })
    return rows


def access_class(row):
    if row["bankrupt_in_turn"]:
        return "bankrupted_this_turn"
    if row["started_in_jail"] and not row["jail_exit"]:
        return "jail_no_exit"
    if row["sent_to_jail"]:
        return "sent_to_jail_this_turn"
    if row["has_management"]:
        return "management"
    if row["game_end_turn"]:
        return "game_ended_before_menu"
    return "UNEXPLAINED_NO_MENU"


# --------------------------------------------------------- CRN horizon


def dice_uses(events, seat_of):
    """List of (seat, reason, landing) per DICE_ROLLED in order."""
    uses = []
    for i, e in enumerate(events):
        if e["type"] != "DICE_ROLLED":
            continue
        pid = e["actor"]["player_id"]
        landing = None
        for f in events[i + 1:i + 4]:
            if f["type"] == "PLAYER_MOVED" and f["actor"]["player_id"] == pid:
                landing = f["payload"]["to"]
                break
            if f["type"] == "DICE_ROLLED":
                break
        uses.append({"d": (e["payload"]["d1"], e["payload"]["d2"]), "seat": seat_of[pid],
                     "reason": e["payload"].get("reason"), "landing": landing, "turn": e["turn_index"]})
    return uses


def crn_horizon(a, b):
    """First draw index where seat differs / where (seat, landing) differs; None if never."""
    n = min(len(a), len(b))
    seat_div = next((k for k in range(n) if a[k]["seat"] != b[k]["seat"]), None)
    land_div = next((k for k in range(n) if (a[k]["seat"], a[k]["landing"]) != (b[k]["seat"], b[k]["landing"])), None)
    assert all(a[k]["d"] == b[k]["d"] for k in range(n)), "raw dice prefix differs"
    return {"shared_prefix_draws": n, "first_seat_divergence": seat_div, "first_landing_divergence": land_div}


# ---------------------------------------------------------- group episodes


def group_episodes(events, players, board: Board, routes_by_seq):
    """Episodes of complete colour-group ownership, all routes, with loss tracking."""
    tracker = Tracker(players, board)
    active = {}
    episodes = []
    i = 0
    n = len(events)
    turn_owner = None
    while i < n:
        e = events[i]
        if e["type"] == "TURN_STARTED":
            # resolved lazily by the first player event
            turn_owner = None
        if turn_owner is None and (e["actor"].get("kind") == "PLAYER" or e["type"] == "LLM_DECISION_REQUESTED"):
            turn_owner = e["actor"].get("player_id") or e["payload"].get("player_id")
        before = {(p, g) for p in players for g in tracker.groups_of(p)}
        if e["type"] == "TRADE_ACCEPTED":
            acts, j = actual_settlement(events, i)
            for k in range(i + 1, j):
                tracker.apply(events[k])
            marker, end_seq, route = e, events[j - 1]["seq"], "trade"
            i = j
        else:
            tracker.apply(e)
            marker, end_seq = e, e["seq"]
            route = routes_by_seq.get(e["seq"]) if e["type"] == "PROPERTY_PURCHASED" else "bank_return"
            i += 1
        after = {(p, g) for p in players for g in tracker.groups_of(p)}
        for key in sorted(before - after):
            ep = active.pop(key)
            ep.update(end_seq_exclusive=marker["seq"], end_turn=marker["turn_index"], end_reason="ownership_loss")
        for p, g in sorted(after - before):
            ep = {"player_id": p, "group": g, "route": route, "acq_seq": marker["seq"],
                  "acq_event": marker["event_id"], "acq_turn": marker["turn_index"],
                  "settlement_end_seq": end_seq, "acquired_on_own_turn": turn_owner == p,
                  "buildings_at_acquisition": tracker.buildings_on(g),
                  "mortgaged_at_acquisition": sum(tracker.mortgaged[x] for x in board.groups[g]),
                  "cash_after_acquisition": tracker.cash[p]}
            episodes.append(ep)
            active[(p, g)] = ep
    for ep in active.values():
        ep.update(end_seq_exclusive=n, end_turn=events[-1]["turn_index"], end_reason="game_end")
    return episodes


def measure_windows(ep, events, menus, board: Board, turns):
    """Two deployment windows for one episode. Pure event/menu reading."""
    pid, g = ep["player_id"], ep["group"]
    idx = set(board.groups[g])
    keys = {board.index_to_key[i] for i in idx}
    lo, hi = ep["settlement_end_seq"], ep["end_seq_exclusive"]
    fut = [e for e in events if lo < e["seq"] < hi]
    builds = [e for e in fut if e["type"] in BUILD_EVENTS and e["payload"]["player_id"] == pid
              and e["payload"]["space_index"] in idx]
    mgmt = [e for e in fut if e["type"] == "LLM_DECISION_REQUESTED" and e["payload"]["player_id"] == pid
            and e["payload"]["decision_type"] == MANAGEMENT]
    res = {"first_build_turn": builds[0]["turn_index"] if builds else None,
           "elapsed_to_build": (builds[0]["turn_index"] - ep["acq_turn"]) if builds else None,
           "ever_built": bool(builds),
           "rent_until_loss_or_end": sum(e["payload"]["amount"] for e in fut if e["type"] == "RENT_PAID"
                                         and e["payload"]["to_player_id"] == pid and e["payload"]["space_index"] in idx)}

    def legal(decision_id):
        m = menus[decision_id]
        return "build_houses_or_hotel" in m["available_actions"] and bool(keys & set(m["buildable_space_keys"]))

    # Window A: first actual management menu turn
    if mgmt:
        first = mgmt[0]
        t = first["turn_index"]
        turn_end = next((e["seq"] for e in fut if e["type"] == "TURN_ENDED" and e["seq"] > first["seq"]), hi)
        in_turn = [e for e in mgmt if e["turn_index"] == t and e["seq"] < turn_end]
        res.update(first_mgmt_turn=t, first_mgmt_decision=first["payload"]["decision_id"],
                   elapsed_to_first_mgmt=t - ep["acq_turn"],
                   entry_legal=legal(first["payload"]["decision_id"]),
                   legal_any_menu_that_turn=any(legal(e["payload"]["decision_id"]) for e in in_turn),
                   built_first_mgmt_turn=any(b["turn_index"] == t and b["seq"] < turn_end for b in builds),
                   pre_mgmt_decision_types=[e["payload"]["decision_type"] for e in fut
                                            if e["type"] == "LLM_DECISION_REQUESTED" and e["payload"]["player_id"] == pid
                                            and e["seq"] < first["seq"]])
    else:
        res.update(first_mgmt_turn=None, first_mgmt_decision=None, elapsed_to_first_mgmt=None, entry_legal=None,
                   legal_any_menu_that_turn=None, built_first_mgmt_turn=None, pre_mgmt_decision_types=[])
    # Window B: next own turn (rest of acquisition turn if own turn, else next TURN_STARTED owned by pid)
    if ep["acquired_on_own_turn"]:
        wturn = ep["acq_turn"]
    else:
        wturn = next((r["turn"] for r in turns if r["owner"] == pid and r["turn"] > ep["acq_turn"]), None)
    if wturn is None:
        res.update(next_own_turn=None, built_next_own_turn=None)
    else:
        res.update(next_own_turn=wturn, built_next_own_turn=any(b["turn_index"] == wturn for b in builds))
    # Legal-but-skipped management turns across the whole episode
    skipped = set()
    built_turns = {b["turn_index"] for b in builds}
    for e in mgmt:
        if legal(e["payload"]["decision_id"]) and e["turn_index"] not in built_turns:
            skipped.add(e["turn_index"])
    res["legal_turns_without_build"] = len(skipped)
    res["management_turns_in_episode"] = len({e["turn_index"] for e in mgmt})
    return res


# ------------------------------------------------------------ attempts


def selected_valid_index(attempts):
    valid = [i for i, a in enumerate(attempts) if a.get("outcome") == "valid"]
    return valid[-1] if valid else None


def content_tool_mismatch(attempt):
    """Minimal independent parse: content JSON name vs parsed tool-call name."""
    content, tool = attempt.get("assistant_content"), attempt.get("parsed_tool_call") or {}
    if not isinstance(content, str) or not tool.get("name"):
        return None
    try:
        obj = json.loads(content)
    except ValueError:
        m = re.search(r'"name"\s*:\s*"([a-z_]+)"', content)
        if not m or m.group(1) == tool["name"]:
            return None
        return {"content_name": m.group(1), "tool_name": tool["name"], "parsed": False, "args_equal": None}
    if not isinstance(obj, dict) or not isinstance(obj.get("name"), str) or obj["name"] == tool["name"]:
        return None
    args = tool.get("arguments")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = None
    cargs = obj.get("parameters", obj.get("arguments"))
    if cargs is None and "public_message" in obj:
        cargs = {k: v for k, v in obj.items() if k not in {"name", "type"}}
    if isinstance(cargs, str):
        try:
            cargs = json.loads(cargs)
        except ValueError:
            cargs = None
    return {"content_name": obj["name"], "tool_name": tool["name"], "parsed": True,
            "args_equal": (cargs == args) if isinstance(cargs, dict) and isinstance(args, dict) else None}


# ------------------------------------------------------------------ main


def load_rows(path):
    with path.open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main():
    board = Board(json.loads((ROOT / "contracts/data/board.json").read_text())["spaces"])
    results = {"analysis_version": "fable_phase1_v1"}
    games = []
    sources = []
    route_cross = Counter()
    route_disagreements = []
    settlement_rows, bankruptcy_rows, episode_rows, turn_rows, crn_rows = [], [], [], [], []
    jail_card_checks = Counter()
    jail_card_diffs = []
    access_by_model = defaultdict(Counter)
    jail_choice_by_model = defaultdict(Counter)
    model_attempts = defaultdict(Counter)
    opus_chain = Counter()
    opus_by_game = {}
    memory_slot = defaultdict(Counter)
    fallback_notes = Counter()
    mismatch = defaultdict(Counter)
    opus48 = Counter()
    per_block_uses = defaultdict(list)
    per_game_models = {}
    for collection in COLLECTIONS:
        index_path = collection / "game-index.csv"
        sources.append(index_path)
        with index_path.open() as f:
            index = list(csv.DictReader(f))
        for row in index:
            game = int(row["collection_game"])
            run = collection / row["package"] / "run"
            cfg = json.loads((run / "run_config.json").read_text())
            summary = json.loads((run / "summary.json").read_text())
            names = {p["player_id"]: NAMES[p["openrouter_model_id"]] for p in cfg["players"]}
            seat_of = {s["player_id"]: s["seat_index"] for s in cfg["seat_assignment"]}
            players = [p["player_id"] for p in cfg["players"]]
            per_game_models[game] = names
            events = list(load_rows(run / "events.jsonl"))
            actions = list(load_rows(run / "actions.jsonl"))
            assert [e["seq"] for e in events] == list(range(len(events)))
            for fn in ("events.jsonl", "actions.jsonl", "decisions.jsonl", "run_config.json", "summary.json"):
                sources.append(run / fn)
            # --- menus and observations from decisions ledger
            menus, obs_cards, resolved = {}, {}, {}
            for d in load_rows(run / "decisions.jsonl"):
                if d["phase"] == "decision_started":
                    st = d["prompt_payload"]["action_state"]
                    menus[d["decision_id"]] = {
                        "available_actions": st["available_actions"],
                        "buildable_space_keys": st.get("scenario", {}).get("options", {}).get("buildable_space_keys", [])}
                    gs = d["prompt_payload"]["game_state"]
                    obs_cards[d["decision_id"]] = {gs["you"]["player_id"]: gs["you"]["get_out_of_jail_cards"],
                                                   **{o["player_id"]: o["get_out_of_jail_cards"] for o in gs["others"]}}
                    mem = gs["memory"]["your_private_thoughts_last_10"]
                    m = names[d["player_id"]]
                    memory_slot[m]["decisions"] += 1
                    if not mem:
                        memory_slot[m]["empty_private_memory"] += 1
                    elif all((x.get("thought") or "").strip() == "fallback" for x in mem):
                        memory_slot[m]["only_fallback_private_memory"] += 1
                    else:
                        memory_slot[m]["has_model_note"] += 1
                else:
                    resolved[d["decision_id"]] = d
            action_by_id = {a["decision_id"]: a for a in actions}
            # --- attempts, refusals, fallback notes, mismatches
            for did, d in resolved.items():
                m = names[d["player_id"]]
                atts = d["attempts"]
                sel = selected_valid_index(atts)
                model_attempts[m]["decisions"] += 1
                model_attempts[m]["attempts"] += len(atts)
                refused = [i for i, a in enumerate(atts) if a.get("outcome") == "refused"]
                model_attempts[m]["refused_attempts"] += len(refused)
                model_attempts[m]["decisions_with_refusal"] += bool(refused)
                model_attempts[m]["fallback_decisions"] += bool(d.get("fallback_used"))
                if d.get("fallback_used"):
                    fa = d["final_action"]
                    fallback_notes[(m, fa.get("private_thought"), fa.get("public_message"))] += 1
                    conds = [a.get("response_condition") for a in atts]
                    outs = [a.get("outcome") for a in atts]
                    model_attempts[m]["fallback_after_invalid_action_only_retry"] += (
                        len(atts) == 2 and conds[1] == "same_model_without_private_thought" and outs[1] != "refused")
                for a in atts:
                    if "4.8" in str(a.get("requested_model")) or "4.8" in str((a.get("raw_response") or {}).get("model")):
                        opus48["attempts_touching_opus_4_8"] += 1
                if m == "Opus":
                    opus_chain[" -> ".join(f"{a.get('response_condition')}:{a.get('outcome')}" for a in atts)] += 1
                    opus_by_game.setdefault(game, Counter())
                    opus_by_game[game]["decisions"] += 1
                    opus_by_game[game]["refused_decisions"] += bool(refused)
                    if refused and len(atts) >= 2 and atts[1].get("response_condition") == "standard":
                        model_attempts[m]["refusal_on_ordinary_corrective_retry"] += 1
                        model_attempts[m]["refusal_on_ordinary_corrective_retry_ids"] = did
                if sel is not None:
                    mm = content_tool_mismatch(atts[sel])
                    if mm:
                        mismatch[m]["selected_valid_name_mismatch"] += 1
                        mismatch[m]["parsed_json"] += mm["parsed"]
                        mismatch[m]["exact_args_equal"] += mm["args_equal"] is True
                        if mm["tool_name"] == "accept_trade" and mm["content_name"] == "reject_trade":
                            mismatch[m]["content_reject_tool_accept"] += 1
                        if mm["tool_name"] == "end_turn" and mm["content_name"] in {"build_houses_or_hotel", "mortgage_property", "unmortgage_property"}:
                            mismatch[m]["content_manage_tool_end_turn"] += 1
            # --- routes: two classifiers
            tracker = Tracker(players, board)
            in_auction = False
            routes_by_seq = {}
            i = 0
            while i < len(events):
                e = events[i]
                if e["type"] == "AUCTION_STARTED":
                    in_auction = True
                if e["type"] == "AUCTION_ENDED":
                    in_auction = False
                if e["type"] == "PROPERTY_PURCHASED":
                    r1 = route_by_paired_cash(events, i)
                    r2 = route_by_ownership(tracker, e, in_auction)
                    route_cross[(r1, r2)] += 1
                    if r1 != r2:
                        route_disagreements.append({"game": game, "seq": e["seq"], "paired_cash": r1, "ownership": r2})
                    routes_by_seq[e["seq"]] = r1
                if e["type"] == "TRADE_ACCEPTED":
                    expected, meta = predict_settlement(e, tracker)
                    actual, j = actual_settlement(events, i)
                    ok = expected == actual
                    settlement_rows.append({"game": game, "seq": e["seq"], "event_id": e["event_id"], "turn": e["turn_index"],
                                            "prediction_matches_events": ok, "n_events": len(actual),
                                            "cash_before": {p: tracker.cash[p] for p in (meta["offerer"], meta["acceptor"])},
                                            **meta})
                    if not ok:
                        settlement_rows[-1]["expected"] = expected
                        settlement_rows[-1]["actual"] = actual
                    # jail cards move without events
                    tracker.jail_cards[meta["offerer"]] -= meta["jail_cards_offerer_to_acceptor"]
                    tracker.jail_cards[meta["acceptor"]] += meta["jail_cards_offerer_to_acceptor"]
                    tracker.jail_cards[meta["acceptor"]] -= meta["jail_cards_acceptor_to_offerer"]
                    tracker.jail_cards[meta["offerer"]] += meta["jail_cards_acceptor_to_offerer"]
                    for k in range(i + 1, j):
                        tracker.apply(events[k])
                    settlement_rows[-1]["cash_after"] = {p: tracker.cash[p] for p in (meta["offerer"], meta["acceptor"])}
                    i = j
                    continue
                if e["type"] == "CASH_CHANGED" and e["payload"]["reason"] == "BANKRUPTCY":
                    # tracker currently reflects state after the sweep (sweep is cash only)
                    pre = Tracker(players, board)
                    pre.cash = dict(tracker.cash)
                    pre.owner, pre.mortgaged, pre.houses, pre.hotel = dict(tracker.owner), dict(tracker.mortgaged), dict(tracker.houses), dict(tracker.hotel)
                    pre.jail_cards = dict(tracker.jail_cards)
                    # undo sweep for cash_before
                    k = i - 1
                    while k >= 0 and events[k]["type"] == "CASH_CHANGED" and events[k]["payload"]["reason"] == "BANKRUPTCY_CASH":
                        pre.cash[events[k]["payload"]["player_id"]] -= events[k]["payload"]["delta"]
                        k -= 1
                    blk = predict_bankruptcy_block(events, i, pre)
                    blk["game"] = game
                    blk["debtor_model"] = names[blk["debtor"]]
                    blk["creditor_model"] = names.get(blk["creditor"]) if blk["creditor"] else None
                    blk["game_ending"] = any(x["type"] == "GAME_ENDED" for x in events[i:blk["block_end_exclusive"] + 3])
                    blk["via_declare_bankruptcy_action"] = any(
                        a["action"]["action"] == "declare_bankruptcy" and a["actor_player_id"] == blk["debtor"]
                        and a["turn_index"] == e["turn_index"] for a in actions)
                    bankruptcy_rows.append(blk)
                    # jail cards: creditor inherits, bank returns
                    if blk["creditor"]:
                        tracker.jail_cards[blk["creditor"]] += tracker.jail_cards[blk["debtor"]]
                    tracker.jail_cards[blk["debtor"]] = 0
                if e["type"] == "LLM_DECISION_REQUESTED":
                    did = e["payload"]["decision_id"]
                    # observation check for jail cards (state before this decision's action)
                    obs = obs_cards[did]
                    for pid, n_cards in obs.items():
                        if tracker.jail_cards[pid] == n_cards:
                            jail_card_checks["match"] += 1
                        else:
                            jail_card_checks["differ"] += 1
                            jail_card_diffs.append({"game": game, "decision_id": did, "player": pid,
                                                    "tracked": tracker.jail_cards[pid], "observed": n_cards})
                    act = action_by_id[did]["action"]
                    if act["action"] == "use_get_out_of_jail_card":
                        tracker.jail_cards[e["payload"]["player_id"]] -= 1
                tracker.apply(e)
                i += 1
            # terminal reconciliation
            assert tracker.cash == {p: summary["players"][p]["cash"] for p in players}, game
            terminal = json.loads(sorted((run / "state").glob("*.json"))[-1].read_text())
            assert tracker.owner == {s["index"]: s["owner_id"] for s in terminal["board"] if s["price"] is not None}, game
            assert {p["player_id"]: p["get_out_of_jail_cards"] for p in terminal["players"]} == tracker.jail_cards, game
            # --- turns and access
            turns = turn_table(events)
            for r in turns:
                r["game"] = game
                r["model"] = names[r["owner"]]
                r["access_class"] = access_class(r)
                access_by_model[r["model"]][r["access_class"]] += 1
                access_by_model[r["model"]]["own_turns"] += 1
                turn_rows.append(r)
            for a in actions:
                if a["decision_type"] == "JAIL_DECISION":
                    jail_choice_by_model[names[a["actor_player_id"]]][a["action"]["action"]] += 1
            # --- episodes
            eps = group_episodes(events, players, board, routes_by_seq)
            for ep in eps:
                ep.update(game=game, model=names[ep["player_id"]])
                ep.update(measure_windows(ep, events, menus, board, turns))
                ep["winner"] = ep["player_id"] == summary["winner_player_id"]
                episode_rows.append(ep)
            # --- dice uses for CRN horizon
            per_block_uses[cfg["seed"]].append((game, dice_uses(events, seat_of)))
            first_build = next(e for e in events if e["type"] in BUILD_EVENTS)
            games.append({"game": game, "seed": cfg["seed"], "source_sha": row["git_sha"][:8],
                          "treatment_fingerprint": cfg["treatment_fingerprint"][:8],
                          "seat_models": [names[s["player_id"]] for s in sorted(cfg["seat_assignment"], key=lambda s: s["seat_index"])],
                          "winner": names[summary["winner_player_id"]], "winner_seat": seat_of[summary["winner_player_id"]],
                          "turns": summary["turn_count"], "events": len(events), "decisions": len(actions),
                          "first_builder": names[first_build["payload"]["player_id"]],
                          "first_builder_won": first_build["payload"]["player_id"] == summary["winner_player_id"]})
    # CRN horizons
    for seed, lst in per_block_uses.items():
        for a in range(len(lst)):
            for b in range(a + 1, len(lst)):
                h = crn_horizon(lst[a][1], lst[b][1])
                crn_rows.append({"seed": seed, "game_a": lst[a][0], "game_b": lst[b][0], **h})
    # --- summaries
    def ep_summary(rows):
        out = {}
        for m in NAMES.values():
            sel = [r for r in rows if r["model"] == m]
            out[m] = {
                "episodes": len(sel),
                "first_mgmt_observed": sum(r["first_mgmt_turn"] is not None for r in sel),
                "built_first_mgmt_turn": sum(r["built_first_mgmt_turn"] is True for r in sel),
                "entry_legal": sum(r["entry_legal"] is True for r in sel),
                "entry_legal_and_built": sum(r["entry_legal"] is True and r["built_first_mgmt_turn"] is True for r in sel),
                "legal_any_menu_that_turn": sum(r["legal_any_menu_that_turn"] is True for r in sel),
                "built_next_own_turn": sum(r["built_next_own_turn"] is True for r in sel),
                "ever_built": sum(r["ever_built"] for r in sel),
                "legal_turns_without_build_total": sum(r["legal_turns_without_build"] for r in sel),
                "median_elapsed_to_first_mgmt": _median([r["elapsed_to_first_mgmt"] for r in sel if r["elapsed_to_first_mgmt"] is not None]),
            }
        return out
    trade_eps = [r for r in episode_rows if r["route"] == "trade"]
    purchase_eps = [r for r in episode_rows if r["route"] in {"direct_purchase", "auction"}]
    inherit_eps = [r for r in episode_rows if r["route"] == "creditor_inheritance"]
    results.update({
        "games": len(games), "events": sum(g["events"] for g in games), "decisions": sum(g["decisions"] for g in games),
        "first_builder_wins": sum(g["first_builder_won"] for g in games),
        "wins": dict(Counter(g["winner"] for g in games)),
        "route_crosscheck": {f"{a}|{b}": n for (a, b), n in sorted(route_cross.items())},
        "route_disagreements": route_disagreements,
        "deed_routes_by_paired_cash": dict(Counter(k[0] for k, n in route_cross.items() for _ in range(n))),
        "trade_settlements": {"n": len(settlement_rows),
                              "prediction_matches_events": sum(r["prediction_matches_events"] for r in settlement_rows),
                              "with_mortgage_interest": sum((r["offerer_interest"] or r["acceptor_interest"]) > 0 for r in settlement_rows),
                              "total_interest_paid": sum(r["offerer_interest"] + r["acceptor_interest"] for r in settlement_rows),
                              "with_jail_cards": sum((r["jail_cards_offerer_to_acceptor"] + r["jail_cards_acceptor_to_offerer"]) > 0 for r in settlement_rows),
                              "acceptor_is_thread_initiator": sum(r["acceptor"] == r["thread_initiator"] for r in settlement_rows)},
        "bankruptcies": {"n": len(bankruptcy_rows),
                         "to_creditor": sum(not r["to_bank"] for r in bankruptcy_rows),
                         "to_bank": sum(r["to_bank"] for r in bankruptcy_rows),
                         "inherited_set_ok": sum(r["inherited_set_ok"] for r in bankruptcy_rows),
                         "cash_sweep_ok": sum(r["cash_swept_ok"] for r in bankruptcy_rows),
                         "game_ending": sum(r["game_ending"] for r in bankruptcy_rows),
                         "via_declare_bankruptcy_action": sum(r["via_declare_bankruptcy_action"] for r in bankruptcy_rows),
                         "automatic_no_liquidation_option": sum(not r["via_declare_bankruptcy_action"] for r in bankruptcy_rows),
                         "with_buildings_inherited": sum(r["buildings_inherited"] > 0 for r in bankruptcy_rows),
                         "buildings_inherited_total": sum(r["buildings_inherited"] for r in bankruptcy_rows),
                         "mortgaged_deeds_inherited_total": sum(r["mortgaged_inherited"] for r in bankruptcy_rows),
                         "jail_cards_moved_total": sum(r["jail_cards_moved"] for r in bankruptcy_rows),
                         "debtor_by_model": dict(Counter(r["debtor_model"] for r in bankruptcy_rows)),
                         "creditor_by_model": dict(Counter(r["creditor_model"] for r in bankruptcy_rows if r["creditor_model"]))},
        "jail_card_observation_checks": dict(jail_card_checks),
        "jail_card_observation_differences": jail_card_diffs[:20],
        "turn_access_by_model": {m: dict(c) for m, c in access_by_model.items()},
        "jail_choice_by_model": {m: dict(c) for m, c in jail_choice_by_model.items()},
        "unexplained_no_menu_turns": [r for r in turn_rows if r["access_class"] == "UNEXPLAINED_NO_MENU"][:20],
        "episodes": {"total": len(episode_rows), "by_route": dict(Counter(r["route"] for r in episode_rows)),
                     "by_route_and_model": {m: dict(Counter(r["route"] for r in episode_rows if r["model"] == m)) for m in NAMES.values()},
                     "trade_route": ep_summary(trade_eps),
                     "purchase_or_auction_route": ep_summary(purchase_eps),
                     "inheritance_route": {
                         "episodes": len(inherit_eps),
                         "at_game_ending_bankruptcy": sum(r["end_reason"] == "game_end" and r["first_mgmt_turn"] is None for r in inherit_eps),
                         "with_buildings_at_inheritance": sum(r["buildings_at_acquisition"] > 0 for r in inherit_eps),
                         "with_mortgage_at_inheritance": sum(r["mortgaged_at_acquisition"] > 0 for r in inherit_eps),
                         "heir_built_later": sum(r["ever_built"] for r in inherit_eps),
                         "by_model": {m: {"episodes": sum(r["model"] == m for r in inherit_eps),
                                          "with_buildings": sum(r["model"] == m and r["buildings_at_acquisition"] > 0 for r in inherit_eps),
                                          "no_follow_up_game_end": sum(r["model"] == m and r["first_mgmt_turn"] is None and r["end_reason"] == "game_end" for r in inherit_eps)}
                                      for m in NAMES.values()}},
                     "player_games_without_non_inherited_group": {
                         m: sum(1 for g in games for pid, mm in per_game_models[g["game"]].items() if mm == m
                                and not any(r["game"] == g["game"] and r["player_id"] == pid and r["route"] != "creditor_inheritance" for r in episode_rows))
                         for m in NAMES.values()}},
        "crn_horizon": {"pairs": len(crn_rows),
                        "first_seat_divergence_min_max_median": _mmm([r["first_seat_divergence"] for r in crn_rows]),
                        "first_landing_divergence_min_max_median": _mmm([r["first_landing_divergence"] for r in crn_rows]),
                        "shared_prefix_draws_min_max": _mmm([r["shared_prefix_draws"] for r in crn_rows])},
        "attempts_by_model": {m: dict(c) for m, c in model_attempts.items()},
        "opus_attempt_chains": dict(opus_chain),
        "opus_refused_share_by_game": {g: round(c["refused_decisions"] / c["decisions"], 3) for g, c in sorted(opus_by_game.items())},
        "private_memory_slot_by_model": {m: dict(c) for m, c in memory_slot.items()},
        "fallback_final_action_messages": [{"model": m, "private_thought": pt, "public_message": pm, "n": n} for (m, pt, pm), n in fallback_notes.items()],
        "content_tool_mismatch_by_model": {m: dict(c) for m, c in mismatch.items()},
        "opus_4_8_attempts": dict(opus48),
        "semantic_review": "not performed; availability and accounting only",
    })
    # write outputs
    (OUT / "fable_results.json").write_text(json.dumps(results, indent=2, sort_keys=True, default=str) + "\n")
    (OUT / "fable_games.json").write_text(json.dumps(games, indent=2) + "\n")
    _write_jsonl(OUT / "fable_trade_settlement_checks.jsonl", settlement_rows)
    _write_jsonl(OUT / "fable_bankruptcy_blocks.jsonl", bankruptcy_rows)
    _write_jsonl(OUT / "fable_group_episodes_all_routes.jsonl", episode_rows)
    _write_jsonl(OUT / "fable_turn_access.jsonl", turn_rows)
    with (OUT / "fable_crn_horizon.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(crn_rows[0].keys()))
        w.writeheader()
        w.writerows(crn_rows)
    manifest = [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(sources))]
    (OUT / "fable_source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: results[k] for k in ("games", "events", "decisions", "first_builder_wins", "wins", "route_crosscheck",
                                                "trade_settlements", "bankruptcies", "jail_card_observation_checks",
                                                "turn_access_by_model", "crn_horizon", "attempts_by_model",
                                                "content_tool_mismatch_by_model", "private_memory_slot_by_model")},
                     indent=2, sort_keys=True, default=str))
    print("episodes:", json.dumps(results["episodes"], indent=2, sort_keys=True, default=str))


def _median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def _mmm(xs):
    vals = [x for x in xs if x is not None]
    return {"min": min(vals) if vals else None, "max": max(vals) if vals else None,
            "median": _median(vals), "none_count": sum(x is None for x in xs)}


def _write_jsonl(path, rows):
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=str) + "\n")


if __name__ == "__main__":
    main()
