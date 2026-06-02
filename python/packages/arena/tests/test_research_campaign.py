from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from pathlib import Path

import pytest

from monopoly_arena.long_campaign import build_campaign_plan, load_campaign_config, run_campaign, write_campaign_plan
from monopoly_arena.research_registry import (
    get_model_roster,
    get_seed_cohort,
    load_model_roster_registry,
    load_seed_registry,
    validate_seed_registry,
)


def _campaign_config() -> dict:
    return load_campaign_config(Path("campaigns/monopoly-long-v1-smoke.json"))


def test_seed_registry_validates_required_cohorts() -> None:
    registry = load_seed_registry()
    for cohort_id in [
        "smoke",
        "easy",
        "normal",
        "volatile",
        "auction_heavy",
        "trade_heavy",
        "liquidation_heavy",
        "publication",
    ]:
        cohort = get_seed_cohort(cohort_id, registry)
        assert cohort["cohort_id"] == cohort_id
        assert cohort["seeds"]


def test_seed_registry_rejects_duplicate_seeds() -> None:
    registry = load_seed_registry()
    mutated = deepcopy(registry)
    smoke_seeds = mutated["cohorts"]["smoke"]["seeds"]
    smoke_seeds.append(deepcopy(smoke_seeds[0]))

    with pytest.raises(ValueError, match="duplicate seed"):
        validate_seed_registry(mutated)


def test_model_roster_registry_validates_and_rejects_disabled_roster_by_default() -> None:
    registry = load_model_roster_registry()
    smoke = get_model_roster("smoke", registry)
    assert len(smoke["actors"]) == 4

    baseline_mix = get_model_roster("baseline_mix", registry)
    assert any(actor["actor_type"] == "baseline" for actor in baseline_mix["actors"])

    baseline_field = get_model_roster("baseline_field", registry)
    assert all(actor["actor_type"] == "baseline" for actor in baseline_field["actors"])

    with pytest.raises(ValueError, match="disabled actors"):
        get_model_roster("frontier", registry)

    frontier = get_model_roster("frontier", registry, include_disabled=True)
    assert any(not actor["enabled"] for actor in frontier["actors"])


def test_smoke_campaign_plan_expands_every_seed_and_latin_square_seat() -> None:
    plan = build_campaign_plan(_campaign_config())
    rows = plan["run_matrix"]
    assert len(rows) == 8
    assert plan["campaign_manifest"]["run_count"] == 8
    assert plan["campaign_manifest"]["prompt_pipeline"]["status"] == "unchanged"

    first_seed_rows = [row for row in rows if row["seed"] == 101]
    assert len(first_seed_rows) == 4
    slot_to_seats: dict[str, set[int]] = {}
    for row in first_seed_rows:
        for actor in row["actors"]:
            slot_to_seats.setdefault(actor["roster_actor_ref"], set()).add(actor["seat_index"])
    assert set(slot_to_seats) == {"gpt_oss_120b_low#0", "gpt_oss_120b_medium#1", "qwen3_coder#2", "gpt_oss_120b_low#3"}
    assert all(seats == {0, 1, 2, 3} for seats in slot_to_seats.values())


def test_campaign_plan_run_ids_are_deterministic() -> None:
    first = build_campaign_plan(_campaign_config())["run_matrix"]
    second = build_campaign_plan(_campaign_config())["run_matrix"]
    assert [row["run_id"] for row in first] == [row["run_id"] for row in second]
    assert [row["resume_key"] for row in first] == [row["resume_key"] for row in second]


