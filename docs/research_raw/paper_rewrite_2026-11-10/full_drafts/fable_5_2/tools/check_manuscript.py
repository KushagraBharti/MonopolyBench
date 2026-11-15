#!/usr/bin/env python3
"""Document/data consistency checks for the Fable 5.2 draft (no engine or model call).

1. Every number asserted below is recomputed from the retained ledgers or this draft's re-tabulations and must
   appear as the given literal in the named section file.
2. Every \\TranscriptQuote / \\InlineQuote id used in the sections is declared, and every declared supplementary
   quote is used.
3. Every \\cite key exists in references.bib; every \\ref/\\label pair resolves; the built log has no undefined
   reference, citation or overfull box.
4. Each excerpt used in the manuscript appears in the text extracted from the built PDF (when PyMuPDF is available).
Output: qa/manuscript_checks.json; exit status 1 on any failure.
"""
import json, pathlib, re, sys, collections
HERE = pathlib.Path(__file__).resolve().parent.parent
RW = HERE.parent.parent
S = HERE / "sections"
J = lambda p: json.loads(pathlib.Path(p).read_text())
o = J(HERE / "data/offer_retabulation.json"); e = J(HERE / "data/economy_retabulation.json")
d = J(HERE / "data/distress_retabulation.json"); c = J(HERE / "data/conflict_join.json"); n = J(HERE / "data/decision_census.json")
fail = []; checks = []
def need(file, literal, value, why):
    text = (S / file).read_text()
    ok = literal in text
    checks.append({"file": file, "literal": literal, "recomputed": value, "what": why, "ok": ok})
    if not ok: fail.append((file, literal, why))
def eq(a, b, why):
    ok = a == b; checks.append({"recomputed": a, "expected": b, "what": why, "ok": ok})
    if not ok: fail.append((why, a, b))
cl = o["cells_legal"]; cd = o["cash_direction"]
# --- cohort and conditions
eq(n["decisions"], 6989, "decisions"); eq(n["attempts"], 8679, "attempts")
for m, (dec, att) in {"Sol": (1961, 1991), "Gemini": (1669, 1689), "Opus": (1696, 3301), "Grok": (1663, 1698)}.items():
    eq((n["by_model"][m]["decisions"], n["by_model"][m]["attempts"]), (dec, att), f"{m} decisions/attempts")
    need("setup.tex", f"{dec:,} & {att:,}", (dec, att), f"{m} row of Table 1")
