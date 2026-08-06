from __future__ import annotations

import asyncio
import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from monopoly_arena import OpenRouterResult
from monopoly_arena.long_campaign import (
    _CampaignBillingGuard,
    _preflight_gate_stop_reason,
    build_campaign_plan,
    load_campaign_config,
    run_campaign,
    write_campaign_plan,
)
from monopoly_arena.paths import resolve_repo_root
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
        "pilot_random_v1",
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


def test_model_roster_registry_validates_and_rejects_disabled_roster_by_default() -> (
    None
):
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
            slot_to_seats.setdefault(actor["roster_actor_ref"], set()).add(
                actor["seat_index"]
            )
    assert set(slot_to_seats) == {
        "gpt_oss_120b_low#0",
        "gpt_oss_120b_medium#1",
        "qwen3_coder#2",
        "gpt_oss_120b_low#3",
    }
    assert all(seats == {0, 1, 2, 3} for seats in slot_to_seats.values())


def test_campaign_plan_run_ids_are_deterministic() -> None:
    first_plan = build_campaign_plan(_campaign_config())
    second_plan = build_campaign_plan(_campaign_config())
    first = first_plan["run_matrix"]
    second = second_plan["run_matrix"]
    assert [row["run_id"] for row in first] == [row["run_id"] for row in second]
    assert [row["resume_key"] for row in first] == [row["resume_key"] for row in second]
    assert first_plan["execution_manifest"] == second_plan["execution_manifest"]
    ordered = first_plan["execution_manifest"]["ordered_runs"]
    assert sorted(row["run_index"] for row in ordered) == list(range(len(first)))
    assert [row["run_index"] for row in ordered] != list(range(len(first)))
    assert first_plan["execution_manifest"]["concurrency_effective"] == 1


def test_frontier_campaign_rows_pin_provider_routes_without_sampling_overrides() -> (
    None
):
    config = _campaign_config()
    config["campaign_id"] = "monopoly-long-v1-frontier-provider-test"
    config["model_roster"] = "frontier_medium_4lab"
    config["seat_permutation"] = "configured_order"
    row = build_campaign_plan(config)["run_matrix"][0]

    by_actor = {actor["actor_id"]: actor for actor in row["actors"]}
    assert by_actor["openai_gpt_55_medium"]["provider"] == {
        "only": ["openai"],
        "allow_fallbacks": False,
    }
    assert by_actor["openai_gpt_55_medium"]["billing_policy"] == {
        "mode": "byok_required",
        "expected_provider": "OpenAI",
    }
    assert (
        by_actor["claude_opus_48_medium"]["billing_policy"]["mode"]
        == "openrouter_credits"
    )
    assert by_actor["claude_opus_48_medium"]["provider"]["only"] == ["anthropic"]
    assert by_actor["gemini_31_pro_preview_medium"]["provider"]["only"] == [
        "google-ai-studio"
    ]
    assert by_actor["grok_43_medium"]["provider"]["only"] == ["xai"]
    assert all(actor["top_p"] is None for actor in row["actors"])


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
        "execution_manifest.json",
        "execution_manifest.jsonl",
        "batch_runner_compatibility.json",
        "artifact_manifest.json",
    }
    assert {path.name for path in campaign_dir.iterdir() if path.is_file()} == expected

    matrix_lines = (
        (campaign_dir / "run_matrix.jsonl").read_text(encoding="utf-8").splitlines()
    )
    assert len(matrix_lines) == 8
    first_row = json.loads(matrix_lines[0])
    assert first_row["prompt_pipeline"]["status"] == "unchanged"

    artifact_manifest = json.loads(
        (campaign_dir / "artifact_manifest.json").read_text(encoding="utf-8")
    )
    assert artifact_manifest["prompt_pipeline"]["status"] == "unchanged"
    existing = {
        entry["label"] for entry in artifact_manifest["artifacts"] if entry["exists"]
    }
    planned = {
        entry["label"]
        for entry in artifact_manifest["artifacts"]
        if not entry["exists"]
    }
    assert {
        "campaign_config",
        "campaign_manifest",
        "seed_manifest",
        "model_roster",
        "baseline_roster",
        "run_matrix",
        "run_matrix_jsonl",
        "execution_manifest",
        "execution_manifest_jsonl",
        "batch_runner_compatibility",
    }.issubset(existing)
    assert {
        "results",
        "run_results",
        "leaderboard",
        "statistics",
        "paper_report",
    }.issubset(planned)


