"""Rebuild all 920 trade-response opportunities from delivered prompts.

Source: each TRADE_RESPONSE_DECISION's delivered request (holdings, cash,
current offer) and its resolved applied action. Threads come from the
TRADE_* events. Completion = ownership of every deed of one of the eight
colour groups (mortgaged deeds count), newly obtained by the exchange.
The result is compared row by row with the retained 10 November ledger.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import corpus

OUT = Path(__file__).resolve().parents[1] / "data"
COLOR = ["BROWN", "LIGHT_BLUE", "PINK", "ORANGE", "RED", "YELLOW", "GREEN", "DARK_BLUE"]
RETAINED = corpus.REPO / "docs/research_raw/paper_rewrite_2026-11-10/integrated/data/agenda_offers.json"


def holdings(entry):
    owned = {h["space_key"]: h for h in entry["holdings"]["owned"]}
    return owned


def complete_groups(keys, groups):
    return {g for g in COLOR if all(k in keys for k in groups[g])}


def threads_from_events(events):
    """Map offer event seq -> (thread number, stage index, initiator)."""
    out = {}
    current = {}
    n = 0
    for e in events:
        t = e["type"]
        if t not in ("TRADE_PROPOSED", "TRADE_COUNTERED", "TRADE_ACCEPTED", "TRADE_REJECTED"):
            continue
        p = e["payload"]
        pair = (p["initiator_player_id"], p["counterparty_player_id"])
        if t == "TRADE_PROPOSED":
            n += 1
            current[pair] = n
        out[e["seq"]] = (current[pair], p["exchange_index"], p["initiator_player_id"], t)
    return out


def build():
    data = corpus.build_cache()
    spaces, groups, by_index = corpus.board()
    rows = []
    for g, game in data["games"].items():
        tmap = threads_from_events(game["events"])
        ev_by_seq = {e["seq"]: e for e in game["events"]}
        for idx, d in game["decisions"].items():
            if d["type"] != "TRADE_RESPONSE_DECISION":
                continue
            pay = d["payload"]
            sc = pay["action_state"]["scenario"]
            rec = d["player"]
            author = sc["current_offer"]["from_player_id"]
            give = sc["current_offer"]["if_you_accept"]["you_give"]
            recv = sc["current_offer"]["if_you_accept"]["you_receive"]
            gs = pay["game_state"]
            plist = {gs["you"]["player_id"]: gs["you"], **{o["player_id"]: o for o in gs["others"]}}
            r_own, a_own = holdings(plist[rec]), holdings(plist[author])
            r_keys, a_keys = set(r_own), set(a_own)
            r_after = (r_keys - set(give["properties"])) | set(recv["properties"])
            a_after = (a_keys - set(recv["properties"])) | set(give["properties"])
            r_before_c, a_before_c = complete_groups(r_keys, groups), complete_groups(a_keys, groups)
            r_new = sorted(complete_groups(r_after, groups) - r_before_c)
            a_new = sorted(complete_groups(a_after, groups) - a_before_c)
            r_lost = sorted(r_before_c - complete_groups(r_after, groups))
            a_lost = sorted(a_before_c - complete_groups(a_after, groups))
            # mortgage-transfer interest is paid by the receiver of a mortgaged deed
            def interest(keys, src):
                return sum(int(math.ceil(spaces[k]["mortgage"] * 0.1)) for k in keys if src.get(k, {}).get("mortgaged"))
            r_int = interest(recv["properties"], a_own)
            a_int = interest(give["properties"], r_own)
            r_cash, a_cash = plist[rec]["cash"], plist[author]["cash"]
            r_cash_after = r_cash - give["cash"] + recv["cash"] - r_int
            a_cash_after = a_cash - recv["cash"] + give["cash"] - a_int
            res = d["res"]
            action = (res["final_action"] or {}).get("action")
            # thread from the response event emitted by this decision
            resp_seq = None
            for s in range(res["seq_start"], res["seq_end"] + 1):
                e = ev_by_seq.get(s)
                if e and e["type"] in ("TRADE_COUNTERED", "TRADE_ACCEPTED", "TRADE_REJECTED"):
                    resp_seq = s
                    break
            thread, stage_from_event, initiator, rtype = tmap[resp_seq]
            stage = sc["exchange_index"]
            cell = ("Both" if a_new and r_new else "Author only" if a_new else "Recipient only" if r_new else "Neither")
            conds = [a["condition"] for a in res["attempts"]]
            selected = res["attempts"][-1] if res["attempts"] else {}
            rows.append({
                "game": g, "decision": idx, "turn": d["turn"], "thread": f"G{g:02d}-T{thread:03d}",
                "stage": stage, "opening": stage == 0, "initiator": initiator,
                "author": author, "recipient": rec,
                "author_model": game["pmodel"][author], "recipient_model": game["pmodel"][rec],
                "response": action, "accept_legal": "accept_trade" in pay["action_state"]["available_actions"],
                "author_gives": {"cash": give["cash"] if False else recv["cash"], "properties": recv["properties"], "jail": recv.get("get_out_of_jail_cards", 0)},
                "author_asks": {"cash": give["cash"], "properties": give["properties"], "jail": give.get("get_out_of_jail_cards", 0)},
                "author_new": a_new, "recipient_new": r_new, "author_lost": a_lost, "recipient_lost": r_lost,
                "cell": cell,
                "author_cash": a_cash, "recipient_cash": r_cash,
                "author_cash_after": a_cash_after, "recipient_cash_after": r_cash_after,
                "author_interest": a_int, "recipient_interest": r_int,
                "deeds_to_recipient_mortgaged": [k for k in recv["properties"] if a_own.get(k, {}).get("mortgaged")],
                "deeds_to_author_mortgaged": [k for k in give["properties"] if r_own.get(k, {}).get("mortgaged")],
                "response_conditions": conds, "selected_condition": selected.get("condition"),
                "fallback": res["fallback_used"],
                "private_note": (res["final_action"] or {}).get("private_thought"),
                "public_message": (res["final_action"] or {}).get("public_message"),
                "response_event_seq": resp_seq,
            })
    return rows


def compare_retained(rows):
    ret = json.loads(RETAINED.read_text())
    key = {(r["game"], r["decision"]): r for r in ret}
    mism = Counter()
    checked = 0
    for r in rows:
        o = key.get((r["game"], r["decision"]))
        if o is None:
            mism["missing"] += 1
            continue
        checked += 1
        if o["response"] != r["response"]:
            mism["response"] += 1
        if sorted(o["author_new_groups"]) != r["author_new"]:
            mism["author_new"] += 1
        if sorted(o["recipient_new_groups"]) != r["recipient_new"]:
            mism["recipient_new"] += 1
        if o["author"] != r["author"] or o["recipient"] != r["recipient"]:
            mism["parties"] += 1
        if o["exchange_index"] != r["stage"]:
            mism["stage"] += 1
        if o["recipient_cash_if_accepted"] != r["recipient_cash_after"]:
            mism["recipient_cash_after"] += 1
        if o["author_cash_if_accepted"] != r["author_cash_after"]:
            mism["author_cash_after"] += 1
        if o["thread_id"] != r["thread"]:
            mism["thread_label"] += 1
    return {"retained_rows": len(ret), "rebuilt_rows": len(rows), "joined": checked, "field_mismatches": dict(mism),
            "retained_sha256": corpus.sha256(RETAINED)}


if __name__ == "__main__":
    rows = build()
    OUT.mkdir(exist_ok=True)
    (OUT / "offers_rebuilt.json").write_text(json.dumps(rows, indent=1))
    rep = compare_retained(rows)
    c = Counter(r["response"] for r in rows)
    rep["responses"] = dict(c)
    rep["threads"] = len({r["thread"] for r in rows})
    rep["accept_legal"] = sum(r["accept_legal"] for r in rows)
    (OUT / "offers_rebuilt_check.json").write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))
