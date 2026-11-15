"""Regenerate the manuscript figure from retained data, without game execution."""
import collections
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent.parent / "data"
rows = json.loads((DATA / "first_management_windows.json").read_text())["rows"]
entry = json.loads((DATA / "t09_entry_nonbuild_records.json").read_text())
groups = json.loads((DATA / "t03_trade_groups.json").read_text())
whole = collections.Counter(r["cause"] for r in rows)
residual = collections.Counter(r["category"] for r in entry)
assert len(rows) == 63
assert sum(r["entry_eligible"] for r in groups) == 42
assert sum(r["entry_eligible_built"] for r in groups) == 34
assert (whole["built"], whole["never_legal_in_window"],
        whole["default_after_refusal"] + whole["default_other"],
        whole["received_conflict"], whole["valid_end"]) == (43, 9, 4, 4, 3)
assert (residual["engine_default"], residual["received_content_tool_conflict"],
        residual["consistent_end_with_stated_reserve"]) == (3, 3, 2)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "pdf.fonttype": 42, "axes.spines.top": False,
                     "axes.spines.right": False})
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.25), gridspec_kw={"wspace": .65})
panels = [
    (axes[0], [43, 9, 4, 4, 3],
     ["Built", "Never buildable", "Engine default", "Received conflict", "Other valid END"],
     "All first windows (63 groups)"),
    (axes[1], [34, 3, 3, 2],
     ["Built", "Engine default", "Received conflict", "Stated hold"],
     "Buildable on entry (42 groups)"),
]
for ax, values, labels, title in panels:
    colors = ["#35676B"] + ["#8F9AA4"] * (len(values)-1)
    bars = ax.barh(labels, values, color=colors, height=.65)
    ax.invert_yaxis()
    ax.set_xlim(0, max(values)*1.2)
    ax.set_xlabel("Color-group episodes")
    ax.set_title(title, fontsize=10, pad=12)
    ax.bar_label(bars, padding=4)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
fig.subplots_adjust(left=.18, right=.98, bottom=.18, top=.85)
out = HERE / "assets"
out.mkdir(exist_ok=True)
fig.savefig(out / "execution.pdf")
fig.savefig(out / "execution.png", dpi=180)
plt.close(fig)

offers = json.loads((DATA / "agenda_offers.json").read_text())
checks = {}
for cell in ["author_only", "recipient_only", "both", "neither"]:
    subset = [r for r in offers if r["accept_available"] and r["completion_cell"] == cell]
    checks[cell] = {"n": len(subset), **collections.Counter(r["response"] for r in subset)}
assert len(offers) == 920 and sum(r["accept_available"] for r in offers) == 918
assert checks["author_only"]["reject_trade"] == 159
assert checks["recipient_only"]["reject_trade"] == 38
report = {"scope": "Retained-ledger recount and document figure generation only; no game execution",
          "completion_cells": checks,
          "whole_window": dict(whole), "entry_residual": dict(residual),
          "source_hashes": {n: hashlib.sha256((DATA/n).read_bytes()).hexdigest()
                            for n in ["first_management_windows.json", "t03_trade_groups.json",
                                      "t09_entry_nonbuild_records.json", "agenda_offers.json"]}}
(HERE / "qa" / "ledger_checks.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2))
