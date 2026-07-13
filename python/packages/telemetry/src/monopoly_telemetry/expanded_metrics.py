from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


EXPANDED_METRICS_VERSION = "expanded_game_metrics_v1"
TERMINAL_TRADE_EVENTS = {"TRADE_ACCEPTED", "TRADE_REJECTED", "TRADE_EXPIRED"}


def analyze_saved_game(saved_game_dir: Path, output_dir: Path | None = None) -> dict[str, Any]:
    """Build deterministic, evidence-linked metrics for one saved MonopolyBench game."""
    saved_game_dir = saved_game_dir.resolve()
    run_dir = saved_game_dir / "run" if (saved_game_dir / "run").is_dir() else saved_game_dir
    if not (run_dir / "events.jsonl").exists():
        raise FileNotFoundError(f"No events.jsonl under {run_dir}")
    if output_dir is None:
        root = saved_game_dir if run_dir != saved_game_dir else run_dir
        output_dir = root / "analysis" / "expanded_metrics"
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    events = _read_jsonl(run_dir / "events.jsonl")
    actions = _read_jsonl(run_dir / "actions.jsonl")
    decisions = _read_jsonl(run_dir / "decisions.jsonl")
    summary = _read_json(run_dir / "summary.json", {})
    board = _load_board(run_dir)
    player_ids, initial_cash = _load_initial_players(run_dir, summary)

    trade_episodes = _trade_episodes(events)
    auction_episodes = _auction_episodes(events, board)
    mortgage_episodes = _mortgage_episodes(events)
    cash_ledger, cash_stats = _cash_metrics(events, player_ids, initial_cash)
    cash_reason_metrics = _cash_reason_metrics(cash_ledger)
    trade_player_episodes = _trade_player_episode_rows(trade_episodes)
    auction_player_episodes = _auction_player_episode_rows(auction_episodes)
    decision_rows, decision_stats = _decision_metrics(decisions, actions, player_ids)
    player_metrics = _player_metrics(
        player_ids=player_ids,
        summary=summary,
        events=events,
        actions=actions,
        trade_episodes=trade_episodes,
        auction_episodes=auction_episodes,
        mortgage_episodes=mortgage_episodes,
        cash_stats=cash_stats,
        decision_stats=decision_stats,
    )

    semantic_status = {
        "schema_version": "semantic_metric_status_v1",
        "exact_from_artifacts": [
            "trade funnel and resolution depth",
            "observed auction participation, dropouts, bids, and wins",
            "mortgage and unmortgage cycles",
            "cash inflow, outflow, volatility, drawdown, shocks, and recovery",
            "action choice and retry/fallback reliability",
        ],
        "requires_judge_labels": {
            "promise_fulfillment": "Requires an extracted promise, conditions, deadline, and later evidence.",
            "deception": "Requires a supported contradiction plus strategic intent; keywords are not proof.",
            "negotiation_quality": "Requires contextual assessment of leverage, concessions, and outcome quality.",
            "long_horizon_agency": "Requires trajectory-level assessment across multiple decisions and phases.",
        },
        "requires_oracle_or_counterfactual": {
            "optimal_decision_rate": "No exact label exists without a declared policy/value oracle.",
            "decision_regret": "Requires counterfactual rollouts or a separately validated value model.",
        },
    }

    run_id = str(summary.get("run_id") or (events[0].get("run_id") if events else run_dir.name))
    result = {
        "schema_version": EXPANDED_METRICS_VERSION,
        "run_id": run_id,
        "source_run_dir": "run" if run_dir != saved_game_dir else ".",
        "counts": {
            "players": len(player_ids),
            "events": len(events),
            "actions": len(actions),
            "resolved_decisions": len(decision_rows),
            "trade_episodes": len(trade_episodes),
            "auction_episodes": len(auction_episodes),
            "mortgage_episodes": len(mortgage_episodes),
            "cash_reason_rows": len(cash_reason_metrics),
            "trade_player_episode_rows": len(trade_player_episodes),
            "auction_player_episode_rows": len(auction_player_episodes),
        },
        "player_metrics": player_metrics,
        "limitations": semantic_status,
    }

    _write_json(output_dir / "summary.json", result)
    _write_json(output_dir / "semantic_metric_status.json", semantic_status)
    _write_csv(output_dir / "player_metrics.csv", player_metrics)
    _write_csv(output_dir / "trade_episodes.csv", trade_episodes)
    _write_csv(output_dir / "trade_player_episodes.csv", trade_player_episodes)
    _write_csv(output_dir / "auction_episodes.csv", auction_episodes)
    _write_csv(output_dir / "auction_player_episodes.csv", auction_player_episodes)
    _write_csv(output_dir / "mortgage_episodes.csv", mortgage_episodes)
    _write_csv(output_dir / "cash_ledger.csv", cash_ledger)
    _write_csv(output_dir / "cash_reason_metrics.csv", cash_reason_metrics)
    _write_csv(output_dir / "decision_metrics.csv", decision_rows)
    (output_dir / "metric_definitions.md").write_text(_metric_definitions(), encoding="utf-8")
    (output_dir / "expanded_metrics_report.md").write_text(
        _metrics_report(run_id, player_metrics, semantic_status), encoding="utf-8"
    )
    return result


