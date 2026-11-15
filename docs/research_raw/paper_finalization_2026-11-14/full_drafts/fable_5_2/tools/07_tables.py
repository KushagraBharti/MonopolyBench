"""Generate LaTeX fragments, the machine-readable supplement and the figure.

Read-only over the saved games and over data/*.json written by scripts 01 to 06.
Every generated table cell is computed here; nothing is typed from memory.
"""
import collections
import csv
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from coding import CARRIED, CODING, TIER_LABEL, TIER_ORDER
from lib import *

C = collections.Counter
eps = read_json("episodes.json")
fin = read_json("finance_summary.json")
tot = read_json("stated_totals.json")
barg = read_json("bargaining_summary.json")
corp = read_json("corpus_summary.json")
SUPP = PKG / "supplement"
SUPP.mkdir(exist_ok=True)
WITNESSED = {(12, 190), (17, 234), (12, 249)}


def k(e):
    return (e["game"], e["first"])


def cat(e):
    if e["ustar"] < e["debt"]:
        return "unpayable"
    if k(e) == (7, 338):
        return "menu_unpayable"
    if e["cash"] + e["m0"] >= e["debt"]:
        return "A"
    if e["u0"] >= e["debt"]:
        return "B"
    return "C"


def out(name, text):
    (SECTIONS / name).write_text(text.rstrip() + "\n")


def para(text):
    """Stored multi-paragraph text to LaTeX, keeping every character."""
    parts = [p for p in (text or "").replace("\r", "").split("\n\n")]
    return r"\par ".join(tex(" ".join(p.split())) for p in parts if p.strip())


FIELD_NAME = {"reasoning.summary": "reasoning summary", "reasoning.text": "reasoning text"}


def texq(text):
    """Author-written text: escape, then turn paired straight quotes into typeset quotes."""
    parts = text.split('"')
    out_ = []
    for i, part in enumerate(parts):
        out_.append(tex(part))
        if i < len(parts) - 1:
            out_.append("``" if i % 2 == 0 else "''")
    return "".join(out_)


def provider_label(types):
    t = [x for x in types if x != "reasoning.encrypted"]
    return FIELD_NAME.get(t[0], t[0]) if t else "none returned"


# ---------------------------------------------------------------- cohort
def cohort():
    rows = []
    for c in corp["cohort"]:
        g = c["game"]
        job = json.loads((run_dir(g).parent / "cloud" / "job.json").read_text())

        def find(x, key):
            if isinstance(x, dict):
                for kk, v in x.items():
                    if kk == key and not isinstance(v, (dict, list)):
                        return v
                    r = find(v, key)
                    if r is not None:
                        return r
            elif isinstance(x, list):
                for v in x:
                    r = find(v, key)
                    if r is not None:
                        return r
            return None

        seed, sha = find(job, "seed"), find(job, "git_sha")
        folder = run_dir(g).parent.name
        turns = int(folder.split("-")[2].replace("turns", ""))
        seats = "/".join(c["seats"][p][0:3] for p in ("p1", "p2", "p3", "p4"))
        wseat = int(c["winner_id"][1:])
        rows.append(dict(game=g, seed=seed, sha=sha, turns=turns, seats=seats, winner=c["winner"], winner_seat=wseat, folder=folder,
                         collection=run_dir(g).parent.parent.name))
    lines = []
    for r in rows:
        lines.append(f"G{r['game']} & {r['seed']} & {r['seats']} & {r['turns']} & {r['winner']} & {r['winner_seat']} & \\texttt{{{r['sha'][:8]}}} & \\path{{{r['folder']}}} \\\\")
    out("gen_cohort_rows.tex", "\n".join(lines))
    write_json("cohort.json", rows)
    wins_by_seat = C(r["winner_seat"] for r in rows)
    return rows, wins_by_seat


