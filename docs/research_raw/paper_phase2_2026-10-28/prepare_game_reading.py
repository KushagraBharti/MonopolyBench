"""Lossless whole-game reading copies with decoded JSON strings and deduplication.

Every original JSON value is recovered exactly in the round-trip check. This is
preparation, not semantic review. Formatting-only JSON text is kept in a sidecar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from prepare_reading_chunks import decode, encode, pointer_key

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TAG = "$decoded_json_string"


def normalize(value):
    originals = {}

    def visit(item, path):
        if isinstance(item, dict):
            if TAG in item:
                raise ValueError("Reserved reading key exists in source")
            return {k: visit(v, path + "/" + pointer_key(k)) for k, v in item.items()}
        if isinstance(item, list):
            return [visit(v, path + "/" + str(i)) for i, v in enumerate(item)]
        if isinstance(item, str) and item.lstrip().startswith(("{", "[")):
            try:
                parsed = json.loads(item)
            except (ValueError, TypeError):
                return item
            if isinstance(parsed, (dict, list)):
                originals[path] = item
                return {TAG: visit(parsed, path + "/" + TAG)}
        return item

    return visit(value, ""), originals


def restore(value, originals):
    def visit(item, path):
        if isinstance(item, dict) and set(item) == {TAG}:
            parsed = visit(item[TAG], path + "/" + TAG)
            original = originals[path]
            assert json.loads(original) == parsed
            return original
        if isinstance(item, dict):
            return {k: visit(v, path + "/" + pointer_key(k)) for k, v in item.items()}
        if isinstance(item, list):
            return [visit(v, path + "/" + str(i)) for i, v in enumerate(item)]
        return item

    return visit(value, "")


def behavior_view(packet):
    """Keep all response channels, observations, actions and event payloads.

    Provider billing/latency IDs and duplicate envelopes remain in the lossless
    original view. The initial user message must equal its structured payload.
    """
    initial = packet["initial_prompt"]
    instructions = []
    for message in initial["messages"]:
        if message["role"] == "user":
            if isinstance(message["content"], dict):
                assert message["content"] == {"exact_json_value_ref": "payload"}
            else:
                assert json.loads(message["content"]) == initial["payload"]
        else:
            instructions.append(message)
    attempts = []
    fields = ("attempt_index_zero_based", "outcome", "response_condition", "reason",
              "error_type", "error_message", "validation_errors", "requested_model",
              "assistant_content", "parsed_tool_call", "parsed_tool_calls", "prompt")
    for attempt in packet["attempts"]:
        raw = attempt.get("raw_response")
        response = ({k: raw.get(k) for k in ("model", "provider", "choices")}
                    if isinstance(raw, dict) and "choices" in raw else raw)
        attempts.append({k: attempt.get(k) for k in fields} | {"provider_response": response})
    resolution = packet["resolution"]
    return {k: packet[k] for k in ("game", "decision_id", "turn_index", "player_id", "model", "decision_type")} | {
        "observation": initial["payload"], "instructions": instructions,
        "applied_action": packet["applied_action_record"], "attempts": attempts,
        "events": [{k: e[k] for k in ("seq", "turn_index", "actor", "type", "payload")}
                   for e in packet["canonical_event_segment"]],
        "resolution": {k: resolution.get(k) for k in ("fallback_used", "fallback_reason", "retry_used", "applied")}}


def prepare(game):
    ledger = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra/review_unit_ledger.jsonl"
    units = [json.loads(line) for line in ledger.read_text().splitlines() if json.loads(line)["game"] == game]
    cache, packets, sources = {}, [], []
    for unit in units:
        path = ROOT / unit["packet"]
        if path not in cache:
            cache[path] = path.read_text().splitlines()
        line = cache[path][unit["packet_line"] - 1]
        packet = json.loads(line)
        assert packet["decision_id"] == unit["decision_id"]
        packets.append(packet)
        sources.append({"decision_id": unit["decision_id"], "packet": unit["packet"],
                        "packet_line": unit["packet_line"], "source_line_sha256": hashlib.sha256(line.encode()).hexdigest()})
    original = {"packets": packets}
    normalized, originals = normalize(original)
    encoded = encode(normalized, minimum=60)
    assert restore(decode(encoded), originals) == original
    target = HERE / "full_review" / f"game-{game:02d}"
    target.mkdir(parents=True, exist_ok=True)
    text = '{"packets":[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False, separators=(",", ":"))
                                         for p in encoded["packets"]) + '\n]}\n'
    assert restore(decode(json.loads(text)), originals) == original
    (target / "reading.json").write_text(text)
    (target / "json_string_originals.json").write_text(json.dumps(originals, ensure_ascii=False) + "\n")
    view = {"packets": [behavior_view(p) for p in packets]}
    view_normalized, view_strings = normalize(view)
    view_encoded = encode(view_normalized, minimum=60)
    assert restore(decode(view_encoded), view_strings) == view
    reading = '{"packets":[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False, separators=(",", ":"))
                                            for p in view_encoded["packets"]) + '\n]}\n'
    (target / "behavior.json").write_text(reading)
    (target / "behavior_json_strings.json").write_text(json.dumps(view_strings, ensure_ascii=False) + "\n")
    pages = []
    size = 24000
    for i, start in enumerate(range(0, len(reading), size), 1):
        name = f"page-{i:04d}.txt"
        end = min(start + size, len(reading))
        body = reading[start:end]
        (target / name).write_text(f"GAME {game} PAGE {i} CHARACTERS {start}:{end} OF {len(reading)}\n" + body + "\nEND PAGE\n")
        pages.append({"file": name, "start": start, "end": end})
    report = {"version": "lossless_game_reading_v1", "game": game, "decisions": len(units),
              "attempts": sum(len(p["attempts"]) for p in packets),
              "source_characters": len(json.dumps(original, ensure_ascii=False, separators=(",", ":"))),
              "reading_characters": len(text), "behavior_characters": len(reading),
              "behavior_scope": "All applied actions, event payloads, initial observation/system instructions, attempt prompts, all provider choices and parsed response channels. Billing/latency metadata and duplicate initial prompt envelopes remain in reading.json/source packets.",
              "behavior_roundtrip": True, "behavior_sha256": hashlib.sha256(reading.encode()).hexdigest(),
              "decoded_json_strings": len(originals),
              "exact_original_json_roundtrip": True, "semantic_review": "not_performed",
              "reading_sha256": hashlib.sha256(text.encode()).hexdigest(), "pages": pages, "sources": sources}
    (target / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in {"pages", "sources"}})[:-1] + f', "pages": {len(pages)}}}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--games", type=int, nargs="+", required=True)
    args = parser.parse_args()
    for game in args.games:
        prepare(game)
