"""Count scope-limiting sentences in the integrated manuscript source (document-only).

Usage: python3 -I count_hedges.py <integrated_dir> <out_json>
"""
import json
import re
import sys
from pathlib import Path

root, out_path = Path(sys.argv[1]), Path(sys.argv[2])
MAIN = ["introduction", "setup", "methods", "bargaining", "development", "finance_inheritance",
        "temporal_discussion", "related_limits"]
ABSTRACT = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", (root / "manuscript.tex").read_text(), re.S).group(1)
# A sentence counts as a scope limiter when it denies an inference rather than reporting a negative fact.
LIMIT = re.compile(
    r"\b(does not|do not|did not|cannot|can not|is not|are not|not (an?|the|evidence|proof|proposed|claimed|used|"
    r"establish|identify|estimate|necessarily|treat|a )|neither|nor |without (establishing|assigning|treating|being|making)|"
    r"rather than|no (causal|optimal|independent)|not\b.{0,40}\b(establish|identif|evidence|proof|measure|estimate|rank))",
    re.I)
STRONG = re.compile(r"\b(does not|do not|cannot) (establish|identify|estimate|show|isolate|supply|settle|remove|evaluate|"
                    r"license|validate|rank)|\bnot (evidence|proof|an? (identified|measure|estimate|matched|causal))|"
                    r"\bis not (a|an) |\bare not ", re.I)


def clean(tex):
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    tex = re.sub(r"\\begin\{(table|figure|longtable)\}.*?\\end\{\1\}", " ", tex, flags=re.S)
    tex = re.sub(r"\\begin\{tabularx?\}.*?\\end\{tabularx?\}", " ", tex, flags=re.S)
    tex = re.sub(r"\\Transcript(Quote|Source)\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\(cite|label|ref|input)[a-z]*(\[[^\]]*\])*\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", tex)
    tex = re.sub(r"[{}~]", " ", tex)
    return re.sub(r"\s+", " ", tex)


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", text) if len(s.split()) >= 4]


rows, tot_s, tot_l, tot_strong, tot_w = [], 0, 0, 0, 0
paragraph_final = 0
paragraphs = 0
for name in ["abstract"] + MAIN:
    raw = ABSTRACT if name == "abstract" else (root / "sections" / f"{name}.tex").read_text()
    sents = sentences(clean(raw))
    lim = [s for s in sents if LIMIT.search(s)]
    strong = [s for s in sents if STRONG.search(s)]
    paras = [p for p in re.split(r"\n\s*\n", raw) if len(clean(p).split()) > 25 and "\\begin{t" not in p]
    pf = 0
    for p in paras:
        ps = sentences(clean(p))
        if ps and LIMIT.search(ps[-1]):
            pf += 1
    paragraphs += len(paras)
    paragraph_final += pf
    rows.append({"section": name, "sentences": len(sents), "scope_limiters": len(lim), "strong_disclaimers": len(strong),
                 "paragraphs": len(paras), "paragraphs_ending_in_limiter": pf,
                 "words": sum(len(s.split()) for s in sents), "limiter_words": sum(len(s.split()) for s in lim)})
    tot_s += len(sents)
    tot_l += len(lim)
    tot_strong += len(strong)
    tot_w += sum(len(s.split()) for s in sents)
full = clean("".join((root / "sections" / f"{n}.tex").read_text() for n in MAIN) + ABSTRACT)
phrases = ["does not establish", "do not establish", "not evidence", "does not identify", "do not identify",
           "not a matched", "rather than", "does not show", "not an identified", "not proof", "cannot", "neither",
           "not establish", "is not a ", "are not "]
out = {"rows": rows, "total_sentences": tot_s, "total_scope_limiters": tot_l, "total_strong": tot_strong,
       "paragraphs": paragraphs, "paragraphs_ending_in_limiter": paragraph_final,
       "phrase_counts": {p: len(re.findall(re.escape(p), full, re.I)) for p in phrases}}
out_path.write_text(json.dumps(out, indent=1) + "\n")
for r in rows:
    print(f"{r['section']:22s} sent {r['sentences']:3d}  limiters {r['scope_limiters']:3d} ({r['scope_limiters']/max(1,r['sentences']):.0%})"
          f"  strong {r['strong_disclaimers']:3d}  paras {r['paragraphs']:2d} ending-in-limiter {r['paragraphs_ending_in_limiter']:2d}")
print("TOTAL", tot_s, tot_l, f"{tot_l/tot_s:.0%}", "strong", tot_strong, "paras", paragraphs, "ending", paragraph_final)
print(out["phrase_counts"])
