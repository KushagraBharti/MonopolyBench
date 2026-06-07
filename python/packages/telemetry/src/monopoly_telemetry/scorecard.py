from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .run_files import RunFiles


SCORECARD_VERSION = "scorecard_v1"
DEFAULT_STARTING_CASH = 1500


def build_scorecard(run_files: RunFiles) -> dict[str, Any]:
    events = _read_jsonl(run_files.events_path)
    decisions = _read_jsonl(run_files.decisions_path)
    actions = _read_jsonl(run_files.actions_path)
    summary = _read_json(run_files.summary_path)
    usage = _read_json(run_files.usage_path)
    players_payload = _read_json(run_files.players_path)
    seat_assignment = _read_json(run_files.seat_assignment_path)
    board_spec = _load_board_spec()
    snapshots = _read_snapshots(run_files.snapshots_dir)
    return _build_scorecard_from_logs(
        run_id=run_files.run_id,
        events=events,
        decisions=decisions,
        actions=actions,
        summary=summary,
        usage=usage,
        players_payload=players_payload,
        seat_assignment=seat_assignment,
        board_spec=board_spec,
        snapshots=snapshots,
    )


def write_scorecard_artifacts(run_files: RunFiles) -> dict[str, Any]:
    scorecard = build_scorecard(run_files)
    run_files.write_json_artifact(run_files.scorecard_path, scorecard)
    run_files.write_json_artifact(run_files.scorecard_players_path, scorecard["players"])
    _write_jsonl(run_files.scorecard_decisions_path, scorecard["decision_rows"])
    _write_jsonl(run_files.scorecard_events_path, scorecard["event_rows"])
    return scorecard