eq(n["by_model"]["Opus"]["decisions_with_refusal"], 1605, "Opus decisions with refusal")
eq(n["by_model"]["Opus"]["first_attempt_refused"], 1604, "Opus first-attempt refusals")
eq(n["by_model"]["Opus"]["applied_without_note"], 1544, "Opus applied without note")
g14 = [n["opus_refusal_by_game"][str(g)] for g in range(1, 5)]
eq((sum(x["with_refusal"] for x in g14), sum(x["decisions"] for x in g14)), (215, 306), "Opus refusals G1-4")
eq(all(v["with_refusal"] == v["decisions"] for g, v in n["opus_refusal_by_game"].items() if int(g) >= 5), True, "Opus refusals G5-20 complete")
need("setup.tex", "215 of 306", 215, "refusals in games 1-4"); need("setup.tex", "all 1,390", 1390, "refusals in games 5-20")
eq({m: n["by_model"][m]["fallbacks"] for m in n["by_model"]}, {"Sol": 4, "Gemini": 1, "Opus": 61, "Grok": 0}, "defaults by system")
eq(c["selected_conflicts"], 139, "Grok disagreements"); r = c["content_to_received"]
eq((r["end_turn -> propose_trade"], r["build_houses_or_hotel -> end_turn"], r["buy_property -> start_auction"], c["received_name"]["accept_trade"]), (60, 22, 11, 7), "disagreement types")
eq(c["grok_threads"], {"initiated": 136, "settled": 39, "initiated_by_conflict_call": 64, "conflict_initiated_settled": 17, "games_with_conflict_initiation": 20}, "Grok threads by conflict")
# --- bargaining
eq((o["n_rows"], o["n_accept_legal"], o["n_threads"], o["n_settled_threads"]), (920, 918, 526, 113), "offer population")
eq({k: (v["n"], v["accept"], v["counter"], v["reject"]) for k, v in cl.items()}, {"neither": (408, 60, 169, 179), "author_only": (289, 19, 111, 159), "recipient_only": (140, 24, 78, 38), "both": (81, 10, 35, 36)}, "completion cells")
eq((cd["author_only"]["author_pays"], cd["recipient_only"]["recipient_pays"]), (238, 135), "completing side pays"); need("bargaining.tex", "373 times", 238 + 135, "one-sided paying side")
eq((cd["author_only"]["median"], cd["recipient_only"]["median"]), (200, -350.0), "median cash")
fo, lo = o["cells_first_offer"], o["cells_later_offer"]
eq((sum(v["n"] for v in fo.values()), sum(v["accept"] for v in fo.values()), sum(v["counter"] for v in fo.values()), sum(v["reject"] for v in fo.values())), (524, 32, 137, 355), "first offers")
eq((sum(v["n"] for v in lo.values()), sum(v["accept"] for v in lo.values()), sum(v["reject"] for v in lo.values())), (394, 81, 57), "later offers")
need("bargaining.tex", "32 are accepted, 137 are countered and 355 are rejected", None, "first-offer sentence")
eq((fo["author_only"]["reject"], fo["author_only"]["n"], fo["recipient_only"]["reject"], fo["recipient_only"]["n"]), (138, 187, 31, 51), "first-offer contrast")
eq((lo["author_only"]["reject"], lo["author_only"]["n"], lo["recipient_only"]["reject"], lo["recipient_only"]["n"], lo["author_only"]["accept"], lo["recipient_only"]["accept"]), (21, 102, 7, 89, 16, 22), "later-offer contrast")
eq((o["games_with_both_cells"], o["games_reject_rate_higher_author_only"], o["games_reject_rate_equal"], o["games_accept_rate_lower_author_only"]), (19, 17, 1, 13), "game-level contrast")
blk = o["contrast_by_block"]
eq(sum(1 for b in blk.values() if b["reject_rate_author_only"] > b["reject_rate_recipient_only"]), 5, "blocks with higher writer-only rejection")
eq(sum(1 for b in blk.values() if b["accept_rate_author_only"] < b["accept_rate_recipient_only"]), 4, "blocks with lower writer-only acceptance")
st = o["recipient_style_all"]
eq({m: (v["n"], v["accept"], v["counter"], v["reject"]) for m, v in st.items()}, {"Sol": (235, 30, 140, 65), "Gemini": (242, 26, 36, 180), "Opus": (189, 29, 141, 19), "Grok": (254, 28, 77, 149)}, "response styles")
eq(o["response_condition_by_recipient"]["Opus"]["same_model_without_private_thought"], 162, "Opus action-only responses")
eq(c["cells_excluding_conflict_responses"]["author_only"], {"n": 286, "accept": 16, "counter": 111, "reject": 159}, "writer-only without disagreeing responses")
eq(c["grok_responses"]["excluding_conflicts"], {"n": 243, "accept": 21, "counter": 76, "reject": 146}, "Grok without disagreeing responses")
eq(cl["recipient_only"]["reject"] + cl["both"]["reject"], 74, "rejections of recipient-completing offers")
t = d["thresholds"]["100"]
eq((t["bid_to_cash_poor_recipient"], t["bid_to_other_recipient"], t["ask_by_cash_poor_writer"], t["ask_by_other_writer"]),
   ({"n": 85, "accept": 12, "counter": 55, "reject": 18}, {"n": 407, "accept": 47, "counter": 149, "reject": 211}, {"n": 132, "accept": 18, "counter": 52, "reject": 62}, {"n": 207, "accept": 30, "counter": 115, "reject": 62}), "cash-poor table")
