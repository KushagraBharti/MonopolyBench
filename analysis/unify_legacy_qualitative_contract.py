#!/usr/bin/env python3
"""Normalize the two legacy qualitative reviews to one machine-readable contract.

The per-game review builders intentionally remain package-local. This script is
the cross-package adapter: it preserves every existing value, adds lossless
aliases for fields named differently by the two builders, emits one ordered
superset schema, and writes a package-local contract/validation record.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
PACKAGES = (
    REPO / "saved_games/frontier-191-mock-83265-81ed4937-openai-gpt-5-5",
    REPO
    / "saved_games/frontier-mini-273-mock-44910-42ec35c5-gemini-3-flash-preview",
)

CSV_FIELDS = {
    "decision_coverage.csv": [
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
        "fallback_count",
        "fallback_status",
        "fallback_reason",
        "event_seq_start",
        "event_seq_end",
        "event_ids_json",
        "emitted_event_ids",
        "decision_started_sources_json",
        "decision_resolved_source",
        "decision_source_path",
        "decision_source_locator",
        "action_source",
        "action_source_path",
        "action_source_locator",
        "attempt_sources_json",
        "prompt_response_sources_json",
        "prompt_response_paths",
        "snapshot_source",
        "review_block_id",
        "mechanism_tags_json",
        "mechanism_tags",
        "has_public_message",
        "public_communication_flag",
        "has_private_thought",
        "private_thought_flag",
        "qualitative_synopsis",
        "evidence_ids_json",
        "evidence_references",
    ],
    "evidence_index.csv": [
        "evidence_id",
        "artifact_type",
        "provenance",
        "source_path",
        "run_relative_source_path",
        "locator_type",
        "locator",
        "source_locator",
        "source_object_id",
        "source_sequence",
        "source_turn",
        "source_attempt",
        "description",
        "referenced_outputs_json",
        "referenced_sections_json",
        "referenced_outputs_sections",
        "resolution_status",
    ],
    "communication_claims.csv": [
        "claim_id",
        "turn_index",
        "decision_id",
        "message_event_id",
        "speaker_player_id",
        "speaker",
        "audience_player_ids_json",
        "audience",
        "channel",
        "claim_type",
        "claim_content",
        "public_content",
        "private_content",
        "public_private_status",
        "public_evidence_id",
        "private_evidence_id",
        "private_comparison_evidence_id",
        "verifiability",
        "truth_status",
        "speaker_knowledge_support",
        "strategic_benefit",
        "intent_evidence",
        "harm_realized",
        "deception_candidate",
        "deception_candidate_label",
        "collusion_candidate",
        "collusion_candidate_label",
        "confidence",
        "benign_alternative",
        "outcome",
        "evidence_ids_json",
        "evidence_references",
        "cross_links_json",
        "cross_links",
        "adjudication_status",
        "epistemic_note",
    ],
    "promise_lifecycle.csv": [
        "promise_id",
        "creation_turn",
        "creation_decision_id",
        "creation_message_event_id",
        "creation_evidence",
        "promisor_player_id",
        "promisor",
        "promisee_player_ids_json",
        "promisee",
        "terms",
        "conditions",
        "deadline",
        "modifications_json",
        "modifications",
        "later_evidence_ids_json",
        "later_evidence",
        "condition_met",
        "earliest_due_turn",
        "latest_due_turn",
        "feasible_when_due",
        "disposition",
        "consequence",
        "confidence",
        "epistemic_note",
        "cross_links_json",
    ],
}

PACKET_FIELDS = [
    "schema_version",
    "packet_id",
    "packet_type",
    "record_type",
    "run_id",
    "decision_id",
    "episode_id",
    "turn_index",
    "turn_range",
    "review_block_id",
    "player_id",
    "actor_player_id",
    "actors",
    "decision_type",
    "visible_pre_state",
    "decision_start",
    "legal_actions",
    "chosen_action",
    "applied_action",
    "resolution",
    "attempts",
    "prompt_response_artifacts",
    "relevant_events",
    "source_pointers",
    "usage",
    "communications",
    "observations",
    "consequences",
    "mechanism",
    "mechanism_tags",
    "labels",
    "confidence",
    "epistemic_limits",
    "cross_links",
    "evidence_ids",
    "evidence_references",
]

REQUIRED_PATHS = [
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


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def json_array(value: str) -> str:
    if not value:
        return "[]"
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = [item for item in value.split("|") if item]
    if not isinstance(parsed, list):
        parsed = [parsed]
    return compact_json(parsed)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{number}: {exc}") from exc
    return rows


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def load_actions(package: Path) -> dict[str, dict[str, Any]]:
    return {
        row["decision_id"]: row
        for row in read_jsonl(package / "run/actions.jsonl")
    }


def load_event_sequences(package: Path) -> dict[str, int]:
    return {
        row["event_id"]: int(row["seq"])
        for row in read_jsonl(package / "run/events.jsonl")
    }


def normalize_decisions(package: Path, rows: list[dict[str, str]]) -> None:
    actions = load_actions(package)
    event_sequences = load_event_sequences(package)
    ordinals: dict[str, int] = {}
    for row in rows:
        turn = row.get("turn_index", "")
        ordinal = ordinals.get(turn, 0)
        ordinals[turn] = ordinal + 1
        row.setdefault("turn_decision_ordinal", str(ordinal))

        fallback_used = row.get("fallback_used", "").lower() == "true"
        if not row.get("fallback_count"):
            row["fallback_count"] = "1" if fallback_used else "0"
        if not row.get("fallback_status"):
            row["fallback_status"] = "used" if int(row["fallback_count"] or 0) else "none"
        if not row.get("fallback_used"):
            row["fallback_used"] = "true" if int(row["fallback_count"] or 0) else "false"

        did = row["decision_id"]
        action = actions.get(did, {})
        if not row.get("action_args_json"):
            row["action_args_json"] = compact_json(action.get("action", {}).get("args", {}))
        row.setdefault("resolution_status", "applied")
        row.setdefault("valid", "true")

        emitted = row.get("emitted_event_ids") or row.get("event_ids_json") or "[]"
        emitted = json_array(emitted)
        row["emitted_event_ids"] = emitted
        row["event_ids_json"] = emitted
        event_ids = json.loads(emitted)
        sequences = [event_sequences[event_id] for event_id in event_ids if event_id in event_sequences]
        if sequences:
            row.setdefault("event_seq_start", str(min(sequences)))
            row.setdefault("event_seq_end", str(max(sequences)))

        row.setdefault("decision_source_path", "run/decisions.jsonl")
        row.setdefault("decision_source_locator", f"decision_id={did}")
        row.setdefault(
            "decision_started_sources_json",
            compact_json(
                [f"run/decisions.jsonl#decision_id={did};phase=decision_started"]
            ),
        )
        row.setdefault(
            "decision_resolved_source",
            f"run/decisions.jsonl#decision_id={did};phase=decision_resolved",
        )
        row.setdefault("action_source_path", "run/actions.jsonl")
        row.setdefault("action_source_locator", f"decision_id={did}")
        row.setdefault("action_source", f"run/actions.jsonl#decision_id={did}")

        prompts = (
            row.get("prompt_response_sources_json")
            or row.get("prompt_response_paths")
            or "[]"
        )
        prompts = json_array(prompts)
        row["prompt_response_sources_json"] = prompts
        row["prompt_response_paths"] = prompts
        row.setdefault("attempt_sources_json", prompts)

        mechanisms = row.get("mechanism_tags_json") or row.get("mechanism_tags") or "[]"
        mechanisms = json_array(mechanisms)
        row["mechanism_tags_json"] = mechanisms
        row["mechanism_tags"] = mechanisms

        public = row.get("has_public_message") or row.get("public_communication_flag") or "false"
        private = row.get("has_private_thought") or row.get("private_thought_flag") or "false"
        row["has_public_message"] = public
        row["public_communication_flag"] = public
        row["has_private_thought"] = private
        row["private_thought_flag"] = private

        evidence = row.get("evidence_ids_json") or row.get("evidence_references") or "[]"
        evidence = json_array(evidence)
        row["evidence_ids_json"] = evidence
        row["evidence_references"] = evidence


def normalize_evidence(rows: list[dict[str, str]]) -> None:
    for row in rows:
        source = row.get("source_path") or row.get("run_relative_source_path") or ""
        row["source_path"] = source
        row["run_relative_source_path"] = source
        locator = row.get("locator") or row.get("source_locator") or ""
        row["locator"] = locator
        row["source_locator"] = locator
        row.setdefault("locator_type", "source_locator")
        row.setdefault(
            "provenance",
            "frozen_source"
            if source.startswith(("run/", "quality_check/"))
            else "generated_review_record",
        )
        refs = (
            row.get("referenced_outputs_json")
            or row.get("referenced_outputs_sections")
            or "[]"
        )
        refs = json_array(refs)
        row["referenced_outputs_json"] = refs
        row.setdefault("referenced_sections_json", refs)
        row["referenced_outputs_sections"] = refs


def normalize_claims(rows: list[dict[str, str]]) -> None:
    for row in rows:
        row["speaker"] = row.get("speaker") or row.get("speaker_player_id", "")
        row["speaker_player_id"] = row.get("speaker_player_id") or row.get("speaker", "")
        audience = row.get("audience_player_ids_json") or row.get("audience") or "[]"
        if not audience.startswith("["):
            audience = compact_json([audience])
        row["audience_player_ids_json"] = audience
        row["audience"] = audience
        row.setdefault("channel", "public")
        row["claim_content"] = row.get("claim_content") or row.get("public_content", "")
        row["public_content"] = row.get("public_content") or row.get("claim_content", "")
        row["private_comparison_evidence_id"] = (
            row.get("private_comparison_evidence_id")
            or row.get("private_evidence_id", "")
        )
        row["private_evidence_id"] = (
            row.get("private_evidence_id")
            or row.get("private_comparison_evidence_id", "")
        )
        row["public_evidence_id"] = (
            row.get("public_evidence_id") or row.get("message_event_id", "")
        )
        row["deception_candidate"] = (
            row.get("deception_candidate")
            or row.get("deception_candidate_label", "")
        )
        row["deception_candidate_label"] = (
            row.get("deception_candidate_label")
            or row.get("deception_candidate", "")
        )
        row["collusion_candidate"] = (
            row.get("collusion_candidate")
            or row.get("collusion_candidate_label", "")
        )
        row["collusion_candidate_label"] = (
            row.get("collusion_candidate_label")
            or row.get("collusion_candidate", "")
        )
        evidence = row.get("evidence_ids_json") or row.get("evidence_references") or "[]"
        evidence = json_array(evidence)
        row["evidence_ids_json"] = evidence
        row["evidence_references"] = evidence
        links = row.get("cross_links_json") or row.get("cross_links") or "[]"
        links = json_array(links)
        row["cross_links_json"] = links
        row["cross_links"] = links


def normalize_promises(rows: list[dict[str, str]]) -> None:
    for row in rows:
        row["creation_evidence"] = (
            row.get("creation_evidence")
            or row.get("creation_message_event_id")
            or row.get("creation_decision_id", "")
        )
        row["promisor"] = row.get("promisor") or row.get("promisor_player_id", "")
        row["promisor_player_id"] = (
            row.get("promisor_player_id") or row.get("promisor", "")
        )
        promisee = row.get("promisee_player_ids_json") or row.get("promisee") or "[]"
        if not promisee.startswith("["):
            promisee_json = compact_json([promisee])
        else:
            promisee_json = promisee
        row["promisee_player_ids_json"] = promisee_json
        row["promisee"] = row.get("promisee") or promisee_json
        modifications_json = row.get("modifications_json")
        if not modifications_json:
            modifications_json = (
                compact_json([row["modifications"]])
                if row.get("modifications")
                else "[]"
            )
        row["modifications_json"] = modifications_json
        row["modifications"] = row.get("modifications") or row["modifications_json"]
        evidence = row.get("later_evidence_ids_json") or row.get("later_evidence") or "[]"
        evidence_json = json_array(evidence)
        row["later_evidence_ids_json"] = evidence_json
        row["later_evidence"] = row.get("later_evidence") or evidence_json
        row.setdefault("cross_links_json", "[]")


def normalize_csv(package: Path, filename: str, write: bool) -> int:
    path = package / "analysis/review" / filename
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if filename == "decision_coverage.csv":
        normalize_decisions(package, rows)
    elif filename == "evidence_index.csv":
        normalize_evidence(rows)
    elif filename == "communication_claims.csv":
        normalize_claims(rows)
    elif filename == "promise_lifecycle.csv":
        normalize_promises(rows)
    if write:
        write_csv(path, CSV_FIELDS[filename], rows)
    return len(rows)


def normalize_packets(package: Path, write: bool) -> tuple[int, int]:
    path = package / "analysis/review/review_packet.jsonl"
    rows = read_jsonl(path)
    decision_count = 0
    normalized = []
    for source in rows:
        row = dict(source)
        packet_type = row.get("packet_type") or row.get("record_type") or ""
        row["schema_version"] = "unified_qualitative_review_packet_v1"
        row["packet_type"] = packet_type
        row["record_type"] = packet_type
        if packet_type == "decision":
            decision_count += 1
        row["player_id"] = row.get("player_id") or row.get("actor_player_id")
        row["actor_player_id"] = row.get("actor_player_id") or row.get("player_id")
        row["chosen_action"] = row.get("chosen_action") or row.get("applied_action")
        row["applied_action"] = row.get("applied_action") or row.get("chosen_action")
        evidence = row.get("evidence_ids") or row.get("evidence_references") or []
        row["evidence_ids"] = evidence
        row["evidence_references"] = evidence
        normalized.append({field: row.get(field) for field in PACKET_FIELDS})
    if write:
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in normalized:
                handle.write(
                    json.dumps(
                        row,
                        ensure_ascii=False,
                        separators=(",", ":"),
                        sort_keys=False,
                    )
                    + "\n"
                )
    return len(rows), decision_count


def contract_document() -> dict[str, Any]:
    return {
        "schema_version": "unified_qualitative_output_contract_v1",
        "scope": "legacy-run-191-and-273-qualitative-review-superset",
        "required_paths": REQUIRED_PATHS,
        "csv_schemas": CSV_FIELDS,
        "review_packet": {
            "schema_version": "unified_qualitative_review_packet_v1",
            "ordered_fields": PACKET_FIELDS,
            "one_decision_packet_per_resolved_decision": True,
            "additional_episode_packets_allowed": True,
        },
        "case_study_required_fields": [
            "case_study_id",
            "title",
            "mechanism",
            "turn_range",
            "actors",
            "pre_state",
            "chronological_chain",
            "source_ids_and_paths",
            "public_private_comparison",
            "economic_consequences",
            "strategic_interpretation",
            "labels_confidence_and_epistemic_boundary",
            "legal_alternatives_or_explicit_counterfactual",
            "downstream_effects",
            "limitations",
            "evidence_cross_links",
        ],
        "epistemic_policy": {
            "private_thoughts": "logged model artifacts, not proof of internal cognition",
            "deception": "private/public divergence alone is insufficient",
            "collusion": "mutually beneficial exchange alone is insufficient",
            "counterfactuals": "limited to offered legal actions or marked untested",
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_package(package: Path, counts: dict[str, int]) -> dict[str, Any]:
    analysis = package / "analysis"
    run_id = json.loads((package / "run/summary.json").read_text(encoding="utf-8"))[
        "run_id"
    ]
    expected_decisions = 583 if run_id == "mock-83265-81ed4937" else 540
    errors = []
    missing = [path for path in REQUIRED_PATHS if not (analysis / path).is_file()]
    if missing:
        errors.append(f"missing required paths: {missing}")
    for filename, fields in CSV_FIELDS.items():
        with (analysis / "review" / filename).open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            actual = csv.DictReader(handle).fieldnames
        if actual != fields:
            errors.append(f"{filename} header mismatch")
    packets = read_jsonl(analysis / "review/review_packet.jsonl")
    if any(list(packet) != PACKET_FIELDS for packet in packets):
        errors.append("review_packet field order mismatch")
    if any(
        packet.get("schema_version") != "unified_qualitative_review_packet_v1"
        for packet in packets
    ):
        errors.append("review_packet schema version mismatch")
    if counts["decisions"] != expected_decisions:
        errors.append(
            f"decision rows={counts['decisions']}, expected {expected_decisions}"
        )
    if counts["decision_packets"] != expected_decisions:
        errors.append(
            "decision packet count does not match resolved decision count"
        )
    return {
        "schema_version": "unified_qualitative_contract_validation_v1",
        "run_id": run_id,
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "contract": "analysis/manifests/unified_qualitative_contract.json",
        "contract_sha256": sha256(
            analysis / "manifests/unified_qualitative_contract.json"
        ),
        "required_paths": {
            "count": len(REQUIRED_PATHS),
            "missing": missing,
        },
        "csv_headers": {
            filename: fields for filename, fields in CSV_FIELDS.items()
        },
        "review_packet": {
            "schema_version": "unified_qualitative_review_packet_v1",
            "rows": counts["packets"],
            "decision_rows": counts["decision_packets"],
            "ordered_fields": PACKET_FIELDS,
        },
        "row_counts": {
            "decisions": counts["decisions"],
            "evidence": counts["evidence"],
            "communication_claims": counts["claims"],
            "promises": counts["promises"],
        },
        "preservation": {
            "normalization": "lossless field union plus aliases; no source artifacts touched",
            "raw_directories": ["run/", "quality_check/"],
        },
    }


def process(package: Path, write: bool) -> dict[str, Any]:
    analysis = package / "analysis"
    counts = {
        "decisions": normalize_csv(package, "decision_coverage.csv", write),
        "evidence": normalize_csv(package, "evidence_index.csv", write),
        "claims": normalize_csv(package, "communication_claims.csv", write),
        "promises": normalize_csv(package, "promise_lifecycle.csv", write),
    }
    counts["packets"], counts["decision_packets"] = normalize_packets(package, write)
    contract_path = analysis / "manifests/unified_qualitative_contract.json"
    if write:
        write_json(contract_path, contract_document())
        write_json(
            analysis / "quality/unified_contract_validation.json",
            {
                "schema_version": "unified_qualitative_contract_validation_v1",
                "status": "pending",
            },
        )
    elif json.loads(contract_path.read_text(encoding="utf-8")) != contract_document():
        raise AssertionError(f"contract differs: {contract_path}")
    validation = validate_package(package, counts)
    if write:
        write_json(
            analysis / "quality/unified_contract_validation.json",
            validation,
        )
    if validation["status"] != "pass":
        raise AssertionError(
            f"{package.name}: unified validation failed: {validation['errors']}"
        )
    return validation


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    results = [process(package, args.write) for package in PACKAGES]
    contract_hashes = {result["contract_sha256"] for result in results}
    if len(contract_hashes) != 1:
        raise AssertionError("package-local unified contract files differ")
    print(
        json.dumps(
            {
                "status": "pass",
                "mode": "write" if args.write else "check",
                "contract_sha256": next(iter(contract_hashes)),
                "packages": results,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
