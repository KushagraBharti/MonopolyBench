from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


ANALYSIS = Path(__file__).resolve().parents[1]
SAVED = ANALYSIS.parent
RUN = SAVED / "run"
QUALITY_CHECK = SAVED / "quality_check"
REVIEW = ANALYSIS / "review"
ZIP_PATH = SAVED / f"{SAVED.name}-analysis.zip"
REPORT_PATH = ANALYSIS / "quality" / "qualitative_review_validation.json"
RUN_ID = "mock-44910-42ec35c5"
EXPECTED_RUN_TREE = "25524577aa9ec7754151d9997627cec1280bf0255293085d59670bb617477f50"
EXPECTED_QC_TREE = "ff2e7c006d723b85936e530b13b779b55922a3082fd32ac97ccf32457e6663d1"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: object required")
            rows.append(value)
    return rows


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_tree(artifact_set: dict[str, Any], base: Path, errors: list[str]) -> str:
    actual = {
        path.relative_to(base).as_posix()
        for path in base.rglob("*")
        if path.is_file()
    }
    expected = {item["relative_path"] for item in artifact_set["files"]}
    if actual != expected:
        errors.append(f"{base.name} source path set differs from frozen inventory")
    lines: list[str] = []
    for item in artifact_set["files"]:
        path = base / item["relative_path"]
        if (
            not path.is_file()
            or path.stat().st_size != item["bytes"]
            or sha256(path) != item["sha256"]
        ):
            errors.append(f"frozen source mismatch: {base.name}/{item['relative_path']}")
        lines.append(f"{item['relative_path']}\t{item['sha256']}\t{item['bytes']}\n")
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_case_studies(errors: list[str]) -> tuple[int, list[str]]:
    text = (ANALYSIS / "reports" / "case_studies.md").read_text(encoding="utf-8")
    sections = re.split(r"(?m)^## (?=CS-\d{2}\b)", text)[1:]
    required_fields = [
        "Mechanism",
        "Exact turn range",
        "Actors",
        "Pre-state",
        "Chronological decision/action/event/message chain",
        "Exact source IDs and paths",
        "Public/private comparison",
        "Economic consequences",
        "Strategic interpretation",
        "Deception/collusion/promise labels, confidence, epistemic boundary",
        "Plausible legal alternatives",
        "Downstream effects",
        "Limitations",
        "Evidence-index/review-packet links",
    ]
    ids: list[str] = []
    for section in sections:
        heading = section.splitlines()[0]
        match = re.match(r"(CS-\d{2})\b", heading)
        if not match:
            errors.append(f"malformed case-study heading: {heading}")
            continue
        ids.append(match.group(1))
        for field in required_fields:
            if f"**{field}:**" not in section:
                errors.append(f"{match.group(1)} missing required field {field}")
    require(len(sections) == 10, f"expected 10 case studies, found {len(sections)}", errors)
    require(len(ids) == len(set(ids)), "duplicate case-study IDs", errors)
    return len(sections), ids