def _build_scorecard_from_logs(
    *,
    run_id: str,
    events: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    summary: dict[str, Any],
    usage: dict[str, Any],
    players_payload: dict[str, Any],
    seat_assignment: dict[str, Any],
    board_spec: dict[str, Any],
    snapshots: list[dict[str, Any]],
) -> dict[str, Any]:
    board = _build_board_maps(board_spec)
    players = _collect_players(summary, players_payload, seat_assignment, events, decisions, actions)
    by_player = {player["player_id"]: _empty_player_score(player) for player in players}
    run_metrics = _empty_run_metrics(run_id, summary, events, decisions, actions)
    event_rows: list[dict[str, Any]] = []

    owner_by_index: dict[int, str | None] = {}
    mortgaged_by_index: dict[int, bool] = {}
    buildings_by_index: dict[int, dict[str, int]] = {}
    cash_history_by_player: dict[str, list[int]] = {player_id: [DEFAULT_STARTING_CASH] for player_id in by_player}
    pending_purchase_by_player: dict[str, list[int]] = {}
    bankruptcy_creditor_by_turn: dict[int, str] = {}
    bankruptcy_asset_bank_by_turn: set[int] = set()

    for event in events:
        event_type = str(event.get("type") or "")
        payload = _dict(event.get("payload"))
        event_rows.append(_event_row(event))
        _increment(run_metrics["event_counts"], event_type)

        if event_type == "GAME_ENDED":
            run_metrics["winner_player_id"] = payload.get("winner_player_id")
            run_metrics["game_end_reason"] = payload.get("reason")
            continue

        if event_type == "LLM_PUBLIC_MESSAGE":
            player_id = payload.get("player_id")
            _add_player_metric(by_player, player_id, "public_messages_sent", 1)
            continue

        if event_type == "LLM_PRIVATE_THOUGHT":
            player_id = payload.get("player_id")
            _add_player_metric(by_player, player_id, "private_thoughts_recorded", 1)
            continue

        if event_type == "RENT_PAID":
            from_player_id = payload.get("from_player_id")
            to_player_id = payload.get("to_player_id")
            amount = _int(payload.get("amount"))
            run_metrics["total_rent_paid"] += amount
            run_metrics["total_rent_collected"] += amount
            _add_player_metric(by_player, from_player_id, "rent_paid", amount)
            _add_player_metric(by_player, to_player_id, "rent_collected", amount)
            if amount >= 100:
                run_metrics["strategic_descriptive_metrics"]["high_rent_payment_count"] += 1
            continue

        if event_type == "CASH_CHANGED":
            player_id = payload.get("player_id")
            delta = _int(payload.get("delta"))
            reason = str(payload.get("reason") or "")
            _add_player_metric(by_player, player_id, "cash_delta_total", delta)
            if isinstance(player_id, str) and player_id in by_player:
                previous_cash = cash_history_by_player.setdefault(player_id, [DEFAULT_STARTING_CASH])[-1]
                cash_history_by_player[player_id].append(previous_cash + delta)
            if reason.startswith("TAX"):
                amount = abs(delta)
                run_metrics["total_tax_paid"] += amount
                _add_player_metric(by_player, player_id, "taxes_paid", amount)
            if reason == "buy_property" and isinstance(player_id, str):
                if pending_purchase_by_player.get(player_id):
                    pending_purchase_by_player[player_id].pop(0)
                _add_player_metric(by_player, player_id, "properties_bought_directly", 1)
            if reason == "auction_bid" and isinstance(player_id, str):
                if pending_purchase_by_player.get(player_id):
                    pending_purchase_by_player[player_id].pop(0)
                _add_player_metric(by_player, player_id, "properties_won_by_auction", 1)
            if reason.startswith("BANKRUPTCY"):
                run_metrics["total_bankruptcies"] += 1 if reason == "BANKRUPTCY" else 0
                turn_index = _optional_int(event.get("turn_index"))
                if reason == "BANKRUPTCY_CASH" and delta > 0 and isinstance(player_id, str) and turn_index is not None:
                    bankruptcy_creditor_by_turn[turn_index] = player_id
                if reason == "BANKRUPTCY":
                    _set_player_metric(by_player, player_id, "bankrupt", True)
                    _set_player_metric(by_player, player_id, "bankruptcy_turn", event.get("turn_index"))
                    turn_index = _optional_int(event.get("turn_index"))
                    if turn_index is not None:
                        creditor = bankruptcy_creditor_by_turn.get(turn_index)
                        if creditor and creditor != player_id:
                            _set_player_metric(by_player, player_id, "bankruptcy_creditor_type", "player")
                            _set_player_metric(by_player, player_id, "bankruptcy_creditor_player_id", creditor)
                        elif turn_index in bankruptcy_asset_bank_by_turn:
                            _set_player_metric(by_player, player_id, "bankruptcy_creditor_type", "bank")
            continue

        if event_type == "PROPERTY_PURCHASED":
            player_id = payload.get("player_id")
            space_index = _optional_int(payload.get("space_index"))
            price = _int(payload.get("price"))
            if space_index is not None:
                owner_by_index[space_index] = str(player_id) if isinstance(player_id, str) else None
                mortgaged_by_index.setdefault(space_index, False)
            run_metrics["total_property_purchase_count"] += 1
            run_metrics["strategic_descriptive_metrics"]["property_purchase_count"] += 1
            if price > 0:
                run_metrics["total_property_purchase_volume"] += price
                if isinstance(player_id, str) and space_index is not None:
                    pending_purchase_by_player.setdefault(player_id, []).append(space_index)
            continue

        if event_type == "PROPERTY_TRANSFERRED":
            from_player_id = payload.get("from_player_id")
            to_player_id = payload.get("to_player_id")
            space_index = _optional_int(payload.get("space_index"))
            if space_index is not None:
                owner_by_index[space_index] = str(to_player_id) if isinstance(to_player_id, str) else None
                mortgaged_by_index[space_index] = bool(payload.get("mortgaged", False))
            run_metrics["total_property_transfer_count"] += 1
            _add_player_metric(by_player, from_player_id, "properties_lost_by_transfer", 1)
            _add_player_metric(by_player, to_player_id, "properties_acquired_by_transfer", 1)
            if event_type == "PROPERTY_TRANSFERRED" and str(payload.get("reason") or "").startswith("TRADE"):
                _add_player_metric(by_player, from_player_id, "properties_lost_by_trade", 1)
                _add_player_metric(by_player, to_player_id, "properties_acquired_by_trade", 1)
            if str(payload.get("reason") or "").startswith("BANKRUPTCY"):
                _add_player_metric(by_player, from_player_id, "properties_lost_by_bankruptcy", 1)
            continue

        if event_type == "BANKRUPTCY_ASSETS_TO_BANK":
            turn_index = _optional_int(event.get("turn_index"))
            if turn_index is not None:
                bankruptcy_asset_bank_by_turn.add(turn_index)
            continue

        if event_type == "PROPERTY_MORTGAGED":
            player_id = payload.get("player_id")
            space_index = _optional_int(payload.get("space_index"))
            if space_index is not None:
                mortgaged_by_index[space_index] = True
            run_metrics["total_mortgages"] += 1
            run_metrics["strategic_descriptive_metrics"]["mortgage_event_count"] += 1
            _add_player_metric(by_player, player_id, "mortgages", 1)
            continue

        if event_type == "PROPERTY_UNMORTGAGED":
            player_id = payload.get("player_id")
            space_index = _optional_int(payload.get("space_index"))
            if space_index is not None:
                mortgaged_by_index[space_index] = False
            run_metrics["total_unmortgages"] += 1
            run_metrics["strategic_descriptive_metrics"]["mortgage_event_count"] += 1
            _add_player_metric(by_player, player_id, "unmortgages", 1)
            continue

        if event_type in {"HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD"}:
            player_id = payload.get("player_id")
            count = _int(payload.get("count"))
            space_index = _optional_int(payload.get("space_index"))
            if space_index is not None:
                current = buildings_by_index.setdefault(space_index, {"houses": 0, "hotels": 0})
                if event_type == "HOUSE_BUILT":
                    current["houses"] = max(0, current["houses"] + count)
                elif event_type == "HOUSE_SOLD":
                    current["houses"] = max(0, current["houses"] - count)
                elif event_type == "HOTEL_BUILT":
                    current["hotels"] = max(0, current["hotels"] + count)
                    current["houses"] = 0
                elif event_type == "HOTEL_SOLD":
                    current["hotels"] = max(0, current["hotels"] - count)
                    current["houses"] = min(4, current["houses"] + (4 * count))
            metric = {
                "HOUSE_BUILT": "houses_built",
                "HOTEL_BUILT": "hotels_built",
                "HOUSE_SOLD": "houses_sold",
                "HOTEL_SOLD": "hotels_sold",
            }[event_type]
            run_metric = f"total_{metric}"
            run_metrics[run_metric] += count
            run_metrics["strategic_descriptive_metrics"]["development_event_count"] += count
            _add_player_metric(by_player, player_id, metric, count)
            continue

        if event_type == "SENT_TO_JAIL":
            player_id = payload.get("player_id")
            _add_player_metric(by_player, player_id, "jail_entries", 1)
            run_metrics["strategic_descriptive_metrics"]["jail_entry_count"] += 1
            continue

        if event_type == "AUCTION_BID_PLACED":
            player_id = payload.get("bidder_player_id")
            amount = _int(payload.get("bid_amount"))
            run_metrics["total_auction_bid_count"] += 1
            run_metrics["total_auction_bid_volume"] += amount
            _add_player_metric(by_player, player_id, "auction_bids_placed", 1)
            continue

        if event_type == "AUCTION_PLAYER_DROPPED":
            player_id = payload.get("player_id")
            _add_player_metric(by_player, player_id, "auctions_dropped", 1)
            continue

        if event_type == "AUCTION_ENDED":
            player_id = payload.get("winner_player_id")
            winning_bid = _int(payload.get("winning_bid"))
            if player_id:
                _add_player_metric(by_player, player_id, "auctions_won", 1)
                _add_player_metric(by_player, player_id, "auction_win_volume", winning_bid)
                run_metrics["strategic_descriptive_metrics"]["auction_win_count"] += 1
            continue

        if event_type.startswith("TRADE_"):
            _apply_trade_event_metrics(by_player, run_metrics, event_type, payload)

    for action_row in actions:
        actor_player_id = action_row.get("actor_player_id")
        action = _dict(action_row.get("action"))
        action_name = str(action.get("action") or "")
        if action_name == "use_get_out_of_jail_card":
            _add_player_metric(by_player, actor_player_id, "get_out_of_jail_cards_used", 1)

    decision_rows = [_decision_row(entry) for entry in decisions if entry.get("phase") == "decision_resolved"]
    _apply_decision_metrics(by_player, run_metrics, decision_rows)
    _apply_usage_metrics(by_player, run_metrics, usage)
    _apply_snapshot_cash_metrics(by_player, cash_history_by_player, snapshots)
    _apply_final_summary_metrics(by_player, summary, owner_by_index, mortgaged_by_index, buildings_by_index, board)
    _rank_players(by_player, run_metrics)
    _apply_score_matrix(by_player, run_metrics)

    players_list = [by_player[player_id] for player_id in sorted(by_player)]
    return {
        "schema_version": "v1",
        "scorecard_version": SCORECARD_VERSION,
        "run_id": run_id,
        "run": run_metrics,
        "players": players_list,
        "decision_rows": decision_rows,
        "event_rows": event_rows,
    }


