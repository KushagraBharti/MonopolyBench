from __future__ import annotations

import asyncio
from collections import defaultdict
import copy
import hashlib
import json

from monopoly_arena import OpenRouterResult, build_single_player_config
from monopoly_arena.player_config import DEFAULT_SYSTEM_PROMPT
from monopoly_arena.prompting import PromptMemory, build_prompt_bundle, build_space_key_by_index
from monopoly_microbench.catalog import get_suite, list_scenarios, validate_all, validate_scenario
from monopoly_microbench.runner import MicroRunConfig, get_run, run_batch, run_batch_with_progress, run_scenario, score_run
from monopoly_microbench.scorer import score_action


class ScriptedOpenRouter:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def create_chat_completion(self, **kwargs: object) -> OpenRouterResult:
        self.calls.append(dict(kwargs))
        return _tool_call_result("buy_property", {"private_thought": "scripted"})

    async def aclose(self) -> None:
        return None


class FailingOpenRouter:
    async def create_chat_completion(self, **_: object) -> OpenRouterResult:
        raise RuntimeError("scripted provider failure")

    async def aclose(self) -> None:
        return None


def _tool_call_result(name: str, args: dict[str, object]) -> OpenRouterResult:
    payload_args = {
        **args,
        "public_message": args.get("public_message", ""),
        "private_thought": args.get("private_thought", "scripted"),
    }
    response_json = {
        "id": "resp-1",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call-1",
                            "type": "function",
                            "function": {
                                "name": name,
                                "arguments": json.dumps(payload_args, separators=(",", ":"), ensure_ascii=True),
                            },
                        }
                    ],
                }
            }
        ],
    }
    return OpenRouterResult(
        ok=True,
        status_code=200,
        response_json=response_json,
        error=None,
        error_type=None,
        request_id="req-1",
        request_payload_raw=None,
        response_text=json.dumps(response_json, separators=(",", ":"), ensure_ascii=True),
    )


def test_catalog_validates_full_micro_v1() -> None:
    result = validate_all()
    assert result["scenario_count"] >= 130
    suite = get_suite("micro-v1")
    assert len(suite["scenario_ids"]) == 130


def test_reference_actions_score_preferred() -> None:
    for scenario in list_scenarios():
        score = score_action(scenario, scenario["reference_policy"]["action"])
        assert score["label"] in {"preferred", "acceptable"}
        assert score["total"] >= 0.5


def test_micro_v1_quality_diversity_bar() -> None:
    by_category: dict[str, list[dict]] = defaultdict(list)
    scenarios = list_scenarios()
    for scenario in scenarios:
        by_category[scenario["category"]].append(scenario)

    scenarios_with_three_criteria = 0
    scenario_specific_rationales = 0
    for category, items in by_category.items():
        descriptions = {item["description"] for item in items}
        rubric_signatures = {
            json.dumps(
                [(entry["criterion_id"], entry["type"], entry["params"]) for entry in item["evaluation"]["rubric"]],
                sort_keys=True,
            )
            for item in items
        }
        assert len(descriptions) >= 6, category
        assert len(rubric_signatures) >= 3, category
        for item in items:
            assert item["research_sources"], item["scenario_id"]
            assert item["notes"].get("trap_action"), item["scenario_id"]
            if len(item["evaluation"]["rubric"]) >= 3:
                scenarios_with_three_criteria += 1
            rationale = item["reference_policy"]["rationale"]
            assert "Reference policy follows" not in rationale
            if item["title"].split()[0].lower() in rationale.lower() or len(rationale.split()) >= 10:
                scenario_specific_rationales += 1

    assert scenarios_with_three_criteria / len(scenarios) >= 0.60
    assert scenario_specific_rationales / len(scenarios) >= 0.80


