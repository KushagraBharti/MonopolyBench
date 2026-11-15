"""Draw the manuscript figures from the tabulations in ``data/``.

No game data is recomputed here: every plotted value is read from a JSON file
written by the ``a*`` scripts.  The four system colours pass the dataviz
validator on all pairs (light surface) and are doubled by marker shape.
"""
from __future__ import annotations

import collections
import json
import statistics as S
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
ASSETS = HERE / "assets"
ASSETS.mkdir(exist_ok=True)

for name in ("texgyreheros-regular.otf", "texgyreheros-bold.otf", "texgyreheros-italic.otf"):
    try:
        path = subprocess.run(["/Library/TeX/texbin/kpsewhich", name], capture_output=True, text=True).stdout.strip()
        if path:
            fm.fontManager.addfont(path)
    except Exception:
        pass
plt.rcParams.update(
    {
        "font.family": ["TeX Gyre Heros", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 8,
        "axes.titlesize": 8.5,
        "axes.labelsize": 8,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "axes.edgecolor": "#8a8a86",
        "xtick.color": "#52514e",
        "ytick.color": "#52514e",
        "axes.labelcolor": "#2b2b2a",
        "text.color": "#0b0b0b",
        "grid.color": "#e4e3df",
        "grid.linewidth": 0.6,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.dpi": 300,
    }
)
MODELS = ["Sol", "Gemini", "Opus", "Grok"]
COL = {"Sol": "#2a78d6", "Gemini": "#1baf7a", "Opus": "#eb6834", "Grok": "#b0457f"}
MARK = {"Sol": "o", "Gemini": "s", "Opus": "^", "Grok": "D"}
INK = "#0b0b0b"
MUTED = "#8a8a86"
SEQ = ["#d7dde6", "#8fa3bd", "#3b5578"]  # one hue, light -> dark


def load(name):
    return json.loads((DATA / name).read_text())


def save(fig, stem):
    fig.savefig(ASSETS / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(ASSETS / f"{stem}.png", bbox_inches="tight", pad_inches=0.03, dpi=200)
    plt.close(fig)


def system_legend(ax, **kw):
    handles = [Line2D([], [], marker=MARK[m], color="none", markerfacecolor=COL[m], markeredgecolor="white", markersize=6, label=m) for m in MODELS]
    return ax.legend(handles=handles, frameon=False, handletextpad=0.2, columnspacing=0.9, **kw)


# ---------------------------------------------------------------------------
def fig_prices():
    P = load("a6_pure_offers.json")
    rng = np.random.default_rng(7)
    fig, axes = plt.subplots(1, 2, figsize=(6.7, 3.3), sharey=True)
    for ax, kind, who, title in ((axes[0], "ask", "seller_model", "Asks written by the deed holder"), (axes[1], "bid", "buyer_model", "Bids written by the would-be buyer")):
        sel = [p for p in P if p["kind"] == kind and p.get("color") and p["mstat"] in ("unmortgaged", "mortgaged")]
        for xi, miss in enumerate((2, 1, 0)):
            for ms, off in (("unmortgaged", -0.19), ("mortgaged", 0.19)):
                pts = [p for p in sel if p["missing_after"] == miss and p["mstat"] == ms]
                for p in pts:
                    m = p[who]
                    x = xi + off + rng.uniform(-0.13, 0.13)
                    filled = ms == "unmortgaged"
                    ax.plot(x, p["ratio"], MARK[m], markersize=3.6, markerfacecolor=COL[m] if filled else "white",
                            markeredgecolor=COL[m] if not filled else "white", markeredgewidth=0.7 if not filled else 0.4, alpha=0.9, zorder=3)
                if pts:
                    med = S.median(p["ratio"] for p in pts)
                    ax.plot([xi + off - 0.17, xi + off + 0.17], [med, med], color=INK, lw=1.6, solid_capstyle="round", zorder=4)
                    ax.annotate(f"{med:.2f}\nn={len(pts)}", (xi + off, 15.5), ha="center", va="top", fontsize=6.6, color="#52514e", linespacing=1.15)
        ax.set_yscale("log", base=2)
        ax.set_ylim(0.11, 17.5)
        ax.set_yticks([0.125, 0.25, 0.5, 1, 2, 4, 8])
        ax.set_yticklabels(["⅛", "¼", "½", "1", "2", "4", "8"])
        ax.axhline(1, color=MUTED, lw=0.6, zorder=1)
        ax.grid(axis="y", zorder=0)
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["two short", "one short", "completes\nthe group"])
        ax.set_xlim(-0.55, 2.55)
        ax.set_title(title, loc="left", pad=6)
        ax.tick_params(length=0)
    axes[0].set_ylabel("cash ÷ board list price (log scale)")
    fig.text(0.5, -0.045, "buyer's position in the color group after the proposed trade", ha="center", fontsize=8, color="#2b2b2a")
    handles = [Line2D([], [], marker=MARK[m], color="none", markerfacecolor=COL[m], markeredgecolor="white", markersize=6, label=m) for m in MODELS]
    handles += [
        Line2D([], [], marker="o", color="none", markerfacecolor="#6f6f6c", markeredgecolor="white", markersize=5.5, label="deed unmortgaged"),
        Line2D([], [], marker="o", color="none", markerfacecolor="white", markeredgecolor="#6f6f6c", markersize=5.5, label="deed mortgaged"),
        Line2D([], [], color=INK, lw=1.6, label="median"),
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.07), ncol=7, frameon=False, handletextpad=0.25, columnspacing=1.0)
    fig.subplots_adjust(wspace=0.06)
    save(fig, "fig_prices")