cs, nc = d["completing_settlements"], d["noncompleting_settlements"]
eq((cs["payer_completes"], cs["payer_completes_and_seller_under_100"], cs["median_seller_cash_when_payer_completes"], nc["with_net_cash"], nc["seller_under_100"], nc["median_seller_cash"]), (48, 21, 194.0, 57, 9, 571), "cash-poor sellers of completing deeds")
eq((d["settlement_sensitivity"]["50"], d["settlement_sensitivity"]["200"]), ({"cash_poor_seller_settlements": 20, "of_which_buyer_completes": 14}, {"cash_poor_seller_settlements": 40, "of_which_buyer_completes": 24}), "threshold sensitivity")
eq(sum(1 for r in d["distress_settlement_rows"] if r["buyer_completes"] and r["seller_won"]), 6, "cash-poor completing sellers who won")
eq(d["distress_settlements"]["seller_model"]["Opus"], 16, "Opus as cash-poor seller")
# --- development
tg = e["trade_groups_by_configuration"]
eq({m: (v["groups"], v["built_first_window"], v["ever_built"], v["rent_until_loss_or_end"]) for m, v in tg.items()},
   {"Sol": (17, 16, 17, 20818), "Gemini": (18, 17, 17, 26070), "Opus": (15, 7, 12, 5930), "Grok": (13, 3, 8, 4560)}, "trade groups by owner")
for m, v in tg.items(): need("development.tex", f"\\${v['rent_until_loss_or_end']:,}", v["rent_until_loss_or_end"], f"{m} rent")
tt = e["trade_groups_total"]
eq((tt["built_first_window"], tt["ever_built"], tt["rent"], tt["built_x_rent"]["built_rent"], tt["built_x_rent"]["unbuilt_rent"], tt["built_x_rent"]["unbuilt_ever_built_later"], tt["by_eventual_winner"]), (43, 54, 57378, 53810, 3568, 11, 18), "trade group totals")
eq((tt["elapsed_to_management"]["0"], sum(v for k, v in tt["elapsed_to_management"].items() if int(k) > 5)), (35, 2), "time to first management window")
causes = collections.Counter()
for v in tg.values():
    for k, x in v["unbuilt_causes"].items(): causes[k] += x
eq(dict(causes), {"default_other": 1, "valid_end": 3, "default_after_refusal": 3, "never_legal_in_window": 9, "received_conflict": 4}, "unbuilt causes")
nl = e["never_legal_rows"]
eq((sum(1 for r in nl if r["interest"] > 0), sorted(r["cash_after"] for r in nl if r["interest"] == 0)), (7, [125, 158]), "never-legal reasons")
ct = e["completing_terms_all"]; eq((ct["paid_cash"], ct["received_cash"]), (48, 9), "completer paid/received cash")
eq(e["episode_rent_crosscheck_against_flows"], {"episodes": 209, "mismatches": 0}, "rent cross-check")
su = e["spending_units"]; eq((su["n"], su["spend"], su["rent_whole"], su["zero_rent"], su["by_configuration"]["Sol"]["spend"] + su["by_configuration"]["Gemini"]["spend"]), (103, 103450, 93000, 40, 74400), "spending units")
# --- insolvency and estates
eq((e["eliminations_by_certificate"], e["eliminations_kind"]), ({"upper_bound_impossibility": 56, "exhaustive_financing_impossibility": 1, "legal_payment_witness": 3}, {"declared": 56, "automatic": 4}), "elimination classes")
sh = e["shortfall_vs_bound"]; eq((sh["median"], sh["min"], sh["under_100"]), (360.0, 18, 10), "shortfalls")
eq(e["eliminations_by_debtor"], {"Opus": 17, "Sol": 12, "Grok": 18, "Gemini": 13}, "eliminations by debtor")
w = e["winner_is_estate_recipient_by_order"]; eq((w["1"]["winner"], w["2"]["winner"], w["3"]["winner"]), (18, 17, 19), "winner as estate recipient by order")
rows = e["elimination_rows"]
eq(sum(1 for g in range(1, 21) if all(r["creditor"] == r["winner"] for r in rows if r["game"] == g)), 16, "games where winner takes all three estates")
eq(e["estate_deeds"], {"nonterminal": 227, "terminal": 170, "nonterminal_to_winner": 202}, "estate deeds")
lr = e["live_by_route"]
eq({k: (v["n"], v["by_eventual_winner"], v["rent_until_loss_or_end"]) for k, v in lr.items()}, {"trade": (63, 18, 57378), "creditor_inheritance": (52, 45, 11472), "direct_purchase": (16, 12, 23070), "auction": (9, 2, 3358)}, "episodes by route")
eq((e["episodes"]["by_route"]["creditor_inheritance"], e["live_total_rent"], e["flow_totals"]["paid_rent"]["amount"], lr["creditor_inheritance"]["with_any_rent"]), (121, 95278, 121154, 14), "estate episodes and rent totals")
eq((e["first_completion_route"], e["first_completer_won"], e["first_completer_built_x_won"]), ({"trade": 14, "direct_purchase": 6}, 15, {"built=True|won=True": 12, "built=False|won=False": 4, "built=False|won=True": 3, "built=True|won=False": 1}), "first completion and outcome")
for lit, f in [("56 of 60", "insolvency.tex"), ("121 by estate", "insolvency.tex"), ("16 of the 20 games", "insolvency.tex"), ("202", "insolvency.tex"), ("\\$95,278 of the \\$121,154", "insolvency.tex"), ("15 of the 20 games", "insolvency.tex"), ("510 would", "bargaining.tex")]:
    need(f, lit, None, "literal present")
