#!/usr/bin/env python3
"""Re-tabulate retained economic ledgers (existing data only; no engine or model execution).

Inputs (all read-only):
  ../../data/{agenda_flows,agenda_offers,t01_cohort,t05_spending_units,t06_eliminations,
              first_management_windows,certificate_results}.json
  ../../../paper_phase1_2026-10-28/sol/group_episodes.jsonl   (retained phase-1 episode ledger)
  <repo>/contracts/data/board.json                             (group membership, prices)
Output: data/economy_retabulation.json
"""
import json, collections, statistics as st, pathlib, hashlib
HERE = pathlib.Path(__file__).resolve().parent.parent
RW = HERE.parent.parent
RAW = RW.parent
REPO = RAW.parent.parent
D = RW / "data"
C = collections.Counter
MODELS = ["Sol", "Gemini", "Opus", "Grok"]
def J(p): return json.loads(pathlib.Path(p).read_text())
flows = J(D / "agenda_flows.json"); offers = J(D / "agenda_offers.json"); cohort = J(D / "t01_cohort.json")
units = J(D / "t05_spending_units.json"); elims = J(D / "t06_eliminations.json"); fmw = J(D / "first_management_windows.json")
cert = J(D / "certificate_results.json")
EP = RAW / "paper_phase1_2026-10-28" / "sol" / "group_episodes.jsonl"
eps = [json.loads(l) for l in EP.read_text().splitlines() if l.strip()]
board = J(REPO / "contracts" / "data" / "board.json")
def key(name): return name.upper().replace(".", "").replace("&", "").replace("  ", " ").replace(" ", "_")
group_of = {}
for s in board["spaces"]:
    if s.get("kind") == "PROPERTY":
        group_of[key(s["name"])] = s["group"]