# ---------------------------------------------------------------------------
def fig_liquidity():
    B = load("a6_bargaining.json")
    dy = load("a6_dyads.json")
    hc = B["holder_cash"]["author_only_by_holder_cash"]
    strata = ["<100", "100-299", "300-599", "600+"]
    labels = ["under $100", "$100–299", "$300–599", "$600 or more"]
    fig, axes = plt.subplots(1, 2, figsize=(6.7, 2.9), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    for i, s in enumerate(strata):
        d = hc[s]
        n = d["n"]
        parts = [("reject", d["reject"], SEQ[2]), ("counter", d["counter"], SEQ[1]), ("accept", d["accept"], SEQ[0])]
        bottom = 0.0
        for name, v, c in parts:
            h = v / n
            ax.bar(i, max(h - 0.008, 0), bottom=bottom + 0.004, width=0.52, color=c, zorder=3)
            if h > 0.09:
                ax.text(i, bottom + h / 2, f"{100 * h:.0f}%", ha="center", va="center", fontsize=7.2, color="white" if c != SEQ[0] else INK)
            bottom += h
        ax.text(i, 1.012, f"n = {n}", ha="center", va="bottom", fontsize=7, color="#52514e")
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.075)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("holder's cash when the request arrives")
    ax.set_ylabel("share of responses")
    ax.set_title("(a) Holders' responses to completion requests", loc="left", pad=22)
    ax.tick_params(length=0)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=l) for c, l in zip(SEQ[::-1], ["reject", "counter", "accept"])]
    ax.legend(handles=handles, frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(-0.02, 1.035), handlelength=1.0, columnspacing=1.0, borderaxespad=0)

    ax = axes[1]
    later = [d for d in dy if d["settled"] and d["one_sided"] and d["settled_on_later_turn"] and d["holder_declined_on_earlier_turn"]]
    for d in later:
        m = d["holder_model"]
        ax.plot([0, 1], [d["first_holder_decline_cash"], d["settle_holder_cash"]], color=COL[m], lw=1.1, alpha=0.75, zorder=2)
        for x, y in ((0, d["first_holder_decline_cash"]), (1, d["settle_holder_cash"])):
            ax.plot(x, y, MARK[m], markersize=5, markerfacecolor=COL[m], markeredgecolor="white", markeredgewidth=0.8, zorder=3)
    m0 = S.median(d["first_holder_decline_cash"] for d in later)
    m1 = S.median(d["settle_holder_cash"] for d in later)
    ax.plot([0, 1], [m0, m1], color=INK, lw=2.2, zorder=4, solid_capstyle="round")
    ax.plot([0, 1], [m0, m1], "o", markersize=4.5, markerfacecolor=INK, markeredgecolor="white", markeredgewidth=0.8, zorder=5)
    mf = lambda v: f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"
    ax.annotate(f"median ${mf(m1)}", (1, m1), xytext=(9, 0), textcoords="offset points", ha="left", va="center", fontsize=7.2)
    ax.annotate(f"median ${mf(m0)}", (0, m0), xytext=(-9, 10), textcoords="offset points", ha="right", va="center", fontsize=7.2,
                bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none"})
    ax.set_xlim(-0.75, 2.05)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["first refusal", "sale"])
    ax.set_ylim(-40, 1420)
    ax.set_yticks([0, 250, 500, 750, 1000, 1250])
    ax.set_yticklabels(["$0", "$250", "$500", "$750", "$1,000", "$1,250"])
    ax.grid(axis="y", zorder=0)
    ax.set_ylabel("holder's cash")
    ax.set_title(f"(b) Holder's cash in {len(later)} sales that followed a refusal", loc="left", pad=22)
    ax.tick_params(length=0)
    system_legend(ax, loc="upper right", ncol=1, bbox_to_anchor=(1.03, 1.0), title="holder", title_fontsize=7.5, labelspacing=0.5)
    fig.subplots_adjust(wspace=0.36)
    save(fig, "fig_liquidity")


