"""Opus cross-review checks. Existing-record arithmetic only.

Reads frozen draft ledgers (two independent 920-row offer rebuilds that agree),
the board contract, retained completion/dyad/debt ledgers, and canonical
decisions.jsonl files (read-only) for the paid-debt channel check.
Imports no engine or model code. Run from the repository root:

    python3 -I docs/research_raw/paper_revision_2026-11-11/reviews/opus/tools/cross_checks.py
"""
import collections, hashlib, json, pathlib, re, statistics, sys

ROOT = pathlib.Path.cwd()
REV = ROOT / "docs/research_raw/paper_revision_2026-11-11"
FD = REV / "full_drafts"
OUT = REV / "reviews/opus/data"
INPUTS = {
    "opus_offers": FD / "opus/data/offers_rebuilt.json",
    "fable_offers": FD / "fable_5_2/data/a2_offer_ledger.json",
    "board": ROOT / "contracts/data/board.json",
    "completion": FD / "opus/data/completion_episodes.json",
    "dyads": FD / "fable_5_2/data/a6_dyads.json",
    "conversion": FD / "fable_5_2/data/a7_conversion.json",
    "fable_debt": FD / "fable_5_2/data/a4_debt_episodes.json",
    "astra_debt": FD / "astra/data/liquidation_episodes.json",
    "opus_debt": FD / "opus/data/debt_episodes.json",
}
sha = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in INPUTS.items()}
L = lambda k: json.loads(INPUTS[k].read_text())
offers = L("opus_offers"); foff = L("fable_offers"); board = L("board")
res = {"inputs": {k: str(p.relative_to(ROOT)) for k, p in INPUTS.items()}, "sha256": sha}

# ---------- 0. ledger agreement on fields used here
fkey = {(r["game"], r["decision"]): r for r in foff}
mism = collections.Counter()
for r in offers:
    f = fkey[(r["game"], r["decision"])]
    if r["recipient_cash"] != f["recipient_cash_before"]: mism["recipient_cash"] += 1
    if r["author_cash"] != f["author_cash_before"]: mism["author_cash"] += 1
    if r["response"] != f["response"]: mism["response"] += 1
    if r["opening"] != f["opening"]: mism["opening"] += 1
    if r["cell"].lower().replace(" ", "-").replace("-only", "_only") != f["completion_cell"].replace("-", "_"):
        mism["cell"] += 1
res["ledger_field_mismatches_opus_vs_fable"] = dict(mism)

# ---------- helpers
spaces = {s.get("name"): s for s in board["spaces"]}
key2space = {}
for s in board["spaces"]:
    if s.get("kind") == "PROPERTY":
        key2space[s["name"].upper().replace(" ", "_").replace(".", "").replace("&", "AND")] = s
group_size = collections.Counter(s["group"] for s in board["spaces"] if s.get("kind") == "PROPERTY")
house_cost = board["house_cost_by_group"]

def gkey(prop):
    s = key2space.get(prop)
    return s["group"] if s else None

legal = [r for r in offers if r["accept_legal"]]
R = lambda r: r["response"].split("_")[0]  # accept / counter / reject
def tally(rows):
    c = collections.Counter(R(r) for r in rows)
    return {"n": len(rows), "accept": c["accept"], "counter": c["counter"], "reject": c["reject"]}
def rej(rows):
    t = tally(rows); return f'{t["reject"]}/{t["n"]}'
def pct(a, b): return round(100 * a / b, 1) if b else None
asks_deed = lambda r: len(r["author_asks"]["properties"]) > 0
def band(c):
    return "lt100" if c < 100 else ("100-299" if c < 300 else "300plus")
models = ["Sol", "Gemini", "Opus", "Grok"]

