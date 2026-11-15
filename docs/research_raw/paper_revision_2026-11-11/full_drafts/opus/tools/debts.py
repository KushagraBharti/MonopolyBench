"""All debt episodes, including the ones that were paid.

A debt episode starts when the engine presents a LIQUIDATION_DECISION
(a mandatory payment exceeds cash) and continues over consecutive
liquidation decisions by the same player for the same creditor and amount.
Outcome: "paid" if no BANKRUPTCY cash event for that player follows before
the player's next non-liquidation decision; otherwise "eliminated".
Eliminations with no liquidation menu at all are added from BANKRUPTCY
events. The inherited 10 November classification (bound-negative,
payable witness, menu lock) is joined for eliminations only; it was
produced by the earlier engine-executed suite and is not re-derived here.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import corpus

OUT = Path(__file__).resolve().parents[1] / "data"
RETAINED = corpus.REPO / "docs/research_raw/paper_rewrite_2026-11-10/integrated/data/t06_eliminations.json"


def main():
    D = corpus.build_cache()
    spaces, groups, by_index = corpus.board()
    episodes = []
    for g, game in D["games"].items():
        evs = game["events"]
        bankrupt_seq = {}
        for e in evs:
            if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY":
                bankrupt_seq[e["payload"]["player_id"]] = e["seq"]
        decs = sorted(game["decisions"].items())
        i = 0
        while i < len(decs):
            idx, d = decs[i]
            if d["type"] != "LIQUIDATION_DECISION":
                i += 1
                continue
            sc = d["payload"]["action_state"]["scenario"]
            key = (d["player"], sc.get("owed_to_player_id"), sc["owed_amount"], d["turn"])
            members = [(idx, d)]
            j = i + 1
            while j < len(decs) and decs[j][1]["type"] == "LIQUIDATION_DECISION":
                s2 = decs[j][1]["payload"]["action_state"]["scenario"]
                k2 = (decs[j][1]["player"], s2.get("owed_to_player_id"), s2["owed_amount"], decs[j][1]["turn"])
                if k2 != key:
                    break
                members.append(decs[j])
                j += 1
            last_idx, last = members[-1]
            seq_end = last["res"]["seq_start"]
            # next decision boundary
            nxt_seq = decs[j][1]["res"]["seq_start"] if j < len(decs) else 10**9
            bseq = bankrupt_seq.get(d["player"])
            eliminated = bseq is not None and seq_end <= bseq < nxt_seq
            actions = [m[1]["res"]["final_action"]["action"] for m in members]
            you = d["payload"]["game_state"]["you"]
            first = members[0][1]["payload"]["action_state"]["scenario"]
            # resources at first menu
            own = you["holdings"]["owned"]
            mort_avail = sum(spaces[h["space_key"]]["mortgage"] for h in own if not h["mortgaged"])
            bldg_sale = sum(spaces[h["space_key"]]["house_cost"] * (h["houses"] + (5 if h["hotel"] else 0)) // 2 for h in own if spaces[h["space_key"]]["house_cost"])
            episodes.append({
                "game": g, "player": d["player"], "model": game["pmodel"][d["player"]],
                "turn": d["turn"], "first_decision": idx, "last_decision": last_idx, "n_decisions": len(members),
                "owed": first["owed_amount"], "reason": first.get("reason"), "creditor": first.get("owed_to_player_id"),
                "creditor_model": game["pmodel"].get(first.get("owed_to_player_id")) if first.get("owed_to_player_id") else "Bank",
                "cash": you["cash"], "shortfall": first.get("shortfall"),
                "nominal_bound": you["cash"] + mort_avail + bldg_sale,
                "actions": actions, "outcome": "eliminated" if eliminated else "paid",
                "declared": actions[-1] == "declare_bankruptcy",
                "fallback_any": any(m[1]["res"]["fallback_used"] for m in members),
                "creditor_is_winner": first.get("owed_to_player_id") == game["winner"],
            })
            i = j
        # eliminations without a liquidation menu
        covered = {(e["player"]) for e in episodes if e["game"] == g and e["outcome"] == "eliminated"}
        for pid, s in bankrupt_seq.items():
            if pid not in covered:
                episodes.append({"game": g, "player": pid, "model": game["pmodel"][pid], "outcome": "eliminated",
                                 "n_decisions": 0, "actions": [], "declared": False, "no_menu": True, "bankruptcy_seq": s})
    ret = json.loads(RETAINED.read_text())
    rk = {(r["game"], r["player"]): r for r in ret}
    for e in episodes:
        if e["outcome"] == "eliminated":
            r = rk.get((e["game"], e["player"]))
            e["retained_classification"] = None if r is None else ("menu_lock" if r["game"] == 7 and r["player"] == "p2" else ("payable" if r.get("avoidable") else "bound_negative"))
            e["retained_owed"] = r and r["owed"]
    paid = [e for e in episodes if e["outcome"] == "paid"]
    elim = [e for e in episodes if e["outcome"] == "eliminated"]
    summary = {
        "episodes": len(episodes), "paid": len(paid), "eliminated": len(elim),
        "eliminated_no_menu": sum(bool(e.get("no_menu")) for e in elim),
        "paid_by_model": Counter(e["model"] for e in paid), "elim_by_model": Counter(e["model"] for e in elim),
        "episodes_by_model": Counter(e["model"] for e in episodes),
        "paid_decisions": Counter(e["n_decisions"] for e in paid),
        "paid_actions": Counter(a for e in paid for a in e["actions"]),
        "paid_with_building_sale": sum(any(a == "sell_houses_or_hotel" for a in e["actions"]) for e in paid),
        "paid_with_fallback": sum(e["fallback_any"] for e in paid),
        "elim_fallback": sum(e.get("fallback_any", False) for e in elim),
        "retained_join": Counter(e.get("retained_classification") for e in elim),
        "paid_owed_median": sorted(e["owed"] for e in paid)[len(paid) // 2] if paid else None,
        "paid_reason": Counter(e["reason"] for e in paid), "elim_reason": Counter(e.get("reason") for e in elim),
        "paid_shortfall_median": sorted(e["shortfall"] for e in paid)[len(paid) // 2] if paid else None,
    }
    (OUT / "debt_episodes.json").write_text(json.dumps({"summary": summary, "episodes": episodes,
                                                        "retained_sha256": corpus.sha256(RETAINED)}, indent=1, default=dict))
    print(json.dumps(summary, indent=1, default=dict))


if __name__ == "__main__":
    main()
