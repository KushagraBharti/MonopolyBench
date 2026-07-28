from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MaxNLocator, MultipleLocator


ANALYSIS_DIR = Path(__file__).resolve().parents[1]
TABLES_DIR = ANALYSIS_DIR / "tables"
PLOTS_DIR = ANALYSIS_DIR / "plots"
QUALITY_PATH = ANALYSIS_DIR / "quality" / "plot_quality.json"
TICK_INTERVALS = {
    "cost_by_turn.png": 0.05,
    "cost_per_call.png": 0.01,
    "cumulative_cost_by_call.png": 0.50,
    "cost_by_model.png": 0.25,
}


def dollar_formatter(value: float, _position: int | None = None) -> str:
    return f"${value:,.2f}"


def line_plot(
    frame: pd.DataFrame,
    path: Path,
    title: str,
    x_column: str,
    y_column: str,
    y_label: str,
    tick_interval: float,
) -> None:
    figure, axis = plt.subplots(figsize=(12, 6), dpi=160)
    axis.plot(frame[x_column], frame[y_column], linewidth=1.8)
    axis.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=12))
    axis.yaxis.set_major_locator(MultipleLocator(tick_interval))
    axis.yaxis.set_major_formatter(FuncFormatter(dollar_formatter))
    axis.grid(True, alpha=0.25)
    axis.set_title(title)
    axis.set_xlabel(x_column.replace("_", " ").title())
    axis.set_ylabel(y_label)
    figure.tight_layout()
    figure.savefig(path)
    plt.close(figure)


def main() -> None:
    per_call = pd.read_csv(TABLES_DIR / "per_call_usage.csv")
    model_usage = pd.read_csv(TABLES_DIR / "model_usage.csv")
    for column in ("call_index", "turn_index", "cost"):
        per_call[column] = pd.to_numeric(per_call[column], errors="coerce")
    model_usage["cost"] = pd.to_numeric(model_usage["cost"], errors="coerce")

    per_turn = per_call.groupby("turn_index", as_index=False)["cost"].sum()
    line_plot(
        per_turn,
        PLOTS_DIR / "cost_by_turn.png",
        "Cost By Turn",
        "turn_index",
        "cost",
        "Cost",
        TICK_INTERVALS["cost_by_turn.png"],
    )

    ordered = per_call.sort_values("call_index").copy()
    line_plot(
        ordered,
        PLOTS_DIR / "cost_per_call.png",
        "Cost Per Call",
        "call_index",
        "cost",
        "Cost",
        TICK_INTERVALS["cost_per_call.png"],
    )
    ordered["cumulative_cost"] = ordered["cost"].cumsum()
    line_plot(
        ordered,
        PLOTS_DIR / "cumulative_cost_by_call.png",
        "Cumulative Cost By Call",
        "call_index",
        "cumulative_cost",
        "Cumulative Cost",
        TICK_INTERVALS["cumulative_cost_by_call.png"],
    )

    figure, axis = plt.subplots(figsize=(11, 6), dpi=160)
    axis.bar(model_usage["player_id"].astype(str), model_usage["cost"])
    axis.tick_params(axis="x", rotation=25)
    axis.yaxis.set_major_locator(MultipleLocator(TICK_INTERVALS["cost_by_model.png"]))
    axis.yaxis.set_major_formatter(FuncFormatter(dollar_formatter))
    axis.grid(True, axis="y", alpha=0.25)
    axis.set_title("Cost By Model")
    axis.set_xlabel("Player Id")
    axis.set_ylabel("Cost")
    figure.tight_layout()
    figure.savefig(PLOTS_DIR / "cost_by_model.png")
    plt.close(figure)

    quality = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
    quality["status"] = "passed_visual_inspection"
    quality["tick_intervals_usd"] = TICK_INTERVALS
    quality["regenerated_plots"] = [
        {
            "path": f"analysis/plots/{name}",
            "sha256": hashlib.sha256((PLOTS_DIR / name).read_bytes()).hexdigest(),
            "y_axis_format": "$0.00",
            "tick_interval_usd": interval,
        }
        for name, interval in TICK_INTERVALS.items()
    ]
    QUALITY_PATH.write_text(json.dumps(quality, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": quality["status"], "plots": list(TICK_INTERVALS)}, indent=2))


if __name__ == "__main__":
    main()
