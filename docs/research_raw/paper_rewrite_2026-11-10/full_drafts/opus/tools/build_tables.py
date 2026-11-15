#!/usr/bin/env python3
"""Write data-derived appendix tables for the Opus draft.

Reads ../data/opus_retabulation.json (from tools/retabulate.py) and shared
../../data/t01_cohort.json and t02_negotiation.json. Writes sections/gen_*.tex.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DRAFT = HERE.parent
SHARED = DRAFT.parents[1] / "data"
R = json.loads((DRAFT / "data" / "opus_retabulation.json").read_text())
CELLS = [("neither", "Neither"), ("author_only", "Author only"), ("recipient_only", "Recipient only"), ("both", "Both")]
CONFIGS = ["Sol", "Gemini", "Opus", "Grok"]


def acr(t):
    return f"{t['accept']}/{t['counter']}/{t['reject']}"


def money(x):
    if x is None:
        return "--"
    sign = "$-$" if x < 0 else ("$+$" if x > 0 else "")
    v = abs(x)
    s = f"{v:,.1f}" if v != int(v) else f"{int(v):,}"
    return f"{sign}\\${s}"


def write(name, text):
    (DRAFT / "sections" / name).write_text(text, encoding="utf-8")


def responder_table():
    rows = []
    for m in CONFIGS:
        cells = R["responder_by_cell_legal"][m]
        rows.append(f"{m} & " + " & ".join(f"{cells[c]['n']} & {acr(cells[c])}" for c, _ in CELLS) + r"\\")
    return r"""\begin{table}[htbp]
\centering\small
\begin{tabular}{@{}lrlrlrlrl@{}}
\toprule
& \multicolumn{2}{c}{Neither} & \multicolumn{2}{c}{Author only} & \multicolumn{2}{c}{Recipient only} & \multicolumn{2}{c}{Both}\\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}
Responder & $n$ & A/C/R & $n$ & A/C/R & $n$ & A/C/R & $n$ & A/C/R\\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\caption{Accept/counter/reject counts for the 918 acceptance-legal offers, by responding configuration and completion cell. Opus responded under the action-only condition in 162 of its 189 opportunities; under that condition it accepted 7 of 47 author-only and 3 of 34 recipient-only offers.}
\label{tab:app-responder}
\end{table}
"""


def block_table():
    rows = []
    for b in range(1, 6):
        cells = R["block_by_cell_legal"][str(b)]
        rows.append(f"{b} (G{4*b-3}--{4*b}) & " + " & ".join(
            f"{cells[c]['n']} & {acr(cells[c])}" for c in ["author_only", "recipient_only"]) + r"\\")
    return r"""\begin{table}[htbp]
\centering\small
\begin{tabular}{@{}lrlrl@{}}
\toprule
& \multicolumn{2}{c}{Author only} & \multicolumn{2}{c}{Recipient only}\\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
Seed block & $n$ & A/C/R & $n$ & A/C/R\\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\caption{Author-only and recipient-only offers by seed block. The rejection share is higher for author-only offers in every block; the acceptance share is lower in four blocks and reverses in block 3.}
\label{tab:app-blocks}
\end{table}
"""


def game_table():
    rows = []
    for g in range(1, 21):
        cells = R["game_author_vs_recipient_only_legal"][str(g)]
        a, r = cells["author_only"], cells["recipient_only"]
        rows.append(f"{g} & {a['n']} & {acr(a)} & {r['n']} & {acr(r)}" + r"\\")
    return r"""\begin{longtable}{@{}rrlrl@{}}
\caption{Author-only and recipient-only offers by game (A/C/R = accept/counter/reject). Game 6 has one recipient-only offer and game 5 none. Author-only rejection shares exceed recipient-only shares in """ + \
        f"{R['games_reject_share_author_gt_recipient']} of the {R['games_with_both_cells']}" + r""" games with both cells.}\label{tab:app-games}\\
