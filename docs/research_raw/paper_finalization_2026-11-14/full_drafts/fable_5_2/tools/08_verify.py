"""Check the compiled manuscript against the generated data and the stored fields.

Read-only apart from qa/verification.json and qa/verification_output.txt.
  1. every number the prose states is recomputed from data/*.json and must appear in the source
  2. every quotation used in the source is found in the PDF text and in its stored field
  3. the main text ends on or before page 9, body type is 10 pt, margins are one inch
  4. the LaTeX log has no undefined reference, citation or missing character
  5. the sixteen full first responses appear in the PDF, both channels
"""
import collections
import hashlib
import json
import re
import sys

import pymupdf

from lib import *

fin = read_json("finance_summary.json")
corp = read_json("corpus_summary.json")
barg = read_json("bargaining_summary.json")
tabs = read_json("tables_summary.json")
quotes = read_json("quote_manifest.json")
eps = read_json("episodes.json")
PDF = PKG / "build" / "manuscript.pdf"
LOG = (PKG / "build" / "manuscript.log").read_text(errors="replace")
SRC = {p.name: p.read_text() for p in sorted((PKG / "sections").glob("s*.tex"))}
SRC["appendix.tex"] = (PKG / "sections" / "appendix.tex").read_text()
SRC["manuscript.tex"] = (PKG / "manuscript.tex").read_text()
ALL = "\n".join(SRC.values())
problems, checks = [], []


def check(name, ok, detail=""):
    checks.append(dict(check=name, ok=bool(ok), detail=str(detail)))
    if not ok:
        problems.append(f"{name}: {detail}")


def claim(name, value, pattern):
    """value is recomputed from data; pattern must occur in the manuscript source."""
    found = re.search(pattern, ALL) is not None
    check(f"claim {name} = {value}", found, pattern)


C = collections.Counter
st = tabs["stated_totals"]
con = barg["contrasts"]
# ---- finance claims
claim("episodes", fin["episodes"], r"188 financing episodes")
assert fin["episodes"] == 188 and fin["paid"] == 128 and fin["eliminated"] == 60
claim("paid and eliminated", (fin["paid"], fin["eliminated"]), r"paid 128 and were eliminated in sixty")
assert fin["paid_debt_total"] == 51997 and fin["paid_mortgage_actions"] == 180 and fin["paid_sale_actions"] == 89
claim("payment totals", (51997, 180, 89), r"\\\$51,997 of debt through 180 mortgages and 89 building-sale calls")
assert fin["paid_one_action"] == 67 and fin["paid_multi_action"] == 61 and fin["paid_max_actions"] == 10
claim("action counts", (67, 61), r"Sixty-seven took one action and sixty-one took two to ten")
assert fin["first_action_fallbacks"] == 0 and fin["paid_with_fallback"] == 0
assert fin["payable"] == 131
part = fin["partition"]
assert (part["A"]["episodes"], part["A"]["paid"], part["B"]["episodes"], part["B"]["paid"], part["C"]["episodes"], part["C"]["paid"]) == (62, 62, 53, 52, 16, 14)
claim("partition rows", "62/62, 53/52, 16/14", r"& 62 & 62\\\\\n.*& 53 & 52\\\\\n.*& 16 & 14\\\\")
assert fin["middle_paid_without_released"] == 47 and len(fin["middle_paid_with_released"]) == 5 and len(fin["middle_declared"]) == 1
claim("middle support", "47 + 1 + 5", r"Forty-seven of the 53 were paid with no released mortgage")
cov = fin["coverage"]
assert (cov["no_hotel"], cov["listed_mortgages_suffice"], cov["stock_covers_every_downgrade"], cov["one_hotel_per_group_recyclable_stock"]) == (108, 12, 9, 2)
claim("coverage", "108/12/9/2", r"No hotel is present in 108\. In twelve more.*In nine more")
assert fin["premise_complete_ownership"] == 131 and fin["premise_even"] == 131
assert fin["bound_covers"] == 132 and fin["bound_short"] == 56
assert fin["declare_first_when_covers"] == 3 and fin["declare_first_when_short"] == 50 and fin["short_menus_bankruptcy_only"] == 8
claim("first action table", "132/129/3 and 56/6/50", r"& 132 & 129 & 3\\\\\n.*& 56 & 6 & 50\\\\")
assert len(fin["short_start_financing"]) == 6 and sum("Grok" in x for x in fin["short_start_financing"]) == 5
assert fin["A_holding_buildings"] == 30 and fin["A_mortgage_only_despite_buildings"] == 28
claim("kept every building", "28 of 30", r"held buildings in thirty of them, and in 28 it paid by mortgages alone")
assert fin["B_paid_kept_some_buildings"] == 46 and fin["paid_left_unmortgaged"] == 122
claim("kept some", 46, r"46 kept some buildings")
claim("left a deed unmortgaged", 122, r"122 left a deed unmortgaged")
paid = [e for e in eps if e["outcome"] == "paid"]