def check_turn_blocks(
    coverage: list[dict[str, str]], errors: list[str]
) -> tuple[int, list[dict[str, int]]]:
    text = (REVIEW / "chronological_turn_review.md").read_text(encoding="utf-8")
    matches = re.findall(
        r"<!-- review_block id=(TR-\d{3}-\d{3}) start=(\d+) end=(\d+) decision_count=(\d+) -->",
        text,
    )
    blocks: list[dict[str, int]] = []
    expected_start = 0
    coverage_counts = Counter(row["review_block_id"] for row in coverage)
    for block_id, start_text, end_text, count_text in matches:
        start, end, declared = int(start_text), int(end_text), int(count_text)
        require(start == expected_start, f"turn-block gap/overlap before {block_id}", errors)
        require(1 <= end - start + 1 <= 3, f"{block_id} exceeds three turns", errors)
        require(block_id == f"TR-{start:03d}-{end:03d}", f"{block_id} range/name mismatch", errors)
        require(
            coverage_counts[block_id] == declared,
            f"{block_id} decision count mismatch",
            errors,
        )
        blocks.append({"block_id": block_id, "start": start, "end": end, "decision_count": declared})
        expected_start = end + 1
    require(len(blocks) == 91, f"expected 91 turn blocks, found {len(blocks)}", errors)
    require(expected_start == 273, f"turn-block coverage ends at {expected_start - 1}, not 272", errors)
    require(
        set(coverage_counts) == {block["block_id"] for block in blocks},
        "decision coverage references unknown/missing review blocks",
        errors,
    )
    chronological_ids = re.findall(
        rf"\*\*Decision `({re.escape(RUN_ID)}-dec-\d{{6}})`",
        text,
    )
    coverage_ids = [row["decision_id"] for row in coverage]
    require(
        len(chronological_ids) == 540
        and len(chronological_ids) == len(set(chronological_ids)),
        "chronological review does not contain exactly 540 unique decision sections",
        errors,
    )
    require(
        set(chronological_ids) == set(coverage_ids),
        "chronological decision sections and decision_coverage.csv are not bijective",
        errors,
    )
    events = load_jsonl(RUN / "events.jsonl")
    started = [e["turn_index"] for e in events if e["type"] == "TURN_STARTED"]
    ended = [e["turn_index"] for e in events if e["type"] == "TURN_ENDED"]
    require(started == list(range(273)), "TURN_STARTED domain is not exactly 0..272", errors)
    require(ended == list(range(273)), "TURN_ENDED domain is not exactly 0..272", errors)
    terminal = [e for e in events if e["type"] == "GAME_ENDED"]
    require(
        len(terminal) == 1
        and terminal[0]["turn_index"] == 273
        and terminal[0]["event_id"] == f"{RUN_ID}-evt-004101",
        "terminal-only turn 273 marker mismatch",
        errors,
    )
    return len(blocks), blocks


def check_decisions(
    coverage: list[dict[str, str]], packets: list[dict[str, Any]], errors: list[str]
) -> dict[str, int]:
    raw_decisions = load_jsonl(RUN / "decisions.jsonl")
    starts = {row["decision_id"]: row for row in raw_decisions if row["phase"] == "decision_started"}
    resolved = {row["decision_id"]: row for row in raw_decisions if row["phase"] == "decision_resolved"}
    actions = {row["decision_id"]: row for row in load_jsonl(RUN / "actions.jsonl")}
    coverage_ids = [row["decision_id"] for row in coverage]
    require(len(coverage) == 540, f"decision coverage rows={len(coverage)}, expected 540", errors)
    require(len(coverage_ids) == len(set(coverage_ids)), "duplicate decision coverage ID", errors)
    require(set(coverage_ids) == set(starts) == set(resolved) == set(actions), "decision/action coverage is not bijective", errors)

    attempts = sum(len(row["attempts"]) for row in resolved.values())
    retries = {did for did, row in resolved.items() if row["retry_used"]}
    invalid_attempts = sum(
        1
        for row in resolved.values()
        for attempt in row["attempts"]
        if attempt["outcome"] != "valid"
    )
    fallbacks = sum(1 for row in resolved.values() if row["fallback_used"])
    expected_retry_ids = {
        f"{RUN_ID}-dec-{value:06d}"
        for value in (129, 140, 159, 184, 220, 234, 242, 292, 443)
    }
    require(attempts == 549, f"attempt count={attempts}, expected 549", errors)
    require(retries == expected_retry_ids, f"retry decision IDs mismatch: {sorted(retries)}", errors)
    require(invalid_attempts == 9, f"invalid attempt count={invalid_attempts}, expected 9", errors)
    require(fallbacks == 0, f"fallback count={fallbacks}, expected 0", errors)
    require(
        sum(int(row["attempt_count"]) for row in coverage) == 549,
        "coverage attempt-count sum mismatch",
        errors,
    )
    require(
        {row["decision_id"] for row in coverage if int(row["retry_count"]) == 1} == retries,
        "coverage retry rows mismatch raw retry decisions",
        errors,
    )
    require(
        all(int(row["fallback_count"]) == 0 and row["fallback_status"] == "none" for row in coverage),
        "coverage contains a fallback",
        errors,
    )
    for row in coverage:
        did = row["decision_id"]
        require(row["action_id"] == f"action:{did}", f"{did} action ID mismatch", errors)
        require(row["action_type"] == actions[did]["action"]["action"], f"{did} action type mismatch", errors)
        require(int(row["turn_index"]) == resolved[did]["turn_index"], f"{did} turn mismatch", errors)
        require(row["player_id"] == resolved[did]["player_id"], f"{did} player mismatch", errors)
        require(int(row["attempt_count"]) == len(resolved[did]["attempts"]), f"{did} attempt mismatch", errors)

    decision_packets = [packet for packet in packets if packet.get("packet_type") == "decision"]
    packet_ids = [packet.get("decision_id") for packet in decision_packets]
    require(len(decision_packets) == 540, f"decision packets={len(decision_packets)}, expected 540", errors)
    require(len(packet_ids) == len(set(packet_ids)), "duplicate decision packet", errors)
    require(set(packet_ids) == set(resolved), "decision packet IDs mismatch", errors)
    return {
        "decision_starts": len(starts),
        "resolved_decisions": len(resolved),
        "actions": len(actions),
        "attempts": attempts,
        "retry_decisions": len(retries),
        "invalid_attempts": invalid_attempts,
        "fallbacks": fallbacks,
    }


