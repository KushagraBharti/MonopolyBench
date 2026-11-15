"""Rebuild every negotiation response from raw decisions.jsonl and tabulate it.

Read-only. Classifies each offer by stage, form and which player's color group the
proposed transfer would newly complete. Enumerates all 5^5 ordered resamples of the five
seed blocks (the percentile block bootstrap, fully enumerated) for the opening contrasts.
Writes data/offers.json and data/bargaining_summary.json.
"""
import collections
import itertools

from lib import *

C = collections.Counter


def complete(hold):
    return {g for g, m in COLORS.items() if m <= hold}


def offers():
    out = []
    for g in range(1, 21):
        st, rs, lines = load(g)
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
            cell = "both" if rn and an else "proposer_only" if an else "recipient_only" if rn else "neither"
            a, b = yr, yg  # the author offers what the recipient receives
            jail = a["get_out_of_jail_cards"] or b["get_out_of_jail_cards"]
            if a["properties"] and b["properties"]:
                form = "Swap"
            elif not jail and b["properties"] and not a["properties"] and a["cash"] > 0 and b["cash"] == 0:
                form = "Cash bid"
            elif not jail and a["properties"] and not b["properties"] and b["cash"] > 0 and a["cash"] == 0:
                form = "Cash ask"
            else:
                form = "Other"
            fa = r["final_action"]
            open_conflict = None
            if sc["exchange_index"] == 0:
                j = d - 1
                while j >= 0 and not (rs[j]["player_id"] == author and rs[j]["final_action"]["action"] == "propose_trade"):
                    j -= 1
                n = named_action(rs[j]["attempts"][-1].get("assistant_content"))
                open_conflict = bool(n and n != "propose_trade" and not rs[j].get("fallback_used"))
            keeps = None
            if fa["action"] == "counter_trade":
                ar = fa["args"]
                same = (sorted(ar["offer"]["properties"]) == sorted(yg["properties"])
                        and sorted(ar["request"]["properties"]) == sorted(yr["properties"])
                        and ar["offer"].get("get_out_of_jail_cards", 0) == yg.get("get_out_of_jail_cards", 0)
                        and ar["request"].get("get_out_of_jail_cards", 0) == yr.get("get_out_of_jail_cards", 0))
                keeps = bool(same and (ar["request"]["cash"] - ar["offer"]["cash"]) > (yr["cash"] - yg["cash"]))
            n_resp = named_action(r["attempts"][-1].get("assistant_content"))
            out.append(dict(
                game=g, block=(g - 1) // 4 + 1, decision=d, turn=r["turn_index"], exchange_index=sc["exchange_index"],
                author_model=NAME[oth[author]["name"]], recipient_model=who(r), response=fa["action"],
                accept_available="accept_trade" in pp["action_state"]["available_actions"], form=form, completion=cell,
                recipient_cash=you["cash"], opening_call_conflicts=open_conflict,
                response_names_other_action=bool(n_resp and n_resp != fa["action"] and not r.get("fallback_used")),
                counter_keeps_bundle_and_improves_cash=keeps,
                response_condition=r["attempts"][-1].get("response_condition"),
                source_line=lines[d]))
    return out


def rej(rows):
    return sum(o["response"] == "reject_trade" for o in rows), len(rows)


def cellrows(rows, form, comp):
    return [o for o in rows if o["form"] == form and o["completion"] == comp]


def gap(rows, form):
    a, b = rej(cellrows(rows, form, "proposer_only"))
    c, d = rej(cellrows(rows, form, "neither"))
    return dict(own=[a, b], neither=[c, d], gap=None if not b or not d else round(100 * (a / b - c / d), 2))


def block_enumeration(rows, form):
    """Percentile bootstrap over the five seed blocks, all 3,125 ordered resamples."""
    per = {}
    for blk in range(1, 6):
        r = [o for o in rows if o["block"] == blk]
        per[blk] = (rej(cellrows(r, form, "proposer_only")), rej(cellrows(r, form, "neither")))
    vals = []
    for draw in itertools.product(range(1, 6), repeat=5):
        a = sum(per[b][0][0] for b in draw); n1 = sum(per[b][0][1] for b in draw)
        c = sum(per[b][1][0] for b in draw); n2 = sum(per[b][1][1] for b in draw)
        if n1 and n2:
            vals.append(100 * (a / n1 - c / n2))
    vals.sort()
    lo = vals[int(0.025 * (len(vals) - 1))]
    hi = vals[int(round(0.975 * (len(vals) - 1)))]
    loo = []
    for drop in range(1, 6):
        r = [o for o in rows if o["block"] != drop]
        loo.append(gap(r, form)["gap"])
    blocks = {b: dict(own=list(per[b][0]), neither=list(per[b][1]),
                      gap=None if not per[b][0][1] or not per[b][1][1] else round(100 * (per[b][0][0] / per[b][0][1] - per[b][1][0] / per[b][1][1]), 1))
              for b in per}
    return dict(draws=len(vals), percentile_2_5=round(lo, 1), percentile_97_5=round(hi, 1),
                leave_one_block_out=[round(min(loo), 1), round(max(loo), 1)], blocks=blocks)


