"""Estate transfers and the debts that trigger them (fresh arithmetic on events and debt prompts)."""
from __future__ import annotations

import collections
import json

from corpus import OUT, board, load_all, write_json
from state_track import Tracker


def main() -> None:
    B = board()
    debt = json.loads((OUT / "a4_debt_episodes.json").read_text())
    games = load_all()
    out = {"eliminations": []}
    deeds_total = deeds_nonterminal = deeds_nonterminal_winner = 0
    cash_nonterminal = cash_nonterminal_winner = 0
    for n, g in games.items():
        el = sorted((d for d in debt if d["game"] == n and d["outcome"] == "eliminated"), key=lambda d: d["first_decision"])
        tr = Tracker(g)
        idx = 0
        i = 0
        events = g.events
        while i < len(events):
            e = events[i]
            ch = tr.apply(e)
            if ch and ch["kind"] == "bankruptcy":
                d = el[idx]
                terminal = idx == 2
                assert d["player"] == ch["debtor"]
                # estate cash: the BANKRUPTCY_CASH transfer just before
                cash = 0
                for back in events[max(0, i - 3):i]:
                    if back["type"] == "CASH_CHANGED" and back["payload"]["reason"] == "BANKRUPTCY_CASH" and back["payload"]["delta"] > 0:
                        cash = back["payload"]["delta"]
                j = i + 1
                nd = 0
                while j < len(events) and events[j]["type"] == "PROPERTY_PURCHASED" and events[j]["payload"].get("price") == 0:
                    nd += 1
                    j += 1
                # developed-rent debt: debtor stands on a square with buildings owned by the creditor
                st = g.started[d["first_decision"]]["prompt_payload"]["game_state"]
                pos = st["you"]["position"]
                developed = False
                if d["reason"] == "RENT" and pos in B["by_key"]:
                    for o in st["others"]:
                        for h in o["holdings"]["owned"]:
                            if h["space_key"] == pos and (h["hotel"] or h["houses"] > 0):
                                developed = True
                rec = {
                    "game": n, "order": idx + 1, "terminal": terminal, "debtor": g.model[d["player"]],
                    "creditor": g.model[d["creditor"]] if d["creditor"] else "bank",
                    "creditor_is_winner": d["creditor"] == g.winner_pid, "deeds": nd, "cash": cash,
                    "reason": d["reason"], "debt": d["debt"], "developed_rent_debt": developed, "square": pos,
                }
                out["eliminations"].append(rec)
                deeds_total += nd
                if not terminal:
                    deeds_nonterminal += nd
                    cash_nonterminal += cash
                    if rec["creditor_is_winner"]:
                        deeds_nonterminal_winner += nd
                        cash_nonterminal_winner += cash
                idx += 1
            i += 1
    E = out["eliminations"]
    non = [e for e in E if not e["terminal"]]
    out["summary"] = {
        "eliminations": len(E),
        "nonterminal": len(non),
        "creditor_is_winner_all": sum(e["creditor_is_winner"] for e in E),
        "creditor_is_winner_nonterminal": sum(e["creditor_is_winner"] for e in non),
        "estate_deeds_all": deeds_total,
        "estate_deeds_nonterminal": deeds_nonterminal,
        "estate_deeds_nonterminal_to_winner": deeds_nonterminal_winner,
        "estate_cash_nonterminal": cash_nonterminal,
        "estate_cash_nonterminal_to_winner": cash_nonterminal_winner,
        "developed_rent_debts_all": sum(e["developed_rent_debt"] for e in E),
        "developed_rent_debts_nonterminal": sum(e["developed_rent_debt"] for e in non),
        "terminal_to_winner": sum(e["creditor_is_winner"] for e in E if e["terminal"]),
        "terminal_to_bank": sum(e["creditor"] == "bank" for e in E if e["terminal"]),
        "first_elimination_by_debtor": dict(collections.Counter(e["debtor"] for e in E if e["order"] == 1)),
        "debt_reasons": dict(collections.Counter(e["reason"] for e in E)),
    }
    write_json("a8_estate_flows.json", out)
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
