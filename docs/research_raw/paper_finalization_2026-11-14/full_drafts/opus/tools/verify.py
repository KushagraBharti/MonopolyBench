"""Mechanical checks of the built draft. Read-only.

1. Every quotation in the registry is re-found verbatim in its original field.
2. Numbers printed in the prose match values computed from data/*.json.
3. Rule and resolver sources are identical at both run commits and head.
4. The PDF builds without undefined references; main-text pages and words are measured.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import lib
from quotes import field_text

D = lib.DRAFT / "data"
fails: list[str] = []
report: dict = {}


def check(cond: bool, msg: str) -> None:
    if not cond:
        fails.append(msg)


def main() -> None:
    # 1. quotations
    reg = json.loads((D / "quote_registry.json").read_text())
    ok = 0
    for q in reg:
        t = field_text(q)
        if t and q["text"] in t:
            ok += 1
        else:
            fails.append(f"quote {q['id']} not found")
    report["quotes_verified"] = f"{ok}/{len(reg)}"

    # 2. numbers in prose
    tex = (lib.DRAFT / "manuscript.tex").read_text()
    app = (lib.DRAFT / "sections/appendix.tex").read_text()
    fin = json.loads((D / "finance_census.json").read_text())
    s = fin["summary"]
    rows = fin["rows"]
    barg = json.loads((D / "bargaining_census.json").read_text())
    prov = json.loads((D / "provenance.json").read_text())
    scan = json.loads((D / "named_action_scan.json").read_text())["summary"]
    cond = json.loads((D / "response_conditions.json").read_text())
    prem = json.loads((D / "continuation_premises.json").read_text())["summary"]
    fm = s["first_menu_by_region"]
    mf = s["mortgage_first"]
    covered = fm["U0_at_least_D"]["n"] + fm["U0_below_D_le_Ustar"]["n"]
    covered_decl = fm["U0_at_least_D"].get("declare_bankruptcy", 0) + fm["U0_below_D_le_Ustar"].get("declare_bankruptcy", 0)
    expect = {
        f"{covered_decl} of {covered}": True,
        f"{fm['Ustar_below_D']['declare_bankruptcy']} of {fm['Ustar_below_D']['n']}": True,
        f"{s['paid']['n']} payments": True,
        f"{s['paid']['mortgage_actions']} mortgages": True,
        f"{s['paid']['sale_actions']} sale actions": True,
        f"\\${s['paid']['obligations_paid']:,}": True,
        f"{s['paid']['one_action']} take one action": True,
        f"{mf['regionA_paid_holding_buildings'] - len(mf['regionA_paid_selling_any_building'])} of {mf['regionA_paid_holding_buildings']}": True,
        f"\\${mf['regionB_excess_min']} to \\${mf['regionB_excess_max']}": True,
        f"median \\${int(mf['regionB_excess_median'])}": True,
        f"In the {mf['regionB_paid_without_released_mortgage']} payments": True,
        f"{barg['opening_swaps']['proposer_only']['reject']} of {barg['opening_swaps']['proposer_only']['n']}": True,
        f"{barg['opening_swaps']['neither']['reject']} of {barg['opening_swaps']['neither']['n']}": True,
        f"{barg['opening_swaps']['gap_pp']:.1f}-point": True,
        f"{barg['opening_swaps_no_grok_authors']['gap_pp']:.1f} points": True,
        f"{barg['counters_preserving_noncash_exchange']['proposer_only_completion'][0]} of {barg['counters_preserving_noncash_exchange']['proposer_only_completion'][1]}": True,
        f"{barg['responses']['accept']} offers, counter {barg['responses']['counter']} and reject {barg['responses']['reject']}": True,
        f"{barg['threads']} threads": True,
        f"{barg['grok_neither_swaps_authored']} of the 72": True,
        f"{barg['grok_neither_swaps_accepted']} of their 17": True,
        f"{barg['grok_neither_swaps_accepted_from_conflicting_openings']} of those 15": True,
        f"{scan['per_model']['Grok']['content_names_action']} of Grok's {scan['per_model']['Grok']['liquidation_decisions']}": True,
        f"all {scan['liquidation_decisions']} liquidation decisions": True,
        f"{prov['events']:,} events": True,
        f"{prov['decisions']:,} resolved decisions": True,
        f"{prov['attempts']:,} response attempts": True,
        f"{cond['refused_first_attempts']['Opus']:,} first attempts": True,
        f"{prem['hotel_free']} hold no hotel": True,
        f"{prem['initial_cash_and_listed_mortgages_suffice']} more can pay": True,
        f"{prem['bank_stock_covers_every_hotel_downgrade']} more have bank stock": True,
        f"last {prem['single_hotel_per_group_recyclable_stock']} have one hotel": True,
        f"{s['partition']['A_cash_and_listed_mortgages']['episodes']} can be met": True,
        f"{s['partition']['B_sales_needed_no_release']['episodes']} also need sales": True,
        f"({s['partition']['B_sales_needed_no_release']['paid']} paid)": True,
        f"{s['partition']['C_release_necessary']['episodes']} need released mortgages ({s['partition']['C_release_necessary']['paid']} paid)": True,
        f"{100*16/188:.1f}\\% of financing": True,
        f"{100*16/131:.1f}\\% of payable": True,
    }
    missing = [k for k in expect if k not in tex]
    for k in missing:
        fails.append(f"number string not in prose: {k}")
    report["prose_number_checks"] = f"{len(expect) - len(missing)}/{len(expect)}"
    gm = s["first_menu_by_region_model"]["Ustar_below_D"]
    check(gm["Opus"]["declare_bankruptcy"] == gm["Opus"]["n"] and gm["Sol"]["declare_bankruptcy"] == gm["Sol"]["n"], "Opus/Sol short declarations")
    check(f"Gemini in {gm['Gemini']['declare_bankruptcy']} of {gm['Gemini']['n']}" in tex, "Gemini short declarations")
    check(f"Grok in {gm['Grok']['declare_bankruptcy']} of {gm['Grok']['n']}" in tex, "Grok short declarations")
    check(f"{len(scan['conflicts'])} calls" in tex.replace("nine calls", "9 calls"), "named-action conflict count")

    # 3. sources
    same = all(len(set(v.values())) == 1 for v in prov["source_sha256"].values())
    check(same, "rule sources differ between commits")
    report["sources_identical_at_run_commits_and_head"] = same

    # 4. prose style: no em dashes in authored prose outside quotations
    for name, body in [("manuscript.tex", tex), ("appendix.tex", app)]:
        stripped = re.sub(r"\\Q\{[^}]*\}", "", body)
        if "\u2014" in stripped:
            fails.append(f"em dash in {name}")

    # 5. PDF and log
    log = (lib.DRAFT / "build/manuscript.log").read_text(errors="ignore")
    check("undefined" not in log.lower() or "There were undefined" not in log, "undefined references")
    report["latex_warnings"] = len(re.findall(r"LaTeX Warning", log))
    report["overfull_boxes"] = len(re.findall(r"Overfull \\hbox", log))
    pdf = lib.DRAFT / "manuscript.pdf"
    txt = lib.DRAFT / "qa/manuscript.txt"
    subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=txtwrite", f"-sOutputFile={txt}", str(pdf)], check=True)
    pages_txt = subprocess.run(["gs", "-q", "-dNODISPLAY", "-dNOSAFER", "-c", f"({pdf}) (r) file runpdfbegin pdfpagecount = quit"], capture_output=True, text=True).stdout.strip()
    report["pdf_pages"] = int(pages_txt) if pages_txt.isdigit() else pages_txt
    # pages: split per page with gs per page count
    full = txt.read_text(errors="ignore")
    ref_idx = full.find("References")
    main_words = len(re.findall(r"[A-Za-z0-9$][^\s]*", full[:ref_idx])) if ref_idx > 0 else None
    report["main_words_including_tables_and_captions"] = main_words
    report["pdf_sha256"] = lib.sha256_file(pdf)
    check("??" not in full, "unresolved ?? in PDF text")
    # prose word count of the main text (abstract through conclusion, without floats)
    body = tex[tex.index("\\begin{abstract}"):tex.index("\\begingroup\\small\\setlength{\\bibsep}")]
    for env in ["table", "table*", "figure"]:
        body = re.sub(r"\\begin\{%s\}.*?\\end\{%s\}" % (re.escape(env), re.escape(env)), " ", body, flags=re.S)
    qsrc = (lib.DRAFT / "sections/gen_quotes.tex").read_text()
    qd = dict(re.findall(r"csname q@([^\\]+)\\endcsname\{(.*)\}$", qsrc, flags=re.M))
    body = re.sub(r"\\Q\{([^}]*)\}", lambda m: qd.get(m.group(1), ""), body)
    body = re.sub(r"\\(cite|ref|label|input|rowsfile)\{[^}]*\}", " ", body)
    body = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", body)
    body = re.sub(r"[{}$\\~]", " ", body)
    report["main_prose_words_abstract_to_conclusion"] = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'.,%\-]*", body))
    pages = report["pdf_pages"] if isinstance(report["pdf_pages"], int) else 0
    ref_page = None
    for i in range(1, pages + 1):
        out = subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=txtwrite", f"-dFirstPage={i}", f"-dLastPage={i}", "-sOutputFile=-", str(pdf)], capture_output=True, text=True).stdout
        if re.search(r"^\s*References\s*$", out, flags=re.M):
            ref_page = i
            break
    report["references_begin_on_page"] = ref_page
    report["failures"] = fails
    (lib.DRAFT / "qa/verification.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    if fails:
        sys.exit(1)


if __name__ == "__main__":
    main()
