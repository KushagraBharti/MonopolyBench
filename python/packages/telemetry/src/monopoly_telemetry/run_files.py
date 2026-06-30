from __future__ import annotations

from datetime import datetime, timezone
import json
import re
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .writer_jsonl import append_jsonl


@dataclass
class RunFiles:
    run_id: str
    run_dir: Path
    events_path: Path
    decisions_path: Path
    actions_path: Path
    snapshots_dir: Path
    prompts_dir: Path
    quality_dir: Path | None
    summary_path: Path
    run_config_path: Path
    players_path: Path
    seat_assignment_path: Path
    artifact_manifest_path: Path
    scorecard_path: Path
    scorecard_players_path: Path
    scorecard_decisions_path: Path
    scorecard_events_path: Path
    usage_path: Path
    usage_decisions_path: Path
    usage_attempts_path: Path
    pricing_snapshot_path: Path
    cost_report_path: Path
    experiment_manifest_path: Path
    review_cost_aggregate_path: Path
    review_cost_calls_path: Path
    replay_report_path: Path
    state_replay_report_path: Path
    artifact_replay_report_path: Path
    replay_steps_path: Path
    replay_flags_path: Path
    replay_navigation_path: Path
    replay_diff_path: Path
    event_hashes_path: Path
    trace_findings_path: Path
    trace_summary_path: Path
    timeline_path: Path
    decision_index_path: Path
    turn_index_path: Path
    player_timelines_path: Path
    negotiation_threads_path: Path
    auction_threads_path: Path
    asset_flow_path: Path
    cash_flow_path: Path
    behavioral_flags_path: Path
    failure_findings_path: Path
    failure_summary_path: Path
    review_queue_path: Path
    reviews_dir: Path
    review_labels_path: Path
    review_summary_path: Path
    model_cards_dir: Path

    def write_event(self, event: dict[str, Any]) -> None:
        append_jsonl(self.events_path, event)

    def write_snapshot(self, snapshot: dict[str, Any]) -> Path:
        turn_index = snapshot.get("turn_index", 0)
        canonical_path = self.snapshots_dir / f"turn_{turn_index:04d}.json"
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(snapshot, separators=(",", ":"), ensure_ascii=True)
        if not canonical_path.exists():
            canonical_path.write_text(payload, encoding="utf-8")
            return canonical_path

        existing = canonical_path.read_text(encoding="utf-8")
        if existing == payload:
            return canonical_path

        phase = str(snapshot.get("phase") or "UNKNOWN")
        variant_kind = "decision" if phase == "AWAITING_DECISION" else "snapshot"
        variant_path = _next_snapshot_variant_path(self.snapshots_dir, int(turn_index), variant_kind)
        variant_path.write_text(payload, encoding="utf-8")
        return variant_path

    def write_summary(self, summary: dict[str, Any]) -> None:
        self.summary_path.parent.mkdir(parents=True, exist_ok=True)
        self.summary_path.write_text(
            json.dumps(summary, separators=(",", ":"), ensure_ascii=True),
            encoding="utf-8",
        )

    def write_json_artifact(self, path: Path, payload: dict[str, Any] | list[Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, separators=(",", ":"), ensure_ascii=True),
            encoding="utf-8",
        )

    def write_run_config(self, payload: dict[str, Any]) -> None:
        self.write_json_artifact(self.run_config_path, payload)

    def write_players(self, payload: dict[str, Any]) -> None:
        self.write_json_artifact(self.players_path, payload)

    def write_seat_assignment(self, payload: dict[str, Any]) -> None:
        self.write_json_artifact(self.seat_assignment_path, payload)

    def write_decision(self, decision_entry: dict[str, Any]) -> None:
        append_jsonl(self.decisions_path, decision_entry)

    def write_action(self, action_entry: dict[str, Any]) -> None:
        append_jsonl(self.actions_path, action_entry)

    def write_prompt_artifacts(
        self,
        *,
        decision_id: str,
        attempt_index: int,
        system_prompt: str | None,
        user_payload: dict[str, Any] | None,
        tools: list[dict[str, Any]] | None,
        response: dict[str, Any] | None,
        parsed: dict[str, Any] | None,
    ) -> None:
        prefix = _prompt_file_prefix(decision_id, attempt_index=attempt_index)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        try:
            self._write_prompt_artifact_files(
                prefix=prefix,
                system_prompt=system_prompt,
                user_payload=user_payload,
                tools=tools,
                response=response,
                parsed=parsed,
            )
        except OSError:
            compact_prefix = _compact_prompt_file_prefix(decision_id, attempt_index=attempt_index)
            if compact_prefix == prefix:
                raise
            self._write_prompt_artifact_files(
                prefix=compact_prefix,
                system_prompt=system_prompt,
                user_payload=user_payload,
                tools=tools,
                response=response,
                parsed=parsed,
            )

    def _write_prompt_artifact_files(
        self,
        *,
        prefix: str,
        system_prompt: str | None,
        user_payload: dict[str, Any] | None,
        tools: list[dict[str, Any]] | None,
        response: dict[str, Any] | None,
        parsed: dict[str, Any] | None,
    ) -> None:
        if system_prompt is not None:
            (self.prompts_dir / f"{prefix}_system.txt").write_text(system_prompt, encoding="utf-8")
        if user_payload is not None:
            (self.prompts_dir / f"{prefix}_user.json").write_text(
                json.dumps(user_payload, separators=(",", ":"), ensure_ascii=True),
                encoding="utf-8",
            )
        if tools is not None:
            (self.prompts_dir / f"{prefix}_tools.json").write_text(
                json.dumps(tools, separators=(",", ":"), ensure_ascii=True),
                encoding="utf-8",
            )
        if response is not None:
            (self.prompts_dir / f"{prefix}_response.json").write_text(
                json.dumps(response, separators=(",", ":"), ensure_ascii=True),
                encoding="utf-8",
            )
        if parsed is not None:
            (self.prompts_dir / f"{prefix}_parsed.json").write_text(
                json.dumps(parsed, separators=(",", ":"), ensure_ascii=True),
                encoding="utf-8",
            )

    def write_quality_artifacts(
        self,
        *,
        decision_id: str,
        attempt_index: int,
        request_text: str | None,
        response_text: str | None,
    ) -> None:
        if self.quality_dir is None:
            return
        prefix = _prompt_file_prefix(decision_id, attempt_index=attempt_index)
        self.quality_dir.mkdir(parents=True, exist_ok=True)
        if request_text is not None:
            (self.quality_dir / f"{prefix}_request.txt").write_text(request_text, encoding="utf-8")
        if response_text is not None:
            (self.quality_dir / f"{prefix}_response.txt").write_text(response_text, encoding="utf-8")

    def write_artifact_manifest(self) -> None:
        self.write_json_artifact(self.artifact_manifest_path, build_artifact_manifest(self))


