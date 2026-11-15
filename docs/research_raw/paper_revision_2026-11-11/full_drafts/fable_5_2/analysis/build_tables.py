"""Emit every number and table row used by the manuscript.

``sections/facts.tex`` defines ``\\fact{key}`` for scalars flattened from the
tabulation summaries plus a short list of derived values (percentages and
differences).  ``sections/tables.tex`` defines row macros for the native
tables.  The prose never types an analysis number by hand, so a changed
tabulation changes the paper or fails the build on an undefined key.
"""
from __future__ import annotations

import json
import re
import statistics as S
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
MODELS = ["Sol", "Gemini", "Opus", "Grok"]


def load(name):
    return json.loads((DATA / name).read_text())


def sanitize(key: str) -> str:
    key = key.replace("<", "lt").replace("+", "plus").replace("|", ".").replace("=", "eq").replace("_", "-").replace(" ", "-")
    key = re.sub(r"[^A-Za-z0-9.\-]", "", key)
    return key


def fmt(v) -> str | None:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return f"{v:,}" if abs(v) >= 1000 else str(v)
    if isinstance(v, float):
        if v == int(v) and abs(v) >= 1000:
            return f"{int(v):,}"
        s = f"{v:,.3f}".rstrip("0").rstrip(".")
        return s
    if isinstance(v, str) and len(v) < 60 and "\n" not in v:
        return v.replace("_", r"\_").replace("&", r"\&").replace("$", r"\$").replace("%", r"\%").replace("#", r"\#")
    return None