def test_baseline_mix_campaign_rows_expose_runner_baseline_strategies() -> None:
    config = _campaign_config()
    config["campaign_id"] = "monopoly-long-v1-baseline-mix-test"
    config["model_roster"] = "baseline_mix"
    config["seat_permutation"] = "configured_order"
    plan = build_campaign_plan(config)
    rows = plan["run_matrix"]

    assert len(rows) == 2
    assert all(row["contains_baseline"] for row in rows)
    assert all(row["runnable_with_current_batch_runner"] is False for row in rows)
    assert all(row["runnable_with_long_runner"] is True for row in rows)
    assert rows[0]["baseline_strategies"] == {
        "p2": "random_legal",
        "p3": "always_buy",
        "p4": "cash_conservative",
    }


def test_write_campaign_plan_writes_research_artifacts(tmp_path: Path) -> None:
    campaign_dir = write_campaign_plan(_campaign_config(), runs_dir=tmp_path)
    expected = {
        "campaign_config.json",
        "campaign_manifest.json",
        "seed_manifest.json",
        "model_roster.json",
        "baseline_roster.json",
        "run_matrix.json",
        "run_matrix.jsonl",
        "batch_runner_compatibility.json",
        "artifact_manifest.json",
    }
    assert {path.name for path in campaign_dir.iterdir() if path.is_file()} == expected

    matrix_lines = (campaign_dir / "run_matrix.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(matrix_lines) == 8
    first_row = json.loads(matrix_lines[0])
    assert first_row["prompt_pipeline"]["status"] == "unchanged"

    artifact_manifest = json.loads((campaign_dir / "artifact_manifest.json").read_text(encoding="utf-8"))
    assert artifact_manifest["prompt_pipeline"]["status"] == "unchanged"
    existing = {entry["label"] for entry in artifact_manifest["artifacts"] if entry["exists"]}
    planned = {entry["label"] for entry in artifact_manifest["artifacts"] if not entry["exists"]}
    assert {
        "campaign_config",
        "campaign_manifest",
        "seed_manifest",
        "model_roster",
        "baseline_roster",
        "run_matrix",
        "run_matrix_jsonl",
        "batch_runner_compatibility",
    }.issubset(existing)
    assert {"results", "run_results", "leaderboard", "statistics", "paper_report"}.issubset(planned)


class _NoOpenRouter:
    async def create_chat_completion(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("all-baseline campaign execution must not call OpenRouter")

    async def aclose(self) -> None:
        return None


def test_run_campaign_executes_one_all_baseline_cell_without_prompt_artifacts(tmp_path: Path) -> None:
    config = _campaign_config()
    config["campaign_id"] = "monopoly-long-v1-baseline-field-exec-test"
    config["model_roster"] = "baseline_field"
    config["seat_permutation"] = "configured_order"
    config["max_turns"] = 3
    config["continue_on_failure"] = True

    result = asyncio.run(
        run_campaign(
            config,
            runs_dir=tmp_path,
            openrouter_factory=_NoOpenRouter,
            max_runs=1,
            force_execute=True,
        )
    )

    assert result["completed_count"] == 1
    assert result["failed_count"] == 0

    campaign_dir = Path(result["campaign_dir"])
    for name in [
        "results.jsonl",
        "results.csv",
        "run_results.json",
        "leaderboard.json",
        "leaderboard.csv",
        "statistics.json",
        "baseline_comparison.json",
        "paper_report.md",
        "execution_result.json",
    ]:
        assert (campaign_dir / name).exists()

    run_results = json.loads((campaign_dir / "run_results.json").read_text(encoding="utf-8"))
    completed = [entry for entry in run_results["runs"] if entry["status"] == "completed"]
    assert len(completed) == 1
    assert all(player["actor_type"] == "baseline" for player in completed[0]["players"])
    assert completed[0]["artifact_counts"]["prompts"] == 0

    leaderboard = json.loads((campaign_dir / "leaderboard.json").read_text(encoding="utf-8"))
    assert leaderboard["rows"]
    assert all(row["actor_type"] == "baseline" for row in leaderboard["rows"])

    report = (campaign_dir / "paper_report.md").read_text(encoding="utf-8")
    assert "Prompt Invariant" in report
    assert "does not change prompt text" in report
