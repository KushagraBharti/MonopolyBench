"""Read-only checks for the Opus cross-review, 12 November 2026.

Reads stored records only: saved_games/*/run/{events.jsonl,prompts/*,players.json},
saved_games/*/cloud/calls/*.intent.json, contracts/data/board.json, the frozen
11 November offer and debt ledgers, and three frozen 12 November draft data files.
Imports no engine or arena code, replays nothing and contacts no provider.

Usage (from the repository root):
    python3 -I docs/research_raw/paper_revision_2026-11-12/reviews/opus/checks/run_checks.py \
        docs/research_raw/paper_revision_2026-11-12/reviews/opus/checks/fresh_checks.json
"""
import glob
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict

ROOT = "/Users/kushagra/CS-Projects/MonopolyBench/"
OFFERS = ROOT + "docs/research_raw/paper_revision_2026-11-11/integrated/data/offers.json"
DEBTS = ROOT + "docs/research_raw/paper_revision_2026-11-11/integrated/data/liquidation_episodes.json"
OPUS_ROWS = ROOT + "docs/research_raw/paper_revision_2026-11-12/full_drafts/opus/data/finance_rows.json"
OPUS_FIN = ROOT + "docs/research_raw/paper_revision_2026-11-12/full_drafts/opus/data/finance_analysis.json"
FABLE_LEDGER = ROOT + "docs/research_raw/paper_revision_2026-11-12/full_drafts/fable_5_2/data/b1_offer_ledger.json"
BOARD = ROOT + "contracts/data/board.json"
SOURCES = [OFFERS, DEBTS, OPUS_ROWS, OPUS_FIN, FABLE_LEDGER, BOARD]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def run_dir(g):
    base = "railway-research-12-games-2026-10-25" if g <= 12 else "railway-research-8-games-2026-10-26"
    return glob.glob(f"{ROOT}saved_games/{base}/game-{g:02d}-*/run")[0]


def prompt(g, d, kind="user"):
    path = glob.glob(f"{run_dir(g)}/prompts/*dec-{d:06d}_{kind}.json" if kind == "user"
                     else f"{run_dir(g)}/prompts/*dec-{d:06d}_{kind}.txt")[0]
    return json.load(open(path)) if kind == "user" else open(path).read()


out = {"sources": {p.replace(ROOT, ""): sha(p) for p in SOURCES}}

# ---------------------------------------------------------------- debts
rows = json.load(open(OPUS_ROWS))
inh = {(x["game"], x["first_decision"]): x for x in json.load(open(DEBTS))}
assert len(rows) == 188 and all(r["bound"] == inh[(r["game"], r["first_decision"])]["upper_bound"] for r in rows)
first_decl = lambda r: r["actions"][0]["action"] == "declare_bankruptcy"
visible = lambda r: r["cash"] + r["L0"] + r["S"]
PAYABLE_DECL = {(12, 190), (12, 249), (17, 234)}
payable = [r for r in rows if r["outcome"] == "paid" or (r["game"], r["first_decision"]) in PAYABLE_DECL]
above = [r for r in rows if r["debt"] > r["bound"]]
tierN = [r for r in rows if r["tier"] == "N"]
assert len(payable) == 131 and len(above) == 56 and len(tierN) == 16
vis_short_payable = [r for r in payable if visible(r) < r["debt"]]
vis_ok_payable = [r for r in payable if visible(r) >= r["debt"]]
max_gap_N = max(r["debt"] - visible(r) for r in tierN)
max_ratio_N = max(r["debt"] / visible(r) for r in tierN)
matched_gap = [r for r in above if r["debt"] - visible(r) <= max_gap_N]
matched_ratio = [r for r in above if r["debt"] / visible(r) <= max_ratio_N]
out["quit_or_continue"] = {
    "above_bound": [len(above), sum(map(first_decl, above))],
    "payable": [len(payable), sum(map(first_decl, payable))],
    "payable_declared_first": sorted((r["game"], r["first_decision"], r["model"]) for r in payable if first_decl(r)),
    "visible_short_payable_tierN": [len(vis_short_payable), sum(map(first_decl, vis_short_payable))],
    "visible_ok_payable_tiersAB": [len(vis_ok_payable), sum(map(first_decl, vis_ok_payable))],
    "max_visible_gap_tierN": max_gap_N,
    "above_bound_with_gap_le_tierN_max": [len(matched_gap), sum(map(first_decl, matched_gap))],
    "above_bound_with_ratio_le_tierN_max": [len(matched_ratio), sum(map(first_decl, matched_ratio)), round(max_ratio_N, 2)],
    "above_bound_continuers": sorted((r["game"], r["first_decision"], r["model"]) for r in above if not first_decl(r)),
    "above_bound_declared_first_by_model": dict(Counter(r["model"] for r in above if first_decl(r))),
    "above_bound_by_model": dict(Counter(r["model"] for r in above)),
}

