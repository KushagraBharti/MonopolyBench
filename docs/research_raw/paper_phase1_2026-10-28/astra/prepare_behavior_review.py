"""Prepare complete chronological review packets, without assigning behavior labels.

All decisions, attempts and events are retained. Exact duplicate prompt/response
representations point to the retained copy. Encrypted reasoning remains an opaque
reference with length/hash; it is never treated as readable reasoning.
"""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OUT = HERE / "review_packets"
MAX_PACKET_CHARACTERS = 180_000


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def readable_copy(value):
    if isinstance(value, list):
        return [readable_copy(x) for x in value]
    if not isinstance(value, dict):
        return value
    result = {k: readable_copy(v) for k, v in value.items()}
    if "encrypted" in str(value.get("type", "")).lower() and "data" in value:
        result["data"] = {"opaque": True, "serialized_characters": len(encoded(value["data"])),
                          "sha256": digest(value["data"]), "original_available_at_source": True}
    return result


def prompt_copy(record):
    payload = record.get("prompt_payload")
    output = {"payload": payload, "messages": []}
    for message in record.get("prompt_messages") or []:
        duplicate = False
        if payload is not None and message.get("role") == "user":
            try:
                duplicate = json.loads(message.get("content", "")) == payload
            except (ValueError, TypeError):
                pass
        output["messages"].append({**message, "content": {"exact_json_value_ref": "payload"}}
                                  if duplicate else message)
    raw = record.get("prompt_payload_raw")
    if raw is not None:
        try:
            duplicate = json.loads(raw) == payload
        except (ValueError, TypeError):
            duplicate = False
        output["raw_payload"] = {"exact_json_value_ref": "payload"} if duplicate else raw
    return output


def event_segments(events):
    requests = [i for i, e in enumerate(events) if e["type"] == "LLM_DECISION_REQUESTED"]
    if not requests:
        raise ValueError("No recorded decisions; review this game separately")
    for j, index in enumerate(requests):
        begin = 0 if j == 0 else index
        end = requests[j + 1] if j + 1 < len(requests) else len(events)
        yield events[index]["payload"]["decision_id"], begin + 1, events[begin:end]


def batches(units, max_chars):
    batch, size = [], 0
    for unit in units:
        length = len(encoded(unit)) + 1
        if batch and size + length > max_chars:
            yield batch
            batch, size = [], 0
        batch.append(unit)
        size += length
    if batch:
        yield batch


def rows(path):
    with path.open() as stream:
        return [(i, json.loads(line)) for i, line in enumerate(stream, 1) if line.strip()]


def main():
    manifest = json.loads((HERE / "visibility_manifest.json").read_text())
    coverage = {r["decision_id"]: r for _, r in rows(HERE / "decision_coverage.jsonl")}
    OUT.mkdir(exist_ok=True)
    packets, review_units = [], []
    totals = collections.Counter()
    for game in manifest["games"]:
        run = ROOT / game["package"] / "run"
        ledger = rows(run / "decisions.jsonl")
        starts = {r["decision_id"]: (line, r) for line, r in ledger if r["phase"] == "decision_started"}
        finishes = {r["decision_id"]: (line, r) for line, r in ledger if r["phase"] == "decision_resolved"}
        actions = {r["decision_id"]: (line, r) for line, r in rows(run / "actions.jsonl")}
        events = [r for _, r in rows(run / "events.jsonl")]
        units = []
        for did, event_line, segment in event_segments(events):
            start_line, start = starts[did]
            finish_line, finish = finishes[did]
            action_line, action = actions[did]
            attempt_rows = []
            response_hashes = set()
            for i, attempt in enumerate(finish["attempts"]):
                response_hashes.add(digest(attempt.get("raw_response")))
                copy = {k: v for k, v in attempt.items() if not k.startswith("prompt_")}
                copy["prompt"] = ({"initial_prompt_ref": True} if i == 0 and attempt.get("prompt_payload") is None
                                  else prompt_copy(attempt))
                copy["attempt_index_zero_based"] = i
                attempt_rows.append(readable_copy(copy))
            physical = []
            for path in coverage[did]["response_files"]:
                value = json.loads((ROOT / path).read_text())
                matched = digest(value) in response_hashes
                physical.append({"path": path, "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                                 "equal_to_ledger_response": matched,
                                 **({} if matched else {"physical_response": readable_copy(value)})})
                totals["physical_responses"] += 1
                totals["physical_responses_not_equal_to_ledger"] += not matched
            unit = {"version": "behavior_review_packet_v1", "game": game["game"], "decision_id": did,
                    "model": start["openrouter_model_id"], "player_id": start["player_id"],
                    "turn_index": start["turn_index"], "decision_type": start["decision_type"],
                    "source_run": str(run.relative_to(ROOT)),
                    "source_lines": {"decision_started": start_line, "decision_resolved": finish_line,
                                     "action": action_line, "event_segment_start": event_line,
                                     "event_segment_end": event_line + len(segment) - 1},
                    "initial_prompt": prompt_copy(start), "applied_action_record": action,
                    "resolution": {k: v for k, v in finish.items() if k != "attempts"},
                    "attempts": attempt_rows, "physical_responses": physical,
                    "canonical_event_segment": segment, "semantic_review": "pending"}
            units.append(unit)
            totals["decisions"] += 1
            totals["attempts"] += len(attempt_rows)
            totals["events"] += len(segment)
        if set(starts) != {u["decision_id"] for u in units}:
            raise AssertionError("Decision packet coverage differs")
        for number, batch in enumerate(batches(units, MAX_PACKET_CHARACTERS), 1):
            path = OUT / f"game-{game['game']:02d}-part-{number:03d}.jsonl"
            content = "".join(encoded(unit) + "\n" for unit in batch)
            path.write_text(content)
            packets.append({"path": str(path.relative_to(ROOT)), "game": game["game"],
                            "part": number, "decisions": len(batch), "characters": len(content),
                            "sha256": hashlib.sha256(content.encode()).hexdigest(),
                            "first_decision": batch[0]["decision_id"], "last_decision": batch[-1]["decision_id"],
                            "semantic_review": "pending"})
            for line, unit in enumerate(batch, 1):
                review_units.append({"game": game["game"], "decision_id": unit["decision_id"],
                                     "packet": str(path.relative_to(ROOT)), "packet_line": line,
                                     "semantic_review": "pending", "reviewer": None, "cases": []})
    for key in ("events", "decisions", "attempts"):
        if totals[key] != manifest["totals"][key]:
            raise AssertionError(f"Incomplete {key} coverage")
    if totals["physical_responses"] != manifest["totals"]["response_files_inventoried"]:
        raise AssertionError("Incomplete physical response coverage")
    output = {"version": "behavior_review_preparation_v1", "status": "prepared_not_semantically_reviewed",
              "totals": dict(totals), "packets": packets,
              "rules": ["Read game packets chronologically and retain cross-packet context.",
                        "Every unit and every attempt require an explicit review outcome.",
                        "Packet size is a reading aid, not an episode boundary or sampling rule.",
                        "Use canonical source references for exact serialization and opaque fields.",
                        "Recipient exposure and earlier delivery require actual recipient prompts.",
                        "Only listed packets belong to this version; generated files are not review results."]}
    (HERE / "review_packet_manifest.json").write_text(json.dumps(output, indent=2) + "\n")
    with (HERE / "review_unit_ledger.jsonl").open("w") as stream:
        for unit in review_units:
            stream.write(encoded(unit) + "\n")
    print(json.dumps({"totals": dict(totals), "packets": len(packets), "status": output["status"]}, indent=2))


if __name__ == "__main__":
    main()
