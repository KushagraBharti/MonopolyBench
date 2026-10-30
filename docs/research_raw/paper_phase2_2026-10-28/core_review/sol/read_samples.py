"""Render original sample bundles without extractor verdicts or duplicate channels.

Only exact repetition and opaque signatures are abbreviated. No semantic labels
are generated. Output is a reading aid, not evidence that a bundle was read.
"""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PACKETS = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_packets"
KNOWN = {}


def reference_key(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def remember(value, location):
    rendered = reference_key(value)
    if len(rendered) >= 180:
        KNOWN.setdefault(rendered, location)
    if isinstance(value, dict):
        for key, item in value.items():
            remember(item, f"{location}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            remember(item, f"{location}/{index}")


def reference_repeats(value, location="current output"):
    rendered = reference_key(value)
    if len(rendered) >= 180 and rendered in KNOWN:
        return {"exact_repeat_of_previously_read": KNOWN[rendered]}
    if isinstance(value, dict):
        result = {key: reference_repeats(item, f"{location}/{key}") for key, item in value.items()}
    elif isinstance(value, list):
        result = [reference_repeats(item, f"{location}/{index}") for index, item in enumerate(value)]
    else:
        result = value
    # Subsequent channels may repeat fields already displayed in this bundle.
    # Register only after rendering their entire value, never before visiting it.
    if len(rendered) >= 180:
        KNOWN.setdefault(rendered, location)
    return result


def compact(value):
    if isinstance(value, dict):
        return {key: compact(item) for key, item in value.items() if key not in {"signature", "semantic_review"}}
    if isinstance(value, list):
        return [compact(item) for item in value]
    if isinstance(value, str) and value.startswith("campaign-") and ("-dec-" in value or "-evt-" in value):
        return value.rsplit("-", 2)[-2] + "-" + value.rsplit("-", 1)[-1]
    return value


def emit(label, value):
    print(label, json.dumps(reference_repeats(compact(value), label), ensure_ascii=False, separators=(",", ":")))


def load_units(game):
    units = []
    for packet in sorted(PACKETS.glob(f"game-{game:02d}-part-*.jsonl")):
        for line_index, line in enumerate(packet.read_text().splitlines(), 1):
            units.append((json.loads(line), packet.relative_to(ROOT).as_posix(), line_index, hashlib.sha256(line.encode()).hexdigest()))
    return units


def render(index, sample, units):
    position = next(i for i, row in enumerate(units) if row[0]["decision_id"] == sample["decision_id"])
    unit, packet, line, digest = units[position]
    emit("SAMPLE", {"index": index, "selection": sample, "packet": packet, "line": line, "sha256": digest})
    emit("IDENTITY", {key: unit[key] for key in ["decision_id", "decision_type", "player_id", "game", "model", "turn_index", "source_run", "source_lines"]})
    emit("APPLIED", unit["applied_action_record"])
    emit("PROMPT", unit["initial_prompt"])
    for attempt in unit["attempts"]:
        # Parsed tools, assistant_content and raw response may repeat verbatim;
        # preserve the raw fields and all attempt metadata in one object.
        rendered = dict(attempt)
        response = dict(attempt.get("raw_response") or {})
        if "choices" in response:
            choices = []
            for choice in response["choices"]:
                choice = dict(choice)
                message = dict(choice.get("message") or {})
                if "reasoning_details" in message:
                    details = []
                    for detail in message["reasoning_details"]:
                        detail = dict(detail)
                        for field in ["text", "summary"]:
                            if detail.get(field) is not None and detail[field] == message.get("reasoning"):
                                detail[field] = "[exact repeat of message.reasoning]"
                        details.append(detail)
                    message["reasoning_details"] = details
                choice["message"] = message
                choices.append(choice)
            response["choices"] = choices
        rendered["raw_response"] = response
        emit("ATTEMPT", rendered)
    emit("EVENTS", [{key: event[key] for key in ["seq", "turn_index", "type", "actor", "payload"]} for event in unit["canonical_event_segment"]])
    emit("RESOLUTION", unit["resolution"])
    emit("PHYSICAL_RESPONSES", unit["physical_responses"])
    for adjacent in [position - 1, position + 1]:
        if 0 <= adjacent < len(units):
            other, path, row, _ = units[adjacent]
            emit("ADJACENT", {"packet": path, "line": row, "applied": other["applied_action_record"], "events": [{key: event[key] for key in ["seq", "turn_index", "type", "payload"]} for event in other["canonical_event_segment"]]})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    args = parser.parse_args()
    samples = [json.loads(line) for line in (HERE.parent / "public_unflagged_sample.jsonl").read_text().splitlines()]
    # Deduplicate against only explicitly authored completed sample records.
    for record in map(json.loads, (HERE / "negative_control_reviews.jsonl").read_text().splitlines()):
        source = record["source_checks"]
        unit = json.loads((ROOT / source["packet"]).read_text().splitlines()[source["packet_line"] - 1])
        remember(compact(unit), f"reviewed {record['decision_id']}")
    games = {}
    for index in range(args.start, args.end):
        sample = samples[index]
        if sample["game"] not in games:
            games[sample["game"]] = load_units(sample["game"])
        render(index, sample, games[sample["game"]])


if __name__ == "__main__":
    main()