\toprule Game & \multicolumn{2}{c}{Author only} & \multicolumn{2}{c}{Recipient only}\\
& $n$ & A/C/R & $n$ & A/C/R\\\midrule\endfirsthead
\toprule Game & \multicolumn{2}{c}{Author only} & \multicolumn{2}{c}{Recipient only}\\
& $n$ & A/C/R & $n$ & A/C/R\\\midrule\endhead
""" + "\n".join(rows) + r"""
\bottomrule
\end{longtable}
"""


def cash_table():
    rows = []
    med = R["median_net_cash_to_recipient_by_cell"]
    byr = R["median_net_cash_to_recipient_by_cell_response"]
    for c, label in CELLS:
        rows.append(f"{label} & {money(med[c])} & {money(byr[c]['accept'])} & {money(byr[c]['counter'])} & {money(byr[c]['reject'])}" + r"\\")
    seek = R["cash_seeking_by_author_cash"]
    srows = []
    for k, label in [("0-100", "Under \\$100"), ("100-300", "\\$100--299"), ("300-700", "\\$300--699"), ("700-inf", "\\$700 or more")]:
        t = seek[k]
        srows.append(f"{label} & {t['n']} & {t['accept']} & {t['counter']} & {t['reject']}" + r"\\")
    return r"""\begin{table}[htbp]
\centering\small
\begin{tabular}{@{}lrrrr@{}}
\toprule
Completion cell & All offers & Accepted & Countered & Rejected\\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}

\medskip
\begin{tabular}{@{}lrrrr@{}}
\toprule
Author's cash before offer & Cash-seeking offers & Accepted & Countered & Rejected\\
\midrule
""" + "\n".join(srows) + r"""
\bottomrule
\end{tabular}
\caption{Top: median net cash paid by the offer author to the recipient, by completion cell and response (acceptance-legal offers). Negative values mean the recipient would pay. Bottom: the """ + str(R["cash_seeking_legal_offers"]) + r""" acceptance-legal offers in which the author asks for net cash, by the author's cash on hand. The thresholds are descriptive choices, and cash on hand is not accessible finance.}
\label{tab:app-cash}
\end{table}
"""


def initiation_table():
    t02 = json.loads((SHARED / "t02_negotiation.json").read_text())
    rows = []
    for r in t02:
        rows.append(f"{r['configuration']} & {r['proposals']} & {r['proposing_turns']}/{r['eligible_turns']} & "
                    f"{100*r['own_turn_propensity']:.1f}\\% & {r['proposals_per_proposing_turn']:.2f} & {r['eligible_decisions']:,}" + r"\\")
    return r"""\begin{table}[htbp]
\centering\small
\begin{tabular}{@{}lrrrrr@{}}\toprule
Configuration & Proposals & Proposing/eligible own turns & Share & Per proposing turn & Eligible decisions\\\midrule
""" + "\n".join(rows) + r"""
\bottomrule\end{tabular}
\caption{Negotiation initiation (inherited ledger \texttt{t02\_negotiation.json}). Eligible decisions are an action-dependent denominator and not independent opportunities. None of these columns measures bargaining quality.}
\label{tab:app-initiation}
\end{table}
"""


def cohort_table():
    t01 = json.loads((SHARED / "t01_cohort.json").read_text())
    rows = [f"{c['game']} & {(c['game']-1)//4+1} & {c['seed']} & {c['rotation']} & {c['turns']} & {c['winner']} & {c['winner_seat']}" + r"\\" for c in t01]
    return r"""\begin{longtable}{rrrrrlr}
\caption{The twenty-game cohort. Seats and rotations are one-based. Games 1--4 and 5--20 carry different treatment fingerprints.}\label{tab:cohort}\\
\toprule Game & Block & Seed & Rotation & Turns & Winner & Winner seat\\\midrule\endfirsthead
\toprule Game & Block & Seed & Rotation & Turns & Winner & Winner seat\\\midrule\endhead
""" + "\n".join(rows) + r"""
\bottomrule\end{longtable}
"""


def main():
    write("gen_responder.tex", responder_table())
    write("gen_blocks.tex", block_table())
    write("gen_games.tex", game_table())
    write("gen_cash.tex", cash_table())
    write("gen_initiation.tex", initiation_table())
    write("gen_cohort.tex", cohort_table())
    print("tables written")


if __name__ == "__main__":
    main()
