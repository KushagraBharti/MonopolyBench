"""Figure for the proposed central result, from data/cross_checks.json and data/liquidity_openings.json.
Run from repo root with any Python that has matplotlib, e.g.
  /tmp/monopoly-astra-rewrite-venv/bin/python -I docs/research_raw/paper_revision_2026-11-11/reviews/opus/tools/make_figure.py"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = pathlib.Path.cwd(); OUT = ROOT / "docs/research_raw/paper_revision_2026-11-11/reviews/opus"
cc = json.loads((OUT / "data/cross_checks.json").read_text())["A_rejection_composition"]["opening"]
lo = json.loads((OUT / "data/liquidity_openings.json").read_text())["cells"]
frac = lambda s: tuple(int(x) for x in s.split("/"))
C_COMP, C_OTH = "#b5532a", "#33627f"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans"})
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw={"width_ratios": [1.15, 1]})

rows = [("All openings", (138, 187), (105, 176))]
for k in "12345":
    v = cc["by_block"][k]; rows.append((f"Seed block {k}", frac(v["author_only"]), frac(v["neither_requests_deed"])))
for m in ["Sol", "Gemini", "Grok", "Opus"]:
    v = cc["by_recipient"][m]; rows.append((f"Recipient {m}" + ("*" if m == "Opus" else ""), frac(v["author_only"]), frac(v["neither_requests_deed"])))
ys = list(range(len(rows)))[::-1]
for y, (lab, c, o) in zip(ys, rows):
    pc, po = 100 * c[0] / c[1], 100 * o[0] / o[1]
    a.plot([po, pc], [y, y], color="#c9c9c9", lw=2, zorder=1)
    a.scatter(pc, y, color=C_COMP, s=28, zorder=3)
    a.scatter(po, y, facecolor="white", edgecolor=C_OTH, s=28, lw=1.5, zorder=3)
    a.text(103, y, f"{c[0]}/{c[1]} vs {o[0]}/{o[1]}", va="center", fontsize=7, color="#555")
a.set_yticks(ys); a.set_yticklabels([r[0] for r in rows], fontsize=8)
a.axhline(ys[5] - 0.5, color="#e5e5e5", lw=0.8); a.axhline(ys[0] - 0.5, color="#e5e5e5", lw=0.8)
a.set_xlim(0, 100); a.set_xlabel("Opening offers rejected (%)")
a.set_title("(a) Opening rejection, matched requests", fontsize=9, loc="left")
a.scatter([], [], color=C_COMP, s=28, label="completes only the requester's group")
a.scatter([], [], facecolor="white", edgecolor=C_OTH, s=28, lw=1.5, label="requests a deed, completes no group")
a.legend(loc="lower left", bbox_to_anchor=(-0.02, -0.42), fontsize=7, frameon=False)

bands = [("lt100", "under $100"), ("100-299", "$100–299"), ("300plus", "$300+")]
x = range(3)
for scope, ls, lab in [("All_but_Opus", "-", "standard-condition holders"), ("All", ":", "all holders")]:
    pc = [lo[f"{scope}|opening|{b}"]["completion_request"] for b, _ in bands]
    po = [lo[f"{scope}|opening|{b}"]["other_deed_request"] for b, _ in bands]
    b.plot(x, [100 * r["reject"] / r["n"] for r in pc], ls, marker="o", color=C_COMP, lw=1.6, ms=4)
    b.plot(x, [100 * r["reject"] / r["n"] for r in po], ls, marker="o", color=C_OTH, lw=1.6, ms=4, mfc="white")
    if scope == "All_but_Opus":
        for i, (r1, r2) in enumerate(zip(pc, po)):
            b.text(i, 100 * r1["reject"] / r1["n"] + 4, f'{r1["reject"]}/{r1["n"]}', ha="center", fontsize=7, color=C_COMP)
            low = min(100 * r2["reject"] / r2["n"], 100 * lo[f'All|opening|{bands[i][0]}']["other_deed_request"]["reject"] / lo[f'All|opening|{bands[i][0]}']["other_deed_request"]["n"])
            b.text(i, low - 9, f'{r2["reject"]}/{r2["n"]}', ha="center", fontsize=7, color=C_OTH)
b.plot([], [], "-", color="#555", label="standard-condition holders (labelled)")
b.plot([], [], ":", color="#555", label="all holders, incl. Opus")
b.set_xticks(list(x)); b.set_xticklabels([l for _, l in bands]); b.set_ylim(0, 100)
b.set_xlabel("Holder's cash when the opening offer arrives"); b.set_ylabel("Rejected (%)")
b.set_title("(b) Openings by holder cash", fontsize=9, loc="left")
b.legend(loc="lower left", bbox_to_anchor=(-0.02, -0.42), fontsize=7, frameon=False)
fig.tight_layout()
(OUT / "assets").mkdir(exist_ok=True)
for ext in ("pdf", "png"):
    fig.savefig(OUT / f"assets/fig_guard_liquidity.{ext}", dpi=200, bbox_inches="tight")
print("ok")
