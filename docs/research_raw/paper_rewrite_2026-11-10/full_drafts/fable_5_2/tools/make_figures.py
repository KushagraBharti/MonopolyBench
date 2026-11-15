#!/usr/bin/env python3
"""Draw this draft's figures from retained ledgers and this draft's re-tabulations (no engine or model call).

Run with the repository virtualenv:  <repo>/python/.venv/bin/python tools/make_figures.py
Inputs : data/offer_retabulation.json, data/economy_retabulation.json (this draft), ../../data/t06_eliminations.json,
         ../../data/agenda_offers.json
Outputs: figures/fig_bargaining.{pdf,png}, fig_conversion.{pdf,png}, fig_financing.{pdf,png}, fig_routes.{pdf,png},
         figures/figure_manifest.json
Palette: categorical slots 1-5 of the validated reference palette (blue, orange, aqua, yellow, magenta), fixed order,
checked with the dataviz validator on a white surface (adjacent CVD and normal-vision floors pass). Counts are printed
on the marks and repeated in the manuscript tables, which satisfies the sub-3:1 contrast relief rule.
"""
import json, pathlib, hashlib, statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
HERE = pathlib.Path(__file__).resolve().parent.parent
RW = HERE.parent.parent
FIG = HERE / "figures"; FIG.mkdir(exist_ok=True)
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
INK, INK2, MUTED, GRID, NEUTRAL = "#0b0b0b", "#52514e", "#8a8983", "#e4e3df", "#a9a8a2"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5, "xtick.labelsize": 8,
                     "ytick.labelsize": 8.5, "pdf.fonttype": 42, "axes.edgecolor": INK2, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK, "text.color": INK, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.0})
manifest = {"inputs": {}, "outputs": {}}
def read(p):
    p = pathlib.Path(p); manifest["inputs"][str(p.resolve().relative_to(RW.resolve()))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return json.loads(p.read_text())
def save(fig, name):
    for ext in ("pdf", "png"):
        p = FIG / f"{name}.{ext}"
        fig.savefig(p, dpi=220, bbox_inches="tight", facecolor="white")
        manifest["outputs"][p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    plt.close(fig)
def clean(ax, left=False):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    if not left: ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
offer = read(HERE / "data" / "offer_retabulation.json")
econ = read(HERE / "data" / "economy_retabulation.json")
elims = read(RW / "data" / "t06_eliminations.json")
offers = read(RW / "data" / "agenda_offers.json")

# ---------------- Figure 1: bargaining ----------------
cells = [("author_only", "Writer's group only"), ("recipient_only", "Recipient's group only"), ("both", "Both parties' groups"), ("neither", "No group")]
fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.55), gridspec_kw={"width_ratios": [1.25, 1], "wspace": 0.12})
ys = list(range(len(cells)))[::-1]
for y, (k, lab) in zip(ys, cells):
    t = offer["cells_legal"][k]; n = t["n"]; left = 0
    for key, col, tc in (("accept", BLUE, "white"), ("counter", ORANGE, "white"), ("reject", AQUA, INK)):
        w = 100 * t[key] / n
        a.barh(y, w, left=left, height=0.56, color=col, edgecolor="white", linewidth=1.6)
        if w > 5: a.text(left + w / 2, y, str(t[key]), ha="center", va="center", color=tc, fontsize=7.6)
        left += w
    a.text(101.5, y, f"n = {n}", va="center", fontsize=7.5, color=INK2)
a.set_yticks(ys); a.set_yticklabels([lab for _, lab in cells]); a.set_xlim(0, 116); a.set_xticks([0, 25, 50, 75, 100]); a.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
a.set_title("Response to the offer", loc="left", color=INK); a.set_xlabel("Share of acceptance-legal offers"); clean(a)
a.legend(handles=[Patch(color=BLUE, label="Accept"), Patch(color=ORANGE, label="Counter"), Patch(color=AQUA, label="Reject")], loc="upper center", bbox_to_anchor=(0.43, -0.27), ncol=3, frameon=False, fontsize=8, handlelength=1.2, columnspacing=1.4)
legal = [r for r in offers if r["accept_available"]]
for y, (k, lab) in zip(ys, cells):
    net = sorted(r["net_cash_author_to_recipient"] for r in legal if r["completion_cell"] == k)
    q1, med, q3 = st.quantiles(net, n=4)[0], st.median(net), st.quantiles(net, n=4)[2]
    assert med == offer["cells_legal"][k]["median_net_cash_to_recipient"]
    b.plot([q1, q3], [y, y], color=NEUTRAL, lw=2.2, solid_capstyle="round", zorder=2)
    b.plot([med], [y], marker="o", ms=6.5, color=INK2, markeredgecolor="white", markeredgewidth=1.4, zorder=3)
    b.text(med, y + 0.27, f"{'+' if med > 0 else '−' if med < 0 else ''}${abs(med):.0f}", ha="center", va="bottom", fontsize=8, color=INK)
