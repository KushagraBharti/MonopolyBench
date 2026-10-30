"""Read-only check of the frozen census against canonical local records."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PACKAGE = HERE / "extracted/historical-claim-audit"


def read(path):
    return json.loads(path.read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    games = read(PACKAGE / "games.json")
    cases = read(PACKAGE / "cases.json")
    report = read(HERE / "reproduced.json")
    errors = []
    observed = set()
    attempts_checked = 0
    source_files_checked = 0
    default_games = Counter()
    default_models = Counter()
    source_cases = {(c["game"], c["decision_id"], c["kind"]): c for c in cases}
    for game in games:
        number = game["game"]
        source = ROOT / game["source_run"]
        for name, expected in game["source_hashes"].items():
            source_files_checked += 1
            if sha((source / name).read_bytes()) != expected:
                errors.append([number, "source_file_hash", name])
        lines = (source / "decisions.jsonl").read_text().splitlines()
        resolved = {}
        for line in lines:
            row = json.loads(line)
            if row["phase"] != "decision_resolved":
                continue
            resolved[row["decision_id"]] = row
            if not row.get("fallback_used"):
                continue
            key = (number, row["decision_id"], "default")
            observed.add(key)
            case = source_cases.get(key)
            if case is None:
                errors.append([number, "missing_default", row["decision_id"]])
                continue
            default_games[str(number)] += 1
            default_models[row["openrouter_model_id"]] += 1
            if row["final_action"]["action"] != "end_turn":
                errors.append([number, "non_end_default", row["decision_id"]])
            if len(row["attempts"]) != len(case["attempts"]):
                errors.append([number, "attempt_count", row["decision_id"]])
            for i, attempt in enumerate(row["attempts"]):
                attempts_checked += 1
                frozen = case["attempts"][i]
                call = attempt.get("parsed_tool_call")
                name = call.get("name") if isinstance(call, dict) else None
                values = {
                    "attempt_index": i,
                    "outcome": attempt.get("outcome"),
                    "condition": attempt.get("response_condition"),
                    "recorded_errors": attempt.get("validation_errors"),
                    "tool_name": name,
                }
                if name == "build_houses_or_hotel":
                    try:
                        args = call["arguments"]
                        args = json.loads(args) if isinstance(args, str) else args
                        values["plan"] = args["build_plan"]
                    except (ValueError, KeyError, TypeError) as exc:
                        values["plan_parse_error"] = type(exc).__name__
                if values != frozen:
                    errors.append([number, "attempt_fields", row["decision_id"], i])
        last_response = None
        for line in (source / "events.jsonl").read_text().splitlines():
            event = json.loads(line)
            if event["type"] == "LLM_DECISION_RESPONSE":
                last_response = event["payload"]["decision_id"]
            if event["type"] == "CASH_CHANGED" and event["payload"].get("reason") == "BANKRUPTCY":
                key = (number, last_response, "elimination")
                observed.add(key)
                case = source_cases.get(key)
                if not case or case["actor"] != event["payload"]["player_id"] or case["event_seq"] != event["seq"]:
                    errors.append([number, "elimination_marker", event["seq"]])
        for case in [c for c in cases if c["game"] == number]:
            for field in ("source_start", "source_resolution"):
                record = case[field]
                if sha(lines[record["line"] - 1].encode()) != record["line_sha256"]:
                    errors.append([case["case_id"], field])
    if observed != set(source_cases):
        errors.append({"missing": sorted(observed - set(source_cases)), "extra": sorted(set(source_cases) - observed)})
    defaults = [r for r in report["results"] if r["kind"] == "default"]
    target_attempts = [a for r in defaults for a in r["attempts"] if "target_multiset" in a]
    target_patterns = Counter(json.dumps(a["target_multiset"], sort_keys=True) for a in target_attempts)
    figures = read(HERE.parent / "baseline/data/t06_eliminations.json")
    board = read(PACKAGE / "contracts/data/board.json")
    board_rows = board if isinstance(board, list) else board.get("spaces", board.get("board", []))
    index_keys = {s["index"]: re.sub(r"[^A-Za-z0-9]+", "_", s["name"].strip()).strip("_").upper() for s in board_rows}
    event_witnesses_checked = 0
    for case in defaults:
        for attempt in case["attempts"]:
            if attempt["diagnostic"] != "reachable_target":
                continue
            target = Counter({(key, kind): count for key, kind, count in attempt["target_multiset"]})
            actual = Counter()
            debit = 0
            for event in attempt["atomic_execution"]["operation"]["events"]:
                payload = event["payload"]
                if event["type"] in {"HOUSE_BUILT", "HOTEL_BUILT"}:
                    kind = "HOUSE" if event["type"] == "HOUSE_BUILT" else "HOTEL"
                    actual[(index_keys[payload["space_index"]], kind)] += payload.get("count", 1)
                if event["type"] == "CASH_CHANGED" and payload.get("reason") == "BUILD" and payload.get("player_id") == case["actor"]:
                    debit -= payload["delta"]
            if actual != target or debit != attempt["target_cost"]:
                errors.append([case["case_id"], "construction_events", attempt["attempt_index"]])
            event_witnesses_checked += 1
    result = {
        "source_files_hashed": source_files_checked,
        "source_line_hashes_checked": 2 * len(cases),
        "source_case_count": len(observed),
        "cases_by_kind": dict(Counter(c[2] for c in observed)),
        "attempt_records_checked": attempts_checked,
        "errors": errors,
        "default_decisions_by_game": dict(sorted(default_games.items(), key=lambda x: int(x[0]))),
        "default_decisions_by_model": dict(default_models),
        "well_formed_target_attempts": len(target_attempts),
        "unique_deed_kind_count_multisets": len(target_patterns),
        "most_frequent_multiset_count": max(target_patterns.values()),
        "construction_witness_event_multisets_and_debits_checked": event_witnesses_checked,
        "multiset_count_limit": "Repeated targets can begin at different states; this is not a count of independent errors.",
        "figure_rows_accessible_equals_full": sum(x["accessible"] == x["full"] for x in figures),
        "full_reproduced_json_equals_expected": report == read(PACKAGE / "results.json"),
    }
    (HERE / "claim_count_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
