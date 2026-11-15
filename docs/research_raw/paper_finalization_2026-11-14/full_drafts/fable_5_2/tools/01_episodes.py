"""Rebuild every financing episode from raw decisions.jsonl and events.jsonl.

Read-only. No engine, replay, policy or model call. An episode starts at the first
LIQUIDATION_DECISION for one pending obligation and ends when the debt is paid or the
player is eliminated. Outcomes come from the stored events emitted by the last decision
of the episode, not from an earlier ledger.

Writes data/episodes.json and prints a comparison with the 12 November ledger.
"""
import collections
import json

from lib import *

OLD = ROOT / "docs/research_raw/paper_revision_2026-11-12/integrated/data/liquidation_episodes.json"


def event_index(g):
    idx = {}
    with open(run_dir(g) / "events.jsonl") as f:
        for line in f:
            e = json.loads(line)
            idx[e["seq"]] = e
    return idx


def channels(r, attempt=-1):
    a = r["attempts"][attempt]
    tcs = a.get("parsed_tool_calls") or []
    call = tcs[0] if tcs else None
    return {
        "attempt_index": attempt % len(r["attempts"]),
        "response_condition": a.get("response_condition"),
        "outcome": a.get("outcome"),
        "received_call": call["name"] if call else None,
        "assistant_content": a.get("assistant_content") or "",
        "named_in_content": named_action(a.get("assistant_content"), FIN_ACTIONS),
        "provider_text": provider_text(r, attempt),
        "provider_detail_types": provider_detail_types(r, attempt),
        "refusal": message(a).get("refusal"),
        "reasoning_tokens": (((a.get("raw_response") or {}).get("usage") or {}).get("completion_tokens_details") or {}).get("reasoning_tokens"),
    }


