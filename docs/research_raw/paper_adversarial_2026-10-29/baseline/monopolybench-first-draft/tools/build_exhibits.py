"""Build manuscript-size figures and native tables from frozen audit exports."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import StrMethodFormatter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "assets"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.labelsize": 9, "axes.titlesize": 10,
                     "xtick.labelsize": 8, "ytick.labelsize": 9,
                     "pdf.fonttype": 42, "svg.fonttype": "none"})
BLUE, ORANGE, PURPLE, GRAY = "#286787", "#bd6a24", "#766392", "#92989c"
manifest = {"inputs": {}, "outputs": {}}


def read(name):
    path = DATA / (name + ".json")
    manifest["inputs"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return json.loads(path.read_text())


def save(fig, name):
    for ext in ("pdf", "png"):
        path = OUT / f"{name}.{ext}"
        fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
        manifest["outputs"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    plt.close(fig)


cohort = read("t01_cohort")
fig, ax = plt.subplots(figsize=(6.65, 3.6))
for row in cohort:
    b, r = (row["game"] - 1) // 4, row["rotation"] - 1
    ax.add_patch(Rectangle((r, b), 1, 1, facecolor="#eef3f6", edgecolor="white", lw=3))
    ax.text(r+.5, b+.42, row["winner"], ha="center", va="center", weight="bold", fontsize=10)
    ax.text(r+.5, b+.73, f'G{row["game"]:02} · seat {row["winner_seat"]}', ha="center", va="center", color="#48535b", fontsize=8.5)
ax.set(xlim=(0, 4), ylim=(5, 0), xticks=[.5,1.5,2.5,3.5],
       xticklabels=["Rotation 1", "Rotation 2", "Rotation 3", "Rotation 4"],
       yticks=[.5,1.5,2.5,3.5,4.5], yticklabels=[f"Seed block {i}" for i in range(1,6)])
ax.xaxis.tick_top(); ax.tick_params(length=0)
for s in ax.spines.values(): s.set_visible(False)
fig.tight_layout(); save(fig, "cohort")

groups = read("t03_trade_groups")
residual = read("t09_entry_nonbuild_records")
fig, axes = plt.subplots(1, 2, figsize=(6.65, 3.2), gridspec_kw={"width_ratios":[1, 1.17]})
names = [r["configuration"] for r in groups]
for i, row in enumerate(groups):
    axes[0].barh(i, row["trade_groups"], color="#e1e5e8", height=.65)
    axes[0].barh(i, row["first_management_built"], color=BLUE, height=.65)
    axes[0].text(row["trade_groups"]+.35, i, f'{row["first_management_built"]}/{row["trade_groups"]}', va="center", fontsize=8)
    cats = [r["category"] for r in residual if r["model"] == names[i]]
    counts = [row["entry_eligible_built"], sum("default" in c for c in cats),
              sum("conflict" in c for c in cats), sum("consistent_end" in c for c in cats)]
    assert sum(counts) == row["entry_eligible"], (names[i], cats, counts)
    left = 0
    for n, col in zip(counts, [BLUE, ORANGE, PURPLE, GRAY]):
        if n:
            axes[1].barh(i, n, left=left, color=col, height=.65)
            axes[1].text(left+n/2, i, str(n), va="center", ha="center", color="white", weight="bold", fontsize=8)
        left += n
for ax in axes:
    ax.set_yticks(range(4), names); ax.invert_yaxis(); ax.set_xlabel("Group episodes")
    ax.spines[["top","right"]].set_visible(False)
axes[0].set_title("All first windows (n = 63)", loc="left")
axes[0].set_xlim(0,21.2)
axes[1].set_title("Buildable on entry (n = 42)", loc="left")
axes[1].set_xlim(0,16)
fig.legend(handles=[Patch(color=c,label=l) for c,l in zip([BLUE,ORANGE,PURPLE,GRAY],
           ["Built", "Engine default", "Received conflict", "Stated hold"])],
           loc="lower center", bbox_to_anchor=(.5,-.015), ncol=2, frameon=False, fontsize=8)
fig.tight_layout(rect=(0,.13,1,1)); save(fig,"development")

units = read("t05_spending_units")
assert len(units)==103 and sum(r["spend"] for r in units)==103450
assert sum(r["paid_developed_rent_after_first_own_spend"] for r in units)==92550
fig, axes = plt.subplots(1,2,figsize=(6.65,3.6), sharex=True, sharey=True)
for ax, winner in zip(axes,[False, True]):
    rows=[r for r in units if r["winner"]==winner]
    for r in rows:
        ax.scatter(r["spend"], r["paid_developed_rent_after_first_own_spend"],
                   s=35, facecolor=BLUE if r["inherited_deed_at_first_own_spend"] else "white",
                   edgecolor=BLUE, linewidth=.8, zorder=3)
        if r["creditor_eliminations_on_group"]:
            ax.scatter(r["spend"], r["paid_developed_rent_after_first_own_spend"],
                       s=75, facecolor="none", edgecolor="#3b3b3b", linewidth=.65, zorder=2)
    zero=sum(r["paid_developed_rent_after_first_own_spend"]==0 for r in rows)
    ax.set_title(f'{"Winner" if winner else "Other players"} ({len(rows)} units)',loc="left")
    ax.text(.03,.96,f"{zero} zero-receipt units\n(points can overlap)",transform=ax.transAxes,va="top",fontsize=8)
    ax.set_xlabel("Own construction expenditure")
    ax.set_yscale("symlog",linthresh=250); ax.set_ylim(-80,10000)
    ax.set_yticks([0,250,1000,5000]); ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.spines[["top","right"]].set_visible(False)
axes[0].set_ylabel("Paid developed rent after first own spend")
fig.legend(handles=[Line2D([],[],marker="o",linestyle="",markerfacecolor=BLUE,markeredgecolor=BLUE,label="Inherited deed present"),
                    Line2D([],[],marker="o",linestyle="",markerfacecolor="white",markeredgecolor=BLUE,label="No inherited deed"),
                    Line2D([],[],marker="o",linestyle="",markerfacecolor="none",markeredgecolor="#3b3b3b",label="Outer ring: creditor elimination")],
           loc="lower center",bbox_to_anchor=(.5,-.01),ncol=2,frameon=False,fontsize=8)
fig.tight_layout(rect=(0,.16,1,1));save(fig,"spending")

elims=read("t06_eliminations")
assert len(elims)==60 and sum(r["avoidable"] for r in elims)==3
fig,ax=plt.subplots(figsize=(6.65,4.0))
for r in elims:
    col=ORANGE if r["avoidable"] else BLUE if r["accessible"]!=r["full"] else "#a1aab0"
    ax.scatter(r["accessible"],r["owed"],marker="s" if r["elimination"]=="automatic" else "o",s=40,color=col,edgecolor="white",linewidth=.5,zorder=4)
    if r["accessible"]!=r["full"]:
        ax.plot([r["accessible"],r["full"]],[r["owed"]]*2,color=BLUE,lw=2,zorder=2)
        ax.scatter(r["full"],r["owed"],s=40,facecolor="white",edgecolor=BLUE,zorder=4)
ax.plot([0,2100],[0,2100],ls="--",color="#808080",lw=.8,zorder=1)
labels={(12,"dec-000190"):(1030,350,"G12 Sol: payable"),
        (12,"dec-000249"):(950,150,"G12 Grok: payable"),
        (17,"dec-000234"):(1300,520,"G17 Gemini: payable"),
        (7,"dec-000339"):(1200,930,"G7 Opus: hotel lock\n440 accessible / 1,310 nominal")}
for r in elims:
    if (r["game"],r["decision"]) in labels:
        x,y,label=labels[(r["game"],r["decision"])]
        ax.annotate(label,(r["accessible"],r["owed"]),xytext=(x,y),fontsize=8,
                    arrowprops={"arrowstyle":"-","lw":.65,"color":"#606060"},zorder=5)
ax.set(xlim=(-30,2150),ylim=(-30,2100),xlabel="Accessible own finance (game dollars)",ylabel="Current debt (game dollars)")
ax.spines[["top","right"]].set_visible(False)
ax.legend(handles=[Line2D([],[],marker="o",linestyle="",color="#a1aab0",label="Declared (56)"),
                   Line2D([],[],marker="s",linestyle="",color="#a1aab0",label="Automatic (4)")],loc="upper left",frameon=False,fontsize=8)
fig.tight_layout();save(fig,"financing")

neg=read("t02_negotiation")
rows=[]
for r in neg:
    rows.append(f'{r["configuration"]} & {r["proposals"]} & {r["proposing_turns"]}/{r["eligible_turns"]} & {100*r["own_turn_propensity"]:.1f}\\% & {r["proposals_per_proposing_turn"]:.2f} & {r["eligible_decisions"]:,} \\\\')
table=r"""\begin{table}[t]
\centering\small
\begin{tabular}{lrrrrr}\toprule
Agent & Proposals & Proposing/eligible turns & Share & Intensity & Eligible decisions\\\midrule
"""+'\n'.join(rows)+r"""
\bottomrule\end{tabular}
\caption{Negotiation initiation. Intensity is proposals per proposing turn. The final column records a different, action-dependent denominator; it is not an additional set of independent opportunities. Rounding uses two-decimal half-even display where applicable. All conditions in Table~\ref{tab:configurations} remain in these configured-system counts.}
\label{tab:negotiation}
\end{table}
"""
(ROOT/"sections/negotiation_table.tex").write_text(table)
recovery=read("t07_build_recovery")
rows=[f'{r["configuration"]} & {r["uneven_rejection_decisions"]} & {r["some_legal_build_same_decision"]} & {r["same_purchase_multiset"]} & {r["changed_purchase_multiset"]} & {r["ended_in_default"]} \\\\' for r in recovery]
(ROOT/"sections/recovery_table.tex").write_text(r"""\begin{table}[t]
\centering\small
\begin{tabular}{lrrrrr}\toprule
Agent & Rejections & Some build & Same multiset & Changed multiset & Default\\\midrule
"""+'\n'.join(rows)+r"""
\bottomrule\end{tabular}
\caption{Decisions with an uneven-intermediate-building rejection, followed through resolution. ``Some build'' means construction was applied in the same decision, not that the requested allocation or quantity was preserved. Opus's action-only recovery has already used the retry budget. Interleaving the identical purchases executes all 61 defaulted Opus multisets in exact-prefix tests; the original encodings were invalid.}
\label{tab:recovery}
\end{table}
""")
(ROOT/"figure_manifest.json").write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({"figures":4,"tables":2,"inputs":len(manifest["inputs"])}))
