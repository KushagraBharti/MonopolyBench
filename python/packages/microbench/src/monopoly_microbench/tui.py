from __future__ import annotations

import asyncio
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from .catalog import get_suite, list_scenario_summaries, load_scenario
from .runner import MicroRunConfig, build_leaderboard, run_batch, run_scenario


CATEGORIES = [
    "ALL",
    "BUY_OR_AUCTION",
    "AUCTION",
    "TRADE_PROPOSE",
    "TRADE_RESPONSE",
    "BUILD_OR_MORTGAGE",
    "LIQUIDATION",
    "JAIL",
    "POST_TURN_STRATEGY",
]
PROMPT_CONDITION = "live_game"
DEFAULT_MODEL_ID = "openai/gpt-oss-120b"


def main() -> None:
    console = Console()
    state: dict[str, Any] = {
        "category": "ALL",
        "search": "",
        "prompt_condition": PROMPT_CONDITION,
        "model_id": DEFAULT_MODEL_ID,
        "last_results": [],
        "last_batch": None,
    }
    while True:
        console.clear()
        _print_header(console, state)
        _print_catalog(console, state)
        choice = Prompt.ask(
            "Command: number=detail, f=filter, s=search, r=run selected, c=run category, a=run suite, l=leaderboard, q=quit",
            default="q",
        )
        if choice.lower() == "q":
            return
        if choice.lower() == "f":
            state["category"] = Prompt.ask("Category", choices=CATEGORIES, default=str(state["category"]))
            continue
        if choice.lower() == "s":
            state["search"] = Prompt.ask("Search title/tag", default=str(state["search"]))
            continue
        if choice.lower() == "l":
            _show_leaderboard(console, state)
            continue
        if choice.lower() in {"r", "c", "a"}:
            _run_panel(console, state, mode=choice.lower())
            continue
        try:
            scenario = _filtered_scenarios(state)[int(choice) - 1]
        except (ValueError, IndexError):
            continue
        _detail(console, scenario["scenario_id"])


def _print_header(console: Console, state: dict[str, Any]) -> None:
    suite = get_suite("micro-v1")
    console.print(
        Panel(
            f"micro-v1: {len(suite['scenario_ids'])} scenarios | "
            f"category={state['category']} | search={state['search'] or '-'} | "
            f"model={state['model_id']} | prompt={PROMPT_CONDITION}",
            title="MonopolyBench Micro Decision Suite",
        )
    )


def _filtered_scenarios(state: dict[str, Any]) -> list[dict[str, Any]]:
    query = str(state["search"]).strip().lower()
    category = state["category"]
    items = list_scenario_summaries(suite_id="micro-v1")
    filtered = []
    for item in items:
        if category != "ALL" and item["category"] != category:
            continue
        haystack = " ".join([item["title"], item["description"], " ".join(item["tags"])]).lower()
        if query and query not in haystack:
            continue
        filtered.append(item)
    return filtered


def _print_catalog(console: Console, state: dict[str, Any]) -> None:
    table = Table(title="Scenario Catalog")
    table.add_column("#", justify="right")
    table.add_column("ID")
    table.add_column("Category")
    table.add_column("Difficulty")
    table.add_column("Title")
    table.add_column("Scoring")
    for index, item in enumerate(_filtered_scenarios(state), start=1):
        table.add_row(
            str(index),
            item["scenario_id"],
            item["category"],
            item["difficulty"],
            item["title"],
            item["scoring_mode"],
        )
    console.print(table)


def _detail(console: Console, scenario_id: str) -> None:
    scenario = load_scenario(scenario_id)
    console.clear()
    console.rule(scenario["title"])
    console.print(scenario["description"])
    console.print(f"Category: {scenario['category']} | Difficulty: {scenario['difficulty']}")
    console.print(f"Focal player: {scenario['focal_player_id']} | Decision: {scenario['decision_point']['decision_type']}")
    console.print(f"Strategic tension: {scenario['notes']['strategic_theme']}")
    console.print(f"Reference: {scenario['reference_policy']['action']['action']} - {scenario['reference_policy']['rationale']}")
    _print_board_summary(console, scenario)
    _print_legal_actions(console, scenario)
    _print_rubric(console, scenario)
    Prompt.ask("Press enter to return", default="")