# ---------------------------------------------------------------------------
def fig_conversion():
    C = load("a7_conversion.json")["trade_groups"]["by_model"]
    fig, axes = plt.subplots(1, 3, figsize=(6.7, 2.35))
    x = np.arange(4)
    ax = axes[0]
    first = [C[m]["built_first_window_inherited"] for m in MODELS]
    later = [C[m]["ever_built"] - C[m]["built_first_window_inherited"] for m in MODELS]
    never = [C[m]["groups"] - C[m]["ever_built"] for m in MODELS]
    bottom = np.zeros(4)
    for vals, c, lab in ((first, SEQ[2], "first management turn"), (later, SEQ[1], "later"), (never, SEQ[0], "never")):
        for i, v in enumerate(vals):
            if v:
                ax.bar(i, v - 0.12, bottom=bottom[i] + 0.06, width=0.5, color=c, zorder=3)
                ax.text(i, bottom[i] + v / 2, str(v), ha="center", va="center", fontsize=7, color="white" if c != SEQ[0] else INK)
        bottom += np.array(vals)
    ax.set_title("(a) When the group was built on", loc="left", pad=20)
    ax.set_ylabel("trade-completed groups")
    ax.set_ylim(0, 19.5)
    ax.set_yticks([0, 5, 10, 15])
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=l) for c, l in zip(SEQ[::-1], ["first management turn", "later", "never"])]
    ax.legend(handles=handles, frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(-0.22, 0.98), handlelength=0.9, columnspacing=0.7, handletextpad=0.3, fontsize=6.8)
    ax = axes[1]
    v = [C[m]["landings_per_100_group_turns"] for m in MODELS]
    for i, m in enumerate(MODELS):
        ax.bar(i, v[i], width=0.5, color=COL[m], zorder=3)
        ax.text(i, v[i] + 0.12, f"{v[i]:.1f}", ha="center", va="bottom", fontsize=7.2)
    ax.set_title("(b) Exposure", loc="left", pad=20)
    ax.set_ylabel("opponent landings per\n100 turns of ownership")
    ax.set_ylim(0, 6)
    ax = axes[2]
    v = [C[m]["rent_per_landing"] for m in MODELS]
    for i, m in enumerate(MODELS):
        ax.bar(i, v[i], width=0.5, color=COL[m], zorder=3)
        ax.text(i, v[i] + 9, f"${v[i]:.0f}", ha="center", va="bottom", fontsize=7.2)
    ax.set_title("(c) Yield", loc="left", pad=20)
    ax.set_ylabel("rent received per\nopponent landing")
    ax.set_ylim(0, 450)
    ax.set_yticks([0, 100, 200, 300, 400])
    ax.set_yticklabels(["$0", "$100", "$200", "$300", "$400"])
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(MODELS)
        ax.tick_params(length=0)
        ax.grid(axis="y", zorder=0)
    fig.subplots_adjust(wspace=0.62)
    save(fig, "fig_conversion")


