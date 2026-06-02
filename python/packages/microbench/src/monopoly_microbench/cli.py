from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .catalog import get_suite, list_scenario_summaries, validate_all
from .research import (
    build_human_review_queue,
    list_research_suites,
    read_expert_labels,
    validate_research_catalog,
    write_static_research_report,
)
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
    run_parser.add_argument("--prompt-condition", choices=["live_game"], default="live_game")
    suite_parser = sub.add_parser("run-suite")
    suite_parser.add_argument("--suite", default="micro-v1")
    suite_parser.add_argument("--model", default=None)
    suite_parser.add_argument("--prompt-condition", choices=["live_game"], default="live_game")
    compare_parser = sub.add_parser("compare")
    compare_parser.add_argument("--suite", default="micro-v1")
    compare_parser.add_argument("--models", required=True)
    compare_parser.add_argument("--prompt-condition", choices=["live_game"], default="live_game")
    compare_parser.add_argument("--scenario", action="append", dest="scenario_ids")
    score_parser = sub.add_parser("score")
    score_parser.add_argument("--run-id", required=True)
    score_parser.add_argument("--write", action="store_true")
    export_parser = sub.add_parser("export")
    export_parser.add_argument("--batch-id", required=True)
    export_parser.add_argument("--format", choices=["csv", "jsonl"], default="csv")
    export_parser.add_argument("--out", required=True)
    research_parser = sub.add_parser("research-report")
    research_parser.add_argument("--suite", required=True)
    research_parser.add_argument("--runs-dir", default=None)
    research_parser.add_argument("--batch-id", default=None)
    research_parser.add_argument("--result-batch-id", default=None)
    research_parser.add_argument("--labels", default=None)
    queue_parser = sub.add_parser("review-queue")
    queue_parser.add_argument("--suite", required=True)
    queue_parser.add_argument("--out", required=True)
    labels_parser = sub.add_parser("validate-labels")
    labels_parser.add_argument("--labels", required=True)
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
                )
            )
        )
        _print_result(console, result)
    elif args.command == "run-suite":
        results = asyncio.run(
            run_suite(
                args.suite,
                model_id=args.model,
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
                model_ids=list(model_ids),
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
    elif args.command == "research-report":
        validate_research_catalog()
        out_dir = write_static_research_report(
            args.suite,
            runs_dir=Path(args.runs_dir) if args.runs_dir else None,
            batch_id=args.batch_id,
            result_batch_id=args.result_batch_id,
            labels_path=Path(args.labels) if args.labels else None,
        )
        console.print(f"Wrote micro research report artifacts to {out_dir}")
    elif args.command == "review-queue":
        validate_research_catalog()
        queue = build_human_review_queue(args.suite)
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n" for row in queue),
            encoding="utf-8",
        )
        console.print(f"Wrote {len(queue)} human-review tasks to {path}")
    elif args.command == "validate-labels":
        labels = read_expert_labels(Path(args.labels))
        console.print(f"Valid human labels: {len(labels)}")
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
    research_suites = list_research_suites()
    if research_suites and not suite_id:
        console.print(f"Research overlays: {', '.join(suite['suite_id'] for suite in research_suites)}")


def _print_result(console: Console, result: dict) -> None:
    action = result["outcome"]["action"]
    console.print(f"Run: {result['run_id']}")
    console.print(f"Action: {action['action']} {json.dumps(action.get('args', {}), ensure_ascii=True)}")
    console.print(f"Score: {result['score']['total']} {result['score']['label']}")
    console.print(f"Retry: {'yes' if result['outcome']['retry_used'] else 'no'}")
    console.print(f"Artifacts: runs/micro/{result['run_id']}")


if __name__ == "__main__":
    main()
