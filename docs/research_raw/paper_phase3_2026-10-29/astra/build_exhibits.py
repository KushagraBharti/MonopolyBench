"""Regenerate phase-3 exhibits from the frozen, independently checked analyses.

Run from the repository root with python/.venv/bin/python. No provider calls,
engine changes, or canonical artifact writes. Axes describe observed quantities,
not intrinsic model ability or counterfactual returns.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OUT = HERE / "exhibits"
CORE = ROOT / "docs/research_raw/paper_phase2_2026-10-28/core_review"
PHASE1 = ROOT / "docs/research_raw/paper_phase1_2026-10-28"
SOURCES: dict[str, str] = {}
COLORS = {"Sol": "#2463A6", "Gemini": "#1A8066", "Opus": "#985C9C", "Grok": "#C36B22"}
ORDER = list(COLORS)
RESPONSE_CONDITION = {
    "Sol": "standard corrective-retry policy",
    "Gemini": "standard corrective-retry policy",
    "Opus": "refusal recovery to action-only requests; retry budget affected",
    "Grok": "required tool choice; standard corrective-retry policy",
}
MODEL = {
    "Sol": "gpt-6.1-sol",
    "Gemini": "gemini-4-argon",
    "Opus": "claude-opus-5.5",
    "Grok": "grok-4.7",
}
REVERSE = {v: k for k, v in MODEL.items()}
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
    }
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    SOURCES[str(path.relative_to(ROOT))] = sha(path)
    return json.loads(path.read_text())


def table(name: str, rows: list[dict]) -> None:
    (OUT / f"{name}.json").write_text(json.dumps(rows, indent=2) + "\n")
    if rows:
        with (OUT / f"{name}.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def save(fig, name: str) -> None:
    for ext in ("png", "pdf", "svg"):
        fig.savefig(
            OUT / f"{name}.{ext}",
            dpi=180,
            bbox_inches="tight",
            metadata={"Creator": "MonopolyBench phase-3 analysis"},
        )
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    econ = read(CORE / "astra/development_aggregation_check.json")
    design = read(CORE / "sol/corpus_economics_audit.json")["design"]
    negotiation = read(CORE / "astra/negotiation_units.json")["summary"]["initiation"]
    recovery = read(CORE / "sol/build_recovery_audit.json")["summary"]
    bounds = read(CORE / "opus/bankruptcy_bounds.json")
    bounds = [
        {**r, "model": "Gemini" if r["model"] == "Argon" else r["model"]}
        for r in bounds
    ]
    old = read(PHASE1 / "sol/results.json")
    residual = read(HERE / "deployment_residual_check.json")
    assert len(design) == 20 and len(econ["units"]) == 103 and len(bounds) == 60
    assert sum(x["spend"] for x in econ["units"]) == 103450
    assert sum(x["developed_rent_from_first_own_build"] for x in econ["units"]) == 92550
    assert sum(x["avoidable"] for x in bounds) == 3
    assert sum(x["accessible"] != x["full"] for x in bounds) == 1
    assert recovery["opus_all61_same_allocation_legal_after_interleaving"]

    # F1 is an explicitly conceptual diagram. It has no empirical rate.
    fig, ax = plt.subplots(figsize=(11.6, 4.0))
    ax.set(xlim=(0, 12), ylim=(0, 4))
    ax.axis("off")
    labels = [
        (
            "1  Instruction / norm",
            "Win the game\nPublic bluffing permitted\nPrivate honesty requested",
        ),
        (
            "2  Opportunity",
            "Observed state and phase\nLegal actions\nLegal action sequences",
        ),
        (
            "3  Applied behavior",
            "Engine action\nPublic statements\nPrivate records kept separate",
        ),
        (
            "4  Consequence",
            "Settlement and exposure\nDevelopment and financing\nLater recorded outcomes",
        ),
        (
            "5  Alternatives",
            "Prior plans and context\nErrors and channel conflicts\nResponse policy",
        ),
    ]
    for i, (title, body) in enumerate(labels):
        x = i * 2.4
        ax.add_patch(
            FancyBboxPatch(
                (x + 0.05, 1.45),
                2.2,
                1.8,
                boxstyle="round,pad=.06",
                facecolor="#EEF3F8",
                edgecolor="#CCD6E0",
            )
        )
        ax.text(
            x + 1.15, 2.85, title, ha="center", va="center", fontsize=9.1, weight="bold"
        )
        ax.text(
            x + 1.15,
            2.15,
            body,
            ha="center",
            va="center",
            fontsize=8.4,
            linespacing=1.6,
        )
        if i < 4:
            ax.add_patch(
                FancyArrowPatch(
                    (x + 2.27, 2.35),
                    (x + 2.48, 2.35),
                    arrowstyle="->",
                    mutation_scale=12,
                    color="#5A6978",
                )
            )
    ax.text(
        6,
        0.85,
        "Keep four conclusions distinct: task performance • rule feasibility • communication consistency • norm adherence",
        ha="center",
        fontsize=10,
    )
    ax.text(
        6,
        0.35,
        "A favorable outcome does not establish persuasion; an inconsistent explanation does not establish deliberate dishonesty.",
        ha="center",
        fontsize=9,
    )
    save(fig, "f01_evidence_chain")

    # F2: actual seed blocks and rotations, not independent Bernoulli trials.
    fig, ax = plt.subplots(figsize=(8.6, 5.1))
    seeds = list(dict.fromkeys(x["seed"] for x in design))
    grid = []
    for d in design:
        g = d["game"]
        row = seeds.index(d["seed"])
        col = (g - 1) % 4
        winner = REVERSE[d["winner_name"]]
        ax.add_patch(
            plt.Rectangle(
                (col, row), 1, 1, color=COLORS[winner], alpha=0.90, ec="white", lw=3
            )
        )
        ax.text(
            col + 0.5,
            row + 0.5,
            f"G{g:02d}  {winner}\nseat {int(d['winner'][1:])}",
            ha="center",
            va="center",
            color="white",
            weight="bold",
            linespacing=1.6,
        )
        grid.append(
            {
                "game": g,
                "seed": d["seed"],
                "rotation": col + 1,
                "winner": winner,
                "winner_seat": int(d["winner"][1:]),
                "turns": d["turns"],
                "treatment_fingerprint": d["treatment_fingerprint"],
            }
        )
    ax.set(
        xlim=(0, 4),
        ylim=(5, 0),
        xticks=np.arange(4) + 0.5,
        xticklabels=[f"Rotation {i}" for i in range(1, 5)],
        yticks=np.arange(5) + 0.5,
        yticklabels=[f"Block {i + 1}\nseed {s}" for i, s in enumerate(seeds)],
    )
    ax.tick_params(length=0)
    ax.set_title("Game winners across five seed blocks and four rotations", pad=16)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.text(
        0.5,
        -0.025,
        "Shared raw dice streams do not give identical opportunities. Games 1–4 and 5–20 have different treatment fingerprints.",
        ha="center",
        fontsize=8.4,
    )
    save(fig, "f02_seed_rotation_winners")
    table("t01_cohort", grid)

    # F3: initiation propensity and repetition are separate conditional quantities.
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.9), constrained_layout=True)
    profile = []
    for i, name in enumerate(ORDER):
        r = negotiation[MODEL[name]]
        propensity = r["proposing_turns"] / r["eligible_turns"]
        intensity = r["proposals"] / r["proposing_turns"]
        axes[0].barh(i, propensity * 100, color=COLORS[name], height=0.58)
        axes[0].text(
            propensity * 100 + 0.5,
            i,
            f"{r['proposing_turns']}/{r['eligible_turns']}",
            va="center",
            fontsize=9,
        )
        axes[1].barh(i, intensity, color=COLORS[name], height=0.58)
        axes[1].text(intensity + 0.025, i, f"{intensity:.2f}", va="center", fontsize=9)
        profile.append(
            {
                "configuration": name,
                "response_condition": RESPONSE_CONDITION[name],
                **r,
                "own_turn_propensity": propensity,
                "proposals_per_proposing_turn": intensity,
                "eligible_decision_rate": r["proposals"] / r["eligible_decisions"],
                "eligible_decisions_per_turn": r["eligible_decisions"]
                / r["eligible_turns"],
            }
        )
    for ax in axes:
        ax.set(yticks=range(4), yticklabels=ORDER)
        ax.invert_yaxis()
        ax.set_axisbelow(True)
        ax.grid(axis="x", alpha=0.18)
    axes[0].set(
        xlabel="Own eligible turns with ≥1 proposal (%)",
        xlim=(0, 32),
        title="How often a turn includes a proposal",
    )
    axes[1].set(
        xlabel="Proposals per proposing turn",
        xlim=(0, 1.9),
        title="How often a proposing turn repeats",
    )
    fig.text(
        0.5,
        -0.04,
        "Configured agents: Opus has action-only refusal recovery; Grok has required tool choice. Eligibility remains endogenous.",
        ha="center",
        fontsize=8,
    )
    save(fig, "f03_negotiation_profiles")
    table("t02_negotiation", profile)

    # F4: distinct denominators, with raw counts printed. Not a strategic score.
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6), constrained_layout=True)
    trade_rows = []
    for i, name in enumerate(ORDER):
        r = old["trade_group_metrics"][name]
        values = [
            r["trade_groups"],
            r["first_management_built"],
            r["entry_eligible"],
            r["entry_eligible_built"],
        ]
        axes[0].bar(i - 0.17, values[0], width=0.32, color=COLORS[name], alpha=0.28)
        axes[0].bar(i + 0.17, values[1], width=0.32, color=COLORS[name])
        axes[0].text(
            i - 0.17, values[0] + 0.35, str(values[0]), ha="center", fontsize=9
        )
        axes[0].text(
            i + 0.17, values[1] + 0.35, str(values[1]), ha="center", fontsize=9
        )
        rc = residual["counts_by_model"].get(name, {})
        segments = [
            (values[3], "#3D718E"),
            (rc.get("engine_default", 0), "#BAC2CB"),
            (rc.get("received_content_tool_conflict", 0), "#D69B49"),
            (rc.get("consistent_end_with_stated_reserve", 0), "#A9C9B2"),
        ]
        assert sum(v for v, _ in segments) == values[2]
        left = 0
        for count, color in segments:
            width = count / values[2] * 100
            axes[1].barh(i, width, left=left, color=color, height=0.58)
            if count:
                axes[1].text(
                    left + width / 2,
                    i,
                    str(count),
                    ha="center",
                    va="center",
                    fontsize=9,
                )
            left += width
        axes[1].text(
            103, i, f"{values[3]}/{values[2]} built", va="center", fontsize=8.5
        )
        trade_rows.append(
            {
                "configuration": name,
                **{k: v for k, v in r.items() if k != "all_group_routes"},
            }
        )
    axes[0].set(
        xticks=range(4),
        xticklabels=ORDER,
        ylim=(0, 21),
        ylabel="Trade-completed group episodes",
        title="Assembly and first-management development",
    )
    axes[0].legend(
        [
            plt.Rectangle((0, 0), 1, 1, fc="#8999AA", alpha=0.28),
            plt.Rectangle((0, 0), 1, 1, fc="#8999AA"),
        ],
        ["Acquired by trade", "Built that management turn"],
        fontsize=8,
        loc="upper center",
        ncol=2,
    )
    axes[1].set(
        yticks=range(4),
        yticklabels=ORDER,
        xlim=(0, 135),
        xticks=[0, 25, 50, 75, 100],
        xlabel="Entry-buildable group episodes (%) · segment labels are counts",
        title="First-window outcome when buildable at entry",
    )
    axes[1].invert_yaxis()
    axes[1].grid(axis="x", alpha=0.18)
    axes[1].legend(
        [
            plt.Rectangle((0, 0), 1, 1, fc=c)
            for c in ["#3D718E", "#BAC2CB", "#D69B49", "#A9C9B2"]
        ],
        ["Built", "Default", "Received conflict", "Stated hold"],
        fontsize=7.7,
        ncol=2,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.42),
    )
    fig.text(
        0.5,
        -0.13,
        "Opus: action-only recovery condition. Grok: required tool choice. Actual outcomes retained; no corrected behavior is imputed.",
        ha="center",
        fontsize=8.5,
    )
    save(fig, "f04_opportunity_and_deployment")
    table("t03_trade_groups", trade_rows)
    table(
        "t04_bilateral_completion",
        [
            {"newly_completed_sides": int(k), "trades": v}
            for k, v in old["trade_completion_sides"].items()
        ],
    )
    table(
        "t09_entry_nonbuild_records",
        [{k: v for k, v in r.items() if k != "final_action"} for r in residual["rows"]],
    )

    # F5: receipts after own expenditure, not isolated or net investment return.
    fig, spend_axes = plt.subplots(
        1, 2, figsize=(10.6, 5.1), sharex=True, sharey=True, constrained_layout=True
    )
    spending = []
    for u in econ["units"]:
        name = REVERSE[design[u["game"] - 1]["seats"][u["player"]]]
        inherited = "inheritance" in u["latest_deed_routes_at_first_build"].values()
        ax = spend_axes[0 if u["winner"] else 1]
        ax.scatter(
            u["spend"],
            u["developed_rent_from_first_own_build"],
            marker="D" if inherited else "o",
            c="#3D718E",
            s=38,
            alpha=0.68,
            edgecolor="#101820" if u["eliminations"] else "white",
            lw=1 if u["eliminations"] else 0.4,
        )
        spending.append(
            {
                "game": u["game"],
                "player": u["player"],
                "configuration": name,
                "group": u["group"],
                "winner": u["winner"],
                "spend": u["spend"],
                "sale_proceeds": u["sale_proceeds"],
                "paid_developed_rent_after_first_own_spend": u[
                    "developed_rent_from_first_own_build"
                ],
                "paid_developed_rent_whole_game": u["developed_rent_whole_game"],
                "inherited_deed_at_first_own_spend": inherited,
                "creditor_eliminations_on_group": u["eliminations"],
                "first_own_spend_event": u["first_build_seq"],
            }
        )
    for winner, ax in zip([True, False], spend_axes, strict=True):
        subset = [u for u in econ["units"] if u["winner"] == winner]
        n_inherited = sum(
            "inheritance" in u["latest_deed_routes_at_first_build"].values()
            for u in subset
        )
        zeros = sum(u["developed_rent_from_first_own_build"] == 0 for u in subset)
        ax.set_yscale("symlog", linthresh=100)
        ax.set(
            xlabel="Own construction outlay ($)",
            title=f"{'Winners' if winner else 'Other players'} · {len(subset)} units\n{n_inherited} with inherited deeds",
        )
        ax.grid(alpha=0.15)
        ax.set_axisbelow(True)
        ax.text(
            0.98,
            0.07,
            f"{zeros} zero-rent units\n(overlap retained)",
            transform=ax.transAxes,
            ha="right",
            fontsize=8.5,
            bbox={"fc": "white", "ec": "none", "alpha": 0.8},
        )
    spend_axes[0].set_ylabel("Paid developed rent after first own expenditure ($)")
    handles = [
        Line2D(
            [0],
            [0],
            marker=m,
            color="none",
            markerfacecolor="#3D718E",
            markeredgecolor="white",
            label=t,
        )
        for m, t in [("o", "No inherited deed"), ("D", "Inherited deed present")]
    ]
    handles += [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#3D718E",
            markeredgecolor="#101820",
            label="Dark edge: creditor elimination",
        )
    ]
    fig.legend(
        handles=handles,
        fontsize=8,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.10),
        ncol=3,
    )
    fig.text(
        0.5,
        -0.14,
        "103 spending units; 40 zero-rent units, including 26 with no creditor elimination. Not net or incremental investment returns.",
        ha="center",
        fontsize=8.5,
    )
    save(fig, "f05_spending_and_receipts")
    table("t05_spending_units", spending)

    # F6: all eliminations, including four automatic after-mortgage eliminations.
    fig, ax = plt.subplots(figsize=(7.8, 5.4))
    maximum = max(max(r["full"], r["owed"]) for r in bounds) + 100
    ax.plot(
        [0, maximum],
        [0, maximum],
        color="#8A9198",
        lw=1,
        linestyle="--",
        label="Accessible financing = current debt",
    )
    for r in bounds:
        special = r["avoidable"] or r["full"] != r["accessible"]
        color = COLORS[r["model"]] if special else "#9CA7B3"
        ax.scatter(
            r["accessible"],
            r["owed"],
            c=color,
            marker="s" if r["elimination"] != "declared" else "o",
            s=70 if special else 26,
            alpha=1 if special else 0.65,
            zorder=10 if special else 3,
        )
        if special:
            offsets = {
                (7, "Opus"): (-10, 23),
                (12, "Sol"): (30, -32),
                (12, "Grok"): (9, -24),
                (17, "Gemini"): (15, 12),
            }
            ax.annotate(
                f"G{r['game']:02d} {r['model']}",
                (r["accessible"], r["owed"]),
                xytext=offsets[(r["game"], r["model"])],
                textcoords="offset points",
                fontsize=8,
                arrowprops={"arrowstyle": "-", "color": color, "lw": 0.8},
            )
        if r["full"] != r["accessible"]:
            ax.plot(
                [r["accessible"], r["full"]],
                [r["owed"], r["owed"]],
                color=color,
                lw=1.4,
            )
            ax.scatter(r["full"], r["owed"], marker="|", color=color, s=150)
    ax.set(
        xlabel="Cash reachable by self-financing at the eliminating debt ($)",
        ylabel="Current debt ($)",
        xlim=(0, maximum),
        ylim=(0, maximum),
        title="60 eliminations: legal access differs from nominal assets",
    )
    ax.text(
        0.04,
        0.96,
        "56: even the full upper bound is insufficient\n3: a legal sequence pays the current debt\n1: hotel rule blocks nominally sufficient assets",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
    )
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(alpha=0.14)
    fig.text(
        0.5,
        0.005,
        "Circles: 56 declared eliminations. Squares: four automatic eliminations following a mortgage.",
        ha="center",
        fontsize=8.5,
    )
    save(fig, "f06_elimination_financing")
    table("t06_eliminations", bounds)

    # F7: denominator is selected uneven-building rejection decisions.
    fig, ax = plt.subplots(figsize=(9.8, 3.8), constrained_layout=True)
    recovery_rows = []
    for i, name in enumerate(ORDER):
        key = next(
            k for k in recovery["uneven_rejection_decisions"] if k.endswith(MODEL[name])
        )
        total = recovery["uneven_rejection_decisions"][key]
        same = recovery["allocation_preserving_within_decision"].get(key, 0)
        changed = recovery["allocation_changing_within_decision"].get(key, 0)
        default = total - same - changed
        left = 0
        for v, color in [(same, "#3D718E"), (changed, "#8BBDBB"), (default, "#D5A174")]:
            ax.barh(i, v, left=left, color=color, height=0.58)
            if v:
                ax.text(left + v / 2, i, str(v), va="center", ha="center", fontsize=9)
            left += v
        recovery_rows.append(
            {
                "configuration": name,
                "uneven_rejection_decisions": total,
                "some_legal_build_same_decision": same + changed,
                "same_purchase_multiset": same,
                "changed_purchase_multiset": changed,
                "ended_in_default": default,
            }
        )
    ax.set(
        yticks=range(4),
        yticklabels=ORDER,
        xlabel="Decisions with an uneven-intermediate-build rejection",
        title="Recovery outcome includes both response policy and chosen allocation",
    )
    ax.invert_yaxis()
    ax.set_xlim(0, 67)
    ax.legend(
        [plt.Rectangle((0, 0), 1, 1, fc=c) for c in ["#3D718E", "#8BBDBB", "#D5A174"]],
        ["Build: original multiset", "Build: changed multiset", "Engine default"],
        loc="lower right",
        fontsize=8,
    )
    fig.text(
        0.5,
        -0.05,
        "Opus: refusal consumes an attempt, leaving no correction after an invalid action-only retry. Grok: required tool choice.",
        ha="center",
        fontsize=8,
    )
    save(fig, "f07_build_recovery")
    table("t07_build_recovery", recovery_rows)

    # F8: curated contrast, grounded in retained original-record checks.
    omission = read(CORE / "sol/g13_omission_check.json")
    read(CORE / "sol/additional_social_channel_checks.json")
    read(CORE / "sol/g11_social_channel_checks.json")
    assert (
        omission["buyer_exposure_exact"]
        and omission["cash_if_accept_then_mortgage"] == 295
    )
    fig, ax = plt.subplots(figsize=(11.4, 8.4))
    ax.axis("off")
    ax.set(xlim=(0, 12), ylim=(0, 8.8))
    rows = [
        (
            7.0,
            "A · Selective framing, with an earlier buyer motive",
            [
                (
                    "G13 d251 · buyer",
                    "Counters at $130; already values\nsolvency for Short Line rent to p2.",
                    "Returned provider summary",
                ),
                (
                    "G13 d252 · seller",
                    "Declines $130; omits available\nVentnor mortgage in the pitch.",
                    "Applied note + returned explanation",
                ),
                (
                    "G13 d253 · buyer",
                    "Prompt contains d252 message.\nAccepts the $200 transaction.",
                    "Delivered prompt + applied action",
                ),
            ],
            "Legal alternative: $35 + $130 counteroffer + $130 mortgage = $295. No $70 persuasion effect identified.",
        ),
        (
            4.2,
            "B · Correcting a premise while accepting the terms",
            [
                (
                    "G19 d135 · proposer",
                    "Sends an offer with a mistaken\ncolor-group premise.",
                    "Applied public offer",
                ),
                (
                    "G19 d135 · same call",
                    "Private argument says to abort;\nthe received proposal is applied.",
                    "Within-call inconsistency",
                ),
                (
                    "G19 d136 · recipient",
                    "Explicitly corrects the premise\nand accepts the transaction.",
                    "Recipient note + applied action",
                ),
            ],
            "Settlement does not establish uptake of the false premise or a channel-consistent proposer record.",
        ),
        (
            1.4,
            "C · A transient echo followed by correction and rejection",
            [
                (
                    "G11 d255 · proposer",
                    "Claims the proposed trade\nwould complete both groups.",
                    "Applied public proposal",
                ),
                (
                    "G11 d256 · recipient",
                    "Returned text first echoes\ncompletion, then checks and corrects it.",
                    "Within-response sequence",
                ),
                (
                    "G11 d256 · action",
                    "Rejects; the final public/private\nrecord rejects the premise.",
                    "Applied action and arguments",
                ),
            ],
            "Transient textual uptake is observed; durable belief, successful persuasion and general immunity are not identified.",
        ),
    ]
    for y, label, cases, boundary in rows:
        ax.text(0.1, y + 1.55, label, weight="bold", fontsize=10)
        for i, (title, body, footer) in enumerate(cases):
            x = 0.1 + i * 4
            ax.add_patch(
                FancyBboxPatch(
                    (x, y),
                    3.65,
                    1.32,
                    boxstyle="round,pad=.06",
                    fc="#F0F4F7",
                    ec="#C8D1D9",
                )
            )
            ax.text(x + 1.82, y + 1.10, title, ha="center", weight="bold", fontsize=9)
            ax.text(
                x + 1.82, y + 0.65, body, ha="center", fontsize=8.8, linespacing=1.5
            )
            ax.text(
                x + 1.82, y + 0.15, footer, ha="center", fontsize=7.8, color="#4D667B"
            )
            if i < 2:
                ax.add_patch(
                    FancyArrowPatch(
                        (x + 3.7, y + 0.65),
                        (x + 3.94, y + 0.65),
                        arrowstyle="->",
                        mutation_scale=15,
                    )
                )
        ax.text(0.1, y - 0.35, boundary, fontsize=8.4)
    ax.text(
        6,
        0.35,
        "Selected case contrasts, not population rates. Public bluffing is authorized by this cohort's instructions.",
        ha="center",
        fontsize=9,
    )
    save(fig, "f08_social_chronology")

    # F9: canonical cash only; do not label this liquidation wealth or net worth.
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), constrained_layout=True)
    cash_rows = []
    for ax, game in zip(axes, [14, 15, 19], strict=True):
        d = design[game - 1]
        path = next(p for p in econ["event_source_hashes"] if f"/game-{game:02d}-" in p)
        source = ROOT / path
        assert sha(source) == econ["event_source_hashes"][path]
        SOURCES[path] = sha(source)
        first_state = read(sorted((source.parent / "state").glob("*.json"))[0])
        # For these three games the initial snapshot precedes every cash change.
        cash = {p["player_id"]: p["cash"] for p in first_state["players"]}
        assert all(v == 1500 for v in cash.values())
        paths = {p: [(0, 1500)] for p in cash}
        for line in source.read_text().splitlines():
            e = json.loads(line)
            if e["type"] != "CASH_CHANGED":
                continue
            p = e["payload"]["player_id"]
            cash[p] += e["payload"]["delta"]
            paths[p].append((e["turn_index"], cash[p]))
            cash_rows.append(
                {
                    "game": game,
                    "event_seq": e["seq"],
                    "turn": e["turn_index"],
                    "player": p,
                    "configuration": REVERSE[d["seats"][p]],
                    "cash": cash[p],
                    "reason": e["payload"].get("reason"),
                }
            )
        for p, rows in paths.items():
            name = REVERSE[d["seats"][p]]
            ax.step(
                [r[0] for r in rows],
                [r[1] for r in rows],
                where="post",
                color=COLORS[name],
                label=name,
                lw=1.4,
            )
        assert cash[d["winner"]] == d["winner_final_cash"]
        ax.set(
            title=f"G{game:02d} · {REVERSE[d['winner_name']]} wins",
            xlabel="Global game turn",
            ylabel="Cash ($)",
        )
        ax.grid(alpha=0.15)
    axes[0].legend(fontsize=8, ncol=2)
    save(fig, "f09_cash_trajectories")
    table("t08_cash_trajectories", cash_rows)

    # Machine-readable values and source identities for all numeric exhibits.
    manifest = {
        "script_sha256": sha(Path(__file__)),
        "source_sha256": SOURCES,
        "artifacts": {
            p.name: sha(p)
            for p in sorted(OUT.iterdir())
            if p.suffix in {".png", ".pdf", ".svg", ".json", ".csv"}
            and p.name != "manifest.json"
        },
        "checks": {
            "20_games": True,
            "103_spending_units": True,
            "60_eliminations": True,
            "outlay_103450": True,
            "post_first_spend_paid_rent_92550": True,
            "three_current_debts_financing_feasible": True,
            "one_hotel_lock": True,
            "61_reordered_opus_plans_legal": True,
            "cash_trajectory_winner_endpoints_match": True,
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {
                "figures": 9,
                "tables": 9,
                "checks": manifest["checks"],
                "directory": str(OUT),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
