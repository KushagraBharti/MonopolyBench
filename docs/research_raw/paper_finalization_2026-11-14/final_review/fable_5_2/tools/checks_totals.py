"""Existing-record arithmetic on the shipped numeric-presence table (read-only).
Splits the 48 unpayable first responses with a financing option by whether buildings lock
further mortgages (listed total < full bound), and prints every match context in that subset."""
import json, collections, re
from lib import *
C = collections.Counter
d = json.loads((INT / "data/stated_totals_check.json").read_text())
eps = {(e["game"], e["first"]): e for e in json.loads((OUT / "episodes_188.json").read_text())}
rows = [r for r in d["rows"] if not r["forced_menu"]]
res = {"n": len(rows), "match": sum(r["has_match"] for r in rows)}
locked = [r for r in rows if r["listed_total"] < r["full_bound"]]
unlocked = [r for r in rows if r["listed_total"] == r["full_bound"]]
res["unlocked"] = {"n": len(unlocked), "match": sum(r["has_match"] for r in unlocked)}
res["locked"] = {"n": len(locked), "match": sum(r["has_match"] for r in locked)}
res["forced"] = {"n": sum(r["forced_menu"] for r in d["rows"]), "locked_among_forced": sum(1 for r in d["rows"] if r["forced_menu"] and r["listed_total"] < r["full_bound"])}
pat = re.compile(r"(?<![\w.])\$?\s?(\d{1,3}(?:,\d{3})+|\d+)(?![\w]|\.\d)")
detail = []
for r in locked:
    e = eps[(r["game"], r["decision"])]
    c, D, u, u0 = r["cash"], r["debt"], r["full_bound"], r["listed_total"]
    full = {u, u - c, D - u} - {0, c, D, D - c}
    listed = {u0, u0 - c, D - u0} - {0, c, D, D - c} - full
    nums = {m["number"] for m in r["matches"]}
    # listed-only numerals need the raw text: re-read the first response
    st, rs = load(r["game"]); rr = rs[r["decision"]]; fa = rr.get("final_action") or {}
    texts = {"note": fa.get("private_thought"), "provider": reasoning(rr), "content": rr["attempts"][-1].get("assistant_content")}
    lnums = set()
    for ch, t in texts.items():
        if not t: continue
        for m in pat.finditer(t):
            n = int(m.group(1).replace(",", ""))
            if n in listed: lnums.add((ch, n))
    detail.append(dict(id=f"G{r['game']} d{r['decision']}", model=e["model"], C=c, D=D, U0=u0, Ustar=u,
                       first_action=e["actions"][0], full_matches=sorted(nums), listed_only_numerals=sorted(lnums),
                       contexts=[(m["channel"], m["number"], m["context"].replace("\n", " ")) for m in r["matches"]][:3],
                       note=(texts["note"] or "")[:420], provider=(texts["provider"] or "")[:420]))
res["locked_detail"] = detail
res["locked_summary"] = dict(C(("full" if x["full_matches"] else "none") + ("+listed" if x["listed_only_numerals"] else "") for x in detail))
(OUT / "totals_checks.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
print({k: v for k, v in res.items() if k != "locked_detail"})
for x in detail:
    print(f"\n{x['id']} {x['model']} C{x['C']} D{x['D']} U0 {x['U0']} U* {x['Ustar']} first={x['first_action']} full={x['full_matches']} listed_only={x['listed_only_numerals']}")
    for ch, n, ctx in x["contexts"][:2]: print(f"    [{ch} {n}] …{ctx[:230]}…")
    if not x["full_matches"]:
        print("    NOTE:", x["note"]); print("    PROV:", x["provider"])