# ---------------------------------------------------------------------------
def fig_debt():
    eps = load("a4_debt_episodes.json")
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    lo, hi = 20, 6000
    ax.plot([lo, hi], [lo, hi], color=MUTED, lw=0.8, zorder=1)
    ax.fill_between([lo, hi], [lo, hi], [lo, lo], color="#f1f0ec", zorder=0, lw=0)
    paid = [e for e in eps if e["inherited_class"] == "paid"]
    below = [e for e in eps if e["inherited_class"] == "below_bound"]
    payable = [e for e in eps if e["inherited_class"] == "payable_witness"]
    lock = [e for e in eps if e["inherited_class"] == "menu_blocked"]
    ax.plot([e["debt"] for e in paid], [e["bound_U"] for e in paid], "o", markersize=4.2, markerfacecolor="#8fa3bd", markeredgecolor="white", markeredgewidth=0.5, zorder=3, label=f"paid ({len(paid)})")
    ax.plot([e["debt"] for e in below], [e["bound_U"] for e in below], "x", markersize=4.6, color=INK, markeredgewidth=1.0, zorder=3, label=f"eliminated, debt above the bound ({len(below)})")
    ax.plot([e["debt"] for e in payable], [e["bound_U"] for e in payable], "D", markersize=5.5, markerfacecolor="#d03b3b", markeredgecolor="white", markeredgewidth=0.7, zorder=4, label=f"eliminated with a payment route ({len(payable)})")
    ax.plot([e["debt"] for e in lock], [e["bound_U"] for e in lock], "s", markersize=5.5, markerfacecolor="white", markeredgecolor="#d03b3b", markeredgewidth=1.2, zorder=4, label=f"eliminated, sale not on the menu ({len(lock)})")
    import matplotlib.patheffects as pe
    marked = sorted(payable, key=lambda e: e["debt"]) + lock
    for i, e in enumerate(marked, 1):
        ax.annotate(str(i), (e["debt"], e["bound_U"]), xytext=(-7, 5), textcoords="offset points", fontsize=7.4, fontweight="bold",
                    color=INK, ha="center", va="center", path_effects=[pe.withStroke(linewidth=2.2, foreground="white")], zorder=6)
    key = "   ".join(f"{i} = G{e['game']} {e['model']}" for i, e in enumerate(marked, 1))
    ax.text(1.02, 0.60, key.replace("   ", "\n"), transform=ax.transAxes, fontsize=7.2, color="#52514e", va="top", linespacing=1.5)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ticks = [25, 50, 100, 250, 500, 1000, 2500, 5000]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels([f"${t:,}" for t in ticks])
    ax.set_yticklabels([f"${t:,}" for t in ticks])
    ax.minorticks_off()
    ax.set_xlabel("debt at the first liquidation menu")
    ax.set_ylabel("own-asset bound U\n(cash + building salvage + mortgage value)")
    ax.text(2600, 42, "debt exceeds\nthe bound", fontsize=7, color="#52514e", ha="center")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.02, 1.0), handletextpad=0.3, borderaxespad=0)
    ax.tick_params(length=2)
    save(fig, "fig_debt")


# ---------------------------------------------------------------------------
def fig_estates():
    rows = load("a5_pre_estate.json")
    rows = sorted(rows, key=lambda r: -r["creditor_asset_share"])
    fig, ax = plt.subplots(figsize=(5.2, 4.3))
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i
        tot = sum(p["assets"] for p in r["positions"].values())
        ax.plot([0, 0.7], [y, y], color="#eceae5", lw=0.6, zorder=0)
        for m, p in r["positions"].items():
            sh = p["assets"] / tot
            if m == r["debtor_model"]:
                ax.plot(sh, y, "x", color=MUTED, markersize=4.5, markeredgewidth=1.0, zorder=2)
            elif m == r["creditor_model"]:
                ax.plot(sh, y, "D", markersize=5.6, markerfacecolor=INK, markeredgecolor="white", markeredgewidth=0.7, zorder=4)
            else:
                ax.plot(sh, y, "o", markersize=4.2, markerfacecolor="#b9c4d2", markeredgecolor="white", markeredgewidth=0.5, zorder=3)
            if m == r["winner_model"]:
                ax.plot(sh, y, "o", markersize=10, markerfacecolor="none", markeredgecolor="#d9622b", markeredgewidth=1.1, zorder=5)
        ax.text(-0.012, y, f"G{r['game']}", ha="right", va="center", fontsize=7, color="#52514e")
    ax.set_xlim(0, 0.68)
    ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_yticks([])
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    ax.set_xticklabels(["0", "10%", "20%", "30%", "40%", "50%", "60%"])
    ax.axvline(0.25, color=MUTED, lw=0.6, zorder=1)
    ax.text(0.25, len(rows) - 0.15, "equal share", fontsize=6.8, color="#52514e", ha="center", va="bottom")
    ax.set_xlabel("share of the four players' assets just before the first elimination")
    ax.spines["left"].set_visible(False)
    handles = [
        Line2D([], [], marker="D", color="none", markerfacecolor=INK, markeredgecolor="white", markersize=6, label="first creditor"),
        Line2D([], [], marker="o", color="none", markerfacecolor="none", markeredgecolor="#d9622b", markeredgewidth=1.1, markersize=9, label="eventual winner"),
        Line2D([], [], marker="x", color=MUTED, linestyle="none", markersize=5, markeredgewidth=1.0, label="first player eliminated"),
        Line2D([], [], marker="o", color="none", markerfacecolor="#b9c4d2", markeredgecolor="white", markersize=5.5, label="other player"),
    ]
    ax.legend(handles=handles, frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1.0), borderaxespad=0, handletextpad=0.3, labelspacing=0.7)
    ax.tick_params(length=2)
    save(fig, "fig_estates")