house_cost = board["house_cost_by_group"]
winner = {c["game"]: c["winner"] for c in cohort}
winner_seat = {c["game"]: c["winner_seat"] for c in cohort}
BLOCK = lambda g: (g - 1) // 4 + 1
out = {"inputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [D / "agenda_flows.json", D / "agenda_offers.json", D / "t05_spending_units.json", D / "t06_eliminations.json", D / "first_management_windows.json", D / "certificate_results.json", EP]}}

# ---- 0. flow totals -------------------------------------------------------
tot = {}
for k in ["paid_rent", "trade_cash", "trade_deed", "estate_cash", "estate_deed"]:
    rr = [x for x in flows if x["kind"] == k]
    tot[k] = {"events": len(rr), "amount": sum(x["amount"] for x in rr),
              "to_eventual_winner": sum(x["amount"] for x in rr if x.get("to_model") == winner[x["game"]])}
out["flow_totals"] = tot
est_d = [x for x in flows if x["kind"] == "estate_deed"]
out["estate_deeds"] = {"nonterminal": sum(1 for x in est_d if not x["terminal_estate"]), "terminal": sum(1 for x in est_d if x["terminal_estate"]),
                       "nonterminal_to_winner": sum(1 for x in est_d if not x["terminal_estate"] and x["to_model"] == winner[x["game"]])}

# ---- 1. completed-group episodes ------------------------------------------
for e in eps:
    e["win"] = e["model"] == winner[e["game"]]
    e["terminal"] = e["access_status"] != "observed"
out["episodes"] = {"n": len(eps), "by_route": dict(C(e["route"] for e in eps)),
                   "by_route_access": {f"{r}|{a}": n for (r, a), n in C((e["route"], e["access_status"]) for e in eps).items()}}
live = [e for e in eps if not e["terminal"]]
out["live_episodes"] = {"n": len(live)}
rt = {}
for r in ["trade", "creditor_inheritance", "direct_purchase", "auction"]:
    rr = [e for e in live if e["route"] == r]
    rt[r] = {"n": len(rr), "by_eventual_winner": sum(e["win"] for e in rr), "built_first_window": sum(1 for e in rr if e["built_first_management"]),
             "entry_legal": sum(1 for e in rr if e["entry_legal"]), "legal_some_time_in_window": sum(1 for e in rr if e["entry_legal"] or e["later_legal_in_window"]),
             "rent_until_loss_or_end": sum(e["rent_until_loss_or_end"] for e in rr), "with_any_rent": sum(1 for e in rr if e["rent_until_loss_or_end"] > 0),
             "games": len(set(e["game"] for e in rr)), "held_to_game_end": sum(1 for e in rr if e["end_reason"] == "game_end")}
out["live_by_route"] = rt
out["live_total_rent"] = sum(v["rent_until_loss_or_end"] for v in rt.values())

# cross-check episode rent against the independent flow ledger
gkeys = collections.defaultdict(set)
for k, g in group_of.items(): gkeys[g].add(k)
mismatch = 0
for e in eps:
    r2 = sum(x["amount"] for x in flows if x["kind"] == "paid_rent" and x["game"] == e["game"] and x["to"] == e["player_id"]
             and x["space_key"] in gkeys[e["group"]] and e["settlement_end_seq"] < x["seq"] < e["end_seq_exclusive"])
    if r2 != e["rent_until_loss_or_end"]: mismatch += 1
out["episode_rent_crosscheck_against_flows"] = {"episodes": len(eps), "mismatches": mismatch}

# trade-completed groups by configuration
tr = [e for e in live if e["route"] == "trade"]
tm = {}
cause = {(r["game"], r["player"], r["group"]): r["cause"] for r in fmw["rows"]}
for m in MODELS:
    rr = [e for e in tr if e["model"] == m]
    tm[m] = {"groups": len(rr), "built_first_window": sum(1 for e in rr if e["built_first_management"]),
             "ever_built": sum(1 for e in rr if e["first_build_turn"] is not None),
             "rent_until_loss_or_end": sum(e["rent_until_loss_or_end"] for e in rr), "with_any_rent": sum(1 for e in rr if e["rent_until_loss_or_end"] > 0),
             "median_rent": st.median(e["rent_until_loss_or_end"] for e in rr), "by_eventual_winner": sum(e["win"] for e in rr),
             "games": len(set(e["game"] for e in rr)),
             "unbuilt_causes": dict(C(cause[(e["game"], e["player_id"], e["group"])] for e in rr if not e["built_first_management"]))}
out["trade_groups_by_configuration"] = tm
out["trade_groups_total"] = {"groups": len(tr), "built_first_window": sum(1 for e in tr if e["built_first_management"]), "ever_built": sum(1 for e in tr if e["first_build_turn"] is not None),
                             "rent": sum(e["rent_until_loss_or_end"] for e in tr), "with_any_rent": sum(1 for e in tr if e["rent_until_loss_or_end"] > 0), "by_eventual_winner": sum(e["win"] for e in tr),
                             "elapsed_to_management": dict(sorted(C(e["elapsed_to_management"] for e in tr).items())),
                             "built_x_rent": {"built_rent": sum(e["rent_until_loss_or_end"] for e in tr if e["built_first_management"]), "unbuilt_rent": sum(e["rent_until_loss_or_end"] for e in tr if not e["built_first_management"]),
                                              "unbuilt_ever_built_later": sum(1 for e in tr if not e["built_first_management"] and e["first_build_turn"] is not None)}}
out["trade_groups_by_game_winner_flag"] = {str(g): {"winner": sum(1 for e in tr if e["game"] == g and e["win"]), "others": sum(1 for e in tr if e["game"] == g and not e["win"])} for g in range(1, 21)}

# ---- 2. terms of the settlements that completed a group --------------------
acc = [r for r in offers if r["response"] == "accept_trade"]
terms = []
for r in acc:
    for role, pid, model, groups, sign in (("author", r["author"], r["author_model"], r["author_new_groups"], -1), ("recipient", r["recipient"], r["recipient_model"], r["recipient_new_groups"], +1)):
        for g in groups:
            net_received = sign * r["net_cash_author_to_recipient"]  # cash received by this side (negative = paid)
            interest = r[f"{role}_interest_if_accepted"]
            cash_after = r[f"{role}_cash_if_accepted"]
            c = cause.get((r["game"], pid, g))
            terms.append({"game": r["game"], "decision": r["decision"], "player": pid, "model": model, "group": g, "role": role,
                          "net_cash_paid": -net_received, "interest": interest, "cash_after": cash_after, "house_cost": house_cost[g],
                          "cash_after_covers_one_house": cash_after >= house_cost[g], "cash_after_covers_house_each": cash_after >= house_cost[g] * len(gkeys[g]),
                          "first_window": c, "both_sides_complete": bool(r["author_new_groups"]) and bool(r["recipient_new_groups"])})
out["completing_settlement_terms_n"] = len(terms)
out["completing_settlement_terms_unmatched"] = sum(1 for t in terms if t["first_window"] is None)
def summ(tt):
    if not tt: return {"n": 0}
    return {"n": len(tt), "median_net_cash_paid": st.median(t["net_cash_paid"] for t in tt), "paid_cash": sum(1 for t in tt if t["net_cash_paid"] > 0), "received_cash": sum(1 for t in tt if t["net_cash_paid"] < 0),
            "median_cash_after": st.median(t["cash_after"] for t in tt), "cash_after_below_one_house": sum(1 for t in tt if not t["cash_after_covers_one_house"]),
            "cash_after_below_house_each": sum(1 for t in tt if not t["cash_after_covers_house_each"])}
out["completing_terms_by_configuration"] = {m: summ([t for t in terms if t["model"] == m]) for m in MODELS}
out["completing_terms_by_first_window"] = {c: summ([t for t in terms if t["first_window"] == c]) for c in fmw["causes"]}
out["completing_terms_all"] = summ(terms)
out["completing_terms_built_vs_not"] = {"built": summ([t for t in terms if t["first_window"] == "built"]), "not_built": summ([t for t in terms if t["first_window"] != "built"])}
out["never_legal_rows"] = [t for t in terms if t["first_window"] == "never_legal_in_window"]
out["completing_terms_rows"] = terms

# ---- 3. eliminations -------------------------------------------------------
cr = {(x["game"], x["decision_id"].split("-dec-")[1]): x for x in cert["results"] if x["kind"] == "elimination"}
est_c = [x for x in flows if x["kind"] in ("estate_cash", "estate_deed")]
el_rows = []
for g in range(1, 21):
    ge = sorted([e for e in elims if e["game"] == g], key=lambda e: e["elimination_event_seq"])
    for i, e in enumerate(ge, 1):
        recips = C(x["to_model"] for x in est_c if x["game"] == g and x["from"] == e["player"] and x.get("elimination_index") == i)
        ded = sum(1 for x in est_c if x["kind"] == "estate_deed" and x["game"] == g and x["from"] == e["player"] and x.get("elimination_index") == i)
        c = cr[(g, e["decision"].split("-")[1])]
        el_rows.append({"game": g, "order": i, "debtor": e["model"], "kind": e["elimination"], "owed": e["owed"], "cash": e["cash"], "full_bound": e["full"],
                        "certificate": c["certificate"], "estate_recipients": dict(recips), "deeds_transferred": ded, "winner": winner[g]})
out["elimination_rows"] = el_rows
out["eliminations_by_debtor"] = dict(C(r["debtor"] for r in el_rows))
out["eliminations_by_debtor_order"] = {m: dict(sorted(C(r["order"] for r in el_rows if r["debtor"] == m).items())) for m in MODELS}
out["eliminations_by_certificate"] = dict(C(r["certificate"] for r in el_rows))
out["eliminations_kind"] = dict(C(r["kind"] for r in el_rows))
out["eliminations_bound_below_debt"] = sum(1 for r in el_rows if r["full_bound"] < r["owed"])
short = [r["owed"] - r["full_bound"] for r in el_rows if r["full_bound"] < r["owed"]]
out["shortfall_vs_bound"] = {"n": len(short), "median": st.median(short), "min": min(short), "max": max(short), "under_100": sum(1 for s in short if s < 100)}
out["debt_size"] = {"median": st.median(r["owed"] for r in el_rows), "min": min(r["owed"] for r in el_rows), "max": max(r["owed"] for r in el_rows)}
def cred(r):
    k = [m for m in r["estate_recipients"]]
    return k[0] if len(k) == 1 else ("none_recorded" if not k else "multiple")
for r in el_rows: r["creditor"] = cred(r)
out["estate_recipient_patterns"] = dict(C(r["creditor"] for r in el_rows))
out["winner_is_estate_recipient_by_order"] = {str(o): {"winner": sum(1 for r in el_rows if r["order"] == o and r["creditor"] == r["winner"]), "n": sum(1 for r in el_rows if r["order"] == o),
                                                       "no_player_recipient": sum(1 for r in el_rows if r["order"] == o and r["creditor"] == "none_recorded")} for o in (1, 2, 3)}
both12 = 0
for g in range(1, 21):
    a = [r for r in el_rows if r["game"] == g and r["order"] in (1, 2)]
    if all(r["creditor"] == winner[g] for r in a): both12 += 1
out["games_winner_received_both_nonterminal_estates"] = both12
out["games_winner_received_first_estate"] = sum(1 for r in el_rows if r["order"] == 1 and r["creditor"] == r["winner"])
out["games_winner_received_no_nonterminal_estate"] = sum(1 for g in range(1, 21) if not any(r["creditor"] == winner[g] for r in el_rows if r["game"] == g and r["order"] in (1, 2)))

# ---- 4. first completed group per game -------------------------------------
fc = []
for g in range(1, 21):
    ge = sorted([e for e in eps if e["game"] == g], key=lambda e: e["acquisition_seq"])
    f = ge[0]
    fc.append({"game": g, "block": BLOCK(g), "route": f["route"], "model": f["model"], "player": f["player_id"], "group": f["group"], "turn": f["acquisition_turn"],
               "built_first_window": f["built_first_management"], "first_window_cause": cause.get((g, f["player_id"], f["group"])), "winner": winner[g], "first_completer_won": f["model"] == winner[g]})
out["first_completion_rows"] = fc
out["first_completer_won"] = sum(r["first_completer_won"] for r in fc)
out["first_completion_route"] = dict(C(r["route"] for r in fc))
out["first_completer_built_x_won"] = {f"built={b}|won={w}": n for (b, w), n in C((r["built_first_window"], r["first_completer_won"]) for r in fc).items()}

# ---- 5. spending units -----------------------------------------------------
out["spending_units"] = {"n": len(units), "spend": sum(u["spend"] for u in units), "rent_whole": sum(u["paid_developed_rent_whole_game"] for u in units),
                         "rent_post": sum(u["paid_developed_rent_after_first_own_spend"] for u in units), "zero_rent": sum(1 for u in units if u["paid_developed_rent_whole_game"] == 0),
                         "winner_units": sum(1 for u in units if u["winner"]), "sale_proceeds": sum(u["sale_proceeds"] for u in units),
                         "by_configuration": {m: {"units": sum(1 for u in units if u["configuration"] == m), "spend": sum(u["spend"] for u in units if u["configuration"] == m),
                                                  "rent_whole": sum(u["paid_developed_rent_whole_game"] for u in units if u["configuration"] == m),
                                                  "sale_proceeds": sum(u["sale_proceeds"] for u in units if u["configuration"] == m),
                                                  "zero_rent": sum(1 for u in units if u["configuration"] == m and u["paid_developed_rent_whole_game"] == 0)} for m in MODELS}}
(HERE / "data" / "economy_retabulation.json").write_text(json.dumps(out, indent=1))
show = {k: v for k, v in out.items() if k not in ("completing_terms_rows", "elimination_rows", "inputs_sha256", "trade_groups_by_game_winner_flag")}
print(json.dumps(show, indent=1))