def check_evidence(
    evidence: list[dict[str, str]],
    coverage: list[dict[str, str]],
    packets: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, int]:
    ids = [row["evidence_id"] for row in evidence]
    require(len(ids) == len(set(ids)), "duplicate evidence ID", errors)
    path_locators = [(row["run_relative_source_path"], row["source_locator"]) for row in evidence]
    require(len(path_locators) == len(set(path_locators)), "duplicate evidence path+locator", errors)
    events = {row["event_id"]: row for row in load_jsonl(RUN / "events.jsonl")}
    decisions = load_jsonl(RUN / "decisions.jsonl")
    decision_keys = {(row["decision_id"], row["phase"]) for row in decisions}
    actions = {row["decision_id"] for row in load_jsonl(RUN / "actions.jsonl")}

    for row in evidence:
        rel = row["run_relative_source_path"]
        path = SAVED / rel
        require(path.is_file(), f"evidence path missing: {rel}", errors)
        require(
            row["resolution_status"].startswith("resolved_"),
            f"evidence unresolved: {row['evidence_id']}",
            errors,
        )
        if row["artifact_type"] == "event":
            obj = events.get(row["source_object_id"])
            require(obj is not None, f"event evidence object missing: {row['evidence_id']}", errors)
            if obj is not None:
                require(str(obj["seq"]) == row["source_sequence"], f"event sequence mismatch: {row['evidence_id']}", errors)
        elif row["artifact_type"] in {"decision_start", "decision_resolution"}:
            phase = "decision_started" if row["artifact_type"] == "decision_start" else "decision_resolved"
            require((row["source_object_id"], phase) in decision_keys, f"decision evidence missing: {row['evidence_id']}", errors)
        elif row["artifact_type"] == "action":
            require(row["source_object_id"] in actions, f"action evidence missing: {row['evidence_id']}", errors)

    evidence_ids = set(ids)
    citation_files = [
        *ANALYSIS.rglob("*.md"),
        REVIEW / "decision_coverage.csv",
        REVIEW / "communication_claims.csv",
        REVIEW / "promise_lifecycle.csv",
        REVIEW / "review_packet.jsonl",
    ]
    cited: set[str] = set()
    for path in citation_files:
        if path.is_file():
            cited.update(re.findall(r"\[EVIDENCE:([^\]]+)\]", path.read_text(encoding="utf-8")))
    missing = sorted(cited - evidence_ids)
    require(not missing, f"unresolved EVIDENCE citations: {missing[:20]}", errors)

    structured_refs: set[str] = set()
    for row in coverage:
        structured_refs.update(json.loads(row["evidence_references"]))
    for packet in packets:
        structured_refs.update(packet.get("evidence_references", []))
    missing_structured = sorted(structured_refs - evidence_ids)
    require(not missing_structured, f"unresolved structured evidence refs: {missing_structured[:20]}", errors)
    return {
        "evidence_rows": len(evidence),
        "markdown_citations": len(cited),
        "structured_evidence_references": len(structured_refs),
    }