def _trade_episodes(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    episodes: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for event in events:
        event_type = str(event.get("type") or "")
        payload = _dict(event.get("payload"))
        if event_type == "TRADE_PROPOSED":
            if current is not None:
                current["outcome"] = "SUPERSEDED_WITHOUT_TERMINAL_EVENT"
                current["censored"] = True
                episodes.append(_finalize_trade(current))
            current = {
                "trade_id": f"trade-{len(episodes) + 1:04d}",
                "initiator_player_id": payload.get("initiator_player_id"),
                "counterparty_player_id": payload.get("counterparty_player_id"),
                "start_event_id": event.get("event_id"),
                "start_seq": _int(event.get("seq")),
                "start_turn": _int(event.get("turn_index")),
                "end_event_id": None,
                "end_seq": None,
                "end_turn": None,
                "outcome": "OPEN_AT_RUN_END",
                "censored": True,
                "counteroffers": 0,
                "offer_revisions": 0,
                "public_exchange_count": 1,
                "initial_offer": payload.get("offer"),
                "initial_request": payload.get("request"),
                "final_offer": payload.get("offer"),
                "final_request": payload.get("request"),
            }
        elif event_type == "TRADE_COUNTERED" and current is not None:
            current["counteroffers"] += 1
            current["offer_revisions"] += _offer_changed(
                current.get("final_offer"), current.get("final_request"), payload.get("offer"), payload.get("request")
            )
            current["public_exchange_count"] += 1
            current["final_offer"] = payload.get("offer")
            current["final_request"] = payload.get("request")
        elif event_type in TERMINAL_TRADE_EVENTS and current is not None:
            current["end_event_id"] = event.get("event_id")
            current["end_seq"] = _int(event.get("seq"))
            current["end_turn"] = _int(event.get("turn_index"))
            current["outcome"] = event_type.removeprefix("TRADE_")
            current["censored"] = False
            current["final_offer"] = payload.get("offer", current.get("final_offer"))
            current["final_request"] = payload.get("request", current.get("final_request"))
            episodes.append(_finalize_trade(current))
            current = None
    if current is not None:
        episodes.append(_finalize_trade(current))
    return episodes


def _finalize_trade(row: dict[str, Any]) -> dict[str, Any]:
    end_seq = row.get("end_seq")
    end_turn = row.get("end_turn")
    row["event_span"] = None if end_seq is None else _int(end_seq) - _int(row.get("start_seq"))
    row["turns_to_resolution"] = None if end_turn is None else _int(end_turn) - _int(row.get("start_turn"))
    row["accepted"] = row.get("outcome") == "ACCEPTED"
    row["back_and_forth_count"] = _int(row.get("counteroffers"))
    row["initial_offer"] = _json_cell(row.get("initial_offer"))
    row["initial_request"] = _json_cell(row.get("initial_request"))
    row["final_offer"] = _json_cell(row.get("final_offer"))
    row["final_request"] = _json_cell(row.get("final_request"))
    return row


def _auction_episodes(events: list[dict[str, Any]], board: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    episodes: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for event in events:
        event_type = str(event.get("type") or "")
        payload = _dict(event.get("payload"))
        if event_type == "AUCTION_STARTED":
            if current is not None:
                current["reason"] = "SUPERSEDED_WITHOUT_END_EVENT"
                current["censored"] = True
                episodes.append(_finalize_auction(current, board))
            current = {
                "auction_id": f"auction-{len(episodes) + 1:04d}",
                "property_space": payload.get("property_space"),
                "initiator_player_id": payload.get("initiator_player_id"),
                "start_event_id": event.get("event_id"),
                "start_seq": _int(event.get("seq")),
                "turn_index": _int(event.get("turn_index")),
                "end_event_id": None,
                "end_seq": None,
                "winner_player_id": None,
                "winning_bid": None,
                "reason": "OPEN_AT_RUN_END",
                "censored": True,
                "bids": [],
                "dropouts": [],
            }
        elif event_type == "AUCTION_BID_PLACED" and current is not None:
            current["bids"].append(
                {
                    "player_id": payload.get("bidder_player_id"),
                    "amount": _int(payload.get("bid_amount")),
                    "event_id": event.get("event_id"),
                    "seq": _int(event.get("seq")),
                }
            )
        elif event_type == "AUCTION_PLAYER_DROPPED" and current is not None:
            current["dropouts"].append(
                {
                    "player_id": payload.get("player_id"),
                    "event_id": event.get("event_id"),
                    "seq": _int(event.get("seq")),
                }
            )
        elif event_type == "AUCTION_ENDED" and current is not None:
            current["end_event_id"] = event.get("event_id")
            current["end_seq"] = _int(event.get("seq"))
            current["winner_player_id"] = payload.get("winner_player_id")
            current["winning_bid"] = payload.get("winning_bid")
            current["reason"] = payload.get("reason")
            current["censored"] = False
            episodes.append(_finalize_auction(current, board))
            current = None
    if current is not None:
        episodes.append(_finalize_auction(current, board))
    return episodes


def _finalize_auction(row: dict[str, Any], board: dict[str, dict[str, Any]]) -> dict[str, Any]:
    bids = list(row.pop("bids", []))
    dropouts = list(row.pop("dropouts", []))
    participants = sorted(
        {str(item.get("player_id")) for item in [*bids, *dropouts] if item.get("player_id") is not None}
    )
    bid_amounts = [_int(item.get("amount")) for item in bids]
    list_price = _int(_dict(board.get(str(row.get("property_space")))).get("price")) or None
    winning_bid = _int(row.get("winning_bid")) if row.get("winning_bid") is not None else None
    increments = [bid_amounts[index] - bid_amounts[index - 1] for index in range(1, len(bid_amounts))]
    row.update(
        {
            "observed_eligible_players": _json_cell(participants),
            "observed_eligible_count": len(participants),
            "participant_count": len({item.get("player_id") for item in bids}),
            "bid_count": len(bids),
            "dropout_count": len(dropouts),
            "dropout_players": _json_cell([item.get("player_id") for item in dropouts]),
            "bids": _json_cell(bids),
            "list_price": list_price,
            "winning_bid": winning_bid,
            "winning_bid_to_list_ratio": _ratio(winning_bid, list_price),
            "winning_premium": None if winning_bid is None or list_price is None else winning_bid - list_price,
            "mean_bid_increment": _mean(increments),
            "max_bid_increment": max(increments) if increments else None,
            "event_span": None
            if row.get("end_seq") is None
            else _int(row.get("end_seq")) - _int(row.get("start_seq")),
        }
    )
    return row


def _trade_player_episode_rows(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for episode in episodes:
        for role, player_field, other_field in [
            ("INITIATOR", "initiator_player_id", "counterparty_player_id"),
            ("COUNTERPARTY", "counterparty_player_id", "initiator_player_id"),
        ]:
            rows.append(
                {
                    "trade_id": episode.get("trade_id"),
                    "player_id": episode.get(player_field),
                    "counterparty_player_id": episode.get(other_field),
                    "role": role,
                    "start_turn": episode.get("start_turn"),
                    "end_turn": episode.get("end_turn"),
                    "outcome": episode.get("outcome"),
                    "accepted": episode.get("accepted"),
                    "censored": episode.get("censored"),
                    "counteroffers": episode.get("counteroffers"),
                    "back_and_forth_count": episode.get("back_and_forth_count"),
                    "public_exchange_count": episode.get("public_exchange_count"),
                    "event_span": episode.get("event_span"),
                    "turns_to_resolution": episode.get("turns_to_resolution"),
                    "initial_offer": episode.get("initial_offer"),
                    "initial_request": episode.get("initial_request"),
                    "final_offer": episode.get("final_offer"),
                    "final_request": episode.get("final_request"),
                }
            )
    return rows


def _auction_player_episode_rows(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for episode in episodes:
        eligible = [str(value) for value in json.loads(str(episode.get("observed_eligible_players") or "[]"))]
        bids = [_dict(item) for item in json.loads(str(episode.get("bids") or "[]"))]
        dropouts = [str(value) for value in json.loads(str(episode.get("dropout_players") or "[]"))]
        for player_id in eligible:
            player_bids = [_int(item.get("amount")) for item in bids if str(item.get("player_id")) == player_id]
            rows.append(
                {
                    "auction_id": episode.get("auction_id"),
                    "turn_index": episode.get("turn_index"),
                    "property_space": episode.get("property_space"),
                    "player_id": player_id,
                    "observed_eligible": True,
                    "participated_with_bid": bool(player_bids),
                    "bid_count": len(player_bids),
                    "first_bid": player_bids[0] if player_bids else None,
                    "last_bid": player_bids[-1] if player_bids else None,
                    "maximum_bid": max(player_bids) if player_bids else None,
                    "dropped_out": player_id in dropouts,
                    "won": episode.get("winner_player_id") == player_id,
                    "winning_bid": episode.get("winning_bid") if episode.get("winner_player_id") == player_id else None,
                    "list_price": episode.get("list_price"),
                    "winner_bid_to_list_ratio": episode.get("winning_bid_to_list_ratio")
                    if episode.get("winner_player_id") == player_id
                    else None,
                    "auction_reason": episode.get("reason"),
                }
            )
    return rows


def _mortgage_episodes(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    open_mortgages: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        event_type = str(event.get("type") or "")
        if event_type not in {"PROPERTY_MORTGAGED", "PROPERTY_UNMORTGAGED"}:
            continue
        payload = _dict(event.get("payload"))
        player_id = str(payload.get("player_id") or "")
        space_index = _int(payload.get("space_index"))
        key = (player_id, space_index)
        if event_type == "PROPERTY_MORTGAGED":
            open_mortgages[key].append(
                {
                    "mortgage_id": f"mortgage-{sum(len(items) for items in open_mortgages.values()) + len(rows) + 1:04d}",
                    "player_id": player_id,
                    "space_index": space_index,
                    "mortgage_event_id": event.get("event_id"),
                    "mortgage_seq": _int(event.get("seq")),
                    "mortgage_turn": _int(event.get("turn_index")),
                    "mortgage_amount": _int(payload.get("amount")),
                }
            )
        elif open_mortgages[key]:
            row = open_mortgages[key].pop(0)
            row.update(
                {
                    "unmortgage_event_id": event.get("event_id"),
                    "unmortgage_seq": _int(event.get("seq")),
                    "unmortgage_turn": _int(event.get("turn_index")),
                    "unmortgage_amount": _int(payload.get("amount")),
                    "duration_turns": _int(event.get("turn_index")) - _int(row.get("mortgage_turn")),
                    "financing_cost": _int(payload.get("amount")) - _int(row.get("mortgage_amount")),
                    "censored": False,
                }
            )
            rows.append(row)
    for queue in open_mortgages.values():
        for row in queue:
            row.update(
                {
                    "unmortgage_event_id": None,
                    "unmortgage_seq": None,
                    "unmortgage_turn": None,
                    "unmortgage_amount": None,
                    "duration_turns": None,
                    "financing_cost": None,
                    "censored": True,
                }
            )
            rows.append(row)
    return sorted(rows, key=lambda row: _int(row.get("mortgage_seq")))


def _cash_metrics(
    events: list[dict[str, Any]], player_ids: list[str], initial_cash: dict[str, int]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    balances = {player_id: _int(initial_cash.get(player_id, 1500)) for player_id in player_ids}
    peaks = dict(balances)
    histories: dict[str, list[int]] = {player_id: [balance] for player_id, balance in balances.items()}
    deltas: dict[str, list[int]] = defaultdict(list)
    ledgers: list[dict[str, Any]] = []
    for event in events:
        if event.get("type") != "CASH_CHANGED":
            continue
        payload = _dict(event.get("payload"))
        player_id = str(payload.get("player_id") or "")
        if player_id not in balances:
            balances[player_id] = 0
            peaks[player_id] = 0
            histories[player_id] = [0]
        delta = _int(payload.get("delta"))
        before = balances[player_id]
        after = before + delta
        balances[player_id] = after
        peaks[player_id] = max(peaks[player_id], after)
        histories[player_id].append(after)
        deltas[player_id].append(delta)
        ledgers.append(
            {
                "event_id": event.get("event_id"),
                "seq": event.get("seq"),
                "turn_index": event.get("turn_index"),
                "player_id": player_id,
                "reason": payload.get("reason"),
                "delta": delta,
                "cash_before": before,
                "cash_after": after,
                "running_peak": peaks[player_id],
                "drawdown_from_peak": peaks[player_id] - after,
            }
        )
    stats: dict[str, dict[str, Any]] = {}
    for player_id in sorted(balances):
        player_deltas = deltas[player_id]
        history = histories[player_id]
        shock_recoveries = _shock_recoveries(player_id, ledgers)
        recovered = [item["events_to_recovery"] for item in shock_recoveries if not item["censored"]]
        stats[player_id] = {
            "initial_cash": history[0],
            "reconstructed_final_cash": history[-1],
            "cash_inflow": sum(value for value in player_deltas if value > 0),
            "cash_outflow": -sum(value for value in player_deltas if value < 0),
            "net_cash_flow": sum(player_deltas),
            "cash_change_count": len(player_deltas),
            "cash_inflow_event_count": sum(value > 0 for value in player_deltas),
            "cash_outflow_event_count": sum(value < 0 for value in player_deltas),
            "largest_cash_inflow": max([value for value in player_deltas if value > 0], default=0),
            "largest_cash_outflow": -min([value for value in player_deltas if value < 0], default=0),
            "cash_delta_mean": _mean(player_deltas),
            "cash_delta_stdev": _stdev(player_deltas),
            "cash_mean_absolute_change": _mean([abs(value) for value in player_deltas]),
            "cash_balance_mean": _mean(history),
            "cash_balance_stdev": _stdev(history),
            "cash_min": min(history),
            "cash_max": max(history),
            "cash_max_drawdown": _max_drawdown(history),
            "cash_max_underwater_events": _max_underwater_duration(history),
            "cash_below_500_observations": sum(value < 500 for value in history),
            "cash_below_200_observations": sum(value < 200 for value in history),
            "cash_at_zero_observations": sum(value == 0 for value in history),
            "cash_shocks_200_plus": len(shock_recoveries),
            "cash_shocks_recovered": len(recovered),
            "mean_events_to_cash_recovery": _mean(recovered),
        }
    return ledgers, stats


def _cash_reason_metrics(ledger: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in ledger:
        grouped[(str(row.get("player_id")), str(row.get("reason") or "UNKNOWN"))].append(_int(row.get("delta")))
    rows: list[dict[str, Any]] = []
    for (player_id, reason), deltas in sorted(grouped.items()):
        rows.append(
            {
                "player_id": player_id,
                "reason": reason,
                "event_count": len(deltas),
                "inflow_event_count": sum(value > 0 for value in deltas),
                "outflow_event_count": sum(value < 0 for value in deltas),
                "gross_inflow": sum(value for value in deltas if value > 0),
                "gross_outflow": -sum(value for value in deltas if value < 0),
                "net_flow": sum(deltas),
                "mean_delta": _mean(deltas),
                "mean_absolute_delta": _mean([abs(value) for value in deltas]),
                "minimum_delta": min(deltas),
                "maximum_delta": max(deltas),
            }
        )
    return rows


def _shock_recoveries(player_id: str, ledger: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [row for row in ledger if row.get("player_id") == player_id]
    recoveries: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if _int(row.get("delta")) > -200:
            continue
        target = _int(row.get("cash_before"))
        recovered_at: int | None = None
        for later_index in range(index + 1, len(rows)):
            if _int(rows[later_index].get("cash_after")) >= target:
                recovered_at = later_index
                break
        recoveries.append(
            {
                "events_to_recovery": None if recovered_at is None else recovered_at - index,
                "censored": recovered_at is None,
            }
        )
    return recoveries


def _decision_metrics(
    decisions: list[dict[str, Any]], actions: list[dict[str, Any]], player_ids: list[str]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    action_by_decision = {str(row.get("decision_id")): _dict(row.get("action")) for row in actions}
    rows: list[dict[str, Any]] = []
    per_player: dict[str, dict[str, Any]] = {
        player_id: {
            "decision_count": 0,
            "retry_decisions": 0,
            "fallback_decisions": 0,
            "invalid_attempts": 0,
            "action_counts": Counter(),
            "decision_type_counts": Counter(),
        }
        for player_id in player_ids
    }
    for decision in decisions:
        if decision.get("phase") != "decision_resolved":
            continue
        player_id = str(decision.get("player_id") or "")
        stats = per_player.setdefault(
            player_id,
            {
                "decision_count": 0,
                "retry_decisions": 0,
                "fallback_decisions": 0,
                "invalid_attempts": 0,
                "action_counts": Counter(),
                "decision_type_counts": Counter(),
            },
        )
        attempts = [_dict(item) for item in decision.get("attempts") or []]
        invalid_attempts = sum(1 for item in attempts if item.get("outcome") != "valid")
        action = action_by_decision.get(str(decision.get("decision_id"))) or _dict(decision.get("final_action"))
        action_name = str(action.get("action") or "")
        decision_type = str(decision.get("decision_type") or "")
        stats["decision_count"] += 1
        stats["retry_decisions"] += int(bool(decision.get("retry_used")))
        stats["fallback_decisions"] += int(bool(decision.get("fallback_used")))
        stats["invalid_attempts"] += invalid_attempts
        stats["action_counts"][action_name] += 1
        stats["decision_type_counts"][decision_type] += 1
        rows.append(
            {
                "decision_id": decision.get("decision_id"),
                "turn_index": decision.get("turn_index"),
                "player_id": player_id,
                "decision_type": decision_type,
                "action": action_name,
                "attempt_count": len(attempts),
                "invalid_attempts": invalid_attempts,
                "retry_used": bool(decision.get("retry_used")),
                "fallback_used": bool(decision.get("fallback_used")),
                "latency_ms": decision.get("latency_ms"),
                "applied": decision.get("applied"),
                "optimality_status": "NOT_SCORED_NO_ORACLE",
            }
        )
    return rows, per_player


def _player_metrics(
    *,
    player_ids: list[str],
    summary: dict[str, Any],
    events: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    trade_episodes: list[dict[str, Any]],
    auction_episodes: list[dict[str, Any]],
    mortgage_episodes: list[dict[str, Any]],
    cash_stats: dict[str, dict[str, Any]],
    decision_stats: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    event_counts: dict[str, Counter[str]] = defaultdict(Counter)
    rent_paid: Counter[str] = Counter()
    rent_received: Counter[str] = Counter()
    rent_paid_amounts: dict[str, list[int]] = defaultdict(list)
    rent_received_amounts: dict[str, list[int]] = defaultdict(list)
    purchase_spend: Counter[str] = Counter()
    transfers_in: Counter[str] = Counter()
    transfers_out: Counter[str] = Counter()
    houses_built: Counter[str] = Counter()
    hotels_built: Counter[str] = Counter()
    houses_sold: Counter[str] = Counter()
    hotels_sold: Counter[str] = Counter()
    for event in events:
        event_type = str(event.get("type") or "")
        payload = _dict(event.get("payload"))
        actor_id = _event_player(event)
        if actor_id:
            event_counts[actor_id][event_type] += 1
        if event_type == "RENT_PAID":
            payer = str(payload.get("from_player_id"))
            receiver = str(payload.get("to_player_id"))
            amount = _int(payload.get("amount"))
            rent_paid[payer] += amount
            rent_received[receiver] += amount
            rent_paid_amounts[payer].append(amount)
            rent_received_amounts[receiver].append(amount)
        elif event_type == "PROPERTY_PURCHASED":
            purchase_spend[str(payload.get("player_id"))] += _int(payload.get("price"))
        elif event_type == "PROPERTY_TRANSFERRED":
            transfers_in[str(payload.get("to_player_id"))] += 1
            transfers_out[str(payload.get("from_player_id"))] += 1
        elif event_type == "HOUSE_BUILT":
            houses_built[str(payload.get("player_id"))] += _int(payload.get("count"))
        elif event_type == "HOTEL_BUILT":
            hotels_built[str(payload.get("player_id"))] += _int(payload.get("count"))
        elif event_type == "HOUSE_SOLD":
            houses_sold[str(payload.get("player_id"))] += _int(payload.get("count"))
        elif event_type == "HOTEL_SOLD":
            hotels_sold[str(payload.get("player_id"))] += _int(payload.get("count"))

    final_players = _dict(summary.get("players"))
    winner = summary.get("winner_player_id")
    rows: list[dict[str, Any]] = []
    for player_id in player_ids:
        initiated = [row for row in trade_episodes if row.get("initiator_player_id") == player_id]
        received = [row for row in trade_episodes if row.get("counterparty_player_id") == player_id]
        accepted_initiated = [row for row in initiated if row.get("accepted")]
        accepted_involved = [row for row in [*initiated, *received] if row.get("accepted")]
        accepted_received = [row for row in received if row.get("accepted")]
        rejected_initiated = [row for row in initiated if row.get("outcome") == "REJECTED"]
        countered_initiated = [row for row in initiated if _int(row.get("counteroffers")) > 0]
        counterparties = Counter(str(row.get("counterparty_player_id")) for row in initiated)
        observed_eligible = [
            row
            for row in auction_episodes
            if player_id in json.loads(str(row.get("observed_eligible_players") or "[]"))
        ]
        bid_auctions = [
            row for row in observed_eligible if player_id in {str(item.get("player_id")) for item in json.loads(row["bids"])}
        ]
        auction_wins = [row for row in auction_episodes if row.get("winner_player_id") == player_id]
        auction_dropouts = [
            row for row in auction_episodes if player_id in [str(value) for value in json.loads(row["dropout_players"])]
        ]
        mortgages = [row for row in mortgage_episodes if row.get("player_id") == player_id]
        completed_mortgages = [row for row in mortgages if not row.get("censored")]
        unique_mortgaged_assets = {row.get("space_index") for row in mortgages}
        auction_bid_amounts: list[int] = []
        auction_bid_event_count = 0
        for auction in auction_episodes:
            bids = [_dict(item) for item in json.loads(str(auction.get("bids") or "[]"))]
            player_bids = [_int(item.get("amount")) for item in bids if str(item.get("player_id")) == player_id]
            auction_bid_event_count += len(player_bids)
            auction_bid_amounts.extend(player_bids)
        decisions = decision_stats.get(player_id, {})
        action_counts = decisions.get("action_counts", Counter())
        final = _dict(final_players.get(player_id))
        cash = cash_stats.get(player_id, {})
        rows.append(
            {
                "player_id": player_id,
                "winner": player_id == winner,
                "bankrupt": final.get("bankrupt"),
                "final_cash_reported": final.get("cash"),
                "final_net_worth_estimate": final.get("net_worth_estimate"),
                **cash,
                "rent_paid": rent_paid[player_id],
                "rent_received": rent_received[player_id],
                "rent_net": rent_received[player_id] - rent_paid[player_id],
                "rent_payment_count": len(rent_paid_amounts[player_id]),
                "rent_receipt_count": len(rent_received_amounts[player_id]),
                "mean_rent_paid": _mean(rent_paid_amounts[player_id]),
                "mean_rent_received": _mean(rent_received_amounts[player_id]),
                "maximum_rent_paid": max(rent_paid_amounts[player_id], default=0),
                "maximum_rent_received": max(rent_received_amounts[player_id], default=0),
                "direct_property_purchase_count": event_counts[player_id]["PROPERTY_PURCHASED"],
                "direct_property_purchase_spend": purchase_spend[player_id],
                "property_transfers_in": transfers_in[player_id],
                "property_transfers_out": transfers_out[player_id],
                "houses_built": houses_built[player_id],
                "hotels_built": hotels_built[player_id],
                "houses_sold": houses_sold[player_id],
                "hotels_sold": hotels_sold[player_id],
                "building_additions": houses_built[player_id] + hotels_built[player_id],
                "building_liquidations": houses_sold[player_id] + hotels_sold[player_id],
                "building_churn_ratio": _ratio(
                    houses_sold[player_id] + hotels_sold[player_id],
                    houses_built[player_id] + hotels_built[player_id],
                ),
                "trade_proposals_sent": len(initiated),
                "trade_proposals_received": len(received),
                "trade_acceptances_as_initiator": len(accepted_initiated),
                "trade_acceptances_involved": len(accepted_involved),
                "trade_acceptances_as_counterparty": len(accepted_received),
                "trade_rejections_as_initiator": len(rejected_initiated),
                "trade_countered_episode_count": len(countered_initiated),
                "trade_acceptance_rate_as_initiator": _ratio(len(accepted_initiated), len(initiated)),
                "trade_acceptance_rate_as_counterparty": _ratio(len(accepted_received), len(received)),
                "trade_counteroffer_incidence": _ratio(len(countered_initiated), len(initiated)),
                "mean_trade_counteroffers": _mean([_int(row.get("counteroffers")) for row in initiated]),
                "mean_accepted_trade_counteroffers": _mean(
                    [_int(row.get("counteroffers")) for row in accepted_initiated]
                ),
                "mean_trade_event_span": _mean(
                    [_int(row.get("event_span")) for row in initiated if row.get("event_span") is not None]
                ),
                "max_trade_counteroffers": max([_int(row.get("counteroffers")) for row in initiated], default=0),
                "max_accepted_trade_counteroffers": max(
                    [_int(row.get("counteroffers")) for row in accepted_initiated], default=0
                ),
                "trade_partner_hhi": _hhi(counterparties),
                "auction_observed_eligible_count": len(observed_eligible),
                "auction_participation_count": len(bid_auctions),
                "auction_participation_rate": _ratio(len(bid_auctions), len(observed_eligible)),
                "auction_dropout_count": len(auction_dropouts),
                "auction_bid_event_count": auction_bid_event_count,
                "mean_auction_bid": _mean(auction_bid_amounts),
                "maximum_auction_bid": max(auction_bid_amounts, default=0),
                "auction_win_count": len(auction_wins),
                "auction_win_rate_when_observed_eligible": _ratio(len(auction_wins), len(observed_eligible)),
                "auction_win_rate_when_bid": _ratio(len(auction_wins), len(bid_auctions)),
                "mean_winning_bid_to_list_ratio": _mean(
                    [
                        float(row["winning_bid_to_list_ratio"])
                        for row in auction_wins
                        if row.get("winning_bid_to_list_ratio") is not None
                    ]
                ),
                "mortgage_count": len(mortgages),
                "unmortgage_count": len(completed_mortgages),
                "mortgage_cycle_count": len(completed_mortgages),
                "mortgage_open_at_end": len(mortgages) - len(completed_mortgages),
                "mortgage_unique_assets": len(unique_mortgaged_assets),
                "mortgage_churn_actions_per_asset": _ratio(
                    len(mortgages) + len(completed_mortgages), len(unique_mortgaged_assets)
                ),
                "mortgage_repeat_rate": _ratio(
                    len(mortgages) - len(unique_mortgaged_assets), len(mortgages)
                ),
                "mean_mortgage_duration_turns": _mean(
                    [_int(row.get("duration_turns")) for row in completed_mortgages]
                ),
                "mortgage_financing_cost": sum(_int(row.get("financing_cost")) for row in completed_mortgages),
                "mortgage_financing_cost_rate": _ratio(
                    sum(_int(row.get("financing_cost")) for row in completed_mortgages),
                    sum(_int(row.get("mortgage_amount")) for row in completed_mortgages),
                ),
                "decision_count": decisions.get("decision_count", 0),
                "retry_decisions": decisions.get("retry_decisions", 0),
                "fallback_decisions": decisions.get("fallback_decisions", 0),
                "invalid_attempts": decisions.get("invalid_attempts", 0),
                "retry_rate": _ratio(decisions.get("retry_decisions", 0), decisions.get("decision_count", 0)),
                "fallback_rate": _ratio(decisions.get("fallback_decisions", 0), decisions.get("decision_count", 0)),
                "build_decisions": action_counts.get("build_houses_or_hotel", 0),
                "sell_building_decisions": action_counts.get("sell_houses_or_hotel", 0),
                "buy_property_decisions": action_counts.get("buy_property", 0),
                "start_auction_decisions": action_counts.get("start_auction", 0),
                "jail_entries": event_counts[player_id]["SENT_TO_JAIL"],
                "jail_fine_decisions": action_counts.get("pay_jail_fine", 0),
                "jail_roll_decisions": action_counts.get("roll_for_doubles", 0),
                "bankruptcy_declarations": action_counts.get("declare_bankruptcy", 0),
                "public_messages": event_counts[player_id]["LLM_PUBLIC_MESSAGE"],
                "private_thoughts": event_counts[player_id]["LLM_PRIVATE_THOUGHT"],
                "promise_fulfillment_status": "REQUIRES_JUDGE_LABELS",
                "deception_status": "REQUIRES_JUDGE_LABELS",
                "optimal_decision_status": "REQUIRES_DECLARED_ORACLE",
            }
        )
    return rows


def _metric_definitions() -> str:
    return """# Expanded metric definitions

All exact metrics are reconstructed from canonical events, resolved decisions, actions, and initial state. Null means the denominator or required observation does not exist; it never means zero.

## Trades

- **Proposal acceptance rate** = accepted episodes initiated / terminal-or-open proposals initiated.
- **Back-and-forth count** = number of `TRADE_COUNTERED` events between proposal and terminal event.
- **Public exchange count** = proposal plus counteroffers. Messages may add richer negotiation context but do not alter this count.
- **Partner HHI** = sum of squared proposal shares by counterparty; higher values indicate concentration.

## Auctions

- **Observed eligible players** are players with a bid or dropout event in the auction. This is deliberately not called rules-engine eligibility when no explicit eligibility snapshot was emitted.
- **Participation** requires at least one bid. **Dropout** requires `AUCTION_PLAYER_DROPPED`. **Win** comes from `AUCTION_ENDED`.
- **Winning-bid/list ratio** = winning bid / board list price.

## Mortgages and cash

- A **mortgage cycle** pairs a mortgage with the next unmortgage for the same player and space.
- **Mortgage churn actions per asset** = (mortgages + matched unmortgages) / unique mortgaged assets.
- **Cash volatility** is reported both for event deltas and reconstructed balances.
- **Maximum drawdown** is the largest peak-to-later-balance decline in the reconstructed cash series.
- A **cash shock** is a single cash delta of -$200 or worse. Recovery reaches the pre-shock cash balance; unrecovered shocks are censored.
- `cash_reason_metrics.csv` separates gross inflow, gross outflow, and net flow for every player/reason pair.
- Maximum underwater duration counts consecutive reconstructed cash observations below the prior running peak.

## Player-episode tables

- `trade_player_episodes.csv` supplies one initiator and one counterparty row per trade for role-correct denominators.
- `auction_player_episodes.csv` supplies one row per observed eligible player/auction with bids, dropout, and win fields.

## Semantic and counterfactual metrics

Promise fulfillment, deception, negotiation quality, and long-horizon agency require evidence-linked judge labels. Optimality and regret require an explicit oracle or counterfactual evaluator. The deterministic analyzer refuses to fabricate either class.
"""


def _metrics_report(run_id: str, rows: list[dict[str, Any]], semantic_status: dict[str, Any]) -> str:
    lines = [
        "# Expanded numeric metrics",
        "",
        f"Run: `{run_id}`",
        "",
        "## Player summary",
        "",
        "| Player | Trades proposed | Accepted | Auction wins | Mortgage cycles | Cash max drawdown | Rent net |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {player_id} | {trade_proposals_sent} | {trade_acceptances_as_initiator} | "
            "{auction_win_count} | {mortgage_cycle_count} | {cash_max_drawdown} | {rent_net} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "These tables contain exact artifact-derived counts. The following remain explicitly gated:",
            "",
        ]
    )
    for name, explanation in semantic_status["requires_judge_labels"].items():
        lines.append(f"- `{name}`: {explanation}")
    for name, explanation in semantic_status["requires_oracle_or_counterfactual"].items():
        lines.append(f"- `{name}`: {explanation}")
    lines.append("")
    return "\n".join(lines)


def _load_initial_players(run_dir: Path, summary: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
    players_path = run_dir / "players.json"
    players_doc = _read_json(players_path, {})
    raw_players = players_doc.get("players", players_doc) if isinstance(players_doc, dict) else players_doc
    player_ids: list[str] = []
    if isinstance(raw_players, list):
        for player in raw_players:
            player_id = _dict(player).get("player_id") or _dict(player).get("name")
            if player_id:
                player_ids.append(str(player_id))
    elif isinstance(raw_players, dict):
        player_ids.extend(str(key) for key in raw_players)

    initial_cash: dict[str, int] = {}
    state_files = sorted((run_dir / "state").glob("turn_*.json"))
    for state_path in state_files:
        state = _read_json(state_path, {})
        state_players = state.get("players") if isinstance(state, dict) else None
        if not isinstance(state_players, list):
            continue
        for player in state_players:
            item = _dict(player)
            player_id = item.get("player_id") or item.get("name")
            if player_id:
                initial_cash[str(player_id)] = _int(item.get("cash"))
                if str(player_id) not in player_ids:
                    player_ids.append(str(player_id))
        if initial_cash:
            break
    if not player_ids:
        player_ids.extend(str(key) for key in _dict(summary.get("players")))
    return player_ids, initial_cash


def _load_board(run_dir: Path) -> dict[str, dict[str, Any]]:
    repo_board = run_dir
    while repo_board.parent != repo_board and not (repo_board / "contracts" / "data" / "board.json").exists():
        repo_board = repo_board.parent
    board_doc = _read_json(repo_board / "contracts" / "data" / "board.json", {})
    board: dict[str, dict[str, Any]] = {}
    for item in board_doc.get("spaces", []) if isinstance(board_doc, dict) else []:
        row = _dict(item)
        board[_space_key(str(row.get("name") or ""))] = row
    return board


def _event_player(event: dict[str, Any]) -> str | None:
    payload = _dict(event.get("payload"))
    actor = _dict(event.get("actor"))
    value = payload.get("player_id") or payload.get("bidder_player_id") or actor.get("player_id")
    return str(value) if value else None


def _space_key(name: str) -> str:
    return "_".join("".join(character if character.isalnum() else " " for character in name.upper()).split())


def _offer_changed(old_offer: Any, old_request: Any, new_offer: Any, new_request: Any) -> int:
    return int(_json_cell(old_offer) != _json_cell(new_offer) or _json_cell(old_request) != _json_cell(new_request))


def _max_drawdown(values: list[int]) -> int:
    peak = values[0] if values else 0
    maximum = 0
    for value in values:
        peak = max(peak, value)
        maximum = max(maximum, peak - value)
    return maximum


def _max_underwater_duration(values: list[int]) -> int:
    peak = values[0] if values else 0
    current = 0
    maximum = 0
    for value in values:
        if value >= peak:
            peak = value
            current = 0
        else:
            current += 1
            maximum = max(maximum, current)
    return maximum


def _hhi(counter: Counter[str]) -> float | None:
    total = sum(counter.values())
    if not total:
        return None
    return round(sum((count / total) ** 2 for count in counter.values()), 6)


def _mean(values: Iterable[int | float]) -> float | None:
    items = list(values)
    return round(float(statistics.fmean(items)), 6) if items else None


def _stdev(values: Iterable[int | float]) -> float | None:
    items = list(values)
    return round(float(statistics.pstdev(items)), 6) if items else None


def _ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 6)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _json_cell(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
