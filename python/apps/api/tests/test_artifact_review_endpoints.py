import json

from fastapi.testclient import TestClient

from monopoly_api.main import app, run_manager
from monopoly_telemetry import append_jsonl, init_run_files


def test_run_artifact_and_review_endpoints(tmp_path) -> None:
    run_files = init_run_files(tmp_path, "run-artifact-review")
    run_files.write_summary({"run_id": run_files.run_id, "winner_player_id": "p1"})
    run_files.write_json_artifact(
        run_files.scorecard_path,
        {
            "schema_version": "v1",
            "scorecard_version": "scorecard_v1",
            "run_id": run_files.run_id,
            "players": [],
        },
    )
    run_files.write_snapshot(
        {
            "schema_version": "v1",
            "run_id": run_files.run_id,
            "turn_index": 0,
            "phase": "SETUP",
            "players": [],
            "board": [],
        }
    )
    append_jsonl(
        run_files.review_queue_path,
        {
            "schema_version": "v1",
            "queue_item_id": "queue-1",
            "run_id": run_files.run_id,
            "finding_ids": ["finding-1"],
            "status": "pending",
        },
    )

    previous_state = {
        "run_id": run_manager._run_id,
        "telemetry": run_manager._telemetry,
        "decision_index": run_manager._decision_index,
    }
    run_manager._run_id = run_files.run_id
    run_manager._telemetry = run_files
    run_manager._decision_index = None
    try:
        client = TestClient(app)
        artifacts = client.get(f"/runs/{run_files.run_id}/artifacts")
        assert artifacts.status_code == 200
        artifact_names = {entry["name"] for entry in artifacts.json()["artifacts"]}
        assert "scorecard" in artifact_names
        assert "review_labels" in artifact_names

        scorecard = client.get(f"/runs/{run_files.run_id}/artifacts/scorecard")
        assert scorecard.status_code == 200
        assert scorecard.json()["content"]["scorecard_version"] == "scorecard_v1"

        snapshots = client.get(f"/runs/{run_files.run_id}/snapshots")
        assert snapshots.status_code == 200
        assert snapshots.json()["snapshots"][0]["name"] == "turn_0000.json"

        snapshot = client.get(f"/runs/{run_files.run_id}/snapshots/turn_0000.json")
        assert snapshot.status_code == 200
        assert snapshot.json()["content"]["turn_index"] == 0

        queue = client.get(f"/runs/{run_files.run_id}/review/queue")
        assert queue.status_code == 200
        assert queue.json()["queue"][0]["queue_item_id"] == "queue-1"

        queued = client.post(
            f"/runs/{run_files.run_id}/review/queue",
            json={
                "decision_id": "decision-user-selected",
                "turn_index": 2,
                "player_id": "p1",
                "reason_for_review": "user_selected_decision",
            },
        )
        assert queued.status_code == 200
        assert queued.json()["queue_item"]["reason_for_review"] == "user_selected_decision"

        created = client.post(
            f"/runs/{run_files.run_id}/review/labels",
            json={
                "queue_item_id": "queue-1",
                "selected_labels": ["deception_candidate"],
                "confidence": 0.75,
                "notes": "Needs human adjudication.",
            },
        )
        assert created.status_code == 200
        label = created.json()["label"]
        assert label["reviewer_id"] == "local_reviewer"
        assert label["selected_labels"] == ["deception_candidate"]

        labels = client.get(f"/runs/{run_files.run_id}/review/labels")
        assert labels.status_code == 200
        assert labels.json()["labels"][0]["label_id"] == label["label_id"]

        summary = client.get(f"/runs/{run_files.run_id}/review/summary")
        assert summary.status_code == 200
        assert summary.json()["label_count"] == 1
        assert summary.json()["by_label"] == {"deception_candidate": 1}

        artifact_labels = client.get(f"/runs/{run_files.run_id}/artifacts/review_labels")
        assert artifact_labels.status_code == 200
        assert artifact_labels.json()["rows"][0]["label_id"] == label["label_id"]
        raw_labels = run_files.review_labels_path.read_text(encoding="utf-8")
        assert json.loads(raw_labels.splitlines()[0])["reviewer_id"] == "local_reviewer"
    finally:
        run_manager._run_id = previous_state["run_id"]
        run_manager._telemetry = previous_state["telemetry"]
        run_manager._decision_index = previous_state["decision_index"]


