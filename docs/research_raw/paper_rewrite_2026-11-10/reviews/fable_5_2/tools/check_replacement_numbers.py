"""Assert that numbers printed in replacement_prose.tex match the review's
re-tabulations, and that each literal string is present in the TeX source.

Run after check_offers.py, check_windows.py, check_economy.py, check_records.py.
Inherited engine results (witness remainders, 63 of 70 reorderable targets,
57 developed-rent debts, recurrence 9 of 50) are NOT asserted here because
this review did not recompute them; they are listed as inherited.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import OUT, REVIEW  # noqa: E402


def load(name):
    with open(os.path.join(OUT, name)) as fh:
        return json.load(fh)


off = load("offer_checks.json")
eco = load("economy_checks.json")
win = load("window_menu_checks.json")
rec = load("record_checks.json")
tex = open(os.path.join(REVIEW, "replacement_prose.tex")).read()
flat = re.sub(r"\s+", " ", tex)

checks: list[dict] = []


def claim(name, computed, expected, literal=None):
    ok = computed == expected
    present = None if literal is None else (literal in flat)
    checks.append({"claim": name, "computed": computed, "expected": expected, "match": ok, "literal": literal, "literal_in_tex": present})


def acr(d):
    return [d["n"], d["A"], d["C"], d["R"]]


# --- Table cells by position
pos = off["by_thread_position"]
cells = off["cells"]
claim("author-only all", acr(cells["author_only"]), [289, 19, 111, 159], "Author only & 289 & 19 & 111 & 159 & 187 & 3 & 46 & 138 & 102 & 16 & 65 & 21")
claim("author-only first", acr(pos["author_only"]["first"]), [187, 3, 46, 138])
claim("author-only later", acr(pos["author_only"]["later"]), [102, 16, 65, 21])
claim("recipient-only all", acr(cells["recipient_only"]), [140, 24, 78, 38], "Recipient only & 140 & 24 & 78 & 38 & 51 & 2 & 18 & 31 & 89 & 22 & 60 & 7")
claim("recipient-only first", acr(pos["recipient_only"]["first"]), [51, 2, 18, 31])
claim("recipient-only later", acr(pos["recipient_only"]["later"]), [89, 22, 60, 7])
claim("both all", acr(cells["both"]), [81, 10, 35, 36], "Both & 81 & 10 & 35 & 36 & 48 & 3 & 11 & 34 & 33 & 7 & 24 & 2")
claim("both first", acr(pos["both"]["first"]), [48, 3, 11, 34])
claim("both later", acr(pos["both"]["later"]), [33, 7, 24, 2])
claim("neither all", acr(cells["neither"]), [408, 60, 169, 179], "Neither & 408 & 60 & 169 & 179 & 238 & 24 & 62 & 152 & 170 & 36 & 107 & 27")
claim("neither first", acr(pos["neither"]["first"]), [238, 24, 62, 152])
claim("neither later", acr(pos["neither"]["later"]), [170, 36, 107, 27])
tot_first = [sum(acr(pos[c]["first"])[i] for c in pos) for i in range(4)]
tot_later = [sum(acr(pos[c]["later"])[i] for c in pos) for i in range(4)]
claim("totals first", tot_first, [524, 32, 137, 355], "All & 918 & 113 & 393 & 412 & 524 & 32 & 137 & 355 & 394 & 81 & 256 & 57")
claim("totals later", tot_later, [394, 81, 256, 57])
claim("pct rejected first author-only", round(100 * 138 / 187), 74, "(74 against 61 percent)")
claim("pct rejected first recipient-only", round(100 * 31 / 51), 61)
claim("pct rejected later", [round(100 * 21 / 102), round(100 * 7 / 89)], [21, 8], "(21 against 8 percent)")
claim("pct rejected neither", [round(100 * 152 / 238), round(100 * 27 / 170)], [64, 16], "74 against 64 percent of opening offers, 21 against 16 percent of later ones")

# --- by recipient
br = off["by_recipient"]
exp = {"Sol": ([235, 30, 140, 65], [83, 2, 50, 31], [30, 6, 21, 3]), "Gemini": ([242, 26, 36, 180], [76, 4, 9, 63], [31, 6, 10, 15]),
       "Opus": ([189, 29, 141, 19], [52, 7, 42, 3], [42, 5, 31, 6]), "Grok": ([254, 28, 77, 149], [78, 6, 10, 62], [37, 7, 16, 14])}
for m, (a, b, c) in exp.items():
    claim(f"{m} all920", acr(br[m]["all920"]), a)
    claim(f"{m} author-only", acr(br[m]["author_only"]), b)
    claim(f"{m} recipient-only", acr(br[m]["recipient_only"]), c)
claim("Opus action-only responses", br["Opus"]["action_only"]["all"], 162, "action-only in 162")
claim("Gemini+Grok author-only rejections", br["Gemini"]["author_only"]["R"] + br["Grok"]["author_only"]["R"], 125, "125 of the 159")
bg = off["by_game"]
claim("games reject direction", [bg["author_only_reject_share_higher"], bg["games_with_both_cells"]], [17, 19], "17 of the 19 games")
claim("games accept direction", bg["author_only_accept_share_lower"], 13, "four blocks and 13 games")
claim("blocks reject direction", sum(b["reject_higher_for_author_only"] for b in off["by_block"].values()), 5)
claim("blocks accept direction", sum(b["accept_lower_for_author_only"] for b in off["by_block"].values()), 4)

# --- counters
base = off["counter_content"]["baseline_asked_deed_retention_by_cell"]
pure = off["pure_cash_repricing_by_cell"]
inc = off["pure_repricing_increase_by_cell_and_counterer"]
for cell, e in {"author_only": (111, 92, 79), "neither": (110, 87, 81), "both": (35, 26, 25), "recipient_only": (32, 24, 24)}.items():
    claim(f"counters {cell}", (base[cell]["counters_where_author_asked_for_a_deed"], base[cell]["counter_keeps_all_asked_deeds"], pure[cell]["asked_deed_same_bundle_cash_up"]), e)
claim("counter table literal", True, True, "Author only & 111 & 92 & 79 & \\$125")
claim("counter table literal 2", True, True, "Neither & 110 & 87 & 81 & \\$100")
nm = off["cash_for_deed_offers_countered_by_pure_repricing"]
claim("ask/offer", [nm["author_only"]["median_ask_over_offer"], nm["neither"]["median_ask_over_offer"]], [1.556, 1.54], "1.56 times the cash offered for a completing deed (47 offers) and 1.54 times")
claim("ask/offer n", [nm["author_only"]["n"], nm["neither"]["n"]], [47, 56])
bc = nm["author_only"]["by_counterer"], nm["neither"]["by_counterer"]
claim("Sol ask/list", [round(bc[0]["Sol"]["median_ask_over_list"], 1), round(bc[1]["Sol"]["median_ask_over_list"], 1), bc[0]["Sol"]["n"], bc[1]["Sol"]["n"]], [2.9, 2.0, 22, 27])
claim("Grok ask/list", [round(bc[0]["Grok"]["median_ask_over_list"], 1), round(bc[1]["Grok"]["median_ask_over_list"], 1), bc[0]["Grok"]["n"], bc[1]["Grok"]["n"]], [3.2, 2.2, 7, 14])
claim("Opus ask/list", [round(bc[0]["Opus"]["median_ask_over_list"], 1), round(bc[1]["Opus"]["median_ask_over_list"], 1), bc[0]["Opus"]["n"], bc[1]["Opus"]["n"]], [1.1, 1.8, 18, 13])
pr = off["offered_price_to_list_single_deed"]
claim("bids to list", [pr["clear|buyer=author|completes"]["n"], round(pr["clear|buyer=author|completes"]["median_ratio_to_list"], 2), pr["clear|buyer=author|does_not_complete"]["n"], round(pr["clear|buyer=author|does_not_complete"]["median_ratio_to_list"], 2)], [80, 1.59, 118, 1.41], "1.59 times list when the deed completes its group (80 offers) and 1.41 times when it does not (118 offers)")
acc_n = sorted(pr[k]["n"] for k in pr if k.startswith("clear") and k.endswith("accepted_only"))
claim("accepted one-deed cells", [acc_n[0], acc_n[-1]], [4, 12], "between 4 and 12 per cell")
csp = off["completing_side_pays"]
claim("completing side pays", csp["author_only_author_pays"] + csp["recipient_only_recipient_pays"], 373, "373 of the 429")
ndr = off["net_deed_receiver_pays"]["neither"]
claim("deed receiver pays neither", [ndr["net_deed_receiver_pays"], ndr["offers_with_unequal_deed_counts"]], [309, 313], "309 of 313")
to = off["thread_outcomes_by_opening_cell"]
claim("thread outcomes", [to["author_only"]["threads"], to["author_only"]["settled"], to["author_only_opening"]["initiator_still_completes"], to["author_only_opening"]["median_raise_when_completes"]], [187, 26, 24, 97.5], "the median change is \\$97.50")

# --- reasons
rr = rec["E_rejection_reasons"]
claim("74 by cell", rr["by_cell"], {"both": 36, "recipient_only": 38})
claim("74 by recipient", rr["by_recipient"], {"Grok": 31, "Gemini": 31, "Opus": 8, "Sol": 4}, "Grok wrote 31 of the rejections, Gemini 31, Opus 8 and Sol 4")
claim("D by cell", [rr["first_reader_D_by_cell"]["both"]["D"], rr["first_reader_D_by_cell"]["recipient_only"]["D"]], [35, 28], "Thirty-five of the first reader's 63")

# --- conflicts and accepted author-only
bcf = rec["B_conflicts"]
claim("conflict openings", [bcf["threads_opened_by_conflict"], bcf["grok_threads"], bcf["of_which_settled"]], [64, 136, 17], "Sixty-four of its 136 threads")
claim("conflict acceptances", [bcf["conflicting_acceptances"], len(bcf["conflicting_acceptances_author_only_cell"])], [7, 3])
claim("reverse bankruptcy conflicts", [bcf["content_declares_but_call_liquidates"], bcf["of_those_with_debt_above_bound_at_elimination"]], [7, 7], "In seven other liquidation decisions")

# --- unbuilt windows
nl = win["summary"]["never_legal"]
grok = [x for x in nl if " Grok " in x["case"]]
opus = [x for x in nl if " Opus " in x["case"]]
claim("never-legal split", [len(nl), len(grok), len(opus)], [9, 4, 5])
claim("grok redemption on menu", sum(x["redemption_on_first_menu"] for x in grok), 4)
claim("grok cash covers", sorted(x["cash_at_first_decision"] for x in grok if x["cash_covers_need"]), [523, 602])
claim("opus cash", sorted(x["cash_at_first_decision"] for x in opus), [7, 31, 125, 158, 268], "\\$7, \\$31, \\$158, \\$268 and \\$125")
claim("mortgaged group deed at window", win["summary"]["counts"]["with_a_mortgaged_group_deed"], 8, "In eight of the nine a group deed was mortgaged")
claim("opus redemption not on menu with mortgage", sum((not x["redemption_on_first_menu"]) and bool(x["group_deeds_mortgaged"]) for x in opus), 3)
need = {x["case"]: x["need"] for x in nl}
claim("need column", [need["G1 Grok ORANGE"], need["G1 Grok DARK_BLUE"], need["G14 Grok DARK_BLUE"], need["G16 Grok ORANGE"], need["G8 Opus BROWN"], need["G12 Opus LIGHT_BLUE"], need["G15 Opus DARK_BLUE"], need["G16 Opus DARK_BLUE"], need["G20 Opus DARK_BLUE"]], [300, 421, 393, 211, 83, 116, 200, 393, 421])

# --- economy
tc = eco["trade_completed"]
claim("trade groups by model", [tc["by_model"][m]["groups"] for m in ("Sol", "Gemini", "Opus", "Grok")], [17, 18, 15, 13])
claim("first-window builds", [tc["by_model"][m]["built_first_management"] for m in ("Sol", "Gemini", "Opus", "Grok")], [16, 17, 7, 3])
claim("rent built first window", [tc["rent_built_first_window"], tc["rent"]], [53810, 57378], "\\$53,810 of the \\$57,378")
inh = eco["inheritance"]
claim("estate completions", [inh["all"], inh["terminal_no_later_decision"], inh["with_later_play"], inh["with_later_play_to_eventual_winner"]], [121, 69, 52, 45])
claim("estate rent", [inh["with_later_play_rent"], inh["with_later_play_collecting_any_rent"]], [11472, 14], "collect \\$11,472, and 14 of the 52")
claim("median turns to end", inh["median_turns_from_live_completion_to_game_end"], 25.0, "25 turns before the game ends")
rb = eco["rent_by_route"]
claim("rent by route", [rb["trade"], rb["direct_purchase"], rb["auction"], eco["rent_total_on_complete_groups"], eco["paid_rent_total"]], [57378, 23070, 3358, 95278, 121154])
ec = eco["elimination_creditors"]
claim("creditors", [ec["to_winner_nonterminal"], ec["nonterminal"], ec["single_creditor_all_three_games"], ec["first_estate_to_winner_games"]], [35, 40, 16, 18], "In 35 of those forty")
ed = eco["estate_deeds"]
claim("estate deeds", [ed["nonterminal_to_winner"], ed["nonterminal"]], [202, 227], "202 of the 227 deeds")
claim("estate cash", [eco["estate_cash"]["nonterminal_to_winner"], eco["estate_cash"]["nonterminal"]], [7148, 7843])
claim("block 3 dark blue", [(x["game"], x["player_id"], x["acquisition_turn"]) for x in eco["block3_dark_blue"]], [(9, "p2", 29), (10, "p2", 29), (11, "p2", 29), (12, "p2", 29)])
b4 = [(x["game"], x["player_id"], x["route"], x["acquisition_turn"]) for x in eco["block4_orange"] if x["route"] == "direct_purchase"]
claim("block 4 orange", b4, [(13, "p1", "direct_purchase", 47), (14, "p1", "direct_purchase", 47), (15, "p1", "direct_purchase", 47)])
el = eco["eliminations"]
claim("eliminations", [el["n"], el["full_below_owed"], len(el["avoidable"]), len(el["full_ge_owed_not_avoidable"])], [60, 56, 3, 1])

# --- records
g13 = rec["C_g13_grok_cash_path"]["changes"]
claim("G13 cash path", [(p["turn"], p["cash"]) for p in g13], [(107, 35), (107, 235), (116, 279), (117, 179), (121, 309), (125, 289), (143, 249), (146, 49)], "between \\$179 and \\$309")
m = rec["D_liquidation_menus"]
claim("sale on menu in payable cases", [m[k]["sale_action_on_menu"] for k in ("G12 d190", "G12 d249", "G17 d234")], [True, True, True])
claim("unlocked collateral", [m["G12 d190"]["mortgage_value_locked_behind_buildings"], m["G17 d234"]["mortgage_value_locked_behind_buildings"]], [340, 375], "\\$340 of mortgages")
claim("G2 d243 actor", rec["A_g2_actors"]["d243"]["model"], "Gemini")
fq = rec["F_quote_arithmetic"]["g2_d124_note"]
claim("G2 note arithmetic", [fq["residual_cash_845_minus_325"], fq["houses_520_buys"], fq["cost_of_nine"]], [520, 3, 1350], "nine would cost \\$1,350")
g = rec["G_chronology"]
claim("G2 turn-69 cash", [g["g2_offers"]["d198"]["author_cash_before"], g["g2_offers"]["d198"]["recipient_cash_before"]], [17, 435], "At turn 69 Opus has \\$17 and Sol \\$435")
claim("G15 cash if accepted", [g["g15_offers"]["d169"]["author_cash_if_accepted"], g["g15_offers"]["d169"]["recipient_cash_if_accepted"]], [830, 233])
claim("G15 cell", g["g15_offers"]["d169"]["completion_cell"], "both")
claim("G2 eliminations", [(e["debtor"], e["turn"], e["owed"]) for e in g["eliminations"]["G2"]], [("Opus", 72, 1300), ("Sol", 85, 1300), ("Grok", 102, 330)])
claim("G15 first elimination", (g["eliminations"]["G15"][0]["debtor"], g["eliminations"]["G15"][0]["turn"]), ("Grok", 81))

# --- direct recomputation of the few prose numbers not carried in the JSON outputs
from common import ledger  # noqa: E402

_offers = ledger("agenda_offers.json")
_conf = {(c["game"], int(c["decision_id"].rsplit("-", 1)[1])) for c in ledger("resolution_conditions.json")["selected_grok_conflicts"]}
_legal = [o for o in _offers if o["accept_available"]]
_acc = [o for o in _legal if o["completion_cell"] == "author_only" and o["response"] == "accept_trade"]
claim("accepted author-only", len(_acc), 19, "Nineteen offers that would complete only the author's group were accepted")
claim("accepted author-only after a counter", sum(o["exchange_index"] > 0 for o in _acc), 16, "Sixteen of the nineteen")
claim("accepted author-only, recipient under 100", sum(o["recipient_cash_before"] < 100 for o in _acc), 8, "In eight the recipient held under \\$100")
claim("accepted author-only by Opus", [sum(o["recipient_model"] == "Opus" for o in _acc), sum(o["recipient_model"] == "Opus" and o["response_condition"] != "standard" for o in _acc)], [7, 7], "Seven were accepted by Opus, all through the action-only path")
claim("accepted author-only conflicts", sum((o["game"], o["decision"]) in _conf for o in _acc), 3)
_first_ao = [o for o in _legal if o["completion_cell"] == "author_only" and o["exchange_index"] == 0]
claim("opening author-only accepted without conflict", sum(o["response"] == "accept_trade" and (o["game"], o["decision"]) not in _conf for o in _first_ao), 1, "one of 187 such opening offers")
_gem_first = lambda cell: [o for o in _legal if o["recipient_model"] == "Gemini" and o["completion_cell"] == cell and o["exchange_index"] == 0]
claim("Gemini opening rejections", [sum(o["response"] == "reject_trade" for o in _gem_first("author_only")), len(_gem_first("author_only")), sum(o["response"] == "reject_trade" for o in _gem_first("neither")), len(_gem_first("neither"))], [62, 67, 83, 95], "Gemini rejects 62 of 67 opening author-only offers and also 83 of 95")
claim("opus counters by cell", [sum(o["response"] == "counter_trade" for o in _legal if o["recipient_model"] == "Opus" and o["completion_cell"] == c) for c in ("author_only", "recipient_only")], [42, 31], "(42 of 52 and 31 of 42)")
_settle = [o for o in _offers if o["response"] == "accept_trade"]
claim("settlements with non-initiator author", sum(o["author"] != o["initiator"] for o in _settle), 44, "In 44 settlements")

import collections as _c  # noqa: E402

_thr = _c.defaultdict(list)
for _o in _offers:
    _thr[_o["thread_id"]].append(_o)
_raises = []
for _t in _thr.values():
    _t.sort(key=lambda r: r["exchange_index"])
    if _t[0]["completion_cell"] != "author_only" or not _t[0]["accept_available"] or _t[-1]["response"] != "accept_trade":
        continue
    _init, _last = _t[0]["author"], _t[-1]
    if not (_last["author_new_groups"] if _last["author"] == _init else _last["recipient_new_groups"]):
        continue
    _cN = _last["net_cash_author_to_recipient"] if _last["author"] == _init else -_last["net_cash_author_to_recipient"]
    _raises.append(_cN - _t[0]["net_cash_author_to_recipient"])
claim("initiator pays more in settled completing threads", [sum(r > 0 for r in _raises), len(_raises)], [18, 24], "in 18 of the 24")

# --- R13 insertions
def _seller(o):
    c = o["net_cash_author_to_recipient"]
    if c > 0:
        return (o["recipient_cash_before"], bool(o["author_new_groups"]), o["recipient_model"], o["completion_cell"])
    if c < 0:
        return (o["author_cash_before"], bool(o["recipient_new_groups"]), o["author_model"], o["completion_cell"])
    return None


from common import median as _median  # noqa: E402

_rows = [r for r in map(_seller, _settle) if r]
_comp = [r for r in _rows if r[1]]
_nei = [r for r in _rows if r[3] == "neither"]
claim("seller cash, integrated definition", [len(_comp), _median([r[0] for r in _comp]), len(_nei), _median([r[0] for r in _nei])], [48, 194.0, 57, 571])
claim("Opus share of completing sales", [sum(r[2] == "Opus" for r in _comp), sum(r[2] == "Opus" and r[0] < 100 for r in _comp), sum(r[0] < 100 for r in _comp)], [21, 13, 21], "Opus is the seller in 21 of the 48 and in 13 of the 21 below")
_c2 = [r for r in _comp if r[2] != "Opus"]
_n2 = [r for r in _nei if r[2] != "Opus"]
claim("seller cash without Opus", [_median([r[0] for r in _c2]), _median([r[0] for r in _n2]), sum(r[0] < 100 for r in _c2), len(_c2)], [287, 642, 8, 27], "medians are \\$287 and \\$642, and 8 of 27")
claim("opening accepted, neither", [sum(o["response"] == "accept_trade" for o in _legal if o["completion_cell"] == "neither" and o["exchange_index"] == 0), sum(1 for o in _legal if o["completion_cell"] == "neither" and o["exchange_index"] == 0)], [24, 238], "against 24 of 238 opening offers that complete nothing")
claim("R13 literals", True, True, "accepted 3 times in 187, twice by a tool call whose own text declined it")
claim("R13 note totals", [225 + 130 + 53, 500 + 30], [408, 530], "Sol's note stops at \\$408 against \\$500 and leaves out \\$340")
claim("G13 turns", [146 - 107, 150 - 146, 114 - 107], [39, 4, 7], "for 39 turns, and it pays \\$200 on another of Sol's railroads four turns before the end")

bad = [c for c in checks if not c["match"] or c["literal_in_tex"] is False]
report = {"assertions": len(checks), "failed": len(bad), "failures": bad, "checks": checks}
with open(os.path.join(OUT, "replacement_number_checks.json"), "w") as fh:
    json.dump(report, fh, indent=1, default=str)
    fh.write("\n")
print(f"{len(checks)} assertions, {len(bad)} failed")
for c in bad:
    print("FAIL", json.dumps(c, default=str))