if __name__ == "__main__":
    offs = offers()
    write_json("offers.json", offs)
    S = {}
    S["responses"] = len(offs)
    S["threads_openings"] = sum(1 for o in offs if o["exchange_index"] == 0)
    S["response_counts"] = dict(C(o["response"] for o in offs))
    S["accept_legal"] = sum(o["accept_available"] for o in offs)
    S["accept_illegal_responses"] = dict(C(o["response"] for o in offs if not o["accept_available"]))
    S["by_recipient"] = {m: dict(C(o["response"] for o in offs if o["recipient_model"] == m), n=sum(1 for o in offs if o["recipient_model"] == m))
                         for m in ("Sol", "Gemini", "Opus", "Grok")}
    S["grok_acceptances_naming_other_action"] = [sum(1 for o in offs if o["recipient_model"] == "Grok" and o["response"] == "accept_trade" and o["response_names_other_action"]),
                                                 sum(1 for o in offs if o["recipient_model"] == "Grok" and o["response"] == "accept_trade")]
    legal = [o for o in offs if o["accept_available"]]
    table = {}
    for stage, sel in (("Opening", lambda o: o["exchange_index"] == 0), ("Later", lambda o: o["exchange_index"] > 0)):
        for form in ("Swap", "Cash bid", "Cash ask", "Other"):
            for comp in ("proposer_only", "recipient_only", "both", "neither"):
                r = [o for o in legal if sel(o) and o["form"] == form and o["completion"] == comp]
                c = C(o["response"] for o in r)
                table[f"{stage}|{form}|{comp}"] = [len(r), c["accept_trade"], c["counter_trade"], c["reject_trade"]]
    S["table"] = table
    op = [o for o in legal if o["exchange_index"] == 0]
    later = [o for o in legal if o["exchange_index"] > 0]
    pops = {
        "all_swaps": (op, "Swap"),
        "no_grok_authors": ([o for o in op if o["author_model"] != "Grok"], "Swap"),
        "no_conflicting_openings": ([o for o in op if not o["opening_call_conflicts"]], "Swap"),
        "cash_bids": (op, "Cash bid"),
    }
    S["contrasts"] = {k: dict(gap(r, f), **block_enumeration(r, f)) for k, (r, f) in pops.items()}
    S["later_swaps"] = gap(later, "Swap")
    S["by_proposer_swaps"] = {m: gap([o for o in op if o["author_model"] == m], "Swap") for m in ("Sol", "Gemini", "Opus", "Grok")}
    S["by_recipient_swaps"] = {m: gap([o for o in op if o["recipient_model"] == m], "Swap") for m in ("Sol", "Gemini", "Opus", "Grok")}
    S["by_recipient_cash_bids"] = {m: gap([o for o in op if o["recipient_model"] == m], "Cash bid") for m in ("Sol", "Gemini", "Opus", "Grok")}
    neither = cellrows(op, "Swap", "neither")
    acc = [o for o in neither if o["response"] == "accept_trade"]
    S["neither_swaps"] = dict(n=len(neither), grok_authored=sum(o["author_model"] == "Grok" for o in neither), accepted=len(acc),
                              accepted_grok_authored=sum(o["author_model"] == "Grok" for o in acc),
                              accepted_grok_authored_from_conflicting_call=sum(1 for o in acc if o["author_model"] == "Grok" and o["opening_call_conflicts"]))
    S["both_swaps_opening"] = rej(cellrows(op, "Swap", "both"))
    focal_bids = [o for o in op if o["form"] == "Cash bid" and o["completion"] in ("proposer_only", "neither")]
    S["cash_bid_authors"] = dict(C(o["author_model"] for o in focal_bids))
    # counters that keep the non-cash bundle and ask for more cash
    for name, sel in (("proposer_only_completion_offers", lambda o: o["completion"] == "proposer_only"),
                      ("neither_deed_requests", lambda o: o["completion"] == "neither" and o["form"] in ("Swap", "Cash bid"))):
        r = [o for o in legal if sel(o) and o["response"] == "counter_trade"]
        S[f"counters_{name}"] = [sum(1 for o in r if o["counter_keeps_bundle_and_improves_cash"]), len(r)]
    # recipient-completing rejections where acceptance was legal (population of the inherited 61/74 reading)
    rc = [o for o in legal if o["completion"] in ("recipient_only", "both") and o["response"] == "reject_trade"]
    S["recipient_completing_rejections"] = dict(n=len(rc), by_cell=dict(C(o["completion"] for o in rc)), by_model=dict(C(o["recipient_model"] for o in rc)))
    write_json("bargaining_summary.json", S)
    for k, v in S.items():
        if k != "table":
            print(k, "=", v)
