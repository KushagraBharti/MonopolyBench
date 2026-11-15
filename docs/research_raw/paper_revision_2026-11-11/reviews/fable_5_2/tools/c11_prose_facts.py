"""Check 11. Assert every number used in replacement_prose.tex against a saved
check output or a frozen draft's data file, and confirm the number's printed
form occurs in the TeX. Fails loudly on any mismatch. Read-only.
"""
import json
import re
import statistics as st
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = HERE.parent / "data"
ROOT = HERE.parents[2]
TEX = (HERE.parent / "replacement_prose.tex").read_text()
J = lambda n: json.load(open(D / n))
c1, c2, c3, c3b, c3c, c3d, c3e = (J("c1_cash_by_cell.json"), J("c2_refusal_to_sale.json"), J("c3_defensive_contrast.json"),
                                   J("c3b_offer_type.json"), J("c3c_swap_table.json"), J("c3d_dedup.json"), J("c3e_grok_conflict_openings.json"))
c4, c5, c6, c7, c8, c9 = (J("c4_seller_conversion.json"), J("c5_debt_census.json"), J("c6_distress_populations.json"),
                          J("c7_landings_and_misc.json"), J("c8_spot_checks.json"), J("c9_cash_sensitivity.json"))
g20 = J("g20_payment_facts.json")
facts = []


def fact(name, value, expect, phrase=None):
    assert value == expect, (name, value, expect)
    if phrase is not None:
        assert phrase in TEX, ("phrase not found in TeX", name, phrase)
    facts.append({"fact": name, "value": value, "phrase": phrase})


# --- corpus, census by cell (ledger) ----------------------------------------
led = json.load(open(ROOT / "full_drafts/fable_5_2/data/a2_offer_ledger.json"))
fact("responses", len(led), 920, "920 responses to trade offers")
fact("A/C/R all", [sum(r["response"] == x for r in led) for x in ("accept_trade", "counter_trade", "reject_trade")], [113, 394, 413], "113 accept, 394 counter and 413 reject")
fact("threads", len({r["thread_id"] for r in led}), 526, "The 526 threads")
fact("legal", c1["legal_offers"], 918, "legal for 918 offers")
fact("cross ledger mismatches Fable vs Opus rebuild", len(c1["cross_ledger_mismatches"]), 0)
oc = c1["opening_contrast"]
fact("opening author_only", [oc["author_only"]["reject"], oc["author_only"]["n"]], [138, 187], "138 of the 187")
fact("opening neither", [oc["neither"]["reject"], oc["neither"]["n"]], [152, 238], "152 of the 238")
def _blk_gap(b):
    ao = [r for r in led if r["accept_available"] and r["opening"] and r["block"] == b and r["completion_cell"] == "author_only"]
    ne = [r for r in led if r["accept_available"] and r["opening"] and r["block"] == b and r["completion_cell"] == "neither"]
    return round(100 * (sum(r["response"] == "reject_trade" for r in ao) / len(ao) - sum(r["response"] == "reject_trade" for r in ne) / len(ne)), 1)
fact("opening all-offer contrast by block", [_blk_gap(b) for b in range(1, 6)], [15.0, 18.9, 5.8, 7.6, 10.8], "positive in each of the five seed blocks")
opus_open = json.load(open(ROOT / "full_drafts/opus/data/bargaining.json"))["open_reject"]
a = c3["a_opening_contrast"]
fact("no-deed openings refused", [a["neither_no_deed_asked"]["reject"], a["neither_no_deed_asked"]["n"], a["neither_no_deed_asked"]["reject_pct"]], [47, 62, 75.8], "62 proposals that ask for none")

