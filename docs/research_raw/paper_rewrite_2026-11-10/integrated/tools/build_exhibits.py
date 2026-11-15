"""Build document exhibits from retained ledgers only. No engine execution."""

import hashlib
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

HERE = Path(__file__).resolve().parents[1]
BASE = HERE.parent
sources = {}


def load(name):
    source = BASE / "data" / name
    raw = source.read_bytes()
    (HERE / "data" / name).write_bytes(raw)
    sources[name] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


windows = load("first_management_windows.json")["rows"]
entry = load("t09_entry_nonbuild_records.json")
groups = load("t03_trade_groups.json")
elims = load("t06_eliminations.json")
cohort = load("t01_cohort.json")
offers = load("agenda_offers.json")
cause = Counter(r["cause"] for r in windows)
whole = [cause["built"], cause["never_legal_in_window"],
         cause["default_after_refusal"] + cause["default_other"],
         cause["received_conflict"], cause["valid_end"]]
assert whole == [43, 9, 4, 4, 3]
assert sum(r["entry_eligible"] for r in groups) == 42
assert sum(r["entry_eligible_built"] for r in groups) == 34
assert Counter(r["category"] for r in entry) == {
    "engine_default": 3, "received_content_tool_conflict": 3,
    "consistent_end_with_stated_reserve": 2,
}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "pdf.fonttype": 42, "axes.spines.top": False,
                     "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.1), gridspec_kw={"wspace": .75})
panels = [(axes[0], whole, ["Built", "No option on\ncompleted group", "Engine default", "Received conflict", "Other valid END"], "First windows (63 groups)"),
          (axes[1], [34, 3, 3, 2], ["Built", "Engine default", "Received conflict", "Stated hold"], "Buildable on entry (42 groups)")]
for ax, values, labels, title in panels:
    bars = ax.barh(labels, values, color=["#24638A"] + ["#9DA5AC"] * (len(values) - 1), height=.65)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values) * 1.15)
    ax.set_xlabel("Color-group episodes")
    ax.set_title(title, fontsize=10, pad=12)
    ax.bar_label(bars, padding=3)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
fig.subplots_adjust(left=.2, right=.99, bottom=.17, top=.85)
for ext in ["pdf", "png"]:
    fig.savefig(HERE / "assets" / f"execution.{ext}", dpi=200)
plt.close(fig)

assert len(elims) == 60
assert sum(r["full"] < r["owed"] for r in elims) == 56
assert sum(r["avoidable"] for r in elims) == 3
assert Counter(r["elimination"] for r in elims) == {"declared": 56, "automatic": 4}
fig, ax = plt.subplots(figsize=(6.8, 4.65))
ax.plot([0, 2100], [0, 2100], color="#A9AFB4", linewidth=.9, zorder=0)
for r in elims:
    positive = r["avoidable"]
    lock = r["game"] == 7 and r["decision"] == "dec-000339"
    ax.scatter(r["full"], r["owed"], marker="s" if r["elimination"] == "automatic" else "o",
               s=40 if positive or lock else 20, facecolor="white" if lock else ("#B64D21" if positive else "#8A9299"),
               edgecolor="#24638A" if lock else ("#B64D21" if positive else "white"), linewidth=.7, zorder=4)
    if lock:
        ax.plot([440, 1310], [750, 750], color="#24638A", linewidth=1.3, zorder=2)
        ax.scatter(440, 750, marker="s", s=40, color="#24638A", zorder=5)
        ax.annotate("G7 Opus: 440 accessible, 1,310 nominal", xy=(1120, 750), xytext=(900, 1000),
                    fontsize=8.5, arrowprops={"arrowstyle": "-", "color": "#24638A"})
    if positive:
        locations = {(12, "Sol"): (1030, 420), (12, "Grok"): (800, 110), (17, "Gemini"): (1320, 630)}
        ax.annotate(f"G{r['game']} {r['model']}: payable", xy=(r["full"], r["owed"]),
                    xytext=locations[(r["game"], r["model"])], fontsize=8.5,
                    arrowprops={"arrowstyle": "-", "color": "#B64D21"})
ax.set(xlim=(0, 2100), ylim=(0, 2100), xlabel="Generous own-asset bound (game dollars)", ylabel="Current debt (game dollars)")
ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
ax.text(30, 2000, "56 debts exceed the bound\n3 legal payment witnesses\n1 hotel lock", va="top", fontsize=9)
fig.tight_layout()
for ext in ["pdf", "png"]:
    fig.savefig(HERE / "assets" / f"finance.{ext}", dpi=200)
plt.close(fig)

def tex_escape(text):
    return str(text).replace("_", r"\_")


rows = []
for r in cohort:
    rows.append(f"{r['game']} & {(r['game']-1)//4+1} & {r['rotation']} & {r['turns']} & {r['winner']} & {r['winner_seat']} \\")
(HERE / "sections" / "cohort_rows.tex").write_text("\\newcommand{\\CohortRows}{%\n" + "\n".join(s + "\\" for s in rows) + "\n}\n")
rows = []
for r in sorted(elims, key=lambda r: (r["game"], r["elimination_event_seq"])):
    decision = int(r["decision"].split("-")[1])
    result = "Payable" if r["avoidable"] else ("Hotel lock" if r["full"] >= r["owed"] else "Below debt")
    rows.append(f"{r['game']} & {decision} & {r['model']} & {r['elimination']} & {r['cash']:,} & {r['owed']:,} & {r['full']:,} & {result} \\")
(HERE / "sections" / "elimination_rows.tex").write_text("\\newcommand{\\EliminationRows}{%\n" + "\n".join(s + "\\" for s in rows) + "\n}\n")
rows = []
for model in ["Sol", "Gemini", "Opus", "Grok"]:
    for cell, label in [("author_only", "Author only"), ("recipient_only", "Recipient only"), ("both", "Both"), ("neither", "Neither")]:
        rr = [r for r in offers if r["accept_available"] and r["recipient_model"] == model and r["completion_cell"] == cell]
        c = Counter(r["response"] for r in rr)
        rows.append(f"{model} & {label} & {len(rr)} & {c['accept_trade']} & {c['counter_trade']} & {c['reject_trade']} \\")
(HERE / "sections" / "response_rows.tex").write_text("\\newcommand{\\ResponseRows}{%\n" + "\n".join(s + "\\" for s in rows) + "\n}\n")
report = {"scope": "Retained-ledger exhibit generation; no game or engine execution", "source_sha256": sources,
          "whole_window_counts": whole, "entry_counts": [34, 3, 3, 2], "eliminations": 60,
          "original_points": {"circles": 56, "squares": 4}, "additional_reachable_endpoint": 1,
          "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(HERE / "qa" / "exhibit_checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
