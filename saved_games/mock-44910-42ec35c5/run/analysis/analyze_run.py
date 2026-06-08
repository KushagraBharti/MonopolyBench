import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OUT = ROOT / "analysis"

PLAYER_ORDER = [
    "OpenAI GPT 5.4 Mini",
    "Claude Haiku 4.5",
    "Gemini 3 Flash Preview",
    "Grok 4.3",
]
COLORS = {
    "OpenAI GPT 5.4 Mini": "#6b7280",
    "Claude Haiku 4.5": "#f59e0b",
    "Gemini 3 Flash Preview": "#db2777",
    "Grok 4.3": "#111827",
}
SHORT = {
    "OpenAI GPT 5.4 Mini": "OpenAI",
    "Claude Haiku 4.5": "Claude",
    "Gemini 3 Flash Preview": "Gemini",
    "Grok 4.3": "Grok",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_csv(path, rows, fieldnames=None):
    rows = list(rows)
    if fieldnames is None:
        keys = []
        seen = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.add(key)
                    keys.append(key)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def money(x, _pos=None):
    return f"${x:,.0f}"


def dollars3(x, _pos=None):
    return f"${x:.3f}"


def top_n(rows, key, n=20):
    return sorted(rows, key=lambda row: row.get(key) or 0, reverse=True)[:n]


summary = read_json(ROOT / "summary.json")
cost_report = read_json(ROOT / "cost_report.json")
replay_report = read_json(ROOT / "replay_report.json")
players_cfg = read_json(ROOT / "players.json")
board_data = read_json(REPO / "contracts" / "data" / "board.json")
house_cost_by_group = board_data.get("house_cost_by_group", {})

usage = read_jsonl(ROOT / "usage_attempts.jsonl")
decisions_all = read_jsonl(ROOT / "decisions.jsonl")
decisions = [row for row in decisions_all if row.get("phase") == "decision_resolved"]
events = read_jsonl(ROOT / "events.jsonl")
actions = read_jsonl(ROOT / "actions.jsonl")
trace_findings = read_jsonl(ROOT / "trace_findings.jsonl")
failure_findings = read_jsonl(ROOT / "failure_findings.jsonl")
max_turn = summary["turn_count"]

per_call = []
for index, row in enumerate(usage):
    item = {
        "call_index": index,
        "turn_index": row.get("turn_index"),
        "decision_id": row.get("decision_id"),
        "attempt_index": row.get("attempt_index"),
        "decision_type": row.get("decision_type"),
        "player_id": row.get("player_id"),
        "model_id": row.get("openrouter_model_id"),
        "finish_reason": row.get("finish_reason"),
        "input_tokens": row.get("input_tokens") or row.get("prompt_tokens") or 0,
        "output_tokens": row.get("output_tokens") or row.get("completion_tokens") or 0,
        "reasoning_tokens": row.get("reasoning_tokens") or 0,
        "total_tokens": row.get("total_tokens") or 0,
        "cached_tokens": row.get("cached_tokens") or 0,
        "cost": row.get("cost") or 0.0,
        "latency_ms": row.get("latency_ms") or 0,
        "retry_used": bool(row.get("retry_used")),
        "fallback_used": bool(row.get("fallback_used")),
        "error_type": row.get("error_type") or "",
        "openrouter_status_code": row.get("openrouter_status_code"),
    }
    item["latency_s"] = item["latency_ms"] / 1000.0
    per_call.append(item)
write_csv(OUT / "per_call_usage.csv", per_call)

invalid_attempts = []
per_decision = []
for decision in decisions:
    attempts = decision.get("attempts") or []
    for attempt_index, attempt in enumerate(attempts):
        if (
            attempt.get("outcome") != "valid"
            or attempt.get("validation_errors")
            or attempt.get("error_type")
        ):
            invalid_attempts.append(
                {
                    "turn_index": decision.get("turn_index"),
                    "decision_id": decision.get("decision_id"),
                    "decision_type": decision.get("decision_type"),
                    "player_id": decision.get("player_id"),
                    "model_id": decision.get("openrouter_model_id"),
                    "attempt_index": attempt_index,
                    "outcome": attempt.get("outcome"),
                    "reason": attempt.get("reason") or "",
                    "error_type": attempt.get("error_type") or "",
                    "error_message": (attempt.get("error_message") or "")[:500],
                    "validation_errors": json.dumps(
                        attempt.get("validation_errors") or [], ensure_ascii=False
                    ),
                    "latency_ms": attempt.get("latency_ms") or 0,
                }
            )
    action = decision.get("final_action") or {}
    per_decision.append(
        {
            "turn_index": decision.get("turn_index"),
            "decision_id": decision.get("decision_id"),
            "decision_type": decision.get("decision_type"),
            "player_id": decision.get("player_id"),
            "model_id": decision.get("openrouter_model_id"),
            "attempt_count": len(attempts),
            "retry_used": bool(decision.get("retry_used")),
            "fallback_used": bool(decision.get("fallback_used")),
            "final_action": action.get("action") or "",
            "latency_ms": decision.get("latency_ms") or 0,
            "emitted_event_count": len(decision.get("emitted_event_ids") or []),
        }
    )
write_csv(OUT / "per_decision.csv", per_decision)
write_csv(OUT / "invalid_attempts.csv", invalid_attempts)

per_action = []
for action_row in actions:
    action = action_row.get("action") or {}
    per_action.append(
        {
            "turn_index": action_row.get("turn_index"),
            "decision_id": action_row.get("decision_id"),
            "actor_player_id": action_row.get("actor_player_id"),
            "decision_type": action_row.get("decision_type"),
            "action": action.get("action") or "",
            "args": json.dumps(action.get("args") or {}, ensure_ascii=False),
            "public_message": action.get("public_message") or "",
            "private_thought": action.get("private_thought") or "",
        }
    )
write_csv(OUT / "actions.csv", per_action)

snapshots = []
for path in sorted((ROOT / "state").glob("turn_[0-9][0-9][0-9][0-9].json")):
    snapshots.append((read_json(path).get("turn_index"), path, read_json(path)))

per_turn_financial = []
turn_bank = []
for turn, _path, snapshot in snapshots:
    players = {player["player_id"]: player for player in snapshot.get("players", [])}
    assets = {
        player_id: {
            "property_value": 0,
            "building_value": 0,
            "mortgage_liability": 0,
            "property_count": 0,
            "houses": 0,
            "hotels": 0,
        }
        for player_id in PLAYER_ORDER
    }
    for space in snapshot.get("board", []):
        owner = space.get("owner_id")
        kind = space.get("kind")
        group = space.get("group")
        price = space.get("price") or 0
        if owner in assets and kind in ("PROPERTY", "RAILROAD", "UTILITY"):
            assets[owner]["property_value"] += price
            assets[owner]["property_count"] += 1
            if space.get("mortgaged"):
                assets[owner]["mortgage_liability"] += price / 2
        if owner in assets and kind == "PROPERTY":
            house_cost = house_cost_by_group.get(group, 0)
            houses = int(space.get("houses") or 0)
            hotel = bool(space.get("hotel"))
            assets[owner]["houses"] += houses
            assets[owner]["hotels"] += 1 if hotel else 0
            assets[owner]["building_value"] += (houses + (5 if hotel else 0)) * house_cost
    for player_id in PLAYER_ORDER:
        player = players.get(player_id, {})
        asset = assets[player_id]
        cash = player.get("cash") or 0
        net_worth = (
            cash
            + asset["property_value"]
            + asset["building_value"]
            - asset["mortgage_liability"]
        )
        per_turn_financial.append(
            {
                "turn_index": turn,
                "player_id": player_id,
                "cash": cash,
                "net_worth_estimate": net_worth,
                "property_value_estimate": asset["property_value"],
                "building_value_estimate": asset["building_value"],
                "mortgage_liability_estimate": asset["mortgage_liability"],
                "property_count": asset["property_count"],
                "houses": asset["houses"],
                "hotels": asset["hotels"],
                "position": player.get("position"),
                "in_jail": bool(player.get("in_jail")),
                "bankrupt": bool(player.get("bankrupt")),
                "bankrupt_to": player.get("bankrupt_to") or "",
            }
        )
    bank = snapshot.get("bank", {})
    turn_bank.append(
        {
            "turn_index": turn,
            "houses_remaining": bank.get("houses_remaining"),
            "hotels_remaining": bank.get("hotels_remaining"),
        }
    )
write_csv(OUT / "per_turn_financials.csv", per_turn_financial)
write_csv(OUT / "bank_inventory_by_turn.csv", turn_bank)

usage_by_turn = defaultdict(lambda: defaultdict(float))
usage_by_turn_player = defaultdict(lambda: defaultdict(float))
for row in per_call:
    turn = row["turn_index"]
    player_id = row["player_id"]
    for key in ["input_tokens", "output_tokens", "reasoning_tokens", "total_tokens", "cost", "latency_ms"]:
        usage_by_turn[turn][key] += row[key]
        usage_by_turn_player[(turn, player_id)][key] += row[key]
    usage_by_turn[turn]["calls"] += 1
    usage_by_turn_player[(turn, player_id)]["calls"] += 1
    usage_by_turn[turn]["retry_calls"] += int(row["retry_used"])
    usage_by_turn_player[(turn, player_id)]["retry_calls"] += int(row["retry_used"])

per_turn_usage = [
    {
        "turn_index": turn,
        **{
            key: values.get(key, 0)
            for key in [
                "calls",
                "input_tokens",
                "output_tokens",
                "reasoning_tokens",
                "total_tokens",
                "cost",
                "latency_ms",
                "retry_calls",
            ]
        },
    }
    for turn, values in sorted(usage_by_turn.items())
]
write_csv(OUT / "per_turn_usage_total.csv", per_turn_usage)
write_csv(
    OUT / "per_turn_usage_by_player.csv",
    [
        {
            "turn_index": turn,
            "player_id": player_id,
            **{
                key: values.get(key, 0)
                for key in [
                    "calls",
                    "input_tokens",
                    "output_tokens",
                    "reasoning_tokens",
                    "total_tokens",
                    "cost",
                    "latency_ms",
                    "retry_calls",
                ]
            },
        }
        for (turn, player_id), values in sorted(usage_by_turn_player.items())
    ],
)

event_counts = Counter(event.get("type") for event in events)
write_csv(OUT / "event_counts.csv", [{"event_type": key, "count": value} for key, value in event_counts.most_common()])
write_csv(
    OUT / "decision_type_counts.csv",
    [{"decision_type": key, "count": value} for key, value in Counter(row["decision_type"] for row in per_decision).most_common()],
)
write_csv(
    OUT / "action_counts.csv",
    [{"action": key, "count": value} for key, value in Counter(row["action"] for row in per_action).most_common()],
)

rent_payments = []
cash_changes = []
bankruptcy_cash_events = []
trade_events = []
property_events = []
building_events = []
for event in events:
    event_type = event.get("type")
    payload = event.get("payload") or {}
    base = {
        "seq": event.get("seq"),
        "turn_index": event.get("turn_index"),
        "event_id": event.get("event_id"),
        "event_type": event_type,
        "actor_player_id": (event.get("actor") or {}).get("player_id") or "",
    }
    if event_type == "RENT_PAID":
        rent_payments.append(
            {
                **base,
                "from_player_id": payload.get("from_player_id"),
                "to_player_id": payload.get("to_player_id"),
                "amount": payload.get("amount") or 0,
                "space_index": payload.get("space_index"),
            }
        )
    if event_type == "CASH_CHANGED":
        row = {
            **base,
            "player_id": payload.get("player_id"),
            "delta": payload.get("delta") or 0,
            "reason": payload.get("reason") or "",
        }
        cash_changes.append(row)
        if str(payload.get("reason") or "").startswith("BANKRUPTCY"):
            bankruptcy_cash_events.append(row)
    if event_type and "TRADE" in event_type:
        trade_events.append({**base, "payload": json.dumps(payload, ensure_ascii=False)})
    if event_type and (event_type.startswith("PROPERTY_") or event_type in ("ASSET_TRANSFERRED", "PROPERTY_TRANSFERRED")):
        property_events.append({**base, "payload": json.dumps(payload, ensure_ascii=False)})
    if event_type and any(marker in event_type for marker in ("HOUSE_", "HOTEL_", "BUILDING")):
        building_events.append({**base, "payload": json.dumps(payload, ensure_ascii=False)})

write_csv(OUT / "rent_payments.csv", rent_payments)
write_csv(OUT / "rent_by_player.csv", [])
write_csv(OUT / "cash_changes.csv", cash_changes)
write_csv(OUT / "bankruptcy_cash_events.csv", bankruptcy_cash_events)
write_csv(OUT / "trade_events.csv", trade_events)
write_csv(OUT / "property_events.csv", property_events)
write_csv(OUT / "building_events.csv", building_events)


def finding_rows(rows):
    return [
        {
            "finding_id": row.get("finding_id"),
            "finding_type": row.get("finding_type"),
            "severity": row.get("severity"),
            "confidence": row.get("confidence"),
            "status": row.get("status"),
            "turn_index": row.get("turn_index"),
            "decision_id": row.get("decision_id") or "",
            "player_id": row.get("player_id") or "",
            "model_id": row.get("model_id") or "",
            "summary": row.get("summary") or "",
            "human_review_required": bool(row.get("human_review_required")),
            "tags": ",".join(row.get("tags") or []),
        }
        for row in rows
    ]


write_csv(OUT / "trace_findings.csv", finding_rows(trace_findings))
write_csv(OUT / "failure_findings.csv", finding_rows(failure_findings))
write_csv(OUT / "top_expensive_calls.csv", top_n(per_call, "cost"))
write_csv(OUT / "top_latency_calls.csv", top_n(per_call, "latency_ms"))
write_csv(OUT / "top_output_token_calls.csv", top_n(per_call, "output_tokens"))
write_csv(OUT / "top_reasoning_token_calls.csv", top_n(per_call, "reasoning_tokens"))

model_rows = []
for player_id in PLAYER_ORDER:
    model_id = next(
        (player["openrouter_model_id"] for player in players_cfg["players"] if player["player_id"] == player_id),
        "",
    )
    values = cost_report["by_player"].get(player_id, {})
    decision_count = values.get("decision_count") or 0
    final_row = next(
        row
        for row in per_turn_financial
        if row["turn_index"] == summary["turn_count"] and row["player_id"] == player_id
    )
    model_rows.append(
        {
            "player_id": player_id,
            "model_id": model_id,
            "decisions": decision_count,
            "attempts": sum(1 for row in per_call if row["player_id"] == player_id),
            "input_tokens": values.get("input_tokens", 0),
            "output_tokens": values.get("output_tokens", 0),
            "reasoning_tokens": values.get("reasoning_tokens", 0),
            "total_tokens": values.get("total_tokens", 0),
            "cached_tokens": values.get("cached_tokens", 0),
            "cost": values.get("cost", 0.0),
            "latency_ms": values.get("latency_ms", 0),
            "cost_per_decision": values.get("cost", 0.0) / decision_count if decision_count else 0,
            "avg_latency_ms_per_decision": values.get("latency_ms", 0) / decision_count if decision_count else 0,
            "invalid_attempts": sum(1 for row in invalid_attempts if row["player_id"] == player_id),
            "fallbacks": sum(1 for row in per_decision if row["player_id"] == player_id and row["fallback_used"]),
            "final_cash_summary": summary["players"].get(player_id, {}).get("cash"),
            "final_net_worth_summary": summary["players"].get(player_id, {}).get("net_worth_estimate"),
            "bankrupt_summary": summary["players"].get(player_id, {}).get("bankrupt"),
            "final_cash_snapshot": final_row["cash"],
            "final_net_worth_snapshot": final_row["net_worth_estimate"],
            "bankrupt_snapshot": final_row["bankrupt"],
        }
    )
write_csv(OUT / "player_model_summary.csv", model_rows)

set_sizes = {
    "BROWN": 2,
    "LIGHT_BLUE": 3,
    "PINK": 3,
    "ORANGE": 3,
    "RED": 3,
    "YELLOW": 3,
    "GREEN": 3,
    "DARK_BLUE": 2,
    "RAILROAD": 4,
    "UTILITY": 2,
}
first_sets = []
seen_sets = set()
for turn, _path, snapshot in snapshots:
    counts = {player_id: Counter() for player_id in PLAYER_ORDER}
    for space in snapshot.get("board", []):
        owner = space.get("owner_id")
        group = space.get("group")
        if owner in counts and group in set_sizes:
            counts[owner][group] += 1
    for player_id in PLAYER_ORDER:
        for group, size in set_sizes.items():
            key = (player_id, group)
            if key not in seen_sets and counts[player_id][group] >= size:
                seen_sets.add(key)
                first_sets.append({"turn_index": turn, "player_id": player_id, "group": group, "set_size": size})
write_csv(OUT / "first_complete_sets.csv", first_sets)

rent_agg = {player_id: {"paid": 0, "received": 0, "paid_count": 0, "received_count": 0} for player_id in PLAYER_ORDER}
for row in rent_payments:
    if row["from_player_id"] in rent_agg:
        rent_agg[row["from_player_id"]]["paid"] += row["amount"]
        rent_agg[row["from_player_id"]]["paid_count"] += 1
    if row["to_player_id"] in rent_agg:
        rent_agg[row["to_player_id"]]["received"] += row["amount"]
        rent_agg[row["to_player_id"]]["received_count"] += 1
rent_by_player = [
    {"player_id": player_id, **values, "net_rent": values["received"] - values["paid"]}
    for player_id, values in rent_agg.items()
]
write_csv(OUT / "rent_by_player.csv", rent_by_player)

batch_rows = []
for start in range(0, max_turn + 1, 25):
    end = min(max_turn, start + 24)
    batch_usage = [row for row in per_call if row["turn_index"] is not None and start <= row["turn_index"] <= end]
    batch_events = [event for event in events if event.get("turn_index") is not None and start <= event.get("turn_index") <= end]
    batch_rent = [row for row in rent_payments if start <= row["turn_index"] <= end]
    batch_trace = [row for row in trace_findings if row.get("turn_index") is not None and start <= row["turn_index"] <= end]
    batch_failures = [row for row in failure_findings if row.get("turn_index") is not None and start <= row["turn_index"] <= end]
    batch_rows.append(
        {
            "turn_start": start,
            "turn_end": end,
            "attempts": len(batch_usage),
            "decisions": sum(1 for row in per_decision if start <= row["turn_index"] <= end),
            "cost": sum(row["cost"] for row in batch_usage),
            "input_tokens": sum(row["input_tokens"] for row in batch_usage),
            "output_tokens": sum(row["output_tokens"] for row in batch_usage),
            "reasoning_tokens": sum(row["reasoning_tokens"] for row in batch_usage),
            "total_tokens": sum(row["total_tokens"] for row in batch_usage),
            "max_latency_s": max([row["latency_s"] for row in batch_usage] or [0]),
            "invalid_attempts": sum(1 for row in invalid_attempts if start <= row["turn_index"] <= end),
            "rent_payment_count": len(batch_rent),
            "rent_paid_total": sum(row["amount"] for row in batch_rent),
            "large_rent_count_500_plus": sum(1 for row in batch_rent if row["amount"] >= 500),
            "trade_proposed": sum(1 for event in batch_events if event.get("type") == "TRADE_PROPOSED"),
            "trade_accepted": sum(1 for event in batch_events if event.get("type") == "TRADE_ACCEPTED"),
            "house_events": sum(
                1
                for event in batch_events
                if event.get("type") in ("HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD")
            ),
            "bankruptcy_cash_events": sum(
                1
                for event in batch_events
                if event.get("type") == "CASH_CHANGED"
                and str((event.get("payload") or {}).get("reason") or "").startswith("BANKRUPTCY")
            ),
            "trace_findings": len(batch_trace),
            "failure_findings": len(batch_failures),
        }
    )
write_csv(OUT / "turn_batches_25.csv", batch_rows)

summary_issues = []
final_rows = {
    row["player_id"]: row
    for row in per_turn_financial
    if row["turn_index"] == summary["turn_count"]
}
for player_id in PLAYER_ORDER:
    summary_player = summary["players"].get(player_id, {})
    final_player = final_rows[player_id]
    for field in ("bankrupt", "cash", "net_worth_estimate"):
        if summary_player.get(field) != final_player.get(field):
            summary_issues.append(
                {
                    "kind": "summary_snapshot_mismatch",
                    "field": field,
                    "player_id": player_id,
                    "summary_value": summary_player.get(field),
                    "snapshot_value": final_player.get(field),
                }
            )

analysis_summary = {
    "run_id": summary["run_id"],
    "winner": summary["winner_player_id"],
    "end_reason": summary["reason"],
    "turn_count": summary["turn_count"],
    "replay_status": replay_report.get("status"),
    "event_count": len(events),
    "decision_count": len(per_decision),
    "attempt_count": len(per_call),
    "invalid_attempt_count": len(invalid_attempts),
    "fallback_count": sum(1 for row in per_decision if row["fallback_used"]),
    "total_cost": sum(row["cost"] for row in per_call),
    "total_input_tokens": sum(row["input_tokens"] for row in per_call),
    "total_output_tokens": sum(row["output_tokens"] for row in per_call),
    "total_reasoning_tokens": sum(row["reasoning_tokens"] for row in per_call),
    "total_tokens": sum(row["total_tokens"] for row in per_call),
    "total_latency_ms": sum(row["latency_ms"] for row in per_call),
    "cost_per_turn": sum(row["cost"] for row in per_call) / max(1, summary["turn_count"]),
    "cost_per_decision": sum(row["cost"] for row in per_call) / max(1, len(per_decision)),
    "player_model_summary": model_rows,
    "rent_by_player": rent_by_player,
    "first_complete_sets": first_sets,
    "top_expensive_calls": top_n(per_call, "cost", 10),
    "top_latency_calls": top_n(per_call, "latency_ms", 10),
    "top_reasoning_calls": top_n(per_call, "reasoning_tokens", 10),
    "top_output_calls": top_n(per_call, "output_tokens", 10),
    "summary_consistency_issues": summary_issues,
    "trace_summary": read_json(ROOT / "trace_summary.json"),
    "failure_summary": read_json(ROOT / "failure_summary.json"),
}
(OUT / "analysis_summary.json").write_text(json.dumps(analysis_summary, indent=2, ensure_ascii=False), encoding="utf-8")


def by_player_series(metric):
    data = {player_id: ([], []) for player_id in PLAYER_ORDER}
    for row in per_turn_financial:
        data[row["player_id"]][0].append(row["turn_index"])
        data[row["player_id"]][1].append(row[metric])
    return data


def setup_turn_axis(ax, ylabel, title):
    ax.set_xlim(0, max_turn)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=12, integer=True))
    ax.grid(True, alpha=0.25)
    ax.set_xlabel("Turn index")
    ax.set_ylabel(ylabel)
    ax.set_title(title)