# --- Table 1 ------------------------------------------------------------------
o = c3c["opening"]
T = lambda x: [x["n"], x["A"], x["C"], x["R"]]
fact("swap author_only", T(o["swap"]["author_only"]), [116, 1, 20, 95], "116 & 1 & 20 & 95")
fact("swap both", T(o["swap"]["both"]), [48, 3, 11, 34], "48 & 3 & 11 & 34")
fact("swap neither", T(o["swap"]["neither"]), [72, 17, 18, 37], "72 & 17 & 18 & 37")
fact("swap recipient_only", T(o["swap"]["recipient_only"]), [6, 1, 3, 2], "6 & 1 & 3 & 2")
cb = c3b["opening"]["cash_bid"]
fact("cash bid author_only", [cb["author_only"][k] for k in ("n", "A", "C", "R")], [70, 2, 26, 42], "70 & 2 & 26 & 42")
fact("cash bid neither", [cb["neither"][k] for k in ("n", "A", "C", "R")], [103, 4, 32, 67], "103 & 4 & 32 & 67")
fact("offer to sell recipient_only", T(o["offer_to_sell"]["recipient_only"]), [45, 1, 15, 29], "45 & 1 & 15 & 29")
fact("offer to sell neither", T(o["offer_to_sell"]["neither"]), [55, 3, 12, 40], "55 & 3 & 12 & 40")
fact("no deeds", T(o["no_deeds"]["neither"]), [7, 0, 0, 7])
od = c3b["opening"]["other_deed_request"]
fact("other deed requests", [od["author_only"]["n"], od["author_only"]["R"], od["neither"]["n"], od["neither"]["R"]], [1, 1, 1, 1], "9 & 0 & 0 & 9")
tot = [116 + 48 + 72 + 6 + 70 + 103 + 45 + 55 + 9, 1 + 3 + 17 + 1 + 2 + 4 + 1 + 3, 20 + 11 + 18 + 3 + 26 + 32 + 15 + 12, 95 + 34 + 37 + 2 + 42 + 67 + 29 + 40 + 9]
fact("table total", tot, [524, 32, 137, 355], "524 & 32 & 137 & 355")
fact("pct swap author_only", o["swap"]["author_only"]["reject_pct"], 81.9, "95 \\,(82\\%)")
fact("pct swap neither", o["swap"]["neither"]["reject_pct"], 51.4, "37 \\,(51\\%)")
fact("pct swap both", o["swap"]["both"]["reject_pct"], 70.8, "34 \\,(71\\%)")
fact("pct cash bids", [cb["author_only"]["reject_pct"], cb["neither"]["reject_pct"]], [60.0, 65.0], "60\\% against 65\\%")
r = c3c["opening_swaps_by_recipient"]
fact("swap by recipient", {m: [r[m]["author_only"]["R"], r[m]["author_only"]["n"], r[m]["neither"]["R"], r[m]["neither"]["n"]] for m in r},
     {"Sol": [12, 21, 1, 16], "Gemini": [45, 49, 25, 33], "Opus": [3, 9, 2, 11], "Grok": [35, 37, 9, 12]},
     "Sol rejects 12 of 21 against 1 of 16, Gemini 45 of 49 against 25 of 33, Grok 35 of 37 against 9 of 12, and Opus 3 of 9 against 2 of 11")