def _empty_run_metrics(
    run_id: str,
    summary: dict[str, Any],
    events: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    actions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "winner_player_id": summary.get("winner_player_id"),
        "game_end_reason": summary.get("reason"),
        "final_turn_index": summary.get("turn_count"),
        "total_event_count": len(events),
        "total_decision_log_entries": len(decisions),
        "total_applied_action_count": len(actions),
        "event_counts": {},
        "total_rent_paid": 0,
        "total_rent_collected": 0,
        "total_tax_paid": 0,
        "total_auction_bid_count": 0,
        "total_auction_bid_volume": 0,
        "total_trade_proposed": 0,
        "total_trade_accepted": 0,
        "total_trade_rejected": 0,
        "total_trade_countered": 0,
        "total_trade_expired": 0,
        "total_property_purchase_count": 0,
        "total_property_purchase_volume": 0,
        "total_property_transfer_count": 0,
        "total_bankruptcies": 0,
        "total_houses_built": 0,
        "total_hotels_built": 0,
        "total_houses_sold": 0,
        "total_hotels_sold": 0,
        "total_mortgages": 0,
        "total_unmortgages": 0,
        "strategic_descriptive_metrics": {
            "property_purchase_count": 0,
            "auction_win_count": 0,
            "trade_accept_count": 0,
            "development_event_count": 0,
            "mortgage_event_count": 0,
            "jail_entry_count": 0,
            "high_rent_payment_count": 0,
        },
        "reliability_metrics": {
            "invalid_attempt_rate": None,
            "retry_rate": None,
            "fallback_rate": None,
            "average_decision_latency_ms": None,
        },
        "usage_metrics": {
            "source": "openrouter_actuals_only",
            "local_tokenizer_estimates_used": False,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_reasoning_tokens": 0,
            "total_cached_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "cost_per_turn": None,
            "cost_per_decision": None,
            "cost_per_completed_game": None,
        },
        "score_matrix": {
            "version": "score_matrix_v1",
            "description": "Post-hoc descriptive score dimensions; primary benchmark score remains final net worth / win outcome.",
            "dimensions": [
                "net_worth_score",
                "winner_score",
                "speed_score",
                "bankruptcy_pressure_score",
                "survival_score",
                "reliability_score",
                "cost_adjusted_score",
                "combined_experimental_score",
            ],
            "rankings": [],
        },
        "decision_stats": {
            "total_resolved": 0,
            "invalid_attempts": 0,
            "retries": 0,
            "fallbacks": 0,
            "fallback_reasons": {},
        },
    }


