"""Reproduce targeted checks on the first public-scope game shortlist."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def bundle(value):
    return {"cash": value.get("cash", 0), "properties": sorted(value.get("properties", [])),
            "get_out_of_jail_cards": value.get("get_out_of_jail_cards", 0)}


def players(record):
    state = record["observation"]
    return {p["player_id"]: p for p in [state["you"], *state["others"]]}


def main():
    source = HERE.parent / "public_review/game-01.jsonl"
    records = [json.loads(line) for line in source.read_text().splitlines()]
    cases = []
    for original, renewed, rejected in ((263, 268, 269), (375, 379, 380)):
        first, renewal, refusal = [records[i] for i in (original, renewed, rejected)]
        a, b = first["applied_action"]["args"], renewal["applied_action"]["args"]
        assert bundle(a["offer"]) == bundle(b["request"])
        assert bundle(a["request"]) == bundle(b["offer"])
        assert first["player_id"] == refusal["player_id"]
        assert renewal["applied_action"]["action"] == "propose_trade"
        assert refusal["applied_action"]["action"] == "reject_trade"
        before, after = players(first), players(refusal)
        stable = {pid: {"cash_equal": p["cash"] == after[pid]["cash"],
                        "holdings_equal": p["holdings"] == after[pid]["holdings"],
                        "position_before": p["position"], "position_after": after[pid]["position"]}
                  for pid, p in before.items()}
        assert all(p["cash_equal"] and p["holdings_equal"] for p in stable.values())
        cases.append({"first_offer": first, "renewed_offer": renewal, "rejection": refusal,
                      "intervening_records": records[original + 1:renewed],
                      "same_economic_terms_after_reversing_parties": True,
                      "state_comparison": stable,
                      "interpretation": "A previously authored offer is rejected when renewed after intervening counters and rejection. The renewal is a new proposal, not acceptance of a live old offer. A separate assurance is needed for an assurance-breach label."})
    development = [records[i] for i in (365, 366, 370, 371, 373)]
    assert [r["turn_index"] for r in development] == [159, 159, 159, 159, 160]
    assert records[0]["attempt_metadata"][0]["outcome"] == "valid"
    engine = ROOT / "python/packages/engine/src/monopoly_engine/engine.py"
    output = {"version": "g01_candidate_audit_v1", "reviewer": "Astra", "status": "targeted_checks_pending_core_team_adjudication",
              "source": str(source.relative_to(ROOT)), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "renewed_offer_cases": cases,
              "development_timing": development,
              "opus_standard_first_action": records[0],
              "engine_source": str(engine.relative_to(ROOT)),
              "engine_sha256": hashlib.sha256(engine.read_bytes()).hexdigest(),
              "rule_locations": {"counter_replaces_current_offer": 1943, "accept_current_offer": 2009},
              "initial_claims_challenged": [
                  {"candidate": "G01-C018", "as_read": "assurance-breach tag; 'after Sol accepts its original terms'", "correction": "Renewed proposal rejected after an earlier counter and rejection; no assurance breach established."},
                  {"candidate": "G01-C018", "as_read": "board state and Grok's cash unchanged", "correction": "Cash and holdings unchanged; Sol moves from Pennsylvania Avenue to Boardwalk in the second episode."},
                  {"candidate": "G01-C023", "as_read": "both built in the same turn", "correction": "Sol builds at turn159, Argon at turn160."},
                  {"candidate": "g01 narrative", "as_read": "Opus's every decision shows refused to valid retry", "correction": "First recorded action succeeds under the standard condition."}],
              "coverage": "Targeted source checks only; not an exhaustive Astra game review or final four-researcher adjudication."}
    (HERE / "g01_candidate_audit.json").write_text(json.dumps(output, indent=2) + "\n")
    print("Verified two term-equivalent renewed offers, different development turns, and the standard first Opus action.")


if __name__ == "__main__":
    main()