# ------------------------------------------- what the first-decision prompts supply
fin = json.load(open(OPUS_FIN))["necessary"]["rows"]
board = json.load(open(BOARD))
price = {re.sub(r"[^A-Z0-9]+", "_", s["name"].upper()).strip("_"): s["price"] for s in board["spaces"] if "price" in s}
prompt_rows = []
for r in fin:
    g, d = r["game"], r["first_decision"]
    u = prompt(g, d)
    system = prompt(g, d, "system")
    listed = set(u["action_state"]["scenario"]["options"]["mortgageable_space_keys"])
    unl = [o["space_key"] for o in u["game_state"]["you"]["holdings"]["owned"]
           if not o["mortgaged"] and o["space_key"] not in listed]
    notes = [n.get("thought", "") for n in u["game_state"]["memory"].get("your_private_thoughts_last_10", [])]
    sentences = [s for n in notes for s in re.split(r"(?<=[.;])\s", n)]
    released_value_statements = [
        s for s in sentences
        if re.search(r"mortgag", s, re.I) and re.search(r"\$\d", s)
        and any(k.split("_")[0].lower() in s.lower() for k in unl)
    ]
    prompt_rows.append({
        "game": g, "decision": d, "model": r["model"], "condition": r["response_condition"],
        "carried_notes": len(notes), "released_deeds": unl, "released_value": sum(price[k] // 2 for k in unl),
        "value_fields_in_prompt": bool(re.search(r'"(price|mortgage_value|rent|house_cost|group)"', json.dumps(u))),
        "system_prompt_mentions_mortgage": "mortgag" in system.lower(),
        "notes_state_listed_or_other_mortgage_amounts": any(re.search(r"mortgag", s, re.I) and re.search(r"\$\d", s) for s in sentences),
        "notes_name_a_released_deed_with_mortgage_amount": released_value_statements,
        "scenario_note": u["action_state"]["scenario"]["note"],
    })
out["first_decision_prompts"] = {
    "rows": prompt_rows,
    "with_value_fields": sum(p["value_fields_in_prompt"] for p in prompt_rows),
    "system_mentions_mortgage": sum(p["system_prompt_mentions_mortgage"] for p in prompt_rows),
    "with_carried_notes": sum(p["carried_notes"] > 0 for p in prompt_rows),
    "notes_state_some_mortgage_amount": sum(p["notes_state_listed_or_other_mortgage_amounts"] for p in prompt_rows),
    "notes_name_released_deed_with_amount": sum(bool(p["notes_name_a_released_deed_with_mortgage_amount"]) for p in prompt_rows),
}

# --------------------------------------------- the liquidation note in every stored prompt
notes = Counter()
fields = Counter()
for f in glob.glob(ROOT + "saved_games/*/game-*/run/prompts/*_user.json"):
    u = json.load(open(f))
    a = u.get("action_state", {})
    if a.get("decision_type") == "LIQUIDATION_DECISION":
        notes[a["scenario"].get("note")] += 1
    if a.get("decision_type") in ("LIQUIDATION_DECISION", "TRADE_RESPONSE_DECISION"):
        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    fields[k] += 1
                    if k != "memory":
                        walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(u["game_state"]); walk(a)
out["liquidation_scenario_notes"] = {k: v for k, v in notes.items()}
out["trade_and_liquidation_prompt_fields"] = sorted(fields)

# --------------------------------------------------------------- tool choice
tc = Counter()
for f in glob.glob(ROOT + "saved_games/*/game-*/cloud/calls/*.intent.json"):
    p = json.load(open(f)).get("payload", {})
    tc[f'{p.get("model")}|{p.get("tool_choice")}'] += 1
out["tool_choice_request_records"] = dict(tc)

# ---------------------------------------------------------------- offers
offers = json.load(open(OFFERS))


def form(r):
    o, q = r["offer"], r["request"]
    if o["properties"] and q["properties"]:
        return "swap"
    if not o["properties"] and not o["get_out_of_jail_cards"] and q["properties"] and not q["get_out_of_jail_cards"] and o["cash"] > 0 and q["cash"] == 0:
        return "cashbid"
    if o["properties"] and not q["properties"] and not q["get_out_of_jail_cards"] and q["cash"] > 0 and not o["get_out_of_jail_cards"]:
        return "sale"
    return "other"


legal = [r for r in offers if r["accept_available"]]
for r in legal:
    r["form"] = form(r)
    r["block"] = (r["game"] - 1) // 4 + 1
op = [r for r in legal if r["exchange_index"] == 0]
conflict_threads = {r["thread_id"] for r in json.load(open(FABLE_LEDGER)) if r["opening"] and r["author_channel_conflict"]}
acr = lambda rs: [len(rs), sum(r["response"] == "accept_trade" for r in rs), sum(r["response"] == "counter_trade" for r in rs), sum(r["response"] == "reject_trade" for r in rs)]
cellsel = lambda rs, f, c: [r for r in rs if r["form"] == f and r["completion_cell"] == c]
out["opening_table"] = {f"{f}|{c}": acr(cellsel(op, f, c)) for f in ("swap", "cashbid", "sale", "other")
                        for c in ("author_only", "recipient_only", "both", "neither") if cellsel(op, f, c)}
H = [r for r in op if r["form"] in ("swap", "cashbid")]
nog = lambda rs: [r for r in rs if r["author_model"] != "Grok"]
out["opening_acceptance"] = {
    "completing_swap_or_cash": acr([r for r in H if r["completion_cell"] == "author_only"]),
    "neither_swap_or_cash": acr([r for r in H if r["completion_cell"] == "neither"]),
    "completing_no_grok_author": acr(nog([r for r in H if r["completion_cell"] == "author_only"])),
    "neither_no_grok_author": acr(nog([r for r in H if r["completion_cell"] == "neither"])),
    "neither_accepts_by_author": dict(Counter(r["author_model"] for r in H if r["completion_cell"] == "neither" and r["response"] == "accept_trade")),
    "all_openings": acr(op), "all_openings_by_author": {m: acr([r for r in op if r["author_model"] == m]) for m in ("Sol", "Gemini", "Opus", "Grok")},
    "later_offers": acr([r for r in legal if r["exchange_index"] > 0]),
}
settled = {r["thread_id"] for r in offers if r["response"] == "accept_trade"}
out["thread_settlement"] = {k: [sum(r["thread_id"] in settled for r in v), len(v)] for k, v in {
    "completing": [r for r in H if r["completion_cell"] == "author_only"],
    "neither": [r for r in H if r["completion_cell"] == "neither"],
    "completing_no_grok": nog([r for r in H if r["completion_cell"] == "author_only"]),
    "neither_no_grok": nog([r for r in H if r["completion_cell"] == "neither"]),
}.items()}
rej = lambda rs: [sum(r["response"] == "reject_trade" for r in rs), len(rs)]


def gap(rs, f):
    a, b = rej(cellsel(rs, f, "author_only")), rej(cellsel(rs, f, "neither"))
    return None if not a[1] or not b[1] else 100 * (a[0] / a[1] - b[0] / b[1])


strata = {}
for side in ("recipient_model", "author_model"):
    for f in ("swap", "cashbid"):
        for m in ("Sol", "Gemini", "Opus", "Grok"):
            sub = [r for r in op if r[side] == m]
            strata[f"{side}|{f}|{m}"] = [rej(cellsel(sub, f, "author_only")), rej(cellsel(sub, f, "neither")),
                                          None if gap(sub, f) is None else round(gap(sub, f), 1)]
out["strata"] = strata


def standardized(f, side, weight_cell):
    tot = w_sum = 0
    for m in ("Sol", "Gemini", "Opus", "Grok"):
        sub = [r for r in op if r[side] == m]
        g = gap(sub, f)
        if g is None:
            continue
        w = len(cellsel(sub, f, weight_cell))
        tot += w * g; w_sum += w
    return round(tot / w_sum, 1)


out["recipient_standardized_gap"] = {f"{f}|w={c}": standardized(f, "recipient_model", c) for f in ("swap", "cashbid") for c in ("author_only", "neither")}
out["counters"] = {f"{f}|{c}": [sum(r["response"] == "counter_trade" for r in cellsel(op, f, c)), len(cellsel(op, f, c))]
                   for f in ("swap", "cashbid") for c in ("author_only", "neither")}
out["counters_by_block_completing"] = {b: {f: [sum(r["response"] == "counter_trade" for r in cellsel([x for x in op if x["block"] == b], f, "author_only")),
                                               len(cellsel([x for x in op if x["block"] == b], f, "author_only"))] for f in ("swap", "cashbid")} for b in range(1, 6)}

HC = {"BROWN": 50, "LIGHT_BLUE": 50, "PINK": 100, "MAGENTA": 100, "ORANGE": 100, "RED": 150, "YELLOW": 150, "GREEN": 200, "DARK_BLUE": 200}


def cap_bin(r):
    costs = [HC[g] for g in r["author_new_groups"] if g in HC]
    c = r["author_cash_if_accepted"] // min(costs)
    return "0" if c < 1 else "1-2" if c <= 2 else "3-5" if c <= 5 else "6+"


out["capacity_bins"] = {f: {b: [sum(r["response"] == "reject_trade" for r in v), sum(r["response"] == "counter_trade" for r in v), len(v)]
                            for b, v in sorted({k: [r for r in cellsel(op, f, "author_only") if cap_bin(r) == k] for k in ("0", "1-2", "3-5", "6+")}.items())}
                        for f in ("swap", "cashbid")}
RECIP = re.compile(r"in return|monopoly-for-monopoly|for me as well|on my side|completes? a (color )?(set|group|monopoly) for me", re.I)
NEVER = re.compile(r"\bnever\b|not for sale|do not counter|no counter", re.I)
txt = lambda r: (r["public_message"] or "") + "\n" + (r["applied_private_note"] or "")
wording = {}
for c in ("author_only", "neither"):
    for m in ("Sol", "Gemini", "Opus", "Grok"):
        rj = [r for r in H if r["completion_cell"] == c and r["recipient_model"] == m and r["response"] == "reject_trade"]
        wording[f"{c}|{m}"] = {"rejections": len(rj), "reciprocity": sum(bool(RECIP.search(txt(r))) for r in rj), "commitment": sum(bool(NEVER.search(txt(r))) for r in rj)}
out["refusal_wording_with_baseline"] = wording
rj74 = [r for r in legal if r["response"] == "reject_trade" and r["completion_cell"] in ("recipient_only", "both")]
out["recipient_completing_rejections"] = {"n": len(rj74), "by_cell": dict(Counter(r["completion_cell"] for r in rj74)), "opening": sum(r["exchange_index"] == 0 for r in rj74)}

# ------------------------------------------------------------ resampling
bygame = defaultdict(list)
for r in op:
    bygame[r["game"]].append(r)
versions = {"all": lambda r: True, "no_grok_author": lambda r: r["author_model"] != "Grok", "no_conflict_openings": lambda r: r["thread_id"] not in conflict_threads}
res = {}
for vn, vf in versions.items():
    for f in ("swap", "cashbid"):
        rs = [r for r in op if vf(r)]
        rng = random.Random(7)
        two, games = [], []
        for _ in range(20000):
            samp = []
            for b in [rng.randint(1, 5) for _ in range(5)]:
                gs = [4 * (b - 1) + i for i in range(1, 5)]
                for g in [rng.choice(gs) for _ in range(4)]:
                    samp += [r for r in bygame[g] if vf(r)]
            v = gap(samp, f)
            if v is not None:
                two.append(v)
            v = gap([r for g in [rng.randint(1, 20) for _ in range(20)] for r in bygame[g] if vf(r)], f)
            if v is not None:
                games.append(v)
        two.sort(); games.sort()
        q = lambda a: [round(a[int(0.025 * len(a))], 1), round(a[int(0.975 * len(a)) - 1], 1)]
        res[f"{vn}|{f}"] = {"point": round(gap(rs, f), 1),
                            "blocks": [None if gap([r for r in rs if r["block"] == b], f) is None else round(gap([r for r in rs if r["block"] == b], f), 1) for b in range(1, 6)],
                            "leave_one_block_out": [round(min(gap([r for r in rs if r["block"] != b], f) for b in range(1, 6)), 1),
                                                    round(max(gap([r for r in rs if r["block"] != b], f) for b in range(1, 6)), 1)],
                            "blocks_then_games_95": q(two), "games_only_95": q(games), "draws": 20000, "seed": 7}
out["resampling"] = res

# ---------------------------------------------------------- estates and context
winners, elims = {}, defaultdict(list)
for g in range(1, 21):
    for line in open(run_dir(g) + "/events.jsonl"):
        e = json.loads(line)
        if e["type"] == "GAME_ENDED":
            winners[g] = e["payload"]["winner_player_id"]
        if e["type"] == "CASH_CHANGED" and e["payload"].get("reason") == "BANKRUPTCY":
            elims[g].append(e["payload"]["player_id"])
non = to_win = 0
for x in json.load(open(DEBTS)):
    if x["outcome"] != "bankrupt":
        continue
    g = x["game"]
    terminal = elims[g][-1] == x["player"] and len(elims[g]) == 3
    if not terminal:
        non += 1
        cred = prompt(g, x["first_decision"])["action_state"]["scenario"].get("owed_to_player_id")
        to_win += cred == winners[g]
out["nonterminal_estates"] = {"nonterminal_eliminations": non, "to_eventual_winner": to_win}

json.dump(out, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in out.items() if k not in ("first_decision_prompts", "trade_and_liquidation_prompt_fields", "strata", "resampling", "sources")}, indent=1))
print(json.dumps(out["resampling"], indent=1))
print({k: v for k, v in out["first_decision_prompts"].items() if k != "rows"})