# ---------- A. opening/later contrast with composition-matched baseline
A = {}
for stage in ("opening", "later"):
    rows = [r for r in legal if r["opening"] == (stage == "opening")]
    ao = [r for r in rows if r["cell"] == "Author only"]
    ne = [r for r in rows if r["cell"] == "Neither"]
    ne_d = [r for r in ne if asks_deed(r)]
    ne_nod = [r for r in ne if not asks_deed(r)]
    ro = [r for r in rows if r["cell"] == "Recipient only"]
    A[stage] = {"author_only": tally(ao), "neither_all": tally(ne), "neither_requests_deed": tally(ne_d),
                "neither_no_deed_request": tally(ne_nod), "recipient_only": tally(ro)}
    by = {}
    for m in models:
        by[m] = {"author_only": rej([r for r in ao if r["recipient_model"] == m]),
                 "neither_requests_deed": rej([r for r in ne_d if r["recipient_model"] == m])}
    A[stage]["by_recipient"] = by
    blk = {}
    for b in range(1, 6):
        g = set(range(4 * b - 3, 4 * b + 1))
        a1 = [r for r in ao if r["game"] in g]; n1 = [r for r in ne_d if r["game"] in g]
        blk[b] = {"author_only": rej(a1), "neither_requests_deed": rej(n1),
                  "diff_pts": round(pct(tally(a1)["reject"], len(a1)) - pct(tally(n1)["reject"], len(n1)), 1)}
    A[stage]["by_block"] = blk
res["A_rejection_composition"] = A

# ---------- B. holder cash: completion requests vs other deed requests, within system and stage
B = {"definition": "holder = recipient of an acceptance-legal offer that requests >=1 deed from it; cash = recipient's delivered cash"}
cells = collections.defaultdict(list)
for r in legal:
    if not asks_deed(r): continue
    kind = "completion_request" if r["cell"] == "Author only" else ("other_deed_request" if r["cell"] == "Neither" else None)
    if not kind: continue
    cells[(kind, r["recipient_model"], "open" if r["opening"] else "later", band(r["recipient_cash"]))].append(r)
tab = {}
for kind in ("completion_request", "other_deed_request"):
    for m in models + ["All", "All_but_Opus"]:
        for st in ("open", "later", "both"):
            for bd in ("lt100", "100-299", "300plus"):
                rows = []
                for (k, mm, s, b), v in cells.items():
                    if k != kind or b != bd: continue
                    if st != "both" and s != st: continue
                    if m == "All" or (m == "All_but_Opus" and mm != "Opus") or mm == m: rows += v
                t = tally(rows)
                tab[f"{kind}|{m}|{st}|{bd}"] = t
B["cells"] = tab
def rr(kind, m, st, bd):
    t = tab[f"{kind}|{m}|{st}|{bd}"]; return t["reject"], t["n"]
summary = {}
for m in models + ["All", "All_but_Opus"]:
    row = {}
    for kind in ("completion_request", "other_deed_request"):
        lo = rr(kind, m, "both", "lt100"); hi = rr(kind, m, "both", "300plus")
        row[kind] = {"lt100": f"{lo[0]}/{lo[1]}", "300plus": f"{hi[0]}/{hi[1]}",
                     "lt100_pct": pct(*lo), "300plus_pct": pct(*hi)}
    cr, od = row["completion_request"], row["other_deed_request"]
    if None not in (cr["lt100_pct"], cr["300plus_pct"], od["lt100_pct"], od["300plus_pct"]):
        row["completion_minus_other_at_300plus"] = round(cr["300plus_pct"] - od["300plus_pct"], 1)
        row["completion_minus_other_at_lt100"] = round(cr["lt100_pct"] - od["lt100_pct"], 1)
    summary[m] = row