b.axvline(0, color=INK2, lw=0.7, zorder=1)
b.set_yticks(ys); b.set_yticklabels([]); b.set_ylim(-0.6, len(cells) - 0.35); a.set_ylim(-0.6, len(cells) - 0.35)
b.set_xlim(-640, 420); b.set_xticks([-600, -400, -200, 0, 200, 400]); b.set_xticklabels(["−600", "−400", "−200", "0", "200", "400"])
b.set_title("Net cash offered, writer to recipient", loc="left", color=INK, x=0.02); b.set_xlabel("Game dollars: median and interquartile range"); clean(b)
b.text(-630, -0.52, "recipient pays", fontsize=7.5, color=INK2, ha="left", va="bottom"); b.text(410, -0.52, "writer pays", fontsize=7.5, color=INK2, ha="right", va="bottom")
b.xaxis.grid(True, color=GRID, lw=0.6); b.set_axisbelow(True)
save(fig, "fig_bargaining")

# ---------------- Figure 2: from completion to development ----------------
M = ["Sol", "Gemini", "Opus", "Grok"]
cats = [("built", "Built", BLUE, "white"), ("never_legal_in_window", "Not legal to build in the window", ORANGE, "white"), ("default", "Engine default", AQUA, INK),
        ("received_conflict", "Channel conflict", YELLOW, INK), ("valid_end", "Valid end of turn", MAGENTA, INK)]
fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.45), gridspec_kw={"width_ratios": [1.35, 1], "wspace": 0.14})
ys = list(range(len(M)))[::-1]
tot = 0
for y, m in zip(ys, M):
    t = econ["trade_groups_by_configuration"][m]; u = t["unbuilt_causes"]
    vals = {"built": t["built_first_window"], "never_legal_in_window": u.get("never_legal_in_window", 0), "default": u.get("default_after_refusal", 0) + u.get("default_other", 0),
            "received_conflict": u.get("received_conflict", 0), "valid_end": u.get("valid_end", 0)}
    assert sum(vals.values()) == t["groups"]; tot += t["groups"]
    left = 0
    for key, lab, col, tc in cats:
        v = vals[key]
        if not v: continue
        a.barh(y, v, left=left, height=0.56, color=col, edgecolor="white", linewidth=1.6)
        a.text(left + v / 2, y, str(v), ha="center", va="center", color=tc, fontsize=8)
        left += v
    a.text(left + 0.35, y, f"{t['built_first_window']} of {t['groups']} built", va="center", fontsize=7.5, color=INK2)
assert tot == 63
a.set_yticks(ys); a.set_yticklabels(M); a.set_xlim(0, 24.5); a.set_xticks([0, 5, 10, 15]); a.set_xlabel("Trade-completed color groups"); clean(a)
a.set_title("First management window after the trade", loc="left", color=INK)
fig.legend(handles=[Patch(color=c, label=l) for _, l, c, _ in cats], loc="lower center", bbox_to_anchor=(0.5, -0.17), ncol=5, frameon=False, fontsize=7.6, handlelength=1.2, columnspacing=1.2)
for y, m in zip(ys, M):
    v = econ["trade_groups_by_configuration"][m]["rent_until_loss_or_end"]
    b.barh(y, v, height=0.56, color=BLUE, edgecolor="white", linewidth=1.6)
    b.text(v + 500, y, f"${v:,}", va="center", fontsize=8, color=INK)
b.set_yticks(ys); b.set_yticklabels([]); b.set_xlim(0, 34000); b.set_xticks([0, 10000, 20000]); b.set_xticklabels(["0", "10,000", "20,000"])
b.set_xlabel("Game dollars"); b.set_title("Rent paid on those groups afterwards", loc="left", color=INK); clean(b)
save(fig, "fig_conversion")

# ---------------- Figure 3: debt against the generous own-asset bound ----------------
fig, ax = plt.subplots(figsize=(6.3, 3.6))
ax.plot([0, 2100], [0, 2100], color=NEUTRAL, lw=0.8, zorder=1)
ax.text(1870, 1930, "bound = debt", rotation=40.5, fontsize=7.5, color=INK2, ha="center", va="center")
n_below = 0
for r in elims:
    mk = "o" if r["elimination"] == "declared" else "s"
    if r["full"] < r["owed"]:
        n_below += 1
        ax.scatter(r["full"], r["owed"], marker=mk, s=30, color=NEUTRAL, edgecolor="white", linewidth=0.9, zorder=2)
    elif r["avoidable"]:
        ax.scatter(r["full"], r["owed"], marker=mk, s=44, color=ORANGE, edgecolor="white", linewidth=0.9, zorder=4)
    else:  # nominal bound above debt but no legal access (G7)
        ax.plot([r["accessible"], r["full"]], [r["owed"], r["owed"]], color=BLUE, lw=2, zorder=3)
        ax.scatter(r["full"], r["owed"], marker="s", s=44, facecolor="white", edgecolor=BLUE, linewidth=1.3, zorder=4)
        ax.scatter(r["accessible"], r["owed"], marker="s", s=44, color=BLUE, edgecolor="white", linewidth=0.9, zorder=4)
