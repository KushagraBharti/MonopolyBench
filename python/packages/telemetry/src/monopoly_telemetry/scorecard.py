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
    players_payload = _read_json(run_files.players_path)
    seat_assignment = _read_json(run_files.seat_assignment_path)
    board_spec = _load_board_spec()
    return _build_scorecard_from_logs(
        run_id=run_files.run_id,
        events=events,
        decisions=decisions,
        actions=actions,
        summary=summary,
        players_payload=players_payload,
        seat_assignment=seat_assignment,
        board_spec=board_spec,
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
    players_payload: dict[str, Any],
    seat_assignment: dict[str, Any],
    board_spec: dict[str, Any],
) -> dict[str, Any]:
    board = _build_board_maps(board_spec)
    players = _collect_players(summary, players_payload, seat_assignment, events, decisions, actions)
    by_player = {player["player_id"]: _empty_player_score(player) for player in players}
    run_metrics = _empty_run_metrics(run_id, summary, events, decisions, actions)
    event_rows: list[dict[str, Any]] = []

    owner_by_index: dict[int, str | None] = {}
    mortgaged_by_index: dict[int, bool] = {}

    for event in events:
        event_type = str(event.get("type") or "")
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
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
            continue

        if event_type == "CASH_CHANGED":
            player_id = payload.get("player_id")
            delta = _int(payload.get("delta"))
            reason = str(payload.get("reason") or "")
            _add_player_metric(by_player, player_id, "cash_delta_total", delta)
            if reason.startswith("TAX"):
                amount = abs(delta)
                run_metrics["total_tax_paid"] += amount
                _add_player_metric(by_player, player_id, "taxes_paid", amount)
            if reason.startswith("BANKRUPTCY"):
                run_metrics["total_bankruptcies"] += 1 if reason == "BANKRUPTCY" else 0
                if reason == "BANKRUPTCY":
                    _set_player_metric(by_player, player_id, "bankrupt", True)
                    _set_player_metric(by_player, player_id, "bankruptcy_turn", event.get("turn_index"))
            continue

        if event_type == "PROPERTY_PURCHASED":
            player_id = payload.get("player_id")
            space_index = _optional_int(payload.get("space_index"))
            price = _int(payload.get("price"))
            if space_index is not None:
                owner_by_index[space_index] = str(player_id) if isinstance(player_id, str) else None
                mortgaged_by_index.setdefault(space_index, False)
            run_metrics["total_property_purchase_count"] += 1
            if price > 0:
                run_metrics["total_property_purchase_volume"] += price
            _add_player_metric(by_player, player_id, "properties_bought_directly", 1)
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
            continue

        if event_type == "PROPERTY_MORTGAGED":
            player_id = payload.get("player_id")
            space_index = _optional_int(payload.get("space_index"))
            if space_index is not None:
                mortgaged_by_index[space_index] = True
            run_metrics["total_mortgages"] += 1
            _add_player_metric(by_player, player_id, "mortgages", 1)
            continue

        if event_type == "PROPERTY_UNMORTGAGED":
            player_id = payload.get("player_id")
            space_index = _optional_int(payload.get("space_index"))
            if space_index is not None:
                mortgaged_by_index[space_index] = False
            run_metrics["total_unmortgages"] += 1
            _add_player_metric(by_player, player_id, "unmortgages", 1)
            continue

        if event_type in {"HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD"}:
            player_id = payload.get("player_id")
            count = _int(payload.get("count"))
            metric = {
                "HOUSE_BUILT": "houses_built",
                "HOTEL_BUILT": "hotels_built",
                "HOUSE_SOLD": "houses_sold",
                "HOTEL_SOLD": "hotels_sold",
            }[event_type]
            run_metric = f"total_{metric}"
            run_metrics[run_metric] += count
            _add_player_metric(by_player, player_id, metric, count)
            continue

        if event_type == "SENT_TO_JAIL":
            player_id = payload.get("player_id")
            _add_player_metric(by_player, player_id, "jail_entries", 1)
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
            continue

        if event_type.startswith("TRADE_"):
            _apply_trade_event_metrics(by_player, run_metrics, event_type, payload)

    decision_rows = [_decision_row(entry) for entry in decisions if entry.get("phase") == "decision_resolved"]
    _apply_decision_metrics(by_player, run_metrics, decision_rows)
    _apply_final_summary_metrics(by_player, summary, owner_by_index, mortgaged_by_index, board)
    _rank_players(by_player, run_metrics)

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
        "final_net_worth_estimate": None,
        "final_liquid_net_worth_estimate": None,
        "bankrupt": False,
        "bankruptcy_turn": None,
        "turns_played": 0,
        "turns_survived": 0,
        "opponents_bankrupted": 0,
        "final_property_count": 0,
        "final_mortgage_count": 0,
        "final_unmortgaged_property_count": 0,
        "final_complete_color_group_count": 0,
        "houses_built": 0,
        "hotels_built": 0,
        "houses_sold": 0,
        "hotels_sold": 0,
        "rent_collected": 0,
        "rent_paid": 0,
        "net_rent_flow": 0,
        "taxes_paid": 0,
        "jail_entries": 0,
        "properties_bought_directly": 0,
        "properties_won_by_auction": 0,
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
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_reasoning_tokens": 0,
        "total_cached_tokens": 0,
        "total_cost": 0.0,
        "cash_delta_total": 0,
        "mortgages": 0,
        "unmortgages": 0,
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
    for entry in players_payload.get("players", []):
        if isinstance(entry, dict) and isinstance(entry.get("player_id"), str):
            by_id[entry["player_id"]] = dict(entry)
    for assignment in seat_assignment.get("assignments", []):
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
    for player_id, entry in summary.get("players", {}).items():
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


