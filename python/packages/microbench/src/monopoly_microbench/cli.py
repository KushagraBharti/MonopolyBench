from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .catalog import get_suite, list_scenario_summaries, validate_all
from .runner import MicroRunConfig, export_batch, run_batch, run_scenario, run_suite, score_run


def main() -> None:
    parser = argparse.ArgumentParser(prog="monopoly-micro")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    list_parser = sub.add_parser("list")
    list_parser.add_argument("--suite", default=None)
    list_parser.add_argument("--category", default=None)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--scenario", required=True)
    run_parser.add_argument("--model", default=None)
    run_parser.add_argument("--name", default=None)
    run_parser.add_argument("--reasoning", default=None)
    run_parser.add_argument("--prompt-condition", default="default")
    run_parser.add_argument("--baseline", default=None)
    suite_parser = sub.add_parser("run-suite")
    suite_parser.add_argument("--suite", default="micro-v1")
    suite_parser.add_argument("--model", default=None)
    suite_parser.add_argument("--prompt-condition", default="default")
    suite_parser.add_argument("--baseline", default=None)
    compare_parser = sub.add_parser("compare")
    compare_parser.add_argument("--suite", default="micro-v1")
    compare_parser.add_argument("--models", required=True)
    compare_parser.add_argument("--prompt-condition", default="default")
    compare_parser.add_argument("--baseline", default=None)
    compare_parser.add_argument("--scenario", action="append", dest="scenario_ids")
    score_parser = sub.add_parser("score")
    score_parser.add_argument("--run-id", required=True)
    score_parser.add_argument("--write", action="store_true")
    export_parser = sub.add_parser("export")
    export_parser.add_argument("--batch-id", required=True)
    export_parser.add_argument("--format", choices=["csv", "jsonl"], default="csv")
    export_parser.add_argument("--out", required=True)
    sub.add_parser("tui")
    args = parser.parse_args()
    console = Console()
    if args.command == "validate":
        result = validate_all()
        console.print(f"Valid micro catalog: {result['scenario_count']} scenarios, {result['suite_count']} suites")
    elif args.command == "list":
        _print_scenarios(console, args.suite, args.category)
    elif args.command == "run":
        result = asyncio.run(
            run_scenario(
                MicroRunConfig(
                    scenario_id=args.scenario,
                    openrouter_model_id=args.model,
                    name=args.name,
                    reasoning={"effort": args.reasoning} if args.reasoning else None,
                    prompt_condition=args.prompt_condition,
                    baseline=args.baseline,
                )
            )
        )
        _print_result(console, result)
    elif args.command == "run-suite":
        results = asyncio.run(
            run_suite(
                args.suite,
                model_id=args.model,
                baseline=args.baseline,
                prompt_condition=args.prompt_condition,
            )
        )
        console.print(f"Completed {len(results)} scenario runs.")
    elif args.command == "compare":
        models_payload = json.loads(Path(args.models).read_text(encoding="utf-8"))
        model_ids = models_payload.get("models", models_payload)
        result = asyncio.run(
            run_batch(
                suite_id=args.suite,
                model_ids=[] if args.baseline else list(model_ids),
                baseline=args.baseline,
                prompt_condition=args.prompt_condition,
                scenario_ids=args.scenario_ids,
            )
        )
        console.print_json(data=result)
    elif args.command == "score":
        console.print_json(data=score_run(args.run_id, write=args.write))
    elif args.command == "export":
        path = export_batch(args.batch_id, fmt=args.format, out=Path(args.out))
        console.print(f"Wrote {path}")
    elif args.command == "tui":
        from .tui import main as tui_main

        tui_main()


def _print_scenarios(console: Console, suite_id: str | None, category: str | None) -> None:
    table = Table(title="Micro Scenarios")
    for column in ("ID", "Category", "Difficulty", "Title"):
        table.add_column(column)
    for item in list_scenario_summaries(suite_id=suite_id):
        if category and item["category"] != category:
            continue
        table.add_row(item["scenario_id"], item["category"], item["difficulty"], item["title"])
    console.print(table)
    if suite_id:
        suite = get_suite(suite_id)
        console.print(f"Suite {suite_id}: {len(suite['scenario_ids'])} scenarios")


def _print_result(console: Console, result: dict) -> None:
    action = result["outcome"]["action"]
    console.print(f"Run: {result['run_id']}")
    console.print(f"Action: {action['action']} {json.dumps(action.get('args', {}), ensure_ascii=True)}")
    console.print(f"Score: {result['score']['total']} {result['score']['label']}")
    console.print(f"Retry: {'yes' if result['outcome']['retry_used'] else 'no'}")
    console.print(f"Fallback: {'yes' if result['outcome']['fallback_used'] else 'no'}")
    console.print(f"Artifacts: runs/micro/{result['run_id']}")


if __name__ == "__main__":
    main()
