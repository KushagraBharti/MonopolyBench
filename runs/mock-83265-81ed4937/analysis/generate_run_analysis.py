from __future__ import annotations

import csv
import json
import math
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


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def usage_from_attempt(attempt: dict) -> dict:
    raw = attempt.get("raw_response") or {}
    usage = raw.get("usage") or {}
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


def board_values(snapshot: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for player_id in PLAYERS:
        result[player_id] = {
            "property_value": 0,
            "building_value": 0,
            "mortgage_liability": 0,
            "property_count": 0,
            "mortgaged_count": 0,
            "houses": 0,
            "hotels": 0,
        }

    for space in snapshot.get("board", []):
        owner = space.get("owner_id")
        if owner not in result:
            continue
        price = int(space.get("price") or 0)
        group = space.get("group")
        houses = int(space.get("houses") or 0)
        hotel = bool(space.get("hotel"))
        house_cost = HOUSE_COST_BY_GROUP.get(group, 0)
        result[owner]["property_value"] += price
        result[owner]["building_value"] += houses * house_cost + (5 * house_cost if hotel else 0)
        result[owner]["property_count"] += 1
        result[owner]["houses"] += houses
        result[owner]["hotels"] += 1 if hotel else 0
        if space.get("mortgaged"):
            result[owner]["mortgage_liability"] += price // 2
            result[owner]["mortgaged_count"] += 1
    return result


def snapshot_sort_key(path: Path) -> tuple[int, int]:
    stem = path.stem
    parts = stem.split("_")
    turn = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else -1
    decision = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
    return turn, decision


def snapshot_rows() -> tuple[list[dict], dict | None]:
    latest_by_turn: dict[int, Path] = {}
    for path in (RUN_DIR / "state").glob("turn_*.json"):
        turn, decision = snapshot_sort_key(path)
        current = latest_by_turn.get(turn)
        if current is None or snapshot_sort_key(path) > snapshot_sort_key(current):
            latest_by_turn[turn] = path

    rows: list[dict] = []
    final_snapshot = None
    for turn in sorted(latest_by_turn):
        snapshot = json.loads(latest_by_turn[turn].read_text(encoding="utf-8"))
        final_snapshot = snapshot
        values = board_values(snapshot)
        players_by_id = {p["player_id"]: p for p in snapshot.get("players", [])}
        for player_id in PLAYERS:
            player = players_by_id.get(player_id, {})
            v = values[player_id]
            cash = int(player.get("cash") or 0)
            net = cash + v["property_value"] + v["building_value"] - v["mortgage_liability"]
            rows.append(
                {
                    "turn_index": turn,
                    "player_id": player_id,
                    "cash": cash,
                    "net_worth": net,
                    "property_value": v["property_value"],
                    "building_value": v["building_value"],
                    "mortgage_liability": v["mortgage_liability"],
                    "property_count": v["property_count"],
                    "mortgaged_count": v["mortgaged_count"],
                    "houses": v["houses"],
                    "hotels": v["hotels"],
                    "bankrupt": bool(player.get("bankrupt")),
                    "position": player.get("position"),
                    "in_jail": bool(player.get("in_jail")),
                }
            )
    return rows, final_snapshot


def decision_rows(decisions: list[dict]) -> tuple[list[dict], list[dict]]:
    resolved = [d for d in decisions if d.get("phase") == "decision_resolved"]
    started = [d for d in decisions if d.get("phase") == "decision_started"]
    rows: list[dict] = []
    for idx, decision in enumerate(resolved, start=1):
        attempts = decision.get("attempts") or []
        usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "reasoning_tokens": 0,
            "cached_tokens": 0,
            "cost": 0.0,
        }
        missing_usage = 0
        invalid_attempts = 0
        for attempt in attempts:
            errors = attempt.get("validation_errors") or []
            invalid_attempts += 1 if errors else 0
            attempt_usage = usage_from_attempt(attempt)
            if not attempt_usage["total_tokens"] and not attempt_usage["cost"]:
                missing_usage += 1
            for key in usage:
                usage[key] += attempt_usage[key]
        action = decision.get("final_action") or {}
        rows.append(
            {
                "call_index": idx,
                "turn_index": decision.get("turn_index"),
                "decision_id": decision.get("decision_id"),
                "player_id": decision.get("player_id"),
                "model_id": decision.get("openrouter_model_id"),
                "provider_model": ((attempts[0].get("raw_response") or {}).get("model") if attempts else None),
                "decision_type": decision.get("decision_type"),
                "action": action.get("action"),
                "attempt_count": len(attempts),
                "invalid_attempts": invalid_attempts,
                "retry_used": bool(decision.get("retry_used")),
                "fallback_used": bool(decision.get("fallback_used")),
                "missing_usage_attempts": missing_usage,
                "latency_ms": int(decision.get("latency_ms") or 0),
                **usage,
            }
        )

    resolved_ids = {d.get("decision_id") for d in resolved}
    pending = [d for d in started if d.get("decision_id") not in resolved_ids]
    return rows, pending


