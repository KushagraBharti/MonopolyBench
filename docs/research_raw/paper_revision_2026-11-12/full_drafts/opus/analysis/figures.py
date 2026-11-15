"""Two figures from the analysis outputs (no record reading beyond data/*.json).

Palette: the dataviz reference slots 1-3 (blue, orange, aqua), validated
light-mode with scripts/validate_palette.js (all checks pass; aqua needs
relief, which the printed counts and tables provide). Text uses ink colours.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
DRAFT = HERE.parent
ASSETS = DRAFT / "assets"
ASSETS.mkdir(exist_ok=True)
FONT_DIR = Path.home() / ".local/share/texlive/2026-compatible/texmf-dist/fonts/opentype/public/tex-gyre"
for f in ("texgyreheros-regular.otf", "texgyreheros-bold.otf"):
    if (FONT_DIR / f).exists():
        font_manager.fontManager.addfont(str(FONT_DIR / f))
plt.rcParams.update({
    "font.family": "TeX Gyre Heros" if (FONT_DIR / "texgyreheros-regular.otf").exists() else "DejaVu Sans",
    "font.size": 9.5, "axes.edgecolor": "#8a8984", "axes.linewidth": 0.6, "axes.labelcolor": "#0b0b0b",
    "xtick.color": "#52514e", "ytick.color": "#52514e", "text.color": "#0b0b0b",
    "pdf.fonttype": 42, "svg.fonttype": "none", "figure.dpi": 150,
})
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e2e1dc", "#ffffff"

offers = json.loads((DRAFT / "data/offers_analysis.json").read_text())
finance = json.loads((DRAFT / "data/finance_analysis.json").read_text())
reading = json.loads((DRAFT / "data/necessary_text_reading.json").read_text())


def save(fig, name):
    fig.savefig(ASSETS / f"{name}.pdf", bbox_inches="tight", facecolor=SURF, metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(ASSETS / f"{name}.png", bbox_inches="tight", facecolor=SURF, dpi=200)
    plt.close(fig)


# ------------------------------------------------------------ Figure: offer forms
rows = [("all", "swap", "Swaps, all proposers"),
        ("without_conflicting_grok_openings", "swap", "Swaps, excl. conflicting Grok openings"),
        ("without_grok_authored", "swap", "Swaps, excl. Grok-authored offers"),
        ("all", "cash_bid", "Cash bids, all proposers"),
        ("without_conflicting_grok_openings", "cash_bid", "Cash bids, excl. conflicting Grok openings"),
        ("without_grok_authored", "cash_bid", "Cash bids, excl. Grok-authored offers")]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.7, 3.6), gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.08}, sharey=True)
ys = [5.6, 4.6, 3.6, 2.0, 1.0, 0.0]
for y, (ver, form, label) in zip(ys, rows):
    g = offers["composition_versions"][ver][form]
    a, b = g["proposer_only"], g["neither"]
    ra, rb = a["R"] / a["n"], b["R"] / b["n"]
    ax1.plot([rb, ra], [y, y], color="#b9b8b2", lw=1.6, zorder=1, solid_capstyle="round")
    ax1.scatter([ra], [y], s=34, color=BLUE, zorder=3, edgecolor=SURF, linewidth=1.2)
    ax1.scatter([rb], [y], s=34, color=ORANGE, zorder=3, edgecolor=SURF, linewidth=1.2, marker="D")
    lo, hi = (ra, rb) if ra < rb else (rb, ra)
    left_is_a = ra < rb
    ax1.text(lo - 0.018, y, f"{a['R']}/{a['n']}" if left_is_a else f"{b['R']}/{b['n']}", ha="right", va="center", fontsize=8.6, color=INK2)
    ax1.text(hi + 0.018, y, f"{b['R']}/{b['n']}" if left_is_a else f"{a['R']}/{a['n']}", ha="left", va="center", fontsize=8.6, color=INK2)
    # gap panel
    rs = offers["resampling"][ver][form]["two_stage"]
    gap = g["gap_pp"]
    ax2.plot([rs["p2.5"], rs["p97.5"]], [y, y], color=INK2, lw=1.3, solid_capstyle="round", zorder=2)
    blocks = offers["seed_blocks"][ver][form]["per_block"]
    for bk, v in blocks.items():
        if v["gap_pp"] is not None:
            ax2.scatter([v["gap_pp"]], [y + 0.28], s=9, color="#9a9993", zorder=2, linewidth=0)
    ax2.scatter([gap], [y], s=30, color=INK, zorder=3, edgecolor=SURF, linewidth=1.0)
    ax2.text(rs["p97.5"] + 2.5, y, f"{gap:+.1f}".replace("-", "\u2212"), va="center", fontsize=8.6, color=INK)
ax1.set_yticks(ys)
ax1.set_yticklabels([r[2] for r in rows])
ax1.set_xlim(0.15, 1.0)
ax1.set_xticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax1.set_xticklabels(["20%", "40%", "60%", "80%", "100%"])
ax1.set_xlabel("Share of opening offers rejected")
ax2.set_xlim(-45, 65)
ax2.axvline(0, color="#8a8984", lw=0.7, zorder=0)
ax2.set_xlabel("Gap, proposer-only minus neither (pp)")
for ax in (ax1, ax2):
    ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
ax2.spines["left"].set_visible(False)
from matplotlib.lines import Line2D
handles = [Line2D([0], [0], marker="o", ls="", color=BLUE, markersize=5.5),
           Line2D([0], [0], marker="D", ls="", color=ORANGE, markersize=5),
           Line2D([0], [0], color=INK2, lw=1.3),
           Line2D([0], [0], marker="o", ls="", color="#9a9993", markersize=3)]
fig.legend(handles, ["completes proposer's group only", "completes neither group",
                     "gap: two-stage resampling, 95%", "gap in one seed block"],
           loc="upper center", bbox_to_anchor=(0.45, 1.10), ncol=2, frameon=False, fontsize=8.6,
           handletextpad=0.35, columnspacing=1.4)
save(fig, "offer_forms")

# ------------------------------------------------------------ Figure: sixteen necessary episodes
nec = finance["necessary"]["rows"]
cat = {(r["game"], r["decision"]): r for r in reading["rows"]}
nec = sorted(nec, key=lambda r: (r["outcome"] != "paid", r["game"], r["first_decision"]))
fig, ax = plt.subplots(figsize=(6.7, 5.0))
for i, r in enumerate(nec):
    y = len(nec) - 1 - i
    base = r["cash"] + r["L0"]
    segs = [(0, base, BLUE), (base, r["S"], AQUA), (base + r["S"], r["U"], ORANGE)]
    for left, width, col in segs:
        if width > 0:
            ax.barh(y, width - 4 if width > 8 else width, left=left + 2, height=0.62, color=col, linewidth=0, zorder=2)
    ax.plot([r["debt"], r["debt"]], [y - 0.42, y + 0.42], color=INK, lw=1.6, zorder=4, solid_capstyle="butt")
    c = cat[(r["game"], r["first_decision"])]
    word = {"explicit": "states them", "open_check": "open check", "omits": "omits them"}[c["category"]]
    chan = {"note": "note", "provider": "reasoning"}[c["channel"]]
    out = "paid" if r["outcome"] == "paid" else "bankrupt"
    ax.text(1500, y, f"{out}; {word} ({chan})", va="center", fontsize=8.4, color=INK if r["outcome"] == "paid" else INK)
labels = [f"G{r['game']} d{r['first_decision']} {r['model']}" for r in nec]
ax.set_yticks(range(len(nec) - 1, -1, -1))
ax.set_yticklabels(labels, fontsize=8.6)
ax.set_xlim(0, 1480)
ax.set_xlabel("Game dollars at the first liquidation decision")
ax.axhline(1.5, color="#8a8984", lw=0.6, ls=(0, (2, 2)))
ax.grid(axis="x", color=GRID, lw=0.6, zorder=0)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.tick_params(length=0)
handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=AQUA),
           plt.Rectangle((0, 0), 1, 1, color=ORANGE), plt.Line2D([0], [0], color=INK, lw=1.6)]
ax.legend(handles, ["cash + mortgages listed on the first menu", "half the cost of every building",
                    "mortgages released only by selling buildings", "debt owed"],
          loc="upper left", bbox_to_anchor=(0, 1.15), ncol=2, frameon=False, fontsize=8.6, handlelength=1.2,
          handletextpad=0.4, columnspacing=0.9)
save(fig, "necessary_collateral")
print("figures written to", ASSETS)
