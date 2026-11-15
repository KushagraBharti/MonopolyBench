"""Opus xhigh final-review checks.

Read-only re-tabulation of existing ledgers, original saved-game records and
engine source. No engine execution, game, replay or model call. Run from the
repository root:

    python3 -I docs/research_raw/paper_rewrite_2026-11-10/final_review/opus/checks/opus_final_checks.py
"""
import collections as C
import glob
import hashlib
import json
import math
import re
import statistics as st
import sys

PKG = "docs/research_raw/paper_rewrite_2026-11-10"
INT = PKG + "/integrated"
SG = "saved_games"
out = {"scope": "Read-only re-tabulation of existing ledgers, original records and engine source; no execution."}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# --- pins -------------------------------------------------------------------
pins = json.load(open(INT + "/qa/integrated_file_hashes.json"))["files"]
bad = [p for p, h in pins.items() if sha(INT + "/" + p) != h]
out["pins"] = {"n": len(pins), "mismatches": bad, "pdf": sha(INT + "/manuscript.pdf")}

offers = json.load(open(INT + "/data/agenda_offers.json"))
cohort = {c["game"]: c for c in json.load(open(INT + "/data/t01_cohort.json"))}
L = [r for r in offers if r["accept_available"]]

# --- counters (OPF-09) ------------------------------------------------------
by = C.defaultdict(dict)
for r in offers:
    by[r["thread_id"]][r["exchange_index"]] = r
cnt = C.defaultdict(C.Counter)
med = []
for r in offers:
    if r["response"] != "counter_trade" or not r["accept_available"]:
        continue
    n = by[r["thread_id"]][r["exchange_index"] + 1]
    assert n["author"] == r["recipient"]
    c = r["completion_cell"]
    req = set(r["request"]["properties"])
    retain = bool(req) and req <= set(n["offer"]["properties"])
    pres = bool(r["author_new_groups"]) and set(r["author_new_groups"]) <= set(n["recipient_new_groups"])
    only = pres and not n["author_new_groups"]
    same = (set(n["offer"]["properties"]) == req and set(n["request"]["properties"]) == set(r["offer"]["properties"])
            and n["offer"]["get_out_of_jail_cards"] == r["request"]["get_out_of_jail_cards"]
            and n["request"]["get_out_of_jail_cards"] == r["offer"]["get_out_of_jail_cards"])
    inc = -n["net_cash_author_to_recipient"] > r["net_cash_author_to_recipient"]
    k = cnt[c]
    k["n"] += 1
    k["req>=1"] += bool(req)
    k["retain_all_requested"] += retain
    k["preserve_author_completion"] += pres
    k["retain_xor_preserve"] += (retain != pres) if c == "author_only" else 0
    k["only_author"] += only
    k["only_author_cash_up"] += only and inc
    k["req_same_noncash_cash_up"] += bool(req) and same and inc
    if only and inc:
        med.append(-n["net_cash_author_to_recipient"] - r["net_cash_author_to_recipient"])
out["counters"] = {c: dict(v) for c, v in cnt.items()}
out["counters"]["author_only_median_cash_increase"] = st.median(med)

# --- stage/seed consistency, initiation, settlements, prices ---------------
blk = lambda g: (g - 1) // 4 + 1
rate = lambda rs, x: sum(r["response"] == x for r in rs) / len(rs)
cons = {}
for resp, better in (("reject_trade", 1), ("accept_trade", -1)):
    b = sum(better * (rate([r for r in L if blk(r["game"]) == i and r["completion_cell"] == "author_only"], resp)
                      - rate([r for r in L if blk(r["game"]) == i and r["completion_cell"] == "recipient_only"], resp)) > 0
            for i in range(1, 6))
    gs = [g for g in range(1, 21) if any(r["game"] == g and r["completion_cell"] == "author_only" for r in L)
          and any(r["game"] == g and r["completion_cell"] == "recipient_only" for r in L)]
    gh = sum(better * (rate([r for r in L if r["game"] == g and r["completion_cell"] == "author_only"], resp)
                       - rate([r for r in L if r["game"] == g and r["completion_cell"] == "recipient_only"], resp)) > 0 for g in gs)
    cons[resp] = {"blocks": b, "games": gh, "games_with_both": len(gs)}