def minunit(e):
    v = []
    for a in e["route"]:
        if a["action"] == "mortgage":
            v.append(a["value"])
        elif a["action"] == "sell":
            v += [HOUSE_COST[SPACES[i["space"]]["group"]] // 2 for i in a["items"]]
    return min(v)


n119 = sum(1 for e in paid if e["cash_after"] < minunit(e))
assert n119 == 119
claim("no surplus unit", n119, r"in 119 the cash left over was smaller")
# ---- stated totals and tiers
assert st["n"] == 48 and st["by"]["exact_full_bound"] == 43 and st["by"]["includes_locked"] == 2 and st["by"]["listed_only"] == 3
claim("exact bound on unpayable debts", "43 of 48", r"In 43 of the 48")
assert st["channel"] == {"provider": 13, "note": 30}
claim("channel split", "30 notes, 13 provider", r"Thirty of these figures are in authored notes and thirteen in provider fields")
assert st["locked"] == 21 and st["locked_by"]["exact_full_bound"] == 16
claim("locked collateral population", "37, 32, 5", r"37 first responses face collateral.*Thirty-two count it or raise it\. Five stop")
assert tabs["tiers"] == {"explicit": 5, "ordered": 3, "inclusive": 5, "omission": 2, "tentative": 1}
claim("tiers", "5/3/5/1/2", r"Explicit dependency & 5 &.*\n.*Ordered route & 3 &.*\n.*Inclusive budget & 5 &.*\n.*Tentative resource & 1 &.*\n.*Omission & 2 &")
assert tabs["carried"]["conditional|paid"] == 4 and tabs["carried"]["conditional|bankrupt"] == 2
claim("carried conditional inventories", "4 paid, 2 declared", r"A conditional inventory precedes both declarations and four payments")
# ---- corpus claims
assert (corp["events"], corp["decisions"], corp["attempts"]) == (50918, 6989, 8679)
claim("corpus size", "50,918 / 6,989 / 8,679", r"50,918 events, 6,989 decisions and 8,679 response attempts")
assert corp["wins"] == {"Sol": 8, "Gemini": 7, "Opus": 3, "Grok": 2}
assert corp["first_attempt_refusals"] == {"Opus": 1604} and corp["later_attempt_refusals"] == {"Opus": 1} and corp["refused_recovery_attempts"] == 0
claim("refusals", 1604, r"refused 1,604 of Opus's first attempts")
assert corp["content_action_conflicts"] == {"Grok": 139} and corp["content_names_action"] == {"Grok": 1068}
claim("Grok conflicts", 139, r"In 139 Grok decisions")
assert corp["liquidation_decisions"] == 338 and corp["liquidation_content_names_action"] == {"Grok": 27} and len(corp["liquidation_named_conflicts"]) == 9
claim("financing named-action check", "27 named, 9 differ, 338 decisions", r"Across all 338 financing decisions, Grok's assistant content names an action 27 times and the received call differs in nine")
assert corp["fallback_decisions_by_model"] == {"Opus": 61, "Sol": 4, "Gemini": 1}
assert corp["provider_text_present"] == {"Grok": 1662, "Opus": 1560, "Gemini": 1316, "Sol": 287}
assert tabs["prompts"]["distinct_system_prompts"] == {"standard": 1, "recovery": 1}
assert tabs["wins_by_seat"] == {"1": 7, "2": 7, "3": 3, "4": 3}
assert len(tabs["seeds"]) == 5 and sorted(tabs["commits"].values()) == [4, 16]
# ---- bargaining claims
assert barg["responses"] == 920 and barg["threads_openings"] == 526
assert barg["response_counts"] == {"counter_trade": 394, "reject_trade": 413, "accept_trade": 113}
claim("responses", "113/394/413", r"920 responses to offers: 113 acceptances, 394 counters and 413 rejections")
br = barg["by_recipient"]
assert (br["Sol"]["counter_trade"], br["Sol"]["n"], br["Opus"]["counter_trade"], br["Opus"]["n"]) == (140, 235, 141, 189)
assert (br["Gemini"]["reject_trade"], br["Gemini"]["n"], br["Grok"]["reject_trade"], br["Grok"]["n"]) == (180, 242, 149, 254)
assert sorted(br[m]["accept_trade"] for m in br) == [26, 28, 29, 30]
assert con["all_swaps"]["own"] == [95, 116] and con["all_swaps"]["neither"] == [37, 72] and round(con["all_swaps"]["gap"], 1) == 30.5
assert con["no_grok_authors"]["own"] == [90, 108] and con["no_grok_authors"]["neither"] == [24, 36] and round(con["no_grok_authors"]["gap"], 1) == 16.7
assert (con["no_grok_authors"]["percentile_2_5"], con["no_grok_authors"]["percentile_97_5"]) == (-3.8, 31.9)
claim("swap contrast", "30.5 and 16.7, range -3.8 to 31.9", r"a difference of 30\.5 percentage points.*\n(.*\n)*.*a difference of 16\.7 points.*\$-3\.8\$ to \$31\.9\$")
assert round(con["cash_bids"]["gap"], 1) == -5.0
gaps = [barg["by_recipient_cash_bids"][m]["gap"] for m in ("Sol", "Gemini", "Opus", "Grok")]
assert round(min(gaps), 1) == -0.2 and round(max(gaps), 1) == 8.5
ns = barg["neither_swaps"]
assert (ns["n"], ns["grok_authored"], ns["accepted"], ns["accepted_grok_authored"], ns["accepted_grok_authored_from_conflicting_call"]) == (72, 36, 17, 15, 13)
assert barg["counters_proposer_only_completion_offers"] == [79, 111]
assert barg["recipient_completing_rejections"]["n"] == 74
assert barg["grok_acceptances_naming_other_action"] == [7, 28]

# ---- quotations
doc = pymupdf.open(PDF)
pages = [p.get_text() for p in doc]


def norm(s):
    s = s.replace("\u00ad", "").replace("ﬁ", "fi").replace("ﬂ", "fl").replace("ﬀ", "ff").replace("ﬃ", "ffi").replace("ﬄ", "ffl")
    s = s.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'").replace("−", "-")
    s = re.sub(r"-\n", "", s)
    return re.sub(r"[^A-Za-z0-9$%]+", "", s)


# drop the folio line of each page so that a quotation running over a page break still matches
flat = norm("\n".join(re.sub(r"\n\d+\s*$", "\n", t) for t in pages))
used = set(re.findall(r"\\(?:QB|Q)\{([^}]+)\}", ALL))
by_id = {q["id"]: q for q in quotes}
check("every quotation id used in the source is in the manifest", used <= set(by_id), sorted(used - set(by_id)))
def in_pdf(text):
    """Whole quotation, or every sentence of it when a column or page break with a float splits it."""
    if norm(text) in flat:
        return True
    parts = [x for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]
    return len(parts) > 1 and all(norm(x) in flat for x in parts)


missing = [qid for qid in sorted(used & set(by_id)) if not in_pdf(by_id[qid]["text"])]
check("every used quotation appears in the PDF text", not missing, missing)
bad_src = []
for qid in sorted(used & set(by_id)):
    q = by_id[qid]
    _, rs, _ = load(q["game"])
    r = rs[q["decision"]]
    field = {"note": r["final_action"].get("private_thought") or "", "public": r["final_action"].get("public_message") or "",
             "provider": provider_text(r), "content": r["attempts"][-1].get("assistant_content") or ""}[q["channel"]]
    if q["text"] not in field or text_sha256(field) != q["field_sha256"]:
        bad_src.append(qid)
check("every used quotation is verbatim in its stored field", not bad_src, bad_src)
unused = sorted(set(by_id) - used)

# ---- sixteen full texts
supp = json.loads((PKG / "supplement" / "sixteen_first_texts.json").read_text())
miss16 = []
for row in supp:
    for ch in ("authored_private_note", "provider_reasoning_field"):
        t = row["channels"][ch]["text"]
        # paragraph by paragraph, so that a page break inside a long field does not hide a match
        for para_ in [x for x in t.split("\n\n") if x.strip()]:
            if norm(para_) not in flat:
                miss16.append((row["entry"], ch, para_[:60]))
check("all sixteen first responses are printed in full, both channels", len(supp) == 16 and not miss16, miss16)
n_note = sum(1 for r in supp if r["channels"]["authored_private_note"]["text"])
n_prov = sum(1 for r in supp if r["channels"]["provider_reasoning_field"]["text"])
check("channel availability among the sixteen", (n_note, n_prov) == (11, 16), (n_note, n_prov))

# ---- layout
ref_page = next(i + 1 for i, t in enumerate(pages) if re.search(r"^References\s*$", t, re.M))
concl_page = next(i + 1 for i, t in enumerate(pages) if re.search(r"^\d+\s*\n?Conclusion\s*$", t, re.M) or "Conclusion\n" in t and i < 12)
app_page = next(i + 1 for i, t in enumerate(pages) if "What the corpus supports for each original question" in t)
check("main text ends on or before page 9", concl_page <= 9 and ref_page <= 10, f"conclusion page {concl_page}, references start page {ref_page}")
sizes = collections.Counter()
xs = []
for p in list(doc)[:concl_page]:
    for b in p.get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            for sp in line["spans"]:
                if sp["text"].strip():
                    sizes[(round(sp["size"], 1), sp["font"])] += len(sp["text"])
                    xs.append((sp["bbox"][0], sp["bbox"][2]))
body = sizes.most_common(1)[0]
check("body type is 10 pt Termes", abs(body[0][0] - 10.0) < 0.1 and "Termes" in body[0][1], body)
left, right = min(x[0] for x in xs), max(x[1] for x in xs)
pw = doc[0].rect.width
# one inch is 72 pt; microtype lets punctuation protrude by up to about 2 pt
check("side margins are one inch, allowing punctuation protrusion", left >= 69.5 and pw - right >= 69.5, f"left {left:.1f}pt right {pw - right:.1f}pt")
check("page size is US letter", (round(doc[0].rect.width), round(doc[0].rect.height)) == (612, 792))

# ---- log
check("no undefined references or citations", not re.search(r"undefined|multiply defined", LOG, re.I), re.findall(r".*undefined.*", LOG)[:3])
check("no missing characters", "Missing character" not in LOG, re.findall(r"Missing character.*", LOG)[:3])
over = [float(x) for x in re.findall(r"Overfull \\hbox \(([0-9.]+)pt too wide\)", LOG)]
check("no overfull box wider than 3 pt", all(x <= 3 for x in over), over)

# ---- word count of the main text
def prose_words(tex):
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    tex = re.sub(r"\\begin\{(table|figure)\*?\}.*?\\end\{\1\*?\}", " ", tex, flags=re.S)
    q = sum(len(by_id[m].split() if False else by_id[m]["text"].split()) for m in re.findall(r"\\(?:QB|Q)\{([^}]+)\}", tex))
    tex = re.sub(r"\\(QB|Q)\{[^}]+\}", " ", tex)
    tex = re.sub(r"\\(cite|ref|label|path|url|input|rows)\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?", " ", tex)
    tex = re.sub(r"[{}$~\\]", " ", tex)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9,.'’\-]*", tex)), q


main_w = sum(prose_words(SRC[k])[0] for k in SRC if k.startswith("s"))
quote_w = sum(prose_words(SRC[k])[1] for k in SRC if k.startswith("s"))
abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", SRC["manuscript.tex"], re.S).group(1)
abs_w = prose_words(abstract)[0]
check("authored main prose is within 4,500 to 5,500 words", 4500 <= main_w <= 5500, main_w)

result = dict(
    pdf=str(PDF.relative_to(PKG)), pdf_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(), pages=len(doc),
    conclusion_page=concl_page, references_start_page=ref_page, appendix_start_page=app_page,
    main_authored_prose_words=main_w, main_quoted_words=quote_w, abstract_words=abs_w,
    quotations_in_manifest=len(by_id), quotations_used=len(used), quotations_unused=unused,
    body_font=dict(size=body[0][0], font=body[0][1]), overfull_boxes_pt=over,
    checks=checks, problems=problems,
)
(PKG / "qa" / "verification.json").write_text(json.dumps(result, indent=1) + "\n")
lines = [f"{'ok ' if c['ok'] else 'FAIL'} {c['check']}" + ("" if c["ok"] else f"  <- {c['detail']}") for c in checks]
summary = (f"pages {len(doc)} | conclusion on page {concl_page} | references start page {ref_page} | appendix starts page {app_page}\n"
           f"main authored prose {main_w} words | quoted model text in main {quote_w} words | abstract {abs_w} words\n"
           f"quotations used {len(used)} of {len(by_id)} | checks {len(checks)} | problems {len(problems)}")
(PKG / "qa" / "verification_output.txt").write_text("\n".join(lines) + "\n" + summary + "\n")
print("\n".join(l for l in lines if l.startswith("FAIL")))
print(summary)
sys.exit(1 if problems else 0)
