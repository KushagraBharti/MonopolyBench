"""Recompute the figures this review relies on and verify every new quoted span.

Reads saved records and the integrated paper's sources. Runs no engine, replay or model.
Writes data/checks.json. Run rebuild.py first.
"""
import json, re, glob, collections, hashlib
from lib import *

DATA = HERE.parent / "data"
E = json.loads((DATA / "episodes.json").read_text())
O = json.loads((DATA / "offers.json").read_text())
PAPER_EPS = {(p["game"], p["first_decision"]): p for p in json.loads((INT / "data/liquidation_episodes.json").read_text())}
out = {}

# ---- debt census -------------------------------------------------------------
for e in E:
    e["outcome"] = PAPER_EPS[(e["game"], e["first"])]["outcome"]  # paid or eliminated, from the event-based ledger


def cls(e):
    if e["ustar"] < e["debt"]:
        return "bound_short"
    if e["u0"] < e["debt"]:
        return "released_mortgages_necessary"
    if e["cash"] + e["m0"] >= e["debt"]:
        return "cash_and_listed_mortgages"
    return "sales_needed"


paid = [e for e in E if e["outcome"] == "paid"]
short = [e for e in E if cls(e) == "bound_short"]
choice = [e for e in short if e["menu"] != ["declare_bankruptcy"]]
nec = [e for e in E if cls(e) == "released_mortgages_necessary"]
out["debt"] = {
    "episodes": len(E), "paid": len(paid), "eliminated": len(E) - len(paid),
    "class_by_outcome": {f"{c}|{o}": n for (c, o), n in sorted(collections.Counter((cls(e), e["outcome"]) for e in E).items())},
    "paid_one_action": sum(len(e["actions"]) == 1 for e in paid), "paid_multi_action": sum(len(e["actions"]) > 1 for e in paid),
    "paid_max_actions": max(len(e["actions"]) for e in paid),
    "paid_mortgage_actions": sum(a == "mortgage_property" for e in paid for a in e["actions"]),
    "paid_sale_actions": sum(a == "sell_houses_or_hotel" for e in paid for a in e["actions"]),
    "paid_debt_total": sum(e["debt"] for e in paid), "fallback_actions": sum(any(e["fallbacks"]) for e in E),
    "bound_sufficient_episodes": len(E) - len(short),
    "bound_sufficient_first_action_declare": sum(e["actions"][0] == "declare_bankruptcy" for e in E if cls(e) != "bound_short"),
    "bound_short_episodes": len(short), "bound_short_first_action_declare": sum(e["actions"][0] == "declare_bankruptcy" for e in short),
    "bound_short_bankruptcy_only_menus": len(short) - len(choice),
    "bound_short_with_choice": len(choice), "bound_short_with_choice_declare_first": sum(e["actions"][0] == "declare_bankruptcy" for e in choice),
    "bound_short_liquidate_first": [f"G{e['game']} d{e['first']} {e['model']}" for e in choice if e["actions"][0] != "declare_bankruptcy"],
    "payable_declarations": [f"G{e['game']} d{e['first']} {e['model']} {cls(e)}" for e in E if cls(e) != "bound_short" and e["actions"][0] == "declare_bankruptcy"],
    "g7_d338": next({k: e[k] for k in ("debt", "cash", "salvage", "m0", "u0", "ustar", "actions", "menu")} for e in E if (e["game"], e["first"]) == (7, 338)),
    "eliminations_by_system": dict(collections.Counter(e["model"] for e in E if e["outcome"] != "paid")),
    "payments_by_system": dict(collections.Counter(e["model"] for e in paid)),
    "payments_using_mortgages_absent_from_first_menu": sum(e["mortgages_absent_from_first_menu"] > 0 for e in paid),
    "mortgages_absent_from_first_menu_used": sum(e["mortgages_absent_from_first_menu"] for e in paid),
    "non_necessary_uses": [f"G{e['game']} d{e['first']} {e['model']}" for e in paid if e["mortgages_absent_from_first_menu"] and cls(e) != "released_mortgages_necessary"],
}

# ---- sixteen necessity episodes: table values, printed text, request contents ----
rows = [l.split(" & ") for l in (INT / "sections/necessary_rows.tex").read_text().splitlines() if l.startswith("G")]
table = {r[0]: (int(r[2].replace(",", "")), int(r[3].replace(",", "")), int(r[4].replace(",", "")), r[5]) for r in rows}
tex = (INT / "sections/necessary_texts.tex").read_text()
blocks = re.split(r"\\Needspace\{8\\baselineskip\}\\subsection\*\{", tex)[1:]


