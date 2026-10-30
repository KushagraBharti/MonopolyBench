"""Opus phase-1 independent economic reducer, version opus_phase1_v1.

Written from engine.py semantics and canonical events. It does not import or adapt
sol/economics.py or astra/*. Board data comes from contracts/data/board.json.

Scope: downstream, read-only. No engine simulation, no provider calls, no writes
outside this directory. Group completion is an ownership fact, not a value oracle.

Key semantics checked against python/packages/engine/src/monopoly_engine/engine.py:
- TRADE_ACCEPTED actor is the receiver of the current offer; the offerer is the other
  party (accept is only legal for the non-author, engine.py:2018). `offer` flows
  offerer->receiver and `request` receiver->offerer (engine.py:1890-1922).
- A mortgaged deed received in a trade costs its recipient ceil(10% of mortgage value)
  (engine.py:1778-1800, 1924-1941). Mortgage value is half the printed price.
- Bankruptcy to a creditor re-emits PROPERTY_PURCHASED price=0 on an owned deed and
  keeps houses, hotels and mortgages (engine.py:2997-3009). Bankruptcy to the bank
  emits no per-deed event: the deeds return unowned, unmortgaged and undeveloped and
  the marker is CASH_CHANGED reason=BANKRUPTCY_ASSETS_TO_BANK (engine.py:3010-3027).
- A management menu (POST_TURN_ACTION_DECISION) exists only on the player's own turn
  and never while in jail (engine.py:1485-1497). A trade on the owner's own post-turn
  resumes that menu at once (engine.py:2103-2115).
- Buildability requires the full group, no mortgaged deed in the group, cash at least
  one house cost, bank stock, and even building (engine.py:2519-2550).
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COLLECTIONS = [
    ROOT / "saved_games/railway-research-12-games-2026-10-25",
    ROOT / "saved_games/railway-research-8-games-2026-10-26",
]
MODEL_LABEL = {
    "anthropic/claude-opus-5.5": "Opus",
    "openai/gpt-6.1-sol": "Sol",
    "google/gemini-4-argon": "Gemini",
    "x-ai/grok-4.7": "Grok",
}
MANAGEMENT = "POST_TURN_ACTION_DECISION"
SETTLEMENT_CASH = {"TRADE_CASH", "MORTGAGE_INTEREST"}
HOUSE_LIMIT = 4


def space_key(name: str) -> str:
    out, prev_sep = [], False
    for ch in name.strip():
        if ch.isalnum():
            out.append(ch.upper())
            prev_sep = False
        elif not prev_sep:
            out.append("_")
            prev_sep = True
    return "".join(out).strip("_")


def load_board(path: Path | None = None) -> dict[str, Any]:
    spec = json.loads((path or ROOT / "contracts/data/board.json").read_text())
    spaces = spec["spaces"]
    ownable = {s["index"]: s for s in spaces if s.get("price") is not None}
    groups: dict[str, list[int]] = defaultdict(list)
    for s in spaces:
        if s["kind"] == "PROPERTY":
            groups[s["group"]].append(s["index"])
    return {
        "ownable": ownable,
        "groups": {g: sorted(v) for g, v in groups.items()},
        "group_of": {i: s["group"] for i, s in ownable.items() if s["kind"] == "PROPERTY"},
        "key": {s["index"]: space_key(s["name"]) for s in spaces},
        "index_of_key": {space_key(s["name"]): s["index"] for s in spaces},
        "house_cost": spec["house_cost_by_group"],
    }


class Ledger:
    """Economic state folded from events only."""

    def __init__(self, board: dict[str, Any], players: list[str], initial: dict[str, Any] | None = None):
        self.board = board
        self.owner = {i: None for i in board["ownable"]}
        self.mortgaged = {i: False for i in board["ownable"]}
        self.houses = {i: 0 for i in board["ownable"]}
        self.hotel = {i: False for i in board["ownable"]}
        self.cash = {p: 1500 for p in players}
        self.bankrupt = {p: False for p in players}
        self.bank_houses, self.bank_hotels = 32, 12
        if initial is not None:
            self.load_snapshot(initial)

    def load_snapshot(self, snap: dict[str, Any]) -> None:
        for s in snap["board"]:
            if s["index"] in self.owner:
                self.owner[s["index"]] = s["owner_id"]
                self.mortgaged[s["index"]] = s["mortgaged"]
                self.houses[s["index"]] = s["houses"]
                self.hotel[s["index"]] = s["hotel"]
        for p in snap["players"]:
            self.cash[p["player_id"]] = p["cash"]
            self.bankrupt[p["player_id"]] = p["bankrupt"]
        self.bank_houses = snap["bank"]["houses_remaining"]
        self.bank_hotels = snap["bank"]["hotels_remaining"]

    def projection(self) -> tuple:
        return (
            tuple((i, self.owner[i], self.mortgaged[i], self.houses[i], self.hotel[i]) for i in sorted(self.owner)),
            tuple(sorted((p, self.cash[p], self.bankrupt[p]) for p in self.cash)),
            (self.bank_houses, self.bank_hotels),
        )

    @staticmethod
    def project_snapshot(snap: dict[str, Any], ownable: set[int]) -> tuple:
        return (
            tuple((s["index"], s["owner_id"], s["mortgaged"], s["houses"], s["hotel"])
                  for s in sorted(snap["board"], key=lambda s: s["index"]) if s["index"] in ownable),
            tuple(sorted((p["player_id"], p["cash"], p["bankrupt"]) for p in snap["players"])),
            (snap["bank"]["houses_remaining"], snap["bank"]["hotels_remaining"]),
        )

    def full_groups(self) -> set[tuple[str, str]]:
        out = set()
        for g, idx in self.board["groups"].items():
            o = self.owner[idx[0]]
            if o is not None and all(self.owner[i] == o for i in idx):
                out.add((o, g))
        return out

    def build_block_reasons(self, player: str, group: str) -> list[str]:
        """Why the engine would not list this group as buildable, from folded state."""
        idx = self.board["groups"][group]
        reasons = []
        if not all(self.owner[i] == player for i in idx):
            reasons.append("not_full_group")
        if any(self.mortgaged[i] for i in idx):
            reasons.append("mortgaged_constituent")
        if self.cash[player] < self.board["house_cost"][group]:
            reasons.append("cash_below_house_cost")
        if all(self.hotel[i] for i in idx):
            reasons.append("fully_developed")
        if self.bank_houses <= 0 and not any(self.houses[i] == HOUSE_LIMIT for i in idx):
            reasons.append("bank_houses_exhausted")
        return reasons


def interest(board: dict[str, Any], mortgaged: bool, index: int) -> int:
    return math.ceil((board["ownable"][index]["price"] // 2) * 0.1) if mortgaged else 0


def reduce_events(events: list[dict[str, Any]], board: dict[str, Any], players: list[str],
                  initial: dict[str, Any] | None = None, keep_projections: bool = False) -> dict[str, Any]:
    """Fold events into deed acquisitions, settlements and group episodes."""
    if [e["seq"] for e in events] != list(range(events[0]["seq"], events[0]["seq"] + len(events))):
        raise ValueError("non-contiguous event sequence")
    L = Ledger(board, players, initial)
    held_route: dict[int, str] = {}       # how the current owner obtained the deed
    acquisitions, trades, episodes = [], [], []
    active: dict[tuple[str, str], dict[str, Any]] = {}
    in_auction = False
    turn_owner: dict[int, str] = {}
    pending_turn = None
    settlement = None
    projections = [] if keep_projections else None
    issues: list[str] = []

    def acquire(e, idx, frm, to, route, price):
        L.owner[idx] = to
        held_route[idx] = route
        acquisitions.append({"seq": e["seq"], "turn": e["turn_index"], "space_index": idx,
                             "space_key": board["key"][idx], "from": frm, "to": to,
                             "route": route, "price": price,
                             "mortgaged_on_receipt": L.mortgaged[idx],
                             "buildings_on_receipt": L.houses[idx] + 5 * L.hotel[idx]})

    def close_settlement(next_seq):
        nonlocal settlement
        s = settlement
        settlement = None
        exp, got = s["expected"], s["observed"]
        parties = s["record"]["parties"]
        ok = (Counter(exp["transfers"]) == Counter(got["transfers"]) and
              all(exp["trade_cash"][q] == got["trade_cash"].get(q, 0) for q in parties) and
              all(exp["interest"][q] == got["interest"].get(q, 0) for q in parties))
        if not ok:
            issues.append(f"settlement_mismatch seq={s['seq']}")
        rec = s["record"]
        rec.update(settlement_matches_payload=ok, settlement_end_seq=next_seq - 1,
                   interest_paid={q: exp["interest"][q] for q in parties},
                   cash_after={q: L.cash[q] for q in parties},
                   groups_after=sorted([list(x) for x in L.full_groups() if x[0] in parties]))
        trades.append(rec)
        sync_groups(s["marker"], "trade")

    def sync_groups(marker, cause):
        now = L.full_groups()
        for key in sorted(set(active) - now):
            ep = active.pop(key)
            ep["end_seq"] = marker["seq"]
            ep["end_turn"] = marker["turn_index"]
            ep["end_reason"] = cause_of_loss(marker)
        for (p, g) in sorted(now - set(active)):
            idx = board["groups"][g]
            ep = {"player_id": p, "group": g, "start_seq": marker["seq"], "start_turn": marker["turn_index"],
                  "completion_route": cause,
                  "constituent_routes": {board["key"][i]: held_route.get(i, "initial_state") for i in idx},
                  "buildings_at_start": sum(L.houses[i] + 5 * L.hotel[i] for i in idx),
                  "mortgaged_at_start": sum(L.mortgaged[i] for i in idx),
                  "cash_at_start": L.cash[p],
                  "start_on_owner_turn": turn_owner.get(marker["turn_index"]) == p}
            ep["provenance_mix"] = "+".join(sorted(set(ep["constituent_routes"].values())))
            episodes.append(ep)
            active[(p, g)] = ep

    def cause_of_loss(marker):
        t = marker["type"]
        if t == "TRADE_ACCEPTED":
            return "traded_away"
        if t == "PROPERTY_PURCHASED":
            return "bankrupt_to_player"
        if t == "CASH_CHANGED" and marker["payload"].get("reason") == "BANKRUPTCY_ASSETS_TO_BANK":
            return "bankrupt_to_bank"
        return "other:" + t

    if initial is not None:  # groups already complete in a supplied starting state
        for (p0, g) in sorted(L.full_groups()):
            idx = board["groups"][g]
            ep = {"player_id": p0, "group": g, "start_seq": events[0]["seq"] - 1,
                  "start_turn": initial.get("turn_index", 0), "completion_route": "initial_state",
                  "constituent_routes": {board["key"][i]: "initial_state" for i in idx},
                  "provenance_mix": "initial_state",
                  "buildings_at_start": sum(L.houses[i] + 5 * L.hotel[i] for i in idx),
                  "mortgaged_at_start": sum(L.mortgaged[i] for i in idx), "cash_at_start": L.cash[p0],
                  "start_on_owner_turn": None}
            episodes.append(ep)
            active[(p0, g)] = ep
    for e in events:
        t, p = e["type"], e["payload"]
        if settlement is not None and not (
                t == "PROPERTY_TRANSFERRED" or (t == "CASH_CHANGED" and p.get("reason") in SETTLEMENT_CASH)):
            close_settlement(e["seq"])
        if t == "TURN_STARTED":
            pending_turn = e["turn_index"]
        elif pending_turn is not None:
            pid = (e.get("actor") or {}).get("player_id") or (p.get("player_id") if t == "LLM_DECISION_REQUESTED" else None)
            if pid:
                turn_owner[pending_turn] = pid
                pending_turn = None

        if t == "AUCTION_STARTED":
            in_auction = True
        elif t == "AUCTION_ENDED":
            in_auction = False
        elif t == "PROPERTY_PURCHASED":
            idx, buyer, price = p["space_index"], p["player_id"], p["price"]
            prev = L.owner[idx]
            if prev is None:
                if price <= 0:
                    raise ValueError(f"zero-price purchase of unowned deed at seq {e['seq']}")
                acquire(e, idx, None, buyer, "auction" if in_auction else "direct_purchase", price)
            else:
                if price != 0 or not L.bankrupt.get(prev):
                    raise ValueError(f"owned-deed purchase outside creditor bankruptcy at seq {e['seq']}")
                acquire(e, idx, prev, buyer, "creditor_inheritance", 0)
            sync_groups(e, acquisitions[-1]["route"])
        elif t == "TRADE_ACCEPTED":
            parties = [p["initiator_player_id"], p["counterparty_player_id"]]
            receiver = e["actor"]["player_id"]
            if receiver not in parties:
                raise ValueError("acceptor is not a party")
            offerer = parties[1] if receiver == parties[0] else parties[0]
            off, req = p["offer"], p["request"]
            o_idx = [board["index_of_key"][k] for k in off["properties"]]
            r_idx = [board["index_of_key"][k] for k in req["properties"]]
            expected = {
                "transfers": [(i, offerer, receiver) for i in o_idx] + [(i, receiver, offerer) for i in r_idx],
                "trade_cash": {offerer: req["cash"] - off["cash"], receiver: off["cash"] - req["cash"]},
                "interest": {offerer: sum(interest(board, L.mortgaged[i], i) for i in r_idx),
                             receiver: sum(interest(board, L.mortgaged[i], i) for i in o_idx)},
            }
            settlement = {
                "seq": e["seq"], "marker": e, "expected": expected,
                "observed": {"transfers": [], "trade_cash": Counter(), "interest": Counter()},
                "record": {"seq": e["seq"], "turn": e["turn_index"], "thread_initiator": parties[0],
                           "thread_counterparty": parties[1], "final_offer_author": offerer,
                           "accepting_player": receiver, "exchange_index": p["exchange_index"],
                           "parties": parties, "cash_before": {q: L.cash[q] for q in parties},
                           "offer": off, "request": req,
                           "mortgaged_deeds_moved": [board["key"][i] for i in o_idx + r_idx if L.mortgaged[i]],
                           "groups_before": sorted([list(x) for x in L.full_groups() if x[0] in parties])},
            }
        elif t == "PROPERTY_TRANSFERRED":
            if settlement is None:
                raise ValueError(f"transfer outside trade settlement at seq {e['seq']}")
            idx = p["space_index"]
            if L.owner[idx] != p["from_player_id"]:
                raise ValueError(f"transfer from non-owner at seq {e['seq']}")
            settlement["observed"]["transfers"].append((idx, p["from_player_id"], p["to_player_id"]))
            if p["mortgaged"] != L.mortgaged[idx]:
                issues.append(f"transfer_mortgage_flag seq={e['seq']}")
            acquire(e, idx, p["from_player_id"], p["to_player_id"], "trade", None)
        elif t == "CASH_CHANGED":
            who, delta, reason = p["player_id"], p["delta"], p["reason"]
            L.cash[who] += delta
            if settlement is not None and reason == "TRADE_CASH":
                settlement["observed"]["trade_cash"][who] += delta
            elif settlement is not None and reason == "MORTGAGE_INTEREST":
                settlement["observed"]["interest"][who] += -delta
            if reason == "BANKRUPTCY":
                L.bankrupt[who] = True
            elif reason == "BANKRUPTCY_ASSETS_TO_BANK":
                for i in L.owner:
                    if L.owner[i] == who:
                        L.bank_houses += L.houses[i]
                        L.bank_hotels += int(L.hotel[i])
                        L.owner[i], L.mortgaged[i], L.houses[i], L.hotel[i] = None, False, 0, False
                        held_route.pop(i, None)
                        acquisitions.append({"seq": e["seq"], "turn": e["turn_index"], "space_index": i,
                                             "space_key": board["key"][i], "from": who, "to": None,
                                             "route": "returned_to_bank", "price": None,
                                             "mortgaged_on_receipt": False, "buildings_on_receipt": 0})
                sync_groups(e, "bank_return")
        elif t == "PROPERTY_MORTGAGED":
            L.mortgaged[p["space_index"]] = True
        elif t == "PROPERTY_UNMORTGAGED":
            L.mortgaged[p["space_index"]] = False
        elif t == "HOUSE_BUILT":
            L.houses[p["space_index"]] += p["count"]
            L.bank_houses -= p["count"]
        elif t == "HOTEL_BUILT":
            L.houses[p["space_index"]] = 0
            L.hotel[p["space_index"]] = True
            L.bank_houses += HOUSE_LIMIT
            L.bank_hotels -= 1
        elif t == "HOUSE_SOLD":
            L.houses[p["space_index"]] -= p["count"]
            L.bank_houses += p["count"]
        elif t == "HOTEL_SOLD":
            L.hotel[p["space_index"]] = False
            L.houses[p["space_index"]] = HOUSE_LIMIT
            L.bank_houses -= HOUSE_LIMIT
            L.bank_hotels += 1
        if projections is not None and settlement is None:
            projections.append((e["seq"], L.projection()))
    if settlement is not None:
        close_settlement(events[-1]["seq"] + 1)
        if projections is not None:
            projections.append((events[-1]["seq"], L.projection()))
    terminal = any(e["type"] == "GAME_ENDED" for e in events)
    for ep in active.values():
        ep.update(end_seq=None, end_turn=None, end_reason="game_end" if terminal else "record_end")
    return {"ledger": L, "acquisitions": acquisitions, "trades": trades, "episodes": episodes,
            "turn_owner": turn_owner, "issues": issues, "projections": projections}


def menu_from_started(row: dict[str, Any]) -> dict[str, Any] | None:
    payload = row.get("prompt_payload")
    if not isinstance(payload, dict):
        return None
    st = payload.get("action_state") or {}
    opts = (st.get("scenario") or {}).get("options") or {}
    return {"available_actions": st.get("available_actions"),
            "buildable_space_keys": opts.get("buildable_space_keys"),
            "decision_type": st.get("decision_type")}


def measure_access(ep: dict[str, Any], events: list[dict[str, Any]], board: dict[str, Any],
                   menus: dict[str, dict[str, Any] | None], resolved: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Access, entry legality and deployment for one group episode.

    Own-turn counting: an owner turn is a TURN_STARTED whose first acting player is the
    owner. Doubles create extra turns with new turn indexes, so global turn delay is
    reported separately from own-turn delay.
    """
    pid, group = ep["player_id"], ep["group"]
    keys = {board["key"][i] for i in board["groups"][group]}
    idxs = set(board["groups"][group])
    lo = ep["start_seq"]
    hi = ep["end_seq"] if ep["end_seq"] is not None else events[-1]["seq"] + 1
    seg = [e for e in events if lo < e["seq"] < hi]
    first = None
    own_turns_before: list[dict[str, Any]] = []
    cur_turn, cur_is_owner, cur_info = None, False, None
    for e in seg:
        t, p = e["type"], e["payload"]
        if t == "TURN_STARTED":
            cur_turn, cur_is_owner, cur_info = e["turn_index"], None, None
            continue
        if cur_is_owner is None:
            actor = (e.get("actor") or {}).get("player_id") or (p.get("player_id") if t == "LLM_DECISION_REQUESTED" else None)
            if actor:
                cur_is_owner = actor == pid
                if cur_is_owner:
                    cur_info = {"turn": cur_turn, "jail_actions": [], "sent_to_jail": False}
                    own_turns_before.append(cur_info)
        if t == "LLM_DECISION_REQUESTED" and p.get("player_id") == pid:
            if p["decision_type"] == MANAGEMENT:
                first = e
                break
            if p["decision_type"] == "JAIL_DECISION" and cur_info is not None:
                m = menus.get(p["decision_id"]) or {}
                r = resolved.get(p["decision_id"]) or {}
                cur_info["jail_actions"].append({
                    "decision_id": p["decision_id"],
                    "chosen": ((r.get("final_action") or {}).get("action")),
                    "pay_fine_legal": "pay_jail_fine" in (m.get("available_actions") or []),
                    "card_legal": "use_get_out_of_jail_card" in (m.get("available_actions") or [])})
        if t == "SENT_TO_JAIL" and p.get("player_id") == pid and cur_info is not None:
            cur_info["sent_to_jail"] = True
    same_turn = first is not None and first["turn_index"] == ep["start_turn"]
    access_turn_info = (own_turns_before[-1] if first is not None and own_turns_before
                        and own_turns_before[-1]["turn"] == first["turn_index"] else None)
    prior_turns = own_turns_before[:-1] if access_turn_info is not None else own_turns_before
    out = {
        "same_turn_access": same_turn,
        "own_turns_without_access": len(prior_turns),
        "no_access_turn_reasons": ["sent_to_jail" if x["sent_to_jail"] else
                                   "jail_stay" if x["jail_actions"] else "other" for x in prior_turns],
        "jail_decisions_before_access": [j for x in own_turns_before for j in x["jail_actions"]],
    }
    if first is None:
        out.update(access="censored_" + ("loss" if ep["end_seq"] is not None else ep["end_reason"]),
                   first_mgmt_turn=None, global_turn_delay=None)
        builds_any = [e for e in seg if e["type"] in ("HOUSE_BUILT", "HOTEL_BUILT")
                      and e["payload"]["player_id"] == pid and e["payload"]["space_index"] in idxs]
        out["built_in_episode"] = bool(builds_any)
        return out
    did = first["payload"]["decision_id"]
    menu = menus.get(did)
    turn = first["turn_index"]
    turn_end = next((e["seq"] for e in seg if e["seq"] > first["seq"] and e["type"] == "TURN_ENDED"
                     and e["turn_index"] == turn), hi)
    in_turn = [e for e in seg if first["seq"] <= e["seq"] < turn_end]
    mgmt_reqs = [e for e in in_turn if e["type"] == "LLM_DECISION_REQUESTED" and e["payload"].get("player_id") == pid
                 and e["payload"]["decision_type"] == MANAGEMENT]

    def legal(req):
        m = menus.get(req["payload"]["decision_id"])
        if m is None or m.get("available_actions") is None:
            return None
        return "build_houses_or_hotel" in m["available_actions"] and bool(keys & set(m.get("buildable_space_keys") or []))

    entry = legal(first)
    later = [legal(r) for r in mgmt_reqs]
    built_turn = any(e["type"] in ("HOUSE_BUILT", "HOTEL_BUILT") and e["payload"]["player_id"] == pid
                     and e["payload"]["space_index"] in idxs for e in in_turn)
    builds = [e for e in seg if e["type"] in ("HOUSE_BUILT", "HOTEL_BUILT")
              and e["payload"]["player_id"] == pid and e["payload"]["space_index"] in idxs]
    window_complete = turn_end < hi or ep["end_reason"] != "record_end"
    # Management turns of the owner in the episode, up to and including the first build.
    by_turn: dict[int, dict[str, Any]] = {}
    first_build_seq = builds[0]["seq"] if builds else hi
    for e in seg:
        if e["seq"] > first_build_seq:
            break
        if (e["type"] == "LLM_DECISION_REQUESTED" and e["payload"].get("player_id") == pid
                and e["payload"]["decision_type"] == MANAGEMENT):
            slot = by_turn.setdefault(e["turn_index"], {"legal": False, "missing_menu": False})
            lg = legal(e)
            slot["missing_menu"] |= lg is None
            slot["legal"] |= bool(lg)
    turns_seq = sorted(by_turn)
    build_turn = builds[0]["turn_index"] if builds else None
    skipped = [t for t in turns_seq if by_turn[t]["legal"] and t != build_turn]
    out.update(
        access="observed", first_mgmt_turn=turn, first_mgmt_decision=did,
        global_turn_delay=turn - ep["start_turn"], menu_missing=menu is None,
        entry_buildable=entry,
        buildable_any_menu_first_turn=None if None in later else any(later),
        mgmt_decisions_in_first_turn=len(mgmt_reqs),
        built_in_first_mgmt_turn=built_turn,
        first_mgmt_window_complete=window_complete,
        built_in_episode=bool(builds),
        first_build_turn=build_turn,
        mgmt_turns_before_first_build=len([t for t in turns_seq if t != build_turn]),
        legal_turns_skipped_before_first_build=len(skipped),
        missing_menus_before_first_build=sum(by_turn[t]["missing_menu"] for t in turns_seq),
    )
    return out


def game_dirs() -> list[tuple[int, Path, dict[str, str]]]:
    out = []
    for coll in COLLECTIONS:
        with open(coll / "game-index.csv") as fh:
            for row in csv.DictReader(fh):
                out.append((int(row["collection_game"]), coll / row["package"] / "run", row))
    out.sort(key=lambda x: x[0])
    return out


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