def build():
    out = []
    for g in range(1, 21):
        st, rs, lines = load(g)
        ev = event_index(g)
        eps, cur = [], None
        for i in sorted(rs):
            r = rs[i]
            if r["decision_type"] != "LIQUIDATION_DECISION":
                continue
            sc = st[i]["prompt_payload"]["action_state"]["scenario"]
            sig = (r["player_id"], r["turn_index"], sc["owed_amount"], sc.get("owed_to_player_id"), sc.get("reason"))
            if cur is None or cur["sig"] != sig or cur["closed"]:
                cur = {"sig": sig, "ds": [], "closed": False}
                eps.append(cur)
            cur["ds"].append(i)
            if r["final_action"]["action"] == "declare_bankruptcy":
                cur["closed"] = True
        for e in eps:
            i = e["ds"][0]
            r0, s0 = rs[i], st[i]
            pp = s0["prompt_payload"]
            sc = pp["action_state"]["scenario"]
            you = pp["game_state"]["you"]
            owned = you["holdings"]["owned"]
            salvage = mstar = hotels = houses = 0
            built = {}
            for h in owned:
                sp = SPACES[h["space_key"]]
                lv = 5 if h.get("hotel") else h.get("houses", 0)
                if lv:
                    salvage += lv * HOUSE_COST[sp["group"]] // 2
                    built[h["space_key"]] = lv
                hotels += 1 if h.get("hotel") else 0
                houses += h.get("houses", 0)
                if not h.get("mortgaged"):
                    mstar += sp["price"] // 2
            listed = list(sc["options"].get("mortgageable_space_keys", []))
            listed_sales = list(sc["options"].get("sellable_building_space_keys", []))
            m0 = sum(mortgage_value(k) for k in listed)
            # route
            route, sale_total, mort_total, released_used = [], 0, 0, []
            for d in e["ds"]:
                fa = rs[d]["final_action"]
                if fa["action"] == "mortgage_property":
                    k = fa["args"]["space_key"]
                    v = mortgage_value(k)
                    mort_total += v
                    new = k not in listed
                    if new:
                        released_used.append(k)
                    route.append({"d": d, "action": "mortgage", "space": k, "value": v, "released": new})
                elif fa["action"] == "sell_houses_or_hotel":
                    v = 0
                    items = []
                    for it in fa["args"]["sell_plan"]:
                        unit = HOUSE_COST[SPACES[it["space_key"]]["group"]] // 2
                        v += unit * it["count"]
                        items.append({"space": it["space_key"], "kind": it["kind"], "count": it["count"]})
                    sale_total += v
                    route.append({"d": d, "action": "sell", "items": items, "value": v})
                else:
                    route.append({"d": d, "action": "declare"})
            last = rs[e["ds"][-1]]
            # outcome from the events emitted by the last decision
            bankrupt = False
            for seq in range(last["emitted_event_seq_start"], last["emitted_event_seq_end"] + 1):
                x = ev.get(seq)
                if x and x["type"] == "CASH_CHANGED" and x["payload"].get("reason") == "BANKRUPTCY" and x["payload"].get("player_id") == r0["player_id"]:
                    bankrupt = True
            declared = last["final_action"]["action"] == "declare_bankruptcy"
            # developed-group structure for the continued-financing premises
            groups = sorted({SPACES[k]["group"] for k in built})
            own_keys = {h["space_key"] for h in owned}
            p1 = all(COLORS[gname] <= own_keys for gname in groups)
            p2 = True
            hotels_by_group = {}
            for gname in groups:
                lv = [built.get(k, 0) for k in COLORS[gname] if k in own_keys]
                if max(lv) - min(lv) > 1:
                    p2 = False
                hotels_by_group[gname] = sum(1 for k in COLORS[gname] if built.get(k) == 5)
            houses_in_hotel_free = sum(lv for k, lv in built.items() if hotels_by_group[SPACES[k]["group"]] == 0)
            first = channels(r0)
            fa0 = r0["final_action"]
            rec = dict(
                game=g, first=i, last=e["ds"][-1], decisions=e["ds"], model=who(r0), player_id=r0["player_id"],
                turn=r0["turn_index"], debt=sc["owed_amount"], creditor=sc.get("owed_to_player_id"), reason=sc.get("reason"),
                cash=you["cash"], salvage=salvage, m0=m0, mstar=mstar,
                u0=you["cash"] + salvage + m0, ustar=you["cash"] + salvage + mstar,
                listed_mortgages=listed, listed_sales=listed_sales,
                menu=[a if isinstance(a, str) else a.get("action") for a in pp["action_state"]["available_actions"]],
                built=built, hotels=hotels, houses=houses, bank_houses=pp["game_state"]["bank"]["houses_remaining"],
                hotels_by_group=hotels_by_group, houses_in_hotel_free_groups=houses_in_hotel_free,
                developed_groups_complete=p1, developed_groups_even=p2,
                actions=[rs[d]["final_action"]["action"] for d in e["ds"]],
                fallbacks=[bool(rs[d].get("fallback_used")) for d in e["ds"]],
                conditions=[rs[d]["attempts"][-1].get("response_condition") for d in e["ds"]],
                route=route, sale_total=sale_total, mortgage_total=mort_total, released_mortgages_used=released_used,
                declared=declared, bankrupt=bankrupt, outcome="bankrupt" if bankrupt else "paid",
                cash_after=None if bankrupt else you["cash"] + sale_total + mort_total - sc["owed_amount"],
                first_action=fa0["action"], first_args=fa0.get("args"),
                first_note=fa0.get("private_thought") or "", first_public=fa0.get("public_message") or "",
                first_channels=first, first_attempts=len(r0["attempts"]),
                source_file=str(decisions_path(g).relative_to(ROOT)), source_line=lines[i],
                decision_id=r0["decision_id"],
            )
            out.append(rec)
    return out


if __name__ == "__main__":
    for g, rel in GAME_MAP.items():
        assert (ROOT / rel / "decisions.jsonl").exists(), rel
    eps = build()
    write_json("episodes.json", eps)
    C = collections.Counter
    print("episodes", len(eps), C(e["outcome"] for e in eps))
    print("liquidation decisions", sum(len(e["decisions"]) for e in eps))
    print("declared vs bankrupt", C((e["declared"], e["bankrupt"]) for e in eps))
    old = {(p["game"], p["first_decision"]): p for p in json.loads(OLD.read_text())}
    mine = {(e["game"], e["first"]): e for e in eps}
    diff = [k for k in mine if k not in old or old[k]["outcome"] != mine[k]["outcome"] or old[k]["debt"] != mine[k]["debt"]
            or old[k]["cash"] != mine[k]["cash"] or old[k]["upper_bound"] != mine[k]["ustar"] or old[k]["actions"] != mine[k]["actions"]]
    print("12 Nov ledger rows", len(old), "| keys only in one", len(set(old) ^ set(mine)), "| field differences", len(diff))
