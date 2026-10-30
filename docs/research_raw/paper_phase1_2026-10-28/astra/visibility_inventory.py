"""Inventory evidence availability without claiming semantic review of its contents.

Canonical artifacts are read only. Outputs preserve decision/file references;
they never infer that token counts or encrypted fields are readable reasoning.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
COLLECTIONS = (
    "railway-research-12-games-2026-10-25",
    "railway-research-8-games-2026-10-26",
)


def records(path):
    with path.open() as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                yield number, json.loads(line)


def reasoning_inventory(response):
    """Return locations/types only, preserving provider labels and unreadability."""
    found = []
    if not isinstance(response, dict):
        return found
    choices = response.get("choices") or []
    for choice_index, choice in enumerate(choices):
        if not isinstance(choice, dict):
            continue
        message = choice.get("message") or {}
        if not isinstance(message, dict):
            continue
        for field in ("reasoning", "reasoning_content"):
            value = message.get(field)
            if isinstance(value, str) and value.strip():
                found.append({"location": f"choices[{choice_index}].message.{field}",
                              "kind": field, "readable": True, "characters": len(value)})
        for detail_index, detail in enumerate(message.get("reasoning_details") or []):
            if not isinstance(detail, dict):
                continue
            kind = detail.get("type", "unspecified")
            location = f"choices[{choice_index}].message.reasoning_details[{detail_index}]"
            # Provider summaries remain summaries; opaque/encrypted data is not text.
            readable = False
            for field in ("text", "summary"):
                value = detail.get(field)
                if isinstance(value, str) and value.strip() and "encrypted" not in str(kind):
                    found.append({"location": location + "." + field, "kind": kind,
                                  "readable": True, "characters": len(value)})
                    readable = True
            if not readable:
                found.append({"location": location, "kind": kind, "readable": False,
                              "available_fields": sorted(detail)})
    return found


def final_note_origin(action, fallback_used):
    value = action.get("private_thought")
    if not isinstance(value, str) or not value.strip():
        return "no_nonempty_final_note"
    return "deterministic_fallback" if fallback_used else "nonfallback_final_action"


def main():
    totals = collections.Counter()
    manifests, decisions, file_rows, response_rows = [], [], [], []
    model_totals = collections.defaultdict(collections.Counter)
    issues = []
    for collection_name in COLLECTIONS:
        collection = ROOT / "saved_games" / collection_name
        with (collection / "game-index.csv").open() as index_stream:
            indexes = list(csv.DictReader(index_stream))
        for index in indexes:
            run = collection / index["package"] / "run"
            game = int(index["collection_game"])
            config = json.loads((run / "run_config.json").read_text())
            by_decision = collections.defaultdict(lambda: collections.defaultdict(list))
            event_count = 0
            for line, event in records(run / "events.jsonl"):
                event_count += 1
                if event["type"] in {"LLM_PUBLIC_MESSAGE", "LLM_PRIVATE_THOUGHT"}:
                    did = event["payload"].get("decision_id")
                    by_decision[did][event["type"]].append({"event_id": event["event_id"], "line": line})
            actions = {}
            for line, action in records(run / "actions.jsonl"):
                did = action.get("decision_id")
                if did in actions:
                    raise ValueError(f"Duplicate action decision {did}")
                actions[did] = line
            starts, finishes = {}, {}
            for line, record in records(run / "decisions.jsonl"):
                target = starts if record["phase"] == "decision_started" else finishes
                if record["phase"] not in {"decision_started", "decision_resolved"}:
                    issues.append({"game": game, "kind": "unknown_decision_phase", "line": line})
                    continue
                did = record["decision_id"]
                if did in target:
                    raise ValueError(f"Duplicate {record['phase']} {did}")
                target[did] = (line, record)
            if set(starts) != set(finishes) or set(actions) != set(finishes):
                raise ValueError(f"Decision/action coverage mismatch in game {game}")
            response_files = collections.defaultdict(list)
            for path in sorted(run.rglob("*")):
                if not path.is_file():
                    continue
                relative = str(path.relative_to(ROOT))
                file_rows.append({"game": game, "path": relative, "bytes": path.stat().st_size,
                                  "semantic_review": "pending"})
                if path.name.endswith("_response.json"):
                    match = re.match(r"decision_(.*?-dec-\d+)", path.name)
                    did = match.group(1) if match else None
                    response_files[did].append(relative)
                    response = json.loads(path.read_text())
                    response_rows.append({"game": game, "decision_id": did, "path": relative,
                                          "reasoning_fields": reasoning_inventory(response),
                                          "semantic_review": "pending"})
                    if did not in finishes:
                        issues.append({"game": game, "kind": "unmatched_response_file", "path": relative})
            for did, (line, resolved) in finishes.items():
                model = resolved["openrouter_model_id"]
                attempts = []
                for attempt_index, attempt in enumerate(resolved.get("attempts", [])):
                    fields = reasoning_inventory(attempt.get("raw_response"))
                    attempts.append({"index_zero_based": attempt_index,
                                     "outcome": attempt.get("outcome"),
                                     "response_condition": attempt.get("response_condition"),
                                     "reasoning_fields": fields,
                                     "semantic_review": "pending"})
                events = by_decision[did]
                final_action = resolved.get("final_action") or {}
                row = {"game": game, "run_id": resolved["run_id"], "decision_id": did,
                       "model": model, "player_id": resolved["player_id"],
                       "turn": resolved["turn_index"], "decision_type": resolved["decision_type"],
                       "decision_ledger": str((run / "decisions.jsonl").relative_to(ROOT)),
                       "started_line": starts[did][0], "resolved_line": line,
                       "action_line": actions[did], "applied": resolved.get("applied"),
                       "applied_action": final_action.get("action"),
                       "fallback_used": bool(resolved.get("fallback_used")),
                       "final_action_origin": "deterministic_fallback" if resolved.get("fallback_used") else "nonfallback_final_action",
                       "final_private_note_origin": final_note_origin(final_action, bool(resolved.get("fallback_used"))),
                       "final_public_message_nonempty": bool(str(final_action.get("public_message") or "").strip()),
                       "public_event_refs": events["LLM_PUBLIC_MESSAGE"],
                       "private_event_refs": events["LLM_PRIVATE_THOUGHT"],
                       "response_files": response_files[did], "attempts": attempts,
                       "semantic_review": "pending", "behavior_labels": None}
                decisions.append(row)
                for counter in (totals, model_totals[model]):
                    counter["decisions"] += 1
                    counter["attempts"] += len(attempts)
                    counter["decisions_with_public_events"] += bool(row["public_event_refs"])
                    counter["decisions_with_private_events"] += bool(row["private_event_refs"])
                    counter["private_note_events_from_fallback"] += len(row["private_event_refs"]) if row["fallback_used"] else 0
                    counter["private_note_events_nonfallback"] += len(row["private_event_refs"]) if not row["fallback_used"] else 0
                    counter["decisions_with_readable_provider_reasoning_in_ledger"] += any(
                        f["readable"] for a in attempts for f in a["reasoning_fields"])
                    counter["decisions_with_opaque_reasoning_fields_in_ledger"] += any(
                        not f["readable"] for a in attempts for f in a["reasoning_fields"])
            source_files = []
            for name in ("events.jsonl", "actions.jsonl", "decisions.jsonl", "run_config.json", "summary.json"):
                path = run / name
                source_files.append({"path": str(path.relative_to(ROOT)),
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            manifests.append({"game": game, "run_id": index["run_id"], "seed": config["seed"],
                              "source_git_sha": index["git_sha"], "package": str(run.parent.relative_to(ROOT)),
                              "players": config["players"], "events": event_count,
                              "decisions": len(finishes), "source_files": source_files})
            totals["games"] += 1
            totals["events"] += event_count
    totals["run_files_inventoried"] = len(file_rows)
    totals["response_files_inventoried"] = len(response_rows)
    for name, rows in (("decision_coverage.jsonl", decisions), ("file_coverage.jsonl", file_rows),
                       ("response_coverage.jsonl", response_rows)):
        with (OUT / name).open("w") as stream:
            for row in rows:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
    report = {"status": "availability_inventory_only_semantic_review_pending", "totals": dict(totals),
              "by_model": {k: dict(v) for k, v in model_totals.items()}, "games": manifests,
              "issues": issues, "limitations": [
                  "Provider-labeled reasoning text may be a summary; it is not proof of latent intent.",
                  "Token usage is not readable reasoning. Opaque fields remain opaque.",
                  "Canonical actions and emitted public/private events are separate from all returned attempts.",
                  "File enumeration covers run directories; collection-level audits remain separate sources.",
                  "No behavioral label or semantic-review completion is inferred from this inventory."]}
    (OUT / "visibility_manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"totals": dict(totals), "issues": len(issues)}, indent=2))


if __name__ == "__main__":
    main()