def savefig(name):
    plt.tight_layout()
    plt.savefig(OUT / name, dpi=180)
    plt.close()


bankruptcy_turns = sorted(
    set(row["turn_index"] for row in bankruptcy_cash_events if row.get("reason") == "BANKRUPTCY")
)


def draw_bankruptcy_markers(ax):
    for turn in bankruptcy_turns:
        ax.axvline(turn, color="#ef4444", linestyle="--", alpha=0.35, linewidth=1)


for metric, ylabel, title, filename in [
    ("net_worth_estimate", "Estimated net worth ($)", "Net worth by turn", "net_worth_by_turn.png"),
    ("cash", "Cash ($)", "Cash by turn", "cash_by_turn.png"),
    ("property_value_estimate", "Face-value property assets ($)", "Property value by turn", "property_value_by_turn.png"),
    ("building_value_estimate", "Building investment value ($)", "Building value by turn", "building_value_by_turn.png"),
    ("property_count", "Owned properties", "Owned property count by turn", "property_count_by_turn.png"),
    ("houses", "House equivalents", "House count by turn", "houses_by_turn.png"),
]:
    fig, ax = plt.subplots(figsize=(12, 6))
    for player_id, (xs, ys) in by_player_series(metric).items():
        ax.plot(xs, ys, label=SHORT[player_id], color=COLORS[player_id], linewidth=2)
    setup_turn_axis(ax, ylabel, title)
    if "$" in ylabel:
        ax.yaxis.set_major_formatter(FuncFormatter(money))
    draw_bankruptcy_markers(ax)
    ax.legend(ncol=4, fontsize=9)
    savefig(filename)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot([row["turn_index"] for row in turn_bank], [row["houses_remaining"] for row in turn_bank], label="Houses remaining", color="#16a34a", linewidth=2)
