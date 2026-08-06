"""Regenerate the paper's Run 273 asset-balance and house-supply figure."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
TABLE_ROOT = (
    REPO_ROOT
    / "saved_games"
    / "frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview"
    / "analysis"
    / "tables"
)
OUTPUT_ROOT = REPO_ROOT / "paper" / "figures"

PLAYERS = {
    "OpenAI GPT 5.4 Mini": {
        "color": "#D55E00",
        "linestyle": "-",
        "marker": "o",
        "markevery": 18,
    },
    "Claude Haiku 4.5": {
        "color": "#0072B2",
        "linestyle": (0, (5, 2)),
    },
    "Gemini 3 Flash Preview": {
        "color": "#009E73",
        "linestyle": (0, (7, 3)),
    },
    "Grok 4.3": {
        "color": "#CC79A7",
        "linestyle": "-.",
    },
}

# First frozen checkpoints at which the player is recorded bankrupt.
BANKRUPTCY_CHECKPOINTS = {
    "OpenAI GPT 5.4 Mini": 110,
    "Claude Haiku 4.5": 167,
    "Grok 4.3": 273,
}


def main() -> None:
    state = pd.read_csv(TABLE_ROOT / "state_by_turn_player.csv")
    bank = pd.read_csv(TABLE_ROOT / "bank_inventory_by_turn.csv")

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10.5,
            "axes.labelsize": 11.5,
            "legend.fontsize": 10.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, (wealth_ax, bank_ax) = plt.subplots(
        2,
        1,
        figsize=(12, 7.2),
        sharex=True,
        gridspec_kw={"height_ratios": [2.15, 1], "hspace": 0.08},
    )

    for player, style in PLAYERS.items():
        series = state.loc[state["player_id"].eq(player)].sort_values("turn_index")
        if player in BANKRUPTCY_CHECKPOINTS:
            series = series.loc[
                series["turn_index"] <= BANKRUPTCY_CHECKPOINTS[player]
            ]
        wealth_ax.plot(
            series["turn_index"],
            series["net_worth_estimate"],
            label=player,
            linewidth=2.2,
            **style,
        )

    bank_ax.step(
        bank["turn_index"],
        bank["houses_remaining"],
        where="post",
        color="#4B5563",
        linewidth=2.4,
    )

    for player, checkpoint in BANKRUPTCY_CHECKPOINTS.items():
        color = PLAYERS[player]["color"]
        for axis in (wealth_ax, bank_ax):
            axis.axvline(
                checkpoint,
                color=color,
                linestyle=":",
                linewidth=1.6,
                alpha=0.95,
                zorder=1,
            )

    for axis in (wealth_ax, bank_ax):
        axis.axvspan(167, 180, color="#6B7280", alpha=0.12, linewidth=0)
        axis.grid(True, color="#D8E0EA", linewidth=0.9)
        axis.set_axisbelow(True)

    wealth_ax.annotate(
        "exchange + house-scarcity window",
        xy=(170, 6150),
        xytext=(147, 9100),
        arrowprops={"arrowstyle": "-", "color": "#5F6368", "linewidth": 1.1},
        bbox={
            "boxstyle": "round,pad=0.2",
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.94,
        },
        color="#414141",
    )
    bank_ax.annotate(
        "bank supply reaches 0",
        xy=(181, 0),
        xytext=(171, 27),
        arrowprops={"arrowstyle": "-", "color": "#5F6368", "linewidth": 1.1},
        bbox={
            "boxstyle": "round,pad=0.2",
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.94,
        },
        color="#414141",
    )

    wealth_ax.set_ylabel("Face-value asset-balance\nproxy ($)")
    wealth_ax.set_ylim(-250, 10850)
    wealth_ax.legend(
        loc="upper left",
        ncol=2,
        frameon=True,
        framealpha=0.96,
        handlelength=3.2,
        columnspacing=1.35,
    )

    bank_ax.set_ylabel("Bank houses")
    bank_ax.set_xlabel("Authoritative state checkpoint index")
    bank_ax.set_ylim(-1.5, 34)
    bank_ax.set_yticks([0, 8, 16, 24, 32])
    bank_ax.set_xlim(0, 275)

    for axis in (wealth_ax, bank_ax):
        for spine in axis.spines.values():
            spine.set_linewidth(1.2)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        OUTPUT_ROOT / "run273_house_lock.png",
        dpi=200,
        bbox_inches="tight",
        facecolor="white",
    )
    fig.savefig(
        OUTPUT_ROOT / "run273_house_lock.pdf",
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