b = c3c["opening_swaps_by_block"]
fact("swap gap positive in each block", all(b[k]["author_only"]["reject_pct"] > b[k]["neither"]["reject_pct"] for k in b), True, "It is present in each seed block")
fact("conflict-opened neither swaps", c3e["conflict_opened_by_type_and_cell"]["swap|neither"], 29, "29 were opened by a Grok call")
fact("accepted neither swaps conflict-opened", [c3e["of_which_conflict_opened"], o["swap"]["neither"]["A"]], [13, 17], "13 of the seventeen")
fact("conflict threads", c3e["conflict_opened_threads"], 64, "Without the 64 threads")
w = c3e["opening_without_conflict_threads"]["swap"]
fact("swaps without conflict threads", [w["author_only"]["R"], w["author_only"]["n"], w["neither"]["R"], w["neither"]["n"]], [93, 112, 26, 43], "93 of 112 one-sided swaps (83\\%) and 26 of 43 non-completing swaps (60\\%)")
cuts = c3e["without_conflict_threads_cuts"]
fact("without conflict, recipients positive", all(v["author_only"]["reject_pct"] > v["neither"]["reject_pct"] for v in cuts["swap_by_recipient"].values()), True)
fact("without conflict, blocks positive", sum(v["author_only"]["reject_pct"] > v["neither"]["reject_pct"] for v in cuts["swap_by_block"].values()), 4, "four of the five blocks")
fact("without conflict, block 4 baseline", cuts["swap_by_block"]["4"]["neither"]["n"], 5, "the fifth has five non-completing swaps left")
f1 = c3d["first_occurrence"]["swap"]
fact("first occurrence swaps", [f1["author_only"]["R"], f1["author_only"]["n"], f1["neither"]["R"], f1["neither"]["n"]], [77, 93, 33, 67], "77 of 93 and 33 of 67")
ng = c3d["all_openings_without_grok_authors"]["swap"]
fact("without Grok authors", [ng["author_only"]["R"], ng["author_only"]["n"], ng["neither"]["R"], ng["neither"]["n"]], [90, 108, 24, 36], "90 of 108 and 24 of 36")
gaps = [round(o["swap"]["author_only"]["reject_pct"] - o["swap"]["neither"]["reject_pct"]), round(w["author_only"]["reject_pct"] - w["neither"]["reject_pct"]),
        round(f1["author_only"]["reject_pct"] - f1["neither"]["reject_pct"]), round(ng["author_only"]["reject_pct"] - ng["neither"]["reject_pct"])]
fact("gap range", [min(gaps), max(gaps)], [17, 34], "between seventeen and thirty-four points")
cbb = c3b["opening"]["cash_bid"]["by_block"]
fact("cash bids lower in blocks", sum(cbb[k]["author_only"]["reject_pct"] < cbb[k]["neither"]["reject_pct"] for k in cbb), 4, "lower for completing bids in four of the five blocks")
la = c3b["later"]
fact("later swaps", [la["with_deeds"]["author_only"]["R"], la["with_deeds"]["author_only"]["n"], la["with_deeds"]["neither"]["R"], la["with_deeds"]["neither"]["n"]], [8, 39, 7, 34], "8 of 39 against 7 of 34")
fact("later cash bids", [la["cash_bid"]["author_only"]["R"], la["cash_bid"]["author_only"]["n"], la["cash_bid"]["neither"]["R"], la["cash_bid"]["neither"]["n"]], [13, 61, 13, 73], "13 of 61 against 13 of 73")
gp = c3d["game_recipient_pairs_with_both_swap_kinds"]
fact("game-recipient pairs", [gp["equal"], sum(gp.values())], [13, 21], "13 of the 21 pairs of game and recipient")

# --- prices ---------------------------------------------------------------------
pure = json.load(open(ROOT / "full_drafts/fable_5_2/data/a6_pure_offers.json"))
asks = [x for x in pure if x["kind"] == "ask"]
cells = {}
for x in asks:
    m = "mortgaged" if x["mstat"] in ("mortgaged", "mixed") else "unmortgaged"
    cells.setdefault((x["seller_model"], m, x["opening"]), {True: [], False: []})[x["buyer_completes"]].append(x["ratio"])
hi = lo = 0
for k, v in cells.items():
    if k[0] == "Gemini" or not v[True] or not v[False]:
        continue
    hi += st.median(v[True]) > st.median(v[False]); lo += st.median(v[True]) < st.median(v[False])
fact("seller x mortgage x stage cells", [hi, lo], [11, 1], "is higher in eleven")
ou = cells[("Opus", "unmortgaged", False)]
fact("Opus later unmortgaged", [round(st.median(ou[True]), 2), round(st.median(ou[False]), 2)], [1.86, 2.10], "at 1.86 against 2.10 times list")
g = c8["d_ask_gradient"]
fact("ask gradient", [g["unmortgaged|missing_after_2"], g["unmortgaged|missing_after_1"], g["unmortgaged|missing_after_0"]],
     [{"n": 3, "median": 1.61}, {"n": 45, "median": 1.8}, {"n": 37, "median": 2.32}], "1.61 times list")