def init_run_files(runs_dir: Path, run_id: str) -> RunFiles:
    run_files = build_run_files(runs_dir, run_id)
    run_files.snapshots_dir.mkdir(parents=True, exist_ok=True)
    return run_files


def build_run_files(
    runs_dir: Path,
    run_id: str,
    *,
    quality_base_dir: Path | None = None,
) -> RunFiles:
    run_dir = runs_dir / run_id
    snapshots_dir = run_dir / "state"
    prompts_dir = run_dir / "prompts"
    quality_root = quality_base_dir if quality_base_dir is not None else runs_dir.parent / "quality_check"
    quality_dir = quality_root / run_id
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    return RunFiles(
        run_id=run_id,
        run_dir=run_dir,
        events_path=run_dir / "events.jsonl",
        decisions_path=run_dir / "decisions.jsonl",
        actions_path=run_dir / "actions.jsonl",
        snapshots_dir=snapshots_dir,
        prompts_dir=prompts_dir,
        quality_dir=quality_dir,
        summary_path=run_dir / "summary.json",
        run_config_path=run_dir / "run_config.json",
        players_path=run_dir / "players.json",
        seat_assignment_path=run_dir / "seat_assignment.json",
        artifact_manifest_path=run_dir / "artifact_manifest.json",
        scorecard_path=run_dir / "scorecard.json",
        scorecard_players_path=run_dir / "scorecard_players.json",
        scorecard_decisions_path=run_dir / "scorecard_decisions.jsonl",
        scorecard_events_path=run_dir / "scorecard_events.jsonl",
        usage_path=run_dir / "usage.json",
        usage_decisions_path=run_dir / "usage_decisions.jsonl",
        usage_attempts_path=run_dir / "usage_attempts.jsonl",
        pricing_snapshot_path=run_dir / "pricing_snapshot.json",
        cost_report_path=run_dir / "cost_report.json",
        experiment_manifest_path=run_dir / "experiment_manifest.json",
        review_cost_aggregate_path=run_dir / "review_cost_aggregate.json",
        review_cost_calls_path=run_dir / "review_cost_calls.jsonl",
        replay_report_path=run_dir / "replay_report.json",
        state_replay_report_path=run_dir / "state_replay_report.json",
        artifact_replay_report_path=run_dir / "artifact_replay_report.json",
        replay_steps_path=run_dir / "replay_steps.jsonl",
        replay_flags_path=run_dir / "replay_flags.jsonl",
        replay_navigation_path=run_dir / "replay_navigation.json",
        replay_diff_path=run_dir / "replay_diff.json",
        event_hashes_path=run_dir / "event_hashes.json",
        trace_findings_path=run_dir / "trace_findings.jsonl",
        trace_summary_path=run_dir / "trace_summary.json",
        timeline_path=run_dir / "timeline.json",
        decision_index_path=run_dir / "decision_index.json",
        turn_index_path=run_dir / "turn_index.json",
        player_timelines_path=run_dir / "player_timelines.json",
        negotiation_threads_path=run_dir / "negotiation_threads.jsonl",
        auction_threads_path=run_dir / "auction_threads.jsonl",
        asset_flow_path=run_dir / "asset_flow.jsonl",
        cash_flow_path=run_dir / "cash_flow.jsonl",
        behavioral_flags_path=run_dir / "behavioral_flags.jsonl",
        failure_findings_path=run_dir / "failure_findings.jsonl",
        failure_summary_path=run_dir / "failure_summary.json",
        review_queue_path=run_dir / "review_queue.jsonl",
        reviews_dir=run_dir / "reviews",
        review_labels_path=run_dir / "reviews" / "review_labels.jsonl",
        review_summary_path=run_dir / "reviews" / "review_summary.json",
        model_cards_dir=run_dir / "model_cards",
    )


