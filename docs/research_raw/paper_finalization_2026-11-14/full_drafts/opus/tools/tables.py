"""Generate LaTeX tables, the TikZ figure and appendix text from data/*.json.

Inputs are the outputs of finance.py, channels.py, named_actions.py,
bargaining.py and provenance.py plus the hand-authored data/sixteen_rubric.json.
Numbers in generated tables are never typed by hand. Read-only with respect to
all records outside this draft folder.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict

import lib

D = lib.DRAFT / "data"
S = lib.DRAFT / "sections"
fin = json.loads((D / "finance_census.json").read_text())
rows = fin["rows"]
summ = fin["summary"]
ch = json.loads((D / "focal_channels.json").read_text())["records"]
rub = json.loads((D / "sixteen_rubric.json").read_text())
barg = json.loads((D / "bargaining_census.json").read_text())
prov = json.loads((D / "provenance.json").read_text())
scan = json.loads((D / "named_action_scan.json").read_text())["summary"]
MODELS = ["Sol", "Gemini", "Opus", "Grok"]
IDS = {"Sol": "openai/gpt-6.1-sol", "Gemini": "google/gemini-4-argon",
       "Opus": "anthropic/claude-opus-5.5", "Grok": "x-ai/grok-4.7"}


def money(x: int) -> str:
    return f"\\${x:,}"


def esc(t: str | None) -> str:
    if t is None:
        return ""
    rep = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        "→": r"$\rightarrow$", "≈": r"$\approx$", "×": r"$\times$", "≥": r"$\geq$", "≤": r"$\leq$",
        "‑": "-", " ": " ",
    }
    out = "".join(rep.get(c, c) for c in t)
    out = out.replace("\n\n", "\n").strip()
    return out.replace("\n", r"\newline ")


def write(name: str, text: str) -> None:
    (S / name).write_text(text.rstrip() + "\n")


def roster():
    pay = [r for r in rows if r["category"] == "payable"]
    lines = []
    for m in MODELS:
        ep = [r for r in rows if r["model"] == m]
        pm = [r for r in pay if r["model"] == m]
        lines.append(f"{m} & \\path{{{IDS[m]}}} & {prov['decisions_by_model'][m]:,} & {len(ep)} & {sum(r['outcome']=='paid' for r in pm)}/{len(pm)} \\\\")
    write("gen_roster.tex", "\n".join(lines))


def firstmenu():
    def reg(r):
        if r["Ustar"] < r["D"]:
            return 2
        if r["U0"] >= r["D"]:
            return 0
        return 1
    names = [r"$U_0\ge D$", r"$U_0<D\le U_*$", r"$U_*<D$"]
    lines = []
    for k, nm in enumerate(names):
        rr = [r for r in rows if reg(r) == k]
        cells = []
        for m in MODELS:
            mm = [r for r in rr if r["model"] == m]
            cells.append(f"{sum(r['first_action']=='declare_bankruptcy' for r in mm)}/{len(mm)}")
        tot = f"{sum(r['first_action']=='declare_bankruptcy' for r in rr)}/{len(rr)}"
        lines.append(f"{nm} & " + " & ".join(cells) + f" & {tot} \\\\")
    write("gen_firstmenu.tex", "\n".join(lines))


CAT = {"explicit_dependency": "Explicit", "ordered_route": "Ordered", "inclusive_budget": "Inclusive",
       "tentative": "Tentative", "omission": "Omission"}


def sixteen():
    by = {(r["game"], r["decision"]): r for r in rows}
    chans = {(c["game"], c["decision"]): c for c in ch}
    lines = []
    checks = []
    for c in rub["cases"]:
        k = (c["game"], c["decision"])
        r = by[k]
        cc = chans[k]
        channel = "note" if cc["applied_private_note"] else "provider"
        tot = []
        for t in c["stated_totals"]:
            v = t["value"]
            ref = {"U0": r["U0"], "Ustar": r["Ustar"], "M0": r["M0"], "cash_after": r["cash_after_payment"],
                   "U0_minus_C": r["U0"] - r["C"], "route": None}[t["compare"]]
            ok = (ref == v) if ref is not None else None
            checks.append({"case": f"G{k[0]} d{k[1]}", "label": t["label"], "stated": v, "compare": t["compare"], "record": ref, "match": ok})
            if t["compare"] in ("U0", "Ustar"):
                tot.append(("implied " if t.get("implied") else "") + f"{money(v)}{{\\,}}$=${{\\,}}" + ("$U_0$" if t["compare"] == "U0" else "$U_*$"))
            elif t["compare"] == "cash_after":
                tot.append(f"rem.\\ {money(v)}")
        outcome = f"paid, {money(r['cash_after_payment'])} left" if r["outcome"] == "paid" else "declared"
        lines.append(f"G{k[0]} d{k[1]} & {r['model']} & {channel} & {money(r['D'])} & {money(r['U0'])} & {money(r['Ustar'])} & {CAT[c['category']]} & {'; '.join(tot) if tot else '---'} & {outcome} \\\\")
    write("gen_sixteen.tex", "\n".join(lines))
    lib.write_json("sixteen_numeric_checks.json", checks)
    bad = [x for x in checks if x["match"] is False]
    assert not bad, bad
    return Counter(c["category"] for c in rub["cases"])


def figure():
    by = {(r["game"], r["decision"]): r for r in rows}
    cases = sorted([c for c in rub["cases"]], key=lambda c: by[(c["game"], c["decision"])]["D"])
    scale = 5.2 / 1500.0
    n = len(cases)
    out = [r"\begin{tikzpicture}[x=1cm,y=0.36cm,font=\scriptsize]"]
    for i, c in enumerate(cases):
        r = by[(c["game"], c["decision"])]
        y = n - i
        u0, us, d = r["U0"] * scale, r["Ustar"] * scale, r["D"] * scale
        out.append(f"\\node[anchor=east] at (0,{y}) {{G{c['game']} d{c['decision']} {r['model']}}};")
        out.append(f"\\fill[barpale] (0,{y-0.32}) rectangle ({us:.3f},{y+0.32});")
        out.append(f"\\fill[bardark] (0,{y-0.32}) rectangle ({u0:.3f},{y+0.32});")
        out.append(f"\\draw[debtline,line width=1.1pt] ({d:.3f},{y-0.45}) -- ({d:.3f},{y+0.45});")
        if r["outcome"] != "paid":
            out.append(f"\\node[font=\\footnotesize\\bfseries,text=declared] at ({us+0.18:.3f},{y}) {{$\\times$}};")
    for v in [0, 500, 1000, 1500]:
        out.append(f"\\draw[gray] ({v*scale:.3f},0.4) -- ({v*scale:.3f},0.15) node[below] {{{v:,}}};")
    out.append(f"\\draw[gray] (0,0.4) -- ({1500*scale:.3f},0.4);")
    out.append(r"\end{tikzpicture}")
    write("gen_fig_sixteen.tex", "\n".join(out))


def departures():
    recs = {(c["game"], c["decision"]): c for c in ch}
    order = [(12, 190), (17, 234), (12, 249), (7, 286), (9, 194), (17, 396), (19, 224), (20, 273), (18, 344)]
    desc = {
        (12, 190): ("covers", "note and provider field total \\$408; note: payment impossible"),
        (17, 234): ("covers", "note totals \\$530; note: payment impossible"),
        (12, 249): ("covers", "content names a sale; note: ``bankruptcy is wrong''"),
        (7, 286): ("short", "content declares, citing the correct \\$1,291"),
        (9, 194): ("short", "content declares; note: ``Declare bankruptcy now''"),
        (17, 396): ("short", "content declares; note calls the sale ``forced''"),
        (19, 224): ("short", "content declares; note asserts a false precondition"),
        (20, 273): ("short", "content declares; note: ``Declare now''"),
        (18, 344): ("short", "note: mortgaging makes the creditor pay a 10\\% fee"),
    }
    act = {"declare_bankruptcy": "declare", "mortgage_property": "mortgage", "sell_houses_or_hotel": "sell"}
    lines = []
    for k in order:
        c = recs[k]
        cov, d = desc[k]
        lines.append(f"G{k[0]} d{k[1]} & {c['model']} & {cov} & {act[c['applied_action']]} & {d} \\\\")
    write("gen_departures.tex", "\n".join(lines))


def bargaining():
    lines = []
    for m in MODELS:
        x = barg["by_recipient_model"][m]
        lines.append(f"{m} & {x['n']} & {x['accept']} & {x['counter']} & {x['reject']} \\\\")
    write("gen_responses.tex", "\n".join(lines))

    def cell(x):
        return f"{x['reject']}/{x['n']}"
    pops = [("Opening swaps", barg["opening_swaps"]),
            ("\\quad no Grok authors", barg["opening_swaps_no_grok_authors"]),
            ("\\quad no conflicting calls", barg["opening_swaps_no_conflicting_openings"]),
            ("Opening cash bids", barg["opening_cash_bids"]),
            ("Later swaps", barg["later_swaps"])]
    keymap = {"Opening swaps": "All swaps", "\\quad no Grok authors": "No Grok authors",
              "\\quad no conflicting calls": "No conflicting openings", "Opening cash bids": "Cash bids"}
    out = []
    for name, p in pops:
        rs = barg["retained_block_summaries"].get(keymap.get(name, ""), {})
        blocks = rs.get("block_gaps")
        rng = f"{min(blocks):.1f} to {max(blocks):.1f}" if blocks else "---"
        out.append(f"{name} & {cell(p['proposer_only'])} & {cell(p['neither'])} & {p['gap_pp']:.1f} & {rng} \\\\")
    write("gen_contrast.tex", "\n".join(out))


def app_texts():
    recs = {(c["game"], c["decision"]): c for c in ch}
    rubk = {(c["game"], c["decision"]): c for c in rub["cases"]}
    out = []
    for k in [(c["game"], c["decision"]) for c in rub["cases"]]:
        c = recs[k]
        r = rubk[k]
        status = f"paid, {money(c['cash_after_payment'])} left" if c["outcome"] == "paid" else "declared bankruptcy"
        out.append(f"\\paragraph{{G{k[0]} d{k[1]}, {c['model']} ({status}; coded {CAT[r['category']].lower()}).}}")
        out.append(f"{{\\footnotesize $C={money(c['C'])}$, $D={money(c['D'])}$, $U_0={money(c['U0'])}$, $U_*={money(c['Ustar'])}$. Applied action: \\texttt{{{esc(c['applied_action'])}}}. Carried own notes in the request: {c['carried_notes_count']}.\\par}}")
        if c["applied_private_note"]:
            out.append(f"\\chan{{Applied private note (attempt 0)}}{{{esc(c['applied_private_note'])}}}")
        else:
            out.append("\\chan{Applied private note}{\\textit{None. The standard attempt was refused; the action-only recovery attempt has no note argument.}}")
        for a in c["attempts"]:
            if a["outcome"] == "refused" and not a["provider_reasoning"]:
                out.append(f"\\chan{{Attempt {a['attempt_index']} ({esc(a['response_condition'])})}}{{\\textit{{Refused; no text returned.}}}}")
                continue
            types = ", ".join(t for t in a["provider_reasoning_detail_types"] if t != "reasoning.encrypted")
            if a["provider_reasoning"]:
                out.append(f"\\chan{{Provider reasoning field, {esc(types)} (attempt {a['attempt_index']}, {esc(a['response_condition'])})}}{{{esc(a['provider_reasoning'])}}}")
            if a["assistant_content"] and a["assistant_content"].strip():
                out.append(f"\\chan{{Assistant content (attempt {a['attempt_index']})}}{{{esc(a['assistant_content'])}}}")
        out.append(f"{{\\footnotesize\\textit{{Coding note.}} Values: {esc(r['values'])}. Accounting: {esc(r['accounting'])}. Route: {esc(r['route'])}.\\par}}")
    write("gen_app_texts.tex", "\n".join(out))


def app_departures():
    recs = [c for c in ch if c["group"] != "necessary_collateral"]
    out = []
    for c in recs:
        out.append(f"\\paragraph{{G{c['game']} d{c['decision']}, {c['model']} ({'payable' if c['group'].startswith('payable') else 'above bound'}).}}")
        out.append(f"{{\\footnotesize $C={money(c['C'])}$, $D={money(c['D'])}$, $U_*={money(c['Ustar'])}$. Applied call: \\texttt{{{esc(c['applied_action'])}}}. Later actions in the episode: {esc(', '.join(a['action'] for a in c['episode_actions'][1:]) or 'none')}.\\par}}")
        out.append(f"\\chan{{Applied private note}}{{{esc(c['applied_private_note'])}}}")
        for a in c["attempts"]:
            if a["provider_reasoning"]:
                txt = a["provider_reasoning"]
                if len(txt) > 1600:
                    txt = txt[:1600].rsplit(" ", 1)[0] + " [...]"
                out.append(f"\\chan{{Provider reasoning field (attempt {a['attempt_index']}){' excerpt' if len(a['provider_reasoning'])>1600 else ''}}}{{{esc(txt)}}}")
            if a["assistant_content"] and a["assistant_content"].strip():
                out.append(f"\\chan{{Assistant content (attempt {a['attempt_index']})}}{{{esc(a['assistant_content'])}}}")
    write("gen_app_departures.tex", "\n".join(out))


def app_offers():
    offers = json.loads(lib.OFFER_FILE.read_text())
    legal = [r for r in offers if r["accept_available"]]
    from bargaining import form  # same classifier

    cells = [("author_only", "Proposer only"), ("recipient_only", "Recipient only"), ("both", "Both"), ("neither", "Neither")]
    out = []
    for stage, rs in [("Opening", [r for r in legal if r["exchange_index"] == 0]), ("Later", [r for r in legal if r["exchange_index"] > 0])]:
        for f in ["Swap", "Cash bid", "Cash ask", "Other"]:
            vals = []
            for ck, _ in cells:
                x = [r for r in rs if form(r) == f and r["completion_cell"] == ck]
                cnt = Counter(r["response"] for r in x)
                vals.append(f"{len(x)} [{cnt['accept_trade']}/{cnt['counter_trade']}/{cnt['reject_trade']}]")
            out.append(f"{stage} & {f} & " + " & ".join(vals) + " \\\\")
    write("gen_app_offers.tex", "\n".join(out))
    strata = []
    for m in MODELS:
        a = barg["opening_swaps_by_proposer"][m]
        b = barg["opening_swaps_by_recipient"][m]
        c = barg["opening_cash_bids_by_recipient"][m]
        def g(x):
            return f"{x['gap_pp']:.1f}" if x["proposer_only"]["n"] >= 5 and x["neither"]["n"] >= 5 else "---"
        strata.append(f"{m} & {a['proposer_only']['reject']}/{a['proposer_only']['n']} & {a['neither']['reject']}/{a['neither']['n']} & {g(a)} & {b['proposer_only']['reject']}/{b['proposer_only']['n']} & {b['neither']['reject']}/{b['neither']['n']} & {g(b)} & {c['proposer_only']['reject']}/{c['proposer_only']['n']} & {c['neither']['reject']}/{c['neither']['n']} & {g(c)} \\\\")
    write("gen_app_strata.tex", "\n".join(strata))
    blocks = []
    for name, key in [("All opening swaps", "All swaps"), ("Without Grok authors", "No Grok authors"), ("Without conflicting openings", "No conflicting openings"), ("Opening cash bids", "Cash bids")]:
        s = barg["retained_block_summaries"][key]
        bg = ", ".join(f"{x:.1f}" for x in s["block_gaps"])
        lo = f"{min(s['leave_one_block_out']):.1f} to {max(s['leave_one_block_out']):.1f}"
        rp = s["resampling_percentiles"]
        alt = s["alternative_resampling"]
        blocks.append(f"{name} & {s['gap_pp']:.1f} & {bg} & {lo} & {rp[0]:.1f} to {rp[1]:.1f} & {alt['Individual games'][0]:.1f} to {alt['Individual games'][1]:.1f} \\\\")
    write("gen_app_blocks.tex", "\n".join(blocks))


def app_cohort():
    out = []
    for c in prov["cohort"]:
        out.append(f"G{c['game']} & {c['seed']} & {c['rotation']} & {', '.join(c['seats'])} & {c['turns']} & {c['winner']} ({c['winner_seat']}) & \\texttt{{{c['source_commit'][:8]}}} \\\\")
    write("gen_app_cohort.tex", "\n".join(out))
    src = []
    for p, h in prov["source_sha256"].items():
        same = len(set(h.values())) == 1
        src.append(f"\\path{{{p}}} & \\texttt{{{h['HEAD'][:16]}}} & {'identical' if same else 'differs'} \\\\")
    write("gen_app_sources.tex", "\n".join(src))


def app_premises():
    prem = json.loads((D / "continuation_premises.json").read_text())
    c = prem["summary"]
    lab = {"hotel_free": "No hotel at entry",
           "initial_cash_and_listed_mortgages_suffice": "Hotels held; cash plus listed mortgages cover $D$",
           "bank_stock_covers_every_hotel_downgrade": "Bank houses $\\ge 4\\times$ hotels held",
           "single_hotel_per_group_recyclable_stock": "One hotel per group; recyclable house stock"}
    out = [f"{lab[k]} & {c[k]} \\\\" for k in ["hotel_free", "initial_cash_and_listed_mortgages_suffice", "bank_stock_covers_every_hotel_downgrade", "single_hotel_per_group_recyclable_stock"]]
    write("gen_app_premises.tex", "\n".join(out))


def app_middle():
    keys = [(3, 228), (3, 356), (3, 461), (3, 482), (18, 428)]
    by = {(r["game"], r["decision"]): r for r in rows}
    out = []
    for k in keys:
        r = by[k]
        hb = ", ".join(f"{g.replace('_', ' ').title()} {n}" for g, n in r["hotels_by_group"].items() if n) or "none"
        out.append(f"G{k[0]} d{k[1]} & {r['model']} & {money(r['C'])} & {money(r['D'])} & {money(r['M0'])} & {money(r['S'])} & {money(r['U0'])} & {r['bank_houses']} & {hb} \\\\")
    write("gen_app_middle.tex", "\n".join(out))


def app_scan():
    out = []
    for m in MODELS:
        x = scan["per_model"][m]
        out.append(f"{m} & {x['liquidation_decisions']} & {x['with_content']} & {x['content_names_action']} & {x['conflicts']} \\\\")
    write("gen_app_scan.tex", "\n".join(out))


def app_prompts():
    for name in ["standard_system_prompt", "recovery_system_prompt"]:
        t = (lib.INTEGRATED / "data" / f"{name}.txt").read_text()
        body = "\n".join(esc(line) if line.strip() else "" for line in t.split("\n"))
        body = body.replace("\n\n", "\n\n")
        write(f"gen_{name}.tex", "{\\footnotesize\\raggedright\\obeylines " + body + "\n}")


def main():
    app_middle()
    app_scan()
    app_prompts()
    roster()
    firstmenu()
    cats = sixteen()
    figure()
    departures()
    bargaining()
    app_texts()
    app_departures()
    app_offers()
    app_cohort()
    app_premises()
    print("categories", dict(cats))
    print("named-action scan", scan["per_model"])


if __name__ == "__main__":
    main()