B["summary_by_recipient"] = summary
# who receives low-cash completion requests
cr_low = [r for r in legal if r["cell"] == "Author only" and r["recipient_cash"] < 100]
B["low_cash_completion_requests_by_recipient"] = dict(collections.Counter(r["recipient_model"] for r in cr_low))
B["low_cash_completion_requests_by_author"] = dict(collections.Counter(r["author_model"] for r in cr_low))
# targeting: share of completion requests vs other deed requests arriving at <100 holders, by recipient model
tgt = {}
for m in models + ["All", "All_but_Opus"]:
    sel = lambda r: m == "All" or (m == "All_but_Opus" and r["recipient_model"] != "Opus") or r["recipient_model"] == m
    crq = [r for r in legal if r["cell"] == "Author only" and sel(r)]
    odq = [r for r in legal if r["cell"] == "Neither" and asks_deed(r) and sel(r)]
    tgt[m] = {"completion_requests_to_lt100": f'{sum(r["recipient_cash"]<100 for r in crq)}/{len(crq)}',
              "other_deed_requests_to_lt100": f'{sum(r["recipient_cash"]<100 for r in odq)}/{len(odq)}'}
B["targeting"] = tgt
# net cash offered to holder, by band (completion requests): does the offer itself differ?
nc = collections.defaultdict(list)
for r in legal:
    if r["cell"] != "Author only": continue
    net = r["recipient_cash_after"] - r["recipient_cash"]
    nc[band(r["recipient_cash"])].append(net)
B["completion_request_net_cash_to_holder_median"] = {k: statistics.median(v) for k, v in nc.items()}
res["B_holder_cash"] = B

# ---------- C. holder cash jointly with author's post-trade building capacity (completion requests)
C = collections.defaultdict(lambda: collections.Counter())
capdef = "full = author cash after >= house cost x deeds in newly completed group; one = >= one house; none = less"
for r in legal:
    if r["cell"] != "Author only": continue
    gs = r["author_new"]
    if not gs: continue
    g = gs[0]
    hc = house_cost.get(g) or house_cost.get(g.upper())
    if hc is None: continue
    ca = r["author_cash_after"]
    cap = "full" if ca >= hc * group_size[g] else ("one" if ca >= hc else "none")
    hb = "lt100" if r["recipient_cash"] < 100 else ("100-299" if r["recipient_cash"] < 300 else "300plus")
    for who in ("All", "All_but_Opus"):
        if who == "All_but_Opus" and r["recipient_model"] == "Opus": continue
        C[f"{who}|{hb}|{cap}"][R(r)] += 1
res["C_holder_cash_by_rival_capacity"] = {"definition": capdef,
    "cells": {k: {"n": sum(v.values()), "reject": v["reject"], "counter": v["counter"], "accept": v["accept"]} for k, v in sorted(C.items())}}

# ---------- D. within-pair release sequences
dy = L("dyads")
D = {}
one_sided_later = []
for p in dy:
    if not p["settled"]: continue
    reqs = sorted(p["requests"], key=lambda q: (q["turn"], q["decision"]))
    acc = [q for q in reqs if q["response"] == "accept_trade"]
    if not acc: continue
    sale = acc[-1]
    if sale["cell"] not in ("author_only", "recipient_only"): continue
    prior = [q for q in reqs if q["turn"] < sale["turn"] and q["response"] in ("reject_trade", "counter_trade")]
    holder_declines = [q for q in prior if q.get("written_by") == "completer"]
    if holder_declines:
        first = holder_declines[0]
        one_sided_later.append({"game": p["game"], "group": p["group"], "holder": p["holder_model"], "buyer": p["completer_model"],
                                "cash_at_first_holder_refusal": first["holder_cash"], "cash_at_sale": sale["holder_cash"],
                                "turns_between": sale["turn"] - first["turn"]})
D["rows_holder_refused_then_sold"] = one_sided_later
D["n"] = len(one_sided_later)
D["lower_at_sale"] = sum(r["cash_at_sale"] < r["cash_at_first_holder_refusal"] for r in one_sided_later)
D["under100_at_sale"] = sum(r["cash_at_sale"] < 100 for r in one_sided_later)
D["under100_at_sale_excluding_opus_holders"] = f'{sum(r["cash_at_sale"] < 100 for r in one_sided_later if r["holder"] != "Opus")}/{sum(r["holder"] != "Opus" for r in one_sided_later)}'
D["games"] = sorted({r["game"] for r in one_sided_later})
res["D_pairs"] = D