out["contrast_consistency"] = cons
out["initiation"] = dict(C.Counter(r["author_model"] for r in offers if r["exchange_index"] == 0))

acc = [r for r in offers if r["response"] == "accept_trade"]
rows = []
for r in acc:
    x = r["net_cash_author_to_recipient"]
    if x:
        s, b = ("recipient", "author") if x > 0 else ("author", "recipient")
        rows.append((r, s, b, r[s + "_cash_before"]))
pc = [x for x in rows if x[0][x[2] + "_new_groups"]]
low = [x for x in pc if x[3] < 100]
out["settlement_cash"] = {
    "payer_completing": len(pc), "median_seller_cash": st.median(x[3] for x in pc), "below100": len(low),
    "neither": len([x for x in rows if x[0]["completion_cell"] == "neither"]),
    "neither_median": st.median(x[3] for x in rows if x[0]["completion_cell"] == "neither"),
    "low_by_model": dict(C.Counter(x[0][x[1] + "_model"] for x in low)),
    "low_winners": sum(cohort[x[0]["game"]]["winner"] == x[0][x[1] + "_model"] for x in low),
    "thresholds": {t: [sum(bool(x[0][x[2] + "_new_groups"]) for x in rows if x[3] < t), sum(x[3] < t for x in rows)] for t in (50, 100, 150, 200)},
}
aoa = [r for r in L if r["completion_cell"] == "author_only" and r["response"] == "accept_trade"]
out["author_only_accepts"] = {
    "n": len(aoa), "later": sum(r["exchange_index"] > 0 for r in aoa),
    "recipient_below_100": sum(r["recipient_cash_before"] < 100 for r in aoa),
    "opus": sum(r["recipient_model"] == "Opus" for r in aoa),
    "opening": [(r["game"], r["decision"], r["recipient_model"], r["response_condition"]) for r in aoa if r["exchange_index"] == 0],
}
rej = [r for r in L if r["completion_cell"] in ("recipient_only", "both") and r["response"] == "reject_trade"]
out["reason_population"] = {"n": len(rej), "by_recipient": dict(C.Counter(r["recipient_model"] for r in rej)),
                            "top_games": C.Counter(r["game"] for r in rej).most_common(2)}

board = json.load(open("contracts/data/board.json"))
norm = lambda s: re.sub(r"[^A-Z]", "", s.upper())
bynorm = {norm(s["name"]): s["price"] for s in board["spaces"] if s.get("price")}
price = lambda k: bynorm[norm(k)]
isbid = lambda r: (r["offer"]["cash"] > 0 and not r["offer"]["properties"] and r["offer"]["get_out_of_jail_cards"] == 0
                   and r["request"]["properties"] and r["request"]["cash"] == 0 and r["request"]["get_out_of_jail_cards"] == 0)
isask = lambda r: (r["request"]["cash"] > 0 and not r["request"]["properties"] and r["request"]["get_out_of_jail_cards"] == 0
                   and r["offer"]["properties"] and r["offer"]["cash"] == 0 and r["offer"]["get_out_of_jail_cards"] == 0)
ratio = lambda r: (r["offer"]["cash"] / sum(map(price, r["request"]["properties"])) if isbid(r)
                   else r["request"]["cash"] / sum(map(price, r["offer"]["properties"])))
cuts = {"All": lambda r: True,
        "Unmortgaged": lambda r: r["author_interest_if_accepted"] == 0 and r["recipient_interest_if_accepted"] == 0,
        "Opening": lambda r: r["exchange_index"] == 0, "Later": lambda r: r["exchange_index"] > 0}
pt = {}
for name, f in cuts.items():
    pt[name] = []
    for kind, cell in (("bid", "author_only"), ("bid", "neither"), ("ask", "recipient_only"), ("ask", "neither")):
        rs = [r for r in L if f(r) and (isbid(r) if kind == "bid" else isask(r)) and r["completion_cell"] == cell]
        pt[name].append(f"{st.median(map(ratio, rs)):.3f} ({len(rs)})")
