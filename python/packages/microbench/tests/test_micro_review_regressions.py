import asyncio
import json
import pytest
from monopoly_arena import OpenRouterResult
from monopoly_microbench.runner import MicroRunConfig, run_scenario, run_suite, run_batch, run_batch_with_progress


@pytest.mark.parametrize("entrypoint", ["suite", "batch", "progress"])
def test_entire_selection_is_screened_before_client_creation(tmp_path, entrypoint):
    calls = []

    def client_factory():
        calls.append(True)
        raise AssertionError("Provider client constructed before fixture preflight")

    kwargs = {"suite_id": "micro-v1", "runs_dir": tmp_path, "openrouter_factory": client_factory}
    if entrypoint == "suite":
        coroutine = run_suite(**kwargs, model_id="test/model")
    elif entrypoint == "batch":
        coroutine = run_batch(**kwargs, model_ids=["test/model"])
    else:
        coroutine = run_batch_with_progress(**kwargs, model_id="test/model")
    with pytest.raises(ValueError, match="[Qq]uarantin"):
        asyncio.run(coroutine)
    assert calls == []


@pytest.mark.parametrize("failure", ["exception", "account"])
def test_failed_micro_request_closes_client_and_accounts_for_call(tmp_path, failure):
    class Client:
        closed = False

        async def create_chat_completion(self, **kwargs):
            if failure == "exception":
                raise RuntimeError("Connection lost after submission")
            return OpenRouterResult(False, 402, None, "Account unavailable", "http_error", None)

        async def aclose(self):
            self.closed = True

    client = Client()
    with pytest.raises(RuntimeError):
        asyncio.run(run_scenario(MicroRunConfig(
            scenario_id="buy-or-auction-boardwalk-fame-bias-low-cash-15", run_id="failed-micro"),
            runs_dir=tmp_path, openrouter_factory=lambda: client))
    assert client.closed
    run_dir = next(tmp_path.rglob("failed-micro"))
    assert json.loads((run_dir / "failure.json").read_text())["complete"] is False
    usage = json.loads((run_dir / "usage.json").read_text())
    assert usage["attempt_count"] == 1
    assert not (run_dir / "actions.jsonl").exists()
    assert not (run_dir / "result.json").exists()