ax.plot([row["turn_index"] for row in turn_bank], [row["hotels_remaining"] for row in turn_bank], label="Hotels remaining", color="#7c3aed", linewidth=2)
setup_turn_axis(ax, "Inventory count", "Bank building inventory by turn")
ax.set_ylim(0, 34)
draw_bankruptcy_markers(ax)
ax.legend()
savefig("bank_building_inventory_by_turn.png")

fig, ax = plt.subplots(figsize=(12, 6))
for player_id in PLAYER_ORDER:
    xs, ys, cumulative = [], [], 0.0
    for row in per_call:
        if row["player_id"] == player_id:
            cumulative += row["cost"]
        xs.append(row["call_index"])
        ys.append(cumulative)
    ax.plot(xs, ys, label=SHORT[player_id], color=COLORS[player_id], linewidth=2)
ax.set_xlim(0, max(1, len(per_call) - 1))
ax.set_xlabel("Call index")
ax.set_ylabel("Cumulative cost (USD)")
ax.set_title("Cumulative OpenRouter cost by call")
ax.yaxis.set_major_formatter(FuncFormatter(dollars3))
ax.grid(True, alpha=0.25)
ax.legend(ncol=4, fontsize=9)
savefig("cumulative_cost_by_call.png")

for metric, ylabel, title, filename, formatter in [
    ("cost", "Cost per call (USD)", "Per-call cost outliers", "call_cost_scatter.png", dollars3),
    ("latency_s", "Latency per call (seconds)", "Per-call latency outliers", "call_latency_scatter.png", None),
    ("output_tokens", "Output tokens per call", "Output tokens per call", "call_output_tokens_scatter.png", None),
    ("reasoning_tokens", "Reasoning tokens per call", "Reasoning tokens per call", "call_reasoning_tokens_scatter.png", None),
]:
    fig, ax = plt.subplots(figsize=(12, 6))
    for player_id in PLAYER_ORDER:
        rows = [row for row in per_call if row["player_id"] == player_id]
        ax.scatter(
            [row["call_index"] for row in rows],
            [row[metric] for row in rows],
            label=SHORT[player_id],
            color=COLORS[player_id],
            s=18,
            alpha=0.65,
        )
    ax.set_xlim(0, max(1, len(per_call) - 1))
    ax.set_xlabel("Call index")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if formatter:
        ax.yaxis.set_major_formatter(FuncFormatter(formatter))
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=4, fontsize=9)
    savefig(filename)

