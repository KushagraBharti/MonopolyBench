"""Rebuild the liquidation episodes and the negotiation responses from raw decisions.

Reads saved decisions.jsonl files only. Writes data/episodes.json and data/offers.json
in the reviewer's folder and compares both with the integrated paper's data files.
"""
import json, collections
from lib import *

OUT = HERE.parent / "data"


def episodes():
    out = []
    for g in range(1, 21):
        st, rs = load(g)
        cur = None
        eps = []
        for i in sorted(rs):
            r = rs[i]
            if r["decision_type"] != "LIQUIDATION_DECISION":
                continue
            sc = st[i]["prompt_payload"]["action_state"]["scenario"]
            sig = (r["player_id"], r["turn_index"], sc["owed_amount"], sc.get("owed_to_player_id"), sc.get("reason"))
            if cur is None or cur["sig"] != sig or cur["closed"]:
                cur = {"sig": sig, "game": g, "ds": [], "closed": False}
                eps.append(cur)
            cur["ds"].append(i)
            if (r.get("final_action") or {}).get("action") == "declare_bankruptcy":
                cur["closed"] = True
        for e in eps:
            i = e["ds"][0]
            pp = st[i]["prompt_payload"]
            sc = pp["action_state"]["scenario"]
            you = pp["game_state"]["you"]
            salvage = mstar = 0
            for h in you["holdings"]["owned"]:
                sp = SPACES[h["space_key"]]
                n = h.get("houses", 0) + (5 if h.get("hotel") else 0)
                if n:
                    salvage += n * HOUSE_COST[sp["group"]] // 2
                if not h.get("mortgaged"):
                    mstar += sp["price"] // 2
            listed = sc["options"].get("mortgageable_space_keys", [])
            m0 = sum(SPACES[k]["price"] // 2 for k in listed)
            acts = [(rs[j].get("final_action") or {}).get("action") for j in e["ds"]]
            used_new = sum(
                1 for j in e["ds"]
                if rs[j]["final_action"]["action"] == "mortgage_property"
                and rs[j]["final_action"]["args"]["space_key"] not in listed)
            e.update(first=i, model=who(rs[i]), turn=rs[i]["turn_index"], debt=sc["owed_amount"], cash=you["cash"],
                     salvage=salvage, m0=m0, mstar=mstar, u0=you["cash"] + salvage + m0, ustar=you["cash"] + salvage + mstar,
                     actions=acts, fallbacks=[bool(rs[j].get("fallback_used")) for j in e["ds"]],
                     menu=pp["action_state"]["available_actions"], mortgages_absent_from_first_menu=used_new)
            e["sig"] = list(e["sig"])
            del e["closed"]
            out.append(e)
    return out


def complete(hold):
    return {g for g, m in COLORS.items() if m <= hold}


def offers():
    out = []
    for g in range(1, 21):
        st, rs = load(g)
        for d in sorted(rs):
            r = rs[d]
            if r["decision_type"] != "TRADE_RESPONSE_DECISION":
                continue
            pp = st[d]["prompt_payload"]
            sc = pp["action_state"]["scenario"]
            co = sc["current_offer"]
            gs = pp["game_state"]
            you = gs["you"]
            author = co["from_player_id"]
            oth = {o["player_id"]: o for o in gs["others"]}
            yh = {h["space_key"] for h in you["holdings"]["owned"]}
            ah = {h["space_key"] for h in oth[author]["holdings"]["owned"]}
            yg, yr = co["if_you_accept"]["you_give"], co["if_you_accept"]["you_receive"]
            give, recv = set(yg["properties"]), set(yr["properties"])
            rn = complete((yh - give) | recv) - complete(yh)
            an = complete((ah - recv) | give) - complete(ah)
            cell = "both" if rn and an else "author_only" if an else "recipient_only" if rn else "neither"
            a, b = yr, yg  # the author offers what the recipient receives
            if a["properties"] and b["properties"]:
                form = "Swap"
            elif not a["get_out_of_jail_cards"] and not b["get_out_of_jail_cards"] and b["properties"] and not a["properties"] and a["cash"] > 0 and b["cash"] == 0:
                form = "Cash bid"
            elif not a["get_out_of_jail_cards"] and not b["get_out_of_jail_cards"] and a["properties"] and not b["properties"] and b["cash"] > 0 and a["cash"] == 0:
                form = "Cash ask"
            else:
                form = "Other"
            fa = r.get("final_action") or {}
            # the proposal that opened the thread, for the channel-conflict screen
            open_conflict = None
            if sc["exchange_index"] == 0:
                j = d - 1
                while j >= 0 and not (rs[j]["player_id"] == author and (rs[j].get("final_action") or {}).get("action") == "propose_trade"):
                    j -= 1
                n = named_action(rs[j])
                open_conflict = bool(n and n != "propose_trade" and not rs[j].get("fallback_used"))
            keeps_bundle = None
            if fa.get("action") == "counter_trade":
                ar = fa["args"]
                same = (sorted(ar["offer"]["properties"]) == sorted(yg["properties"])
                        and sorted(ar["request"]["properties"]) == sorted(yr["properties"])
                        and ar["offer"].get("get_out_of_jail_cards", 0) == yg.get("get_out_of_jail_cards", 0)
                        and ar["request"].get("get_out_of_jail_cards", 0) == yr.get("get_out_of_jail_cards", 0))
                keeps_bundle = bool(same and (ar["request"]["cash"] - ar["offer"]["cash"]) > (yr["cash"] - yg["cash"]))
            out.append(dict(game=g, decision=d, turn=r["turn_index"], exchange_index=sc["exchange_index"],
                            author_model=NAME[oth[author]["name"]], recipient_model=who(r), response=fa.get("action"),
                            accept_available="accept_trade" in pp["action_state"]["available_actions"], form=form,
                            completion_cell=cell, recipient_cash=you["cash"], recipient_gives_deeds=bool(give),
                            opening_call_conflicts=open_conflict, counter_keeps_bundle_and_improves_cash=keeps_bundle))
    return out


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    eps = episodes()
    offs = offers()
    (OUT / "episodes.json").write_text(json.dumps(eps, indent=1) + "\n")
    (OUT / "offers.json").write_text(json.dumps(offs, indent=1) + "\n")
    paper_eps = {(p["game"], p["first_decision"]): p for p in json.loads((INT / "data/liquidation_episodes.json").read_text())}
    mine = {(e["game"], e["first"]): e for e in eps}
    diffs = [k for k in paper_eps if k not in mine or paper_eps[k]["debt"] != mine[k]["debt"] or paper_eps[k]["cash"] != mine[k]["cash"]
             or paper_eps[k]["upper_bound"] != mine[k]["ustar"] or paper_eps[k]["actions"] != mine[k]["actions"]]
    print("episodes", len(eps), "paper", len(paper_eps), "field differences", len(diffs), "unmatched", len(set(mine) - set(paper_eps)))
    paper_off = {(p["game"], p["decision"]): p for p in json.loads((INT / "data/offers.json").read_text())}
    od = [o for o in offs if (o["game"], o["decision"]) not in paper_off or any(
        paper_off[(o["game"], o["decision"])][k] != o[k] for k in ("completion_cell", "response", "exchange_index", "accept_available", "author_model", "recipient_model"))]
    print("responses", len(offs), "paper", len(paper_off), "row differences", len(od), collections.Counter(o["response"] for o in offs))