def test_batch_artifact_and_model_card_endpoints(tmp_path) -> None:
    batch_dir = tmp_path / "batches" / "batch-api"
    model_cards_dir = batch_dir / "model_cards"
    model_cards_dir.mkdir(parents=True)
    (batch_dir / "batch_manifest.json").write_text(
        json.dumps(
            {
                "schema_version": "v1",
                "batch_manifest_version": "batch_manifest_v1",
                "batch_id": "batch-api",
                "run_count": 1,
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    (batch_dir / "batch_config.json").write_text('{"batch_id":"batch-api"}', encoding="utf-8")
    (batch_dir / "leaderboard.json").write_text('{"rankings":[]}', encoding="utf-8")
    (batch_dir / "results.jsonl").write_text('{"run_id":"run-1"}\n', encoding="utf-8")
    (model_cards_dir / "openai_gpt-test.json").write_text(
        '{"model_card_version":"model_card_v1","model_id":"openai/gpt-test"}',
        encoding="utf-8",
    )
    (model_cards_dir / "openai_gpt-test.md").write_text(
        "# openai/gpt-test\n\nPrivate thoughts: linked via replay/review artifacts, not quoted here\n",
        encoding="utf-8",
    )

    previous_runs_dir = run_manager._runs_dir
    run_manager._runs_dir = tmp_path
    try:
        client = TestClient(app)
        batches = client.get("/batches")
        assert batches.status_code == 200
        assert batches.json()["batches"][0]["batch_id"] == "batch-api"

        detail = client.get("/batches/batch-api")
        assert detail.status_code == 200
        assert detail.json()["manifest"]["run_count"] == 1

        artifacts = client.get("/batches/batch-api/artifacts")
        assert artifacts.status_code == 200
        assert artifacts.json()["model_cards"][0]["card_id"] == "openai_gpt-test"

        results = client.get("/batches/batch-api/artifacts/results")
        assert results.status_code == 200
        assert results.json()["rows"][0]["run_id"] == "run-1"

        card = client.get("/batches/batch-api/model_cards/openai_gpt-test")
        assert card.status_code == 200
        assert card.json()["json"]["model_card_version"] == "model_card_v1"
        assert "Private thoughts: linked" in card.json()["markdown"]
    finally:
        run_manager._runs_dir = previous_runs_dir


def test_run_dashboard_endpoints_tolerate_partial_run_directories(tmp_path) -> None:
    partial_run = tmp_path / "mock-partial-run"
    partial_run.mkdir()
    (partial_run / "summary.json").write_text("{", encoding="utf-8")

    matching_run = tmp_path / "mock-complete-run"
    matching_run.mkdir()
    (matching_run / "scorecard.json").write_text(
        json.dumps(
            {
                "players": [
                    {
                        "player_id": "p1",
                        "openrouter_model_id": "openai/gpt-test",
                        "winner": True,
                        "final_net_worth_estimate": 3200,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (matching_run / "usage.json").write_text(
        json.dumps(
            {
                "by_model": {
                    "openai/gpt-test": {
                        "cost": 1.25,
                        "total_tokens": 4200,
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    previous_runs_dir = run_manager._runs_dir
    run_manager._runs_dir = tmp_path
    try:
        client = TestClient(app)

        runs = client.get("/runs")
        assert runs.status_code == 200
        by_run_id = {run["run_id"]: run for run in runs.json()["runs"]}
        assert by_run_id["mock-partial-run"]["summary_exists"] is False
        assert by_run_id["mock-partial-run"]["scorecard_exists"] is False

        model = client.get("/models/openai__gpt-test")
        assert model.status_code == 200
        assert model.json()["model_id"] == "openai/gpt-test"
        assert model.json()["game_count"] == 1
        assert model.json()["total_tokens"] == 4200
    finally:
        run_manager._runs_dir = previous_runs_dir