turns = [row["turn_index"] for row in per_turn_usage]
fig, axs = plt.subplots(4, 1, figsize=(12, 13), sharex=True)
plots = [
    ("cost", "Cost (USD)", "Cost per turn"),
    ("total_tokens", "Total tokens", "Total tokens per turn"),
    ("reasoning_tokens", "Reasoning tokens", "Reasoning tokens per turn"),
    ("latency_ms", "Latency (seconds)", "Total model latency per turn"),
]
for ax, (metric, ylabel, title) in zip(axs, plots):
    ys = [(row[metric] / 1000 if metric == "latency_ms" else row[metric]) for row in per_turn_usage]
    ax.plot(turns, ys, color="#2563eb", linewidth=1.8)
    ax.set_xlim(0, max_turn)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=11)
    ax.grid(True, alpha=0.25)
    if metric == "cost":
        ax.yaxis.set_major_formatter(FuncFormatter(dollars3))
    draw_bankruptcy_markers(ax)
axs[-1].set_xlabel("Turn index")
savefig("per_turn_usage_panels.png")

decisions_by_turn = Counter(row["turn_index"] for row in per_decision)
all_turns = list(range(0, max_turn + 1))
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(all_turns, [decisions_by_turn.get(turn, 0) for turn in all_turns], color="#0f766e", width=0.9)
setup_turn_axis(ax, "Decisions", "LLM decisions per turn")
draw_bankruptcy_markers(ax)
savefig("decisions_per_turn.png")