# ---------------------------------------------------------------- sixteen
def sixteen():
    nec = [e for e in eps if cat(e) == "C"]
    assert len(nec) == 16
    st_by = {(r["game"], r["first"]): r for r in tot}
    supp, coding_rows, text_blocks, carried_rows = [], [], [], []
    for e in nec:
        g, d = k(e)
        st, rs, lines = load(g)
        r0 = rs[d]
        ch = e["first_channels"]
        cd = CODING[(g, d)]
        whole = {"note": e["first_note"], "provider": ch["provider_text"], "content": ch["assistant_content"], "public": e["first_public"]}
        assert cd["span"] in whole[cd["channel"]], (g, d, cd["span"])
        srow = st_by[(g, d)]
        stated = "full bound" if srow["states_full_bound"] else ("listed-only total" if srow["states_listed_only"] and cd["tier"] == "omission" else "none")
        route_txt = []
        for x in e["route"]:
            if x["action"] == "mortgage":
                route_txt.append(f"mortgage {SHORT[x['space']]} ${x['value']}" + (" (released)" if x["released"] else ""))
            elif x["action"] == "sell":
                n = sum(i["count"] for i in x["items"])
                hot = sum(1 for i in x["items"] if i["kind"] == "HOTEL")
                what = f"{n - hot} house{'s' if n - hot != 1 else ''}" + (f" and {hot} hotel downgrade{'s' if hot != 1 else ''}" if hot else "")
                route_txt.append(f"sell {what} ${x['value']}")
            else:
                route_txt.append("declare bankruptcy")
        # carried notes
        notes = st[d]["prompt_payload"]["game_state"]["memory"]["your_private_thoughts_last_10"]
        kind, cspan, cremark = CARRIED[(g, d)]
        joined = "\n".join(n["thought"] for n in notes)
        if cspan:
            assert cspan in joined, (g, d, cspan)
        assert (kind == "empty") == (len(notes) == 0), (g, d, len(notes))
        supp.append(dict(
            entry=f"G{g} d{d}", game=g, decision=d, decision_id=r0["decision_id"], system=e["model"], turn=e["turn"],
            debt=e["debt"], cash=e["cash"], salvage=e["salvage"], listed_mortgage_value=e["m0"], all_mortgage_value=e["mstar"],
            listed_only_total_U0=e["u0"], full_bound_Ustar=e["ustar"], listed_mortgages=e["listed_mortgages"], listed_sales=e["listed_sales"],
            buildings=e["built"], bank_houses=e["bank_houses"], outcome=e["outcome"], cash_after_payment=e["cash_after"],
            applied_first_action=e["first_action"], applied_first_args=e["first_args"], route=e["route"],
            response_condition=ch["response_condition"], attempts=e["first_attempts"], selected_attempt_index=ch["attempt_index"],
            channels=dict(
                authored_private_note=dict(text=e["first_note"], sha256=text_sha256(e["first_note"]), pointer="final_action.private_thought",
                                           present=bool(e["first_note"])),
                authored_public_message=dict(text=e["first_public"], sha256=text_sha256(e["first_public"]), pointer="final_action.public_message"),
                provider_reasoning_field=dict(text=ch["provider_text"], sha256=text_sha256(ch["provider_text"]),
                                              pointer=f"attempts[{ch['attempt_index']}].raw_response.choices[0].message.reasoning",
                                              detail_types=ch["provider_detail_types"], reported_reasoning_tokens=ch["reasoning_tokens"]),
                assistant_content_not_applied=dict(text=ch["assistant_content"], sha256=text_sha256(ch["assistant_content"]),
                                                   pointer=f"attempts[{ch['attempt_index']}].assistant_content")),
            coding=dict(tier=cd["tier"], evidence_channel=cd["channel"], evidence_span=cd["span"], figures=cd["figures"], other=cd["other"],
                        route_remark=cd["route"], stated_total_number_match=stated,
                        full_bound_figures_found=srow["full_bound_figure"], listed_only_figures_found=srow["listed_only_figure"],
                        coder="one LLM author reading the stored fields; not human annotation"),
            carried_notes=dict(count=len(notes), kind=kind, span=cspan, remark=cremark, turns=[n["turn_index"] for n in notes]),
            source_file=e["source_file"], source_line=e["source_line"], source_file_sha256=file_sha256(decisions_path(g)),
        ))
        chan = "note + provider" if e["first_note"] else "provider only"
        outcome = f"paid, \\${e['cash_after']} left" if e["outcome"] == "paid" else "declared"
        coding_rows.append(
            f"G{g} d{d} & {e['model']} & {money(e['debt'])} & {money(e['u0'])} & {money(e['ustar'])} & {TIER_LABEL[cd['tier']]} & "
            f"{texq(cd['figures'])} {texq(cd['other'])} & {texq(cd['route'])} & {outcome} \\\\\\addlinespace[2pt]")
        # full text block
        head = (f"\\fieldhead{{G{g} d{d}}}{{{e['model']}, turn {e['turn']}. Debt \\${money(e['debt'])}; cash \\${money(e['cash'])}; "
                f"listed-only total \\${money(e['u0'])}; full bound \\${money(e['ustar'])}. "
                f"Applied first action: {tex(e['first_action'].replace('_', ' '))}. "
                f"{'Paid with $' + str(e['cash_after']) + ' left' if e['outcome'] == 'paid' else 'Declared bankruptcy'}"
                f"{' after ' + str(len(e['actions'])) + ' actions' if e['outcome'] == 'paid' else ''}. "
                f"Tier: {TIER_LABEL[cd['tier']].lower()}.}}")
        head = head.replace("Paid with $", "Paid with \\$")
        blk = [head]
        if e["first_note"]:
            blk.append(f"\\fieldtext{{Authored note (applied tool argument, standard response)}}{{{para(e['first_note'])}}}")
        else:
            blk.append("\\fieldabsent{Authored note}{None. The first attempt was refused with no text and the action-only recovery prompt requests no note.}")
        if ch["provider_text"]:
            blk.append(f"\\{'fieldtextlong' if len(ch['provider_text']) > 1500 else 'fieldtext'}{{Provider field ({provider_label(ch['provider_detail_types'])}"
                       f"{', recovery attempt' if not e['first_note'] else ''})}}{{{para(ch['provider_text'])}}}")
        else:
            blk.append("\\fieldabsent{Provider field}{None returned.}")
        if ch["assistant_content"] and not ch["assistant_content"].lstrip().startswith("{"):
            blk.append(f"\\fieldtext{{Assistant content (returned beside the call, not applied)}}{{{para(ch['assistant_content'])}}}")
        elif ch["assistant_content"]:
            blk.append("\\fieldabsent{Assistant content}{Repeats the call arguments as JSON; kept in the supplement.}")
        text_blocks.append("\n".join(blk))
        ckind = {"conditional": "Conditional inventory", "rule": "States the rule", "none": "No capacity figure", "empty": "No notes carried"}[kind]
        carried_rows.append(f"G{g} d{d} & {e['model']} & {len(notes)} & {ckind} & {texq(cremark)} & "
                            f"{'paid' if e['outcome'] == 'paid' else 'declared'} \\\\")
    (SUPP / "sixteen_first_texts.json").write_text(json.dumps(supp, indent=1, ensure_ascii=False) + "\n")
    out("gen_sixteen_coding_rows.tex", "\n".join(coding_rows))
    out("gen_sixteen_texts.tex", "\n\n".join(text_blocks))
    out("gen_carried_rows.tex", "\n".join(carried_rows))
    tiers = C(CODING[k(e)]["tier"] for e in nec)
    by_tier_model = {t: C(e["model"] for e in nec if CODING[k(e)]["tier"] == t) for t in TIER_ORDER}
    carried = C((CARRIED[k(e)][0], e["outcome"]) for e in nec)
    return nec, tiers, by_tier_model, carried