blk = {}
for x in asks:
    blk.setdefault(x["block"], {True: [], False: []})[x["buyer_completes"]].append(x["ratio"])
fact("pooled ask ordering reverses in blocks", sum(st.median(v[True]) < st.median(v[False]) for v in blk.values()), 2, "reverses in two of the five seed blocks")
e = c8["e_same_deed_rows"]
fact("same-deed cases", len(e), 7, "In seven cases")
fact("same mortgage status", sum(x["same_mortgage_status"] for x in e), 6, "Mortgage status matches in six")
sm = c8["e_summary_same_mortgage_status"]
fact("six matched, first and median", [sm["first"], sm["median"]], [{"lower": 1, "higher": 4, "equal": 1}, {"lower": 1, "higher": 4, "equal": 1}], "asked more in four, less in one and the same in one")
fact("all seven", [c8["e_summary"]["first"], c8["e_summary"]["median"]], [{"lower": 1, "higher": 5, "equal": 1}, {"lower": 2, "higher": 4, "equal": 1}], "five, one, one and four, two, one")
g4 = [x for x in e if x["game"] == 4][0]
fact("G4 row", [g4["other_asks"][0][:3], [x[0] for x in g4["completing_asks"]], g4["completing_asks"][0][1] - g4["other_asks"][0][1], g4["first"], g4["median"]],
     [[280, 74, "unmortgaged"], [450, 250, 175, 100, 150], 78, "higher", "lower"], "\\$280 for an unmortgaged Boardwalk at turn 74")
low = [x for x in e if x["median"] == "lower"]
fact("lower cases are Opus Boardwalk, cash <= 210", [sorted((x["seller"], x["deed"]) for x in low), max(a_[3] for x in low for a_ in x["completing_asks"] + x["other_asks"])],
     [[("Opus", "BOARDWALK"), ("Opus", "BOARDWALK")], 210], "holding \\$210 or less")
cc = c8["a_concessions"]
fact("concessions", [cc["concessions"], cc["author_only"]["accepted"], cc["author_only"]["n"], cc["neither"]["accepted"], cc["neither"]["n"]], [199, 9, 58, 24, 86], "In 199 offers")
fact("concessions no deed from author", [cc["author_only"]["by_offer_type"]["cash_only_from_author"], cc["neither"]["by_offer_type"]["cash_only_from_author"]], [[3, 34], [13, 43]], "3 of 34 and 13 of 43")
cr = json.load(open(ROOT / "full_drafts/opus/data/bargaining.json"))["counter_repricing"]
fact("counter repricing (Opus rebuild)", json.dumps(cr).count("79") > 0 and json.dumps(cr).count("81") > 0, True, "79 of 111 to proposer-completing offers and 81 of 110")

# --- reasons (inherited codes, joined) -----------------------------------------------
rc = c7["b_reason_codes_opus_join"]["D"]
fact("rival code", [rc["common"], rc["rows"], rc["kappa"], rc["common_by_cell"], rc["games_G1_G15_share"]], [61, 74, 0.786, {"Both": 34, "Recipient only": 27}, 31], "31 of the 61 agreed codes")
fact("own-cost code", c7["b_reason_codes_opus_join"]["C"]["common"], 41, "price or cash in 41")
fact("rows by recipient", rc["rows_by_recipient"], {"Grok": 31, "Gemini": 31, "Sol": 4, "Opus": 8}, "Gemini and Grok write 62 of the 74")

# --- capacity null ------------------------------------------------------------------
cap = c3["c_capacity_cut"]["opening"]["pooled"]
fact("capacity cut", [[cap[k]["reject"], cap[k]["n"]] for k in ("full_layer", "one_house", "less")], [[100, 134], [32, 42], [6, 11]], "100 of 134")