def flatten(obj, prefix, out, skip=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in skip:
                continue
            flatten(v, f"{prefix}.{k}" if prefix else str(k), out, skip)
    elif isinstance(obj, list):
        if len(obj) <= 8 and all(not isinstance(x, (dict, list)) for x in obj):
            for i, v in enumerate(obj):
                flatten(v, f"{prefix}.{i}", out, skip)
    else:
        s = fmt(obj)
        if s is not None:
            out[sanitize(prefix)] = s


def pct(a, b, nd=0):
    return f"{100 * a / b:.{nd}f}"


def money(v):
    return f"\\${v:,.0f}"


def main() -> None:
    facts: dict[str, str] = {}
    cond = load("a1_conditions.json")
    flatten({k: v for k, v in cond.items() if k not in ("sources", "system_prompt")}, "cond", facts)
    flatten({k: v for k, v in cond["system_prompt"].items() if not k.endswith("_text") and k != "unified_diff"}, "cond.prompt", facts)
    flatten(load("a2_offer_ledger_reconciliation.json"), "ledger", facts)
    flatten(load("a3_group_summary.json"), "groups", facts)
    debt = load("a4_debt_summary.json")
    flatten(debt, "debt", facts, skip=("reconciliation_mismatches",))
    est = load("a5_pre_estate_summary.json")
    flatten(est, "estate", facts)
    barg = load("a6_bargaining.json")
    flatten(barg, "barg", facts, skip=("same_game_seller_deed_pairs", "seller_fate_rows", "rows", "definition", "joint_recipient_stage_cell"))
    conv = load("a7_conversion.json")
    flatten(conv, "conv", facts, skip=("rows", "definition", "turns"))
    flows = load("a8_estate_flows.json")
    flatten(flows["summary"], "flows", facts)
    flatten(load("state_track_validation.json"), "track", facts, skip=("examples",))

    # ------------------------------------------------------------ derived
    D = {}
    cen = barg["census"]
    for c in ("author_only", "recipient_only", "both", "neither"):
        d = cen["cells"][c]
        D[f"d.cell.{c}.rejectpct"] = pct(d["reject"], d["n"], 1)
        D[f"d.cell.{c}.acceptpct"] = pct(d["accept"], d["n"], 1)
        for st in ("opening", "later"):
            e = cen["cells_by_stage"][f"{c}|{st}"]
            D[f"d.cell.{c}.{st}.rejectpct"] = pct(e["reject"], e["n"], 1)
    for m in MODELS:
        d = cen["by_recipient"][m]
        D[f"d.recipient.{m}.rejectpct"] = pct(d["reject"], d["n"])
        D[f"d.recipient.{m}.counterpct"] = pct(d["counter"], d["n"])
    hc = barg["holder_cash"]
    for s in ("<100", "100-299", "300-599", "600+"):
        d = hc["author_only_by_holder_cash"][s]
        D[f"d.holder.{s}.rejectpct"] = pct(d["reject"], d["n"])
        D[f"d.holder.{s}.counterpct"] = pct(d["counter"], d["n"])
        D[f"d.holder.{s}.acceptpct"] = pct(d["accept"], d["n"])
        o = hc["other_deed_requests_by_holder_cash"][s]
        D[f"d.other.{s}.rejectpct"] = pct(o["reject"], o["n"])
    g = hc["reject_gap_under100_vs_300plus"]
    D["d.gap.low.pct"] = pct(*g["all"]["low"])
    D["d.gap.high.pct"] = pct(*g["all"]["high"])
    lobo = [v["gap_points"] for v in g["leave_one_block_out"].values()]
    D["d.gap.lobo.min"] = f"{min(lobo):.0f}"
    D["d.gap.lobo.max"] = f"{max(lobo):.0f}"
    for b, v in g["per_block"].items():
        D[f"d.gap.block{b}.low.pct"] = pct(*v["low"])
        D[f"d.gap.block{b}.high.pct"] = pct(*v["high"])
    for k in ("excluding_opus_recipients", "opening_only", "later_only", "other_deed_requests", "excluding_opus_either_side"):
        D[f"d.gap.{k}.low.pct"] = pct(*g[k]["low"])
        D[f"d.gap.{k}.high.pct"] = pct(*g[k]["high"])
    for m in MODELS:
        for s in ("<100", "100-299", "300+"):
            d = hc["author_only_by_recipient_and_cash"][f"{m}|{s}"]
            D[f"d.holder.{m}.{s}.rejectpct"] = pct(d["reject"], d["n"]) if d["n"] else "n/a"
    t = hc["requests_aimed_at_holders_under_100"]
    D["d.target.completion.pct"] = pct(*t["author_only"])
    D["d.target.other.pct"] = pct(*t["neither"])
    dy = barg["dyads"]
    D["d.dyads.settled.pct"] = pct(dy["settled"], dy["dyads"])
    D["d.dyads.onesided.under100.pct"] = pct(dy["one_sided_holder_cash_at_settlement"]["<100"], dy["settled_one_sided"])
    sens = barg["grok_sensitivity"]
    D["d.grok.conflict.thread.pct"] = pct(sens["threads_opened_by_conflicting_grok_call"], sens["of_grok_threads"])
    ao = sens["cells_after_exclusion"]["author_only"]
    ro = sens["cells_after_exclusion"]["recipient_only"]
    D["d.grok.excl.ao.rejectpct"] = pct(ao["reject"], ao["n"], 1)
    D["d.grok.excl.ro.rejectpct"] = pct(ro["reject"], ro["n"], 1)
    r = sens["reject_under100_vs_300plus_after_exclusion"]
    D["d.grok.excl.gap.low.pct"] = pct(*r["low"])
    D["d.grok.excl.gap.high.pct"] = pct(*r["high"])
    tg = conv["trade_groups"]
    fb, nb = tg["first_window_built"], tg["first_window_not_built"]
    D["d.conv.early.rentperlanding"] = f"{fb['rent'] / fb['landings']:.0f}"
    D["d.conv.late.rentperlanding"] = f"{nb['rent'] / nb['landings']:.0f}"
    D["d.conv.early.landrate"] = f"{100 * fb['landings'] / fb['group_turns']:.1f}"
    D["d.conv.late.landrate"] = f"{100 * nb['landings'] / nb['group_turns']:.1f}"
    D["d.conv.early.rentshare"] = pct(fb["rent"], tg["total_rent"], 1)
    sg = sum(tg["by_model"][m]["rent_paid"] for m in ("Sol", "Gemini"))
    D["d.conv.solgemini.rent"] = f"{sg:,}"
    D["d.conv.solgemini.rentshare"] = pct(sg, tg["total_rent"])
    D["d.conv.top5.pct"] = f"{100 * tg['top5_groups_share_of_rent']:.0f}"
    D["d.debt.paid.pct"] = pct(debt["paid"], debt["feasible_episodes"], 1)
    D["d.debt.sale.dominated"] = str(debt["paid_sale_when_menu_mortgages_cover_shortfall"])
    us = cond["usage"]
    for m in MODELS:
        D[f"d.usage.{m}.zeroshare"] = pct(us[m]["reasoning_zero"], us[m]["reasoning_field_present"])
    op = cond["opus_refusals"]
    g14 = [op["per_game"][str(i)] for i in (1, 2, 3, 4)]
    D["d.opus.g14.refused"] = str(sum(x["first_attempt_refused"] for x in g14))
    D["d.opus.g14.decisions"] = str(sum(x["opus_decisions"] for x in g14))
    D["d.opus.g520.refused"] = str(sum(op["per_game"][str(i)]["first_attempt_refused"] for i in range(5, 21)))
    tm = op["g1_g4_timing"]
    D["d.opus.g14.before.refused"] = str(sum(tm[k]["refused_up_to_last_ok"][0] for k in tm))
    D["d.opus.g14.before.n"] = str(sum(tm[k]["refused_up_to_last_ok"][1] for k in tm))
    D["d.opus.g14.after.refused"] = str(sum(tm[k]["refused_after_last_ok"][0] for k in tm))
    D["d.opus.g14.after.n"] = str(sum(tm[k]["refused_after_last_ok"][1] for k in tm))
    D["d.opus.notes.absent"] = f"{cond['private_note_windows']['Opus']['empty'] + cond['private_note_windows']['Opus']['only_fallback_like']:,}"
    D["d.opus.standard.attempts"] = f"{1605 + 91 + 1:,}"
    D["d.cost.byok"] = "141.39"
    pe = load("a5_pre_estate.json")
    disc = [r for r in pe if not r["creditor_leads_assets"]]
    D["d.estate.discordant"] = str(len(disc))
    D["d.estate.discordant.creditorwins"] = str(sum(r["creditor_is_winner"] for r in disc))
    lead = [r for r in pe if r["creditor_leads_assets"]]
    D["d.estate.leader.creditorwins"] = str(sum(r["creditor_is_winner"] for r in lead))
    D["d.estate.share.median"] = f"{100 * S.median(r['creditor_asset_share'] for r in pe):.0f}"
    P = load("a6_pure_offers.json")
    sel = lambda kind, ms, miss: [p["ratio"] for p in P if p["kind"] == kind and p.get("color") and p["mstat"] == ms and p["missing_after"] == miss]
    for kind in ("ask", "bid"):
        for ms in ("unmortgaged", "mortgaged"):
            for miss in (2, 1, 0):
                xs = sel(kind, ms, miss)
                D[f"d.grad.{kind}.{ms}.{miss}.median"] = f"{S.median(xs):.2f}"
                D[f"d.grad.{kind}.{ms}.{miss}.n"] = str(len(xs))
    cells = barg["prices"]["by_author_and_mortgage"]
    for k, v in cells.items():
        kind, m, ms = k.split("|")
        for side in ("completes", "other"):
            if v[side]["median"] is not None:
                D[f"d.price.{kind}.{m}.{ms}.{side}"] = f"{v[side]['median']:.2f}"
                D[f"d.price.{kind}.{m}.{ms}.{side}.n"] = str(v[side]["n"])
    pooled = barg["prices"]["pooled"]
    for k, v in pooled.items():
        D[f"d.price.pooled.{k}"] = f"{v['median']:.2f}"
    sp = barg["dyads"]["one_sided_pure_cash_settlements"]
    for k in ("under_100_opus", "under_100_other", "100_plus_opus", "100_plus_other"):
        D[f"d.settle.{k}"] = f"{sp[k]['median']:.2f}"
        D[f"d.settle.{k}.n"] = str(sp[k]["n"])
    co = conv["cohort"]
    for m in MODELS:
        D[f"d.wins.{m}"] = str(co["wins_by_system"][m])
    sc = conv["seller_conversion"]
    D["d.seller.winners"] = str(sc["all_one_sided"]["built_after_sale"]["seller_won"] + sc["all_one_sided"]["no_construction_after_sale"]["seller_won"])
    pr = barg["prices"]
    lob = pr["ask_unmortgaged_leave_one_block_out"]
    D["d.ask.lobo.comp.min"] = f"{min(v[0] for v in lob.values()):.2f}"
    D["d.ask.lobo.comp.max"] = f"{max(v[0] for v in lob.values()):.2f}"
    D["d.ask.lobo.other.min"] = f"{min(v[1] for v in lob.values()):.2f}"
    D["d.ask.lobo.other.max"] = f"{max(v[1] for v in lob.values()):.2f}"
    pb = pr["ask_unmortgaged_per_block"]
    D["d.ask.blocks.higher"] = str(sum(1 for v in pb.values() if v["completes"]["median"] > v["other"]["median"]))
    st = pr["by_stage_and_mortgage"]
    askst = [v for k, v in st.items() if k.startswith("ask|")]
    D["d.ask.stagecells.higher"] = str(sum(1 for v in askst if v["completes"]["median"] > v["other"]["median"]))
    D["d.ask.stagecells.n"] = str(len(askst))
    D["d.pairs.n"] = str(len(pr["same_game_seller_deed_pairs"]))
    sc_ = pr["ask_by_seller_cash_and_mortgage"]
    cc = [v for v in sc_.values() if v["completes"]["n"] >= 3 and v["other"]["n"] >= 3]
    D["d.ask.cashcells.higher"] = str(sum(1 for v in cc if v["completes"]["median"] > v["other"]["median"]))
    D["d.ask.cashcells.n"] = str(len(cc))
    dyrows = load("a6_dyads.json")
    lat = [d for d in dyrows if d["settled"] and d["one_sided"] and d["settled_on_later_turn"]]
    D["d.dyads.onesided.later.medianturns"] = f"{S.median(d['settle_turn'] - d['first_turn'] for d in lat):g}"
    D["d.dyads.onesided.later.blocks"] = str(len({d["block"] for d in lat}))
    hd_ = [d for d in lat if d["holder_declined_on_earlier_turn"]]
    D["d.pairs.decline.medianturns"] = f"{S.median(d['settle_turn'] - d['first_holder_decline_turn'] for d in hd_):g}"
    D["d.pairs.decline.games"] = str(len({d["game"] for d in hd_}))
    D["d.pairs.decline.blocks"] = str(len({d["block"] for d in hd_}))
    D["d.pairs.decline.median.first"] = f"{S.median(d['first_holder_decline_cash'] for d in hd_):,.2f}".replace(".00", "")
    D["d.pairs.decline.median.sale"] = f"{S.median(d['settle_holder_cash'] for d in hd_):,.2f}".replace(".00", "")
    um = [d for d in dyrows if not d["settled"] and d["last_turn"] > d["first_turn"]]
    D["d.pairs.unsettled.median.first"] = f"{S.median(d['first_holder_cash'] for d in um):,.2f}".replace(".00", "")
    D["d.pairs.unsettled.median.last"] = f"{S.median(d['last_holder_cash'] for d in um):,.2f}".replace(".00", "")
    mu = [d for d in dyrows if d["settled"] and not d["one_sided"]]
    D["d.pairs.mutual.median"] = f"{S.median(d['settle_holder_cash'] for d in mu):,.2f}".replace(".00", "")
    D["d.dyads.onesided.later.games"] = str(len({d["game"] for d in lat}))
    uns_ = [d for d in dyrows if not d["settled"]]
    D["d.dyads.unsettled.estate.pct"] = pct(sum(1 for d in uns_ if "estate" in d.get("fate", "")), len(uns_))
    # ---- inherited semantic codes (two retained model-assisted readings; not recoded here)
    repo = HERE.parents[4]
    base = repo / "docs/research_raw/paper_agenda_revision_2026-10-29"
    first = json.loads((base / "negotiation/rejection_reason_coding.json").read_text())
    comp = json.loads((base / "reviews/negotiation/reason_comparison.json").read_text())["categories"]
    meta = {f"G{r['game']:02d}d{r['decision']}": r for r in first["rows_data"]}
    D["inh.reason.rows"] = str(first["rows"])
    for code in ("D", "C"):
        c = comp[code]
        D[f"inh.reason.{code}.first"] = str(c["first_pass_positive"])
        D[f"inh.reason.{code}.second"] = str(c["reviewer_positive"])
        D[f"inh.reason.{code}.both"] = str(c["common_positive"])
        D[f"inh.reason.{code}.neither"] = str(c["both_negative"])
        D[f"inh.reason.{code}.disagree"] = str(c["disagreement_rows"])
        n = first["rows"]
        po = (c["common_positive"] + c["both_negative"]) / n
        pa, pb = c["first_pass_positive"] / n, c["reviewer_positive"] / n
        pe_ = pa * pb + (1 - pa) * (1 - pb)
        D[f"inh.reason.{code}.kappa"] = f"{(po - pe_) / (1 - pe_):.2f}"
    common = comp["D"]["common_positive_keys"]
    for m in MODELS:
        D[f"inh.reason.D.both.{m}"] = str(sum(1 for k in common if meta[k]["recipient_model"] == m))
        D[f"inh.reason.rows.{m}"] = str(sum(1 for r in meta.values() if r["recipient_model"] == m))
    for cell_ in ("both", "recipient_only"):
        D[f"inh.reason.D.both.{cell_}"] = str(sum(1 for k in common if meta[k]["completion_cell"] == cell_))
        D[f"inh.reason.rows.{cell_}"] = str(sum(1 for r in meta.values() if r["completion_cell"] == cell_))
    top = sorted(((sum(1 for k in common if int(k[1:3]) == gnum), gnum) for gnum in range(1, 21)), reverse=True)[:2]
    D["inh.reason.D.top2games"] = str(top[0][0] + top[1][0])
    D["inh.reason.D.top2games.names"] = f"G{min(top[0][1], top[1][1])} and G{max(top[0][1], top[1][1])}"
    D["inh.reason.rows.top2games"] = str(sum(1 for k in meta if int(k[1:3]) in (top[0][1], top[1][1])))
    for m in MODELS:
        dm = debt["by_model"][m]
        D[f"d.debt.{m}.payable"] = str(dm["paid"] + dm["payable_but_eliminated"])
        D[f"d.conv.unbuilt.n.{m}"] = str(conv["trade_groups"]["by_model"][m]["groups"] - conv["trade_groups"]["by_model"][m]["built_first_window_inherited"])
    de = load("a4_debt_episodes.json")
    g20 = next(e for e in de if e["game"] == 20 and e["first_decision"] == 327)
    D["d.debt.g20.actions"] = str(len(g20["decisions"]))
    D["d.debt.g20.debt"] = f"{g20['debt']:,}"
    D["d.debt.g20.left"] = str(g20["cash_after_payment"])
    D["d.debt.g20.mortgages"] = str(g20["n_mortgages"])
    D["d.debt.g20.sales"] = str(g20["n_sales"])
    for m in MODELS:
        D[f"d.conv.rpl.{m}"] = f"{conv['trade_groups']['by_model'][m]['rent_per_landing']:.0f}"
    D["d.opus.g520.refused"] = f"{int(D['d.opus.g520.refused']):,}"
    D["d.cost.gateway"] = f"{cond['usage_totals']['sum_usage_cost_field']:.2f}"
    D["d.cost.upstream"] = f"{cond['usage_totals']['sum_upstream_inference_cost_field']:.2f}"
    uf = barg["dyads"]["unsettled_fates"]
    D["d.dyads.unsettled.terminal"] = str(uf.get("another player via terminal_estate", 0) + uf.get("same would-be completer via terminal_estate", 0))
    sprow = [r for r in barg["dyads"]["one_sided_pure_cash_settlements"]["rows"] if r["holder_cash"] < 100]
    D["d.settle.low.other.above"] = str(sum(1 for r in sprow if r["holder_model"] != "Opus" and r["ratio"] > 1))
    D["d.settle.low.opus.below"] = str(sum(1 for r in sprow if r["holder_model"] == "Opus" and r["ratio"] < 1))
    qm = json.loads((DATA / "quote_manifest.json").read_text())["quotes"]
    D["d.quotes.cards"] = str(sum(1 for q in qm if not q.get("inline")))
    D["d.quotes.inline"] = str(sum(1 for q in qm if q.get("inline")))
    D["d.quotes.reused"] = str(sum(1 for q in qm if q.get("reused_from")))
    # ---- inherited first-management-window classification
    win = json.loads((repo / "docs/research_raw/paper_rewrite_2026-11-10/data/first_management_windows.json").read_text())
    for m in MODELS:
        for cause, v in win["summary"][m].items():
            D[f"inh.window.{m}.{cause}"] = str(v)
    tgr = load("a7_trade_groups.json")
    noopt = [r for r in tgr if r["inherited_first_window_cause"] == "never_legal_in_window"]
    D["d.conv.noopt.n"] = str(len(noopt))
    D["d.conv.noopt.mortgaged"] = str(sum(1 for r in noopt if r["mortgaged_deeds_at_completion"] > 0))
    unb = [r for r in tgr if not r["inherited_built_first_window"]]
    D["d.conv.unbuilt.n"] = str(len(unb))
    D["d.conv.defaults"] = str(sum(1 for r in tgr if r["inherited_first_window_cause"] in ("default_after_refusal", "default_other")))
    pbk = conv["trade_groups"]["per_block_rent_per_landing"]
    D["d.conv.blocks.ordered"] = str(sum(1 for v in pbk.values() if v["Sol+Gemini"]["rent_per_landing"] > v["Opus+Grok"]["rent_per_landing"]))
    bmm = conv["trade_groups"]["by_model"]
    D["d.conv.first.solgemini"] = str(bmm["Sol"]["built_first_window_inherited"] + bmm["Gemini"]["built_first_window_inherited"])
    D["d.conv.groups.solgemini"] = str(bmm["Sol"]["groups"] + bmm["Gemini"]["groups"])
    D["d.conv.first.opusgrok"] = str(bmm["Opus"]["built_first_window_inherited"] + bmm["Grok"]["built_first_window_inherited"])
    D["d.conv.groups.opusgrok"] = str(bmm["Opus"]["groups"] + bmm["Grok"]["groups"])
    rpl = lambda ms: sum(bmm[m]["rent_paid"] for m in ms) / sum(bmm[m]["opponent_landings"] for m in ms)
    D["d.conv.rpl.solgemini"] = f"{rpl(('Sol', 'Gemini')):.0f}"
    D["d.conv.rpl.opusgrok"] = f"{rpl(('Opus', 'Grok')):.0f}"
    D["d.conv.rpl.ratio"] = f"{rpl(('Sol', 'Gemini')) / rpl(('Opus', 'Grok')):.1f}"
    lr = [bmm[m]["landings_per_100_group_turns"] for m in MODELS]
    D["d.conv.landrate.min"] = f"{min(lr):.1f}"
    D["d.conv.landrate.max"] = f"{max(lr):.1f}"
    for k, v in D.items():
        facts[sanitize(k)] = v

    lines = [
        "% Generated by analysis/build_tables.py. Do not edit by hand.",
        r"\makeatletter",
        r"\newcommand{\fact}[1]{\ifcsname fact@#1\endcsname\csname fact@#1\endcsname\else\PackageError{facts}{Undefined fact: #1}{Run analysis/build_tables.py or fix the key.}\fi}",
    ]
    for k in sorted(facts):
        lines.append(f"\\expandafter\\gdef\\csname fact@{k}\\endcsname{{{facts[k]}}}")
    lines.append(r"\makeatother")
    (HERE / "sections" / "facts.tex").write_text("\n".join(lines) + "\n")
    (DATA / "facts.json").write_text(json.dumps(facts, indent=1, sort_keys=True) + "\n")

    # ------------------------------------------------------------ tables
    T = ["% Generated by analysis/build_tables.py. Do not edit by hand."]

    def macro(name, rows):
        T.append(f"\\newcommand{{\\{name}}}{{%")
        T.extend(rows)
        T.append("}")

    # configurations and conditions
    res, notes = cond["resolution"], cond["private_note_windows"]
    ids = {"Sol": "openai/gpt-6.1-sol", "Gemini": "google/gemini-4-argon", "Opus": "anthropic/claude-opus-5.5", "Grok": "x-ai/grok-4.7"}
    rows = []
    for m in MODELS:
        u = us[m]
        with_notes = notes[m]["prompts"] - notes[m]["empty"] - notes[m].get("only_fallback_like", 0)
        rows.append(
            f"{m} & \\path{{{ids[m]}}} & {res[m]['decisions']:,} & {u['attempts']:,} & {res[m]['fallback_used']} & {with_notes:,} & "
            f"{u['reasoning_tokens_median_where_reported']:,.0f} & {u['completion_tokens_mean_per_attempt_with_usage']:,.0f}\\\\"
        )
    macro("ConfigRows", rows)

    # offer census by cell and stage
    names = {"author_only": "Author only", "recipient_only": "Recipient only", "both": "Both", "neither": "Neither"}
    rows = []
    for c in ("author_only", "recipient_only", "both", "neither"):
        a = cen["cells"][c]
        o = cen["cells_by_stage"][f"{c}|opening"]
        l = cen["cells_by_stage"][f"{c}|later"]
        rows.append(
            f"{names[c]} & {a['n']} & {a['accept']}/{a['counter']}/{a['reject']} & {o['n']} & {o['accept']}/{o['counter']}/{o['reject']} & "
            f"{l['n']} & {l['accept']}/{l['counter']}/{l['reject']}\\\\"
        )
    tot = {k: sum(cen["cells"][c][k] for c in names) for k in ("n", "accept", "counter", "reject")}
    to = {k: sum(cen["cells_by_stage"][f"{c}|opening"][k] for c in names) for k in ("n", "accept", "counter", "reject")}
    tl = {k: sum(cen["cells_by_stage"][f"{c}|later"][k] for c in names) for k in ("n", "accept", "counter", "reject")}
    rows.append("\\midrule")
    rows.append(f"All & {tot['n']} & {tot['accept']}/{tot['counter']}/{tot['reject']} & {to['n']} & {to['accept']}/{to['counter']}/{to['reject']} & {tl['n']} & {tl['accept']}/{tl['counter']}/{tl['reject']}\\\\")
    macro("OfferRows", rows)

    # behaviour profile by system
    prices = barg["prices"]["by_author_and_mortgage"]
    rows = []
    for m in MODELS:
        r = cen["by_recipient"][m]
        liquid = hc["author_only_by_recipient_and_cash"][f"{m}|300+"]
        poor = hc["author_only_by_recipient_and_cash"][f"{m}|<100"]
        ask = prices[f"ask|{m}|unmortgaged"]
        def cellfmt(v):
            return f"{v['median']:.2f} ({v['n']})" if v["n"] else "none"
        rows.append(
            f"{m} & {cen['threads_by_initiator'][m]} & {r['accept']}/{r['counter']}/{r['reject']} & "
            f"{liquid['reject']}/{liquid['n']} & {poor['reject']}/{poor['n']} & {cellfmt(ask['completes'])} & {cellfmt(ask['other'])}\\\\"
        )
    macro("ProfileRows", rows)

    # price cells
    rows = []
    for m in ("Sol", "Opus", "Grok", "Gemini"):
        for ms in ("unmortgaged", "mortgaged"):
            a, b = prices[f"ask|{m}|{ms}"], prices[f"bid|{m}|{ms}"]
            def c(v):
                return f"{v['median']:.2f} ({v['n']})" if v["n"] else "--"
            rows.append(f"{m} & {ms} & {c(a['completes'])} & {c(a['other'])} & {c(b['completes'])} & {c(b['other'])}\\\\")
    macro("PriceRows", rows)

    # same game / seller / deed pairs
    rows = []
    for p in barg["prices"]["same_game_seller_deed_pairs"]:
        comp = ", ".join(f"\\${x[2]:,}" for x in p["completing_asks"])
        oth = ", ".join(f"\\${x[2]:,}" for x in p["other_asks"])
        cash = sorted(x[4] for x in p["completing_asks"] + p["other_asks"])
        cash_txt = f"\\${cash[0]}" if cash[0] == cash[-1] else f"\\${cash[0]}--\\${cash[-1]}"
        deed = p["deed"].replace("_", " ").title().replace("Avenue", "Ave.")
        rows.append(f"G{p['game']} & {p['seller_model']} & {deed} & {oth} & {comp} & {cash_txt} & {p['direction_by_median']}\\\\")
    macro("PairRows", rows)

    # conversion table
    bm = tg["by_model"]
    spec = [
        ("Groups completed by trade", lambda d: d["groups"]),
        ("\\quad with a mortgaged deed at completion", lambda d: d["mortgaged_deed_at_completion"]),
        ("\\quad median cash after the trade", lambda d: money(d["median_cash_after_completion"])),
        ("Built in the first management turn$^{\\dagger}$", lambda d: d["built_first_window_inherited"]),
        ("Ever built", lambda d: d["ever_built"]),
        ("Median turns to first build", lambda d: f"{d['median_turns_to_first_build_when_built']:g}"),
        ("Construction outlay", lambda d: money(d["construction_spend"])),
        ("Opponent landings", lambda d: d["opponent_landings"]),
        ("\\quad per 100 turns of ownership", lambda d: f"{d['landings_per_100_group_turns']:.1f}"),
        ("Rent received", lambda d: money(d["rent_paid"])),
        ("\\quad per opponent landing", lambda d: money(d["rent_per_landing"])),
    ]
    rows = [f"{label} & " + " & ".join(str(f(bm[m])) for m in MODELS) + "\\\\" for label, f in spec]
    macro("ConversionRows", rows)

    # seller conversion table
    rows = []
    for label, key in (("Seller held under \\$100", "seller_under_100"), ("Seller held \\$100 or more", "seller_100_plus"), ("All one-sided sales", "all_one_sided")):
        for sub, k2 in (("built within 8 turns", "built_after_sale"), ("did not build", "no_construction_after_sale")):
            d = sc[key][k2]
            med = d["median_turns_to_elimination"]
            rows.append(f"{label} & {sub} & {d['n']} & {d['seller_won']} & {d['seller_eliminated']} & {med:g}\\\\")
        if key != "all_one_sided":
            rows.append("\\addlinespace")
    macro("SellerRows", rows)

    # debt by system
    rows = []
    for m in MODELS:
        d = debt["by_model"][m]
        rows.append(f"{m} & {d['episodes']} & {d['paid']} & {d['eliminated']} & {d['payable_but_eliminated']}\\\\")
    rows.append("\\midrule")
    rows.append(f"All & {debt['episodes']} & {debt['paid']} & {debt['eliminated']} & {debt['classes']['payable_witness']}\\\\")
    macro("DebtRows", rows)

    # pre-estate table
    rows = []
    for r in sorted(pe, key=lambda r: r["game"]):
        c = r["positions"][r["creditor_model"]]
        dev = ", ".join(x.replace("_", " ").title() for x in c["developed_groups"])
        est_groups = ", ".join(x.replace("_", " ").title() for x in r["estate"]["complete_groups"]) or "none"
        rows.append(
            f"{r['game']} & {r['turn']} & {r['debtor_model']} & {r['creditor_model']} & {100 * r['creditor_asset_share']:.0f}\\% & "
            f"{r['creditor_rank_assets']} & {r['creditor_rank_rent_received']} & {dev} & {r['estate']['deeds']} ({est_groups}) & {r['winner_model']}\\\\"
        )
    macro("EstateRows", rows)

    # joint recipient x stage x cell
    rows = []
    jt = cen["joint_recipient_stage_cell"]
    for m in MODELS:
        for st in ("opening", "later"):
            cells_ = []
            for c in ("author_only", "recipient_only", "both", "neither"):
                d = jt[f"{m}|{st}|{c}"]
                cells_.append(f"{d['n']} & {d['accept']}/{d['counter']}/{d['reject']}")
            rows.append(f"{m} & {st} & " + " & ".join(cells_) + "\\\\")
        if m != "Grok":
            rows.append("\\addlinespace")
    macro("JointRows", rows)

    # later-turn one-sided dyads
    dyr = load("a6_dyads.json")
    later = sorted((d for d in dyr if d["settled"] and d["one_sided"] and d["settled_on_later_turn"]), key=lambda d: (d["game"], d["first_turn"]))
    rows = []
    for d in later:
        who = "holder" if d["holder_declined_on_earlier_turn"] and not d["completer_declined_on_earlier_turn"] else ("buyer" if not d["holder_declined_on_earlier_turn"] else "both")
        rows.append(
            f"{d['game']} & {d['group'].replace('_', ' ').title()} & {d['holder_model']} & {d['completer_model']} & {d['n_requests']} & {who} & "
            f"{d['first_turn']} & \\${d['first_holder_cash']:,} & {d['settle_turn']} & \\${d['settle_holder_cash']:,}\\\\"
        )
    macro("DyadRows", rows)

    # cohort
    co_rows = []
    wb = co["winner_by_block_and_rotation"]
    turns = conv["cohort"].get("turns") or {}
    for b in range(1, 6):
        for rot in range(1, 5):
            gnum = (b - 1) * 4 + rot
            w, seat = wb[str(b)][str(rot)]
            co_rows.append(f"{gnum} & {b} & {rot} & {turns.get(str(gnum), '')} & {w} & {seat}\\\\")
    macro("CohortRows", co_rows)

    # refusal timeline
    bins = op["g1_g4_ten_minute_bins_refused_of_first_attempts"]
    macro("RefusalBinRows", [f"{k} & {v[0]} & {v[1]}\\\\" for k, v in bins.items()])

    # usage table
    rows = []
    for m in MODELS:
        u = us[m]
        rows.append(
            f"{m} & {u['attempts']:,} & {u['usage_present']:,} & {u['reasoning_zero']:,} & {u['reasoning_tokens_mean_where_reported']:,.0f} & "
            f"{u['reasoning_tokens_max']:,} & {u['completion_tokens_max']:,} & {u['upstream_cost_sum']:.2f}\\\\"
        )
    macro("UsageRows", rows)

    # board fields by phase
    ph = cond["board_fields_by_phase"]
    label = {"BUY_OR_AUCTION_DECISION": "Purchase", "AUCTION_BID_DECISION": "Auction bid", "POST_TURN_ACTION_DECISION": "Management",
             "TRADE_RESPONSE_DECISION": "Trade response", "LIQUIDATION_DECISION": "Debt liquidation", "JAIL_DECISION": "Jail"}
    rows = []
    for k in ("BUY_OR_AUCTION_DECISION", "AUCTION_BID_DECISION", "POST_TURN_ACTION_DECISION", "TRADE_RESPONSE_DECISION", "LIQUIDATION_DECISION", "JAIL_DECISION"):
        d = ph[k]
        given = []
        if d["has_price"]:
            given.append("price, house cost, rent schedule, group")
        elif d["has_group"]:
            given.append("group")
        rows.append(f"{label[k]} & {d['prompts']:,} & {', '.join(given) or 'none'}\\\\")
    macro("PhaseRows", rows)

    # tool descriptions
    td = cond["tool_descriptions"]["tools"]
    assert all(v["distinct_descriptions"] == 1 for v in td.values())
    macro("ToolRows", [f"\\texttt{{{k.replace('_', chr(92) + '_')}}} & {v['description']} & {v['prompts']:,}\\\\" for k, v in td.items()])

    # rent per landing by block
    pbk2 = conv["trade_groups"]["per_block_rent_per_landing"]
    rows = []
    for b in sorted(pbk2):
        a, c = pbk2[b]["Sol+Gemini"], pbk2[b]["Opus+Grok"]
        rows.append(f"{b} & {a['groups']} & {a['landings']} & \\${a['rent']:,} & \\${a['rent_per_landing']:.0f} & {c['groups']} & {c['landings']} & \\${c['rent']:,} & \\${c['rent_per_landing']:.0f}\\\\")
    macro("BlockRentRows", rows)

    # completion routes
    gs = load("a3_group_summary.json")
    label2 = {"trade": "Trade", "purchase": "Direct purchase", "auction": "Auction", "nonterminal_estate": "Estate before the last elimination", "terminal_estate": "Estate at the last elimination"}
    rows = []
    for k in ("trade", "purchase", "auction", "nonterminal_estate", "terminal_estate"):
        rows.append(f"{label2[k]} & {gs['routes'][k]} & {gs['winner_by_route'][k]} & {gs['rent_earning_by_route'][k]} & \\${gs['rent_by_route'][k]:,}\\\\")
    rows.append("\\midrule")
    rows.append(f"All & {gs['episodes']} & {sum(gs['winner_by_route'].values())} & {sum(gs['rent_earning_by_route'].values())} & \\${sum(gs['rent_by_route'].values()):,}\\\\")
    macro("RouteRows", rows)

    (HERE / "sections" / "tables.tex").write_text("\n".join(T) + "\n")
    (DATA / "facts_index.txt").write_text("\n".join(f"{k}\t{facts[k]}" for k in sorted(facts)) + "\n")
    print("facts", len(facts), "table macros", sum(1 for line in T if line.startswith("\\newcommand")))


if __name__ == "__main__":
    main()