# ---------------------------------------------------------------- departures
def departures():
    sel = [e for e in eps if (e["ustar"] < e["debt"] and e["first_action"] != "declare_bankruptcy") or (cat(e) in "ABC" and e["first_action"] == "declare_bankruptcy")]
    assert len(sel) == 9
    supp = []
    for e in sel:
        ch = e["first_channels"]
        supp.append(dict(entry=f"G{e['game']} d{e['first']}", system=e["model"], debt=e["debt"], cash=e["cash"], listed_only_total_U0=e["u0"],
                         full_bound_Ustar=e["ustar"], bound_covers_debt=e["ustar"] >= e["debt"], menu=e["menu"],
                         applied_first_action=e["first_action"], applied_first_args=e["first_args"], action_named_in_assistant_content=ch["named_in_content"],
                         authored_private_note=e["first_note"], authored_public_message=e["first_public"],
                         assistant_content_not_applied=ch["assistant_content"], provider_reasoning_field=ch["provider_text"],
                         provider_detail_types=ch["provider_detail_types"], later_actions=e["actions"][1:], outcome=e["outcome"],
                         declared_by_player=e["declared"], source_file=e["source_file"], source_line=e["source_line"]))
    (SUPP / "nine_departures.json").write_text(json.dumps(supp, indent=1, ensure_ascii=False) + "\n")

    def clip(text, n):
        text = text or ""
        return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + " [...]"

    blocks = []
    for e in sel:
        g, d = k(e)
        if (g, d) in ((12, 190), (17, 234)):
            continue
        ch = e["first_channels"]
        fa = e["route"][0]
        if fa["action"] == "mortgage":
            applied = f"mortgage {SHORT[fa['space']]} (\\${fa['value']})"
        elif fa["action"] == "sell":
            n = sum(i["count"] for i in fa["items"])
            applied = f"sell {n} house{'s' if n != 1 else ''} (\\${fa['value']})"
        else:
            applied = "declare bankruptcy"
        later = e["actions"][1:]
        end = ("the player then declared" if e["declared"] and later else
               "the engine closed the episode when nothing more was offered" if not e["declared"] else "no later action")
        named = (ch["named_in_content"] or "none").replace("_", " ")
        head = (f"\\fieldhead{{G{g} d{d}}}{{{e['model']}, turn {e['turn']}. Debt \\${money(e['debt'])}; cash \\${money(e['cash'])}; "
                f"full bound \\${money(e['ustar'])}. Applied call: {applied}. Action named in assistant content: {named}. "
                f"Later calls in the episode: {len(later)}; {end}.}}")
        blk = [head]
        blk.append(f"\\fieldtext{{Authored note inside the applied call}}{{{para(e['first_note'])}}}")
        blk.append(f"\\fieldtext{{Public message inside the applied call}}{{{para(e['first_public'])}}}")
        if ch["assistant_content"]:
            blk.append(f"\\fieldtextlong{{Assistant content, not applied{' (first 700 characters)' if len(ch['assistant_content']) > 700 else ''}}}{{{para(clip(ch['assistant_content'], 700))}}}")
        if ch["provider_text"]:
            blk.append(f"\\fieldtextlong{{Provider field ({provider_label(ch['provider_detail_types'])}){' (first 900 characters)' if len(ch['provider_text']) > 900 else ''}}}{{{para(clip(ch['provider_text'], 900))}}}")
        blocks.append("\n".join(blk))
    out("gen_departures.tex", "\n\n".join(blocks))
    return sel


