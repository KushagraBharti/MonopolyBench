"""Draw the two figures from the analysis outputs.  No game, engine or model call.

Colors are the first three categorical slots of the reference palette
(blue, orange, aqua), validated for a light surface with the dataviz
validator: adjacent CVD separation 9.2, normal-vision 27.6.  Aqua is below
3:1 contrast on white, so every aqua segment carries a printed count and the
same counts appear in the tables.  Text uses ink colors, never series colors.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parents[1]
DATA, ASSETS = HERE / "data", HERE / "assets"
ASSETS.mkdir(exist_ok=True)
O = json.loads((DATA / "b1_offers.json").read_text())
D = json.loads((DATA / "b2_debt.json").read_text())
R = json.loads((DATA / "b6_readings.json").read_text())

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GRAY, INK, INK2, GRID, SURFACE = "#9a9994", "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9.2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK,
    "axes.titlesize": 9.8, "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left",
    "pdf.fonttype": 42, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "legend.frameon": False,
    "xtick.major.size": 0, "ytick.major.size": 0,
})


def save(fig, name):
    fig.savefig(ASSETS / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(ASSETS / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 1: debts
# ---------------------------------------------------------------------------
T = D["tiers_among_payable"]
ab = D["above_bound"]
rows = [
    ("Cash and mortgages\nalready listed", T["listed"]["paid"], 0, 0),
    ("Building sales\nas well", T["sales"]["paid"], T["sales"]["declared"], 0),
    ("Mortgages the menu\ndoes not yet list", T["unlisted"]["paid"], T["unlisted"]["declared"], 0),
    ("Debt above\nevery own asset", 0, ab["declared_at_first_menu"], ab["episodes"] - ab["declared_at_first_menu"]),
    ("Menu offers no\nbuilding sale", 0, 0, 1),
]
assert sum(a + b + c for _, a, b, c in rows) == 188
fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.3, 4.1), gridspec_kw={"width_ratios": [1.0, 1.15], "wspace": 0.74})
for i, (label, paid, quit_, other) in enumerate(rows):
    left = 0
    for val, col in ((paid, BLUE), (quit_, ORANGE), (other, GRAY)):
        if val:
            ax.barh(i, val, left=left, height=0.52, color=col, edgecolor=SURFACE, linewidth=1.6)
            if val >= 9:
                ax.text(left + val / 2, i, str(val), ha="center", va="center", color="white", fontsize=8.2, fontweight="bold")
            left += val
    small = [str(v) for v in (paid, quit_, other) if 0 < v < 9]
    if small:
        ax.text(left + 1.2, i, " + ".join(small) if len(small) > 1 else small[0], ha="left", va="center", color=INK, fontsize=8.2)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows], fontsize=8.6)
ax.invert_yaxis()
ax.set_xlim(0, 70)
ax.set_xticks([0, 20, 40, 60])
ax.xaxis.grid(True, color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
ax.spines["left"].set_visible(False)
ax.set_xlabel("Debt episodes")
ax.set_title("A. All 188 debts", x=-0.55)
ax.legend(handles=[Patch(color=BLUE, label="Paid"), Patch(color=ORANGE, label="Quit at the first menu"), Patch(color=GRAY, label="Eliminated after liquidating")],
          loc="upper center", bbox_to_anchor=(0.36, -0.2), ncol=1, fontsize=8.6, handlelength=1.1, labelcolor=INK)

cases = sorted(R["rows"], key=lambda r: (r["outcome"] != "paid", r["reach_without_unlisted"] - r["debt"]))
for i, r in enumerate(cases):
    lo = r["reach_without_unlisted"] - r["debt"]
    hi = lo + r["unlisted_mortgage"]
    col = BLUE if r["outcome"] == "paid" else ORANGE
    bx.plot([lo, hi], [i, i], color=col, linewidth=2, solid_capstyle="round", zorder=2)
    bx.scatter([lo], [i], s=34, color=SURFACE, edgecolor=col, linewidth=1.6, zorder=3)
    bx.scatter([hi], [i], s=38, color=col, edgecolor=SURFACE, linewidth=1.2, zorder=3)
bx.axvline(0, color=INK2, linewidth=0.9, zorder=1)
bx.set_yticks(range(len(cases)))
bx.set_yticklabels([f"G{r['game']} {r['model']}" for r in cases], fontsize=8.0)
bx.invert_yaxis()
bx.set_xlim(-360, 400)
bx.set_xticks([-300, 0, 300])
bx.set_xticklabels(["$300 short", "the debt", "$300 over"])
bx.xaxis.grid(True, color=GRID, linewidth=0.6)
bx.set_axisbelow(True)
bx.spines["left"].set_visible(False)
bx.set_title("B. The sixteen debts in row three", x=-0.3)
bx.set_xlabel("Most the debtor could raise,\nrelative to the debt")
n_paid = sum(r["outcome"] == "paid" for r in cases)
bx.axhline(n_paid - 0.5, color=GRID, linewidth=0.8)
bx.legend(handles=[Line2D([], [], marker="o", color=BLUE, markerfacecolor=SURFACE, markeredgewidth=1.6, linewidth=0, markersize=5.5, label="Without unlisted mortgages"),
                   Line2D([], [], marker="o", color=BLUE, linewidth=0, markersize=5.8, label="With them (paid)"),
                   Line2D([], [], marker="o", color=ORANGE, linewidth=0, markersize=5.8, label="With them (quit)")],
          loc="upper center", bbox_to_anchor=(0.42, -0.2), ncol=1, fontsize=8.6, handletextpad=0.4, labelcolor=INK)
save(fig, "debt_partition")

# ---------------------------------------------------------------------------
# Figure 2: opening offers
# ---------------------------------------------------------------------------
H = O["headline_cells"]
cells = [
    ("Swap, completes\nproposer only", H["swap_proposer_only"]),
    ("Swap, completes\nboth", H["swap_both"]),
    ("Swap, completes\nneither", H["swap_neither"]),
    ("Cash bid, completes\nproposer only", H["cash_bid_proposer_only"]),
    ("Cash bid, completes\nneither", H["cash_bid_neither"]),
]
fig, (ax, bx) = plt.subplots(1, 2, figsize=(6.2, 4.0), gridspec_kw={"width_ratios": [1.0, 0.95], "wspace": 1.22})
ypos = [0, 1, 2, 3.35, 4.35]
for y, (label, c) in zip(ypos, cells):
    left = 0
    for key, col in (("reject", BLUE), ("counter", ORANGE), ("accept", AQUA)):
        w = 100 * c[key] / c["n"]
        ax.barh(y, w, left=left, height=0.56, color=col, edgecolor=SURFACE, linewidth=1.6)
        if w >= 9:
            ax.text(left + w / 2, y, str(c[key]), ha="center", va="center", color="white", fontsize=8.2, fontweight="bold")
        left += w
    tail = [str(c[k]) for k in ("accept",) if 0 < 100 * c[k] / c["n"] < 9]
    if tail:
        ax.text(101.5, y, tail[0], ha="left", va="center", color=INK, fontsize=8.2)
ax.set_yticks(ypos)
ax.set_yticklabels([l for l, c in cells], fontsize=8.4)
for y, (_, c) in zip(ypos, cells):
    ax.text(-2.0, y + 0.42, "", fontsize=1)
ax.invert_yaxis()
ax.set_xlim(0, 108)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xlabel("Share of opening offers (%)")
ax.xaxis.grid(True, color=GRID, linewidth=0.6)
ax.set_axisbelow(True)
ax.spines["left"].set_visible(False)
ax.set_title("A. Responses to opening offers", x=-0.6)
ax.legend(handles=[Patch(color=BLUE, label="Reject"), Patch(color=ORANGE, label="Counter"), Patch(color=AQUA, label="Accept")],
          loc="upper center", bbox_to_anchor=(0.4, -0.2), ncol=3, fontsize=8.6, handlelength=1.1, columnspacing=1.2, labelcolor=INK)

S = O["sensitivity"]
series = [
    ("Swaps,\nall proposers", S["swap_gap"]),
    ("Swaps, no conflicting\nGrok openings", S["swap_gap_without_conflict_openings"]),
    ("Swaps, no Grok-\nauthored offers", S["swap_gap_without_grok_authors"]),
    ("Cash bids,\nall proposers", S["cash_bid_gap"]),
]
for i, (label, s) in enumerate(series):
    g = s["game_resampling"]
    lo, hi = s["leave_one_block_out_range_pp"]
    bx.plot([g["p2_5_pp"], g["p97_5_pp"]], [i, i], color=BLUE, linewidth=1.1, alpha=0.55, zorder=2, solid_capstyle="butt")
    bx.plot([lo, hi], [i, i], color=BLUE, linewidth=4.2, zorder=3, solid_capstyle="butt")
    bx.scatter([b for b in s["per_block_pp"] if b is not None], [i + 0.27] * 5, s=13, color=SURFACE, edgecolor=INK2, linewidth=0.8, zorder=3)
    bx.scatter([s["point_pp"]], [i], s=40, color=BLUE, edgecolor=SURFACE, linewidth=1.3, zorder=4)
    bx.text(84, i, f"{s['point_pp']:+.1f}".replace("-", "−"), ha="right", va="center", color=INK, fontsize=8.4)
bx.axvline(0, color=INK2, linewidth=0.9, zorder=1)
bx.set_yticks(range(len(series)))
bx.set_yticklabels([s[0] for s in series], fontsize=8.4)
bx.invert_yaxis()
bx.set_ylim(len(series) - 0.4, -0.75)
bx.set_xlim(-32, 86)
bx.set_xticks([-25, 0, 25, 50])
bx.xaxis.grid(True, color=GRID, linewidth=0.6)
bx.set_axisbelow(True)
bx.spines["left"].set_visible(False)
bx.set_xlabel("Rejection share, proposer only\nminus neither (percentage points)")
bx.set_title("B. Size of the completion gap", x=-0.95)
bx.legend(handles=[Line2D([], [], marker="o", color=BLUE, linewidth=0, markersize=5.8, label="All twenty games"),
                   Line2D([], [], color=BLUE, linewidth=4.2, label="Leave one seed block out"),
                   Line2D([], [], color=BLUE, linewidth=1.1, alpha=0.55, label="Game resampling, 2.5 to 97.5%"),
                   Line2D([], [], marker="o", color=INK2, markerfacecolor=SURFACE, linewidth=0, markersize=4, label="Each seed block alone")],
          loc="upper center", bbox_to_anchor=(0.12, -0.3), ncol=1, fontsize=8.4, handlelength=1.5, labelcolor=INK)
save(fig, "offer_responses")
print("figures written")