# ---------------------------------------------------------------------------
def fig_timeline():
    rows = load("a7_trade_groups.json")
    eps = {(e["game"], e["player"], e["group"]): e for e in load("a3_group_episodes.json") if e["route"] == "trade"}
    land = load("a7_landings.json") if (DATA / "a7_landings.json").exists() else {}
    CLIP = 180
    fig, axes = plt.subplots(4, 1, figsize=(6.7, 8.3), sharex=True, gridspec_kw={"height_ratios": [17, 18, 15, 13], "hspace": 0.16})
    for ax, m in zip(axes, MODELS):
        xs = sorted([r for r in rows if r["model"] == m], key=lambda r: (-(r["first_build_turn"] is not None), r["turns_to_first_build"] if r["turns_to_first_build"] is not None else 999, -r["duration_turns"]))
        for i, r in enumerate(xs):
            y = len(xs) - 1 - i
            dur = min(r["duration_turns"], CLIP)
            ax.plot([0, dur], [y, y], color="#d9dde3", lw=3.4, solid_capstyle="butt", zorder=1)
            if r["turns_to_first_build"] is not None:
                b = min(r["turns_to_first_build"], CLIP)
                ax.plot([b, dur], [y, y], color=COL[m], lw=3.4, solid_capstyle="butt", alpha=0.55, zorder=2)
            key = f"{r['game']}|{r['player']}|{r['group']}"
            for t, amt, due in land.get(key, []):
                if t > CLIP:
                    continue
                if amt > 0:
                    ax.plot(t, y, "o", markersize=2.6 + 3.6 * min(amt, 1500) ** 0.5 / 1500 ** 0.5, markerfacecolor=INK, markeredgecolor="white", markeredgewidth=0.4, zorder=4)
                elif due > 0:
                    ax.plot(t, y, "o", markersize=4.2, markerfacecolor="white", markeredgecolor="#d03b3b", markeredgewidth=0.9, zorder=4)
                else:
                    ax.plot(t, y, "|", markersize=5, color=MUTED, markeredgewidth=0.8, zorder=3)
            if r["duration_turns"] > CLIP:
                ax.annotate("", xy=(CLIP + 5, y), xytext=(CLIP, y), arrowprops={"arrowstyle": "-|>", "color": MUTED, "lw": 0.7})
            ax.text(-3, y, f"G{r['game']} {r['group'].replace('_', ' ').title()}", ha="right", va="center", fontsize=6.3, color="#52514e")
            end = {"bankrupt": "bankrupt", "game_end": "won" if r["winner"] else "game end", "traded_away": "traded"}[r["end_reason"]]
            if r["duration_turns"] <= CLIP:
                ax.text(dur + 2.5, y, end, ha="left", va="center", fontsize=5.8, color=MUTED)
        ax.set_ylim(-0.7, len(xs) - 0.3)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_title(f"{m}  ({len(xs)} groups)", loc="left", pad=2, fontsize=8.5)
        ax.set_xlim(0, CLIP + 8)
        ax.grid(axis="x", zorder=0)
        ax.tick_params(length=2)
    axes[-1].set_xlabel("turns since the trade that completed the group")
    handles = [
        Line2D([], [], color="#d9dde3", lw=3.4, label="owned, no buildings"),
        Line2D([], [], color="#6f6f6c", lw=3.4, alpha=0.55, label="owned, built on (system color)"),
        Line2D([], [], marker="o", color="none", markerfacecolor=INK, markeredgecolor="white", markersize=5.5, label="opponent lands and pays (area ∝ rent)"),
        Line2D([], [], marker="o", color="none", markerfacecolor="white", markeredgecolor="#d03b3b", markeredgewidth=0.9, markersize=4.6, label="lands, rent not paid in full"),
        Line2D([], [], marker="|", color=MUTED, linestyle="none", markersize=6, label="lands on a mortgaged deed"),
    ]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.905), ncol=3, frameon=False, handletextpad=0.6, columnspacing=1.4, fontsize=7, handlelength=1.6)
    save(fig, "fig_timeline")


if __name__ == "__main__":
    fig_prices()
    fig_liquidity()
    fig_conversion()
    fig_debt()
    fig_estates()
    fig_timeline()
    print("figures written to", ASSETS)