def prompts():
    """Stored system prompts of one refusal and recovery pair, wrapped for print."""
    import textwrap

    def system_text(msgs):
        m = next((m for m in (msgs or []) if m.get("role") == "system"), None)
        if m is None:
            return None
        c = m["content"]
        return c if isinstance(c, str) else "".join(x.get("text", "") for x in c)

    g = 1
    st, rs, _ = load(g)
    d = next(i for i in sorted(rs) if who(rs[i]) == "Opus" and len(rs[i]["attempts"]) == 2
             and rs[i]["attempts"][1].get("response_condition") == "same_model_without_private_thought")
    texts = {"standard": system_text(st[d]["prompt_messages"]), "recovery": system_text(rs[d]["attempts"][1]["prompt_messages"])}
    info = {}
    for name, t in texts.items():
        wrapped = "\n".join("\n".join(textwrap.wrap(line, 96)) if line.strip() else "" for line in t.strip().split("\n"))
        out(f"gen_prompt_{name}.tex", "\\begingroup\\scriptsize\n\\begin{verbatim}\n" + wrapped + "\n\\end{verbatim}\n\\endgroup")
        (SUPP / f"system_prompt_{name}.txt").write_text(t)
        info[name] = dict(game=g, decision=d, sha256=text_sha256(t), chars=len(t))
    seen = {"standard": set(), "recovery": set()}
    n = {"standard": 0, "recovery": 0}
    for gg in range(1, 21):
        st2, rs2, _ = load(gg)
        for i in rs2:
            t = system_text(st2[i]["prompt_messages"])
            if t is not None:
                seen["standard"].add(text_sha256(t)); n["standard"] += 1
            for a in rs2[i]["attempts"]:
                if a.get("response_condition") == "same_model_without_private_thought":
                    t = system_text(a.get("prompt_messages"))
                    if t is not None:
                        seen["recovery"].add(text_sha256(t)); n["recovery"] += 1
    info["distinct_system_prompts"] = {c: len(v) for c, v in seen.items()}
    info["system_prompts_checked"] = n
    return info