assert n_below == 56
notes = {(12, "Sol"): ("G12 Sol: payable", (1150, 380)), (12, "Grok"): ("G12 Grok: payable", (1050, 170)), (17, "Gemini"): ("G17 Gemini: payable", (1330, 560)),
         (7, "Opus"): ("G7 Opus: $1,310 nominal,\n$440 reachable (hotel lock)", (1420, 900))}
for r in elims:
    k = (r["game"], r["model"])
    if r["full"] >= r["owed"] and k in notes:
        lab, xy = notes[k]
        ax.annotate(lab, (r["full"], r["owed"]), xytext=xy, fontsize=7.8, color=INK, va="center", arrowprops={"arrowstyle": "-", "lw": 0.6, "color": INK2}, zorder=5)
ax.set_xlim(-30, 2150); ax.set_ylim(-30, 2100); ax.set_xlabel("Generous own-asset upper bound (game dollars)"); ax.set_ylabel("Debt owed at elimination (game dollars)")
ax.tick_params(axis="y", length=2.5, width=0.6, colors=INK2); clean(ax, left=True)
ax.legend(handles=[Line2D([], [], marker="o", ls="", color=NEUTRAL, markersize=5.5, label="Bound below debt: declared (53)"), Line2D([], [], marker="s", ls="", color=NEUTRAL, markersize=5.5, label="Bound below debt: automatic (3)"),
                   Line2D([], [], marker="o", ls="", color=ORANGE, markersize=6.5, label="Legal payment sequence exists (3)"), Line2D([], [], marker="s", ls="", color=BLUE, markersize=6.5, label="Bound above debt, not reachable (1)")],
          loc="upper left", frameon=False, fontsize=7.8, handletextpad=0.3)
assert sum(1 for r in elims if r["full"] < r["owed"] and r["elimination"] == "declared") == 53
assert sum(1 for r in elims if r["full"] < r["owed"] and r["elimination"] == "automatic") == 3
save(fig, "fig_financing")

# ---------------- Figure 4: how complete groups were assembled ----------------
ep = econ["live_by_route"]; term = econ["episodes"]["by_route_access"]["creditor_inheritance|no_access_before_game_end"]
rows = [("Trade", ep["trade"]["by_eventual_winner"], ep["trade"]["n"]), ("Estate before the final elimination", ep["creditor_inheritance"]["by_eventual_winner"], ep["creditor_inheritance"]["n"]),
        ("Direct purchase", ep["direct_purchase"]["by_eventual_winner"], ep["direct_purchase"]["n"]), ("Auction", ep["auction"]["by_eventual_winner"], ep["auction"]["n"]),
        ("Estate at the final elimination", term, term)]
assert sum(r[2] for r in rows) == 209
fig, ax = plt.subplots(figsize=(6.3, 2.35))
ys = list(range(len(rows)))[::-1]
for y, (lab, w, n) in zip(ys, rows):
    ax.barh(y, w, height=0.56, color=BLUE, edgecolor="white", linewidth=1.6)
    if w >= 4: ax.text(w / 2, y, str(w), ha="center", va="center", color="white", fontsize=8)
    if n - w:
        ax.barh(y, n - w, left=w, height=0.56, color=ORANGE, edgecolor="white", linewidth=1.6)
        if n - w >= 4: ax.text(w + (n - w) / 2, y, str(n - w), ha="center", va="center", color="white", fontsize=8)
    extra = "" if w >= 4 and (n - w >= 4 or n == w) else f"  ({w} + {n - w})"
    ax.text(n + 1.2, y, f"{n}{extra}", va="center", fontsize=8, color=INK2)
ax.set_yticks(ys); ax.set_yticklabels([r[0] for r in rows]); ax.set_xlim(0, 78); ax.set_xlabel("Completed-group episodes (209 in twenty games)"); clean(ax)
ax.legend(handles=[Patch(color=BLUE, label="Completed by the eventual winner"), Patch(color=ORANGE, label="Completed by a player later eliminated")], loc="upper center", bbox_to_anchor=(0.4, -0.3), ncol=2, frameon=False, fontsize=8, handlelength=1.2)
save(fig, "fig_routes")
(FIG / "figure_manifest.json").write_text(json.dumps(manifest, indent=1))
print(json.dumps(manifest["outputs"], indent=1))
