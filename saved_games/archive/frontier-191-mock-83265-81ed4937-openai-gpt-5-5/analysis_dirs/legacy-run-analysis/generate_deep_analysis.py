from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt
import pandas as pd


RUN_DIR = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = RUN_DIR / "analysis"
TABLE_DIR = ANALYSIS_DIR / "tables"
PLOT_DIR = ANALYSIS_DIR / "plots"

PLAYERS = [
    "OpenAI GPT 5.5",
    "Claude Opus 4.8",
    "Gemini 3.1 Pro Preview",
    "Grok 4.3",
]

COLORS = {
    "OpenAI GPT 5.5": "#111827",
    "Claude Opus 4.8": "#d97706",
    "Gemini 3.1 Pro Preview": "#2563eb",
    "Grok 4.3": "#16a34a",
}

HOUSE_COST_BY_GROUP = {
    "BROWN": 50,
    "LIGHT_BLUE": 50,
    "PINK": 100,
    "ORANGE": 100,
    "RED": 150,
    "YELLOW": 150,
    "GREEN": 200,
    "DARK_BLUE": 200,
}

EVENT_GROUPS = {
    "llm": {"LLM_DECISION_REQUESTED", "LLM_DECISION_RESPONSE", "LLM_PUBLIC_MESSAGE", "LLM_PRIVATE_THOUGHT"},
    "cash": {"CASH_CHANGED", "RENT_PAID"},
    "trade": {"TRADE_PROPOSED", "TRADE_COUNTERED", "TRADE_ACCEPTED", "TRADE_REJECTED"},
    "auction": {"AUCTION_STARTED", "AUCTION_BID_PLACED", "AUCTION_PLAYER_DROPPED", "AUCTION_ENDED"},
    "building": {"HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD"},
    "property": {"PROPERTY_PURCHASED", "PROPERTY_TRANSFERRED", "PROPERTY_MORTGAGED", "PROPERTY_UNMORTGAGED"},
    "movement": {"TURN_STARTED", "TURN_ENDED", "DICE_ROLLED", "PLAYER_MOVED", "SENT_TO_JAIL", "CARD_DRAWN"},
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    if not rows and not fieldnames:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = fieldnames or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def snapshot_sort_key(path: Path) -> tuple[int, int]:
    parts = path.stem.split("_")
    turn = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else -1
    decision = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    return turn, decision


def build_board_map(snapshot: dict) -> dict[int, dict]:
    return {int(space["index"]): space for space in snapshot.get("board", [])}


def board_value_by_player(snapshot: dict) -> dict[str, dict]:
    values = {
        player: {
            "property_value": 0,
            "building_value": 0,
            "mortgage_liability": 0,
            "property_count": 0,
            "mortgaged_count": 0,
            "unmortgaged_count": 0,
            "houses": 0,
            "hotels": 0,
            "complete_groups": 0,
        }
        for player in PLAYERS
    }
    group_owners: dict[str, list[str | None]] = defaultdict(list)
    for space in snapshot.get("board", []):
        group = space.get("group")
        if group and group not in {"RAILROAD", "UTILITY"}:
            group_owners[group].append(space.get("owner_id"))
        owner = space.get("owner_id")
        if owner not in values:
            continue
        price = int(space.get("price") or 0)
        house_cost = HOUSE_COST_BY_GROUP.get(group, 0)
        houses = int(space.get("houses") or 0)
        hotel = bool(space.get("hotel"))
        values[owner]["property_value"] += price
        values[owner]["building_value"] += houses * house_cost + (house_cost * 5 if hotel else 0)
        values[owner]["property_count"] += 1
        values[owner]["houses"] += houses
        values[owner]["hotels"] += int(hotel)
        if space.get("mortgaged"):
            values[owner]["mortgage_liability"] += price // 2
            values[owner]["mortgaged_count"] += 1
        else:
            values[owner]["unmortgaged_count"] += 1
    for group, owners in group_owners.items():
        if owners and owners[0] in values and all(owner == owners[0] for owner in owners):
            values[owners[0]]["complete_groups"] += 1
    return values


def latest_snapshots_by_turn() -> tuple[list[dict], dict | None, dict[int, dict]]:
    latest: dict[int, Path] = {}
    for path in (RUN_DIR / "state").glob("turn_*.json"):
        turn, _ = snapshot_sort_key(path)
        if turn < 0:
            continue
        if turn not in latest or snapshot_sort_key(path) > snapshot_sort_key(latest[turn]):
            latest[turn] = path

    rows: list[dict] = []
    snapshots: dict[int, dict] = {}
    final_snapshot = None
    for turn in sorted(latest):
        snapshot = read_json(latest[turn])
        snapshots[turn] = snapshot
        final_snapshot = snapshot
        values = board_value_by_player(snapshot)
        players_by_id = {player["player_id"]: player for player in snapshot.get("players", [])}
        for player_id in PLAYERS:
            player = players_by_id.get(player_id, {})
            v = values[player_id]
            cash = int(player.get("cash") or 0)
            net_worth = cash + v["property_value"] + v["building_value"] - v["mortgage_liability"]
            rows.append(
                {
                    "turn_index": turn,
                    "player_id": player_id,
                    "cash": cash,
                    "net_worth": net_worth,
                    "property_value": v["property_value"],
                    "building_value": v["building_value"],
                    "mortgage_liability": v["mortgage_liability"],
                    "property_count": v["property_count"],
                    "mortgaged_count": v["mortgaged_count"],
                    "unmortgaged_count": v["unmortgaged_count"],
                    "houses": v["houses"],
                    "hotels": v["hotels"],
                    "complete_groups": v["complete_groups"],
                    "bankrupt": bool(player.get("bankrupt")),
                    "position": player.get("position"),
                    "in_jail": bool(player.get("in_jail")),
                }
            )
    return rows, final_snapshot, snapshots


def usage_from_attempt(attempt: dict) -> dict:
    usage = ((attempt.get("raw_response") or {}).get("usage") or {})
    prompt_details = usage.get("prompt_tokens_details") or {}
    completion_details = usage.get("completion_tokens_details") or {}
    return {
        "input_tokens": int(usage.get("prompt_tokens") or 0),
        "output_tokens": int(usage.get("completion_tokens") or 0),
        "total_tokens": int(usage.get("total_tokens") or 0),
        "reasoning_tokens": int(completion_details.get("reasoning_tokens") or 0),
        "cached_tokens": int(prompt_details.get("cached_tokens") or 0),
        "cost": float(usage.get("cost") or 0.0),
    }


def parse_decisions(decisions: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    resolved = [row for row in decisions if row.get("phase") == "decision_resolved"]
    started = [row for row in decisions if row.get("phase") == "decision_started"]
    calls = []
    attempts = []
    for call_index, decision in enumerate(resolved, start=1):
        usage_totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "reasoning_tokens": 0, "cached_tokens": 0, "cost": 0.0}
        invalid_attempts = 0
        missing_usage = 0
        provider_model = None
        provider_name = None
        for attempt_index, attempt in enumerate(decision.get("attempts") or [], start=1):
            raw = attempt.get("raw_response") or {}
            provider_model = provider_model or raw.get("model")
            provider_name = provider_name or raw.get("provider")
            usage = usage_from_attempt(attempt)
            if not usage["total_tokens"] and not usage["cost"]:
                missing_usage += 1
            errors = attempt.get("validation_errors") or []
            invalid_attempts += int(bool(errors))
            for key in usage_totals:
                usage_totals[key] += usage[key]
            attempts.append(
                {
                    "call_index": call_index,
                    "attempt_index": attempt_index,
                    "turn_index": decision.get("turn_index"),
                    "decision_id": decision.get("decision_id"),
                    "player_id": decision.get("player_id"),
                    "model_id": decision.get("openrouter_model_id"),
                    "provider_model": raw.get("model"),
                    "provider_name": raw.get("provider"),
                    "decision_type": decision.get("decision_type"),
                    "outcome": attempt.get("outcome"),
                    "error_type": attempt.get("error_type"),
                    "error_message": attempt.get("error_message"),
                    "validation_error_count": len(errors),
                    "latency_ms": int(attempt.get("latency_ms") or 0),
                    **usage,
                }
            )
        final_action = decision.get("final_action") or {}
        calls.append(
            {
                "call_index": call_index,
                "turn_index": int(decision.get("turn_index") or 0),
                "decision_id": decision.get("decision_id"),
                "player_id": decision.get("player_id"),
                "model_id": decision.get("openrouter_model_id"),
                "provider_model": provider_model,
                "provider_name": provider_name,
                "decision_type": decision.get("decision_type"),
                "action": final_action.get("action"),
                "attempt_count": len(decision.get("attempts") or []),
                "invalid_attempts": invalid_attempts,
                "retry_used": bool(decision.get("retry_used")),
                "fallback_used": bool(decision.get("fallback_used")),
                "fallback_reason": decision.get("fallback_reason"),
                "missing_usage_attempts": missing_usage,
                "latency_ms": int(decision.get("latency_ms") or 0),
                **usage_totals,
            }
        )
    resolved_ids = {row.get("decision_id") for row in resolved}
    pending = [row for row in started if row.get("decision_id") not in resolved_ids]
    return calls, attempts, pending


def event_derived_tables(events: list[dict], board_by_index: dict[int, dict]) -> dict[str, list[dict]]:
    event_counts = [{"event_type": k, "count": v} for k, v in Counter(e.get("type") for e in events).most_common()]
    events_by_turn: dict[int, Counter] = defaultdict(Counter)
    cash_rows = []
    rent_rows = []
    trade_rows = []
    auction_rows = []
    building_rows = []
    property_rows = []
    jail_rows = []
    bankruptcy_rows = []
    movement_rows = []

    for event in events:
        event_type = event.get("type")
        turn = int(event.get("turn_index") or 0)
        seq = int(event.get("seq") or 0)
        payload = event.get("payload") or {}
        events_by_turn[turn][event_type] += 1

        if event_type == "CASH_CHANGED":
            cash_rows.append(
                {
                    "turn_index": turn,
                    "seq": seq,
                    "player_id": payload.get("player_id"),
                    "delta": int(payload.get("delta") or 0),
                    "reason": payload.get("reason"),
                }
            )
            if payload.get("reason") == "BANKRUPTCY":
                bankruptcy_rows.append({"turn_index": turn, "seq": seq, "player_id": payload.get("player_id")})
        elif event_type == "RENT_PAID":
            space = board_by_index.get(int(payload.get("space_index") or -1), {})
            rent_rows.append(
                {
                    "turn_index": turn,
                    "seq": seq,
                    "from_player_id": payload.get("from_player_id"),
                    "to_player_id": payload.get("to_player_id"),
                    "amount": int(payload.get("amount") or 0),
                    "space_index": payload.get("space_index"),
                    "space_name": space.get("name"),
                    "space_group": space.get("group"),
                }
            )
        elif event_type in {"TRADE_PROPOSED", "TRADE_COUNTERED", "TRADE_ACCEPTED", "TRADE_REJECTED"}:
            trade_rows.append(
                {
                    "turn_index": turn,
                    "seq": seq,
                    "event_type": event_type,
                    "initiator_player_id": payload.get("initiator_player_id"),
                    "counterparty_player_id": payload.get("counterparty_player_id"),
                    "exchange_index": payload.get("exchange_index"),
                    "offer_cash": (payload.get("offer") or {}).get("cash", 0),
                    "request_cash": (payload.get("request") or {}).get("cash", 0),
                    "offer_properties": ",".join((payload.get("offer") or {}).get("properties") or []),
                    "request_properties": ",".join((payload.get("request") or {}).get("properties") or []),
                    "offer_jail_cards": (payload.get("offer") or {}).get("get_out_of_jail_cards", 0),
                    "request_jail_cards": (payload.get("request") or {}).get("get_out_of_jail_cards", 0),
                }
            )
        elif event_type in {"AUCTION_STARTED", "AUCTION_BID_PLACED", "AUCTION_PLAYER_DROPPED", "AUCTION_ENDED"}:
            auction_rows.append(
                {
                    "turn_index": turn,
                    "seq": seq,
                    "event_type": event_type,
                    "player_id": payload.get("player_id") or payload.get("winner_player_id"),
                    "property_space": payload.get("property_space"),
                    "bid": payload.get("bid"),
                    "winning_bid": payload.get("winning_bid"),
                    "reason": payload.get("reason"),
                }
            )
        elif event_type in {"HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD"}:
            space = board_by_index.get(int(payload.get("space_index") or -1), {})
            building_rows.append(
                {
                    "turn_index": turn,
                    "seq": seq,
                    "event_type": event_type,
                    "player_id": payload.get("player_id"),
                    "space_index": payload.get("space_index"),
                    "space_name": space.get("name"),
                    "space_group": space.get("group"),
                    "count": int(payload.get("count") or 0),
                }
            )
        elif event_type in {"PROPERTY_PURCHASED", "PROPERTY_TRANSFERRED", "PROPERTY_MORTGAGED", "PROPERTY_UNMORTGAGED"}:
            space_index = payload.get("space_index")
            if space_index is None and payload.get("properties"):
                space_index = None
            space = board_by_index.get(int(space_index or -1), {})
            property_rows.append(
                {
                    "turn_index": turn,
                    "seq": seq,
                    "event_type": event_type,
                    "player_id": payload.get("player_id") or payload.get("to_player_id") or payload.get("from_player_id"),
                    "space_index": space_index,
                    "space_name": space.get("name"),
                    "space_group": space.get("group"),
                    "price": payload.get("price"),
                    "from_player_id": payload.get("from_player_id"),
                    "to_player_id": payload.get("to_player_id"),
                }
            )
        elif event_type == "SENT_TO_JAIL":
            jail_rows.append({"turn_index": turn, "seq": seq, "player_id": payload.get("player_id"), "reason": payload.get("reason")})
        elif event_type in {"DICE_ROLLED", "PLAYER_MOVED", "CARD_DRAWN"}:
            row = {"turn_index": turn, "seq": seq, "event_type": event_type, "player_id": (event.get("actor") or {}).get("player_id")}
            row.update(payload)
            movement_rows.append(row)

    all_event_types = sorted({e.get("type") for e in events})
    by_turn_rows = []
    for turn, counter in sorted(events_by_turn.items()):
        row = {"turn_index": turn, "total_events": sum(counter.values())}
        for group, event_types in EVENT_GROUPS.items():
            row[f"{group}_events"] = sum(counter.get(t, 0) for t in event_types)
        for event_type in all_event_types:
            row[event_type] = counter.get(event_type, 0)
        by_turn_rows.append(row)

    return {
        "event_counts": event_counts,
        "events_by_turn": by_turn_rows,
        "cash_events": cash_rows,
        "rent_events": rent_rows,
        "trade_events": trade_rows,
        "auction_events": auction_rows,
        "building_events": building_rows,
        "property_events": property_rows,
        "jail_events": jail_rows,
        "bankruptcies": bankruptcy_rows,
        "movement_events": movement_rows,
    }


def group_sum(rows: list[dict], keys: list[str], sum_cols: list[str], count_name: str = "count") -> list[dict]:
    grouped: dict[tuple, dict] = {}
    for row in rows:
        key = tuple(row.get(k) for k in keys)
        target = grouped.setdefault(key, {k: row.get(k) for k in keys} | {count_name: 0} | {c: 0 for c in sum_cols})
        target[count_name] += 1
        for col in sum_cols:
            target[col] += float(row.get(col) or 0)
    return list(grouped.values())


def aggregate_tables(calls: list[dict], event_tables: dict[str, list[dict]], state_rows: list[dict]) -> dict[str, list[dict]]:
    by_model = group_sum(
        calls,
        ["player_id", "model_id"],
        ["input_tokens", "output_tokens", "reasoning_tokens", "total_tokens", "cached_tokens", "cost", "latency_ms", "invalid_attempts"],
        "calls",
    )
    for row in by_model:
        calls_count = row["calls"] or 1
        row["avg_latency_ms"] = round(row["latency_ms"] / calls_count, 2)
        row["cost_per_call"] = round(row["cost"] / calls_count, 8)
    by_model.sort(key=lambda r: r["cost"], reverse=True)

    decision_type = group_sum(
        calls,
        ["player_id", "decision_type"],
        ["input_tokens", "output_tokens", "reasoning_tokens", "total_tokens", "cost", "latency_ms", "invalid_attempts"],
        "calls",
    )
    for row in decision_type:
        row["avg_latency_ms"] = round(row["latency_ms"] / (row["calls"] or 1), 2)
        row["cost_per_call"] = round(row["cost"] / (row["calls"] or 1), 8)
    decision_type.sort(key=lambda r: (r["player_id"] or "", -r["cost"]))

    action_mix = group_sum(calls, ["player_id", "decision_type", "action"], ["cost", "latency_ms"], "calls")
    for row in action_mix:
        row["avg_latency_ms"] = round(row["latency_ms"] / (row["calls"] or 1), 2)
    action_mix.sort(key=lambda r: (r["player_id"] or "", r["decision_type"] or "", -(r["calls"] or 0)))

    calls_by_turn = group_sum(
        calls,
        ["turn_index"],
        ["input_tokens", "output_tokens", "reasoning_tokens", "total_tokens", "cost", "latency_ms", "invalid_attempts"],
        "calls",
    )
    calls_by_turn_by_key = {int(row["turn_index"]): row for row in calls_by_turn}
    events_by_turn_by_key = {int(row["turn_index"]): row for row in event_tables["events_by_turn"]}

    state_wide: dict[int, dict] = defaultdict(dict)
    for row in state_rows:
        turn = int(row["turn_index"])
        player = row["player_id"].split()[0].lower()
        if player == "gemini":
            player = "gemini"
        state_wide[turn][f"{player}_net_worth"] = row["net_worth"]
        state_wide[turn][f"{player}_cash"] = row["cash"]
        state_wide[turn][f"{player}_houses"] = row["houses"]
        state_wide[turn][f"{player}_hotels"] = row["hotels"]
        state_wide[turn][f"{player}_properties"] = row["property_count"]

    max_turn = max([int(row["turn_index"]) for row in state_rows], default=0)
    turn_metrics = []
    for turn in range(max_turn + 1):
        call_row = calls_by_turn_by_key.get(turn, {})
        event_row = events_by_turn_by_key.get(turn, {})
        row = {
            "turn_index": turn,
            "calls": call_row.get("calls", 0),
            "cost": round(float(call_row.get("cost") or 0), 6),
            "input_tokens": int(call_row.get("input_tokens") or 0),
            "output_tokens": int(call_row.get("output_tokens") or 0),
            "reasoning_tokens": int(call_row.get("reasoning_tokens") or 0),
            "total_tokens": int(call_row.get("total_tokens") or 0),
            "latency_ms": int(call_row.get("latency_ms") or 0),
            "invalid_attempts": int(call_row.get("invalid_attempts") or 0),
            "total_events": int(event_row.get("total_events") or 0),
            "rent_events": int(event_row.get("RENT_PAID") or 0),
            "trade_events": int(event_row.get("trade_events") or 0),
            "auction_events": int(event_row.get("auction_events") or 0),
            "building_events": int(event_row.get("building_events") or 0),
            "cash_events": int(event_row.get("cash_events") or 0),
        }
        row.update(state_wide.get(turn, {}))
        turn_metrics.append(row)

    batch_rows = []
    for size in [10, 25]:
        for batch_start in range(0, max_turn + 1, size):
            batch_end = min(batch_start + size - 1, max_turn)
            batch_turns = [row for row in turn_metrics if batch_start <= row["turn_index"] <= batch_end]
            batch_rows.append(
                {
                    "batch_size": size,
                    "turn_start": batch_start,
                    "turn_end": batch_end,
                    "calls": sum(int(row["calls"]) for row in batch_turns),
                    "events": sum(int(row["total_events"]) for row in batch_turns),
                    "cost": round(sum(float(row["cost"]) for row in batch_turns), 6),
                    "input_tokens": sum(int(row["input_tokens"]) for row in batch_turns),
                    "output_tokens": sum(int(row["output_tokens"]) for row in batch_turns),
                    "reasoning_tokens": sum(int(row["reasoning_tokens"]) for row in batch_turns),
                    "latency_ms": sum(int(row["latency_ms"]) for row in batch_turns),
                    "rent_events": sum(int(row["rent_events"]) for row in batch_turns),
                    "trade_events": sum(int(row["trade_events"]) for row in batch_turns),
                    "auction_events": sum(int(row["auction_events"]) for row in batch_turns),
                    "building_events": sum(int(row["building_events"]) for row in batch_turns),
                }
            )

    rent_flow = []
    for player in PLAYERS:
        collected = sum(row["amount"] for row in event_tables["rent_events"] if row["to_player_id"] == player)
        paid = sum(row["amount"] for row in event_tables["rent_events"] if row["from_player_id"] == player)
        rent_flow.append({"player_id": player, "rent_collected": collected, "rent_paid": paid, "net_rent": collected - paid})

    cash_by_reason = group_sum(event_tables["cash_events"], ["player_id", "reason"], ["delta"], "events")
    rent_by_space = group_sum(event_tables["rent_events"], ["space_name", "space_group", "to_player_id"], ["amount"], "rent_events")
    rent_by_space.sort(key=lambda row: row["amount"], reverse=True)

    trade_summary = group_sum(event_tables["trade_events"], ["initiator_player_id", "counterparty_player_id", "event_type"], [], "events")
    auction_summary = [row for row in event_tables["auction_events"] if row["event_type"] == "AUCTION_ENDED"]
    auction_summary.sort(key=lambda row: int(row.get("winning_bid") or 0), reverse=True)

    top_cost = sorted(calls, key=lambda r: float(r["cost"]), reverse=True)[:30]
    top_latency = sorted(calls, key=lambda r: int(r["latency_ms"]), reverse=True)[:30]
    top_reasoning = sorted(calls, key=lambda r: int(r["reasoning_tokens"]), reverse=True)[:30]
    top_output = sorted(calls, key=lambda r: int(r["output_tokens"]), reverse=True)[:30]
    reliability = [row for row in calls if row["invalid_attempts"] or row["retry_used"] or row["fallback_used"] or row["missing_usage_attempts"]]

    return {
        "model_usage": by_model,
        "decision_type_by_model": decision_type,
        "action_mix": action_mix,
        "turn_metrics": turn_metrics,
        "batch_summary": batch_rows,
        "rent_flow_by_player": rent_flow,
        "cash_by_reason_player": cash_by_reason,
        "rent_by_space": rent_by_space,
        "trade_summary": trade_summary,
        "auction_summary": auction_summary,
        "top_30_costliest_calls": top_cost,
        "top_30_slowest_calls": top_latency,
        "top_30_reasoning_calls": top_reasoning,
        "top_30_output_calls": top_output,
        "reliability_issues": reliability,
    }


def save_plot(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_player_lines(df: pd.DataFrame, column: str, title: str, ylabel: str, path: Path) -> None:
    plt.figure(figsize=(13, 6.5))
    for player in PLAYERS:
        sub = df[df["player_id"] == player]
        if not sub.empty:
            plt.plot(sub["turn_index"], sub[column], label=player, color=COLORS[player], linewidth=2)
    plt.title(title)
    plt.xlabel("Turn index")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.25)
    plt.legend(fontsize=8)
    save_plot(path)


def make_plots(state_rows: list[dict], calls: list[dict], tables: dict[str, list[dict]], event_tables: dict[str, list[dict]]) -> None:
    state_df = pd.DataFrame(state_rows)
    calls_df = pd.DataFrame(calls)
    turn_df = pd.DataFrame(tables["turn_metrics"])
    model_df = pd.DataFrame(tables["model_usage"])
    decision_df = pd.DataFrame(tables["decision_type_by_model"])
    rent_flow_df = pd.DataFrame(tables["rent_flow_by_player"])
    batch_df = pd.DataFrame(tables["batch_summary"])

    if not state_df.empty:
        plot_player_lines(state_df, "net_worth", "Net Worth by Turn", "Net worth ($)", PLOT_DIR / "net_worth_by_turn.png")
        plot_player_lines(state_df, "cash", "Cash by Turn", "Cash ($)", PLOT_DIR / "cash_by_turn.png")
        plot_player_lines(state_df, "property_value", "Property Face Value by Turn", "Property face value ($)", PLOT_DIR / "property_value_by_turn.png")
        plot_player_lines(state_df, "building_value", "Building Value by Turn", "Building value ($)", PLOT_DIR / "building_value_by_turn.png")
        plot_player_lines(state_df, "mortgage_liability", "Mortgage Liability by Turn", "Mortgage liability ($)", PLOT_DIR / "mortgage_liability_by_turn.png")
        plot_player_lines(state_df, "property_count", "Property Count by Turn", "Properties", PLOT_DIR / "property_count_by_turn.png")
        plot_player_lines(state_df, "houses", "Houses Controlled by Turn", "Houses", PLOT_DIR / "houses_by_turn.png")
        plot_player_lines(state_df, "hotels", "Hotels Controlled by Turn", "Hotels", PLOT_DIR / "hotels_by_turn.png")

        supply = state_df.groupby("turn_index", as_index=False)[["houses", "hotels"]].sum()
        supply["bank_houses"] = 32 - supply["houses"]
        supply["bank_hotels"] = 12 - supply["hotels"]
        plt.figure(figsize=(13, 6))
        plt.plot(supply["turn_index"], supply["bank_houses"], label="Bank houses", color="#dc2626", linewidth=2)
        plt.plot(supply["turn_index"], supply["bank_hotels"], label="Bank hotels", color="#2563eb", linewidth=2)
        plt.title("Bank Building Supply by Turn")
        plt.xlabel("Turn index")
        plt.ylabel("Pieces remaining")
        plt.grid(True, alpha=0.25)
        plt.legend()
        save_plot(PLOT_DIR / "bank_building_supply_by_turn.png")

    if not calls_df.empty:
        calls_df["cumulative_cost"] = calls_df["cost"].cumsum()
        plt.figure(figsize=(13, 6))
        plt.plot(calls_df["call_index"], calls_df["cumulative_cost"], color="#111827", linewidth=2)
        plt.title("Cumulative Cost by LLM Call")
        plt.xlabel("LLM call index")
        plt.ylabel("Cumulative cost ($)")
        plt.grid(True, alpha=0.25)
        save_plot(PLOT_DIR / "cumulative_cost_by_call.png")

        plt.figure(figsize=(13, 6))
        for player in PLAYERS:
            sub = calls_df[calls_df["player_id"] == player].copy()
            sub["player_cumulative_cost"] = sub["cost"].cumsum()
            plt.plot(sub["call_index"], sub["player_cumulative_cost"], label=player, color=COLORS[player], linewidth=2)
        plt.title("Cumulative Cost by Model")
        plt.xlabel("LLM call index")
        plt.ylabel("Cumulative model cost ($)")
        plt.grid(True, alpha=0.25)
        plt.legend(fontsize=8)
        save_plot(PLOT_DIR / "cumulative_cost_by_model.png")

        for metric, ylabel, name in [
            ("cost", "Cost per call ($)", "cost_per_call.png"),
            ("latency_ms", "Latency (ms)", "latency_per_call.png"),
            ("input_tokens", "Input tokens", "input_tokens_per_call.png"),
            ("output_tokens", "Output tokens", "output_tokens_per_call.png"),
            ("reasoning_tokens", "Reasoning tokens", "reasoning_tokens_per_call.png"),
        ]:
            plt.figure(figsize=(13, 6))
            for player in PLAYERS:
                sub = calls_df[calls_df["player_id"] == player]
                plt.scatter(sub["call_index"], sub[metric], label=player, color=COLORS[player], s=15, alpha=0.72)
            plt.title(ylabel + " by LLM Call")
            plt.xlabel("LLM call index")
            plt.ylabel(ylabel)
            plt.grid(True, alpha=0.25)
            plt.legend(fontsize=8)
            save_plot(PLOT_DIR / name)

        fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
        for ax, metric, ylabel in [
            (axes[0], "input_tokens", "Input tokens"),
            (axes[1], "output_tokens", "Output tokens"),
            (axes[2], "reasoning_tokens", "Reasoning tokens"),
        ]:
            for player in PLAYERS:
                sub = calls_df[calls_df["player_id"] == player]
                ax.scatter(sub["call_index"], sub[metric], label=player, color=COLORS[player], s=13, alpha=0.7)
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.25)
        axes[0].set_title("Token Usage per Call, Split by Token Type")
        axes[2].set_xlabel("LLM call index")
        axes[0].legend(fontsize=8)
        save_plot(PLOT_DIR / "tokens_per_call_subplots.png")

    if not turn_df.empty:
        for metric, ylabel, name in [
            ("cost", "Cost per turn ($)", "cost_by_turn.png"),
            ("total_tokens", "Total tokens per turn", "tokens_by_turn.png"),
            ("reasoning_tokens", "Reasoning tokens per turn", "reasoning_tokens_by_turn.png"),
            ("calls", "LLM calls per turn", "calls_by_turn.png"),
            ("total_events", "Events per turn", "events_by_turn.png"),
        ]:
            plt.figure(figsize=(13, 6))
            plt.plot(turn_df["turn_index"], turn_df[metric], color="#111827", linewidth=1.8)
            plt.title(ylabel)
            plt.xlabel("Turn index")
            plt.ylabel(ylabel)
            plt.grid(True, alpha=0.25)
            save_plot(PLOT_DIR / name)

        plt.figure(figsize=(13, 6))
        for metric, color in [
            ("trade_events", "#2563eb"),
            ("auction_events", "#d97706"),
            ("building_events", "#16a34a"),
            ("rent_events", "#dc2626"),
        ]:
            plt.plot(turn_df["turn_index"], turn_df[metric], label=metric, color=color, linewidth=1.8)
        plt.title("Strategic Event Counts by Turn")
        plt.xlabel("Turn index")
        plt.ylabel("Events")
        plt.grid(True, alpha=0.25)
        plt.legend()
        save_plot(PLOT_DIR / "strategic_events_by_turn.png")

    if not model_df.empty:
        order = [p for p in PLAYERS if p in set(model_df["player_id"])]
        model_df = model_df.set_index("player_id").loc[order].reset_index()
        for metric, ylabel, name in [
            ("cost", "Total cost ($)", "cost_by_model.png"),
            ("calls", "LLM calls", "calls_by_model.png"),
            ("latency_ms", "Total latency (ms)", "latency_by_model.png"),
        ]:
            plt.figure(figsize=(11, 6))
            plt.bar(model_df["player_id"], model_df[metric], color=[COLORS[p] for p in model_df["player_id"]])
            plt.title(ylabel + " by Model")
            plt.xlabel("Model")
            plt.ylabel(ylabel)
            plt.xticks(rotation=20, ha="right")
            plt.grid(True, axis="y", alpha=0.25)
            save_plot(PLOT_DIR / name)

        plt.figure(figsize=(11, 6))
        bottom = [0] * len(model_df)
        for metric, label, color in [
            ("input_tokens", "Input", "#94a3b8"),
            ("output_tokens", "Output", "#0f766e"),
            ("reasoning_tokens", "Reasoning", "#b45309"),
        ]:
            vals = model_df[metric].tolist()
            plt.bar(model_df["player_id"], vals, bottom=bottom, label=label, color=color)
            bottom = [a + b for a, b in zip(bottom, vals)]
        plt.title("Token Mix by Model")
        plt.xlabel("Model")
        plt.ylabel("Tokens")
        plt.xticks(rotation=20, ha="right")
        plt.grid(True, axis="y", alpha=0.25)
        plt.legend()
        save_plot(PLOT_DIR / "tokens_by_model_stacked.png")

    if not decision_df.empty:
        pivot = decision_df.pivot_table(index="player_id", columns="decision_type", values="calls", aggfunc="sum", fill_value=0)
        pivot = pivot.reindex([p for p in PLAYERS if p in pivot.index])
        plt.figure(figsize=(12, 7))
        bottom = [0] * len(pivot)
        colors = ["#64748b", "#2563eb", "#16a34a", "#d97706", "#dc2626", "#7c3aed", "#0891b2"]
        for idx, col in enumerate(pivot.columns):
            vals = pivot[col].tolist()
            plt.bar(pivot.index, vals, bottom=bottom, label=col, color=colors[idx % len(colors)])
            bottom = [a + b for a, b in zip(bottom, vals)]
        plt.title("Decision Type Mix by Model")
        plt.xlabel("Model")
        plt.ylabel("Calls")
        plt.xticks(rotation=20, ha="right")
        plt.legend(fontsize=8)
        plt.grid(True, axis="y", alpha=0.25)
        save_plot(PLOT_DIR / "decision_type_mix_by_model.png")

    if not rent_flow_df.empty:
        plt.figure(figsize=(11, 6))
        x = range(len(rent_flow_df))
        plt.bar(x, rent_flow_df["rent_collected"], width=0.35, label="Collected", color="#16a34a")
        plt.bar([i + 0.35 for i in x], rent_flow_df["rent_paid"], width=0.35, label="Paid", color="#dc2626")
        plt.xticks([i + 0.175 for i in x], rent_flow_df["player_id"], rotation=20, ha="right")
        plt.title("Rent Collected vs Paid by Player")
        plt.xlabel("Player")
        plt.ylabel("Rent ($)")
        plt.legend()
        plt.grid(True, axis="y", alpha=0.25)
        save_plot(PLOT_DIR / "rent_collected_paid_by_player.png")

    if not batch_df.empty:
        for size in [10, 25]:
            sub = batch_df[batch_df["batch_size"] == size]
            labels = [f"{int(r.turn_start)}-{int(r.turn_end)}" for r in sub.itertuples()]
            for metric, ylabel, name in [
                ("cost", "Cost ($)", f"cost_by_{size}_turn_batch.png"),
                ("calls", "LLM calls", f"calls_by_{size}_turn_batch.png"),
                ("reasoning_tokens", "Reasoning tokens", f"reasoning_tokens_by_{size}_turn_batch.png"),
            ]:
                plt.figure(figsize=(13, 6))
                plt.bar(labels, sub[metric], color="#2563eb")
                plt.title(f"{ylabel} by {size}-Turn Batch")
                plt.xlabel("Turn batch")
                plt.ylabel(ylabel)
                plt.xticks(rotation=35, ha="right")
                plt.grid(True, axis="y", alpha=0.25)
                save_plot(PLOT_DIR / name)