# ---------------------------------------------------------------- stated totals
def stated_totals():
    un = [r for r in tot if r["group"] == "unpayable" and not r["forced_menu"]]
    rows = []
    for m in ("Sol", "Gemini", "Opus", "Grok"):
        c = C(r["reading"] for r in un if r["model"] == m)
        rows.append(f"{m} & {sum(c.values())} & {c['exact_full_bound']} & {c['includes_locked']} & {c['listed_only']} \\\\")
    c = C(r["reading"] for r in un)
    rows.append("\\midrule")
    rows.append(f"All & {sum(c.values())} & {c['exact_full_bound']} & {c['includes_locked']} & {c['listed_only']} \\\\")
    out("gen_stated_totals_rows.tex", "\n".join(rows))
    (SUPP / "stated_totals_unpayable.json").write_text(json.dumps([r for r in tot if r["group"] == "unpayable"], indent=1, ensure_ascii=False) + "\n")
    locked = [r for r in un if r["locked_collateral"]]
    return dict(n=len(un), by=dict(c), locked=len(locked), locked_by=dict(C(r["reading"] for r in locked)),
                channel=dict(C(r["full_bound_channel"] for r in un if r["states_full_bound"])))


# ---------------------------------------------------------------- census csv
def census_csv():
    cover = {}
    for e in eps:
        if e["outcome"] == "paid" or k(e) in WITNESSED:
            if e["hotels"] == 0:
                cover[k(e)] = "no hotel"
            elif e["cash"] + e["m0"] >= e["debt"]:
                cover[k(e)] = "listed mortgages suffice"
            elif e["bank_houses"] >= 4 * e["hotels"]:
                cover[k(e)] = "bank stock covers every downgrade"
            else:
                cover[k(e)] = "one hotel per group, recyclable stock"
    label = {"A": "cash and listed mortgages", "B": "sales also needed", "C": "released mortgages necessary",
             "unpayable": "own assets fall short", "menu_unpayable": "bound covers, menu cannot reach"}
    with open(SUPP / "episodes_188.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entry", "game", "first_decision", "last_decision", "system", "turn", "debt", "cash", "building_salvage", "listed_mortgage_value",
                    "all_mortgage_value", "listed_only_total_U0", "full_bound_Ustar", "category", "menu", "first_action", "n_actions", "outcome",
                    "declared_by_player", "cash_after_payment", "released_mortgages_used", "hotels", "bank_houses", "continued_financing_condition",
                    "first_response_condition", "source_file", "source_line"])
        for e in eps:
            w.writerow([f"G{e['game']} d{e['first']}", e["game"], e["first"], e["last"], e["model"], e["turn"], e["debt"], e["cash"], e["salvage"], e["m0"],
                        e["mstar"], e["u0"], e["ustar"], label[cat(e)], "|".join(e["menu"]), e["first_action"], len(e["actions"]), e["outcome"],
                        e["declared"], "" if e["cash_after"] is None else e["cash_after"], len(e["released_mortgages_used"]), e["hotels"], e["bank_houses"],
                        cover.get(k(e), ""), e["first_channels"]["response_condition"], e["source_file"], e["source_line"]])