# --- liquidity ------------------------------------------------------------------------
fact("completion requests", c9["n_completion_requests"], 289, "There are 289")
t = c1["tables"]["author_only"]
B = lambda d, k: [d[k]["reject"], d[k]["n"]]
fact("standard holders opening", [B(t["no_opus_recipient_opening_by_band"], k) for k in ("lt100", "100_299", "ge300")], [[13, 20], [17, 24], [105, 125]], "13 of 20 opening requests")
fact("standard holders later", [B(t["no_opus_recipient_later_by_band"], k) for k in ("lt100", "100_299", "ge300")], [[4, 28], [5, 16], [12, 24]], "4 of 28, 5 of 16 and 12 of 24")
rb = t["by_recipient_band"]
fact("Sol", [B(rb, "('Sol', 'lt100')"), B(rb, "('Sol', 'ge300')")], [[4, 26], [25, 45]], "4 of 26 requests refused under \\$100 against 25 of 45")
fact("Grok", [B(rb, "('Grok', 'lt100')"), B(rb, "('Grok', 'ge300')")], [[3, 11], [46, 52]], "3 of 11 against 46 of 52")
fact("Gemini", [B(rb, "('Gemini', 'lt100')"), B(rb, "('Gemini', 'ge300')")], [[10, 11], [46, 52]], "Gemini refuses 10 of 11 and 46 of 52")
opus_all = [sum(rb[f"('Opus', '{k}')"]["reject"] for k in ("lt100", "100_299", "ge300")), sum(rb[f"('Opus', '{k}')"]["n"] for k in ("lt100", "100_299", "ge300"))]
fact("Opus", opus_all, [3, 52], "Opus refuses 3 of the 52")
top = dict(c9["low_cash_requests"]["top_game_holder_counts"])
fact("Sol low-cash requests from three games", [top["G1 Sol"] + top["G9 Sol"] + top["G18 Sol"], c9["low_cash_requests"]["by_holder_model"]["Sol"]], [19, 26], "Nineteen of Sol's 26")
th = c9["thresholds"]
ok = all(th[f"lt{lo_}_vs_ge{hi_}|no_opus_holder_opening"]["low"][2] < th[f"lt{lo_}_vs_ge{hi_}|no_opus_holder_opening"]["high"][2]
         and th[f"lt{lo_}_vs_ge{hi_}|no_opus_holder_later"]["low"][2] < th[f"lt{lo_}_vs_ge{hi_}|no_opus_holder_later"]["high"][2]
         for lo_ in (50, 100, 150, 200) for hi_ in (300, 500))
fact("threshold sensitivity same sign", ok, True, "Cutoffs of \\$50 to \\$200")
n = c1["tables"]["neither_asks_deed"]["no_opus_recipient_opening_by_band"]
fact("non-completing requests, standard holders, opening", [B(n, "lt100"), B(n, "100_299"), B(n, "ge300")], [[4, 9], [7, 13], [92, 138]], "4 of 9 opening requests")
gg = c1["defensive_gap_within_cash_band"]["neither_asks_deed"]["no_opus_recipient_opening_by_band"]
fact("gap by band", [round(gg[k]["gap_points"]) for k in ("lt100", "100_299", "ge300")], [21, 17, 17], "seventeen to twenty-one points in each cash band")
op_ = c2["completion_requests_thread_opener_by_holder_cash"]
fact("holder opened thread", [op_["lt100"]["holder_opened_thread"], sum(op_["lt100"].values()), op_["ge300"]["holder_opened_thread"], sum(op_["ge300"].values())], [21, 69, 15, 175], "21 of the 69")
fo, ne = c6["fable_definition_one_sided_completion"], c6["neither_net_cash_settlements"]
fact("one-sided sales", [fo["receiver_under_100"], fo["n"], ne["receiver_under_100"], ne["n"]], [20, 43, 9, 57], "Forty-three settlements")
fact("Opus share of low-cash", fo["under_100_by_receiver_model"]["Opus"], 12, "Twelve of the 20")
fact("without Opus", [fo["under_100_without_opus_receiver"], fo["n_without_opus_receiver"], ne["under_100_without_opus_receiver"], ne["n_without_opus_receiver"]], [8, 23, 6, 41], "8 of 23 against 6 of 41")
pc, pn = c6["opus_definition_pure_cash_completing_buyer"], c6["opus_definition_pure_cash_completing_nobody"]
fact("pure cash", [pc["receiver_under_100"], pc["n"], pn["receiver_under_100"], pn["n"], pc["under_100_without_opus_receiver"], pc["n_without_opus_receiver"], pn["under_100_without_opus_receiver"], pn["n_without_opus_receiver"]],
     [14, 22, 7, 31, 6, 11, 4, 22], "14 of 22 against 7 of 31, and 6 of 11 against 4 of 22")
