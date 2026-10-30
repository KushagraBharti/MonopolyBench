"""Question-led figures from retained finite-population results."""

from pathlib import Path
import hashlib
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "xtick.labelsize": 8,
        "ytick.labelsize": 9,
        "pdf.fonttype": 42,
    }
)
manifest = {"inputs": {}, "outputs": {}}


def read(name):
    p = ROOT / "data" / name
    manifest["inputs"][str(p.relative_to(ROOT))] = hashlib.sha256(
        p.read_bytes()
    ).hexdigest()
    return json.loads(p.read_text())


def save(fig, name):
    for ext in ("pdf", "png"):
        p = ROOT / "assets" / f"{name}.{ext}"
        fig.savefig(p, dpi=220, bbox_inches="tight", facecolor="white")
        manifest["outputs"][str(p.relative_to(ROOT))] = hashlib.sha256(
            p.read_bytes()
        ).hexdigest()
    plt.close(fig)


n = read("agenda_negotiation.json")
rows = [
    r
    for r in n["completion_response_table"]
    if r["population"] == "acceptance_available"
]
assert sum(r["offers"] for r in rows) == 918
assert sum(r["accept_trade"] for r in rows) == 113
labels = {
    "neither": "Neither party",
    "author_only": "Offer author only",
    "recipient_only": "Recipient only",
    "both": "Both parties",
}
cols = ["#286787", "#766392", "#a66a35"]
fig, ax = plt.subplots(figsize=(6.65, 3.1))
for i, r in enumerate(rows):
    left = 0
    for key, col in zip(["accept_trade", "counter_trade", "reject_trade"], cols):
        count = r[key]
        width = 100 * count / r["offers"]
        ax.barh(
            i,
            width,
            left=left,
            color=col,
            height=0.62,
            edgecolor="white",
            linewidth=0.7,
        )
        ax.text(
            left + width / 2,
            i,
            str(count),
            ha="center",
            va="center",
            color="white",
            fontsize=9,
        )
        left += width
    ax.text(101, i, f"n = {r['offers']}", va="center", fontsize=8)
ax.set_yticks(range(4), [labels[r["completion"]] for r in rows])
ax.invert_yaxis()
ax.set_xlim(0, 118)
ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
ax.set_xlabel("Response share within the offered-completion category")
ax.set_title("Which party would gain a new complete color group?", loc="left")
ax.spines[["top", "right"]].set_visible(False)
fig.legend(
    handles=[
        Patch(color=c, label=label)
        for c, label in zip(cols, ["Accept", "Counter", "Reject"])
    ],
    loc="lower center",
    ncol=3,
    frameon=False,
    bbox_to_anchor=(0.52, -0.02),
)
fig.tight_layout(rect=(0, 0.08, 1, 1))
save(fig, "offer_responses")

r = read("agenda_recurrence.json")
groups = [
    ("all_uneven", "All error episodes"),
    ("delivered_feedback", "Corrective request recorded"),
    ("first_delivered_per_player_game", "First corrective episode / player-game"),
]
fig, ax = plt.subplots(figsize=(6.65, 2.8))
for i, (key, label) in enumerate(groups):
    row = r["summary"][key]["total"]
    counts = [
        row["next_first_repeats"],
        row["next_submission_observed"] - row["next_first_repeats"],
        row["no_later_submission"],
    ]
    assert sum(counts) == row["episodes"]
    left = 0
    for count, col in zip(counts, ["#a66a35", "#286787", "#c5cbd0"]):
        ax.barh(
            i,
            count,
            left=left,
            color=col,
            height=0.62,
            edgecolor="white",
            linewidth=0.7,
        )
        if count:
            ax.text(
                left + count / 2,
                i,
                str(count),
                ha="center",
                va="center",
                color="white" if col != "#c5cbd0" else "#333333",
                fontsize=9,
            )
        left += count
ax.set_yticks(range(3), [label for _, label in groups])
ax.invert_yaxis()
ax.set_xlabel("Overlapping episode populations; counts, not causal effects")
ax.spines[["top", "right"]].set_visible(False)
fig.legend(
    handles=[
        Patch(color=c, label=label)
        for c, label in zip(
            ["#a66a35", "#286787", "#c5cbd0"],
            ["Error repeated", "No repeat at next submission", "No later submission"],
        )
    ],
    loc="lower center",
    ncol=1,
    frameon=False,
    bbox_to_anchor=(0.58, -0.22),
    fontsize=8,
)
fig.tight_layout(rect=(0, 0.13, 1, 1))
save(fig, "error_recurrence")
(ROOT / "agenda_figure_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(
    json.dumps(
        {
            "figures": 2,
            "inputs": len(manifest["inputs"]),
            "outputs": len(manifest["outputs"]),
        }
    )
)
