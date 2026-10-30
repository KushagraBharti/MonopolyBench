"""Trace canonical public-message occurrences into delivered timeline summaries.

This sidecar instruments the existing PromptMemory without changing its output.
It records occurrence provenance, not semantic exposure, recipient awareness,
speaker intent, or coverage of text repeated elsewhere in the prompt.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "python/packages/arena/src"))
sys.path.insert(0, str(ROOT / "python/packages/engine/src"))
sys.path.insert(0, str(ROOT / "python/packages/telemetry/src"))

from monopoly_arena.prompting import PromptMemory, _can_merge_timeline_items  # noqa: E402


class DeliveryMemory(PromptMemory):
    """Attach identifiers externally so the production memory stays unchanged."""

    def __init__(self):
        super().__init__()
        self.current_event = None
        self.claimed_source = None
        self.pending_sources = {}
        self.summary_sources = {}
        self.held_summaries = []  # Prevent Python object-id reuse in the sidecar.
        self.public = {}
        self.inserted = set()
        self.suppressed = []
        self.claimed_without_summary = {}
        self.summary_called = False
        self.deliveries = defaultdict(dict)

    def update(self, event):
        self.current_event = event
        self.claimed_source = None
        self.summary_called = False
        super().update(event)
        if self.claimed_source and not self.summary_called:
            self.claimed_without_summary[self.claimed_source] = {
                "action_event_id": event["event_id"], "event_type": event["type"],
                "reason": event.get("payload", {}).get("reason"),
            }

    def _track_public_message(self, turn_index, payload):
        super()._track_public_message(turn_index, payload)
        player = payload["player_id"]
        pending = self._pending_messages_by_player[player][-1]
        event = self.current_event
        source = event["event_id"]
        self.pending_sources[id(pending)] = source
        self.public[source] = {
            "event_id": source, "seq": event["seq"], "turn": turn_index,
            "player_id": player, "decision_id": payload["decision_id"],
            "message": payload.get("message"),
        }

    def _claim_pending_message(self, event):
        pending = super()._claim_pending_message(event)
        self.claimed_source = self.pending_sources.get(id(pending)) if pending is not None else None
        return pending

    def _append_or_merge_summary(self, summary):
        self.summary_called = True
        source = self.claimed_source if summary.get("message") is not None else None
        previous = self._public_timeline[-1] if self._public_timeline else None
        merges = previous is not None and _can_merge_timeline_items(previous, summary)
        if merges:
            if source and previous.get("message") is not None:
                self.suppressed.append({
                    "source_event_id": source,
                    "retained_source_event_id": self.summary_sources.get(id(previous)),
                    "action_event_id": self.current_event["event_id"],
                    "timeline_event_type": summary["event_type"],
                })
            elif source:
                self.summary_sources[id(previous)] = source
                self.inserted.add(source)
        else:
            self.held_summaries.append(summary)
            self.summary_sources[id(summary)] = source
            if source:
                self.inserted.add(source)
        super()._append_or_merge_summary(summary)

    def observe(self, start):
        player = start["player_id"]
        recorded = start["prompt_payload"]["game_state"]["memory"]
        if self.snapshot_for_player(player) != recorded:
            raise AssertionError(f"Memory differs at {start['decision_id']}")
        for summary in self._public_timeline:
            source = self.summary_sources.get(id(summary))
            if source is not None:
                origin = self.public[source]
                assert summary["message"] == origin["message"]
                assert summary["player_id"] == origin["player_id"]
                assert summary["turn_index"] == origin["turn"]
            if source is not None and player != self.public[source]["player_id"]:
                self.deliveries[source].setdefault(player, {
                    "decision_id": start["decision_id"], "turn": start["turn_index"],
                })


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def games():
    for name in ("railway-research-12-games-2026-10-25", "railway-research-8-games-2026-10-26"):
        collection = ROOT / "saved_games" / name
        with (collection / "game-index.csv").open() as stream:
            for row in csv.DictReader(stream):
                yield int(row["collection_game"]), collection / row["package"] / "run"


def main():
    messages, merged, counts, sources = [], [], Counter(), []
    by_model = defaultdict(Counter)
    for game, run in games():
        memory = DeliveryMemory()
        decisions = read_rows(run / "decisions.jsonl")
        starts = {r["decision_id"]: r for r in decisions if r["phase"] == "decision_started"}
        resolved = {r["decision_id"]: r for r in decisions if r["phase"] == "decision_resolved"}
        config = json.loads((run / "run_config.json").read_text())
        models = {p["player_id"]: p["openrouter_model_id"] for p in config["players"]}
        for event in read_rows(run / "events.jsonl"):
            if event["type"] == "LLM_DECISION_REQUESTED":
                memory.observe(starts[event["payload"]["decision_id"]])
                counts["checked_initial_memories"] += 1
            memory.update(event)
        suppressed = {r["source_event_id"]: r for r in memory.suppressed}
        for source, row in memory.public.items():
            fallback = resolved[row["decision_id"]]["fallback_used"]
            row.update(game=game, model=models[row["player_id"]],
                       origin="deterministic_fallback" if fallback else "selected_model_action",
                       source_ledger=str((run / "events.jsonl").relative_to(ROOT)),
                       in_public_timeline_at_least_once=source in memory.inserted,
                       omitted_on_building_merge=source in suppressed,
                       claimed_on_unsummarized_event=memory.claimed_without_summary.get(source),
                       first_opponent_timeline_prompts=memory.deliveries.get(source, {}))
            messages.append(row)
            nonempty = isinstance(row["message"], str) and bool(row["message"].strip())
            for c in (counts, by_model[row["model"]]):
                c["canonical_public_messages"] += 1
                c["nonempty_canonical_messages"] += nonempty
                if nonempty:
                    c["nonempty_inserted_into_timeline"] += source in memory.inserted
                    c["nonempty_omitted_on_building_merge"] += source in suppressed
                    c["nonempty_not_inserted_into_timeline"] += source not in memory.inserted
                    c["nonempty_claimed_on_unsummarized_event"] += source in memory.claimed_without_summary
                    c["nonempty_delivered_to_at_least_one_opponent_timeline"] += bool(memory.deliveries.get(source))
                    c["nonempty_inserted_without_observed_opponent_timeline_delivery"] += (
                        source in memory.inserted and not memory.deliveries.get(source))
            if source in suppressed:
                merged.append({**suppressed[source], **row})
        for filename in ("events.jsonl", "decisions.jsonl", "run_config.json"):
            path = run / filename
            sources.append({"path": str(path.relative_to(ROOT)),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    for name, rows in (("public_delivery.jsonl", messages), ("merged_public_messages.jsonl", merged)):
        with (HERE / name).open("w") as stream:
            for row in rows:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
    report = {
        "version": "sol_round2_delivery_v1", "counts": dict(counts),
        "by_model": {m: dict(c) for m, c in sorted(by_model.items())},
        "scope": "Occurrence attribution in public_timeline_last_20 of initial decision prompts only. "
                 "No inferred awareness, reliance, semantic equivalence or completeness of other prompt fields. "
                 "Missing timeline delivery is not a general claim of nonexposure.",
        "sources": sources,
        "analysis_sources": [
            {"path": str(path.relative_to(ROOT)),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(HERE.glob("*.py"))
        ],
        "prompting_sha256": hashlib.sha256((ROOT / "python/packages/arena/src/monopoly_arena/prompting.py").read_bytes()).hexdigest(),
    }
    (HERE / "public_delivery_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"sources"}}, indent=2))


if __name__ == "__main__":
    main()