def write_report(summary: dict, tables: dict[str, list[dict]], replay: dict, generated_summary: dict) -> None:
    final_players = tables["final_players"]
    model_usage = tables["model_usage"]
    top_cost = tables["top_30_costliest_calls"][:10]
    rent_flow = tables["rent_flow_by_player"]
    bankruptcies = summary.get("bankruptcies", [])

    lines = [
        f"# Deep Run Analysis: {RUN_DIR.name}",
        "",
        "## Integrity",
        f"- Raw winner: `{summary['winner_player_id']}`",
        f"- End reason: `{summary['end_reason']}`",
        f"- Turn count: `{summary['turn_count']}`",
        f"- Replay status: `{replay.get('status')}`",
        f"- Replay first mismatch: `{replay.get('first_mismatch_index')}`",
        f"- Derived summary winner bankrupt flag: `{generated_summary.get('players', {}).get(summary['winner_player_id'], {}).get('bankrupt')}`",
        f"- Corrected final snapshot winner bankrupt flag: `{next((p['bankrupt'] for p in final_players if p['player_id'] == summary['winner_player_id']), None)}`",
        "",
        "## Cost And Tokens",
        f"- Total cost: `${summary['total_cost']:.6f}`",
        f"- Tokens: `{summary['input_tokens']:,}` input, `{summary['output_tokens']:,}` output, `{summary['reasoning_tokens']:,}` reasoning, `{summary['total_tokens']:,}` total",
        f"- Calls/retries/fallbacks/invalid attempts: `{summary['calls']}` / `{summary['retries']}` / `{summary['fallbacks']}` / `{summary['invalid_attempts']}`",
        f"- Median latency: `{summary['median_latency_ms']:,} ms`; max latency: `{summary['max_latency_ms']:,} ms`",
        "",
        "## Final Players",
    ]
    for player in final_players:
        lines.append(
            f"- {player['player_id']}: cash `${player['cash']:,}`, net `${player['net_worth']:,}`, property value `${player['property_value']:,}`, building value `${player['building_value']:,}`, mortgage liability `${player['mortgage_liability']:,}`, bankrupt `{player['bankrupt']}`"
        )
    lines += ["", "## Model Usage"]
    for row in model_usage:
        lines.append(
            f"- {row['player_id']}: `{int(row['calls'])}` calls, `${float(row['cost']):.6f}`, `{int(row['input_tokens']):,}` in, `{int(row['output_tokens']):,}` out, `{int(row['reasoning_tokens']):,}` reasoning"
        )
    lines += ["", "## Rent Flow"]
    for row in rent_flow:
        lines.append(
            f"- {row['player_id']}: collected `${int(row['rent_collected']):,}`, paid `${int(row['rent_paid']):,}`, net `${int(row['net_rent']):,}`"
        )
    lines += ["", "## Bankruptcies"]
    for row in bankruptcies:
        lines.append(f"- Turn `{row['turn_index']}`: `{row['player_id']}`")
    lines += ["", "## Top Costliest Calls"]
    for row in top_cost:
        lines.append(
            f"- call `{row['call_index']}`, turn `{row['turn_index']}`, `{row['player_id']}`, `{row['decision_type']}` -> `{row['action']}`: `${float(row['cost']):.6f}`, `{int(row['total_tokens']):,}` tokens, `{int(row['latency_ms']) / 1000:.1f}s`"
        )
    lines += [
        "",
        "## External Framing Notes",
        "- AgentBench motivates multi-turn interactive evaluation and highlights long-term reasoning, decision-making, and instruction following as common agent failure modes: https://arxiv.org/abs/2308.03688",
        "- DSGBench argues for fine-grained decision tracking and strategy turning-point analysis in strategic-game benchmarks: https://arxiv.org/abs/2503.06047",
        "- ReliabilityBench argues that single-run success rates miss reliability properties; retries, fallbacks, perturbations, and fault tolerance should be tracked separately: https://arxiv.org/abs/2601.06112",
        "- Hasbro Monopoly rules ground the housing-shortage and bankruptcy interpretation: 32 houses, 12 hotels, buildings sold back at half price, and last remaining player wins: https://www.hasbro.com/common/instruct/40753.pdf",
        "",
        "## Generated Artifacts",
        "- `analysis/tables/*.csv`",
        "- `analysis/plots/*.png`",
        "- `analysis/deep_analysis_summary.json`",
        "- `analysis/deep_analysis_report.md`",
    ]
    (ANALYSIS_DIR / "deep_analysis_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ANALYSIS_DIR.mkdir(exist_ok=True)
    TABLE_DIR.mkdir(exist_ok=True)
    PLOT_DIR.mkdir(exist_ok=True)

    events = read_jsonl(RUN_DIR / "events.jsonl")
    actions = read_jsonl(RUN_DIR / "actions.jsonl")
    decisions = read_jsonl(RUN_DIR / "decisions.jsonl")
    generated_summary = read_json(RUN_DIR / "summary.json")
    replay = read_json(RUN_DIR / "replay_report.json")

    state_rows, final_snapshot, _snapshots = latest_snapshots_by_turn()
    board_by_index = build_board_map(final_snapshot or {})
    event_tables = event_derived_tables(events, board_by_index)
    calls, attempts, pending = parse_decisions(decisions)
    tables = aggregate_tables(calls, event_tables, state_rows)

    final_turn = max((row["turn_index"] for row in state_rows), default=0)
    final_players = [row for row in state_rows if row["turn_index"] == final_turn]
    winner_id = (events[-1].get("payload") or {}).get("winner_player_id") if events and events[-1].get("type") == "GAME_ENDED" else generated_summary.get("winner_player_id")
    for row in final_players:
        row["winner"] = row["player_id"] == winner_id
    final_players.sort(key=lambda row: (not row["winner"], row["bankrupt"], -row["net_worth"]))
    tables["final_players"] = final_players

    for name, rows in event_tables.items():
        write_csv(TABLE_DIR / f"{name}.csv", rows)
    for name, rows in tables.items():
        write_csv(TABLE_DIR / f"{name}.csv", rows)
    write_csv(TABLE_DIR / "llm_calls.csv", calls)
    write_csv(TABLE_DIR / "llm_attempts.csv", attempts)
    write_csv(TABLE_DIR / "state_by_turn_player.csv", state_rows)
    write_csv(TABLE_DIR / "pending_decisions.csv", pending)

    total_cost = sum(float(row["cost"]) for row in calls)
    latency_values = [int(row["latency_ms"]) for row in calls]
    summary = {
        "run_id": RUN_DIR.name,
        "winner_player_id": winner_id,
        "end_reason": (events[-1].get("payload") or {}).get("reason") if events and events[-1].get("type") == "GAME_ENDED" else generated_summary.get("reason"),
        "turn_count": final_turn,
        "events": len(events),
        "actions": len(actions),
        "decision_log_entries": len(decisions),
        "calls": len(calls),
        "attempts": len(attempts),
        "pending_decisions": len(pending),
        "game_ended": bool(events and events[-1].get("type") == "GAME_ENDED"),
        "replay_status": replay.get("status"),
        "replay_first_mismatch_index": replay.get("first_mismatch_index"),
        "summary_winner_bankrupt_flag": generated_summary.get("players", {}).get(winner_id, {}).get("bankrupt"),
        "corrected_winner_bankrupt_flag": next((row["bankrupt"] for row in final_players if row["player_id"] == winner_id), None),
        "total_cost": round(total_cost, 8),
        "input_tokens": sum(int(row["input_tokens"]) for row in calls),
        "output_tokens": sum(int(row["output_tokens"]) for row in calls),
        "reasoning_tokens": sum(int(row["reasoning_tokens"]) for row in calls),
        "total_tokens": sum(int(row["total_tokens"]) for row in calls),
        "cached_tokens": sum(int(row["cached_tokens"]) for row in calls),
        "missing_usage_calls": sum(int(bool(row["missing_usage_attempts"])) for row in calls),
        "invalid_attempts": sum(int(row["invalid_attempts"]) for row in calls),
        "retries": sum(int(bool(row["retry_used"])) for row in calls),
        "fallbacks": sum(int(bool(row["fallback_used"])) for row in calls),
        "avg_latency_ms": round(sum(latency_values) / len(latency_values), 2) if latency_values else 0,
        "median_latency_ms": int(median(latency_values)) if latency_values else 0,
        "max_latency_ms": max(latency_values, default=0),
        "final_players": final_players,
        "model_usage": tables["model_usage"],
        "bankruptcies": event_tables["bankruptcies"],
        "event_counts": event_tables["event_counts"],
        "generated_plot_count": None,
        "generated_table_count": None,
    }

    make_plots(state_rows, calls, tables, event_tables)
    summary["generated_plot_count"] = len(list(PLOT_DIR.glob("*.png")))
    summary["generated_table_count"] = len(list(TABLE_DIR.glob("*.csv")))
    write_json(ANALYSIS_DIR / "deep_analysis_summary.json", summary)
    write_report(summary, tables, replay, generated_summary)


if __name__ == "__main__":
    main()
