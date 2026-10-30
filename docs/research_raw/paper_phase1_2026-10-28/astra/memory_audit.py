"""Audit private memory actually delivered, including source-note provenance.

This is downstream, read-only analysis. A literal 'fallback' string alone never
determines provenance. Resolved decision metadata identifies synthetic notes.
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


class NoteHistory:
    def __init__(self, limit=10):
        self.limit = limit
        self.notes = collections.defaultdict(list)

    def append(self, event, fallback_used):
        payload = event["payload"]
        self.notes[payload["player_id"]].append({
            "value": {"turn_index": event["turn_index"], "thought": payload.get("thought")},
            "event_id": event["event_id"], "decision_id": payload["decision_id"],
            "origin": "deterministic_fallback" if fallback_used else "model_response",
        })
        self.notes[payload["player_id"]] = self.notes[payload["player_id"]][-self.limit:]

    def compare(self, player, observed):
        expected = self.notes[player]
        return isinstance(observed, list) and observed == [n["value"] for n in expected]

    def origins(self, player):
        return collections.Counter(n["origin"] for n in self.notes[player])


def read_rows(path):
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def memory_in(row):
    return (row.get("prompt_payload") or {}).get("game_state", {}).get("memory", {})


def attempt_memory(attempt, index, initial_memory):
    # The resolver deliberately omits the duplicated initial prompt in attempts[0].
    if index == 0 and attempt.get("prompt_payload") is None:
        return initial_memory, "initial_decision_record"
    return memory_in(attempt), "attempt_record"


def main():
    manifest = json.loads((OUT / "visibility_manifest.json").read_text())
    models = collections.defaultdict(collections.Counter)
    game_counts = []
    rows, issues = [], []
    for game in manifest["games"]:
        run = ROOT / game["package"] / "run"
        records = read_rows(run / "decisions.jsonl")
        starts = {r["decision_id"]: r for r in records if r["phase"] == "decision_started"}
        resolved = {r["decision_id"]: r for r in records if r["phase"] == "decision_resolved"}
        history = NoteHistory()
        by_game = collections.defaultdict(collections.Counter)
        for event in read_rows(run / "events.jsonl"):
            kind, payload = event["type"], event["payload"]
            if kind == "LLM_PRIVATE_THOUGHT":
                history.append(event, resolved[payload["decision_id"]]["fallback_used"])
            if kind != "LLM_DECISION_REQUESTED":
                continue
            did = payload["decision_id"]
            start, finish = starts[did], resolved[did]
            player, model = start["player_id"], start["openrouter_model_id"]
            memory = memory_in(start)
            observed = memory.get("your_private_thoughts_last_10")
            matches = history.compare(player, observed)
            if not matches:
                issues.append({"game": game["game"], "decision_id": did, "kind": "private_memory_disagreement"})
            origins = history.origins(player)
            for count in (models[model], by_game[model]):
                count["decisions"] += 1
                count["private_memory_matches_events"] += matches
                count["empty_private_memory"] += observed == []
                count["only_synthetic_private_memory"] += bool(origins) and not origins["model_response"]
                count["with_model_authored_private_memory"] += bool(origins["model_response"])
                count["model_note_entry_exposures"] += origins["model_response"]
                count["synthetic_note_entry_exposures"] += origins["deterministic_fallback"]
                count["decisions_with_refusal_attempt"] += any(a["outcome"] == "refused" for a in finish["attempts"])
            attempts_match = []
            attempt_memory_sources = []
            for index, attempt in enumerate(finish["attempts"]):
                delivered, source = attempt_memory(attempt, index, memory)
                same = delivered == memory
                attempt_memory_sources.append(source)
                attempts_match.append(same)
                models[model]["attempts_checked"] += 1
                models[model]["attempts_with_same_memory_as_initial_request"] += same
                if not same:
                    issues.append({"game": game["game"], "decision_id": did,
                                   "attempt_index_zero_based": index, "kind": "attempt_memory_differs"})
            rows.append({"game": game["game"], "decision_id": did, "model": model,
                         "player_id": player, "turn": start["turn_index"],
                         "memory_matches_events": matches, "source_note_origins": dict(origins),
                         "source_notes": [{k: v for k, v in n.items() if k != "value"}
                                          for n in history.notes[player]],
                         "public_memory_entries": len(memory.get("public_timeline_last_20", [])),
                         "attempt_memory_matches_initial": attempts_match,
                         "attempt_memory_sources": attempt_memory_sources,
                         "source_ledger": str((run / "decisions.jsonl").relative_to(ROOT))})
        game_counts.append({"game": game["game"], "seed": game["seed"],
                            "source_git_sha": game["source_git_sha"],
                            "by_model": {m: dict(c) for m, c in by_game.items()}})
    report = {"version": "astra_memory_v1", "by_model": {m: dict(c) for m, c in models.items()},
              "by_game": game_counts, "issues": issues,
              "scope": "Delivered private-memory provenance and equality, not memory utility or behavioral intent.",
              "units": "Entry exposures count the same retained note each time it appears in a new initial decision prompt."}
    (OUT / "memory_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    with (OUT / "memory_coverage.jsonl").open("w") as stream:
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps({"decisions": len(rows), "issues": len(issues), "by_model": report["by_model"]}, indent=2))
    if issues:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