def _empty_player_score(player: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "v1",
        "player_id": player["player_id"],
        "name": player.get("name"),
        "openrouter_model_id": player.get("openrouter_model_id"),
        "model_display_name": player.get("model_display_name"),
        "seat_index": player.get("seat_index"),
        "turn_order": player.get("turn_order"),
        "winner": False,
        "final_rank": None,
        "primary_score": None,
        "final_cash": None,
        "final_property_face_value": 0,
        "final_mortgage_liability_estimate": 0,
        "final_building_value_estimate": 0,
        "final_net_worth_estimate": None,
        "final_liquid_net_worth_estimate": None,
        "bankrupt": False,
        "bankruptcy_turn": None,
        "bankruptcy_creditor_type": None,
        "bankruptcy_creditor_player_id": None,
        "turns_played": 0,
        "turns_survived": 0,
        "opponents_bankrupted": 0,
        "final_property_count": 0,
        "final_mortgage_count": 0,
        "final_unmortgaged_property_count": 0,
        "final_complete_color_group_count": 0,
        "final_developed_monopoly_count": 0,
        "final_railroad_count": 0,
        "final_utility_count": 0,
        "houses_owned": 0,
        "hotels_owned": 0,
        "houses_built": 0,
        "hotels_built": 0,
        "houses_sold": 0,
        "hotels_sold": 0,
        "rent_collected": 0,
        "rent_paid": 0,
        "net_rent_flow": 0,
        "taxes_paid": 0,
        "jail_entries": 0,
        "jail_turns": 0,
        "get_out_of_jail_cards_used": 0,
        "properties_bought_directly": 0,
        "properties_won_by_auction": 0,
        "properties_acquired_by_trade": 0,
        "properties_lost_by_trade": 0,
        "properties_lost_by_bankruptcy": 0,
        "properties_acquired_by_transfer": 0,
        "properties_lost_by_transfer": 0,
        "auction_bids_placed": 0,
        "auction_win_volume": 0,
        "auctions_won": 0,
        "auctions_dropped": 0,
        "trades_proposed": 0,
        "trades_received": 0,
        "trades_accepted": 0,
        "trades_rejected": 0,
        "counters_made": 0,
        "public_messages_sent": 0,
        "private_thoughts_recorded": 0,
        "invalid_attempts": 0,
        "retries_used": 0,
        "fallbacks_used": 0,
        "average_decision_latency_ms": None,
        "decision_count": 0,
        "valid_first_response_count": 0,
        "valid_first_response_rate": None,
        "retry_rate": None,
        "fallback_rate": None,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_reasoning_tokens": 0,
        "total_cached_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "cost_per_decision": None,
        "cost_per_turn_survived": None,
        "cost_per_net_worth_point": None,
        "cash_delta_total": 0,
        "lowest_cash_reached": DEFAULT_STARTING_CASH,
        "average_cash_observed": DEFAULT_STARTING_CASH,
        "ended_turn_low_cash_count": 0,
        "mortgages": 0,
        "unmortgages": 0,
        "score_matrix": {},
    }


