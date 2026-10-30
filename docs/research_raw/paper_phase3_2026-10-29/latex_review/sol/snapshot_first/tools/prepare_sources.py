"""One-time prose import and reproducible data-table preparation.

Editable outline/figure prose is created only if absent. --refresh-tables
regenerates native table snippets from the frozen data, never the edited prose.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parents[1]
BASE = HERE.parent
ROOT = BASE.parents[2]
MANIFEST = {}
MD = MarkdownIt()
ESC = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "τ": r"\ensuremath{\tau}", "≥": r"\ensuremath{\geq}", "≤": r"\ensuremath{\leq}", "×": r"\ensuremath{\times}", "→": r"\ensuremath{\rightarrow}", "≠": r"\ensuremath{\neq}", "–": "--", "—": "---", "’": "'", "“": "``", "”": "''"}


def tex(value):
    return "".join(ESC.get(c, c) for c in str(value))


def track(path):
    MANIFEST[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path


def inline(tokens):
    result = []
    for t in tokens or []:
        if t.type == "text": result.append(tex(t.content))
        elif t.type in {"softbreak", "hardbreak"}: result.append("\n")
        elif t.type == "strong_open": result.append(r"\textbf{")
        elif t.type == "em_open": result.append(r"\emph{")
        elif t.type in {"strong_close", "em_close", "link_close"}: result.append("}")
        elif t.type == "code_inline": result.append(r"\texttt{" + tex(t.content) + "}")
        elif t.type == "link_open":
            href = t.attrGet("href")
            if not re.match(r"\w+://", href):
                href = "run:../" + href
            result.append(r"\href{" + href.replace("%", r"\%") + "}{")
        else: raise ValueError(t.type)
    return "".join(result)


def prose(source, outline=False):
    tokens = MD.parse(source)
    parts = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.type == "heading_open":
            content = tokens[i + 1]
            level = int(t.tag[1])
            if level == 1:
                i += 3
                continue
            title = content.content
            numbered = bool(re.match(r"^\d+(?:\.\d+)*[. ]", title))
            title = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", title)
            command = "section" if level == 2 else "subsection"
            star = "" if outline and numbered else "*"
            parts.append(f"\\{command}{star}{{{tex(title)}}}\n")
            if star: parts.append(f"\\addcontentsline{{toc}}{{{command}}}{{{tex(title)}}}\n")
            i += 3
            continue
        if t.type == "inline": parts.append(inline(t.children))
        elif t.type == "paragraph_open": pass
        elif t.type == "paragraph_close": parts.append("\n\n")
        elif t.type == "bullet_list_open": parts.append("\\begin{itemize}\n")
        elif t.type == "bullet_list_close": parts.append("\\end{itemize}\n")
        elif t.type == "ordered_list_open": parts.append("\\begin{enumerate}\n")
        elif t.type == "ordered_list_close": parts.append("\\end{enumerate}\n")
        elif t.type == "list_item_open": parts.append("\\item ")
        elif t.type == "list_item_close": parts.append("\n")
        else: raise ValueError(t.type)
        i += 1
    return "".join(parts)


def write(path, text, overwrite=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if overwrite or not path.exists(): path.write_text(text)


def load(stem):
    path = BASE / "astra/exhibits" / (stem + ".json")
    data = json.loads(track(path).read_text())
    for ext in ("json", "csv"):
        p = track(path.with_suffix("." + ext))
        shutil.copy2(p, HERE / "data" / p.name)
    return data


def table(stem, caption, heads, aligns, rows, notes, overwrite):
    n = len(heads)
    header = " & ".join(r"\textbf{" + tex(h) + "}" for h in heads) + r" \\"
    out = ["% Generated from frozen data; edit generator for data-column changes.\n",
           r"\begingroup\small\setlength{\tabcolsep}{4pt}\renewcommand{\arraystretch}{1.12}" + "\n",
           r"\begin{longtable}{" + aligns + "}\n",
           r"\caption{" + tex(caption) + "}\\label{tab:" + stem + r"}\\" + "\n",
           r"\toprule" + "\n" + header + "\n\\midrule\n\\endfirsthead\n",
           r"\multicolumn{" + str(n) + r"}{l}{\tablename\ \thetable\ continued}\\" + "\n\\toprule\n" + header + "\n\\midrule\n\\endhead\n",
           r"\midrule\multicolumn{" + str(n) + r"}{r}{Continued on next page}\\" + "\n\\endfoot\n\\bottomrule\n\\endlastfoot\n"]
    for row in rows:
        assert len(row) == n
        out.append(" & ".join(tex(v) for v in row) + r" \\" + "\n")
    out += ["\\end{longtable}\n\\endgroup\n", r"\tablenote{" + tex(notes) + "}\n", r"\sourcepath{data/" + stem + ".json}\n"]
    write(HERE / "tables" / (stem + ".tex"), "".join(out), overwrite)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-tables", action="store_true")
    args = parser.parse_args()
    for name in ("data", "assets", "figures", "tables", "source_snapshots"):
        (HERE / name).mkdir(exist_ok=True)
    for name in ("paper_outline.md", "figures_and_tables.md", "astra/exhibit_captions.md"):
        src = track(BASE / name)
        shutil.copy2(src, HERE / "source_snapshots" / src.name)
    outline = (BASE / "paper_outline.md").read_text()
    outline = outline.replace("Successful retry may change quantity:", "Successful retry may change the purchase multiset (within-decision allocation):")
    body = prose(outline, outline=True)
    body = body.replace("Successful retry may change the purchase multiset (within-decision allocation):", r"Successful retry may change the purchase multiset (within-decision allocation)\footnote{Conversion correction, 29 October 2026: the Markdown said ``change quantity.'' T7 measures a changed purchase multiset, from the audit field \texttt{allocation\_changing\_within\_decision}; a quantity delta is not implied.}:")
    write(HERE / "outline_body.tex", "% Editable LaTeX; imported once from the source snapshot.\n" + body)
    captions = (BASE / "astra/exhibit_captions.md").read_text()
    blocks = re.split(r"(?m)^## F(\d+) [—–-] (.+)\n", captions)
    figures = []
    stems = sorted((BASE / "astra/exhibits").glob("f*.pdf"))
    assert len(stems) == 9
    for i in range(1, len(blocks), 3):
        num, title, raw = int(blocks[i]), blocks[i + 1], blocks[i + 2]
        raw = raw.split("## Figure selection")[0].strip()
        # These notes were placed at the end of the relevant source section.
        links = re.match(r"^(?:\[[^]]+\]\([^)]+\)[,.]?\s*)+", raw)
        if links: raw = raw[links.end():]
        source = stems[num - 1]
        shutil.copy2(track(source), HERE / "assets" / source.name)
        label = source.stem
        caption = prose(raw).strip()
        snippet = ("\\begin{figure}[p]\n\\centering\n" +
                   r"\includegraphics[width=\linewidth,height=" + ("4.4in" if num in {1,3,4,5,7,9} else "0.57\\textheight") + r",keepaspectratio]{" + source.name + "}\n" +
                   r"\caption[" + tex(title) + "]{" + caption + "}\n\\label{fig:" + label + "}\n\\end{figure}\n")
        write(HERE / "figures" / (label + ".tex"), snippet)
        landscape = num in {1,3,4,5,7,9}
        figures.append("\\clearpage\n" + ("\\begin{landscape}\n" if landscape else "") + "\\input{figures/" + label + "}\n\\clearpage\n" + ("\\end{landscape}\n" if landscape else ""))
    write(HERE / "figure_inputs.tex", "".join(figures))

    t1=load("t01_cohort"); fps=list(dict.fromkeys(r["treatment_fingerprint"] for r in t1))
    table("t01_cohort", "Outcomes across seed blocks and rotations", ["Game","Seed","Rotation","Winner","Seat","Turns","Fingerprint"], "r r r l r r l", [[r[k] for k in ("game","seed","rotation","winner","winner_seat","turns")]+[r["treatment_fingerprint"][:8]] for r in t1], "Seats and rotations are one-based. Fingerprints abbreviate source versions, not a causal treatment effect. Full values are printed below.", args.refresh_tables)
    with (HERE/"tables/t01_cohort.tex").open("a") as f:
        for fp in fps: f.write("\\par{\\footnotesize\\path{"+fp+"}}\n")
    t2=load("t02_negotiation")
    table("t02_negotiation", "Initiation propensity, intensity and decision granularity", ["Agent","Proposals","Proposing / eligible turns","Propensity %","Proposals / proposing turn","Eligible decisions","Decision rate %","Decisions / turn","Zero-proposal games"], "l r L{1.05in} r L{0.9in} r r r r", [[r['configuration'],r['proposals'],f"{r['proposing_turns']}/{r['eligible_turns']}",f"{100*r['own_turn_propensity']:.2f}",f"{r['proposals']}/{r['proposing_turns']} = {r['proposals_per_proposing_turn']:.2f}",r['eligible_decisions'],f"{100*r['eligible_decision_rate']:.2f}",f"{r['eligible_decisions_per_turn']:.2f}",r['zero_proposal_games']] for r in t2], "Propensity and eligible-decision frequency are percentages; intensity and decisions per turn are ratios. Display uses half-even rounding: 18/16 = 1.125 is shown as 1.12. Exact fractions and JSON floats remain in the data. Opus has action-only refusal recovery; Grok has required tool choice. Eligibility is endogenous.",args.refresh_tables)
    t3=load("t03_trade_groups")
    table("t03_trade_groups","Trade-completed groups and first actual management window",["Agent","All groups","Built in window","Entry legal","Entry legal, built","Legal during window","No access"],"l r r r r r r",[[r[k] for k in ('configuration','trade_groups','first_management_built','entry_eligible','entry_eligible_built','eligible_during_window','without_access')] for r in t3],"Group episodes, not trades. The entry-conditioned population has 42 groups; 34 are built. All-window totals are 63 groups and 43 builds; 54 become legal during the window. These are applied outcomes, not willingness.",args.refresh_tables)
    t4=load('t04_bilateral_completion')
    table('t04_bilateral_completion','Color-group completion on each side of accepted trades',['Sides completing a group','Trades'],'l r',[[{0:'Neither side',1:'One side',2:'Both sides'}[r['newly_completed_sides']],r['trades']] for r in t4],'113 accepted trades. Completion is not bilateral welfare or an optimal-value score.',args.refresh_tables)
    t5=load('t05_spending_units')
    group={'BROWN':'BR','LIGHT_BLUE':'LB','PINK':'PK','ORANGE':'OR','RED':'RD','YELLOW':'YL','GREEN':'GR','DARK_BLUE':'DB'}
    table('t05_spending_units','All 103 construction-spending units',['Game','Seat / agent','Group','Win','Outlay','Sales','Paid rent after own spend','Whole-game paid rent','Inherited','Creditor eliminations','First spend event'],"r l l l r r r r l r r",[[r['game'],r['player']+' '+r['configuration'],group[r['group']],'Y' if r['winner'] else 'N',r['spend'],r['sale_proceeds'],r['paid_developed_rent_after_first_own_spend'],r['paid_developed_rent_whole_game'],'Y' if r['inherited_deed_at_first_own_spend'] else 'N',r['creditor_eliminations_on_group'],r['first_own_spend_event']] for r in t5],"All monetary columns are game dollars. Unit: game/player/color with own house or hotel spending. BR=brown; LB=light blue; PK=pink; OR=orange; RD=red; YL=yellow; GR=green; DB=dark blue. Inherited means at least one inherited deed at first own spend. Receipts are paid developed rent, not ROI. Y/N denote yes/no. Totals: outlay103450, whole-game receipts93000, post-own-spend receipts92550.",args.refresh_tables)
    t6=load('t06_eliminations')
    table('t06_eliminations','Current-debt finance at all 60 eliminations',['Game','Decision','Seat / agent','Kind','Debt','Cash','Menu mortgage','Accessible','Full bound','Bank houses','Pays current debt'],"r l l l r r r r r r l",[[r['game'],r['decision'].replace('dec-000','d'),r['player']+' '+r['model'],'Auto' if r['elimination']=='automatic' else 'Decl.',r['owed'],r['cash'],r['menu_mortgage_only'],r['accessible'],r['full'],r['bank_houses'],'Yes' if r['avoidable'] else 'No'] for r in t6],"Game dollars. Menu mortgage = current cash plus first-screen mortgageable collateral. Accessible = own legal liquidation honoring stock and phase; full = building-sale proceeds plus unlocked mortgage values and cash, ignoring stock restrictions. Auto rows use the triggering decision state. Pays current debt is the source avoidable flag, not future survival or rationality. Full legal steps, applied actions and elimination event IDs remain in the paired JSON. G7 is the only accessible/full gap.",args.refresh_tables)
    t7=load('t07_build_recovery')
    table('t07_build_recovery','Outcomes of all decisions with an uneven-intermediate-build rejection',['Agent','Rejections','Some legal build','Same multiset','Changed multiset','Default'],"l r r r r r",[[r[k] for k in ('configuration','uneven_rejection_decisions','some_legal_build_same_decision','same_purchase_multiset','changed_purchase_multiset','ended_in_default')] for r in t7],"Recovery means some legal build within the same decision. A changed purchase multiset does not necessarily mean changed total quantity. Eventual same-turn attainment and altered future play are separate. All61 Opus defaulted purchase multisets execute after reordering, without imputing new outcomes.",args.refresh_tables)
    t8=load('t08_cash_trajectories')
    table('t08_cash_trajectories','All 631 cash observations for G14, G15 and G19, in source order',['Game','Event','Turn','Seat','Agent','Cash after event','Reason'],"r r r l l r L{2.2in}",[[r[k] for k in ('game','event_seq','turn','player','configuration','cash','reason')] for r in t8],"Game dollars. Cash is a balance after the event, not the change in balance or liquidatable wealth. Initial1500 balances used in F9 are not extra rows here. Preserve source order within a turn. Reasons are canonical event codes.",args.refresh_tables)
    t9=load('t09_entry_nonbuild_records')
    cats={'engine_default':'Engine default','received_content_tool_conflict':'Received conflict','consistent_end_with_stated_reserve':'Stated hold'}
    table('t09_entry_nonbuild_records','All eight entry-buildable groups not built in their first window',['Game','Agent','Group','Decision','Turn','Record class','Content action','Attempt','Source line'],"r l l l r L{1.0in} L{1.5in} l r",[[r['game'],r['model'],group[r['group']],'d'+str(int(r['decision_id'].split('-dec-')[-1])),r['turn'],cats[r['category']],r['selected_content_name'] if r['selected_content_name'] is not None else 'Absent',r['selected_attempt_index'] if r['selected_attempt_index'] is not None else 'Absent',r['line']] for r in t9],"All applied actions are end_turn. Absent means no selected valid attempt/content; it is not attempt0. Game plus short decision uniquely identifies the retained record. Full IDs, original file paths, source lines and attempt outcomes are in the paired JSON. Three defaults, three conflicts, two stated holds. No executable lost-build or intent attribution.",args.refresh_tables)
    inputs=[]
    for p in sorted((HERE/'tables').glob('t0*.tex')):
        stem=p.stem; wide=stem[:3] in {'t02','t05','t06','t09'}
        inputs.append('\\clearpage\n'+('\\begin{landscape}\n' if wide else '')+'\\input{tables/'+stem+'}\n\\clearpage\n'+('\\end{landscape}\n' if wide else ''))
    write(HERE/'table_inputs.tex',''.join(inputs))
    write(HERE/'peer_inputs.tex',"The peer exhibit index is being assembled.\n")
    selection=captions.split('## Figure selection\n')[1]
    write(HERE/'selection_notes.tex',prose(selection))
    (HERE/'source_manifest.json').write_text(json.dumps({'sources':MANIFEST,'scope':'One-time prose conversion; native table generation from frozen JSON; original sources retained. No literature review conversion.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
    print('Prepared full outline, nine figures and nine native tables (837 records).')


if __name__=='__main__': main()