def check_bankruptcies(packets: list[dict[str, Any]], errors: list[str]) -> dict[str, Any]:
    expected = {
        "OpenAI GPT 5.4 Mini": f"{RUN_ID}-evt-002066",
        "Claude Haiku 4.5": f"{RUN_ID}-evt-002850",
        "Grok 4.3": f"{RUN_ID}-evt-004098",
    }
    events = load_jsonl(RUN / "events.jsonl")
    found = {
        row["payload"].get("player_id"): row["event_id"]
        for row in events
        if row["type"] == "CASH_CHANGED" and row["payload"].get("reason") == "BANKRUPTCY"
    }
    require(found == expected, f"bankruptcy events mismatch: {found}", errors)
    episode_packets = [
        packet for packet in packets if packet.get("packet_type") == "bankruptcy_window"
    ]
    require(len(episode_packets) == 3, f"bankruptcy packets={len(episode_packets)}, expected 3", errors)
    text = (REVIEW / "bankruptcy_windows.md").read_text(encoding="utf-8")
    headings = re.findall(r"(?m)^## (BW-[A-Z]+) · .*? · turns (\d+)–(\d+)", text)
    require(len(headings) == 3, f"bankruptcy windows={len(headings)}, expected 3", errors)
    for event_id in expected.values():
        require(text.count(event_id) >= 1, f"bankruptcy window omits {event_id}", errors)
    return {"events": expected, "windows": len(headings)}


def check_communications(errors: list[str]) -> dict[str, int]:
    claims = load_csv(REVIEW / "communication_claims.csv")
    claim_ids = [row["claim_id"] for row in claims]
    decision_ids = [row["decision_id"] for row in claims]
    require(len(claims) == 540, f"communication claims={len(claims)}, expected 540", errors)
    require(len(claim_ids) == len(set(claim_ids)), "duplicate communication claim ID", errors)
    require(len(decision_ids) == len(set(decision_ids)), "duplicate communication decision ID", errors)
    require(
        sum(row["deception_candidate_label"] == "D2_candidate" for row in claims) == 1,
        "expected exactly one D2_candidate",
        errors,
    )
    require(
        not any(row["deception_candidate_label"] in {"D3", "D4"} for row in claims),
        "unsupported D3/D4 label present",
        errors,
    )
    require(
        not any(row["collusion_candidate_label"] in {"C2", "C3", "C4"} for row in claims),
        "unsupported C2-C4 label present",
        errors,
    )
    promises = load_csv(REVIEW / "promise_lifecycle.csv")
    require(len(promises) == 4, f"promise lifecycle rows={len(promises)}, expected 4", errors)
    require(
        any(row["promise_id"] == "PROMISE-NONE-EXPLICIT-INTERPERSONAL" for row in promises),
        "explicit no-interpersonal-promise sentinel missing",
        errors,
    )
    return {"claim_rows": len(claims), "promise_rows": len(promises)}


def check_packets(packets: list[dict[str, Any]], errors: list[str]) -> dict[str, int]:
    ids = [packet["packet_id"] for packet in packets]
    require(len(ids) == len(set(ids)), "duplicate review packet ID", errors)
    types = Counter(packet["packet_type"] for packet in packets)
    expected = {
        "decision": 540,
        "trade_episode": 44,
        "auction_episode": 8,
        "mortgage_episode": 31,
        "bankruptcy_window": 3,
    }
    require(types == expected, f"review packet type counts mismatch: {dict(types)}", errors)
    for packet in packets:
        for field in ("source_pointers", "observations", "labels", "confidence", "epistemic_limits", "cross_links"):
            require(field in packet, f"{packet['packet_id']} missing {field}", errors)
    return dict(types)


def check_replay_and_cost(errors: list[str]) -> dict[str, Any]:
    replay = load_json(ANALYSIS / "quality" / "replay_verification.json")
    state = replay["state_replay"]
    artifact = replay["artifact_replay"]
    require(state["status"] == "passed", "state replay status is not passed", errors)
    require(state["original_compared_event_count"] == state["replay_compared_event_count"] == 1942, "state replay count is not 1,942/1,942", errors)
    require(artifact["status"] == "passed", "artifact replay status is not passed", errors)
    require(artifact["original_compared_event_count"] == artifact["replay_compared_event_count"] == 4102, "artifact replay count is not 4,102/4,102", errors)
    calls = load_json(ANALYSIS / "quality" / "call_reconciliation.json")
    usage = calls["usage_reconciliation"]
    require(usage["attempt_sums"]["cost"] == "4.24475240", "exact Decimal cost changed", errors)
    require(
        str(usage["usage_json_totals"]["cost"]) == "4.244752400000001",
        "aggregate JSON cost changed",
        errors,
    )
    require(calls["counts"]["missing_usage_attempts"] == 0, "provider usage is missing", errors)
    return {
        "state_replay": "1942/1942 passed",
        "artifact_replay": "4102/4102 passed",
        "attempt_decimal_cost": "4.24475240",
        "aggregate_json_cost": "4.244752400000001",
    }


