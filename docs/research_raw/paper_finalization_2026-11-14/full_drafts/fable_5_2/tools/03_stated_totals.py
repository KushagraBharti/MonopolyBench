"""Number-match check on first texts where an agent states what it can raise.

For every financing episode whose own-asset bound U* falls short of the debt, and for the
sixteen payable episodes that need released collateral, look for a dollar figure in the
first response that equals

  the full bound      U*  (or the proceeds U* - C, or the gap D - U*, or the remainder U* - D)
  the listed-only sum U0  (or U0 - C, or D - U0), when U0 differs from U*.

This is string arithmetic on stored text. A match shows that the figure is written in the
response. It does not show how the figure was derived, and a response that itemises
resources without a total has to be read directly; those cases are listed, not scored.
Figures that coincide with the debt, the cash or the shortfall D - C are not counted.
Writes data/stated_totals.json.
"""
import collections
import re

from lib import *

C = collections.Counter
eps = read_json("episodes.json")
NUM = re.compile(r"(?<![\w.])\$?\s?(\d{1,3}(?:,\d{3})+|\d+)(?![\w]|\.\d)")


def nums(t):
    return {int(x.replace(",", "")) for x in NUM.findall(t or "")}


def context(text, n, width=70):
    for m in NUM.finditer(text or ""):
        if int(m.group(1).replace(",", "")) == n:
            a, b = max(0, m.start() - width), min(len(text), m.end() + width)
            return text[a:b].replace("\n", " ")
    return ""


rows = []
for e in eps:
    payable_necessity = e["u0"] < e["debt"] <= e["ustar"]
    unpayable = e["ustar"] < e["debt"]
    if not (payable_necessity or unpayable):
        continue
    ch = e["first_channels"]
    texts = {"note": e["first_note"], "provider": ch["provider_text"], "content": ch["assistant_content"]}
    trivial = {e["debt"], e["cash"], e["debt"] - e["cash"]}
    star = {e["ustar"], e["ustar"] - e["cash"], abs(e["debt"] - e["ustar"])} - trivial - {0}
    zero = ({e["u0"], e["u0"] - e["cash"], e["debt"] - e["u0"]} - trivial - {0} - star) if e["u0"] != e["ustar"] else set()
    hit = {}
    for name, t in texts.items():
        ns = nums(t)
        hit[name] = {"star": sorted(star & ns), "zero": sorted(zero & ns)}
    any_star = sorted(set().union(*[set(h["star"]) for h in hit.values()]))
    any_zero = sorted(set().union(*[set(h["zero"]) for h in hit.values()]))
    where = next((n for n in ("note", "provider", "content") if hit[n]["star"]), None)
    rows.append(dict(
        game=e["game"], first=e["first"], model=e["model"], debt=e["debt"], cash=e["cash"], u0=e["u0"], ustar=e["ustar"],
        group="payable_necessity" if payable_necessity else "unpayable",
        forced_menu=e["menu"] == ["declare_bankruptcy"], locked_collateral=e["u0"] != e["ustar"],
        first_action=e["first_action"], hits=hit, states_full_bound=bool(any_star), states_listed_only=bool(any_zero),
        full_bound_figure=any_star, listed_only_figure=any_zero, full_bound_channel=where,
        full_bound_context=context(texts[where], any_star[0]) if where else "",
    ))

# Responses that itemise without a matching total, read directly from the stored text.
# Each entry records what the text counts. These are author readings of five short texts.
READ = {
    (2, 215): "includes_locked",   # Opus: light-blue mortgages "for $160 once the houses are gone", no total stated
    (10, 188): "includes_locked",  # Sol: "even subsequently mortgaging light blues adds only $160", no total stated
    (3, 426): "listed_only",       # Sol: "maximum $914" = U0, omits $160 of light-blue mortgages
    (5, 309): "listed_only",       # Opus: "only gets me to 639 total" = U0, omits $160
    (8, 280): "listed_only",       # Grok: "total $386" = U0, "No unmortgaged properties", omits $280
}
for r in rows:
    k = (r["game"], r["first"])
    if r["states_full_bound"]:
        r["reading"] = "exact_full_bound"
    elif k in READ:
        r["reading"] = READ[k]
    elif r["states_listed_only"]:
        r["reading"] = "listed_only"
    elif r["forced_menu"]:
        r["reading"] = "forced_menu_no_figure"
    else:
        r["reading"] = "unclassified"

write_json("stated_totals.json", rows)
un = [r for r in rows if r["group"] == "unpayable"]
opt = [r for r in un if not r["forced_menu"]]
print("unpayable", len(un), "| with a financing option", len(opt), "| forced menus", len(un) - len(opt))
print("with option, by reading:", C(r["reading"] for r in opt))
print("with option, no locked collateral:", C(r["reading"] for r in opt if not r["locked_collateral"]))
print("with option, locked collateral:", C(r["reading"] for r in opt if r["locked_collateral"]))
print("forced menus:", C(r["reading"] for r in un if r["forced_menu"]))
print("channel of the full-bound figure:", C(r["full_bound_channel"] for r in opt if r["states_full_bound"]))
print("by model, with option:", sorted(C((r["model"], r["reading"]) for r in opt).items()))
nec = [r for r in rows if r["group"] == "payable_necessity"]
print("necessity:", C((r["states_full_bound"], r["states_listed_only"]) for r in nec))
for r in nec:
    print(f"   G{r['game']} d{r['first']} {r['model']} U0 {r['u0']} U* {r['ustar']} D {r['debt']} full {r['full_bound_figure']} listed {r['listed_only_figure']} ch {r['full_bound_channel']}")
print()
for r in opt:
    if r["states_full_bound"]:
        print(f"G{r['game']} d{r['first']} {r['model']} U* {r['ustar']} D {r['debt']} C {r['cash']} fig {r['full_bound_figure']} [{r['full_bound_channel']}] :: {r['full_bound_context']}")
