from __future__ import annotations

import json
from pathlib import Path

from monopoly_telemetry.expanded_metrics import analyze_saved_game


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _event(seq: int, event_type: str, payload: dict[str, object], player_id: str | None = None) -> dict[str, object]:
    return {
        "run_id": "test-run",
        "event_id": f"event-{seq}",
        "seq": seq,
        "turn_index": seq // 10,
        "type": event_type,
        "actor": {"kind": "PLAYER" if player_id else "ENGINE", "player_id": player_id},
        "payload": payload,
    }


def _make_saved_game(tmp_path: Path) -> Path:
    saved = tmp_path / "saved"
    run = saved / "run"
    events = [
        _event(
            1,
            "LLM_DECISION_REQUESTED",
            {"decision_id": "decision-1", "player_id": "A", "decision_type": "POST_TURN_DECISION"},
        ),
        _event(2, "LLM_DECISION_RESPONSE", {"decision_id": "decision-1", "player_id": "A"}, "A"),
        _event(
            3,
            "LLM_PUBLIC_MESSAGE",
            {"decision_id": "decision-1", "player_id": "A", "message": "I will trade fairly."},
            "A",
        ),
        _event(
            4,
            "LLM_PRIVATE_THOUGHT",
            {"decision_id": "decision-1", "player_id": "A", "thought": "Use the trade to gain leverage."},
            "A",
        ),
        _event(
            5,
            "TRADE_PROPOSED",
            {
                "initiator_player_id": "A",
                "counterparty_player_id": "B",
                "offer": {"cash": 50, "properties": []},
                "request": {"cash": 0, "properties": ["BOARDWALK"]},
            },
            "A",
        ),
        _event(
            6,
            "TRADE_COUNTERED",
            {
                "initiator_player_id": "A",
                "counterparty_player_id": "B",
                "offer": {"cash": 100, "properties": []},
                "request": {"cash": 0, "properties": ["BOARDWALK"]},
            },
            "B",
        ),
        _event(
            7,
            "TRADE_ACCEPTED",
            {
                "initiator_player_id": "A",
                "counterparty_player_id": "B",
                "offer": {"cash": 100, "properties": []},
                "request": {"cash": 0, "properties": ["BOARDWALK"]},
            },
            "A",
        ),
        _event(10, "AUCTION_STARTED", {"property_space": "BOARDWALK", "initiator_player_id": "A"}),
        _event(
            11,
            "AUCTION_BID_PLACED",
            {"property_space": "BOARDWALK", "bidder_player_id": "B", "bid_amount": 300},
            "B",
        ),
        _event(12, "AUCTION_PLAYER_DROPPED", {"property_space": "BOARDWALK", "player_id": "A"}, "A"),
        _event(
            13,
            "AUCTION_ENDED",
            {"property_space": "BOARDWALK", "winner_player_id": "B", "winning_bid": 300, "reason": "SOLD"},
        ),
        _event(20, "PROPERTY_MORTGAGED", {"player_id": "A", "space_index": 1, "amount": 30}, "A"),
        _event(30, "PROPERTY_UNMORTGAGED", {"player_id": "A", "space_index": 1, "amount": 33}, "A"),
        _event(31, "CASH_CHANGED", {"player_id": "A", "delta": -250, "reason": "test"}, "A"),
        _event(32, "CASH_CHANGED", {"player_id": "A", "delta": 250, "reason": "test_recovery"}, "A"),
        _event(33, "RENT_PAID", {"from_player_id": "A", "to_player_id": "B", "amount": 40}, "A"),
    ]
    _write_jsonl(run / "events.jsonl", events)
    action = {
        "decision_id": "decision-1",
        "actor_player_id": "A",
        "action": {
            "action": "propose_trade",
            "args": {},
            "public_message": "I will trade fairly.",
            "private_thought": "Use the trade to gain leverage.",
        },
    }
    _write_jsonl(run / "actions.jsonl", [action])
    prompt_payload = {
        "game_state": {
            "you": {"player_id": "A", "cash": 1500, "holdings": {"owned": [], "mortgaged": []}},
            "others": [{"player_id": "B", "cash": 1500, "holdings": {"owned": [], "mortgaged": []}}],
            "bank": {},
        },
        "action_state": {
            "scenario": {},
            "available_actions": ["propose_trade", "end_turn"],
        },
    }
    decisions = [
        {
            "phase": "decision_started",
            "run_id": "test-run",
            "decision_id": "decision-1",
            "turn_index": 0,
            "player_id": "A",
            "decision_type": "POST_TURN_DECISION",
            "prompt_payload": prompt_payload,
        },
        {
            "phase": "decision_resolved",
            "run_id": "test-run",
            "decision_id": "decision-1",
            "turn_index": 0,
            "player_id": "A",
            "decision_type": "POST_TURN_DECISION",
            "attempts": [{"outcome": "valid"}],
            "retry_used": False,
            "fallback_used": False,
            "final_action": action["action"],
            "emitted_event_seq_start": 2,
            "emitted_event_seq_end": 7,
            "applied": True,
        },
    ]
    _write_jsonl(run / "decisions.jsonl", decisions)
    (run / "state").mkdir(parents=True)
    (run / "state" / "turn_0000.json").write_text(
        json.dumps(
            {
                "players": [
                    {"player_id": "A", "cash": 1500},
                    {"player_id": "B", "cash": 1500},
                ]
            }
        ),
        encoding="utf-8",
    )
    (run / "players.json").write_text(
        json.dumps({"players": [{"player_id": "A"}, {"player_id": "B"}]}), encoding="utf-8"
    )
    (run / "summary.json").write_text(
        json.dumps(
            {
                "run_id": "test-run",
                "winner_player_id": "B",
                "players": {
                    "A": {"cash": 1500, "bankrupt": False},
                    "B": {"cash": 1500, "bankrupt": False},
                },
            }
        ),
        encoding="utf-8",
    )
    return saved


def test_expanded_metrics_reconstructs_domain_episodes(tmp_path: Path) -> None:
    saved = _make_saved_game(tmp_path)

    result = analyze_saved_game(saved)

    assert result["counts"]["trade_episodes"] == 1
    assert result["counts"]["auction_episodes"] == 1
    assert result["counts"]["mortgage_episodes"] == 1
    players = {row["player_id"]: row for row in result["player_metrics"]}
    assert players["A"]["trade_acceptance_rate_as_initiator"] == 1.0
    assert players["A"]["mean_trade_counteroffers"] == 1.0
    assert players["A"]["auction_dropout_count"] == 1
    assert players["B"]["auction_win_count"] == 1
    assert players["A"]["mortgage_cycle_count"] == 1
    assert players["A"]["mortgage_financing_cost"] == 3
    assert players["A"]["cash_max_drawdown"] == 250
    assert players["A"]["cash_shocks_recovered"] == 1
    assert players["A"]["cash_max_underwater_events"] == 1
    assert players["A"]["rent_paid"] == 40
    assert players["A"]["optimal_decision_status"] == "REQUIRES_DECLARED_ORACLE"
    assert (saved / "analysis" / "expanded_metrics" / "cash_reason_metrics.csv").exists()
    assert (saved / "analysis" / "expanded_metrics" / "trade_player_episodes.csv").exists()
    assert (saved / "analysis" / "expanded_metrics" / "auction_player_episodes.csv").exists()