# ---------- E. seller build/win split conditioned on holding a complete group at the sale
conv = L("conversion")["seller_conversion"]["rows"]
comp = L("completion")["episodes"]
model_of = {}
for r in offers:
    model_of[(r["game"], r["author_model"])] = r["author"]; model_of[(r["game"], r["recipient_model"])] = r["recipient"]
E_rows = []
for s in conv:
    pid = model_of.get((s["game"], s["seller_model"]))
    holds = [e for e in comp if e["game"] == s["game"] and e["owner"] == pid and e["start_turn"] <= s["turn"]
             and (e["end_turn"] is None or e["end_turn"] >= s["turn"]) and not e.get("terminal")]
    built = s["houses_built_within"]["8"] > 0
    E_rows.append({"game": s["game"], "seller": s["seller_model"], "seller_pid": pid, "turn": s["turn"], "seller_cash": s["seller_cash"],
                   "held_complete_group": bool(holds), "held_groups": sorted({e["color"] for e in holds}),
                   "built_within_8": built, "seller_won": s["seller_won"], "seller_building_levels_at_sale": s["seller_building_levels_at_sale"]})
def split(rows):
    out = {}
    for b in (True, False):
        sub = [r for r in rows if r["built_within_8"] == b]
        pg = {(r["game"], r["seller"]) for r in sub}
        pgw = {(r["game"], r["seller"]) for r in sub if r["seller_won"]}
        out["built" if b else "not_built"] = {"sales": len(sub), "won_sales": sum(r["seller_won"] for r in sub),
                                               "player_games": len(pg), "winning_player_games": len(pgw)}
    return out
res["E_seller_conversion"] = {
    "definition": "held_complete_group: seller owns a non-terminal completion episode spanning the sale turn (Opus completion ledger)",
    "all": split(E_rows),
    "held_complete_group": split([r for r in E_rows if r["held_complete_group"]]),
    "no_complete_group": split([r for r in E_rows if not r["held_complete_group"]]),
    "held_and_not_built_rows": [r for r in E_rows if r["held_complete_group"] and not r["built_within_8"]],
    "built_without_held_group_rows": [r for r in E_rows if not r["held_complete_group"] and r["built_within_8"]],
}

# ---------- F. same-seller/game/deed asks with both estimands (single-deed cash-for-deed asks)
F = collections.defaultdict(lambda: {"completing": [], "other": []})
for r in legal:
    ag, aa = r["author_gives"], r["author_asks"]
    if len(ag["properties"]) == 1 and ag["cash"] == 0 and ag.get("jail", 0) == 0 and not aa["properties"] and aa["cash"] > 0 and aa.get("jail", 0) == 0:
        deed = ag["properties"][0]
        if gkey(deed) is None: continue
        k = (r["game"], r["author_model"], deed)
        (F[k]["completing"] if r["recipient_new"] else F[k]["other"]).append((r["turn"], aa["cash"], r["author_cash"], r["recipient_model"]))
Frows = []
for (g, s, d), v in sorted(F.items()):
    if v["completing"] and v["other"]:
        c = sorted(v["completing"]); o = sorted(v["other"])
        mc, mo = statistics.median(x[1] for x in c), statistics.median(x[1] for x in o)
        dirm = "higher" if mc > mo else ("lower" if mc < mo else "equal")
        dirf = "higher" if c[0][1] > o[0][1] else ("lower" if c[0][1] < o[0][1] else "equal")
        Frows.append({"game": g, "seller": s, "deed": d, "completing_asks_turn_cash_sellercash": c, "other_asks_turn_cash_sellercash": o,
                      "median_direction": dirm, "first_ask_direction": dirf})