def aggregate_by_model(calls: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for row in calls:
        player = row["player_id"]
        g = grouped.setdefault(
            player,
            {
                "player_id": player,
                "model_id": row["model_id"],
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "total_tokens": 0,
                "cached_tokens": 0,
                "cost": 0.0,
                "latency_ms": 0,
                "invalid_attempts": 0,
                "fallbacks": 0,
                "retries": 0,
            },
        )
        g["calls"] += 1
        for key in ("input_tokens", "output_tokens", "reasoning_tokens", "total_tokens", "cached_tokens", "latency_ms", "invalid_attempts"):
            g[key] += int(row.get(key) or 0)
        g["cost"] += float(row.get("cost") or 0.0)
        g["fallbacks"] += 1 if row.get("fallback_used") else 0
        g["retries"] += 1 if row.get("retry_used") else 0
    for g in grouped.values():
        calls = g["calls"] or 1
        g["avg_latency_ms"] = round(g["latency_ms"] / calls, 2)
        g["cost_per_call"] = round(g["cost"] / calls, 8)
    return sorted(grouped.values(), key=lambda r: r["cost"], reverse=True)


def event_tables(events: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    counts = Counter(event.get("type") for event in events)
    event_counts = [{"event_type": k, "count": v} for k, v in counts.most_common()]

    by_turn: dict[int, Counter] = defaultdict(Counter)
    for event in events:
        by_turn[int(event.get("turn_index") or 0)][event.get("type")] += 1
    turn_rows = []
    event_types = sorted(counts)
    for turn, counter in sorted(by_turn.items()):
        row = {"turn_index": turn, "total_events": sum(counter.values())}
        for event_type in event_types:
            row[event_type] = counter.get(event_type, 0)
        turn_rows.append(row)

    bankruptcies = []
    for event in events:
        payload = event.get("payload") or {}
        if event.get("type") == "CASH_CHANGED" and payload.get("reason") == "BANKRUPTCY":
            bankruptcies.append(
                {
                    "turn_index": event.get("turn_index"),
                    "player_id": payload.get("player_id"),
                    "seq": event.get("seq"),
                }
            )
    return event_counts, turn_rows, bankruptcies


def batch_rows(calls: list[dict], snapshots: list[dict], events: list[dict], batch_size: int = 25) -> list[dict]:
    event_counter: dict[int, Counter] = defaultdict(Counter)
    for event in events:
        batch = int(event.get("turn_index") or 0) // batch_size
        event_counter[batch][event.get("type")] += 1

    calls_by_batch: dict[int, list[dict]] = defaultdict(list)
    for call in calls:
        calls_by_batch[int(call.get("turn_index") or 0) // batch_size].append(call)

    turns = [int(r["turn_index"]) for r in snapshots]
    max_batch = (max(turns) if turns else 0) // batch_size
    rows = []
    for batch in range(max_batch + 1):
        batch_calls = calls_by_batch.get(batch, [])
        counter = event_counter.get(batch, Counter())
        rows.append(
            {
                "turn_start": batch * batch_size,
                "turn_end": batch * batch_size + batch_size - 1,
                "calls": len(batch_calls),
                "events": sum(counter.values()),
                "cost": round(sum(float(c.get("cost") or 0) for c in batch_calls), 6),
                "input_tokens": sum(int(c.get("input_tokens") or 0) for c in batch_calls),
                "output_tokens": sum(int(c.get("output_tokens") or 0) for c in batch_calls),
                "reasoning_tokens": sum(int(c.get("reasoning_tokens") or 0) for c in batch_calls),
                "rent_events": counter.get("RENT_PAID", 0),
                "trade_events": counter.get("TRADE_PROPOSED", 0) + counter.get("TRADE_REJECTED", 0) + counter.get("TRADE_ACCEPTED", 0),
                "building_events": counter.get("BUILDINGS_BUILT", 0) + counter.get("BUILDINGS_SOLD", 0),
                "bankruptcy_cash_events": sum(
                    1
                    for e in events
                    if (int(e.get("turn_index") or 0) // batch == batch if batch else int(e.get("turn_index") or 0) < batch_size)
                )
                if False
                else counter.get("CASH_CHANGED", 0),
            }
        )
    return rows


def save_plot(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_lines(df: pd.DataFrame, y: str, title: str, ylabel: str, path: Path, x: str = "turn_index") -> None:
    plt.figure(figsize=(12, 6))
    for player in PLAYERS:
        sub = df[df["player_id"] == player]
        if not sub.empty:
            plt.plot(sub[x], sub[y], label=player, color=COLORS[player], linewidth=2)
    plt.title(title)
    plt.xlabel("Turn index")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.25)
    plt.legend(loc="best", fontsize=8)
    save_plot(path)


def make_plots(calls: list[dict], snapshots: list[dict], by_model: list[dict], events_by_turn: list[dict], batch_summary: list[dict]) -> None:
    calls_df = pd.DataFrame(calls)
    snap_df = pd.DataFrame(snapshots)
    model_df = pd.DataFrame(by_model)
    turn_df = pd.DataFrame(events_by_turn)
    batch_df = pd.DataFrame(batch_summary)

    if not snap_df.empty:
        plot_lines(snap_df, "net_worth", "Net Worth by Turn", "Net worth ($)", PLOT_DIR / "net_worth_by_turn.png")
        plot_lines(snap_df, "cash", "Cash by Turn", "Cash ($)", PLOT_DIR / "cash_by_turn.png")
        plot_lines(snap_df, "building_value", "Building Asset Value by Turn", "Building value ($)", PLOT_DIR / "building_value_by_turn.png")
        plot_lines(snap_df, "property_count", "Property Count by Turn", "Properties", PLOT_DIR / "property_count_by_turn.png")

    if not calls_df.empty:
        calls_df["cumulative_cost"] = calls_df["cost"].cumsum()
        plt.figure(figsize=(12, 6))
        plt.plot(calls_df["call_index"], calls_df["cumulative_cost"], color="#111827", linewidth=2)
        plt.title("Cumulative Cost by LLM Call")
        plt.xlabel("LLM call index")
        plt.ylabel("Cumulative cost ($)")
        plt.grid(True, alpha=0.25)
        save_plot(PLOT_DIR / "cumulative_cost_by_call.png")

        plt.figure(figsize=(12, 6))
        for player in PLAYERS:
            sub = calls_df[calls_df["player_id"] == player]
            plt.scatter(sub["call_index"], sub["cost"], label=player, color=COLORS[player], s=18, alpha=0.8)
        plt.title("Cost per LLM Call")
        plt.xlabel("LLM call index")
        plt.ylabel("Cost per call ($)")
        plt.grid(True, alpha=0.25)
        plt.legend(loc="best", fontsize=8)
        save_plot(PLOT_DIR / "cost_per_call.png")

        plt.figure(figsize=(12, 6))
        for player in PLAYERS:
            sub = calls_df[calls_df["player_id"] == player]
            plt.scatter(sub["call_index"], sub["latency_ms"] / 1000, label=player, color=COLORS[player], s=18, alpha=0.8)
        plt.title("Latency per LLM Call")
        plt.xlabel("LLM call index")
        plt.ylabel("Latency (seconds)")
        plt.grid(True, alpha=0.25)
        plt.legend(loc="best", fontsize=8)
        save_plot(PLOT_DIR / "latency_per_call.png")

        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
        for ax, col, label in [
            (axes[0], "input_tokens", "Input tokens"),
            (axes[1], "output_tokens", "Output tokens"),
            (axes[2], "reasoning_tokens", "Reasoning tokens"),
        ]:
            for player in PLAYERS:
                sub = calls_df[calls_df["player_id"] == player]
                ax.scatter(sub["call_index"], sub[col], label=player, color=COLORS[player], s=14, alpha=0.75)
            ax.set_ylabel(label)
            ax.grid(True, alpha=0.25)
        axes[0].set_title("Token Usage per LLM Call")
        axes[2].set_xlabel("LLM call index")
        axes[0].legend(loc="best", fontsize=8)
        save_plot(PLOT_DIR / "tokens_per_call_subplots.png")

    if not model_df.empty:
        model_df = model_df.set_index("player_id").loc[[p for p in PLAYERS if p in set(model_df["player_id"])]].reset_index()
        plt.figure(figsize=(10, 6))
        plt.bar(model_df["player_id"], model_df["cost"], color=[COLORS[p] for p in model_df["player_id"]])
        plt.title("Total Cost by Model")
        plt.xlabel("Model")
        plt.ylabel("Cost ($)")
        plt.xticks(rotation=20, ha="right")
        plt.grid(True, axis="y", alpha=0.25)
        save_plot(PLOT_DIR / "cost_by_model.png")

        plt.figure(figsize=(10, 6))
        bottom = [0] * len(model_df)
        for col, label, color in [
            ("input_tokens", "Input", "#94a3b8"),
            ("output_tokens", "Output", "#0f766e"),
            ("reasoning_tokens", "Reasoning", "#b45309"),
        ]:
            vals = model_df[col].tolist()
            plt.bar(model_df["player_id"], vals, bottom=bottom, label=label, color=color)
            bottom = [a + b for a, b in zip(bottom, vals)]
        plt.title("Token Mix by Model")
        plt.xlabel("Model")
        plt.ylabel("Tokens")
        plt.xticks(rotation=20, ha="right")
        plt.legend()
        plt.grid(True, axis="y", alpha=0.25)
        save_plot(PLOT_DIR / "tokens_by_model_stacked.png")

    if not turn_df.empty:
        plt.figure(figsize=(12, 6))
        plt.plot(turn_df["turn_index"], turn_df["total_events"], color="#111827", linewidth=1.7)
        plt.title("Event Volume by Turn")
        plt.xlabel("Turn index")
        plt.ylabel("Events")
        plt.grid(True, alpha=0.25)
        save_plot(PLOT_DIR / "events_by_turn.png")

    if not batch_df.empty:
        labels = [f'{int(r.turn_start)}-{int(r.turn_end)}' for r in batch_df.itertuples()]
        plt.figure(figsize=(12, 6))
        plt.bar(labels, batch_df["cost"], color="#2563eb")
        plt.title("Cost by 25-Turn Batch")
        plt.xlabel("Turn batch")
        plt.ylabel("Cost ($)")
        plt.xticks(rotation=30, ha="right")
        plt.grid(True, axis="y", alpha=0.25)
        save_plot(PLOT_DIR / "cost_by_25_turn_batch.png")


def main() -> None:
    ANALYSIS_DIR.mkdir(exist_ok=True)
    TABLE_DIR.mkdir(exist_ok=True)
    PLOT_DIR.mkdir(exist_ok=True)

    events = read_jsonl(RUN_DIR / "events.jsonl")
    decisions = read_jsonl(RUN_DIR / "decisions.jsonl")
    actions = read_jsonl(RUN_DIR / "actions.jsonl")
    calls, pending = decision_rows(decisions)
    snapshots, final_snapshot = snapshot_rows()
    by_model = aggregate_by_model(calls)
    event_counts, events_by_turn, bankruptcies = event_tables(events)
    batches = batch_rows(calls, snapshots, events)

    final_rows = []
    if final_snapshot:
        last_turn_rows = [r for r in snapshots if r["turn_index"] == max(r["turn_index"] for r in snapshots)]
        final_rows = sorted(last_turn_rows, key=lambda r: (r["bankrupt"], -r["net_worth"]))

    action_mix_counter = Counter((row.get("player_id"), row.get("action")) for row in calls)
    action_mix = [
        {"player_id": player, "action": action, "count": count}
        for (player, action), count in sorted(action_mix_counter.items(), key=lambda item: (item[0][0] or "", item[0][1] or ""))
    ]

    write_csv(TABLE_DIR / "llm_calls.csv", calls)
    write_csv(TABLE_DIR / "model_usage.csv", by_model)
    write_csv(TABLE_DIR / "state_by_turn_player.csv", snapshots)
    write_csv(TABLE_DIR / "final_players.csv", final_rows)
    write_csv(TABLE_DIR / "event_counts.csv", event_counts)
    write_csv(TABLE_DIR / "events_by_turn.csv", events_by_turn)
    write_csv(TABLE_DIR / "bankruptcies.csv", bankruptcies)
    write_csv(TABLE_DIR / "action_mix.csv", action_mix)
    write_csv(TABLE_DIR / "batch_summary_25_turns.csv", batches)
    write_csv(TABLE_DIR / "top_20_costliest_calls.csv", sorted(calls, key=lambda r: r["cost"], reverse=True)[:20])
    write_csv(TABLE_DIR / "top_20_slowest_calls.csv", sorted(calls, key=lambda r: r["latency_ms"], reverse=True)[:20])

    total_cost = sum(float(r["cost"]) for r in calls)
    total_input = sum(int(r["input_tokens"]) for r in calls)
    total_output = sum(int(r["output_tokens"]) for r in calls)
    total_reasoning = sum(int(r["reasoning_tokens"]) for r in calls)
    total_tokens = sum(int(r["total_tokens"]) for r in calls)
    final_event = events[-1] if events else None
    game_ended = [e for e in events if e.get("type") == "GAME_ENDED"]
    event_decision_requests = {
        (e.get("payload") or {}).get("decision_id")
        for e in events
        if e.get("type") == "LLM_DECISION_REQUESTED"
    }
    resolved_ids = {r["decision_id"] for r in calls}
    unresolved_event_decisions = sorted(d for d in event_decision_requests if d and d not in resolved_ids)

    summary = {
        "run_id": RUN_DIR.name,
        "artifact_status": "incomplete_no_game_ended" if not game_ended else "complete",
        "max_turns_configured": json.loads((RUN_DIR / "run_config.json").read_text(encoding="utf-8")).get("max_turns"),
        "last_event": final_event,
        "event_count": len(events),
        "action_count": len(actions),
        "decision_log_entries": len(decisions),
        "resolved_llm_calls": len(calls),
        "pending_decision_started_entries": len(pending),
        "unresolved_event_decision_ids": unresolved_event_decisions,
        "game_ended_events": len(game_ended),
        "turn_min": min((e.get("turn_index") for e in events), default=None),
        "turn_max": max((e.get("turn_index") for e in events), default=None),
        "total_cost": round(total_cost, 8),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_reasoning_tokens": total_reasoning,
        "total_tokens": total_tokens,
        "missing_usage_calls": sum(1 for r in calls if r["missing_usage_attempts"]),
        "invalid_attempts": sum(int(r["invalid_attempts"]) for r in calls),
        "retries": sum(1 for r in calls if r["retry_used"]),
        "fallbacks": sum(1 for r in calls if r["fallback_used"]),
        "avg_latency_ms": round(sum(int(r["latency_ms"]) for r in calls) / len(calls), 2) if calls else None,
        "median_latency_ms": median([int(r["latency_ms"]) for r in calls]) if calls else None,
        "max_latency_ms": max((int(r["latency_ms"]) for r in calls), default=0),
        "final_players": final_rows,
        "by_model": by_model,
        "bankruptcies": bankruptcies,
        "event_counts": event_counts,
    }
    write_json(ANALYSIS_DIR / "analysis_summary.json", summary)

    make_plots(calls, snapshots, by_model, events_by_turn, batches)

    top_cost = sorted(calls, key=lambda r: r["cost"], reverse=True)[:5]
    top_latency = sorted(calls, key=lambda r: r["latency_ms"], reverse=True)[:5]
    report = [
        f"# MonopolyBench Run Analysis: {RUN_DIR.name}",
        "",
        "## Integrity",
        f"- Artifact status: `{summary['artifact_status']}`",
        f"- Last saved event: seq `{final_event.get('seq') if final_event else None}`, turn `{final_event.get('turn_index') if final_event else None}`, type `{final_event.get('type') if final_event else None}`",
        f"- GAME_ENDED events: `{len(game_ended)}`",
        f"- Unresolved decision ids in event log: `{', '.join(unresolved_event_decisions) if unresolved_event_decisions else 'none'}`",
        f"- Events/actions/resolved calls: `{len(events)}` / `{len(actions)}` / `{len(calls)}`",
        "",
        "## Cost And Tokens",
        f"- Total cost: `${total_cost:.6f}`",
        f"- Tokens: `{total_input:,}` input, `{total_output:,}` output, `{total_reasoning:,}` reasoning, `{total_tokens:,}` total",
        f"- Missing usage calls: `{summary['missing_usage_calls']}`",
        f"- Retries/fallbacks/invalid attempts: `{summary['retries']}` / `{summary['fallbacks']}` / `{summary['invalid_attempts']}`",
        "",
        "## Final Saved State",
    ]
    for row in final_rows:
        report.append(
            f"- {row['player_id']}: cash `${row['cash']:,}`, net worth `${row['net_worth']:,}`, properties `{row['property_count']}`, houses `{row['houses']}`, hotels `{row['hotels']}`, bankrupt `{row['bankrupt']}`"
        )
    report += [
        "",
        "## Top Costliest Calls",
    ]
    for row in top_cost:
        report.append(
            f"- call {row['call_index']} turn {row['turn_index']} {row['player_id']} {row['decision_type']} `{row['action']}`: ${row['cost']:.6f}, {row['total_tokens']:,} tokens, {row['latency_ms']/1000:.1f}s"
        )
    report += [
        "",
        "## Top Slowest Calls",
    ]
    for row in top_latency:
        report.append(
            f"- call {row['call_index']} turn {row['turn_index']} {row['player_id']} {row['decision_type']} `{row['action']}`: {row['latency_ms']/1000:.1f}s, ${row['cost']:.6f}"
        )
    report += [
        "",
        "## Generated Files",
        "- `analysis/plots/*.png`",
        "- `analysis/tables/*.csv`",
        "- `analysis/analysis_summary.json`",
    ]
    (ANALYSIS_DIR / "analysis_report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()