def _print_board_summary(console: Console, scenario: dict[str, Any]) -> None:
    table = Table(title="Board Summary")
    table.add_column("Player")
    table.add_column("Cash", justify="right")
    table.add_column("Position")
    table.add_column("Jail")
    table.add_column("Owned")
    state = scenario["decision_point"]["state"]
    for player in state["players"]:
        owned = [
            space["name"]
            for space in state["board"]
            if space.get("owner_id") == player["player_id"]
        ]
        table.add_row(
            player["name"],
            str(player["cash"]),
            str(player["position"]),
            "yes" if player["in_jail"] else "no",
            ", ".join(owned[:6]) + ("..." if len(owned) > 6 else ""),
        )
    console.print(table)


def _print_legal_actions(console: Console, scenario: dict[str, Any]) -> None:
    table = Table(title="Legal Actions")
    table.add_column("Action")
    table.add_column("Args")
    table.add_column("Highlights")
    for action in scenario["decision_point"]["legal_actions"]:
        schema = action.get("args_schema", {})
        args = ", ".join((schema.get("properties") or {}).keys()) or "none"
        hints = action.get("ui_hints", {}).get("highlight_space_indices", [])
        table.add_row(action["action"], args, ", ".join(str(item) for item in hints) or "-")
    console.print(table)


def _print_rubric(console: Console, scenario: dict[str, Any]) -> None:
    table = Table(title="Rubric")
    table.add_column("Criterion")
    table.add_column("Type")
    table.add_column("Points", justify="right")
    table.add_column("Description")
    for item in scenario["evaluation"]["rubric"]:
        table.add_row(item["criterion_id"], item["type"], str(item["max_points"]), item["description"])
    console.print(table)


def _run_panel(console: Console, state: dict[str, Any], *, mode: str) -> None:
    model_id = Prompt.ask("Model ID", default=str(state["model_id"]))
    prompt_condition = PROMPT_CONDITION
    state["model_id"] = model_id
    state["prompt_condition"] = prompt_condition
    if mode == "r":
        filtered = _filtered_scenarios(state)
        if not filtered:
            console.print("No selected scenario.")
            Prompt.ask("Press enter", default="")
            return
        scenario_id = filtered[0]["scenario_id"]
        result = asyncio.run(
            run_scenario(
                MicroRunConfig(
                    scenario_id=scenario_id,
                    openrouter_model_id=model_id,
                    prompt_condition=prompt_condition,
                )
            )
        )
        state["last_results"] = [result]
        _show_result(console, result)
        return
    if mode == "c":
        scenario_ids = [item["scenario_id"] for item in _filtered_scenarios(state)]
        if not scenario_ids:
            console.print("No scenarios match current category/search.")
            Prompt.ask("Press enter", default="")
            return
    else:
        scenario_ids = None
    batch = asyncio.run(
        run_batch(
            suite_id="micro-v1",
            model_ids=[model_id],
            prompt_condition=prompt_condition,
            scenario_ids=scenario_ids,
        )
    )
    state["last_batch"] = batch
    state["last_results"] = []
    _show_leaderboard(console, state)


def _show_result(console: Console, result: dict[str, Any]) -> None:
    console.print(Panel(f"Run: {result['run_id']}", title="Result Inspector"))
    action = result["outcome"]["action"]
    console.print(f"Action: {action['action']} {action.get('args', {})}")
    console.print(f"Public: {action.get('public_message', '')}")
    console.print(f"Private: {action.get('private_thought', '')}")
    console.print(f"Retry: {result['outcome']['retry_used']}")
    _print_score(console, result["score"])
    Prompt.ask("Press enter to return", default="")


def _print_score(console: Console, score: dict[str, Any]) -> None:
    table = Table(title=f"Score {score['total']} {score['label']}")
    table.add_column("Criterion")
    table.add_column("Points")
    table.add_column("Passed")
    table.add_column("Message")
    for item in score["breakdown"]:
        table.add_row(item["criterion_id"], f"{item['points']}/{item['max_points']}", str(item["passed"]), item["message"])
    console.print(table)


def _show_leaderboard(console: Console, state: dict[str, Any]) -> None:
    console.clear()
    batch = state.get("last_batch")
    leaderboard = batch["leaderboard"] if batch else build_leaderboard(state.get("last_results", []))
    table = Table(title="Leaderboard")
    for column in ("Model", "Scenarios", "Avg", "Retry", "Invalid", "Latency"):
        table.add_column(column)
    for row in leaderboard.get("rows", []):
        table.add_row(
            row["model"],
            str(row["scenario_count"]),
            str(row["average_score"]),
            str(row["retry_rate"]),
            str(row["invalid_rate"]),
            str(row["average_latency_ms"]),
        )
    console.print(table)
    for model, categories in leaderboard.get("category_breakdown", {}).items():
        console.print(f"{model}: {categories}")
    Prompt.ask("Press enter to return", default="")