fig, ax = plt.subplots(figsize=(12, 6))
for player_id in PLAYER_ORDER:
    rows = [row for row in rent_payments if row["from_player_id"] == player_id]
    ax.scatter(
        [row["turn_index"] for row in rows],
        [row["amount"] for row in rows],
        label=f"{SHORT[player_id]} paid",
        color=COLORS[player_id],
        s=24,
        alpha=0.7,
    )
setup_turn_axis(ax, "Rent amount ($)", "Rent payments by turn")
ax.yaxis.set_major_formatter(FuncFormatter(money))
draw_bankruptcy_markers(ax)
ax.legend(ncol=4, fontsize=8)
savefig("rent_payments_by_turn.png")

fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
batch_x = [(row["turn_start"] + row["turn_end"]) / 2 for row in batch_rows]
width = 22
axs[0].bar(batch_x, [row["cost"] for row in batch_rows], width=width, color="#2563eb")
axs[0].set_ylabel("Cost (USD)")
axs[0].yaxis.set_major_formatter(FuncFormatter(dollars3))
axs[0].set_title("25-turn batch cost")
axs[1].bar(batch_x, [row["rent_paid_total"] for row in batch_rows], width=width, color="#db2777")
axs[1].set_ylabel("Rent paid ($)")
axs[1].yaxis.set_major_formatter(FuncFormatter(money))
axs[1].set_title("25-turn batch rent volume")
axs[2].bar(batch_x, [row["failure_findings"] for row in batch_rows], width=width, color="#ef4444")
axs[2].set_ylabel("Failure findings")
axs[2].set_title("25-turn batch failure findings")
for ax in axs:
    ax.set_xlim(0, max_turn)
    ax.grid(True, axis="y", alpha=0.25)
    draw_bankruptcy_markers(ax)