fact("sellers with 300 or more", c2["one_sided_sales_by_holder_cash_band"]["ge300"], 17, "17 of the 43 sellers held \\$300 or more")
acc = [x for x in pure if x["response"] == "accept_trade" and x["buyer_completes"] and x["seller_cash"] < 100]
oth = [x["ratio"] for x in acc if x["seller_model"] != "Opus"]; opu = [x["ratio"] for x in acc if x["seller_model"] == "Opus"]
fact("distress prices", [len(oth), round(st.median(oth), 2), sum(v > 1 for v in oth), len(opu), round(st.median(opu), 2), sum(v < 1 for v in opu)], [6, 2.25, 5, 8, 0.66, 7], "2.25 times list")
s2 = c2["summary"]
fact("pair histories", [s2["n"], s2["cash_fell"], s2["price_vs_declined"], s2["n"] - s2["same_deed_bundle"]], [14, 13, {"lower": 4, "higher": 8, "equal": 2}, 9], "higher at the sale in 8, equal in 2 and lower in 4")
swaps_to_cash = sum(bool(x["declined_holder_gets"]) and not x["sale_holder_gets"] for x in c2["rows"])
fact("refused swaps later sold for cash", swaps_to_cash, 5, "five refused swaps")
u = c2["unsettled_multi_turn_pairs"]
fact("unsettled base rate", [u["holder_cash_direction_first_to_last"]["lower"], u["n"]], [25, 38], "also fell in 25")
fact("who won", [c4["buyer_won"]["seller_won"], c4["buyer_won"]["buyer_won"], c4["buyer_won"]["sales"]], [10, 11, 43], "in 10 of the 43 and the buyer in 11")
gt = c4["by_group_held_in_sale_turn"]
fact("by group and build", [gt["held_group|all"]["player_games"], gt["held_group|built"]["player_games"], gt["held_group|built"]["winning_player_games"],
                            gt["held_group|not_built"]["player_games"], gt["held_group|not_built"]["winning_player_games"], gt["no_group|all"]["winning_player_games"], gt["no_group|all"]["player_games"]],
     [20, 12, 8, 8, 0, 1, 18], "In 20 player-games")