class _NoOpenRouter:
    async def create_chat_completion(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("all-baseline campaign execution must not call OpenRouter")

    async def aclose(self) -> None:
        return None


class _LowCreditOpenRouter:
    generation_call_count = 0

    async def create_chat_completion(self, *_args: object, **_kwargs: object) -> None:
        type(self).generation_call_count += 1
        raise AssertionError(
            "credit-gated campaign must not call a generation endpoint"
        )

    async def get_models(self) -> OpenRouterResult:
        return OpenRouterResult(
            ok=True,
            status_code=200,
            response_json={"data": []},
            error=None,
            error_type=None,
            request_id="models-request",
        )

    async def get_credits(self) -> OpenRouterResult:
        return OpenRouterResult(
            ok=True,
            status_code=200,
            response_json={
                "data": {
                    "total_credits": 100.0,
                    "total_usage": 90.0,
                }
            },
            error=None,
            error_type=None,
            request_id="credits-request",
        )

    async def aclose(self) -> None:
        return None


class _HighCreditOpenRouter(_LowCreditOpenRouter):
    async def get_credits(self) -> OpenRouterResult:
        return OpenRouterResult(
            ok=True,
            status_code=200,
            response_json={
                "data": {
                    "total_credits": 100.0,
                    "total_usage": 0.0,
                }
            },
            error=None,
            error_type=None,
            request_id="credits-request",
        )


def test_run_campaign_executes_one_all_baseline_cell_without_prompt_artifacts(
    tmp_path: Path,
) -> None:
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
        "endpoint_snapshot_before.json",
        "endpoint_snapshot_after.json",
        "credits_before.json",
        "credits_after.json",
        "execution_preflight_snapshot.json",
        "budget_report.json",
    ]:
        assert (campaign_dir / name).exists()

    run_results = json.loads(
        (campaign_dir / "run_results.json").read_text(encoding="utf-8")
    )
    completed = [
        entry for entry in run_results["runs"] if entry["status"] == "completed"
    ]
    assert len(completed) == 1
    assert all(player["actor_type"] == "baseline" for player in completed[0]["players"])
    assert completed[0]["artifact_counts"]["prompts"] == 0

    leaderboard = json.loads(
        (campaign_dir / "leaderboard.json").read_text(encoding="utf-8")
    )
    assert leaderboard["rows"]
    assert all(row["actor_type"] == "baseline" for row in leaderboard["rows"])

    report = (campaign_dir / "paper_report.md").read_text(encoding="utf-8")
    assert "Prompt Invariant" in report
    assert "does not change prompt text" in report


def test_credit_gate_preserves_every_planned_cell_without_generation_calls(
    tmp_path: Path,
) -> None:
    config = _campaign_config()
    config["campaign_id"] = "monopoly-long-v1-credit-gate-test"
    config["model_roster"] = "frontier_medium_4lab"
    config["seat_permutation"] = "configured_order"
    config["minimum_available_credits"] = 20.0
    _LowCreditOpenRouter.generation_call_count = 0

    result = asyncio.run(
        run_campaign(
            config,
            runs_dir=tmp_path,
            openrouter_factory=_LowCreditOpenRouter,
            force_execute=True,
        )
    )

    run_results = json.loads(
        (Path(result["campaign_dir"]) / "run_results.json").read_text(encoding="utf-8")
    )
    assert len(run_results["runs"]) == 2
    assert {entry["status"] for entry in run_results["runs"]} == {
        "not_started_credit_gate"
    }
    assert result["stop_reason"] == "available_credit_10.0_below_required_20.0"
    assert result["actual_cost"] == 0
    assert _LowCreditOpenRouter.generation_call_count == 0