def test_micro_v1_research_grade_state_and_coarse_rubric_diversity() -> None:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for scenario in list_scenarios():
        by_category[scenario["category"]].append(scenario)

    minimum_state_signatures = {
        "LIQUIDATION": 8,
        "POST_TURN_STRATEGY": 10,
    }
    for category, items in by_category.items():
        coarse_rubric_signatures = {
            json.dumps(
                [(entry["criterion_id"], entry["type"]) for entry in item["evaluation"]["rubric"]],
                sort_keys=True,
            )
            for item in items
        }
        assert len(coarse_rubric_signatures) >= 3, category

        stripped_state_signatures = {
            _stable_hash(_strip_volatile_state_fields(item["decision_point"]["state"]))
            for item in items
        }
        assert len(stripped_state_signatures) >= minimum_state_signatures.get(category, min(6, len(items))), category


def test_catalog_rejects_invalid_legal_action_arg_schema() -> None:
    scenario = copy.deepcopy(
        next(item for item in list_scenarios() if item["scenario_id"] == "trade-propose-water-works-for-new-york-01")
    )
    trade_schema = scenario["decision_point"]["legal_actions"][0]["args_schema"]
    trade_schema["properties"]["offer"]["properties"]["properties"]["items"] = "string"
    try:
        validate_scenario(scenario)
    except ValueError as exc:
        assert "invalid args_schema" in str(exc) or "not valid under any" in str(exc)
    else:
        raise AssertionError("Expected invalid legal action args_schema to fail validation.")


def test_model_run_writes_isolated_result(tmp_path) -> None:
    result = asyncio.run(
        run_scenario(
            MicroRunConfig(
                scenario_id="buy-or-auction-vermont-light-blue-tempo-01",
                openrouter_model_id="test/model",
            ),
            runs_dir=tmp_path / "runs",
            openrouter_factory=ScriptedOpenRouter,
        )
    )
    run_id = result["run_id"]
    detail = get_run(run_id, runs_dir=tmp_path / "runs")
    assert detail["result"]["score"]["total"] >= 0.5
    assert (tmp_path / "runs" / "micro" / run_id / "result.json").exists()


def test_score_run_recomputes_existing_result(tmp_path) -> None:
    result = asyncio.run(
        run_scenario(
            MicroRunConfig(
                scenario_id="buy-or-auction-vermont-light-blue-tempo-01",
                openrouter_model_id="test/model",
            ),
            runs_dir=tmp_path / "runs",
            openrouter_factory=ScriptedOpenRouter,
        )
    )
    recomputed = score_run(result["run_id"], runs_dir=tmp_path / "runs")
    assert recomputed["score"] == result["score"]


def test_live_game_prompt_matches_normal_game_prompt() -> None:
    scenario = next(
        item for item in list_scenarios() if item["scenario_id"] == "buy-or-auction-vermont-light-blue-tempo-01"
    )
    player = build_single_player_config(player_id=scenario["decision_point"]["player_id"], name="Alpha", openrouter_model_id="test/model")
    memory = PromptMemory(space_key_by_index=build_space_key_by_index())
    normal_decision = copy.deepcopy(scenario["decision_point"])
    live_game_configured_decision = copy.deepcopy(scenario["decision_point"])
    live_game_configured_decision["micro_prompt_condition"] = "live_game"
    normal_bundle = build_prompt_bundle(
        normal_decision,
        player,
        memory=memory,
        space_key_by_index=build_space_key_by_index(),
    )
    configured_live_game_bundle = build_prompt_bundle(
        live_game_configured_decision,
        player,
        memory=memory,
        space_key_by_index=build_space_key_by_index(),
    )
    assert configured_live_game_bundle.system_prompt == DEFAULT_SYSTEM_PROMPT
    assert normal_bundle.user_payload == configured_live_game_bundle.user_payload
    assert "prompt_condition" not in configured_live_game_bundle.user_payload["action_state"]
    assert "full_protocol_state" not in configured_live_game_bundle.user_payload


def test_batch_runner_writes_leaderboard(tmp_path) -> None:
    batch = asyncio.run(
        run_batch(
            suite_id="micro-v1",
            model_ids=["test/model"],
            scenario_ids=["buy-or-auction-vermont-light-blue-tempo-01"],
            runs_dir=tmp_path / "runs",
            openrouter_factory=ScriptedOpenRouter,
        )
    )
    assert batch["leaderboard"]["rows"]


