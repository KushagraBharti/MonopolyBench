"""Read-only cohort overview for exhibit planning (Opus, phase 3).

Computes per-game winner/seat/seed, per-model usage and OpenRouter-reported
cost coverage from canonical saved-game files. Makes no provider calls and
writes only to the output path given on the command line.

Usage: python3 -I cohort_overview.py <saved_games_dir> <out_json>
"""
import hashlib
import json
import sys
from pathlib import Path

COLLECTIONS = [
    "railway-research-12-games-2026-10-25",
    "railway-research-8-games-2026-10-26",
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    root = Path(sys.argv[1])
    out = Path(sys.argv[2])
    games = []
    by_model = {}
    n = 0
    for coll in COLLECTIONS:
        for gdir in sorted(p for p in (root / coll).glob("game-*") if p.is_dir()):
            run = gdir / "run"
            n += 1
            summ = json.loads((run / "summary.json").read_text())
            seat = json.loads((run / "seat_assignment.json").read_text())
            usage = json.loads((run / "usage.json").read_text())
            cfg = json.loads((run / "run_config.json").read_text())
            games.append({
                "collection": coll,
                "game_dir": gdir.name,
                "summary_sha256": sha256(run / "summary.json"),
                "seat_assignment_sha256": sha256(run / "seat_assignment.json"),
                "usage_sha256": sha256(run / "usage.json"),
                "summary_keys": sorted(summ.keys()),
                "seat_assignment": seat,
                "seed": cfg.get("seed"),
                "winner_player_id": summ.get("winner_player_id"),
                "turns": summ.get("turn_count") or summ.get("turns"),
                "usage_attempts": usage.get("attempt_count"),
                "usage_missing_attempts": usage.get("missing_usage_attempt_count"),
                "known_cost_subtotal": usage.get("known_cost_subtotal"),
            })
            for model, m in usage.get("by_model", {}).items():
                agg = by_model.setdefault(model, {
                    "decision_count": 0, "prompt_tokens": 0, "completion_tokens": 0,
                    "reasoning_tokens": 0, "known_cost_subtotal": 0.0,
                    "attempt_count": 0, "missing_cost_attempt_count": 0,
                    "latency_ms": 0,
                })
                own = m.get("own_model", {})
                agg["decision_count"] += m.get("decision_count") or 0
                agg["prompt_tokens"] += m.get("prompt_tokens") or 0
                agg["completion_tokens"] += m.get("completion_tokens") or 0
                agg["reasoning_tokens"] += m.get("reasoning_tokens") or 0
                agg["known_cost_subtotal"] += m.get("known_cost_subtotal") or 0.0
                agg["attempt_count"] += own.get("attempt_count") or 0
                agg["missing_cost_attempt_count"] += own.get("missing_cost_attempt_count") or 0
                agg["latency_ms"] += m.get("latency_ms") or 0
    out.write_text(json.dumps({"games": games, "by_model": by_model, "n_games": n}, indent=1))


if __name__ == "__main__":
    main()