def test_e1_pilot_config_fails_closed_with_all_eight_cells_on_low_credit(
    tmp_path: Path,
) -> None:
    config = load_campaign_config(
        Path("campaigns/monopoly-long-v1-e1-pilot-random-v1.json")
    )
    _LowCreditOpenRouter.generation_call_count = 0

    result = asyncio.run(
        run_campaign(
            config,
            runs_dir=tmp_path,
            openrouter_factory=_LowCreditOpenRouter,
            force_execute=True,
        )
    )

    run_results = json.loads(
        (Path(result["campaign_dir"]) / "run_results.json").read_text(encoding="utf-8")
    )
    assert len(run_results["runs"]) == 8
    assert {entry["status"] for entry in run_results["runs"]} == {
        "not_started_credit_gate"
    }
    assert result["actual_cost"] == 0
    assert _LowCreditOpenRouter.generation_call_count == 0


def test_required_preflight_gate_fails_closed_before_generation(
    tmp_path: Path,
) -> None:
    preflight_path = tmp_path / "preflight.json"
    preflight_path.write_text(
        json.dumps(
            {
                "schema_version": "v1",
                "preflight_version": "openrouter_campaign_preflight_v2",
                "observed_at_utc": "2026-07-29T00:00:00Z",
                "roster_id": "frontier_medium_4lab",
                "credits": {
                    "available_credits": 100.0,
                },
                "verdict": {
                    "all_tool_calls_ready": True,
                    "all_billing_policies_satisfied": True,
                    "openai_byok_ready": True,
                    "all_routes_ready": True,
                    "paid_pilot_authorized_by_preflight": False,
                },
                "provenance": {
                    "registry_sha256": "not-reached-because-authorization-is-false",
                },
            }
        ),
        encoding="utf-8",
    )
    config = _campaign_config()
    config["campaign_id"] = "monopoly-long-v1-preflight-gate-test"
    config["model_roster"] = "frontier_medium_4lab"
    config["seat_permutation"] = "configured_order"
    config["minimum_available_credits"] = 20.0
    config["execution_preflight_path"] = str(preflight_path)
    config["maximum_preflight_age_hours"] = 6.0
    config["require_preflight_authorization"] = True
    _HighCreditOpenRouter.generation_call_count = 0

    result = asyncio.run(
        run_campaign(
            config,
            runs_dir=tmp_path / "runs",
            openrouter_factory=_HighCreditOpenRouter,
            force_execute=True,
        )
    )

    run_results = json.loads(
        (Path(result["campaign_dir"]) / "run_results.json").read_text(encoding="utf-8")
    )
    assert {entry["status"] for entry in run_results["runs"]} == {
        "not_started_preflight_gate"
    }
    assert result["stop_reason"] == "preflight_gate_not_authorized"
    assert _HighCreditOpenRouter.generation_call_count == 0


def test_current_authorized_preflight_shape_opens_the_preflight_gate() -> None:
    registry_path = (
        resolve_repo_root()
        / "contracts"
        / "research"
        / "monopoly_long_v1_model_rosters.json"
    )
    registry_sha256 = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    config = {
        "require_preflight_authorization": True,
        "model_roster": "frontier_medium_4lab",
        "maximum_preflight_age_hours": 6.0,
        "minimum_available_credits": 110.0,
    }
    snapshot = {
        "status": "ok",
        "payload": {
            "preflight_version": "openrouter_campaign_preflight_v2",
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "roster_id": "frontier_medium_4lab",
            "credits": {
                "available_credits": 110.0,
            },
            "verdict": {
                "all_tool_calls_ready": True,
                "all_billing_policies_satisfied": True,
                "openai_byok_ready": True,
                "all_routes_ready": True,
                "paid_pilot_authorized_by_preflight": True,
            },
            "provenance": {
                "registry_sha256": registry_sha256,
            },
        },
    }

    assert _preflight_gate_stop_reason(config, snapshot) is None


