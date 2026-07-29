#!/usr/bin/env python3
"""Validate the exhaustive qualitative-review contract for legacy run 191."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
import traceback
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "analysis"
RUN_ID = "mock-83265-81ed4937"
ZIP_PATH = ROOT / "frontier-191-mock-83265-81ed4937-openai-gpt-5-5-analysis.zip"
REQUIRED = [
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
DECISION_FIELDS = [
    "decision_id",
    "turn_index",
    "turn_decision_ordinal",
    "player_id",
    "decision_type",
    "action_id",
    "action_type",
    "action_args_json",
    "resolution_status",
    "valid",
    "attempt_count",
    "invalid_attempt_count",
    "retry_count",
    "retry_status",
    "fallback_used",
    "fallback_reason",
    "event_seq_start",
    "event_seq_end",
    "event_ids_json",
    "decision_started_sources_json",
    "decision_resolved_source",
    "action_source",
    "attempt_sources_json",
    "prompt_response_sources_json",
    "snapshot_source",
    "review_block_id",
    "mechanism_tags_json",
    "has_public_message",
    "has_private_thought",
    "qualitative_synopsis",
    "evidence_ids_json",
]
EVIDENCE_FIELDS = [
    "evidence_id",
    "artifact_type",
    "provenance",
    "source_path",
    "locator_type",
    "locator",
    "source_object_id",
    "source_sequence",
    "source_turn",
    "source_attempt",
    "description",
    "referenced_outputs_json",
    "referenced_sections_json",
    "resolution_status",
]
FROZEN = {
    "run": (3835, 66557598, "d14d8c74621416ba87bfeca9e66527f27976de4a7847ba8fcb36b360fd15a79e"),
    "quality_check": (1208, 15411551, "2d0572f2f20f65d3f5790fca212791a000bfddcb0b87a56db18bbe63c0cd9de0"),
    "combined": (5043, 81969149, "5b5a35d4d9497a1c23d2d1fb56d230993d545be3d18d4641b727ac789f3fcc64"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise AssertionError(f"{path}:{number}: {exc}") from exc
    return rows


def load_csv(path: Path, expected: list[str] | None = None) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if expected is not None:
            missing = [field for field in expected if field not in (reader.fieldnames or [])]
            assert not missing, (path, reader.fieldnames, missing)
        rows = list(reader)
        assert all(None not in row for row in rows), f"ragged CSV: {path}"
        return rows


def tree(root: Path) -> tuple[int, int, str]:
    rows = []
    total = 0
    for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        total += size
        rows.append(f"{relative}\0{sha256(path)}\n")
    return len(rows), total, hashlib.sha256("".join(rows).encode()).hexdigest()


def combined_tree(run_hash: str, quality_hash: str) -> str:
    return hashlib.sha256(f"run\0{run_hash}\nquality_check\0{quality_hash}\n".encode()).hexdigest()


def png_info(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"bad PNG signature: {path}"
    assert data[12:16] == b"IHDR", f"missing IHDR: {path}"
    return struct.unpack(">II", data[16:24])


def zip_check() -> dict[str, Any]:
    expected = sorted(f"analysis/{p.relative_to(ANALYSIS).as_posix()}" for p in ANALYSIS.rglob("*") if p.is_file())
    assert ZIP_PATH.exists(), f"missing ZIP: {ZIP_PATH}"
    with zipfile.ZipFile(ZIP_PATH) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)), "duplicate ZIP members"
        assert names == expected, "ZIP member order/set differs from analysis tree"
        assert archive.testzip() is None, "ZIP CRC failure"
        for info in archive.infolist():
            assert info.date_time == (1980, 1, 1, 0, 0, 0), (info.filename, info.date_time)
            assert info.compress_type == zipfile.ZIP_DEFLATED, (info.filename, info.compress_type)
            assert (info.external_attr >> 16) == 0o100644, (info.filename, oct(info.external_attr >> 16))
            disk = ANALYSIS / info.filename.removeprefix("analysis/")
            assert archive.read(info.filename) == disk.read_bytes(), f"ZIP byte mismatch: {info.filename}"
    return {
        "status": "pass",
        "entry_count": len(expected),
        "bytes": ZIP_PATH.stat().st_size,
        "sha256": sha256(ZIP_PATH),
        "crc": "pass",
        "exact_path_order_and_content_parity": "pass",
        "fixed_metadata": "pass",
    }


def run_validation(check_archive: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        contract_missing = [path for path in REQUIRED if not (ANALYSIS / path).is_file()]
        assert not contract_missing, contract_missing

        actions = load_jsonl(ROOT / "run/actions.jsonl")
        decisions_raw = load_jsonl(ROOT / "run/decisions.jsonl")
        resolved = [row for row in decisions_raw if row["phase"] == "decision_resolved"]
        events = load_jsonl(ROOT / "run/events.jsonl")
        coverage = load_csv(ANALYSIS / "review/decision_coverage.csv", DECISION_FIELDS)
        evidence = load_csv(ANALYSIS / "review/evidence_index.csv", EVIDENCE_FIELDS)
        packets = load_jsonl(ANALYSIS / "review/review_packet.jsonl")
        claims = load_csv(ANALYSIS / "review/communication_claims.csv")
        promises = load_csv(ANALYSIS / "review/promise_lifecycle.csv")

        action_ids = [row["decision_id"] for row in actions]
        resolved_ids = [row["decision_id"] for row in resolved]
        coverage_ids = [row["decision_id"] for row in coverage]
        packet_decisions = [row for row in packets if row.get("record_type") == "decision"]
        packet_ids = [row["decision_id"] for row in packet_decisions]
        assert len(actions) == len(resolved) == len(coverage) == len(packet_decisions) == 583
        assert len(set(action_ids)) == len(set(resolved_ids)) == len(set(coverage_ids)) == len(set(packet_ids)) == 583
        assert set(action_ids) == set(resolved_ids) == set(coverage_ids) == set(packet_ids)
        assert all(row["action_id"] == row["decision_id"] for row in coverage)
        assert all(row["resolution_status"] == "applied" for row in coverage)

        attempt_count = sum(len(row["attempts"]) for row in resolved)
        retry_decisions = sum(bool(row["retry_used"]) for row in resolved)
        invalid_attempts = sum(
            attempt["outcome"] != "valid" for row in resolved for attempt in row["attempts"]
        )
        fallbacks = sum(bool(row["fallback_used"]) for row in resolved)
        assert (attempt_count, retry_decisions, invalid_attempts, fallbacks) == (604, 21, 23, 2)
        assert sum(int(row["attempt_count"]) for row in coverage) == 604
        assert sum(int(row["invalid_attempt_count"]) for row in coverage) == 23
        assert sum(row["retry_status"] == "retried" for row in coverage) == 21
        assert sum(row["fallback_used"] == "true" for row in coverage) == 2

        turns = sorted({int(row["turn_index"]) for row in actions})
        assert turns[0] == 0 and turns[-1] == 190 and len(turns) <= 191
        turn_markers = [row for row in events if row["type"] == "TURN_STARTED"]
        assert [row["turn_index"] for row in turn_markers] == list(range(191))
        assert events[-1]["turn_index"] == 191 and events[-1]["type"] == "GAME_ENDED"

        manifest = json.loads((ANALYSIS / "manifests/qualitative_review_manifest.json").read_text(encoding="utf-8"))
        blocks = manifest["review_blocks"]
        assert len(blocks) == 64
        cursor = 0
        for block in blocks:
            assert block["turn_start"] == cursor
            assert block["turn_end"] >= block["turn_start"]
            assert block["turn_end"] - block["turn_start"] + 1 <= 3
            cursor = block["turn_end"] + 1
        assert cursor == 192
        chronology = (ANALYSIS / "review/chronological_turn_review.md").read_text(encoding="utf-8")
        headings = re.findall(r"^## (RB-(\d{3})-(\d{3})) · turns (\d+)–(\d+)$", chronology, re.M)
        assert len(headings) == 64
        assert [(int(a), int(b)) for _, a, b, _, _ in headings] == [
            (block["turn_start"], block["turn_end"]) for block in blocks
        ]
        assert all(row["review_block_id"] in {block["block_id"] for block in blocks} for row in coverage)

        bankruptcy_events = [
            row
            for row in events
            if row["type"] == "CASH_CHANGED" and row["payload"].get("reason") == "BANKRUPTCY"
        ]
        bankruptcy_packets = [row for row in packets if row.get("record_type") == "bankruptcy_window"]
        bankruptcy_doc = (ANALYSIS / "review/bankruptcy_windows.md").read_text(encoding="utf-8")
        assert len(bankruptcy_events) == len(bankruptcy_packets) == 3
        assert len(re.findall(r"^## BW-\d{2}", bankruptcy_doc, re.M)) == 3
        assert [row["seq"] for row in bankruptcy_events] == [2851, 3120, 3962]

        evidence_ids = [row["evidence_id"] for row in evidence]
        assert len(evidence_ids) == len(set(evidence_ids))
        evidence_set = set(evidence_ids)
        raw_event_ids = {row["event_id"] for row in events}
        raw_decision_ids = set(action_ids)
        for row in evidence:
            path = ROOT / row["source_path"] if row["provenance"] == "frozen_source" else ROOT / row["source_path"].removeprefix("analysis/")
            if row["provenance"] == "generated_review_record":
                path = ANALYSIS / row["source_path"].removeprefix("analysis/")
            assert path.exists(), (row["evidence_id"], row["source_path"])
        for row in coverage:
            assert set(json.loads(row["evidence_ids_json"])) <= evidence_set
            for path in json.loads(row["prompt_response_sources_json"]):
                assert (ROOT / path).is_file(), path
            assert (ROOT / row["snapshot_source"]).is_file()
        for packet in packets:
            assert set(filter(None, packet.get("evidence_ids", []))) <= evidence_set
        for claim in claims:
            assert set(json.loads(claim["evidence_ids_json"])) <= evidence_set
        for promise in promises:
            assert set(json.loads(promise["later_evidence_ids_json"])) <= evidence_set

        # Resolve all concrete evidence/raw IDs cited in final Markdown.
        markdown = "\n".join(path.read_text(encoding="utf-8") for path in ANALYSIS.rglob("*.md"))
        md_evidence = set(re.findall(r"\bE-(?:EVT|DEC|ACT|ATT)-\d{6}(?:-A\d+)?\b|\bE-STATE-\d{4}\b", markdown))
        assert md_evidence <= evidence_set, sorted(md_evidence - evidence_set)[:20]
        cited_events = set(re.findall(r"\bmock-83265-81ed4937-evt-\d{6}\b", markdown))
        cited_decisions = set(re.findall(r"\bmock-83265-81ed4937-dec-\d{6}\b", markdown))
        assert cited_events <= raw_event_ids
        assert cited_decisions <= raw_decision_ids

        cases = (ANALYSIS / "reports/case_studies.md").read_text(encoding="utf-8")
        case_chunks = re.split(r"(?=^## CS-\d{3} — )", cases, flags=re.M)[1:]
        assert len(case_chunks) >= 1
        case_ids = []
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
            "Deception/collusion/promise labels",
            "Legal alternatives/counterfactual boundary",
            "Downstream effects",
            "Limitations",
            "Evidence-index/review-packet cross-links",
        ]
        for chunk in case_chunks:
            match = re.match(r"## (CS-\d{3}) — ", chunk)
            assert match
            case_ids.append(match.group(1))
            for field in required_fields:
                assert f"| {field} |" in chunk, (match.group(1), field)
            assert "Confidence" in chunk or "confidence" in chunk
            assert "Epistemic" in chunk or "epistemic" in chunk
        assert len(case_ids) == len(set(case_ids))

        assert len(claims) == 583 and len({row["claim_id"] for row in claims}) == 583
        assert {row["decision_id"] for row in claims} == set(action_ids)
        assert promises and len({row["promise_id"] for row in promises}) == len(promises)
        assert all(row["disposition"] for row in promises)

        run_tree = tree(ROOT / "run")
        quality_tree = tree(ROOT / "quality_check")
        assert run_tree == FROZEN["run"], run_tree
        assert quality_tree == FROZEN["quality_check"], quality_tree
        assert combined_tree(run_tree[2], quality_tree[2]) == FROZEN["combined"][2]

        generated = json.loads((ANALYSIS / "manifests/generated_output_hashes.json").read_text(encoding="utf-8"))
        generated_rows = generated["files"]
        excluded = set(generated["excluded_self_referential_paths"])
        actual_paths = sorted(
            path.relative_to(ANALYSIS).as_posix()
            for path in ANALYSIS.rglob("*")
            if path.is_file() and path.relative_to(ANALYSIS).as_posix() not in excluded
        )
        assert [row["relative_path"] for row in generated_rows] == actual_paths
        assert all(
            row["sha256"] == sha256(ANALYSIS / row["relative_path"])
            and int(row["bytes"]) == (ANALYSIS / row["relative_path"]).stat().st_size
            for row in generated_rows
        )
        generated_stream = "".join(f'{row["relative_path"]}\0{row["sha256"]}\n' for row in generated_rows)
        assert int(generated["file_count"]) == len(generated_rows)
        assert int(generated["total_bytes"]) == sum(int(row["bytes"]) for row in generated_rows)
        assert generated["tree_sha256"] == hashlib.sha256(generated_stream.encode()).hexdigest()

        pngs = list(ANALYSIS.rglob("*.png"))
        dimensions = {}
        for path in pngs:
            width, height = png_info(path)
            assert width >= 100 and height >= 100
            dimensions[path.relative_to(ANALYSIS).as_posix()] = [width, height]

        replay = json.loads((ANALYSIS / "quality/replay_verification.json").read_text(encoding="utf-8"))
        assert replay["expected_known_result"] == "state_passed_artifact_failed"
        assert replay["replay_report"]["status"] == "state_passed_artifact_failed"
        serialized = json.dumps(replay, sort_keys=True)
        assert "mock-83265-81ed4937-evt-000669" in serialized
        assert "mock-83265-81ed4937-dec-000096" in serialized
        assert "fallback:illogical_after_retry" in serialized
        integrity = (ANALYSIS / "reports/integrity_report.md").read_text(encoding="utf-8")
        for needle in [
            "state_passed_artifact_failed",
            "1,640 state-relevant",
            "mock-83265-81ed4937-evt-000669",
            "mock-83265-81ed4937-dec-000096",
            'valid=false',
            'error="fallback:illogical_after_retry"',
            'valid=true',
            'error=null',
            "`missing_actions=0`",
            "`extra_actions=0`",
            "`decision_id_mismatch=false`",
        ]:
            assert needle in integrity, needle

        archive = zip_check() if check_archive else {
            "status": "pass_by_deterministic_construction_pending_check_only",
            "expected_entry_count": len([p for p in ANALYSIS.rglob("*") if p.is_file()]),
            "contract": "sorted fixed-metadata ZIP_DEFLATED, exact analysis/ byte parity",
        }
        result = {
            "schema_version": "qualitative_review_validation_v1",
            "run_id": RUN_ID,
            "status": "pass",
            "contract_files": {"status": "pass", "required_count": len(REQUIRED), "missing": []},
            "authoritative_turn_domain": {
                "status": "pass",
                "played_turn_min": 0,
                "played_turn_max": 190,
                "played_turn_count": 191,
                "terminal_checkpoint": 191,
                "snapshot_count": 192,
            },
            "serialization_validation": {
                "status": "pass",
                "decision_csv_rows": len(coverage),
                "evidence_csv_rows": len(evidence),
                "review_packet_rows": len(packets),
                "communication_claim_rows": len(claims),
                "promise_rows": len(promises),
            },
            "png_validation": {"status": "pass", "count": len(pngs), "dimensions": dimensions},
            "chronological_coverage": {
                "status": "pass",
                "block_count": len(blocks),
                "max_block_size": 3,
                "covered_checkpoints": 192,
                "gaps": [],
                "overlaps": [],
            },
            "decision_action_bijection": {
                "status": "pass",
                "decisions": 583,
                "actions": 583,
                "decision_packets": 583,
                "missing": [],
                "extra": [],
                "duplicates": [],
            },
            "attempt_reconciliation": {
                "status": "pass",
                "attempts": attempt_count,
                "retry_decisions": retry_decisions,
                "invalid_attempts": invalid_attempts,
                "fallbacks": fallbacks,
            },
            "bankruptcy_reconciliation": {
                "status": "pass",
                "event_count": 3,
                "window_count": 3,
                "event_sequences": [2851, 3120, 3962],
            },
            "citation_resolution": {
                "status": "pass",
                "evidence_rows": len(evidence),
                "unresolved": [],
                "duplicate_evidence_ids": [],
            },
            "case_study_validation": {
                "status": "pass",
                "case_count": len(case_ids),
                "case_ids": case_ids,
                "missing_fields": [],
            },
            "source_tree_stability": {
                "status": "pass",
                "run": {"file_count": run_tree[0], "bytes": run_tree[1], "tree_sha256": run_tree[2]},
                "quality_check": {
                    "file_count": quality_tree[0],
                    "bytes": quality_tree[1],
                    "tree_sha256": quality_tree[2],
                },
                "combined_tree_sha256": combined_tree(run_tree[2], quality_tree[2]),
            },
            "generated_manifest_consistency": {
                "status": "pass",
                "file_count": generated["file_count"],
                "total_bytes": generated["total_bytes"],
                "tree_sha256": generated["tree_sha256"],
                "excluded_paths": sorted(excluded),
            },
            "replay_status": {
                "status": "pass_exact_known_condition",
                "aggregate_status": "state_passed_artifact_failed",
                "state_relevant_events": 1640,
                "first_artifact_mismatch_sequence": 669,
                "event_id": "mock-83265-81ed4937-evt-000669",
                "decision_id": "mock-83265-81ed4937-dec-000096",
                "missing_actions": 0,
                "extra_actions": 0,
                "decision_id_mismatch": False,
            },
            "archive_parity": archive,
            "fresh_checkout_validation": {
                "status": "pending_external_check" if not check_archive else "check_only_current_tree_pass",
                "required_command": "python analysis/tools/validate_qualitative_review.py --check-only",
            },
            "errors": errors,
            "warnings": warnings,
        }
        return result
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
        return {
            "schema_version": "qualitative_review_validation_v1",
            "run_id": RUN_ID,
            "status": "fail",
            "errors": errors,
            "warnings": warnings,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write-report", action="store_true")
    group.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    result = run_validation(check_archive=args.check_only)
    if args.write_report:
        if result.get("archive_parity", {}).get("status") == "pass":
            result["archive_parity"].pop("bytes", None)
            result["archive_parity"].pop("sha256", None)
            result["archive_parity"]["hash_location"] = "saved_game_manifest.json#/analysis_zip/sha256"
            result["archive_parity"]["self_reference_boundary"] = (
                "The report records structural/byte-parity checks but not the archive hash because "
                "the report is itself an archive member; the external saved-game manifest stores the final hash."
            )
        path = ANALYSIS / "quality/qualitative_review_validation.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
