#!/usr/bin/env python3
"""Checks for ``replacement_prose.tex`` and its PDF.

1. Re-reads every quotation in ``data/quote_manifest.json`` from the stored
   field by offsets and compares the span and both hashes.
2. Checks that each public message whose receipt the prose claims is present
   in the named recipient's stored request.
3. Ties the numbers printed in the prose to the stored-record checks in
   ``data/`` by asserting that each expected phrase occurs in the LaTeX source.
4. Asserts the incident facts the prose states (trade execution, order of
   events, cash positions, the earlier G5 note inside the later request).
5. If the PDF exists, checks that every quotation occurs in its text, that the
   LaTeX log has no warnings that matter, and reports the page count.

Stored records only.  No engine, replay or model query.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from ro_corpus import board, load_all

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
TEX = (HERE / "replacement_prose.tex").read_text()
BK = board()["by_key"]
IDX = {v["index"]: k for k, v in BK.items()}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    games = load_all()
    report = {"quotations": [], "receipts": [], "numbers": [], "facts": [], "pdf": {}}
    ok = True

    # 1. quotations
    manifest = json.loads((DATA / "quote_manifest.json").read_text())
    from build_quotes import field_text, CHANNEL
    rev = {v: k for k, v in CHANNEL.items()}
    for m in manifest:
        g = games[m["game"]]
        text = field_text(g, m["decision"], rev[m["channel"]])
        good = (text[m["start"]:m["end"]] == m["span"]
                and hashlib.sha256(text.encode()).hexdigest() == m["field_sha256"]
                and hashlib.sha256(m["span"].encode()).hexdigest() == m["span_sha256"]
                and any("\\%s{%s}" % (mac, m["id"]) in TEX for mac in ("QuoteCard", "QuoteInline", "QuoteText")))
        report["quotations"].append({"id": m["id"], "source_match_and_used": good})
        ok &= good

    # 2. receipts claimed in the prose: (game, speaking decision, recipient decision)
    for gn, k_from, k_to in [(13, 250, 251), (13, 252, 253), (19, 135, 136)]:
        g = games[gn]
        msg = g.resolved[k_from]["final_action"]["public_message"]
        user = "".join(mm["content"] for mm in g.started[k_to]["prompt_messages"]
                       if mm["role"] == "user" and isinstance(mm["content"], str))
        found = json.dumps(msg, ensure_ascii=False)[1:-1] in user or msg in user or json.dumps(msg)[1:-1] in user
        report["receipts"].append({"game": gn, "from": k_from, "in_request_of": k_to, "found": found})
        ok &= found

    # 3. numbers
    d = json.loads((DATA / "check_debts.json").read_text())
    o = json.loads((DATA / "check_offers.json").read_text())
    rc = json.loads((DATA / "check_recipient_conflicts.json").read_text())
    ec = json.loads((DATA / "check_economy.json").read_text())
    t = d["tiers_among_payable"]
    ab = d["above_bound_menu"]
    v = o["composition_versions"]
    rs = o["resampling"]

    def rng(pair):
        return f"${pair[0]}$, ${pair[1]}$".replace("$-", "$-")

    expect = [
        ("episodes paid eliminated", f"paid {d['paid']} debts and were eliminated in {d['eliminated']}"),
        ("above bound", f"In {d['eliminated_above_bound']} eliminations the debt exceeded every asset"),
        ("payable", f"{d['paid']} of {d['payable']} debts known to be payable"),
        ("actions", f"using {d['paid_mortgage_actions']} mortgages and {d['paid_sale_actions']} building sales"),
        ("tier listed row", f"Cash and listed mortgages & {t['listed']['episodes']} & {t['listed']['paid']} & {t['listed']['declared_first']} & {t['listed']['one_action_paid']}"),
        ("tier sales row", f"Building sales as well & {t['sales']['episodes']} & {t['sales']['paid']} & {t['sales']['declared_first']} & {t['sales']['one_action_paid']}"),
        ("tier unlisted row", f"Mortgages absent from the first menu & {t['unlisted']['episodes']} & {t['unlisted']['paid']} & {t['unlisted']['declared_first']} & {t['unlisted']['one_action_paid']}"),
        ("above bound alt row", f"another action listed & {ab['alternative_listed']} & 0 & {ab['declared_first_when_alternative_listed']}"),
        ("above bound forced row", f"bankruptcy the only action & {ab['only_bankruptcy_listed']} & 0 & {ab['declared_first_when_only_bankruptcy']}"),
        ("one action", f"Sixty-seven payments took one action" if d["paid_one_action"] == 67 else "MISSING"),
        ("median ratio", f"{round(100 * d['median_debt_over_bound_paid'])}\\% of the debtor's four-part sum"),
        ("first action counts", f"in {d['first_action']['payable']['declared_first']} of the {d['payable']} payable debts and in {d['first_action']['above_bound']['declared_first']} of the {d['first_action']['above_bound']['n']} debts above every asset"),
        ("forced menus", f"Eight of the {d['first_action']['above_bound']['n']} menus listed bankruptcy alone" if ab["only_bankruptcy_listed"] == 8 else "MISSING"),
        ("alt declared", f"Of the other {ab['alternative_listed']}, agents declared first in {ab['declared_first_when_alternative_listed']}"),
        ("median cover", f"a median {round(100 * ab['bound_to_debt_ratio_quartiles_alt_listed'][1])}\\% of the debt"),
        ("near boundary", "of the six within a tenth of it, three declared and three continued"
            if (ab["alt_listed_within_10pct_of_debt"], ab["alt_listed_declared_first_within_10pct"]) == (6, 3) else "MISSING"),
        ("gap range", f"between \\${d['sixteen_summary']['gap_range'][0]} and \\${d['sixteen_summary']['gap_range'][1]}"),
        ("sixteen by model", "Gemini five of six, Opus five of five, Sol two of three and Grok two of two"
            if d["sixteen_summary"]["by_model"] == {"Sol": [2, 3], "Gemini": [5, 6], "Opus": [5, 5], "Grok": [2, 2]} else "MISSING"),
        ("games and blocks", "twelve games and all five seed blocks"
            if len(d["sixteen_summary"]["games"]) == 12 and all(x[1] > 0 for x in d["sixteen_summary"]["by_block"].values()) else "MISSING"),
        ("first actions of paid", "Thirteen payments began with a building sale and one with a listed mortgage"
            if d["sixteen_summary"]["paid_first_action"] == {"sell_houses_or_hotel": 13, "mortgage_property": 1} else "MISSING"),
        ("uses", f"Nineteen payments used {d['released_collateral_uses']['mortgages']} mortgages absent from the first menu"
            if d["released_collateral_uses"]["episodes"] == 19 else "MISSING"),
        ("responses", f"{o['responses']} offers with {o['responses_by_action']['accept_trade']} acceptances, {o['responses_by_action']['counter_trade']} counteroffers and {o['responses_by_action']['reject_trade']} rejections"),
        ("legal", f"{o['acceptance_legal']} offers the recipient could accept"),
        ("grok conflicted acceptances", f"Seven of Grok's {rc['grok_acceptances']} acceptances" if rc["grok_conflicted_acceptances"] == 7 else "MISSING"),
        ("completing openings", f"accepted {o['completing_openings_swap_or_cash_bid'][1]} of the {o['completing_openings_swap_or_cash_bid'][0]} opening swaps and cash bids that would complete only the proposer's group, countered {o['completing_openings_swap_or_cash_bid'][2]} and rejected {o['completing_openings_swap_or_cash_bid'][3]}"),
        ("swap cells", f"{v['all']['swap']['proposer_only'][0]} of {v['all']['swap']['proposer_only'][1]} cases (81.9\\%), against {v['all']['swap']['neither'][0]} of {v['all']['swap']['neither'][1]} swaps"),
        ("cash cells", f"{v['all']['cash_bid']['proposer_only'][0]} of {v['all']['cash_bid']['proposer_only'][1]} against {v['all']['cash_bid']['neither'][0]} of {v['all']['cash_bid']['neither'][1]}"),
        ("both", f"{o['table_opening']['swap']['both'][3]} of {o['table_opening']['swap']['both'][0]}"),
        ("sale offers", f"rejected {o['table_opening']['sale_offer']['recipient_only'][3]} of {o['table_opening']['sale_offer']['recipient_only'][0]} offers to sell them"),
        ("comparison authors", f"Grok wrote {o['comparison_swaps']['by_author']['Grok']} of the {o['comparison_swaps']['n']} opening swaps that complete no group and {o['comparison_swaps']['accepted_by_author']['Grok']} of the {o['comparison_swaps']['accepted']}"),
        ("conflict openings among accepted", "Thirteen of those fifteen" if o["comparison_swaps"]["accepted_grok_conflict_openings"] == 13 else "MISSING"),
        ("pairs", "seven of the nine proposer and recipient pairs" if o["author_recipient_pairs_positive"] == [7, 9] else "MISSING"),
        ("no conflict version", f"it is {v['no_conflicting_grok_openings']['swap']['gap']:.1f} points ({v['no_conflicting_grok_openings']['swap']['proposer_only'][0]} of {v['no_conflicting_grok_openings']['swap']['proposer_only'][1]} against {v['no_conflicting_grok_openings']['swap']['neither'][0]} of {v['no_conflicting_grok_openings']['swap']['neither'][1]})"),
        ("no grok version", f"it is {v['no_grok_authored']['swap']['gap']:.1f} points ({v['no_grok_authored']['swap']['proposer_only'][0]} of {v['no_grok_authored']['swap']['proposer_only'][1]} against {v['no_grok_authored']['swap']['neither'][0]} of {v['no_grok_authored']['swap']['neither'][1]})"),
        ("standardized", f"gives {o['standardized_swap_gap']['weights_proposer_only_cell']} to {o['standardized_swap_gap']['weights_neither_cell']} points"),
        ("counters", f"countered {o['counter_share_proposer_only']['cash_bid'][0]} of the {o['counter_share_proposer_only']['cash_bid'][1]} completing cash bids and {o['counter_share_proposer_only']['swap'][0]} of the {o['counter_share_proposer_only']['swap'][1]} completing swaps"),
        ("same deeds", f"In {o['cash_bid_counters_same_deeds_more_cash'][0]} of the {o['cash_bid_counters_same_deeds_more_cash'][1]} cash-bid counters"),
        ("first estate", f"eventual winner in {ec['first_estate_creditor_is_winner']} of 20 games"),
        ("grok conflicts", f"{rc['content_conflicts_with_call']['Grok']} of the {rc['content_names_an_action']['Grok']:,} responses whose assistant content names an action"),
        ("counters all stages", f"{rc['counters_same_bundle_more_cash']['proposer_only_all_stages'][0]} of {rc['counters_same_bundle_more_cash']['proposer_only_all_stages'][1]} counters to offers completing only the proposer"),
        ("counters neither", f"{rc['counters_same_bundle_more_cash']['neither_deed_requests_all_stages'][0]} of {rc['counters_same_bundle_more_cash']['neither_deed_requests_all_stages'][1]} counters to requests for a deed"),
        ("two conflicted acceptances", "Two of the three acceptances are Grok calls whose text refuses"
            if sum(x["recipient_conflict"] for x in rc["accepted_completing_openings"]) == 2 and len(rc["accepted_completing_openings"]) == 3 else "MISSING"),
        ("unlisted total G5", "the total was \\$1,149" if 774 + 375 == 1149 else "MISSING"),
    ]
    # the spread table rows
    for key, label in (("all", "Swaps, all proposers"), ("no_conflicting_grok_openings", "no conflicting openings"),
                       ("no_grok_authored", "no Grok-authored offers")):
        r = rs[key]["swap"]
        pb = [x for x in r["per_block"].values()]
        row = (f"${min(pb)}$ to ${max(pb)}$ & ${r['leave_one_block_out'][0]}$ to ${r['leave_one_block_out'][1]}$ & "
               f"${r['block_exact_3125']['p2.5_p97.5'][0]}$, ${r['block_exact_3125']['p2.5_p97.5'][1]}$ & "
               f"${r['games_only_20000']['p2.5_p97.5'][0]}$, ${r['games_only_20000']['p2.5_p97.5'][1]}$ & "
               f"${r['two_stage_20000']['p2.5_p97.5'][0]}$, ${r['two_stage_20000']['p2.5_p97.5'][1]}$")
        expect.append((f"spread row {key}", row))
        expect.append((f"blocks positive {key}", f"{r['blocks_positive']}/5 & ${min(pb)}$"))
    r = rs["all"]["cash_bid"]
    pb = list(r["per_block"].values())
    expect.append(("spread row cash", (
        f"${min(pb)}$ to ${max(pb)}$ & ${r['leave_one_block_out'][0]}$ to ${r['leave_one_block_out'][1]}$ & "
        f"${r['block_exact_3125']['p2.5_p97.5'][0]}$, ${r['block_exact_3125']['p2.5_p97.5'][1]}$ & "
        f"${r['games_only_20000']['p2.5_p97.5'][0]}$, ${r['games_only_20000']['p2.5_p97.5'][1]}$ & "
        f"${r['two_stage_20000']['p2.5_p97.5'][0]}$, ${r['two_stage_20000']['p2.5_p97.5'][1]}$")))
    # opening table rows
    to = o["table_opening"]

    def cell(x):
        return "0" if x[0] == 0 else f"{x[0]} [{x[1]}/{x[2]}/{x[3]}]"
    for cname, label in (("author_only", "Proposer only"), ("neither", "Neither"), ("both", "Both"), ("recipient_only", "Recipient only")):
        expect.append((f"opening row {cname}", f"{label} & " + " & ".join(cell(to[f][cname]) for f in ("swap", "cash_bid", "sale_offer", "other"))))
    # proposer table rows
    for m in ("Sol", "Gemini", "Opus", "Grok"):
        s, c = o["by_proposer"][m]["swap"], o["by_proposer"][m]["cash_bid"]
        expect.append((f"proposer row {m}", f"{m} & {s[0][0]}/{s[0][1]} & {s[1][0]}/{s[1][1]}"))
        expect.append((f"proposer cash {m}", f"{c[0][0]}/{c[0][1]} & {c[1][0]}/{c[1][1]}\\\\"))
    # sixteen table rows
    actions = {(r["game"], r["decision"]): r for r in d["sixteen"]}
    for (gn, k), r in actions.items():
        debt = f"{r['debt']:,}"
        reach = f"{r['reach_without_unlisted']:,}"
        expect.append((f"sixteen row G{gn} d{k}", f"G{gn} d{k} & {r['model']} & {debt} & {reach} & {r['unlisted_mortgage']} & "))
        m = re.search(r"G%d d%d & [^\n]*& (\d+)\\\\" % (gn, k), TEX)
        expect.append((f"sixteen actions G{gn} d{k}", "OK" if (m and int(m.group(1)) == r["n_actions"]) else "MISSING"))
        chan = "note" if r["channel"] == "applied private note" else "returned"
        expect.append((f"sixteen channel G{gn} d{k}", "OK" if re.search(r"G%d d%d & [^\n]*& %s & " % (gn, k, chan), TEX) else "MISSING"))

    for name, phrase in expect:
        good = phrase == "OK" or (phrase != "MISSING" and phrase in TEX)
        report["numbers"].append({"check": name, "expected_phrase": phrase, "found": good})
        ok &= good

    # 4. incident facts
    facts = []
    g = games[5]
    mem = g.started[263]["prompt_payload"]["game_state"]["memory"]["your_private_thoughts_last_10"]
    facts.append(("G5 d258 note is in the d263 request", any(n.get("thought") == g.resolved[258]["final_action"]["private_thought"] for n in mem)))
    facts.append(("G5 d258 is four turns before d263", g.started[263]["turn_index"] - g.started[258]["turn_index"] == 4))
    facts.append(("G5 d258 builds one Park Place house", g.resolved[258]["final_action"]["action"] == "build_houses_or_hotel"))
    g = games[13]
    h = g.holdings(253)
    cash = {g.model[p]: x["cash"] for p, x in h.items()}
    bankrupt = {g.model[p]: x["bankrupt"] for p, x in h.items()}
    facts.append(("G13 cash at d253: Opus 1,926, Sol 814, Grok 35", (cash["Opus"], cash["Sol"], cash["Grok"]) == (1926, 814, 35)))
    facts.append(("G13 Gemini bankrupt at d253", bankrupt["Gemini"] is True))
    facts.append(("G13 Atlantic to Short Line is nine squares", BK["SHORT_LINE"]["index"] - BK["ATLANTIC_AVENUE"]["index"] == 9))
    facts.append(("G13 Ventnor unmortgaged, worth 130", (not h["p4"]["owned"]["VENTNOR_AVENUE"]["mortgaged"]) and BK["VENTNOR_AVENUE"]["mortgage"] == 130))
    nxt = [e for e in g.events if e["type"] == "PLAYER_MOVED" and e["actor"].get("player_id") == "p4" and e["turn_index"] > 107][0]
    facts.append(("G13 Grok's next move does not reach Short Line", nxt["payload"]["to"] != BK["SHORT_LINE"]["index"]))
    auc = [e for e in g.events if e["type"] == "AUCTION_ENDED" and e["payload"].get("property_space") == "NORTH_CAROLINA_AVENUE"][0]
    facts.append(("G13 Opus wins the North Carolina auction seven turns later", auc["turn_index"] - 107 == 7 and g.model[auc["payload"]["winner_player_id"]] == "Opus"))
    st = g.started[311]
    facts.append(("G13 d311: Grok on Short Line, $49, bankruptcy the only action",
                  st["prompt_payload"]["game_state"]["you"]["position"] == "SHORT_LINE"
                  and st["prompt_payload"]["game_state"]["you"]["cash"] == 49
                  and st["prompt_payload"]["action_state"]["available_actions"] == ["declare_bankruptcy"]
                  and st["turn_index"] == 150))
    facts.append(("G13 estate at turn 150 completes yellow for Sol",
                  any(r["turn"] == 150 and r["creditor"] == "Sol" and "YELLOW" in r["groups"] for r in ec["games"]["13"])))
    win = [e for e in g.events if e["type"] == "GAME_ENDED"][0]["payload"]["winner_player_id"]
    facts.append(("G13 winner is Opus", g.model[win] == "Opus"))
    g = games[16]
    facts.append(("G16 d247 applied accept, content names reject_trade",
                  g.resolved[247]["final_action"]["action"] == "accept_trade"
                  and '"name":"reject_trade"' in g.selected_attempt(247)["assistant_content"].replace(" ", "")))
    facts.append(("G16 Park Place transferred at turn 130",
                  any(e["type"] == "PROPERTY_TRANSFERRED" and e["turn_index"] == 130 and IDX[e["payload"]["space_index"]] == "PARK_PLACE" for e in g.events)))
    g = games[18]
    facts.append(("G18 d83 applied accept, content names reject_trade",
                  g.resolved[83]["final_action"]["action"] == "accept_trade"
                  and '"name":"reject_trade"' in g.selected_attempt(83)["assistant_content"].replace(" ", "")))
    g = games[12]
    facts.append(("G12 d249 applied bankruptcy, content names a sale",
                  g.resolved[249]["final_action"]["action"] == "declare_bankruptcy"
                  and "sell_houses_or_hotel" in g.selected_attempt(249)["assistant_content"]))
    g = games[20]
    acts = [g.resolved[k]["final_action"]["action"] for k in range(327, 337)]
    facts.append(("G20: two sales then eight mortgages", acts == ["sell_houses_or_hotel"] * 2 + ["mortgage_property"] * 8))
    sc = g.started[327]["prompt_payload"]["action_state"]["scenario"]
    listed = sc["options"]["mortgageable_space_keys"]
    facts.append(("G20 d327 menu lists three deeds worth $325", len(listed) == 3 and sum(BK[x]["mortgage"] for x in listed) == 325))
    released = [g.resolved[k]["final_action"]["args"]["space_key"] for k in range(329, 337)
                if g.resolved[k]["final_action"]["args"]["space_key"] not in listed]
    facts.append(("G20: five of the eight mortgages were absent from the first menu", len(released) == 5))
    tot = {}
    for e in g.events:
        if e["turn_index"] == 108 and e["type"] == "CASH_CHANGED":
            tot[e["payload"]["reason"]] = tot.get(e["payload"]["reason"], 0) + e["payload"]["delta"]
    facts.append(("G20 turn 108: $700 from sales and $665 from mortgages", tot.get("SELL_BUILDING") == 700 and tot.get("MORTGAGE") == 665))
    facts.append(("G20: cash $49 before and $14 after", g.started[327]["prompt_payload"]["game_state"]["you"]["cash"] == 49
                  and g.started[337]["prompt_payload"]["game_state"]["you"]["cash"] == 14))
    # timeline rows about the unlisted deeds in the sixteen first requests
    mort_rows, redeem_rows = 0, 0
    for r in d["sixteen"]:
        gg = games[r["game"]]
        st = gg.started[r["decision"]]
        sc = st["prompt_payload"]["action_state"]["scenario"]
        you = st["prompt_payload"]["game_state"]["you"]
        listed = sc["options"]["mortgageable_space_keys"]
        unl = [hh["space_key"] for hh in you["holdings"]["owned"] if not hh["mortgaged"] and hh["space_key"] not in listed]
        for row in st["prompt_payload"]["game_state"]["memory"]["public_timeline_last_20"]:
            if any(u in (row.get("action") or "") for u in unl):
                mort_rows += row["event_type"] == "PROPERTY_MORTGAGED"
                redeem_rows += row["event_type"] == "PROPERTY_UNMORTGAGED"
    facts.append(("sixteen first requests: no timeline mortgage of an unlisted deed, one redemption", (mort_rows, redeem_rows) == (0, 1)))
    rv = json.loads((DATA / "check_request_values.json").read_text())
    facts.append(("338 liquidation requests, no value-like field, no release rule in the menu note or system prompt",
                  rv["liquidation_requests"] == 338 and rv["fields_named_like_values"] == []
                  and rv["scenario_note_states_release_rule"] == 0 and rv["system_prompt_mentions"] == {}))
    for name, good in facts:
        report["facts"].append({"fact": name, "holds": bool(good)})
        ok &= bool(good)

    # 5. PDF
    pdf = HERE / "build" / "replacement_prose.pdf"
    if pdf.exists():
        import fitz
        doc = fitz.open(pdf)
        text = norm(" ".join(page.get_text() for page in doc))
        text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
        missing = []
        for m in manifest:
            span = norm(m["span"]).replace("’", "'")
            # compare on letters and digits only, which survives ligatures, hyphenation and dash glyphs
            key = re.sub(r"[^A-Za-z0-9]", "", span)
            hay = re.sub(r"[^A-Za-z0-9]", "", text)
            if key not in hay:
                missing.append(m["id"])
        log = (HERE / "build" / "replacement_prose.log").read_text(errors="replace")
        report["pdf"] = {
            "pages": doc.page_count,
            "quotations_missing_from_pdf_text": missing,
            "overfull_hbox": len(re.findall(r"Overfull \\hbox", log)),
            "undefined_references": len(re.findall(r"undefined", log, re.I)),
            "missing_characters": len(re.findall(r"Missing character", log)),
            "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        }
        ok &= not missing and report["pdf"]["undefined_references"] == 0 and report["pdf"]["missing_characters"] == 0
    report["all_checks_pass"] = bool(ok)
    report["counts"] = {
        "quotations": len(report["quotations"]), "receipts": len(report["receipts"]),
        "number_checks": len(report["numbers"]), "number_checks_failed": sum(not x["found"] for x in report["numbers"]),
        "facts": len(report["facts"]), "facts_failed": sum(not x["holds"] for x in report["facts"]),
    }
    (DATA / "replacement_checks.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(report["counts"], indent=1))
    print("pdf", report["pdf"])
    for x in report["numbers"]:
        if not x["found"]:
            print("NUMBER NOT FOUND:", x["check"], "|", x["expected_phrase"])
    for x in report["facts"]:
        if not x["holds"]:
            print("FACT FAILS:", x["fact"])
    for x in report["quotations"]:
        if not x["source_match_and_used"]:
            print("QUOTE PROBLEM:", x["id"])
    for x in report["receipts"]:
        if not x["found"]:
            print("RECEIPT NOT FOUND:", x)
    print("ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
