from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


CAMPAIGN_ID = "monopoly-long-v1-e1-pilot-random-v1"
DEFAULT_CAMPAIGN_DIR = "runs/campaigns/monopoly-long-v1-e1-pilot-random-v1"
DEFAULT_VALIDATION = "analysis/research_protocol/pilot/e1_validation.json"
DEFAULT_OUTPUT_DIR = "analysis/research_protocol/pilot/e1_analysis_matrix"
BLINDING_DOMAIN = "monopolybench-e1-nuisance-v1"
TURN_SNAPSHOT_PATTERN = re.compile(r"^turn_(\d{4})\.json$")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the blinded E1 nuisance-analysis matrix from validated runs."
    )
    parser.add_argument("--campaign-dir", default=DEFAULT_CAMPAIGN_DIR)
    parser.add_argument("--validation", default=DEFAULT_VALIDATION)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Return exit 2 unless the analysis matrix is built from a passing E1 campaign.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    campaign_dir = (repo_root / args.campaign_dir).resolve()
    validation_path = (repo_root / args.validation).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    validation = _read_json(validation_path)
    if validation.get("empirical_gate_passed") is not True:
        payload = _blocked_manifest(repo_root, campaign_dir, validation_path, validation)
        _write_json(output_dir / "manifest.json", payload)
        (output_dir / "README.md").write_text(_blocked_markdown(payload), encoding="utf-8")
        print(
            json.dumps(
                {
                    "output": _relative(repo_root, output_dir / "manifest.json"),
                    "provider_calls": 0,
                    "status": payload["status"],
                },
                sort_keys=True,
            )
        )
        return 2 if args.require_complete else 0

    run_results_path = campaign_dir / "run_results.json"
    run_results = [_dict(value) for value in _list(_read_json(run_results_path).get("runs"))]
    rows = [row for row in run_results if row.get("status") in {"completed", "resumed_completed"}]
    if len(rows) < 6:
        raise ValueError("At least six integrity-eligible E1 games are required to choose horizons.")

    terminal_turns = [_terminal_turn_index(_run_dir(repo_root, row)) for row in rows]
    common_horizon = _common_horizon(terminal_turns)
    survival_horizon = _survival_horizon(terminal_turns, common_horizon)
    actor_ids = sorted(
        {
            str(player.get("actor_id"))
            for row in rows
            for player in _list(row.get("players"))
            if player.get("actor_id")
        }
    )
    actor_codes = _blind_actor_codes(actor_ids)

    observation_rows: list[dict[str, Any]] = []
    source_hashes: list[dict[str, Any]] = []
    for campaign_row in rows:
        run_dir = _run_dir(repo_root, campaign_row)
        run_observations, run_hashes = _run_observations(
            repo_root=repo_root,
            campaign_row=campaign_row,
            run_dir=run_dir,
            actor_codes=actor_codes,
            common_horizon=common_horizon,
            survival_horizon=survival_horizon,
        )
        observation_rows.extend(run_observations)
        source_hashes.extend(run_hashes)

    block_rows = _block_summary(observation_rows)
    observations_path = output_dir / "observations.csv"
    blocks_path = output_dir / "block_summary.csv"
    _write_csv(observations_path, observation_rows)
    _write_csv(blocks_path, block_rows)
    payload = {
        "schema_version": "e1_analysis_matrix_manifest_v1",
        "generated_at_utc": _utc_now(),
        "status": "complete",
        "campaign_id": CAMPAIGN_ID,
        "source_commit": _git_head(repo_root),
        "provider_calls": 0,
        "game_count": len(rows),
        "seed_block_count": len({row["seed"] for row in observation_rows}),
        "actor_count": len(actor_codes),
        "observation_count": len(observation_rows),
        "terminal_turn_distribution": {
            "values": sorted(terminal_turns),
            "q25": _quantile(sorted(terminal_turns), 0.25),
            "q75": _quantile(sorted(terminal_turns), 0.75),
        },
        "horizons": {
            "common_net_worth_auc_horizon": common_horizon,
            "restricted_survival_horizon": survival_horizon,
            "selection_rule": (
                "Hc=max(20,min(200,10*floor(Q25/10))); "
                "H=max(Hc,min(300,10*floor(Q75/10)))"
            ),
            "labels_used_for_selection": False,
        },
        "blinding": {
            "status": "actor_identity_not_emitted",
            "domain": BLINDING_DOMAIN,
            "actor_codes": sorted(actor_codes.values()),
            "note": (
                "Codes are assigned by sorting domain-separated actor hashes. "
                "The code-to-identity mapping is intentionally absent from generated outputs."
            ),
        },
        "estimands": {
            "placement_superiority": "(4-final_rank)/3 within each game",
            "restricted_survival": "min(bankruptcy_turn or terminal_turn, H)",
            "common_horizon_net_worth_auc": (
                "mean end-of-turn net-worth estimate over turns 1..Hc; normally terminal "
                "games are absorbing"
            ),
        },
        "artifacts": {
            "observations_csv": _relative(repo_root, observations_path),
            "observations_sha256": _sha256_file(observations_path),
            "block_summary_csv": _relative(repo_root, blocks_path),
            "block_summary_sha256": _sha256_file(blocks_path),
        },
        "source_hashes": sorted(source_hashes, key=lambda value: value["path"]),
        "provenance": {
            "campaign_run_results": _relative(repo_root, run_results_path),
            "campaign_run_results_sha256": _sha256_file(run_results_path),
            "validation": _relative(repo_root, validation_path),
            "validation_sha256": _sha256_file(validation_path),
            "script": _relative(repo_root, Path(__file__).resolve()),
            "script_sha256": _sha256_file(Path(__file__).resolve()),
        },
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "All calculations are downstream of completed run artifacts.",
        },
    }
    _write_json(output_dir / "manifest.json", payload)
    (output_dir / "README.md").write_text(_complete_markdown(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "common_horizon": common_horizon,
                "observation_count": len(observation_rows),
                "output": _relative(repo_root, output_dir / "manifest.json"),
                "provider_calls": 0,
                "status": "complete",
                "survival_horizon": survival_horizon,
            },
            sort_keys=True,
        )
    )
    return 0