def build_artifact_manifest(run_files: RunFiles) -> dict[str, Any]:
    known_paths = _known_artifact_paths(run_files)
    artifacts: list[dict[str, Any]] = []
    for label, path in known_paths:
        if path == run_files.artifact_manifest_path:
            continue
        artifacts.append(_artifact_entry(label, run_files.run_dir, path))
    return {
        "schema_version": "v1",
        "manifest_version": "artifact_manifest_v1",
        "run_id": run_files.run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_files.run_dir),
        "artifacts": artifacts,
    }


def _known_artifact_paths(run_files: RunFiles) -> list[tuple[str, Path]]:
    return [
        ("events", run_files.events_path),
        ("decisions", run_files.decisions_path),
        ("actions", run_files.actions_path),
        ("summary", run_files.summary_path),
        ("run_config", run_files.run_config_path),
        ("players", run_files.players_path),
        ("seat_assignment", run_files.seat_assignment_path),
        ("scorecard", run_files.scorecard_path),
        ("scorecard_players", run_files.scorecard_players_path),
        ("scorecard_decisions", run_files.scorecard_decisions_path),
        ("scorecard_events", run_files.scorecard_events_path),
        ("usage", run_files.usage_path),
        ("usage_decisions", run_files.usage_decisions_path),
        ("usage_attempts", run_files.usage_attempts_path),
        ("pricing_snapshot", run_files.pricing_snapshot_path),
        ("cost_report", run_files.cost_report_path),
        ("experiment_manifest", run_files.experiment_manifest_path),
        ("review_cost_aggregate", run_files.review_cost_aggregate_path),
        ("review_cost_calls", run_files.review_cost_calls_path),
        ("replay_report", run_files.replay_report_path),
        ("state_replay_report", run_files.state_replay_report_path),
        ("artifact_replay_report", run_files.artifact_replay_report_path),
        ("replay_steps", run_files.replay_steps_path),
        ("replay_flags", run_files.replay_flags_path),
        ("replay_navigation", run_files.replay_navigation_path),
        ("replay_diff", run_files.replay_diff_path),
        ("event_hashes", run_files.event_hashes_path),
        ("trace_findings", run_files.trace_findings_path),
        ("trace_summary", run_files.trace_summary_path),
        ("timeline", run_files.timeline_path),
        ("decision_index", run_files.decision_index_path),
        ("turn_index", run_files.turn_index_path),
        ("player_timelines", run_files.player_timelines_path),
        ("negotiation_threads", run_files.negotiation_threads_path),
        ("auction_threads", run_files.auction_threads_path),
        ("asset_flow", run_files.asset_flow_path),
        ("cash_flow", run_files.cash_flow_path),
        ("behavioral_flags", run_files.behavioral_flags_path),
        ("failure_findings", run_files.failure_findings_path),
        ("failure_summary", run_files.failure_summary_path),
        ("review_queue", run_files.review_queue_path),
        ("review_labels", run_files.review_labels_path),
        ("review_summary", run_files.review_summary_path),
        ("artifact_manifest", run_files.artifact_manifest_path),
    ]