out["price_table"] = pt

# --- first windows, episodes (OPF-04) ---------------------------------------
fw = json.load(open(INT + "/data/first_management_windows.json"))
out["first_window_summary"] = fw["summary"]
ep = [json.loads(l) for l in open("docs/research_raw/paper_phase1_2026-10-28/sol/group_episodes.jsonl")]
win = lambda r: cohort[r["game"]]["winner"] == r["model"]
out["routes"] = {rt: {"n": len(rs), "winner": sum(map(win, rs)), "rent_pos": sum(r["rent_until_loss_or_end"] > 0 for r in rs),
                      "rent": sum(r["rent_until_loss_or_end"] for r in rs),
                      "access": dict(C.Counter(r["access_status"] for r in rs))}
                 for rt in sorted({r["route"] for r in ep}) for rs in [[r for r in ep if r["route"] == rt]]}

# --- original records: estates, triggers, memory, prompt census ------------
grp = {s["index"]: s.get("group") for s in board["spaces"]}
est = C.Counter()
trig = []
mem = C.Counter()
census = C.defaultdict(C.Counter)
ECON = {"price", "rent", "house_cost", "group", "group_progress", "mortgage_value", "unmortgage_cost", "redemption", "cost"}


def allkeys(x, acc):
    if isinstance(x, dict):
        for k, v in x.items():
            acc.add(k)
            allkeys(v, acc)
    elif isinstance(x, list):
        for v in x:
            allkeys(v, acc)


for gd in sorted(glob.glob(SG + "/railway-research-*/game-[0-9][0-9]-*")):
    g = int(re.search(r"game-(\d\d)-", gd).group(1))
    run = gd + "/run/"
    pls = json.load(open(run + "players.json"))["players"]
    model = {p["player_id"]: ("Sol" if "gpt" in p["name"] else "Gemini" if "gemini" in p["name"]
                              else "Opus" if "opus" in p["name"] else "Grok") for p in pls}
    ev = [json.loads(l) for l in open(run + "events.jsonl")]
    houses, hotel, bks = C.Counter(), set(), []
    for i, r in enumerate(ev):
        t, p = r["type"], r["payload"]
        if t == "HOUSE_BUILT":
            houses[p["space_index"]] += p.get("count", 1)
        elif t == "HOUSE_SOLD":
            houses[p["space_index"]] -= p.get("count", 1)
        elif t == "HOTEL_BUILT":
            hotel.add(p["space_index"]); houses[p["space_index"]] = 0
        elif t == "HOTEL_SOLD":
            hotel.discard(p["space_index"]); houses[p["space_index"]] = 4
        if t == "CASH_CHANGED" and p.get("reason") == "BANKRUPTCY":
            debtor = p["player_id"]
            cred, deeds = None, 0
            for j in range(max(0, i - 3), i):
                q = ev[j]["payload"]
                if ev[j]["type"] == "CASH_CHANGED" and q.get("reason") == "BANKRUPTCY_CASH" and q["delta"] > 0:
                    cred = q["player_id"]
            j = i + 1
            while j < len(ev) and ev[j]["type"] == "PROPERTY_PURCHASED" and ev[j]["payload"].get("price") == 0:
                cred = ev[j]["payload"]["player_id"]; deeds += 1; j += 1
            sp = next((ev[k]["payload"]["to"] for k in range(i - 1, -1, -1)
                       if ev[k]["type"] == "PLAYER_MOVED" and ev[k]["actor"].get("player_id") == debtor), None)
            dev = grp.get(sp) not in (None, "RAILROAD", "UTILITY") and (sp in hotel or houses[sp] > 0)
            bks.append((cred, deeds, dev, sp))
    for k, (cred, deeds, dev, sp) in enumerate(bks):
        key = "terminal" if k == len(bks) - 1 else "nonterminal"
        cw = cred is not None and model[cred] == cohort[g]["winner"]
        est[key + "_elims"] += 1; est[key + "_deeds"] += deeds
        est[key + "_winner_creditor"] += cw; est[key + "_winner_deeds"] += deeds if cw else 0
        est[key + "_bank"] += cred is None
        est[key + "_developed_trigger"] += dev
        est["first_to_winner"] += (k == 0 and cw)
        if not dev:
            trig.append((g, k, sp))
    est["all_three_to_winner"] += all(c is not None and model[c] == cohort[g]["winner"] for c, *_ in bks)
    for l in open(run + "decisions.jsonl"):
        r = json.loads(l)
        if r["phase"] != "decision_started":
            continue
        pp = r.get("prompt_payload") or {}
        gs = dict(pp.get("game_state") or {})
        notes = [(m.get("thought") or "").strip() for m in gs.pop("memory", {}).get("your_private_thoughts_last_10", [])]
        ks = set()
        allkeys(gs, ks); allkeys(pp.get("action_state") or {}, ks)
        dt = pp.get("action_state", {}).get("decision_type", "?")
        census[dt]["n"] += 1
        census[dt]["with_econ_field"] += bool(ks & ECON)
        if "opus" in r["player_name"]:
            real = [t for t in notes if t and t.lower() != "fallback"]
            mem["empty" if not notes else "only_fallback" if not real else "has_real"] += 1