# ---------------------------------------------------------------- bargaining
def bargaining():
    t = barg["table"]
    comp = [("proposer_only", "Proposer only"), ("recipient_only", "Recipient only"), ("both", "Both"), ("neither", "Neither")]
    rows = []
    for key, name in comp:
        cells = []
        for form in ("Swap", "Cash bid", "Cash ask", "Other"):
            n, a, c, r = t[f"Opening|{form}|{key}"]
            cells.append(f"{n} [{a}/{c}/{r}]" if n else "0")
        rows.append(f"{name} & " + " & ".join(cells) + " \\\\")
    out("gen_opening_rows.tex", "\n".join(rows))
    rows = []
    for stage in ("Opening", "Later"):
        for form in ("Swap", "Cash bid", "Cash ask", "Other"):
            for key, name in comp:
                n, a, c, r = t[f"{stage}|{form}|{key}"]
                if n:
                    rows.append(f"{stage} & {form} & {name} & {n} & {a} & {c} & {r} \\\\")
    out("gen_full_offer_rows.tex", "\n".join(rows))

    def frac(x):
        return f"{x[0]}/{x[1]}"

    def gapcell(gp, minimum=5):
        return "---" if gp["gap"] is None or min(gp["own"][1], gp["neither"][1]) < minimum else f"{gp['gap']:.1f}"

    rows = []
    for m in ("Sol", "Gemini", "Opus", "Grok"):
        p = barg["by_proposer_swaps"][m]
        rs_ = barg["by_recipient_swaps"][m]
        rb = barg["by_recipient_cash_bids"][m]
        rows.append(f"{m} & {frac(p['own'])} & {frac(p['neither'])} & {gapcell(p)} & {frac(rs_['own'])} & {frac(rs_['neither'])} & {gapcell(rs_)} & "
                    f"{frac(rb['own'])} & {frac(rb['neither'])} & {gapcell(rb)} \\\\")
    out("gen_strata_rows.tex", "\n".join(rows))
    names = {"all_swaps": "All opening swaps", "no_grok_authors": "Without Grok-authored offers",
             "no_conflicting_openings": "Without openings from conflicting calls", "cash_bids": "Opening cash bids"}
    rows, brow = [], []
    for key, name in names.items():
        c = barg["contrasts"][key]
        rows.append(f"{name} & {frac(c['own'])} & {frac(c['neither'])} & {c['gap']:.1f} & [{c['percentile_2_5']:.1f}, {c['percentile_97_5']:.1f}] & "
                    f"[{c['leave_one_block_out'][0]:.1f}, {c['leave_one_block_out'][1]:.1f}] \\\\")
        b = c["blocks"]
        brow.append(f"{name} & Proposer only & " + " & ".join(frac(b[str(i)]["own"]) for i in range(1, 6)) + " \\\\")
        brow.append(f" & Neither & " + " & ".join(frac(b[str(i)]["neither"]) for i in range(1, 6)) + " \\\\")
    out("gen_contrast_rows.tex", "\n".join(rows))
    out("gen_block_rows.tex", "\n".join(brow))
    rows = []
    for m in ("Sol", "Gemini", "Opus", "Grok"):
        b = barg["by_recipient"][m]
        rows.append(f"{m} & {b['n']} & {b.get('accept_trade', 0)} & {b.get('counter_trade', 0)} & {b.get('reject_trade', 0)} \\\\")
    out("gen_recipient_rows.tex", "\n".join(rows))


# ---------------------------------------------------------------- coverage and middle
def coverage():
    c = fin["coverage"]
    rows = [
        f"No hotel at entry & {c['no_hotel']} & A highest house is sellable while any house stands; clearing a group lists its mortgages. \\\\",
        f"Cash plus listed mortgages cover the debt & {c['listed_mortgages_suffice']} & A listed mortgage stays listed until used, so a state with nothing offered already has enough cash. \\\\",
        f"Bank houses at least four per hotel held & {c['stock_covers_every_downgrade']} & Every hotel exchange is affordable in any order; house sales only add stock. \\\\",
        f"One hotel per hotel-bearing group; bank houses plus houses in hotel-free groups at least four & {c['one_hotel_per_group_recyclable_stock']} & Either the bank can fund an exchange or a hotel-free group has a house to sell. \\\\",
    ]
    out("gen_coverage_rows.tex", "\n".join(rows))
    rows = []
    for m in fin["middle_constructive"]:
        b = m["built"]
        desc = ", ".join(f"{SHORT[kk]} {'hotel' if v == 5 else v}" for kk, v in b.items())
        rows.append(f"{m['entry']} & {m['model']} & {money(m['debt'])} & {money(m['cash'])} & {money(m['m0'])} & {money(m['salvage'])} & {m['bank_houses']} & {desc} \\\\")
    out("gen_middle_rows.tex", "\n".join(rows))
    rows = []
    for m in fin["coverage_last_class"]:
        rows.append(f"{m['entry']} & {m['bank_houses']} & {m['houses_in_hotel_free_groups']} & {m['bank_houses'] + m['houses_in_hotel_free_groups']} \\\\")
    out("gen_lastclass_rows.tex", "\n".join(rows))