def detex(s):
    for a, b in (("\\$", "$"), ("\\(\\rightarrow\\)", "→"), ("\\textasciitilde{}", "~"), ("\\%", "%"), ("\\&", "&"), ("\\_", "_"), ("\\#", "#")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", re.sub(r"\\par\b", " ", s)).strip()


printed = {}
for b in blocks:
    head, rest = b.split("}", 1)
    m = re.match(r"G(\d+) d(\d+)", head)
    printed[(int(m.group(1)), int(m.group(2)))] = (re.search(r"\\textit\{(.*?)\}", rest).group(1), detex(rest.split("\\par", 1)[1].rsplit("}", 1)[0]))
sixteen = []
for e in nec:
    g, d = e["game"], e["first"]
    st, rs = load(g)
    r = rs[d]
    pp = st[d]["prompt_payload"]
    chan, text = printed[(g, d)]
    src = r["final_action"]["private_thought"] if "private note" in chan else reasoning(r)
    listed = set(pp["action_state"]["scenario"]["options"].get("mortgageable_space_keys", []))
    released = [h["space_key"] for h in pp["game_state"]["you"]["holdings"]["owned"] if not h["mortgaged"] and h["space_key"] not in listed]
    mem = pp["game_state"]["memory"]
    rows_with_deed_amount = [t["action"] for t in mem["public_timeline_last_20"] if any(k in (t.get("action") or "") for k in released) and "mortgag" in (t.get("action") or "").lower()]
    sixteen.append({
        "entry": f"G{g} d{d}", "system": e["model"], "debt": e["debt"], "u0": e["u0"], "ustar": e["ustar"], "outcome": e["outcome"],
        "table_row_matches": table[f"G{g} d{d}"] == (e["debt"], e["u0"], e["ustar"], "paid" if e["outcome"] == "paid" else "bankrupt"),
        "printed_text_equals_source_field": text == re.sub(r"\s+", " ", src).strip(),
        "channel": "private note" if "private note" in chan else "returned reasoning",
        "first_action": e["actions"][0], "actions": len(e["actions"]),
        "released_deeds": released,
        "timeline_rows_showing_a_mortgage_amount_for_a_released_deed": rows_with_deed_amount,
        "system_prompt_mentions_mortgage": "mortgag" in st[d]["prompt_messages"][0]["content"].lower(),
        "menu_lists_values": any(ch.isdigit() for ch in json.dumps(pp["action_state"]["scenario"]["options"])),
    })
out["sixteen"] = sixteen
out["sixteen_summary"] = {
    "episodes": len(sixteen), "paid": sum(s["outcome"] == "paid" for s in sixteen),
    "all_table_rows_match": all(s["table_row_matches"] for s in sixteen),
    "all_printed_texts_equal_source": all(s["printed_text_equals_source_field"] for s in sixteen),
    "requests_with_a_mortgage_row_for_a_released_deed": [s["entry"] for s in sixteen if s["timeline_rows_showing_a_mortgage_amount_for_a_released_deed"]],
    "requests_whose_system_prompt_mentions_mortgage": sum(s["system_prompt_mentions_mortgage"] for s in sixteen),
    "menus_listing_any_number": sum(s["menu_lists_values"] for s in sixteen),
}

# ---- negotiation ---------------------------------------------------------------
def cnt(rs):
    c = collections.Counter(r["response"] for r in rs)
    return [len(rs), c["accept_trade"], c["counter_trade"], c["reject_trade"]]


legal = [o for o in O if o["accept_available"]]
opening = [o for o in legal if o["exchange_index"] == 0]
swap = [o for o in opening if o["form"] == "Swap"]
bid = [o for o in opening if o["form"] == "Cash bid"]


def pair(rs):
    return cnt([o for o in rs if o["completion_cell"] == "author_only"]), cnt([o for o in rs if o["completion_cell"] == "neither"])


def gap(rs):
    a, b = pair(rs)
    return None if not a[0] or not b[0] else round(100 * (a[3] / a[0] - b[3] / b[0]), 2)


def blocks_of(rs):
    return [{"block": b + 1, "own_only_rejected/received": f"{pair(x)[0][3]}/{pair(x)[0][0]}", "neither_rejected/received": f"{pair(x)[1][3]}/{pair(x)[1][0]}", "gap_pp": gap(x)}
            for b in range(5) for x in [[o for o in rs if (o["game"] - 1) // 4 == b]]]


pops = {"all_swaps": swap, "no_grok_authors": [o for o in swap if o["author_model"] != "Grok"],
        "no_conflicting_openings": [o for o in swap if not o["opening_call_conflicts"]], "cash_bids": bid}
low = [o for o in O if o["completion_cell"] == "author_only" and o["recipient_cash"] < 100]
high = [o for o in O if o["completion_cell"] == "author_only" and o["recipient_cash"] >= 300]
out["negotiation"] = {
    "responses": cnt(O), "legal": cnt(legal), "threads": sum(o["exchange_index"] == 0 for o in O),
    "table": {f"{stage}|{f}|{c}": cnt([o for o in rows_ if o["form"] == f and o["completion_cell"] == c])
              for stage, rows_ in (("Opening", opening), ("Later", [o for o in legal if o["exchange_index"] > 0]))
              for f in ("Swap", "Cash bid", "Cash ask", "Other") for c in ("author_only", "recipient_only", "both", "neither")},
    "populations": {k: {"own_only": pair(v)[0], "neither": pair(v)[1], "gap_pp": gap(v), "blocks": blocks_of(v),
                        "leave_one_block_out": [gap([o for o in v if (o["game"] - 1) // 4 != b]) for b in range(5)]} for k, v in pops.items()},
    "swap_by_proposer": {m: {"own_only": pair([o for o in swap if o["author_model"] == m])[0], "neither": pair([o for o in swap if o["author_model"] == m])[1], "gap_pp": gap([o for o in swap if o["author_model"] == m])} for m in NAME.values()},
    "swap_by_recipient": {m: gap([o for o in swap if o["recipient_model"] == m]) for m in NAME.values()},
    "bid_by_recipient": {m: gap([o for o in bid if o["recipient_model"] == m]) for m in NAME.values()},
    "opening_cash_bids_by_proposer": {m: {"own_only": pair([o for o in bid if o["author_model"] == m])[0][0], "neither": pair([o for o in bid if o["author_model"] == m])[1][0]} for m in NAME.values()},
    "responses_by_recipient": {m: cnt([o for o in O if o["recipient_model"] == m]) for m in NAME.values()},
    "neither_swap_acceptances_by_proposer": dict(collections.Counter(o["author_model"] for o in swap if o["completion_cell"] == "neither" and o["response"] == "accept_trade")),
    "neither_swap_acceptances_from_conflicting_openings": sum(1 for o in swap if o["completion_cell"] == "neither" and o["response"] == "accept_trade" and o["opening_call_conflicts"]),
    "conflicting_openings": sum(bool(o["opening_call_conflicts"]) for o in O if o["exchange_index"] == 0),
    "counters_to_own_only": [sum(1 for o in O if o["completion_cell"] == "author_only" and o["response"] == "counter_trade"),
                             sum(1 for o in O if o["completion_cell"] == "author_only" and o["counter_keeps_bundle_and_improves_cash"])],
    "counters_to_neither_deed_requests": [sum(1 for o in O if o["completion_cell"] == "neither" and o["recipient_gives_deeds"] and o["response"] == "counter_trade"),
                                          sum(1 for o in O if o["completion_cell"] == "neither" and o["recipient_gives_deeds"] and o["counter_keeps_bundle_and_improves_cash"])],
    "own_only_holder_cash_below_100": cnt(low), "own_only_holder_cash_300_plus": cnt(high),
    "low_cash_later_offers": sum(o["exchange_index"] > 0 for o in low), "low_cash_facing_opus": sum(o["recipient_model"] == "Opus" for o in low),
    "low_cash_gemini": cnt([o for o in low if o["recipient_model"] == "Gemini"]),
    "rejections_of_recipient_completing_offers": dict(collections.Counter(o["completion_cell"] for o in legal if o["completion_cell"] in ("recipient_only", "both") and o["response"] == "reject_trade")),
    "those_rejections_by_recipient": dict(collections.Counter(o["recipient_model"] for o in legal if o["completion_cell"] in ("recipient_only", "both") and o["response"] == "reject_trade")),
}

# ---- response conditions, channels, requests, replay -----------------------------
decisions = attempts = 0
first_ref = collections.Counter(); opus_first = collections.Counter(); later_ref = []
grok = collections.Counter(); kinds = collections.Counter(); has_reason = collections.Counter(); finals = collections.Counter()
liq_note = collections.Counter()
for g in range(1, 21):
    st, rs = load(g)
    for d, r in rs.items():
        decisions += 1
        attempts += len(r["attempts"])
        m = who(r)
        finals[m] += 1
        det = message(r["attempts"][-1]).get("reasoning_details") or []
        kinds[m + "|" + "+".join(sorted({x.get("type") for x in det})) ] += 1
        has_reason[m] += bool(reasoning(r))
        if m == "Opus":
            opus_first[g] += 1
            first_ref[g] += r["attempts"][0].get("outcome") == "refused"
            later_ref += [f"G{g} d{d}" for a in r["attempts"][1:] if a.get("outcome") == "refused"]
        if m == "Grok":
            n = named_action(r)
            act = (r.get("final_action") or {}).get("action")
            conflict = bool(n and act and n != act and not r.get("fallback_used"))
            grok["conflicts"] += conflict
            if act == "propose_trade":
                grok["openings"] += 1; grok["opening_conflicts"] += conflict
            if act == "accept_trade":
                grok["acceptances"] += 1; grok["acceptance_conflicts"] += conflict
        if r["decision_type"] == "LIQUIDATION_DECISION":
            liq_note[st[d]["prompt_payload"]["action_state"]["scenario"]["note"]] += 1
tool_choice = collections.Counter(); intents = 0; replay = collections.Counter(); events_compared = 0
for g in range(1, 21):
    base = run_dir(g).parent
    for f in glob.glob(str(base / "cloud/calls/*.intent.json")):
        p = json.load(open(f))["payload"]
        intents += 1
        tool_choice[f"{p['model']}|{p.get('tool_choice')}|effort={p.get('reasoning', {}).get('effort')}|sampling_keys={sorted(k for k in p if k in ('temperature', 'top_p', 'max_tokens'))}"] += 1
    ar = json.load(open(run_dir(g) / "artifact_replay_report.json")); sr = json.load(open(run_dir(g) / "state_replay_report.json"))
    events_compared += ar["original_compared_event_count"]
    replay[f"artifact:{ar['status']}:excluded={ar['excluded_event_types']}"] += 1
    replay[f"state:{sr['status']}:excluded={sr['excluded_event_types']}"] += 1
norm = lambda x: re.sub(r"\s+", " ", x).strip()
verb = lambda p: norm(re.search(r"\\begin\{verbatim\}\n(.*?)\\end\{verbatim\}", (INT / p).read_text(), re.S).group(1))
st1, _ = load(1)
out["conditions"] = {
    "decisions": decisions, "attempts": attempts, "saved_request_records": intents, "tool_choice": dict(tool_choice),
    "opus_first_attempt_refusals_g1_g4": [f"{first_ref[g]}/{opus_first[g]}" for g in range(1, 5)],
    "opus_first_attempt_refusals_g5_g20": f"{sum(first_ref[g] for g in range(5, 21))}/{sum(opus_first[g] for g in range(5, 21))}",
    "opus_first_attempt_refusals_total": sum(first_ref.values()), "opus_later_refusals": later_ref,
    "grok": dict(grok), "liquidation_instruction_texts": {k: v for k, v in liq_note.items()},
    "returned_reasoning_present_in_final_attempts": {m: f"{has_reason[m]}/{finals[m]}" for m in NAME.values()},
    "returned_reasoning_detail_types": dict(kinds),
    "replay_reports": dict(replay), "events_compared_in_artifact_replay": events_compared,
    "standard_prompt_printed_equals_stored": verb("sections/standard_prompt.tex") == norm(st1[0]["prompt_messages"][0]["content"]),
    "recovery_prompt_printed_equals_stored": verb("sections/recovery_prompt.tex") == norm(open(sorted(glob.glob(str(run_dir(20) / "prompts/*_retry1_system.txt")))[0]).read()),
}

# ---- new quoted spans used in replacement_prose.tex --------------------------------
SPANS = [
    ("g15-d76-note", 15, 76, "note", "Don't sell Ventnor back to p4 (gives them 2/3 yellow)."),
    ("g15-d158-note", 15, 158, "note", "Never trade Ventnor (p4 yellow) or Penn Ave (p4 green)"),
    ("g15-d162-note", 15, 162, "note", "Never trade Ventnor or Penn Ave."),
    ("g15-d135-public", 15, 135, "public", "Grok, if you let GPT take Pacific for $35, they'll hold the blocker on your Green set"),
    ("g15-d152-public", 15, 152, "public", "Grok, don't let GPT get two greens cheap."),
    ("g15-d154-public", 15, 154, "public", "Make them pay real value for a $300 property."),
    ("g15-d159-public", 15, 159, "public", "Don't let him grab another set piece cheap."),
    ("g15-d161-public", 15, 161, "public", "don't let GPT take Kentucky for $115"),
    ("g15-d166-public", 15, 166, "public", "so let's not hand him the last piece of any set."),
    ("g2-d115-note", 2, 115, "note", "Keep Marvin blocking p4's yellows"),
    ("g2-d118-note", 2, 118, "note", "Marvin from p1 for $200 is a blocker, not a set"),
    ("g2-d119-public", 2, 119, "public", "Marvin controls access to a well-funded yellow monopoly. $450 buys that leverage; $200 doesn't."),
    ("g2-d120-public", 2, 120, "public", "$450 is the price for the player who completes yellow. I'm not building it."),
    ("g2-d122-public", 2, 122, "public", "p1, sit on Marvin. Selling it to p4 gives them a second monopoly on top of light blue"),
    ("g18-d421-reason", 18, 421, "reasoning", "I'll counter with a lower amount — around $250 — keeping my cash buffer"),
    ("g18-d427-reason", 18, 427, "reasoning", "Trading for Pacific at $300 isn't appealing either"),
    ("g18-d431-reason", 18, 431, "reasoning", "Buying Pacific might just prolong p1's survival, so maybe it's smarter to hold onto cash in case p1's orange hotels hit me with heavy rent."),
    ("g18-d431-public", 18, 431, "public", "Thanks for the $750. Your roll, p1. My Pacific offer still stands."),
    ("g18-d423-public", 18, 423, "public", "Offer stands if you change your mind."),
    ("g18-d425-public", 18, 425, "public", "My Pacific offer still stands."),
    ("g18-d427-public", 18, 427, "public", "my Pacific offer still stands."),
    ("g12-d190-carried", 12, 190, "carried", "$53 cash plus $130 in mortgageable non-red assets provides emergency liquidity"),
    ("g17-d234-carried", 17, 234, "carried", "Keeping Baltic Avenue unmortgaged as a $30 emergency reserve"),
    ("g5-d263-carried", 5, 263, "carried", "my total liquidatable cash + houses is $774 < $900"),
    ("g5-d263-reason-first", 5, 263, "reasoning", "Selling all six houses would only raise $600."),
    ("g5-d263-reason-revise", 5, 263, "reasoning", "I initially miscalculated! Selling the houses on Park Place and Boardwalk alone doesn't cover the debt."),
    ("g20-d95-note", 20, 95, "note", "P1's red monopoly is cash-starved; buying New York now would fund dangerous development without completing my oranges."),
    ("g20-d129-public", 20, 129, "public", "That's money you can put into more red houses right now."),
    ("g7-d339-reason", 7, 339, "reasoning", "house selling seems blocked even though St Charles has houses, oddly."),
    ("g13-d252-reason", 13, 252, "reasoning", "I will frame the $130 offer as leaving me $35 short of Short Line, omitting that I could mortgage Ventnor to survive."),
    ("g1-d476-carried-rule", 1, 476, "carried", "yellows cannot be mortgaged while it stands"),
    ("g1-d476-carried-total", 1, 476, "carried", "yellow mortgages ~$400 as reserve"),
    ("g13-d195-carried", 13, 195, "carried", "Unmortgaging Park Place ($193)"),
    ("g18-d309-carried", 18, 309, "carried", "p3 must sell all 5 Dark Blue houses and mortgage a Dark Blue property"),
    ("g20-d327-carried", 20, 327, "carried", "$325 idle mortgage capacity plus building liquidation can cover a hit"),
]
spans = []
for sid, g, d, field, text in SPANS:
    st, rs = load(g)
    r = rs[d]
    fa = r.get("final_action") or {}
    if field == "note":
        hay = [fa.get("private_thought") or ""]
    elif field == "public":
        hay = [fa.get("public_message") or ""]
    elif field == "reasoning":
        hay = [reasoning(r)]
    else:
        hay = [t["thought"] for t in st[d]["prompt_payload"]["game_state"]["memory"]["your_private_thoughts_last_10"]]
    found = [h for h in hay if text in h]
    spans.append({"id": sid, "game": g, "decision": d, "turn": r["turn_index"], "system": who(r), "field": field, "text": text,
                  "found": bool(found), "carried_notes_containing": len(found) if field == "carried" else None,
                  "field_sha256": hashlib.sha256(found[0].encode()).hexdigest() if found else None})
out["new_quoted_spans"] = spans
out["all_new_spans_found"] = all(s["found"] for s in spans)
# carried-note counts used in the text
st12, _ = load(12)
out["g12_d190_carried_notes_with_130"] = sum("$130" in t["thought"] for t in st12[190]["prompt_payload"]["game_state"]["memory"]["your_private_thoughts_last_10"])
st17, _ = load(17)
out["g17_d234_carried_notes_with_30_baltic"] = sum("$30" in t["thought"] and "Baltic" in t["thought"] for t in st17[234]["prompt_payload"]["game_state"]["memory"]["your_private_thoughts_last_10"])
# G20 cash path around the appeal
ev = events(20)
out["g20_grok_cash_changes_turns_26_27"] = [[e["turn_index"], e["payload"]["reason"], e["payload"]["delta"]] for e in ev if e["turn_index"] in (26, 27) and e["type"] == "CASH_CHANGED" and e["payload"].get("player_id") == "p1"]
# G18 turn indices
_, rs18 = load(18)
out["g18_turns"] = {f"d{d}": [rs18[d]["turn_index"], rs18[d]["final_action"]["action"], rs18[d]["final_action"].get("args", {}).get("space_key") or (rs18[d]["final_action"].get("args", {}).get("offer", {}) or {}).get("cash") or (rs18[d]["final_action"].get("args", {}).get("request", {}) or {}).get("cash")] for d in (431, 441, 442, 445, 448, 451, 452, 453, 454, 455, 456, 460)}
# ---- asking prices, from the integrated derived file (definitions inherited) --------
import statistics
asks = [x for x in json.loads((INT / "data/single_deed_prices.json").read_text()) if x["kind"] == "ask"]
cells = collections.defaultdict(lambda: {True: [], False: []})
for x in asks:
    cells[(x["author"], x["mortgaged"])][x["completes"]].append(x)
rows_ = []
for k in sorted(cells):
    c = cells[k]
    if c[True] and c[False]:
        rows_.append({"seller": k[0], "mortgaged": k[1], "completing_asks": len(c[True]), "other_asks": len(c[False]),
                      "median_cash": [statistics.median(x["cash"] for x in c[True]), statistics.median(x["cash"] for x in c[False])],
                      "median_ask_to_list": [round(statistics.median(x["ratio"] for x in c[True]), 2), round(statistics.median(x["ratio"] for x in c[False]), 2)]})
out["asking_price_cells"] = {"cells": rows_, "ratio_median_higher_for_completing": sum(r["median_ask_to_list"][0] > r["median_ask_to_list"][1] for r in rows_),
                             "cash_median_higher_for_completing": sum(r["median_cash"][0] > r["median_cash"][1] for r in rows_)}
# Opus-authored opening cash bids written under action-only recovery
cond = collections.Counter()
for o in O:
    if o["exchange_index"] == 0 and o["form"] == "Cash bid" and o["author_model"] == "Opus" and o["accept_available"]:
        st, rs = load(o["game"])
        j = o["decision"] - 1
        while not ((rs[j].get("final_action") or {}).get("action") == "propose_trade" and who(rs[j]) == "Opus"):
            j -= 1
        cond[rs[j]["attempts"][-1].get("response_condition")] += 1
out["opus_opening_cash_bids_by_response_condition"] = dict(cond)
(DATA / "checks.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: out[k] for k in ("sixteen_summary", "all_new_spans_found", "g12_d190_carried_notes_with_130", "g17_d234_carried_notes_with_30_baltic", "g20_grok_cash_changes_turns_26_27", "g18_turns")}, indent=1))
print([s["id"] for s in spans if not s["found"]])
print(json.dumps(out["debt"], indent=1)[:1800])
print(json.dumps(out["conditions"], indent=1)[:2600])