def test_progress_batch_continues_and_reports_failures(tmp_path) -> None:
    events: list[dict] = []

    async def on_progress(event: dict) -> None:
        events.append(event)

    batch = asyncio.run(
        run_batch_with_progress(
            suite_id="micro-v1",
            model_id="test/model",
            scenario_ids=[
                "buy-or-auction-vermont-light-blue-tempo-01",
                "auction-new-york-orange-completion-02",
            ],
            runs_dir=tmp_path / "runs",
            openrouter_factory=FailingOpenRouter,
            progress_callback=on_progress,
        )
    )
    assert batch["results"] == []
    assert len(batch["failures"]) == 2
    assert [event["event"] for event in events].count("scenario_failed") == 2
    assert events[-1]["event"] == "batch_completed"
    assert events[-1]["failed"] == 2
    assert (tmp_path / "runs" / "micro_batches" / batch["batch_id"] / "failures.jsonl").exists()


def test_tui_filtering_and_selection_helpers() -> None:
    from monopoly_microbench import tui

    state = tui.MicroTuiState(category="JAIL", search="cash")
    items = tui._filtered_scenarios(state)
    assert items
    assert all(item["category"] == "JAIL" for item in items)
    assert any("cash" in item["title"].lower() or "cash" in item["description"].lower() for item in items)
    state.selected_index = 10_000
    tui._clamp_selection(state)
    assert state.selected_index == len(items) - 1


def test_tui_keyboard_navigation_and_edit_helpers() -> None:
    from monopoly_microbench import tui

    state = tui.MicroTuiState()
    tui._apply_dashboard_key(state, tui.KeyPress("down"))
    assert state.selected_index == 1
    tui._apply_dashboard_key(state, tui.KeyPress("right"))
    assert state.category == "BUY_OR_AUCTION"
    tui._apply_dashboard_key(state, tui.KeyPress("tab"))
    assert state.focus == "actions"
    assert tui._apply_dashboard_key(state, tui.KeyPress("char", "r")) == "run_selected"

    tui._apply_dashboard_key(state, tui.KeyPress("char", "/"))
    assert state.input_mode == "search"
    for char in "orange":
        tui._apply_dashboard_key(state, tui.KeyPress("char", char))
    tui._apply_dashboard_key(state, tui.KeyPress("enter"))
    assert state.input_mode is None
    assert state.search.endswith("orange")
    tui._apply_dashboard_key(state, tui.KeyPress("char", "g"))
    assert state.reasoning_effort == "high"
    tui._apply_dashboard_key(state, tui.KeyPress("char", "n"))
    assert state.input_mode == "name"
    for _ in range(len(state.input_buffer)):
        tui._apply_dashboard_key(state, tui.KeyPress("backspace"))
    for char in "Tester":
        tui._apply_dashboard_key(state, tui.KeyPress("char", char))
    tui._apply_dashboard_key(state, tui.KeyPress("enter"))
    assert state.display_name == "Tester"


def test_tui_mouse_click_helpers() -> None:
    from monopoly_microbench import tui

    mouse = tui._parse_sgr_mouse("0;80;25M")
    assert mouse == tui.KeyPress("mouse", x=80, y=25)

    state = tui.MicroTuiState(terminal_width=100, terminal_height=40)
    regions = tui._layout_regions(state)
    action_x = regions["actions"][0] + 2
    action_y = regions["actions"][1] + 2
    assert tui._apply_dashboard_key(state, tui.KeyPress("mouse", x=action_x, y=action_y)) == "run_selected"
    assert state.focus == "actions"
    assert state.action_index == 0

    catalog_x = regions["catalog"][0] + 2
    catalog_y = regions["catalog"][1] + 4
    assert tui._apply_dashboard_key(state, tui.KeyPress("mouse", x=catalog_x, y=catalog_y)) is None
    assert state.focus == "catalog"
    assert state.selected_index == 0


def _strip_volatile_state_fields(payload: dict) -> dict:
    item = copy.deepcopy(payload)
    item.pop("run_id", None)
    item.pop("turn_index", None)
    return item


def _stable_hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
