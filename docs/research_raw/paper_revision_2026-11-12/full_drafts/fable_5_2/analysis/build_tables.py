"""Write ``sections/facts.tex`` and ``sections/tables.tex`` from the analysis outputs.

Every number in the manuscript is cited as ``\\fact{key}``.  Keys are the
flattened paths of the JSON outputs plus a short list of derived values
defined below.  An unknown key is a LaTeX error, so a changed tabulation
either changes the paper or stops the build.  ``data/facts_index.txt`` lists
every key and value.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
load = lambda name: json.loads((DATA / name).read_text())
O, D, C, P, I, R = (load(n) for n in ("b1_offers.json", "b2_debt.json", "b3_conditions.json", "b4_provenance.json", "b5_incidents.json", "b6_readings.json"))
MODELS = ["Sol", "Gemini", "Opus", "Grok"]
F: dict[str, str] = {}


def fmt(v) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, float):
        return f"{v:,.1f}" if abs(v) < 1000 else f"{v:,.0f}"
    return str(v)


def flatten(prefix: str, obj, skip=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in skip:
                continue
            flatten(f"{prefix}.{k}".replace("_", "-").replace("|", "-").replace(">", "").replace(" ", "-"), v, skip)
    elif isinstance(obj, list):
        if all(isinstance(x, (int, float)) for x in obj) and len(obj) <= 6:
            for i, x in enumerate(obj):
                F[f"{prefix}.{i}"] = fmt(x)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        if isinstance(obj, float) and "pp" not in prefix and "share" not in prefix and obj == int(obj):
            obj = int(obj)
        F[prefix] = fmt(obj)


flatten("o", {k: v for k, v in O.items() if k not in ("sources", "reconciliation", "swap_by_pair", "form_definitions")}, skip=("definition", "source", "comparison_source", "source_sha256", "comparison_sha256", "per_block_counts"))
flatten("d", {k: v for k, v in D.items() if k not in ("reconciliation",)}, skip=("rows", "optional_rows"))
flatten("p", {k: v for k, v in P.items() if k in ("totals", "wins_by_system", "wins_by_seat", "first_eliminated_by_system", "decisions_by_system", "attempts_by_system")})
flatten("c", {"opus": {k: v for k, v in C["opus_refusals"].items() if isinstance(v, int)}, "resolution": C["resolution"], "notes": C["private_note_windows"]}, skip=("attempt_count_distribution", "final_response_condition"))


def pct(a, b, nd=1) -> str:
    return f"{100 * a / b:.{nd}f}"


def put(key, val):
    assert key not in F, key
    F[key] = val if isinstance(val, str) else fmt(val)


# ---- derived: offers --------------------------------------------------------
H = O["headline_cells"]
for name, key in (("swpo", "swap_proposer_only"), ("swn", "swap_neither"), ("cbpo", "cash_bid_proposer_only"), ("cbn", "cash_bid_neither"), ("swboth", "swap_both")):
    c = H[key]
    put(f"x.{name}.rej.pct", pct(c["reject"], c["n"]))
    put(f"x.{name}.ctr.pct", pct(c["counter"], c["n"]))
    put(f"x.{name}.acc.pct", pct(c["accept"], c["n"]))
po_all = {k: H["swap_proposer_only"][k] + H["cash_bid_proposer_only"][k] for k in ("n", "accept", "counter", "reject")}
n_all = {k: H["swap_neither"][k] + H["cash_bid_neither"][k] for k in ("n", "accept", "counter", "reject")}
for k, v in po_all.items():
    put(f"x.po.{k}", v)
for k, v in n_all.items():
    put(f"x.nei.{k}", v)
comp = O["composition"]
put("x.nogrok.swpo.pct", pct(*comp["without_grok_authors"]["swap_proposer_only"]))
put("x.nogrok.swn.pct", pct(*comp["without_grok_authors"]["swap_neither"]))
put("x.noconf.swpo.pct", pct(*comp["without_conflict_openings"]["swap_proposer_only"]))
put("x.noconf.swn.pct", pct(*comp["without_conflict_openings"]["swap_neither"]))
put("x.grok.share.swn.pct", pct(comp["swap_neither_by_grok"], H["swap_neither"]["n"], 0))
BR = O["by_recipient"]
BP = O["by_proposer"]
for m in MODELS:
    for cellname, key in (("swpo", "swap_proposer_only"), ("swn", "swap_neither"), ("cbpo", "cash_bid_proposer_only"), ("cbn", "cash_bid_neither")):
        for src, tag in ((BR, "rec"), (BP, "pro")):
            c = src[m][key]
            put(f"x.{tag}.{m}.{cellname}", f"{c['reject']}/{c['n']}")
    a, b = BR[m]["swap_proposer_only"], BR[m]["swap_neither"]
    put(f"x.rec.{m}.swgap", f"{100 * (a['reject'] / a['n'] - b['reject'] / b['n']):.0f}")
    a, b = BR[m]["cash_bid_proposer_only"], BR[m]["cash_bid_neither"]
    put(f"x.rec.{m}.cbgap", str(int(round(100 * (a['reject'] / a['n'] - b['reject'] / b['n'])))))
RW = O["refusal_wording"]
for m in MODELS:
    r = RW["responses_by_recipient_proposer_only_openings"][m]
    put(f"x.style.{m}.rej.pct", pct(r["reject"], r["n"], 0))
S = O["sensitivity"]
SC = O["semantic_codes"]
put("x.codes.other", SC["coded_rows"] - SC["agreed_rival_consequence"])
LV = O["list_value"]
put("x.lv.swpo.fav.pct", pct(*LV["swap_proposer_only"]["favourable_to_recipient"], 0))
put("x.lv.swn.fav.pct", pct(*LV["swap_neither"]["favourable_to_recipient"], 0))
TO = O["thread_outcomes"]
KS = O["keyword_screen"]
HC = O["holder_cash"]["all_author_only"]
put("x.cash.low.rej.pct", pct(HC["under_100"]["reject"], HC["under_100"]["n"], 0))
put("x.cash.high.rej.pct", pct(HC["300_plus"]["reject"], HC["300_plus"]["n"], 0))

# ---- derived: debt ----------------------------------------------------------
T = D["tiers_among_payable"]
put("x.debt.payable.paid.pct", pct(D["classes"]["paid"], D["payable"]))
put("x.debt.above.declared.pct", pct(D["above_bound"]["declared_at_first_menu"], D["above_bound"]["episodes"], 0))
put("x.debt.easy.share.pct", pct(T["listed"]["episodes"], D["payable"], 0))
put("x.debt.median.ratio.pct", f"{100 * D['paid_actions']['median_debt_over_bound']:.0f}")
put("x.debt.above.continued", D["above_bound"]["episodes"] - D["above_bound"]["declared_at_first_menu"])
put("x.debt.payable.continued", D["first_menu_decision"]["payable|continue"])
put("x.debt.payable.declared", D["first_menu_decision"]["payable|declare"])
put("x.debt.agree", D["first_menu_decision"]["payable|continue"] + D["above_bound"]["declared_at_first_menu"])
put("x.debt.known", D["payable"] + D["above_bound"]["episodes"])
put("x.nc.notes", R["channel_by_outcome"]["paid"]["applied private note"])
put("x.nc.returned", R["channel_by_outcome"]["paid"]["provider-returned explanation"])
put("x.nc.explicit", R["codes_by_outcome"]["paid"]["explicit"])
put("x.nc.tentative", R["codes_by_outcome"]["paid"]["tentative"])
put("x.nc.omits", R["codes_by_outcome"]["eliminated"]["omits"])
put("x.nc.numbers.checked", R["stated_numbers_checked"])
put("x.nc.numbers.equal", R["stated_numbers_equal_records"])
put("x.elim.nonterminal.winner", D["eliminations"]["nonterminal_to_eventual_winner"])

# ---- derived: conditions and provenance -------------------------------------
put("x.replay.artifact.events", P["replay"]["artifact_mode"]["events_compared"])
put("x.replay.state.events", P["replay"]["state_mode"]["events_compared"])
put("x.intents", P["request_payloads"]["intent_files"])
for row in P["request_payloads"]["by_model"]:
    put(f"x.intents.{row['model'].split('/')[1]}", row["requests"])
put("x.cost.upstream", f"{C['usage_totals']['sum_upstream_inference_cost_field']:.2f}")
put("x.opus.recovery.trade.responses", O["census"]["opus_recipient_action_only"])
put("x.g14.first4.refused", sum(C["opus_refusals"]["per_game"][str(g)]["first_attempt_refused"] for g in (1, 2, 3, 4)))
put("x.g14.first4.decisions", sum(C["opus_refusals"]["per_game"][str(g)]["opus_decisions"] for g in (1, 2, 3, 4)))
put("x.g520.refused", sum(C["opus_refusals"]["per_game"][str(g)]["first_attempt_refused"] for g in range(5, 21)))
put("x.grok.conflict.accepts", O["census"]["grok_recipient_conflicts"].get("accept_trade", 0))

# ---- write facts ---------------------------------------------------------------
lines = ["% Generated by analysis/build_tables.py. Do not edit by hand."]
for k in sorted(F):
    v = F[k].replace("%", r"\%").replace("$", r"\$").replace("_", r"\_").replace("#", r"\#").replace("&", r"\&")
    if v.startswith("-") and v[1:2].isdigit():
        v = "$-$" + v[1:]
    lines.append(f"\\expandafter\\gdef\\csname fact@{k}\\endcsname{{{v}}}")
(HERE / "sections" / "facts.tex").write_text("\n".join(lines) + "\n")
(DATA / "facts_index.txt").write_text("\n".join(f"{k}\t{F[k]}" for k in sorted(F)) + "\n")
(DATA / "facts.json").write_text(json.dumps(F, indent=1, sort_keys=True) + "\n")

# ---- tables ---------------------------------------------------------------------
TEX: list[str] = ["% Generated by analysis/build_tables.py. Do not edit by hand."]


def macro(name: str, body: str):
    TEX.append(f"\\newcommand{{\\{name}}}{{%\n{body}}}\n")


CELL_LABEL = {"author_only": "Proposer only", "recipient_only": "Recipient only", "both": "Both", "neither": "Neither"}
FORM_LABEL = {"swap": "Swap", "cash_bid": "Cash bid", "sale_offer": "Sale offer", "other": "Other"}


def rate(c):
    return "--" if c["n"] == 0 else pct(c["reject"], c["n"], 0)


# opening form x completion (main text)
rows = []
ft = O["full_table"]["opening"]
for f in ("swap", "cash_bid", "sale_offer", "other"):
    first = True
    for c in ("author_only", "neither", "both", "recipient_only"):
        x = ft[f][c]
        if x["n"] == 0:
            continue
        rows.append(f"{FORM_LABEL[f] if first else ''} & {CELL_LABEL[c]} & {x['n']} & {x['accept']} & {x['counter']} & {x['reject']} & {rate(x)} \\\\")
        first = False
    tot = ft["form_totals"][f]
    rows.append(f" & \\emph{{all}} & \\emph{{{tot['n']}}} & \\emph{{{tot['accept']}}} & \\emph{{{tot['counter']}}} & \\emph{{{tot['reject']}}} & \\emph{{{rate(tot)}}} \\\\" + ("\\addlinespace" if f != "other" else ""))
assert sum(ft["form_totals"][f]["n"] for f in FORM_LABEL) == O["census"]["opening"]
macro("TableOpening", "\\begin{tabular}{@{}llrrrrr@{}}\\toprule\nForm & Completes a group for & Offers & Accept & Counter & Reject & Rejected (\\%)\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# all 918 offers by stage (appendix)
rows = []
for stage, label in (("opening", "Opening"), ("later", "Later")):
    for f in ("swap", "cash_bid", "sale_offer", "other"):
        cells = []
        for c in ("author_only", "neither", "both", "recipient_only"):
            x = O["full_table"][stage][f][c]
            cells.append("--" if x["n"] == 0 else f"{x['n']} ({x['accept']}/{x['counter']}/{x['reject']})")
        rows.append(f"{label if f == 'swap' else ''} & {FORM_LABEL[f]} & " + " & ".join(cells) + " \\\\")
    cells = []
    for c in ("author_only", "neither", "both", "recipient_only"):
        x = O["full_table"][stage]["all_forms"][c]
        cells.append(f"\\emph{{{x['n']} ({x['accept']}/{x['counter']}/{x['reject']})}}")
    rows.append(" & \\emph{all forms} & " + " & ".join(cells) + " \\\\" + ("\\addlinespace" if stage == "opening" else ""))
macro("TableFullOffers", "\\begin{tabular}{@{}llrrrr@{}}\\toprule\nStage & Form & Proposer only & Neither & Both & Recipient only\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# proposer and recipient strata (main text)
def strata_rows(src):
    out = []
    for m in MODELS:
        c = src[m]
        cell = lambda k: "--" if c[k]["n"] == 0 else f"{c[k]['reject']}/{c[k]['n']}"
        out.append(f"{m} & {cell('swap_proposer_only')} & {cell('swap_neither')} & {cell('cash_bid_proposer_only')} & {cell('cash_bid_neither')} \\\\")
    return out


allrow = f"All & {H['swap_proposer_only']['reject']}/{H['swap_proposer_only']['n']} & {H['swap_neither']['reject']}/{H['swap_neither']['n']} & {H['cash_bid_proposer_only']['reject']}/{H['cash_bid_proposer_only']['n']} & {H['cash_bid_neither']['reject']}/{H['cash_bid_neither']['n']} \\\\"
macro("TableStrata", "\\begin{tabular}{@{}lrrrr@{}}\\toprule\n & \\multicolumn{2}{c}{Swap} & \\multicolumn{2}{c}{Cash bid}\\\\\\cmidrule(lr){2-3}\\cmidrule(l){4-5}\n & Proposer only & Neither & Proposer only & Neither\\\\\\midrule\n\\multicolumn{5}{@{}l}{\\emph{By proposer}}\\\\\n" + "\n".join(strata_rows(BP)) + "\n\\addlinespace\\multicolumn{5}{@{}l}{\\emph{By recipient}}\\\\\n" + "\n".join(strata_rows(BR)) + "\n\\midrule " + allrow + "\n\\bottomrule\\end{tabular}")

# seed blocks (appendix)
rows = []
for b in ("1", "2", "3", "4", "5"):
    c = O["by_block"][b]
    cell = lambda k: f"{c[k]['reject']}/{c[k]['n']}"
    rows.append(f"{b} (G{4 * int(b) - 3}--G{4 * int(b)}) & {P['seeds'][b]} & {cell('swap_proposer_only')} & {cell('swap_neither')} & {cell('cash_bid_proposer_only')} & {cell('cash_bid_neither')} & {T['unlisted']['by_block'][b][0]}/{T['unlisted']['by_block'][b][1]} \\\\")
macro("TableBlocks", "\\begin{tabular}{@{}lrrrrrr@{}}\\toprule\n & & \\multicolumn{2}{c}{Swap rejected} & \\multicolumn{2}{c}{Cash bid rejected} & Unlisted-collateral\\\\\\cmidrule(lr){3-4}\\cmidrule(lr){5-6}\nSeed block & Seed & Proposer only & Neither & Proposer only & Neither & debts paid\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# sensitivity (main text)
def srow(label, s, cells=True):
    lo, hi = s["leave_one_block_out_range_pp"]
    b, g = s["block_resampling"], s["game_resampling"]
    sign = lambda v: f"{v:+.1f}".replace("-", "$-$")
    rng = lambda a, c: f"{sign(a)} to {sign(c)}"
    label = label
    return f"{label} & {s['cells']['a'][0]}/{s['cells']['a'][1]} vs {s['cells']['b'][0]}/{s['cells']['b'][1]} & {sign(s['point_pp'])} & {s['blocks_same_sign_as_point']}/5 & {rng(lo, hi)} & {rng(b['p2_5_pp'], b['p97_5_pp'])} & {rng(g['p2_5_pp'], g['p97_5_pp'])} \\\\"


rows = [
    srow("Swap rejection gap, all proposers", S["swap_gap"]),
    srow("\\quad no conflicting Grok openings", S["swap_gap_without_conflict_openings"]),
    srow("\\quad no Grok-authored swaps", S["swap_gap_without_grok_authors"]),
    srow("Cash-bid rejection gap", S["cash_bid_gap"]),
    srow("Counter share, cash bid $-$ swap", S["counter_share_cash_bid_vs_swap_proposer_only"]),
]
macro("TableSensitivity", "\\setlength{\\tabcolsep}{2.4pt}\\begin{tabular}{@{}lcrcccc@{}}\\toprule\n & & Point & Blocks, & Leave one & Seed-block & Game\\\\\nContrast & Cells & (pp) & same sign & block out & resampling & resampling\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# recipient styles (main text)
rows = []
for m in MODELS:
    r = RW["responses_by_recipient_proposer_only_openings"][m]
    w = RW["by_recipient"][m]
    rows.append(f"{m} & {r['n']} & {r['reject']} & {r['counter']} & {r['accept']} & {w['building_terms']}/{w['rejections']} & {w['reciprocity_terms']}/{w['rejections']} & {w['commitment_terms']}/{w['rejections']} \\\\")
rows.append(f"\\midrule All & {po_all['n']} & {po_all['reject']} & {po_all['counter']} & {po_all['accept']} & & & \\\\")
macro("TableStyles", "\\begin{tabular}{@{}lrrrrrrr@{}}\\toprule\n & \\multicolumn{4}{c}{Response} & \\multicolumn{3}{c}{Wording of rejections (pattern match)}\\\\\\cmidrule(lr){2-5}\\cmidrule(l){6-8}\nRecipient & Offers & Reject & Counter & Accept & Building & Reciprocity & Commitment\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# debt partition (main text)
ab = D["above_bound"]
rows = [
    f"Cash and mortgages already listed & {T['listed']['episodes']} & {T['listed']['paid']} & 0 & {T['listed']['single_action_payments']} \\\\",
    f"Building sales as well & {T['sales']['episodes']} & {T['sales']['paid']} & {T['sales']['declared']} & {T['sales']['single_action_payments']} \\\\",
    f"Mortgages the menu does not yet list & {T['unlisted']['episodes']} & {T['unlisted']['paid']} & {T['unlisted']['declared']} & {T['unlisted']['single_action_payments']} \\\\",
    f"\\midrule Payable, all & {D['payable']} & {D['classes']['paid']} & {D['classes']['payable_declared']} & {D['paid_actions']['single_action']} \\\\",
    f"Debt above every own asset & {ab['episodes']} & 0 & {ab['declared_at_first_menu']} & -- \\\\",
    f"Menu offers no building sale (G7) & 1 & 0 & 0 & -- \\\\",
]
macro("TableDebt", "\\begin{tabular}{@{}lrrrr@{}}\\toprule\n & & & Quit at & Paid in\\\\\nWhat payment required at the first menu & Episodes & Paid & first menu & one action\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# sixteen cases (main text)
CODE = {"explicit": "counts them", "tentative": "raises them", "omits": "leaves them out"}
CODE_SHORT = {"explicit": "counted", "tentative": "raised", "omits": "left out"}
CH = {"applied private note": "note", "provider-returned explanation": "returned"}
rows = []
for r in R["rows"]:
    after = "--" if r["cash_after_payment"] is None else f"\\${r['cash_after_payment']:,}"
    out = "paid" if r["outcome"] == "paid" else "quit"
    rows.append(f"G{r['game']} d{r['decision']} & {r['model']} & {r['debt']:,} & {r['reach_without_unlisted']:,} & {r['unlisted_mortgage']:,} & {CH[r['channel']]} & {CODE_SHORT[r['code']]} & {out} & {r['n_actions']} & {after} \\\\")
macro("TableSixteen", "\\setlength{\\tabcolsep}{4.5pt}\\begin{tabular}{@{}llrrrlllrr@{}}\\toprule\n & & & Reach without & Unlisted & & Unlisted value & & & Cash\\\\\nCase & System & Debt & unlisted & value & Channel & in first text & Outcome & Actions & after\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# sixteen cases with quotations (appendix)
rows = []
for r in R["rows"]:
    chk = r["stated_number_check"]
    note = "" if not chk else (" Stated figure matches the records." if chk["equal"] else f" Stated \\${chk['stated']}; the records give \\${chk['from_records']}.")
    rows.append(f"G{r['game']} d{r['decision']} & {r['model']}, {CH[r['channel']]} & \\InlineQuote{{{r['quote_id']}}} & {CODE[r['code']].capitalize()}.{note} \\\\")
macro("TableSixteenQuotes", "\\begin{longtable}{@{}L{.10\\linewidth}L{.12\\linewidth}L{.47\\linewidth}L{.21\\linewidth}@{}}\n\\caption{First stored text in each of the sixteen unlisted-collateral episodes. ``Note'' is the applied private note. ``Returned'' is the provider-returned explanation of an action-only recovery response, which has no private note. The reading in the last column is one pass by the drafting assistant and is not human annotation.}\\label{tab:sixteenquotes}\\\\\n\\toprule Case & System, channel & Exact span & Reading\\\\\\midrule\\endfirsthead\n\\toprule Case & System, channel & Exact span & Reading\\\\\\midrule\\endhead\n" + "\n\\addlinespace\n".join(rows) + "\n\\bottomrule\\end{longtable}")

# rival capacity (appendix)
rc = O["rival_capacity"]
rows = []
for b in ("0", "1-2", "3-5", "6+"):
    s, c = rc["swap_proposer_only"][b], rc["cash_bid_proposer_only"][b]
    rows.append(f"{b.replace('-', '--')} & {s['reject']}/{s['n']} & {s['counter']}/{s['n']} & {c['reject']}/{c['n']} & {c['counter']}/{c['n']} \\\\")
macro("TableCapacity", "\\begin{tabular}{@{}lrrrr@{}}\\toprule\nHouses the proposer could buy & \\multicolumn{2}{c}{Swaps} & \\multicolumn{2}{c}{Cash bids}\\\\\\cmidrule(lr){2-3}\\cmidrule(l){4-5}\nafter the trade & Rejected & Countered & Rejected & Countered\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# keyword screen (appendix)
rows = []
for label, key in (("Swap, proposer only", "swap_proposer_only"), ("Swap, neither", "swap_neither"), ("Cash bid, proposer only", "cash_bid_proposer_only"), ("Cash bid, neither", "cash_bid_neither")):
    k = KS["rejections"][key]
    rows.append(f"{label} & {k['n']} & {k['completion_terms']} & {k['building_terms']} \\\\")
macro("TableKeywords", "\\begin{tabular}{@{}lrrr@{}}\\toprule\nRejected opening offers & Rejections & Completion or blocking terms & Building terms\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# game map (appendix)
rows = []
for g in P["games"]:
    seats = ", ".join(g["seat_order"])
    out = ", ".join(g["eliminated_in_order"])
    rows.append(f"G{g['game']} & {g['block']} & {seats} & {g['turns']} & {g['decisions']} & {g['winner']} ({g['winner_seat']}) & {out} & \\texttt{{{g['source_commit'][:8]}}} \\\\" + ("\\addlinespace" if g["game"] % 4 == 0 and g["game"] < 20 else ""))
macro("TableGames", "\\setlength{\\tabcolsep}{4pt}\\begin{tabular}{@{}lrlrrlll@{}}\\toprule\nGame & Block & Seat order (first to move first) & Turns & Decisions & Winner (seat) & Eliminated, in order & Source\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

# systems (main text)
ids = {"Sol": "openai/gpt-6.1-sol", "Gemini": "google/gemini-4-argon", "Opus": "anthropic/claude-opus-5.5", "Grok": "x-ai/grok-4.7"}
tc = {"Sol": "auto", "Gemini": "auto", "Opus": "auto", "Grok": "required"}
rows = [f"{m} & \\path{{{ids[m]}}} & {tc[m]} & {P['decisions_by_system'][m]:,} & {P['attempts_by_system'][m]:,} & {P['wins_by_system'][m]} \\\\" for m in MODELS]
macro("TableSystems", "\\begin{tabular}{@{}llrrrr@{}}\\toprule\nLabel & OpenRouter identifier & Tool choice & Decisions & Attempts & Wins\\\\\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}")

(HERE / "sections" / "tables.tex").write_text("\n".join(TEX))
print("facts", len(F), "tables", sum(1 for t in TEX if t.startswith("\\newcommand")))
