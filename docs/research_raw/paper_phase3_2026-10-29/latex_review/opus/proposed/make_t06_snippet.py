"""Opus proposal: native longtable for T6 (all 60 eliminations), pdflatex/lualatex portable.

Usage: python3 -I make_t06_snippet.py <t06_eliminations.csv> <out.tex>
Values are copied from the CSV; the only derived cells are the liquidation-route counts
(houses sold, hotels sold, mortgages) parsed from the CSV `steps` list. The full ordered
sequence stays in the CSV/JSON. Requires booktabs and longtable in the host preamble.
"""
import ast
import csv
import hashlib
import sys

src, out = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(open(src, newline="")))
assert len(rows) == 60
sha = hashlib.sha256(open(src, "rb").read()).hexdigest()


def money(v: str) -> str:
    return f"{int(v):,}"


def route(steps: str) -> str:
    s = ast.literal_eval(steps)
    h = sum(x.startswith("sell house") for x in s)
    t = sum(x.startswith("sell hotel") for x in s)
    m = sum(x.startswith("mortgage") for x in s)
    assert h + t + m == len(s)
    return f"{h}/{t}/{m}"


lines = [
    f"% T6 native table proposed by Opus. Source: astra/exhibits/t06_eliminations.csv sha256 {sha}",
    "% Regenerate with latex_review/opus/proposed/make_t06_snippet.py; do not hand-edit values.",
    r"{\footnotesize\setlength{\tabcolsep}{3.2pt}",
    r"\begin{longtable}{@{}rllllrrrrrrcc@{}}",
    r"\caption[All 60 eliminations: current debt and own-action finance]{All 60 eliminations: current debt and the debtor's own legal finance at the elimination decision. Money columns are game dollars; bank houses is a count.}\label{tab:t06-eliminations}\\",
    r"\toprule",
    r"G & Decision & Agent & Seat & Kind & Owed & Cash & Menu & Access. & Full & Bank & Pays & Route \\",
    r"  &          &       &      &      &      &      & mort. & own seq. & bound & houses & debt & H/T/M \\",
    r"\midrule\endfirsthead",
    r"\multicolumn{13}{@{}l}{\emph{T6 continued}}\\ \toprule",
    r"G & Decision & Agent & Seat & Kind & Owed & Cash & Menu & Access. & Full & Bank & Pays & Route \\",
    r"\midrule\endhead",
    r"\midrule\multicolumn{13}{r@{}}{\emph{continued on next page}}\\ \endfoot",
    r"\bottomrule\endlastfoot",
]
for r in rows:
    lines.append(" & ".join([
        r["game"], r["decision"], r["model"], r["player"],
        "decl." if r["elimination"] == "declared" else "auto.",
        money(r["owed"]), money(r["cash"]), money(r["menu_mortgage_only"]),
        money(r["accessible"]), money(r["full"]), r["bank_houses"],
        "Yes" if r["avoidable"] == "True" else "No",
        route(r["steps"]),
    ]) + r" \\")
lines += [r"\end{longtable}}", ""]
notes = r"""\noindent{\footnotesize\textit{Notes.} One row per applied elimination: 56 declared
bankruptcies and four automatic eliminations after a final mortgage. Owed is the current debt. Cash is
cash on hand. Menu mort.\ adds the mortgage value of deeds mortgageable on the first menu screen, with no
building sale. Access.\ own seq.\ adds the greedy own-action liquidation: sell houses, downgrade a hotel
only while the bank holds at least four houses, then mortgage unlocked deeds, repeated. Full bound adds
half the building cost per level and every unmortgaged mortgage value, ignoring the bank-house
constraint. For automatic rows, all bounds are computed at the triggering decision state, before its
action. Bank houses is the bank's house stock at that state. Pays debt reproduces the source field
\texttt{avoidable}: \emph{Yes} means an engine-verified own-action sequence can pay the current debt. It
does not assert later survival, a rational alternative or a changed winner, and it assumes no help from
another player. Route H/T/M counts houses sold, hotels sold and mortgages in the greedy sequence; the
ordered sequence is in the source CSV and JSON. In G7 the hotel-sale rule binds: \$440 accessible against
\$1,310 nominal under a \$750 debt.\par}
"""
open(out, "w", encoding="utf-8").write("\n".join(lines) + notes)
print(out, len(rows), "rows")
