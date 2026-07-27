from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .engine import Engine


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            entries.append(parsed)
    return entries


def replay_actions(
    *,
    seed: int,
    players: list[dict[str, Any]],
    run_id: str,
    actions: Iterable[dict[str, Any]],
    max_turns: int = 200,
    start_ts_ms: int = 0,
    ts_step_ms: int = 250,
    max_trade_exchanges: int = 20,
    max_auction_actions: int = 200,
    assert_decision_ids: bool = True,
) -> list[dict[str, Any]]:
    action_entries = list(actions)
    engine = Engine(
        seed=seed,
        players=players,
        run_id=run_id,
        max_turns=max_turns,
        start_ts_ms=start_ts_ms,
        ts_step_ms=ts_step_ms,
        max_trade_exchanges=max_trade_exchanges,
        max_auction_actions=max_auction_actions,
    )
    events: list[dict[str, Any]] = []

    max_auto_steps = max(1, max_turns + len(players) + 1)
    for entry in action_entries:
        _, new_events, decision, _ = engine.advance_until_decision(max_steps=max_auto_steps)
        events.extend(new_events)
        if decision is None:
            if engine.is_game_over():
                break
            raise ValueError("Replay could not reach the next decision before applying an action.")
        if assert_decision_ids:
            expected_id = entry.get("decision_id")
            if isinstance(expected_id, str) and decision.get("decision_id") != expected_id:
                raise ValueError("Decision id mismatch during replay.")
        action_payload = entry.get("action") if isinstance(entry.get("action"), dict) else entry
        if not isinstance(action_payload, dict):
            raise ValueError("Invalid action payload for replay.")
        decision_meta = entry.get("decision_meta") if isinstance(entry.get("decision_meta"), dict) else None
        _, action_events, _, _ = engine.apply_action(action_payload, decision_meta=decision_meta)
        events.extend(action_events)
        if engine.is_game_over():
            break

    if not engine.is_game_over():
        _, tail_events, _, _ = engine.advance_until_decision(max_steps=max_auto_steps)
        events.extend(tail_events)

    return events


def canonical_event_lines(events: Iterable[dict[str, Any]]) -> list[str]:
    return [json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True) for event in events]