res["F_same_deed"] = {"rows": Frows,
    "median": dict(collections.Counter(r["median_direction"] for r in Frows)),
    "first_ask": dict(collections.Counter(r["first_ask_direction"] for r in Frows))}

# ---------- G. debt episodes: reconcile three ledgers; channel/default check on paid episodes
fd, ad, od = L("fable_debt"), L("astra_debt"), L("opus_debt")["episodes"]
G = {"counts": {"fable": dict(collections.Counter(e["outcome"] for e in fd)),
                "astra": dict(collections.Counter(e["outcome"] for e in ad)),
                "opus": dict(collections.Counter(e["outcome"] for e in od))}}
kf = {(e["game"], e["first_decision"]): e["outcome"] for e in fd}
ka = {(e["game"], e["first_decision"]): e["outcome"] for e in ad}
ko = {(e["game"], e["first_decision"]): e["outcome"] for e in od}
G["same_episode_keys_all_three"] = kf.keys() == ka.keys() == ko.keys()
G["outcome_disagreements"] = [k for k in kf if not (kf[k] == ka.get(k) == ko.get(k))]
paid = [e for e in fd if e["outcome"] == "paid"]
G["paid_multi_decision"] = sum(len(e["decisions"]) >= 2 for e in paid)
G["paid_fallback_any"] = sum(bool(e["fallback_any"]) for e in paid)
G["paid_actions_total"] = sum(len(e["actions"]) for e in paid)
# canonical channel check for Grok and Opus-condition paid decisions
game_dirs = {}
for base in ("saved_games/railway-research-12-games-2026-10-25", "saved_games/railway-research-8-games-2026-10-26"):
    for d in sorted(x for x in (ROOT / base).glob("game-*") if x.is_dir()):
        game_dirs[int(d.name.split("-")[1])] = d
need = collections.defaultdict(set)
for e in paid:
    for dk in e["decisions"]: need[e["game"]].add(dk)
TOOLS = ["mortgage_property", "sell_houses_or_hotel", "declare_bankruptcy", "end_turn", "unmortgage_property"]
chan = {"grok_paid_decisions": 0, "grok_content_names_action": 0, "grok_conflicts": [], "opus_paid_decisions": 0,
        "opus_paid_action_only": 0, "retry_used": 0}
dsha = {}
for g, decs in sorted(need.items()):
    p = game_dirs[g] / "run/decisions.jsonl"
    dsha[g] = hashlib.sha256(p.read_bytes()).hexdigest()
    for line in p.open():
        r = json.loads(line)
        if r["phase"] != "decision_resolved": continue
        k = int(r["decision_id"].rsplit("-", 1)[1])
        if k not in decs: continue
        if r.get("retry_used"): chan["retry_used"] += 1
        applied = r["final_action"]["action"]
        if r["player_name"].startswith("grok"):
            chan["grok_paid_decisions"] += 1
            att = r["attempts"][-1]
            try: content = att["raw_response"]["choices"][0]["message"].get("content") or ""
            except Exception: content = ""
            names = [t for t in TOOLS if t in content]
            if names:
                chan["grok_content_names_action"] += 1
                if applied not in names:
                    chan["grok_conflicts"].append({"game": g, "decision": k, "applied": applied, "content_names": names})
        if r["player_name"].startswith("claude"):
            chan["opus_paid_decisions"] += 1
            cond = (r.get("sequence_meta") or {}).get("final_response_condition") or (r.get("sequence_meta") or {}).get("selected_condition")
            if cond and "without_private_thought" in str(cond): chan["opus_paid_action_only"] += 1
G["paid_channel_check"] = chan
G["decision_file_sha256"] = dsha
res["G_debt"] = G

out = OUT / "cross_checks.json"
out.write_text(json.dumps(res, indent=1, default=str))
print("wrote", out.relative_to(ROOT))