def _artifact_entry(label: str, run_dir: Path, path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "label": label,
        "path": str(path),
        "relative_path": _relative_path(run_dir, path),
        "exists": path.exists(),
    }
    if path.exists() and path.is_file():
        data = path.read_bytes()
        entry["bytes"] = len(data)
        entry["sha256"] = hashlib.sha256(data).hexdigest()
    return entry


def _relative_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _prompt_file_prefix(decision_id: str, *, attempt_index: int) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", decision_id.strip())
    safe = safe.strip("._-") or "decision"
    if attempt_index <= 0:
        return f"decision_{safe}"
    return f"decision_{safe}_retry{attempt_index}"


def _compact_prompt_file_prefix(decision_id: str, *, attempt_index: int) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", decision_id.strip())
    safe = safe.strip("._-") or "decision"
    digest = hashlib.sha1(safe.encode("utf-8")).hexdigest()[:10]
    safe = f"{safe[:23]}-{digest}"
    if attempt_index <= 0:
        return f"decision_{safe}"
    return f"decision_{safe}_retry{attempt_index}"


def _next_snapshot_variant_path(snapshots_dir: Path, turn_index: int, kind: str) -> Path:
    prefix = f"turn_{turn_index:04d}_{kind}_"
    pattern = re.compile(rf"^{re.escape(prefix)}(?P<num>[0-9]+)\.json$")
    max_seen = 0
    if snapshots_dir.exists():
        for path in snapshots_dir.iterdir():
            if not path.is_file():
                continue
            match = pattern.match(path.name)
            if not match:
                continue
            try:
                num = int(match.group("num"))
            except (TypeError, ValueError):
                continue
            if num > max_seen:
                max_seen = num
    return snapshots_dir / f"{prefix}{max_seen + 1:04d}.json"