# --- quotes and references
decl = set(re.findall(r"\\Declare(?:Transcript|Inline)Quote\{([^}]+)\}", (RW / "sections/transcript_quotes.tex").read_text() + (S / "quotes_supplement.tex").read_text()))
body = "".join(p.read_text() for p in S.glob("*.tex") if p.name not in ("quotes_supplement.tex",))
used = set(re.findall(r"\\(?:TranscriptQuote|InlineQuote)\{([^}]+)\}", body))
eq(sorted(used - decl), [], "quote ids used but not declared")
sup = {q["id"] for q in J(HERE / "data/transcript_manifest_supplement.json")["quotes"]}
eq(sorted(sup - used), [], "supplementary quotes declared but unused")
bib = set(re.findall(r"@\w+\{([^,]+),", (HERE / "references.bib").read_text()))
cites = set(k.strip() for grp in re.findall(r"\\cite[tp]?\{([^}]+)\}", body) for k in grp.split(","))
eq(sorted(cites - bib), [], "citation keys missing from references.bib")
labels = set(re.findall(r"\\label\{([^}]+)\}", body)) | {"inc:" + x for x in re.findall(r"\\(?:IncidentTitle|AppIncidentTitle)\{([^}]+)\}", body)}
refs = set(re.findall(r"\\ref\{([^}]+)\}", body))
eq(sorted(refs - labels), [], "references without a label")
log = HERE / "build/manuscript.log"
if log.exists():
    L = log.read_text(errors="ignore")
    eq((len(re.findall(r"Overfull \\hbox", L)), "undefined" in L.lower() and bool(re.search(r"(Reference|Citation) `[^']+' .*undefined", L))), (0, False), "build log: overfull boxes / undefined references")
pdf_info = {}
try:
    import pymupdf
    doc = pymupdf.open(HERE / "build/manuscript.pdf")
    text = re.sub(r"\s+", " ", " ".join(p.get_text() for p in doc))
    norm = lambda s: re.sub(r"\s+", " ", s.replace("\u2014", "—"))
    man = J(RW / "data/transcript_manifest.json"); supm = J(HERE / "data/transcript_manifest_supplement.json")
    missing = []
    for q in man["quotes"] + supm["quotes"]:
        if q["id"] not in used: continue
        for ex in q["excerpts"]:
            probe = norm(ex["text"]).strip()[:60]
            if probe not in text: missing.append(q["id"])
    pdf_info = {"pages": len(doc), "used_quotes": len(used), "excerpts_not_found_in_pdf_text": sorted(set(missing))}
except Exception as ex:  # PyMuPDF only exists in the repository virtualenv
    pdf_info = {"skipped": repr(ex)}
out = {"checks": len(checks), "failures": [list(map(str, f)) for f in fail], "pdf": pdf_info, "quotes_used": sorted(used), "detail": checks}
(HERE / "qa/manuscript_checks.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("checks", "failures", "pdf")}, indent=1))
sys.exit(1 if fail else 0)
