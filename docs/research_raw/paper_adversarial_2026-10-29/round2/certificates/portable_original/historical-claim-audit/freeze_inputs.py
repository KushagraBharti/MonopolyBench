"""Freeze canonical cases and minimal replay inputs before running diagnostics.

The package retains applied actions and per-event digests, not provider reasoning.
No source game or engine file is modified. Run from the repository checkout.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def rows(path):
    with path.open() as stream:
        for line_no, line in enumerate(stream, 1):
            if line.strip():
                yield line_no, json.loads(line), digest(line.rstrip("\n").encode())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    if (HERE / "inputs_manifest.json").exists():
        raise SystemExit("Inputs already frozen; do not overwrite a reviewed manifest.")
    source = ROOT / "docs/research_raw/paper_phase1_2026-10-28/sol/manifest.json"
    games, cases = [], []
    for game in json.loads(source.read_text())["games"]:
        number, run = game["game"], ROOT / game["run"]
        config = json.loads((run / "run_config.json").read_text())
        starts, resolved = {}, {}
        for line_no, row, row_hash in rows(run / "decisions.jsonl"):
            entry = (row, {"line": line_no, "line_sha256": row_hash})
            if row["phase"] == "decision_started":
                starts[row["decision_id"]] = entry
            elif row["phase"] == "decision_resolved":
                resolved[row["decision_id"]] = entry
        events = [row for _, row, _ in rows(run / "events.jsonl")]
        event_hashes = [digest(canonical(row)) for row in events]
        event_prefix_hash = hashlib.sha256()
        prefix_by_decision = {}
        latest_response = None
        for index, event in enumerate(events):
            event_prefix_hash.update(canonical(event) + b"\n")
            if event["type"] == "LLM_DECISION_REQUESTED":
                prefix_by_decision[event["payload"]["decision_id"]] = {
                    "event_count": index + 1,
                    "canonical_prefix_sha256": event_prefix_hash.hexdigest(),
                }
            if event["type"] == "LLM_DECISION_RESPONSE":
                latest_response = event["payload"]["decision_id"]
            if event["type"] == "CASH_CHANGED" and event["payload"].get("reason") == "BANKRUPTCY":
                response, ref = resolved[latest_response]
                start, start_ref = starts[latest_response]
                cases.append({
                    "case_id": f"G{number:02d}-{latest_response[-10:]}-elimination",
                    "kind": "elimination", "game": number, "decision_id": latest_response,
                    "actor": start["player_id"], "model": start["openrouter_model_id"],
                    "source_start": start_ref, "source_resolution": ref,
                    "event_seq": event["seq"], "elimination_event_sha256": event_hashes[index],
                    "applied_action": response["final_action"]["action"],
                    "classification": "declared" if response["final_action"]["action"] == "declare_bankruptcy" else "automatic",
                    "prefix": prefix_by_decision[latest_response],
                })
        for decision_id, (response, ref) in resolved.items():
            if not response.get("fallback_used"):
                continue
            start, start_ref = starts[decision_id]
            attempts = []
            for i, attempt in enumerate(response["attempts"]):
                call = attempt.get("parsed_tool_call")
                item = {"attempt_index": i, "outcome": attempt.get("outcome"),
                        "condition": attempt.get("response_condition"),
                        "recorded_errors": attempt.get("validation_errors"),
                        "tool_name": call.get("name") if isinstance(call, dict) else None}
                if item["tool_name"] == "build_houses_or_hotel":
                    try:
                        args = call["arguments"]
                        if isinstance(args, str):
                            args = json.loads(args)
                        item["plan"] = args["build_plan"]
                    except (ValueError, TypeError, KeyError) as exc:
                        item["plan_parse_error"] = type(exc).__name__
                attempts.append(item)
            cases.append({
                "case_id": f"G{number:02d}-{decision_id[-10:]}-default",
                "kind": "default", "game": number, "decision_id": decision_id,
                "actor": start["player_id"], "model": start["openrouter_model_id"],
                "source_start": start_ref, "source_resolution": ref,
                "applied_action": response["final_action"]["action"],
                "attempts": attempts, "prefix": prefix_by_decision[decision_id],
            })
        target = HERE / "inputs" / f"g{number:02d}"
        target.mkdir(parents=True)
        # Full recorded actions allow verification of the complete historical stream,
        # not a claim that altered branches reproduce its later policy.
        shutil.copy2(run / "actions.jsonl", target / "actions.jsonl")
        write(target / "config.json", {key: config[key] for key in (
            "seed", "players", "run_id", "max_turns", "max_trade_exchanges", "max_auction_actions",
            "start_ts_ms", "ts_step_ms")})
        write(target / "event_hashes.json", event_hashes)
        games.append({"game": number, "seed_block": (number - 1) // 4 + 1,
                      "source_run": game["run"], "action_count": len(list(rows(run / "actions.jsonl"))),
                      "event_count": len(events), "source_hashes": {
                          name: digest((run / name).read_bytes()) for name in
                          ("actions.jsonl", "events.jsonl", "decisions.jsonl", "run_config.json")}})
    # Selection is canonical, independent of whether the later diagnostics succeed.
    cases.sort(key=lambda row: (row["game"], row["decision_id"], row["kind"]))
    write(HERE / "cases.json", cases)
    write(HERE / "games.json", games)
    engine = ROOT / "python/packages/engine/src/monopoly_engine"
    vendor = HERE / "vendor/monopoly_engine"
    vendor.mkdir(parents=True)
    copied_sources = {}
    for path in sorted(engine.glob("*.py")):
        dest = vendor / path.name
        shutil.copy2(path, dest)
        copied_sources[str(dest.relative_to(HERE))] = {"source": str(path.relative_to(ROOT)), "sha256": digest(path.read_bytes())}
    board = ROOT / "contracts/data/board.json"
    dest = HERE / "contracts/data/board.json"
    dest.parent.mkdir(parents=True)
    shutil.copy2(board, dest)
    copied_sources[str(dest.relative_to(HERE))] = {"source": str(board.relative_to(ROOT)), "sha256": digest(board.read_bytes())}
    deps = {name: importlib.metadata.version(name) for name in
            ("pydantic", "pydantic_core", "annotated-types", "typing_extensions", "typing-inspection")}
    (HERE / "requirements.txt").write_text("".join(f"{name}=={version}\n" for name, version in deps.items()))
    write(HERE / "environment.json", {"python": sys.version, "dependencies": deps})
    input_files = [p for folder in ("inputs", "vendor", "contracts") for p in (HERE / folder).rglob("*") if p.is_file()]
    input_files += [HERE / name for name in ("cases.json", "games.json", "requirements.txt", "environment.json")]
    write(HERE / "inputs_manifest.json", {
        "selection": "All canonical BANKRUPTCY markers and all decision_resolved fallback_used records in the 20-game cohort, frozen before diagnostics.",
        "counts": {"eliminations": sum(c["kind"] == "elimination" for c in cases),
                   "defaults": sum(c["kind"] == "default" for c in cases)},
        "source_manifest_sha256": digest(source.read_bytes()), "copied_engine_sources": copied_sources,
        "files": {str(p.relative_to(HERE)): digest(p.read_bytes()) for p in sorted(input_files)},
    })
    print(json.dumps({"games": len(games), "cases": len(cases), "counts": json.loads((HERE / "inputs_manifest.json").read_text())["counts"]}))


if __name__ == "__main__":
    main()