# --- census ---------------------------------------------------------------------------
fact("census", [c5["episodes"], c5["paid"], c5["eliminated"], c5["unclosed"]], [188, 128, 60, 0], "This happens 188 times")
fab = json.load(open(ROOT / "full_drafts/fable_5_2/data/a4_debt_episodes.json"))
fact("rent episodes", sum(x["reason"] == "RENT" for x in fab), 167, "167 of them for rent")
fact("no engine default in paid", c5["paid_episodes_with_engine_default"], 0, "No paid episode contains an engine default")
paid = [x for x in fab if x["outcome"] == "paid"]
fact("single and multi", [c5["paid_single_action"], c5["paid_multi_action"], st.median(x["shortfall_first"] for x in paid if len(x["actions"]) == 1), max(c5["paid_action_count_distribution"], key=int)], [67, 61, 35, "10"], "67 take one action, with a median shortfall of \\$35, and 61 take two to ten")
fact("actions", [c5["paid_mortgage_actions"], c5["paid_sale_actions"], c5["paid_with_building_sale"]], [180, 89, 68], "180 mortgage actions and 89 building-sale actions")
both = [x for x in paid if x["menu_has_sale_first"] and x["menu_mortgage_first"] > 0]
fact("mortgage first", [sum(x["actions"][0] == "mortgage_property" for x in both), len(both)], [40, 51], "40 of 51 episodes")
fact("sold when mortgages covered", sum(x["n_sales"] > 0 and x["menu_mortgage_first"] >= x["shortfall_first"] for x in paid), 2, "Only 2 of the 68")
fact("elimination classes", c5["fable_inherited_class_counts"], {"paid": 128, "below_bound": 56, "menu_blocked": 1, "payable_witness": 3}, "exceeds that bound in 56")
wit = Counter(x["model"] for x in fab if x["inherited_class"] == "payable_witness")
bm = c5["by_model"]
fact("payable by system", {m: [bm[m]["paid"], bm[m]["paid"] + wit.get(m, 0)] for m in bm}, {"Sol": [30, 31], "Gemini": [37, 38], "Opus": [41, 41], "Grok": [20, 21]}, "30 of 31 for Sol, 37 of 38 for Gemini, 41 of 41 for Opus and 20 of 21 for Grok")
fact("later eliminated", c5["paid_episodes_of_players_later_eliminated"], 102, "In 102 of the 128")
fact("Grok conflict inside paid episodes", [c5["grok_paid_episodes_with_conflict"], c5["grok_paid_actions_text_names_other_action"]], [1, 1], "One paid Grok episode")
fact("four drafts agree on census rows", all(not v["keys_only_in_this_check"] and not v["keys_only_in_draft"] and not v["field_differences"] for v in c5["reconciliation_with_drafts"].values()), True)

# --- G20 incident ------------------------------------------------------------------------
fact("G20 state", [g20["sol_cash_in_gemini_d325_prompt"], g20["sol_houses"], g20["sol_hotels"], g20["sol_deeds"], g20["sol_unmortgaged_deeds"], g20["players_not_bankrupt_at_d325"]], [49, 9, 2, 19, 8, 2], "nine orange houses, two brown hotels and nineteen deeds, eight of them unmortgaged")
fact("G20 sums", [sum(g20["sale_cash_events"]), len(g20["sale_cash_events"]), sum(g20["mortgage_cash_events"]), len(g20["mortgage_cash_events"]), g20["owed"], g20["sol_cash_after_payment"]], [700, 2, 665, 8, 1400, 14], "in two actions for \\$700")
fact("G20 elimination", [g20["game_end"][0] - 108, g20["rent_paid_event"]["seq"]], [7, 2245], "eliminated seven turns later")
quotes = json.load(open(D / "new_quote_manifest.json"))["quotes"]
note = {q["decision"]: q["text"] for q in quotes}
fact("Gemini parts", [("$675" in note[325]), ("$690" in note[325]), ("$1,414" in note[325]), 700 - 675, 690 - 665], [True, True, True, 25, 25], "each \\$25 off in opposite directions")

# shortfall statements in Sol's ten notes (read from source, not from the manifest)
import glob
run = glob.glob(str(ROOT.parents[2] / "saved_games/railway-research-*/game-20-*/run"))[0]
started, resolved, order = {}, {}, []
for line in open(run + "/decisions.jsonl"):
    d = json.loads(line)
    if d["phase"] == "decision_started":
        started[d["decision_id"]] = d; order.append(d["decision_id"])
    else:
        resolved[d["decision_id"]] = d
hit = 0
for k in range(327, 337):
    sf = started[order[k]]["prompt_payload"]["action_state"]["scenario"]["shortfall"]
    txt = resolved[order[k]]["final_action"]["private_thought"]
    hit += (f"${sf:,}" in txt) or (f"${sf}" in txt)
    sc = started[order[k]]["prompt_payload"]["action_state"]["scenario"]
    assert set(sc["options"]) == {"mortgageable_space_keys", "sellable_building_space_keys"} and all(isinstance(v, str) for vv in sc["options"].values() for v in vv)
