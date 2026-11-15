"""Build the three manuscript figures from data/*.json (no game records needed).

Palette: reference categorical slots validated with the dataviz validator
(#2a78d6 blue, #eb6834 orange; all-pairs CVD dE 9.2), grays for context.
Identity is always doubled by marker shape or a direct label.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
ASSETS = HERE / "assets"
ASSETS.mkdir(exist_ok=True)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "svg.fonttype": "none", "figure.dpi": 150,
})


def fig_bargaining():
    B = json.loads((DATA / "bargaining.json").read_text())
    P = json.loads((DATA / "pricing.json").read_text())["rows"]
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.0, 3.25), gridspec_kw={"width_ratios": [1.0, 1.15], "wspace": 0.42})
    rows = [("All recipients", "pooled"), ("Seed block 1", "block=1"), ("Seed block 2", "block=2"), ("Seed block 3", "block=3"),
            ("Seed block 4", "block=4"), ("Seed block 5", "block=5"), ("Recipient Sol", "recipient=Sol"),
            ("Recipient Gemini", "recipient=Gemini"), ("Recipient Grok", "recipient=Grok"), ("Recipient Opus*", "recipient=Opus")]
    ys = []
    y = 0
    for i, (lab, key) in enumerate(rows):
        if i in (1, 6):
            y += 0.6
        ys.append(y)
        y += 1
    ys = [max(ys) - v for v in ys]
    for (lab, key), yy in zip(rows, ys):
        d = B["open_reject"][key]
        a = 100 * d["author_only"][0] / d["author_only"][1]
        n = 100 * d["neither"][0] / d["neither"][1]
        ax.plot([n, a], [yy, yy], color=GRID, lw=2.2, zorder=1, solid_capstyle="round")
        ax.scatter([n], [yy], s=30, marker="s", facecolor="white", edgecolor=BLUE, lw=1.3, zorder=3)
        ax.scatter([a], [yy], s=32, marker="o", color=ORANGE, edgecolor="white", lw=0.8, zorder=4)
        ax.text(101.5, yy, f"{d['author_only'][1]} / {d['neither'][1]}", va="center", ha="left", fontsize=6.5, color=MUTED, clip_on=False)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 100)
    ax.set_xlabel("Opening offers rejected (%)")
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.tick_params(axis="y", length=0)
    ax.set_title("(a) Opening rejection", loc="left", fontsize=8.5, color=INK, fontweight="bold")
    ax.text(101.5, max(ys) + 0.95, "n", fontsize=6.5, color=MUTED, ha="left", clip_on=False)
    ax.scatter([], [], s=32, marker="o", color=ORANGE, label="Completes proposer's group only")
    ax.scatter([], [], s=30, marker="s", facecolor="white", edgecolor=BLUE, lw=1.3, label="Completes no group")
    ax.legend(loc="upper left", bbox_to_anchor=(-0.02, -0.17), frameon=False, fontsize=6.8, handletextpad=0.3, ncol=1)

    # (b) price ratios
    rng = np.random.default_rng(7)
    cols = [("ask", True, "Ask,\ncompletes\nbuyer"), ("ask", False, "Ask,\nother"), ("bid", True, "Bid,\ncompletes\nbidder"), ("bid", False, "Bid,\nother")]
    for j, (kind, comp, lab) in enumerate(cols):
        for opus, off, mk in ((False, -0.22, "o"), (True, 0.22, "^")):
            xs = [p["ratio"] for p in P if p["kind"] == kind and p["buyer_completes"] == comp and (p["author_model"] == "Opus") == opus]
            if not xs:
                continue
            xj = j + off + rng.uniform(-0.08, 0.08, len(xs))
            bx.scatter(xj, xs, s=7, marker=mk, color=BLUE if not opus else MUTED, alpha=0.55, lw=0, zorder=2)
            m = float(np.median(xs))
            bx.plot([j + off - 0.13, j + off + 0.13], [m, m], color=INK, lw=1.6, zorder=3, solid_capstyle="round")
            bx.text(j + off, 9.0, f"{m:.2f}", ha="center", va="bottom", fontsize=5.9, color=INK2)
            bx.text(j + off, 0.063, f"n={len(xs)}", ha="center", va="bottom", fontsize=5.4, color=MUTED)
    bx.set_yscale("log")
    bx.set_ylim(0.06, 12)
    bx.set_yticks([0.1, 0.25, 0.5, 1, 2, 4, 8])
    bx.set_yticklabels(["0.1", "0.25", "0.5", "1", "2", "4", "8"])
    bx.axhline(1, color=MUTED, lw=0.6, ls=(0, (3, 2)), zorder=1)
    bx.set_xticks(range(4))
    bx.set_xticklabels([c[2] for c in cols], fontsize=6.8)
    bx.tick_params(axis="x", length=0)
    bx.set_xlim(-0.55, 3.55)
    bx.set_ylabel("Cash / board list price")
    bx.grid(axis="y", color=GRID, lw=0.5)
    bx.set_title("(b) Cash-for-deed prices", loc="left", fontsize=8.5, color=INK, fontweight="bold")
    bx.scatter([], [], s=14, marker="o", color=BLUE, label="Sol, Gemini, Grok authors (standard)")
    bx.scatter([], [], s=14, marker="^", color=MUTED, label="Opus authors (action-only recovery)")
    bx.plot([], [], color=INK, lw=1.6, label="Median (value printed at top)")
    bx.legend(loc="upper left", bbox_to_anchor=(-0.02, -0.29), frameon=False, fontsize=6.8, handletextpad=0.3)
    fig.savefig(ASSETS / "bargaining.pdf", bbox_inches="tight")
    fig.savefig(ASSETS / "bargaining.png", bbox_inches="tight", dpi=200)
    plt.close(fig)


def fig_distress():
    P = json.loads((DATA / "pricing.json").read_text())["rows"]
    sold = [p for p in P if p["response"] == "accept_trade"]
    fig, ax = plt.subplots(figsize=(4.2, 2.9))
    rng = np.random.default_rng(3)
    for j, comp in enumerate((True, False)):
        xs = [p for p in sold if p["buyer_completes"] == comp]
        for opus, mk, col in ((False, "o", BLUE), (True, "^", MUTED)):
            ys = [p["seller_cash"] for p in xs if (p["seller_model"] == "Opus") == opus]
            xj = j + (0.13 if opus else -0.13) + rng.uniform(-0.08, 0.08, len(ys))
            ax.scatter(xj, ys, s=16, marker=mk, color=col, alpha=0.8, lw=0, zorder=3)
        low = sum(p["seller_cash"] < 100 for p in xs)
        ax.text(j, 6000, f"{low} of {len(xs)} sellers\nbelow \\$100", ha="center", va="top", fontsize=7, color=INK)
    ax.axhline(100, color=ORANGE, lw=1.0, ls=(0, (4, 2)), zorder=2)
    ax.text(1.58, 118, "\\$100", color=ORANGE, va="bottom", ha="right", fontsize=7)
    ax.set_yscale("symlog", linthresh=10)
    ax.set_ylim(0, 8000)
    ax.set_yticks([0, 10, 100, 1000])
    ax.set_yticklabels(["0", "10", "100", "1,000"])
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Deed completes\nbuyer's group (22)", "Deed completes\nno group (31)"])
    ax.set_xlim(-0.55, 1.6)
    ax.tick_params(axis="x", length=0)
    ax.set_ylabel("Seller's cash before the sale (game \\$)")
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.scatter([], [], s=16, marker="o", color=BLUE, label="Sol, Gemini or Grok seller")
    ax.scatter([], [], s=16, marker="^", color=MUTED, label="Opus seller")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.2), frameon=False, fontsize=6.8, ncol=2)
    fig.savefig(ASSETS / "distress.pdf", bbox_inches="tight")
    fig.savefig(ASSETS / "distress.png", bbox_inches="tight", dpi=200)
    plt.close(fig)


def fig_lifecycle():
    E = json.loads((DATA / "completion_episodes.json").read_text())["episodes"]
    tr = [x for x in E if x["route"] == "trade"]
    order = ["Sol", "Gemini", "Opus", "Grok"]
    fig, ax = plt.subplots(figsize=(7.0, 5.6))
    y = 0
    ticks, labels = [], []
    xmax = max(x["duration_turns"] for x in tr)
    for m in order:
        xs = sorted([x for x in tr if x["model"] == m], key=lambda x: (x["first_build_turn"] is None, -(x["duration_turns"])))
        start_y = y
        for x in xs:
            s = x["start_turn"]
            dur = x["duration_turns"]
            ax.plot([0, dur], [y, y], color=GRID, lw=2.4, solid_capstyle="butt", zorder=1)
            if x["first_build_turn"] is not None:
                b = x["first_build_turn"] - s
                ax.plot([b, dur], [y, y], color=BLUE, lw=2.4, solid_capstyle="butt", zorder=2, alpha=0.85)
                ax.scatter([b], [y], marker="|", s=40, color=INK, lw=1.0, zorder=4)
            for t, dev in x["landing_log"]:
                if dev:
                    ax.scatter([t - s], [y], s=9, marker="o", color=ORANGE, edgecolor="white", lw=0.3, zorder=5)
                else:
                    ax.scatter([t - s], [y], s=9, marker="o", facecolor="white", edgecolor=INK2, lw=0.6, zorder=5)
            if x["end_reason"] == "eliminated":
                ax.scatter([dur], [y], s=12, marker="x", color=INK2, lw=0.8, zorder=4)
            y += 1
        tot_rent = sum(x["rent"] for x in xs)
        land = sum(x["opp_landings"] for x in xs)
        undev = land - sum(x["landings_developed"] for x in xs)
        ax.text(xmax + 4, (start_y + y - 1) / 2, f"{m}\n{len(xs)} groups\n{land} landings, {undev} undeveloped\nrent \\${tot_rent:,}",
                va="center", ha="left", fontsize=6.8, color=INK, clip_on=False)
        if m != order[-1]:
            ax.axhline(y + 0.2, color=MUTED, lw=0.5)
        y += 1.4
    ax.set_ylim(y - 0.6, -1.0)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-2, xmax + 2)
    ax.set_xlabel("Turns since the trade completed the group (all players' turns)")
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.plot([], [], color=GRID, lw=2.4, label="Owned, not yet built")
    ax.plot([], [], color=BLUE, lw=2.4, label="After first own build")
    ax.scatter([], [], marker="|", s=40, color=INK, label="First build")
    ax.scatter([], [], s=12, marker="o", color=ORANGE, label="Opponent landing, group developed")
    ax.scatter([], [], s=12, marker="o", facecolor="white", edgecolor=INK2, label="Opponent landing, undeveloped")
    ax.scatter([], [], s=14, marker="x", color=INK2, label="Owner eliminated")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=False, fontsize=6.8)
    fig.savefig(ASSETS / "lifecycle.pdf", bbox_inches="tight")
    fig.savefig(ASSETS / "lifecycle.png", bbox_inches="tight", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig_bargaining()
    fig_distress()
    fig_lifecycle()
    print("figures written to", ASSETS)