def check_parseability(errors: list[str]) -> dict[str, int]:
    counts = Counter()
    for path in ANALYSIS.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ANALYSIS).as_posix()
        if path.suffix == ".json":
            load_json(path)
            counts["json"] += 1
        elif path.suffix == ".jsonl":
            load_jsonl(path)
            counts["jsonl"] += 1
        elif path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as handle:
                list(csv.reader(handle))
            counts["csv"] += 1
        elif path.suffix == ".png":
            data = path.read_bytes()
            require(data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24, f"invalid PNG signature: {rel}", errors)
            if len(data) >= 24:
                width, height = struct.unpack(">II", data[16:24])
                require(width >= 100 and height >= 100, f"invalid PNG dimensions: {rel} {width}x{height}", errors)
            counts["png"] += 1
    return dict(counts)


def check_manifests_and_zip(errors: list[str]) -> dict[str, Any]:
    manifest = load_json(ANALYSIS / "manifests" / "analysis_manifest.json")
    excluded = {item["path"] for item in manifest["exclusions"]}
    expected = {item["path"]: item for item in manifest["generated_files"]}
    actual = {
        path.relative_to(ANALYSIS).as_posix(): path
        for path in ANALYSIS.rglob("*")
        if path.is_file() and path.relative_to(ANALYSIS).as_posix() not in excluded
    }
    require(set(actual) == set(expected), "analysis manifest path set mismatch", errors)
    lines: list[str] = []
    for rel, item in expected.items():
        path = actual.get(rel)
        if path is not None:
            require(path.stat().st_size == item["bytes"] and sha256(path) == item["sha256"], f"analysis manifest hash mismatch: {rel}", errors)
        lines.append(f"{rel}\t{item['sha256']}\t{item['bytes']}\n")
    tree = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
    require(tree == manifest["generated_tree_sha256"], "analysis generated-tree hash mismatch", errors)

    qual = load_json(ANALYSIS / "manifests" / "qualitative_review_manifest.json")
    for item in qual["output_inventory"]:
        path = ANALYSIS / item["path"]
        require(path.is_file(), f"qualitative manifest path missing: {item['path']}", errors)
        if path.is_file():
            require(path.stat().st_size == item["bytes"] and sha256(path) == item["sha256"], f"qualitative manifest hash mismatch: {item['path']}", errors)

    analysis_files = {
        path.relative_to(SAVED).as_posix(): path
        for path in ANALYSIS.rglob("*")
        if path.is_file()
    }
    require(ZIP_PATH.is_file(), "analysis ZIP missing", errors)
    if ZIP_PATH.is_file():
        with zipfile.ZipFile(ZIP_PATH) as archive:
            require(archive.testzip() is None, "analysis ZIP CRC failure", errors)
            names = [item.filename for item in archive.infolist() if not item.is_dir()]
            require(len(names) == len(set(names)), "analysis ZIP has duplicate entries", errors)
            require(set(names) == set(analysis_files), "analysis ZIP path set mismatch", errors)
            for rel, path in analysis_files.items():
                if rel in names:
                    require(archive.read(rel) == path.read_bytes(), f"analysis ZIP byte mismatch: {rel}", errors)
        saved_manifest = load_json(SAVED / "saved_game_manifest.json")
        zip_record = saved_manifest["zip_validation"]
        require(zip_record["sha256"] == sha256(ZIP_PATH), "saved manifest ZIP SHA mismatch", errors)
        require(zip_record["bytes"] == ZIP_PATH.stat().st_size, "saved manifest ZIP size mismatch", errors)
        require(zip_record["file_count"] == len(analysis_files), "saved manifest ZIP file-count mismatch", errors)
    return {
        "generated_manifest_consistency": "pass",
        "generated_files": len(expected),
        "zip_files": len(analysis_files),
        "zip_sha256_record": "../saved_game_manifest.json#/zip_validation/sha256",
        "zip_crc": "pass" if ZIP_PATH.is_file() else "not_checked",
        "zip_entry_content_parity": ZIP_PATH.is_file() and not errors,
    }