def _blocked_manifest(
    repo_root: Path,
    campaign_dir: Path,
    validation_path: Path,
    validation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "e1_analysis_matrix_manifest_v1",
        "generated_at_utc": _utc_now(),
        "status": "blocked_validation_incomplete",
        "campaign_id": CAMPAIGN_ID,
        "source_commit": _git_head(repo_root),
        "provider_calls": 0,
        "campaign_dir": _relative(repo_root, campaign_dir),
        "validation": {
            "path": _relative(repo_root, validation_path),
            "exists": validation_path.exists(),
            "sha256": _sha256_file(validation_path) if validation_path.exists() else None,
            "status": validation.get("status"),
            "empirical_gate_passed": validation.get("empirical_gate_passed"),
        },
        "blockers": [
            "E1 empirical validation has not passed.",
            "No horizons, model contrasts, or nuisance parameters were estimated.",
        ],
        "prompt_pipeline": {
            "status": "unchanged",
            "note": "This precheck makes no model or provider call.",
        },
        "provenance": {
            "script": _relative(repo_root, Path(__file__).resolve()),
            "script_sha256": _sha256_file(Path(__file__).resolve()),
        },
    }


def _run_observations(
    *,
    repo_root: Path,
    campaign_row: dict[str, Any],
    run_dir: Path,
    actor_codes: dict[str, str],
    common_horizon: int,
    survival_horizon: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    scorecard_path = run_dir / "scorecard_players.json"
    summary_path = run_dir / "summary.json"
    state_dir = run_dir / "state"
    scorecard_value = json.loads(scorecard_path.read_text(encoding="utf-8"))
    if not isinstance(scorecard_value, list):
        raise ValueError(f"{scorecard_path} must contain a list.")
    scores = [_dict(value) for value in scorecard_value]
    score_by_player = {str(value.get("player_id")): value for value in scores}
    players = [_dict(value) for value in _list(campaign_row.get("players"))]
    terminal_turn = _terminal_turn_index(run_dir)
    snapshots = _turn_snapshots(state_dir)
    if not snapshots:
        raise ValueError(f"No canonical turn snapshots found in {state_dir}.")
    missing_required = [
        turn for turn in range(0, min(common_horizon, terminal_turn) + 1) if turn not in snapshots
    ]
    if missing_required:
        raise ValueError(
            f"{run_dir.name} is missing canonical turn snapshots: {missing_required[:20]}."
        )
    terminal_snapshot = _read_json(snapshots[terminal_turn])
    ended_normally = str(_dict(campaign_row.get("summary")).get("reason") or "") in {
        "bankruptcy",
        "turn_limit",
        "max_turns",
    }
    if common_horizon > terminal_turn and not ended_normally:
        raise ValueError(
            f"{run_dir.name} ended before Hc without an eligible absorbing terminal state."
        )

    net_worth_by_turn: dict[int, dict[str, float]] = {}
    for turn in range(1, common_horizon + 1):
        snapshot = (
            _read_json(snapshots[turn])
            if turn in snapshots
            else terminal_snapshot
        )
        net_worth_by_turn[turn] = _net_worth_by_player(snapshot)

    rows: list[dict[str, Any]] = []
    for player in players:
        player_id = str(player.get("player_id"))
        actor_id = str(player.get("actor_id"))
        score = score_by_player.get(player_id)
        if score is None:
            raise ValueError(f"{run_dir.name} lacks scorecard row for {player_id}.")
        final_rank = _required_int(score.get("final_rank"), f"{run_dir.name}/{player_id}/rank")
        bankrupt = bool(score.get("bankrupt"))
        bankruptcy_turn_value = score.get("bankruptcy_turn")
        bankruptcy_turn = (
            _required_int(
                bankruptcy_turn_value,
                f"{run_dir.name}/{player_id}/bankruptcy_turn",
            )
            if bankrupt
            else None
        )
        survival_time = bankruptcy_turn if bankruptcy_turn is not None else terminal_turn
        auc_values = [
            net_worth_by_turn[turn].get(player_id, 0.0)
            for turn in range(1, common_horizon + 1)
        ]
        rows.append(
            {
                "seed": campaign_row.get("seed"),
                "seed_label": campaign_row.get("seed_label"),
                "run_id": campaign_row.get("run_id"),
                "permutation_id": campaign_row.get("permutation_id"),
                "execution_rank": campaign_row.get("execution_rank"),
                "actor_code": actor_codes[actor_id],
                "seat_index": player.get("seat_index"),
                "final_rank": final_rank,
                "placement_superiority": round((4 - final_rank) / 3, 10),
                "bankrupt": bankrupt,
                "bankruptcy_turn": bankruptcy_turn,
                "terminal_turn": terminal_turn,
                "survival_censored": not bankrupt,
                "restricted_survival_horizon": survival_horizon,
                "restricted_survival": min(survival_time, survival_horizon),
                "common_auc_horizon": common_horizon,
                "net_worth_auc": round(sum(auc_values) / common_horizon, 10),
            }
        )
    source_paths = [
        scorecard_path,
        summary_path,
        run_dir / "state_replay_report.json",
        run_dir / "artifact_replay_report.json",
    ]
    source_paths.extend(snapshots[turn] for turn in range(0, min(common_horizon, terminal_turn) + 1))
    hashes = [
        {
            "path": _relative(repo_root, path),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        for path in source_paths
    ]
    return rows, hashes


def _block_summary(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, Any], list[dict[str, Any]]] = defaultdict(list)
    for row in observations:
        grouped[(row["seed"], row["actor_code"])].append(row)
    rows: list[dict[str, Any]] = []
    for (seed, actor_code), values in sorted(grouped.items()):
        if len(values) != 4:
            raise ValueError(f"Seed {seed}/{actor_code} has {len(values)} rotations, expected 4.")
        rows.append(
            {
                "seed": seed,
                "actor_code": actor_code,
                "rotation_count": len(values),
                "mean_placement_superiority": _mean(
                    [_float(row["placement_superiority"]) for row in values]
                ),
                "mean_restricted_survival": _mean(
                    [_float(row["restricted_survival"]) for row in values]
                ),
                "mean_net_worth_auc": _mean([_float(row["net_worth_auc"]) for row in values]),
            }
        )
    return rows


def _turn_snapshots(state_dir: Path) -> dict[int, Path]:
    snapshots: dict[int, Path] = {}
    for path in state_dir.glob("turn_*.json"):
        match = TURN_SNAPSHOT_PATTERN.fullmatch(path.name)
        if match:
            snapshots[int(match.group(1))] = path
    return snapshots


def _terminal_turn_index(run_dir: Path) -> int:
    snapshots = _turn_snapshots(run_dir / "state")
    if not snapshots:
        raise ValueError(f"No canonical turn snapshots in {run_dir / 'state'}.")
    return max(snapshots)


def _net_worth_by_player(snapshot: dict[str, Any]) -> dict[str, float]:
    players = [_dict(value) for value in _list(snapshot.get("players"))]
    board = [_dict(value) for value in _list(snapshot.get("board"))]
    cash_by_player = {
        str(player.get("player_id")): _float(player.get("cash"))
        for player in players
    }
    result = dict(cash_by_player)
    house_costs = {
        "BROWN": 50,
        "LIGHT_BLUE": 50,
        "PINK": 100,
        "ORANGE": 100,
        "RED": 150,
        "YELLOW": 150,
        "GREEN": 200,
        "DARK_BLUE": 200,
    }
    for space in board:
        owner_id = space.get("owner_id")
        if not isinstance(owner_id, str) or owner_id not in result:
            continue
        price = _float(space.get("price"))
        result[owner_id] += price
        if space.get("mortgaged") is True:
            result[owner_id] -= math.floor(price / 2)
        house_cost = float(house_costs.get(str(space.get("group")), 0))
        result[owner_id] += _float(space.get("houses")) * house_cost
        if space.get("hotel") is True:
            result[owner_id] += 5 * house_cost
    return result


def _common_horizon(terminal_turns: list[int]) -> int:
    q25 = _quantile(sorted(terminal_turns), 0.25)
    return max(20, min(200, 10 * math.floor(q25 / 10)))


def _survival_horizon(terminal_turns: list[int], common_horizon: int) -> int:
    q75 = _quantile(sorted(terminal_turns), 0.75)
    return max(common_horizon, min(300, 10 * math.floor(q75 / 10)))


def _blind_actor_codes(actor_ids: list[str]) -> dict[str, str]:
    ordered = sorted(
        actor_ids,
        key=lambda actor_id: hashlib.sha256(
            f"{BLINDING_DOMAIN}|{actor_id}".encode()
        ).hexdigest(),
    )
    return {actor_id: f"M{index:02d}" for index, actor_id in enumerate(ordered, start=1)}


def _quantile(ordered: list[int], probability: float) -> float:
    if not ordered:
        raise ValueError("Cannot compute a quantile from an empty sample.")
    if len(ordered) == 1:
        return float(ordered[0])
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _run_dir(repo_root: Path, campaign_row: dict[str, Any]) -> Path:
    runs_root = (repo_root / "runs").resolve()
    value = campaign_row.get("run_dir")
    candidate = Path(str(value)) if value else runs_root / str(campaign_row.get("run_id"))
    if not candidate.is_absolute():
        candidate = (repo_root / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        candidate.relative_to(runs_root)
    except ValueError as exc:
        raise ValueError(f"Run directory escapes runs/: {candidate}") from exc
    return candidate


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    path.write_text(buffer.getvalue(), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return value


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _required_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer, got {value!r}.")
    return value


def _float(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot compute the mean of an empty sample.")
    return round(sum(values) / len(values), 10)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def _git_head(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _blocked_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# E1 Analysis Matrix",
            "",
            f"Status: **{payload.get('status')}**.",
            "",
            "No horizons, nuisance estimates, or model contrasts were computed because",
            "the E1 empirical validation gate has not passed.",
            "",
        ]
    )


def _complete_markdown(payload: dict[str, Any]) -> str:
    horizons = _dict(payload.get("horizons"))
    return "\n".join(
        [
            "# E1 Analysis Matrix",
            "",
            "This is a blinded nuisance-estimation artifact, not a pilot leaderboard.",
            "",
            f"- Games: {payload.get('game_count')}",
            f"- Seed blocks: {payload.get('seed_block_count')}",
            f"- Common AUC horizon: {horizons.get('common_net_worth_auc_horizon')}",
            f"- Restricted survival horizon: {horizons.get('restricted_survival_horizon')}",
            f"- Observation rows: {payload.get('observation_count')}",
            "- Model identity emitted: no",
            "- Provider calls: 0",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