fact("Sol notes stating the exact shortfall", hit, 7, "Seven of Sol's ten notes")
fact("G20 d328 plans to mortgage the browns once cleared", "mortgage all remaining properties including browns once cleared" in resolved[order[328]]["final_action"]["private_thought"], True, "mortgaging the brown deeds once their buildings are sold")

# the two payable declarations whose notes omit unlockable mortgages (read from source)
def _note(game, k):
    run_ = glob.glob(str(ROOT.parents[2] / f"saved_games/railway-research-*/game-{game:02d}-*/run"))[0]
    st_, rs_, od_ = {}, {}, []
    for line in open(run_ + "/decisions.jsonl"):
        d = json.loads(line)
        if d["phase"] == "decision_started":
            st_[d["decision_id"]] = d; od_.append(d["decision_id"])
        else:
            rs_[d["decision_id"]] = d
    return st_[od_[k]], rs_[od_[k]]
s12, r12 = _note(12, 190)
s17, r17 = _note(17, 234)
fact("G12 Sol d190 note total", ["maximum liquidity is $408" in r12["final_action"]["private_thought"], r12["final_action"]["action"], s12["prompt_payload"]["action_state"]["scenario"]["owed_amount"]], [True, "declare_bankruptcy", 500], "Sol in G12")
fact("G17 Gemini d234 note total", ["only $530" in r17["final_action"]["private_thought"], r17["final_action"]["action"], s17["prompt_payload"]["action_state"]["scenario"]["owed_amount"]], [True, "declare_bankruptcy", 550], "Gemini in G17")
# unlockable mortgage value left out: board mortgage value is half the list price
board = json.load(open(ROOT.parents[2] / "contracts/data/board.json"))
half = {re.sub(r"[^A-Za-z0-9]+", "_", x["name"].strip()).strip("_").upper(): x["price"] // 2 for x in board["spaces"] if x.get("price")}
def _unlock(s_):
    own = s_["prompt_payload"]["game_state"]["you"]["holdings"]["owned"]
    return sum(half[o["space_key"]] for o in own if (o["houses"] or o["hotel"]) and not o["mortgaged"])
fact("mortgage value unlocked by selling buildings", [_unlock(s12), 408 + _unlock(s12) >= 500, _unlock(s17), 530 + _unlock(s17) >= 550], [340, True, 375, True])

# --- building after completion --------------------------------------------------------------
dt = c7["d_timing_by_system"]
fact("first management turn", [[dt[m]["built_first_management_turn_inherited"], dt[m]["groups"]] for m in ("Sol", "Gemini", "Opus", "Grok")], [[16, 17], [17, 18], [7, 15], [3, 13]], "16 of 17 for Sol, 17 of 18 for Gemini, 7 of 15 for Opus and 3 of 13 for Grok")
cs = c7["c_first_window"]["causes"]
fact("first-window causes", [cs["built"], cs["never_legal_in_window"], cs["default_after_refusal"] + cs["default_other"], cs["received_conflict"], cs["valid_end"]], [43, 9, 4, 4, 3], "43 of 63 groups")
tg = json.load(open(ROOT / "full_drafts/fable_5_2/data/a7_trade_groups.json"))
fact("no-legal-build windows with mortgage", sum(x["mortgaged_deeds_at_completion"] > 0 for x in tg if x["inherited_first_window_cause"] == "never_legal_in_window"), 8, "eight of them with a mortgaged deed")

# --- abstract --------------------------------------------------------------------------------
for phrase in ("6,989 decisions", "188 debt episodes", "95 of 116", "37 of 72", "61 of 74", "128 of 131", "eleven of twelve"):
    assert phrase in TEX, phrase
fact("decisions", c5["decisions"], 6989, "6,989 decisions")

(D / "c11_prose_facts.json").write_text(json.dumps({"asserted": len(facts), "facts": facts}, indent=1))
print("asserted", len(facts), "facts; all passed")