def validate(include_package: bool) -> dict[str, Any]:
    errors: list[str] = []
    required = [
        "README.md",
        "review/chronological_turn_review.md",
        "review/player_dossiers.md",
        "review/bankruptcy_windows.md",
        "review/negotiation_review.md",
        "review/decision_coverage.csv",
        "review/evidence_index.csv",
        "review/review_packet.jsonl",
        "review/communication_claims.csv",
        "review/promise_lifecycle.csv",
        "reports/manual_review_report.md",
        "reports/case_studies.md",
        "reports/integrity_report.md",
        "quality/qualitative_review_validation.json",
        "quality/unified_contract_validation.json",
        "manifests/qualitative_review_manifest.json",
        "manifests/unified_qualitative_contract.json",
        "tools/validate_qualitative_review.py",
    ]
    for rel in required:
        if not include_package and rel in {
            "quality/qualitative_review_validation.json",
            "manifests/qualitative_review_manifest.json",
        }:
            continue
        path = ANALYSIS / rel
        require(path.is_file() and path.stat().st_size > 0, f"required output missing/empty: {rel}", errors)

    coverage = load_csv(REVIEW / "decision_coverage.csv")
    evidence = load_csv(REVIEW / "evidence_index.csv")
    packets = load_jsonl(REVIEW / "review_packet.jsonl")
    turn_count, blocks = check_turn_blocks(coverage, errors)
    decision_counts = check_decisions(coverage, packets, errors)
    evidence_counts = check_evidence(evidence, coverage, packets, errors)
    packet_counts = check_packets(packets, errors)
    bankruptcy = check_bankruptcies(packets, errors)
    communication = check_communications(errors)
    case_count, case_ids = check_case_studies(errors)
    replay = check_replay_and_cost(errors)
    parsed = check_parseability(errors)

    source_manifest = load_json(ANALYSIS / "manifests" / "source_artifact_hashes.json")
    run_tree = source_tree(source_manifest["artifact_sets"]["run"], RUN, errors)
    qc_tree = source_tree(source_manifest["artifact_sets"]["quality_check"], QUALITY_CHECK, errors)
    require(run_tree == EXPECTED_RUN_TREE, "run tree SHA-256 changed", errors)
    require(qc_tree == EXPECTED_QC_TREE, "quality_check tree SHA-256 changed", errors)

    package = {"status": "deferred_by_prepackage_mode"}
    if include_package:
        package = check_manifests_and_zip(errors)

    return {
        "schema_version": "qualitative_review_validation_v1",
        "run_id": RUN_ID,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "checks": {
            "required_contract_files": "pass",
            "authoritative_turn_domain": {"playable": "0..272", "terminal_only": 273},
            "turn_blocks": {"count": turn_count, "ranges": blocks, "maximum_block_size": 3},
            "decision_action_attempt_coverage": decision_counts,
            "review_packets": packet_counts,
            "evidence_resolution": evidence_counts,
            "bankruptcies": bankruptcy,
            "communications_and_promises": communication,
            "case_studies": {"count": case_count, "ids": case_ids},
            "known_replay_and_cost": replay,
            "parseability": parsed,
            "source_tree_stability": {
                "run": run_tree,
                "quality_check": qc_tree,
                "status": "pass" if run_tree == EXPECTED_RUN_TREE and qc_tree == EXPECTED_QC_TREE else "fail",
            },
            "generated_manifest_and_zip": package,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prepackage",
        action="store_true",
        help="Skip generated-manifest and ZIP checks while final outputs are being assembled.",
    )
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write analysis/quality/qualitative_review_validation.json.",
    )
    args = parser.parse_args()
    result = validate(include_package=not args.prepackage)
    if args.write_report:
        REPORT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