out["estates"] = dict(est)
out["non_developed_triggers"] = trig
out["opus_memory"] = dict(mem)
out["prompt_econ_field_census"] = {k: dict(v) for k, v in census.items()}

# --- focal original fields ---------------------------------------------------
def resolved(gglob, n):
    run = glob.glob(SG + "/" + gglob)[0] + "/run/"
    for l in open(run + "decisions.jsonl"):
        r = json.loads(l)
        if r["phase"] == "decision_resolved" and int(r["decision_id"][-6:]) == n:
            return r


def started(gglob, n):
    run = glob.glob(SG + "/" + gglob)[0] + "/run/"
    for l in open(run + "decisions.jsonl"):
        r = json.loads(l)
        if r["phase"] == "decision_started" and int(r["decision_id"][-6:]) == n:
            return r["prompt_payload"]


g7 = started("railway-research-12-games-2026-10-25/game-07-*", 339)
out["g7_d339_menu"] = {"options": g7["action_state"]["scenario"]["options"], "available": g7["action_state"]["available_actions"],
                       "bank": g7["game_state"]["bank"], "cash": g7["game_state"]["you"]["cash"],
                       "built": [h for h in g7["game_state"]["you"]["holdings"]["owned"] if h["houses"] or h["hotel"]]}
out["g12_d249_note"] = resolved("railway-research-12-games-2026-10-25/game-12-*", 249)["final_action"]["private_thought"]
g3 = resolved("railway-research-12-games-2026-10-25/game-03-*", 176)
out["g3_d176"] = {"public": g3["final_action"]["public_message"], "private": g3["final_action"].get("private_thought"),
                  "selected_attempt_content": g3["attempts"][-1].get("assistant_content")}
out["g20_sol_d95_note"] = resolved("railway-research-8-games-2026-10-26/game-20-*", 95)["final_action"]["private_thought"]
out["g20_opus_offers_to_grok"] = [(n, resolved("railway-research-8-games-2026-10-26/game-20-*", n)["final_action"]["public_message"])
                                  for n in (129, 130, 156, 157, 158, 159, 160)]
g1 = started("railway-research-12-games-2026-10-25/game-01-*", 298)
out["g1_d298_menu"] = g1["action_state"]["scenario"]["options"]

# --- engine source (redemption, sale menu) ----------------------------------
src = open("python/packages/engine/src/monopoly_engine/engine.py").read()
out["engine_unmortgage_cost_line"] = re.search(r"def _unmortgage_cost.*?return [^\n]+", src, re.S).group(0)
out["redemption_overcharged_principals"] = [p for p in (30, 50, 60, 70, 75, 80, 90, 100, 110, 120, 130, 140, 150, 160, 175, 200)
                                            if math.ceil(p * 1.1) != -(-p * 11 // 10)]
out["engine_sell_menu_hotel_rule"] = "houses_remaining < HOUSE_LIMIT" in src and "_sellable_building_space_indices" in src

json.dump(out, sys.stdout, indent=1, default=str)