axs[-1].set_xlabel("Turn index")
savefig("turn_batch_panels.png")

fig, axs = plt.subplots(2, 2, figsize=(12, 9))
for ax, (metric, title) in zip(
    axs.flat,
    [
        ("cost", "Cost (USD)"),
        ("input_tokens", "Input tokens"),
        ("output_tokens", "Output tokens"),
        ("reasoning_tokens", "Reasoning tokens"),
    ],
):
    values = [next(row for row in model_rows if row["player_id"] == player_id)[metric] for player_id in PLAYER_ORDER]
    ax.bar([SHORT[player_id] for player_id in PLAYER_ORDER], values, color=[COLORS[player_id] for player_id in PLAYER_ORDER])
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.25)
    if metric == "cost":
        ax.yaxis.set_major_formatter(FuncFormatter(dollars3))
savefig("model_usage_bars.png")

fig, ax = plt.subplots(figsize=(12, 5))
trace_by_turn = Counter(row.get("turn_index") for row in trace_findings if row.get("turn_index") is not None)
failure_by_turn = Counter(row.get("turn_index") for row in failure_findings if row.get("turn_index") is not None)
ax.plot(all_turns, [trace_by_turn.get(turn, 0) for turn in all_turns], label="Trace findings", color="#64748b", linewidth=1.8)
ax.plot(all_turns, [failure_by_turn.get(turn, 0) for turn in all_turns], label="Failure findings", color="#ef4444", linewidth=1.8)
setup_turn_axis(ax, "Finding count", "Trace/failure findings by turn")
draw_bankruptcy_markers(ax)
ax.legend()
savefig("findings_by_turn.png")

