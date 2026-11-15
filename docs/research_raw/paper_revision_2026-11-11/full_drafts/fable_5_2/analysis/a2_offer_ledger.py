"""Rebuild the offer ledger from canonical decision records.

One row per trade-response decision (an *offer* awaiting a response).  Terms
come from the responder's delivered ``current_offer``; cash, holdings and
mortgage flags come from the same delivered pre-decision state.  The rebuilt
ledger is then reconciled row by row with the retained
``paper_rewrite_2026-11-10/data/agenda_offers.json`` so that fresh arithmetic
and the inherited ledger can be told apart.
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

from corpus import REPO, board, complete_groups, load_all, sha256_file, write_json

RETAINED = REPO / "docs/research_raw/paper_rewrite_2026-11-10/data/agenda_offers.json"


def cell(author_new: list, recipient_new: list) -> str:
    if author_new and recipient_new:
        return "both"
    if author_new:
        return "author_only"
    if recipient_new:
        return "recipient_only"
    return "neither"


def build() -> list[dict]:
    B = board()
    rows = []
    for g in load_all().values():
        thread_no = 0
        thread_id = None
        for k in range(g.n_decisions):
            st, rs = g.started[k], g.resolved[k]
            if st["decision_type"] != "TRADE_RESPONSE_DECISION":
                continue
            sc = st["prompt_payload"]["action_state"]["scenario"]
            cur = sc["current_offer"]
            recipient = st["player_id"]
            author = cur["from_player_id"]
            assert author == sc["counterparty_player_id"]
            ex = sc["exchange_index"]
            if ex == 0:
                thread_no += 1
                thread_id = f"G{g.number:02d}-T{thread_no:03d}"
            give = cur["if_you_accept"]["you_give"]  # recipient -> author
            recv = cur["if_you_accept"]["you_receive"]  # author -> recipient
            state = g.state_before(k)["players"]
            a_own, r_own = state[author]["owned"], state[recipient]["owned"]
            a_keys, r_keys = set(a_own), set(r_own)
            assert set(recv["properties"]) <= a_keys and set(give["properties"]) <= r_keys, (g.number, k)
            a_after = (a_keys - set(recv["properties"])) | set(give["properties"])
            r_after = (r_keys - set(give["properties"])) | set(recv["properties"])
            a_new = sorted(complete_groups(a_after) - complete_groups(a_keys))
            r_new = sorted(complete_groups(r_after) - complete_groups(r_keys))
            a_lost = sorted(complete_groups(a_keys) - complete_groups(a_after))
            r_lost = sorted(complete_groups(r_keys) - complete_groups(r_after))
            # mortgage-transfer interest: receiver pays 10% of mortgage value (engine: ceil(m*0.1))
            def interest(keys, owned):
                tot = 0
                for key in keys:
                    if owned[key]["mortgaged"]:
                        m = B["by_key"][key]["mortgage"]
                        tot += -(-m // 10)
                return tot
            a_int = interest(give["properties"], r_own)  # author receives these
            r_int = interest(recv["properties"], a_own)
            net = recv["cash"] - give["cash"]  # author -> recipient
            rows.append(
                {
                    "game": g.number,
                    "block": g.block,
                    "decision": k,
                    "turn": st["turn_index"],
                    "thread_id": thread_id,
                    "exchange_index": ex,
                    "opening": ex == 0,
                    "author": author,
                    "recipient": recipient,
                    "author_model": g.model[author],
                    "recipient_model": g.model[recipient],
                    "response": rs["final_action"]["action"],
                    "accept_available": "accept_trade" in st["prompt_payload"]["action_state"]["available_actions"],
                    "author_gives": recv,
                    "recipient_gives": give,
                    "author_gives_mortgaged": sorted(x for x in recv["properties"] if a_own[x]["mortgaged"]),
                    "recipient_gives_mortgaged": sorted(x for x in give["properties"] if r_own[x]["mortgaged"]),
                    "author_new_groups": a_new,
                    "recipient_new_groups": r_new,
                    "author_lost_groups": a_lost,
                    "recipient_lost_groups": r_lost,
                    "completion_cell": cell(a_new, r_new),
                    "author_cash_before": state[author]["cash"],
                    "recipient_cash_before": state[recipient]["cash"],
                    "net_cash_author_to_recipient": net,
                    "author_interest_if_accepted": a_int,
                    "recipient_interest_if_accepted": r_int,
                    "author_holdings_before": sorted(a_keys),
                    "recipient_holdings_before": sorted(r_keys),
                    "response_condition": rs["sequence_meta"].get("response_condition"),
                    "fallback_used": rs["fallback_used"],
                    "author_is_winner": author == g.winner_pid,
                    "recipient_is_winner": recipient == g.winner_pid,
                    "public_message": rs["final_action"].get("public_message"),
                    "private_note": rs["final_action"].get("private_thought"),
                    "source_line": g.decision_line[k],
                }
            )
    return rows


def reconcile(rows: list[dict]) -> dict:
    old = json.loads(RETAINED.read_text())
    key = lambda r: (r["game"], r["decision"])
    old_by = {key(r): r for r in old}
    new_by = {key(r): r for r in rows}
    report = {
        "retained_sha256": sha256_file(RETAINED),
        "retained_rows": len(old),
        "rebuilt_rows": len(rows),
        "same_keys": set(old_by) == set(new_by),
        "field_mismatches": {},
    }
    pairs = [
        ("response", "response"),
        ("author", "author"),
        ("recipient", "recipient"),
        ("author_model", "author_model"),
        ("recipient_model", "recipient_model"),
        ("exchange_index", "exchange_index"),
        ("completion_cell", "completion_cell"),
        ("accept_available", "accept_available"),
        ("author_cash_before", "author_cash_before"),
        ("recipient_cash_before", "recipient_cash_before"),
        ("net_cash_author_to_recipient", "net_cash_author_to_recipient"),
        ("author_interest_if_accepted", "author_interest_if_accepted"),
        ("recipient_interest_if_accepted", "recipient_interest_if_accepted"),
        ("thread_id", "thread_id"),
        ("turn", "turn"),
    ]
    for new_f, old_f in pairs:
        bad = [k for k in new_by if k in old_by and new_by[k][new_f] != old_by[k][old_f]]
        report["field_mismatches"][new_f] = len(bad)
        if bad:
            report.setdefault("examples", {})[new_f] = [
                [list(k), new_by[k][new_f], old_by[k][old_f]] for k in bad[:5]
            ]
    # offer terms
    bad = 0
    for k, r in new_by.items():
        o = old_by[k]
        if r["author_gives"] != o["offer"] or r["recipient_gives"] != o["request"]:
            bad += 1
    report["field_mismatches"]["terms"] = bad
    return report


def main() -> None:
    rows = build()
    rep = reconcile(rows)
    legal = [r for r in rows if r["accept_available"]]
    c = collections.Counter((r["completion_cell"], r["response"]) for r in legal)
    rep["legal_offers"] = len(legal)
    rep["cells"] = {f"{a}|{b}": n for (a, b), n in sorted(c.items())}
    rep["threads"] = len({r["thread_id"] for r in rows})
    write_json("a2_offer_ledger.json", rows)
    write_json("a2_offer_ledger_reconciliation.json", rep)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
