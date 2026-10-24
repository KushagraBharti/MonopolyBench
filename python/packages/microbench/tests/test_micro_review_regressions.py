import asyncio
import pytest
from monopoly_microbench.runner import run_suite, run_batch, run_batch_with_progress


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