readme = [
    f"# Run analysis: {summary['run_id']}",
    "",
    f"Winner: **{summary['winner_player_id']}**. End reason: **{summary['reason']}** at turn **{summary['turn_count']}**.",
    f"Replay status: **{replay_report.get('status')}** with {replay_report.get('original_event_count')} original events and {replay_report.get('replay_event_count')} replay events.",
    f"Usage: {len(per_decision)} decisions, {len(per_call)} OpenRouter attempts, {len(invalid_attempts)} invalid attempts, {sum(1 for row in per_decision if row['fallback_used'])} fallbacks.",
    f"Cost: ${analysis_summary['total_cost']:.6f}; tokens: {analysis_summary['total_input_tokens']:,} input, {analysis_summary['total_output_tokens']:,} output, {analysis_summary['total_reasoning_tokens']:,} reasoning, {analysis_summary['total_tokens']:,} total.",
    "",
    "## Generated plots",
]
readme.extend(f"- `{path.name}`" for path in sorted(OUT.glob("*.png")))
readme.append("")
readme.append("## Consistency issues")
if summary_issues:
    for issue in summary_issues:
        readme.append(
            f"- {issue['player_id']} `{issue['field']}` mismatch: summary={issue['summary_value']} snapshot={issue['snapshot_value']}"
        )
else:
    readme.append("- None found.")
readme.append("")
readme.append("## Key CSV tables")
readme.extend(f"- `{path.name}`" for path in sorted(OUT.glob("*.csv")))
(OUT / "README.md").write_text("\n".join(readme), encoding="utf-8")

print(
    json.dumps(
        {
            "analysis_dir": str(OUT),
            "run_id": summary["run_id"],
            "winner": summary["winner_player_id"],
            "turn_count": summary["turn_count"],
            "replay_status": replay_report.get("status"),
            "decisions": len(per_decision),
            "attempts": len(per_call),
            "invalid_attempts": len(invalid_attempts),
            "fallbacks": sum(1 for row in per_decision if row["fallback_used"]),
            "cost": round(analysis_summary["total_cost"], 6),
            "summary_issues": summary_issues,
            "plot_count": len(list(OUT.glob("*.png"))),
        },
        indent=2,
    )
)