class _BillingResponseOpenRouter:
    def __init__(self, *, is_byok: bool, provider: str = "OpenAI") -> None:
        self.is_byok = is_byok
        self.provider = provider

    async def create_chat_completion(self, **kwargs: object) -> OpenRouterResult:
        return OpenRouterResult(
            ok=True,
            status_code=200,
            response_json={
                "id": "generation-test",
                "model": kwargs["model"],
                "provider": self.provider,
                "choices": [],
                "usage": {"is_byok": self.is_byok, "cost": 0.0},
            },
            error=None,
            error_type=None,
            request_id="generation-test",
        )

    async def aclose(self) -> None:
        return None


def _openai_billing_guard(tmp_path: Path, *, is_byok: bool) -> _CampaignBillingGuard:
    return _CampaignBillingGuard(
        delegate=_BillingResponseOpenRouter(is_byok=is_byok),
        policies_by_model={
            "openai/gpt-5.5": {
                "actor_id": "openai_gpt_55_medium",
                "provider_route": {"only": ["openai"], "allow_fallbacks": False},
                "billing_policy": {
                    "mode": "byok_required",
                    "expected_provider": "OpenAI",
                },
            }
        },
        run_dir=tmp_path,
    )


def test_campaign_billing_guard_accepts_confirmed_openai_byok(tmp_path: Path) -> None:
    guard = _openai_billing_guard(tmp_path, is_byok=True)
    result = asyncio.run(
        guard.create_chat_completion(
            model="openai/gpt-5.5",
            provider={"only": ["openai"], "allow_fallbacks": False},
        )
    )
    assert result.ok is True
    assert not (tmp_path / "billing_policy_violation.json").exists()


def test_campaign_billing_guard_fails_before_action_when_openai_is_not_byok(
    tmp_path: Path,
) -> None:
    guard = _openai_billing_guard(tmp_path, is_byok=False)
    with pytest.raises(RuntimeError, match="required_byok_not_confirmed"):
        asyncio.run(
            guard.create_chat_completion(
                model="openai/gpt-5.5",
                provider={"only": ["openai"], "allow_fallbacks": False},
            )
        )
    violation = json.loads(
        (tmp_path / "billing_policy_violation.json").read_text(encoding="utf-8")
    )
    assert violation["action_applied"] is False
    assert violation["violations"] == ["required_byok_not_confirmed"]


def test_zero_budget_preserves_every_planned_cell_as_not_started(
    tmp_path: Path,
) -> None:
    config = _campaign_config()
    config["campaign_id"] = "monopoly-long-v1-zero-budget-test"
    config["model_roster"] = "baseline_field"
    config["seat_permutation"] = "configured_order"
    config["cost_budget"] = 0

    result = asyncio.run(
        run_campaign(
            config,
            runs_dir=tmp_path,
            openrouter_factory=_NoOpenRouter,
            force_execute=True,
        )
    )

    run_results = json.loads(
        (Path(result["campaign_dir"]) / "run_results.json").read_text(encoding="utf-8")
    )
    assert len(run_results["runs"]) == 2
    assert {entry["status"] for entry in run_results["runs"]} == {
        "not_started_budget_stop"
    }
    assert result["actual_cost"] == 0


def test_failure_halt_preserves_later_planned_cells(tmp_path: Path) -> None:
    config = _campaign_config()
    config["campaign_id"] = "monopoly-long-v1-failure-ledger-test"
    config["model_roster"] = "baseline_field"
    config["seat_permutation"] = "configured_order"
    config["continue_on_failure"] = False
    plan = build_campaign_plan(config)
    first = min(plan["run_matrix"], key=lambda row: row["execution_rank"])
    blocked_run_dir = tmp_path / first["run_id"]
    blocked_run_dir.mkdir(parents=True)
    (blocked_run_dir / "incomplete.marker").write_text(
        "intentional test fixture", encoding="utf-8"
    )

    result = asyncio.run(
        run_campaign(
            config,
            runs_dir=tmp_path,
            openrouter_factory=_NoOpenRouter,
            force_execute=True,
        )
    )

    run_results = json.loads(
        (Path(result["campaign_dir"]) / "run_results.json").read_text(encoding="utf-8")
    )
    assert len(run_results["runs"]) == 2
    assert run_results["runs"][0]["status"] == "failed"
    assert run_results["runs"][1]["status"] == "not_started_after_failure"