def _collect_players(
    summary: dict[str, Any],
    players_payload: dict[str, Any],
    seat_assignment: dict[str, Any],
    events: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for entry in _list(players_payload.get("players")):
        if isinstance(entry, dict) and isinstance(entry.get("player_id"), str):
            by_id[entry["player_id"]] = dict(entry)
    for assignment in _list(seat_assignment.get("assignments")):
        if not isinstance(assignment, dict) or not isinstance(assignment.get("player_id"), str):
            continue
        current = by_id.setdefault(assignment["player_id"], {"player_id": assignment["player_id"]})
        current.update(
            {
                "seat_index": assignment.get("seat_index"),
                "turn_order": assignment.get("turn_order"),
                "name": current.get("name") or assignment.get("player_name"),
                "openrouter_model_id": current.get("openrouter_model_id") or assignment.get("openrouter_model_id"),
                "model_display_name": current.get("model_display_name") or assignment.get("model_display_name"),
            }
        )
    for player_id, entry in _dict(summary.get("players")).items():
        if isinstance(player_id, str) and isinstance(entry, dict):
            current = by_id.setdefault(player_id, {"player_id": player_id})
            current.setdefault("name", entry.get("name"))
    for entry in [*events, *decisions, *actions]:
        _collect_player_ids_from_object(entry, by_id)
    return list(by_id.values())


def _collect_player_ids_from_object(entry: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> None:
    for key in ("player_id", "actor_player_id", "from_player_id", "to_player_id"):
        value = entry.get(key)
        if isinstance(value, str):
            by_id.setdefault(value, {"player_id": value})
    actor = entry.get("actor")
    if isinstance(actor, dict) and isinstance(actor.get("player_id"), str):
        by_id.setdefault(actor["player_id"], {"player_id": actor["player_id"]})
    payload = entry.get("payload")
    if isinstance(payload, dict):
        for key in (
            "player_id",
            "from_player_id",
            "to_player_id",
            "winner_player_id",
            "initiator_player_id",
            "counterparty_player_id",
            "bidder_player_id",
        ):
            value = payload.get(key)
            if isinstance(value, str):
                by_id.setdefault(value, {"player_id": value})


def _apply_trade_event_metrics(
    by_player: dict[str, dict[str, Any]],
    run_metrics: dict[str, Any],
    event_type: str,
    payload: dict[str, Any],
) -> None:
    initiator = payload.get("initiator_player_id")
    counterparty = payload.get("counterparty_player_id")
    if event_type == "TRADE_PROPOSED":
        run_metrics["total_trade_proposed"] += 1
        _add_player_metric(by_player, initiator, "trades_proposed", 1)
        _add_player_metric(by_player, counterparty, "trades_received", 1)
    elif event_type == "TRADE_ACCEPTED":
        run_metrics["total_trade_accepted"] += 1
        run_metrics["strategic_descriptive_metrics"]["trade_accept_count"] += 1
        _add_player_metric(by_player, initiator, "trades_accepted", 1)
        _add_player_metric(by_player, counterparty, "trades_accepted", 1)
    elif event_type == "TRADE_REJECTED":
        run_metrics["total_trade_rejected"] += 1
        _add_player_metric(by_player, counterparty, "trades_rejected", 1)
    elif event_type == "TRADE_COUNTERED":
        run_metrics["total_trade_countered"] += 1
        _add_player_metric(by_player, counterparty, "counters_made", 1)
    elif event_type == "TRADE_EXPIRED":
        run_metrics["total_trade_expired"] += 1


def _apply_decision_metrics(
    by_player: dict[str, dict[str, Any]],
    run_metrics: dict[str, Any],
    decision_rows: list[dict[str, Any]],
) -> None:
    latencies_by_player: dict[str, list[int]] = {}
    stats = run_metrics["decision_stats"]
    for row in decision_rows:
        stats["total_resolved"] += 1
        player_id = row.get("player_id")
        invalid_attempts = _int(row.get("invalid_attempts"))
        retries = 1 if row.get("retry_used") else 0
        fallbacks = 1 if row.get("fallback_used") else 0
        stats["invalid_attempts"] += invalid_attempts
        stats["retries"] += retries
        stats["fallbacks"] += fallbacks
        _add_player_metric(by_player, player_id, "decision_count", 1)
        _add_player_metric(by_player, player_id, "valid_first_response_count", 0 if invalid_attempts else 1)
        _add_player_metric(by_player, player_id, "invalid_attempts", invalid_attempts)
        _add_player_metric(by_player, player_id, "retries_used", retries)
        _add_player_metric(by_player, player_id, "fallbacks_used", fallbacks)
        if row.get("fallback_reason"):
            _increment(stats["fallback_reasons"], str(row["fallback_reason"]))
        latency = _optional_int(row.get("latency_ms"))
        if isinstance(player_id, str) and latency is not None:
            latencies_by_player.setdefault(player_id, []).append(latency)
    for player_id, latencies in latencies_by_player.items():
        if latencies:
            _set_player_metric(by_player, player_id, "average_decision_latency_ms", round(sum(latencies) / len(latencies), 2))
    total_resolved = stats["total_resolved"]
    if total_resolved:
        run_metrics["reliability_metrics"]["invalid_attempt_rate"] = stats["invalid_attempts"] / total_resolved
        run_metrics["reliability_metrics"]["retry_rate"] = stats["retries"] / total_resolved
        run_metrics["reliability_metrics"]["fallback_rate"] = stats["fallbacks"] / total_resolved
    all_latencies = [latency for latencies in latencies_by_player.values() for latency in latencies]
    if all_latencies:
        run_metrics["reliability_metrics"]["average_decision_latency_ms"] = round(sum(all_latencies) / len(all_latencies), 2)
    for player in by_player.values():
        decision_count = _int(player.get("decision_count"))
        if decision_count:
            player["valid_first_response_rate"] = player["valid_first_response_count"] / decision_count
            player["retry_rate"] = player["retries_used"] / decision_count
            player["fallback_rate"] = player["fallbacks_used"] / decision_count


def _apply_usage_metrics(
    by_player: dict[str, dict[str, Any]],
    run_metrics: dict[str, Any],
    usage: dict[str, Any],
) -> None:
    totals = _dict(usage.get("totals"))
    usage_metrics = run_metrics["usage_metrics"]
    usage_metrics["total_input_tokens"] = _int(totals.get("prompt_tokens") or totals.get("input_tokens"))
    usage_metrics["total_output_tokens"] = _int(totals.get("completion_tokens") or totals.get("output_tokens"))
    usage_metrics["total_reasoning_tokens"] = _int(totals.get("reasoning_tokens"))
    usage_metrics["total_cached_tokens"] = _int(totals.get("cached_tokens"))
    usage_metrics["total_tokens"] = _int(totals.get("total_tokens")) or (
        usage_metrics["total_input_tokens"] + usage_metrics["total_output_tokens"]
    )
    total_cost = totals.get("cost")
    usage_metrics["total_cost"] = float(total_cost) if isinstance(total_cost, (int, float)) else 0.0
    total_decisions = _int(run_metrics["decision_stats"].get("total_resolved"))
    final_turn = _int(run_metrics.get("final_turn_index"))
    if total_decisions:
        usage_metrics["cost_per_decision"] = round(usage_metrics["total_cost"] / total_decisions, 10)
    if final_turn:
        usage_metrics["cost_per_turn"] = round(usage_metrics["total_cost"] / final_turn, 10)
    if by_player:
        usage_metrics["cost_per_completed_game"] = round(usage_metrics["total_cost"], 10)

    usage_by_player = _dict(usage.get("by_player"))
    for player_id, player in by_player.items():
        row = _dict(usage_by_player.get(player_id))
        prompt_tokens = _int(row.get("prompt_tokens") or row.get("input_tokens"))
        completion_tokens = _int(row.get("completion_tokens") or row.get("output_tokens"))
        player["total_input_tokens"] = prompt_tokens
        player["total_output_tokens"] = completion_tokens
        player["total_reasoning_tokens"] = _int(row.get("reasoning_tokens"))
        player["total_cached_tokens"] = _int(row.get("cached_tokens"))
        player["total_tokens"] = _int(row.get("total_tokens")) or prompt_tokens + completion_tokens
        cost = row.get("cost")
        player["total_cost"] = float(cost) if isinstance(cost, (int, float)) else 0.0
        decision_count = _int(player.get("decision_count")) or _int(row.get("decision_count"))
        if decision_count:
            player["cost_per_decision"] = round(player["total_cost"] / decision_count, 10)


def _apply_snapshot_cash_metrics(
    by_player: dict[str, dict[str, Any]],
    cash_history_by_player: dict[str, list[int]],
    snapshots: list[dict[str, Any]],
) -> None:
    low_cash_counts: dict[str, int] = {player_id: 0 for player_id in by_player}
    for snapshot in snapshots:
        for player in _list(snapshot.get("players")):
            if not isinstance(player, dict):
                continue
            player_id = player.get("player_id")
            cash = player.get("cash")
            if isinstance(player_id, str) and isinstance(cash, (int, float)):
                cash_history_by_player.setdefault(player_id, []).append(int(cash))
                if cash < 100:
                    low_cash_counts[player_id] = low_cash_counts.get(player_id, 0) + 1
    for player_id, history in cash_history_by_player.items():
        if player_id not in by_player or not history:
            continue
        by_player[player_id]["lowest_cash_reached"] = min(history)
        by_player[player_id]["average_cash_observed"] = round(sum(history) / len(history), 2)
        by_player[player_id]["ended_turn_low_cash_count"] = low_cash_counts.get(player_id, 0)


def _apply_final_summary_metrics(
    by_player: dict[str, dict[str, Any]],
    summary: dict[str, Any],
    owner_by_index: dict[int, str | None],
    mortgaged_by_index: dict[int, bool],
    buildings_by_index: dict[int, dict[str, int]],
    board: dict[str, Any],
) -> None:
    winner_id = summary.get("winner_player_id")
    for player_id, player in by_player.items():
        summary_player = _dict(_dict(summary.get("players")).get(player_id))
        if summary_player:
            player["final_cash"] = summary_player.get("cash")
            player["final_net_worth_estimate"] = summary_player.get("net_worth_estimate")
            player["primary_score"] = summary_player.get("net_worth_estimate")
            player["bankrupt"] = bool(summary_player.get("bankrupt", player.get("bankrupt", False)))
            player["turns_played"] = _int(summary_player.get("turns_played"))
            player["turns_survived"] = _int(summary_player.get("turns_played"))
        player["winner"] = player_id == winner_id
        owned = [space_index for space_index, owner_id in owner_by_index.items() if owner_id == player_id]
        player["final_property_count"] = len(owned)
        player["final_mortgage_count"] = sum(1 for space_index in owned if mortgaged_by_index.get(space_index, False))
        player["final_unmortgaged_property_count"] = player["final_property_count"] - player["final_mortgage_count"]
        player["final_property_face_value"] = sum(board["price_by_index"].get(space_index, 0) for space_index in owned)
        player["final_railroad_count"] = sum(1 for space_index in owned if board["kind_by_index"].get(space_index) == "RAILROAD")
        player["final_utility_count"] = sum(1 for space_index in owned if board["kind_by_index"].get(space_index) == "UTILITY")
        player["houses_owned"] = sum(_dict(buildings_by_index.get(space_index)).get("houses", 0) for space_index in owned)
        player["hotels_owned"] = sum(_dict(buildings_by_index.get(space_index)).get("hotels", 0) for space_index in owned)
        player["final_building_value_estimate"] = _building_value_estimate(
            player_id,
            owner_by_index,
            buildings_by_index,
            board,
        )
        player["final_mortgage_liability_estimate"] = sum(
            board["price_by_index"].get(space_index, 0) // 2
            for space_index in owned
            if mortgaged_by_index.get(space_index, False)
        )
        player["final_liquid_net_worth_estimate"] = (
            None
            if player["final_cash"] is None
            else player["final_cash"] + player["final_mortgage_liability_estimate"]
        )
        player["final_complete_color_group_count"] = _complete_color_group_count(player_id, owner_by_index, board)
        player["final_developed_monopoly_count"] = _developed_monopoly_count(
            player_id,
            owner_by_index,
            buildings_by_index,
            board,
        )
        player["net_rent_flow"] = player["rent_collected"] - player["rent_paid"]
        turns_survived = _int(player.get("turns_survived"))
        if turns_survived and isinstance(player.get("total_cost"), (int, float)):
            player["cost_per_turn_survived"] = round(float(player["total_cost"]) / turns_survived, 10)
        net_worth = player.get("final_net_worth_estimate")
        if isinstance(net_worth, (int, float)) and net_worth:
            player["cost_per_net_worth_point"] = round(float(player["total_cost"]) / float(net_worth), 10)


def _rank_players(by_player: dict[str, dict[str, Any]], run_metrics: dict[str, Any]) -> None:
    ranked = sorted(
        by_player.values(),
        key=lambda player: (
            _number_or_min(player.get("final_net_worth_estimate")),
            bool(player.get("winner")),
            _number_or_min(player.get("final_liquid_net_worth_estimate")),
            _number_or_min(player.get("final_cash")),
        ),
        reverse=True,
    )
    for index, player in enumerate(ranked, start=1):
        player["final_rank"] = index
    run_metrics["rankings"] = [
        {
            "player_id": player["player_id"],
            "rank": player["final_rank"],
            "primary_score": player["primary_score"],
            "winner": player["winner"],
        }
        for player in ranked
    ]


def _apply_score_matrix(by_player: dict[str, dict[str, Any]], run_metrics: dict[str, Any]) -> None:
    players = list(by_player.values())
    if not players:
        return
    max_net_worth = max((_number_or_zero(player.get("final_net_worth_estimate")) for player in players), default=0.0)
    min_turns_to_win = min(
        (_number_or_zero(player.get("turns_survived")) for player in players if player.get("winner")),
        default=0.0,
    )
    max_opponents_bankrupted = max((_number_or_zero(player.get("opponents_bankrupted")) for player in players), default=0.0)
    matrix_rows: list[dict[str, Any]] = []
    for player in players:
        net_worth = _number_or_zero(player.get("final_net_worth_estimate"))
        turns_survived = _number_or_zero(player.get("turns_survived"))
        decision_count = _int(player.get("decision_count"))
        fallback_rate = float(player.get("fallback_rate") or 0.0)
        retry_rate = float(player.get("retry_rate") or 0.0)
        invalid_rate = 1.0 - float(player.get("valid_first_response_rate") or 0.0) if decision_count else 0.0
        net_worth_score = net_worth / max_net_worth if max_net_worth > 0 else 0.0
        winner_score = 1.0 if player.get("winner") else 0.0
        speed_score = (
            min_turns_to_win / turns_survived
            if player.get("winner") and min_turns_to_win > 0 and turns_survived > 0
            else 0.0
        )
        bankruptcy_pressure_score = (
            _number_or_zero(player.get("opponents_bankrupted")) / max_opponents_bankrupted
            if max_opponents_bankrupted > 0
            else 0.0
        )
        survival_score = 0.0 if player.get("bankrupt") else 1.0
        reliability_score = max(0.0, 1.0 - fallback_rate - (0.5 * retry_rate) - (0.25 * invalid_rate))
        total_cost = float(player.get("total_cost") or 0.0)
        cost_adjusted_score = net_worth / total_cost if total_cost > 0 else None
        combined = (
            0.45 * net_worth_score
            + 0.2 * winner_score
            + 0.1 * speed_score
            + 0.1 * bankruptcy_pressure_score
            + 0.1 * survival_score
            + 0.05 * reliability_score
        )
        player["score_matrix"] = {
            "net_worth_score": round(net_worth_score, 6),
            "winner_score": winner_score,
            "speed_score": round(speed_score, 6),
            "bankruptcy_pressure_score": round(bankruptcy_pressure_score, 6),
            "survival_score": survival_score,
            "reliability_score": round(reliability_score, 6),
            "cost_adjusted_score": cost_adjusted_score,
            "combined_experimental_score": round(combined, 6),
        }
        matrix_rows.append(
            {
                "player_id": player.get("player_id"),
                "model_id": player.get("openrouter_model_id"),
                "final_rank": player.get("final_rank"),
                **player["score_matrix"],
            }
        )
    run_metrics["score_matrix"]["rankings"] = sorted(
        matrix_rows,
        key=lambda row: (
            row.get("combined_experimental_score") or 0,
            row.get("net_worth_score") or 0,
            row.get("winner_score") or 0,
        ),
        reverse=True,
    )


def _decision_row(entry: dict[str, Any]) -> dict[str, Any]:
    attempts = [_dict(attempt) for attempt in _list(entry.get("attempts"))]
    invalid_attempts = sum(1 for attempt in attempts if attempt.get("validation_errors"))
    final_action = _dict(entry.get("final_action"))
    return {
        "schema_version": "v1",
        "run_id": entry.get("run_id"),
        "decision_id": entry.get("decision_id"),
        "turn_index": entry.get("turn_index"),
        "decision_type": entry.get("decision_type"),
        "player_id": entry.get("player_id"),
        "openrouter_model_id": entry.get("openrouter_model_id"),
        "model_display_name": entry.get("model_display_name"),
        "action_name": final_action.get("action"),
        "retry_used": bool(entry.get("retry_used")),
        "fallback_used": bool(entry.get("fallback_used")),
        "fallback_reason": entry.get("fallback_reason"),
        "invalid_attempts": invalid_attempts,
        "latency_ms": entry.get("latency_ms"),
        "emitted_event_seq_start": entry.get("emitted_event_seq_start"),
        "emitted_event_seq_end": entry.get("emitted_event_seq_end"),
    }


def _event_row(event: dict[str, Any]) -> dict[str, Any]:
    payload = _dict(event.get("payload"))
    actor = _dict(event.get("actor"))
    player_id = (
        payload.get("player_id")
        or payload.get("from_player_id")
        or payload.get("bidder_player_id")
        or payload.get("initiator_player_id")
        or actor.get("player_id")
    )
    return {
        "schema_version": "v1",
        "run_id": event.get("run_id"),
        "event_id": event.get("event_id"),
        "seq": event.get("seq"),
        "turn_index": event.get("turn_index"),
        "type": event.get("type"),
        "player_id": player_id,
    }


def _build_board_maps(board_spec: dict[str, Any]) -> dict[str, Any]:
    price_by_index: dict[int, int] = {}
    color_group_by_index: dict[int, str] = {}
    spaces_by_color_group: dict[str, set[int]] = {}
    kind_by_index: dict[int, str] = {}
    house_cost_by_group: dict[str, int] = {
        str(key): _int(value)
        for key, value in _dict(board_spec.get("house_cost_by_group")).items()
    }
    for space in _list(board_spec.get("spaces")):
        if not isinstance(space, dict):
            continue
        index = _optional_int(space.get("index"))
        if index is None:
            continue
        price_by_index[index] = _int(space.get("price"))
        kind = space.get("kind")
        if isinstance(kind, str):
            kind_by_index[index] = kind
        color_group = space.get("color_group") or space.get("group")
        if isinstance(color_group, str) and color_group:
            color_group_by_index[index] = color_group
            if color_group not in {"RAILROAD", "UTILITY"}:
                spaces_by_color_group.setdefault(color_group, set()).add(index)
    return {
        "price_by_index": price_by_index,
        "color_group_by_index": color_group_by_index,
        "spaces_by_color_group": spaces_by_color_group,
        "kind_by_index": kind_by_index,
        "house_cost_by_group": house_cost_by_group,
    }


def _complete_color_group_count(
    player_id: str,
    owner_by_index: dict[int, str | None],
    board: dict[str, Any],
) -> int:
    count = 0
    for value in _dict(board.get("spaces_by_color_group")).values():
        if not isinstance(value, (set, list, tuple)):
            continue
        space_indices = [space_index for space_index in value if isinstance(space_index, int)]
        if space_indices and all(owner_by_index.get(space_index) == player_id for space_index in space_indices):
            count += 1
    return count


def _developed_monopoly_count(
    player_id: str,
    owner_by_index: dict[int, str | None],
    buildings_by_index: dict[int, dict[str, int]],
    board: dict[str, Any],
) -> int:
    count = 0
    for value in _dict(board.get("spaces_by_color_group")).values():
        if not isinstance(value, (set, list, tuple)):
            continue
        space_indices = [space_index for space_index in value if isinstance(space_index, int)]
        if not space_indices or not all(owner_by_index.get(space_index) == player_id for space_index in space_indices):
            continue
        if any(
            _int(_dict(buildings_by_index.get(space_index)).get("houses"))
            or _int(_dict(buildings_by_index.get(space_index)).get("hotels"))
            for space_index in space_indices
        ):
            count += 1
    return count


def _building_value_estimate(
    player_id: str,
    owner_by_index: dict[int, str | None],
    buildings_by_index: dict[int, dict[str, int]],
    board: dict[str, Any],
) -> int:
    total = 0
    for space_index, buildings in buildings_by_index.items():
        if owner_by_index.get(space_index) != player_id:
            continue
        group = board["color_group_by_index"].get(space_index)
        if not isinstance(group, str):
            continue
        house_cost = _int(board["house_cost_by_group"].get(group))
        total += _int(buildings.get("houses")) * house_cost
        total += _int(buildings.get("hotels")) * house_cost * 5
    return total


def _add_player_metric(by_player: dict[str, dict[str, Any]], player_id: Any, metric: str, amount: int | float) -> None:
    if not isinstance(player_id, str) or player_id not in by_player:
        return
    by_player[player_id][metric] = by_player[player_id].get(metric, 0) + amount


def _set_player_metric(by_player: dict[str, dict[str, Any]], player_id: Any, metric: str, value: Any) -> None:
    if not isinstance(player_id, str) or player_id not in by_player:
        return
    by_player[player_id][metric] = value


def _increment(mapping: dict[str, int], key: str) -> None:
    mapping[key] = mapping.get(key, 0) + 1


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
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


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _read_snapshots(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    snapshots: list[dict[str, Any]] = []
    for child in sorted(path.glob("turn_*.json")):
        parsed = _read_json(child)
        if parsed:
            snapshots.append(parsed)
    return snapshots


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, separators=(",", ":"), ensure_ascii=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _resolve_repo_root() -> Path:
    start = Path(__file__).resolve()
    current = start if start.is_dir() else start.parent
    for parent in [current, *current.parents]:
        if (parent / "contracts").is_dir():
            return parent
    raise RuntimeError("Repo root not found (expected contracts/).")


def _load_board_spec() -> dict[str, Any]:
    board_path = _resolve_repo_root() / "contracts" / "data" / "board.json"
    return json.loads(board_path.read_text(encoding="utf-8"))


def _int(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) else 0


def _optional_int(value: Any) -> int | None:
    return int(value) if isinstance(value, (int, float)) else None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _number_or_min(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else float("-inf")


def _number_or_zero(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else 0.0


def _normalize_space_key(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name.strip())
    return cleaned.strip("_").upper()