def _apply_final_summary_metrics(
    by_player: dict[str, dict[str, Any]],
    summary: dict[str, Any],
    owner_by_index: dict[int, str | None],
    mortgaged_by_index: dict[int, bool],
    board: dict[str, Any],
) -> None:
    winner_id = summary.get("winner_player_id")
    for player_id, player in by_player.items():
        summary_player = summary.get("players", {}).get(player_id, {})
        if isinstance(summary_player, dict):
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
        player["net_rent_flow"] = player["rent_collected"] - player["rent_paid"]


def _rank_players(by_player: dict[str, dict[str, Any]], run_metrics: dict[str, Any]) -> None:
    ranked = sorted(
        by_player.values(),
        key=lambda player: (
            bool(player.get("winner")),
            _number_or_min(player.get("final_net_worth_estimate")),
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


def _decision_row(entry: dict[str, Any]) -> dict[str, Any]:
    attempts = entry.get("attempts") if isinstance(entry.get("attempts"), list) else []
    invalid_attempts = sum(1 for attempt in attempts if attempt.get("validation_errors"))
    return {
        "schema_version": "v1",
        "run_id": entry.get("run_id"),
        "decision_id": entry.get("decision_id"),
        "turn_index": entry.get("turn_index"),
        "decision_type": entry.get("decision_type"),
        "player_id": entry.get("player_id"),
        "openrouter_model_id": entry.get("openrouter_model_id"),
        "model_display_name": entry.get("model_display_name"),
        "action_name": (entry.get("final_action") or {}).get("action") if isinstance(entry.get("final_action"), dict) else None,
        "retry_used": bool(entry.get("retry_used")),
        "fallback_used": bool(entry.get("fallback_used")),
        "fallback_reason": entry.get("fallback_reason"),
        "invalid_attempts": invalid_attempts,
        "latency_ms": entry.get("latency_ms"),
        "emitted_event_seq_start": entry.get("emitted_event_seq_start"),
        "emitted_event_seq_end": entry.get("emitted_event_seq_end"),
    }


def _event_row(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    actor = event.get("actor") if isinstance(event.get("actor"), dict) else {}
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
    for space in board_spec.get("spaces", []):
        if not isinstance(space, dict):
            continue
        index = _optional_int(space.get("index"))
        if index is None:
            continue
        price_by_index[index] = _int(space.get("price"))
        color_group = space.get("color_group")
        if isinstance(color_group, str) and color_group:
            color_group_by_index[index] = color_group
            spaces_by_color_group.setdefault(color_group, set()).add(index)
    return {
        "price_by_index": price_by_index,
        "color_group_by_index": color_group_by_index,
        "spaces_by_color_group": spaces_by_color_group,
    }


def _complete_color_group_count(
    player_id: str,
    owner_by_index: dict[int, str | None],
    board: dict[str, Any],
) -> int:
    count = 0
    for space_indices in board["spaces_by_color_group"].values():
        if space_indices and all(owner_by_index.get(space_index) == player_id for space_index in space_indices):
            count += 1
    return count


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


def _number_or_min(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) else float("-inf")


def _normalize_space_key(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name.strip())
    return cleaned.strip("_").upper()