# ---------------------------------------------------------------- figure
def figure(nec):
    plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 8.5, "pdf.fonttype": 42})
    INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
    DARK, PALE = "#256abf", "#86b6ef"
    st_by = {(r["game"], r["first"]): r for r in tot}
    order = []
    for t in TIER_ORDER:
        grp = [e for e in nec if CODING[k(e)]["tier"] == t]
        order.append((t, grp))
    n_rows = sum(len(g) for _, g in order) + len(order)
    fig, ax = plt.subplots(figsize=(7.0, 4.35))
    y = n_rows
    xmax = 1500
    for t, grp in order:
        y -= 1
        ax.text(-455, y - 0.02, f"{TIER_LABEL[t]} ({len(grp)})", ha="left", va="center", fontsize=8.5, fontweight="bold", color=INK)
        for e in grp:
            y -= 1
            gap = 5
            ax.barh(y, e["u0"], height=0.56, color=DARK, linewidth=0, zorder=2)
            ax.barh(y, e["ustar"] - e["u0"] - gap, left=e["u0"] + gap, height=0.56, color=PALE, linewidth=0, zorder=2)
            ax.plot([e["debt"], e["debt"]], [y - 0.42, y + 0.42], color=INK, linewidth=1.6, solid_capstyle="butt", zorder=4)
            s = st_by[k(e)]
            mark = e["ustar"] if s["states_full_bound"] else (e["u0"] if CODING[k(e)]["tier"] == "omission" else None)
            if mark is not None:
                ax.plot([mark], [y], marker="D", markersize=5.2, markerfacecolor="white", markeredgecolor=INK, markeredgewidth=1.1, zorder=5)
            ax.text(-440, y, f"G{e['game']} d{e['first']}", ha="left", va="center", fontsize=8.2, color=INK)
            ax.text(-205, y, e["model"], ha="left", va="center", fontsize=8.2, color=MUTED)
            res = f"paid, \\${e['cash_after']} left" if e["outcome"] == "paid" else "declared"
            ax.text(xmax + 25, y, res, ha="left", va="center", fontsize=8.2, color=INK if e["outcome"] != "paid" else MUTED,
                    fontweight="bold" if e["outcome"] != "paid" else "normal")
    ax.set_ylim(-0.4, n_rows - 0.35)
    ax.set_xlim(-460, xmax + 330)
    ax.set_xticks([0, 250, 500, 750, 1000, 1250, 1500])
    ax.set_xticklabels(["0", "250", "500", "750", "1,000", "1,250", "1,500"])
    ax.set_yticks([])
    ax.set_xlabel("Game dollars at the first menu", color=MUTED, fontsize=8.5)
    ax.xaxis.set_label_coords((460 + 750) / (460 + xmax + 330), -0.075)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["bottom"].set_bounds(0, xmax)
    ax.tick_params(axis="x", colors=MUTED, length=2.5, width=0.6, labelsize=8)
    for x in (0, 250, 500, 750, 1000, 1250, 1500):
        ax.plot([x, x], [-0.4, n_rows - 1.2], color=GRID, linewidth=0.6, zorder=1)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=DARK, label="Cash, all building salvage and the mortgages listed at the first menu"),
               Patch(facecolor=PALE, label="Mortgages released by selling the buildings"),
               Line2D([0], [0], color=INK, linewidth=1.6, label="Debt"),
               Line2D([0], [0], marker="D", color="none", markerfacecolor="white", markeredgecolor=INK, markeredgewidth=1.1, markersize=5.2,
                      label="Total stated in the first response")]
    leg = ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.135), ncol=2, frameon=False, fontsize=8, handlelength=1.6,
                    columnspacing=1.6, handletextpad=0.6)
    for txt in leg.get_texts():
        txt.set_color(INK)
    fig.subplots_adjust(left=0.01, right=0.995, top=0.885, bottom=0.10)
    fig.savefig(ASSETS / "fig_sixteen.pdf")
    fig.savefig(PKG / "qa" / "fig_sixteen.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    cohort_rows, wins_by_seat = cohort()
    nec, tiers, by_tier_model, carried = sixteen()
    dep = departures()
    st_sum = stated_totals()
    census_csv()
    bargaining()
    coverage()
    figure(nec)
    prompt_info = prompts()
    summary = dict(prompts=prompt_info, tiers=dict(tiers), tiers_by_model={t: dict(v) for t, v in by_tier_model.items()},
                   carried={f"{a}|{b}": v for (a, b), v in carried.items()}, stated_totals=st_sum,
                   wins_by_seat={str(a): b for a, b in sorted(wins_by_seat.items())},
                   departures=[f"G{e['game']} d{e['first']} {e['model']}" for e in dep],
                   seeds=sorted({r["seed"] for r in cohort_rows}), commits=dict(C(r["sha"] for r in cohort_rows)))
    write_json("tables_summary.json", summary)
    for kk, v in summary.items():
        print(kk, "=", v)
