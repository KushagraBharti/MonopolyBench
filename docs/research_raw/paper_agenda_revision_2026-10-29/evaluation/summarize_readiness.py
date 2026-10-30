"""Combine completed checks without treating a passing screen as an oracle."""
from __future__ import annotations

import hashlib
import json
import zipfile

import run_offline as runner

CAUSES = {
    "build-red-third-house-illinois-06": "Focal p1 owns Illinois, but Kentucky and Indiana belong to p2; the reference tries to build without the whole red group.",
    "build-red-third-house-kentucky-05": "Reference builds Kentucky, which belongs to p2 rather than focal p1.",
    "buy-or-auction-electric-company-cash-danger-05": "Focal p1 is on Electric Company, which the supplied board assigns to p3; it cannot be auctioned as unowned.",
    "buy-or-auction-reading-first-railroad-07": "Focal p1 is on Reading, which the supplied board assigns to p3; it cannot be bought from the bank.",
    "liquidation-sell-hotel-house-shortage-10": "Boardwalk has a hotel but bank stock is two houses; the engine requires four to downgrade it.",
    "post-turn-propose-orange-before-ending-10": "Requested New York and the orange group have buildings; the proposed deed trade is prohibited while developed.",
    "trade-propose-railroad-swap-for-light-blue-11": "The offer targets p2 for Vermont, but the supplied board assigns Vermont to p3.",
    "trade-response-accept-liquidity-saving-03": "The proposed Pennsylvania Railroad/Electric Company exchange names deeds unowned on the supplied board; valid transfer ownership fails.",
    "trade-response-accept-orange-for-utility-01": "The exchange requests Electric Company, which is unowned on the supplied board rather than held by the giving participant.",
    "trade-response-accept-pink-build-window-10": "The exchange names Virginia and Electric Company, both unowned on the supplied board.",
    "trade-response-accept-red-with-cash-02": "The exchange requests Electric Company, which is unowned on the supplied board rather than held by the giving participant."
}


def main() -> None:
    out = runner.HERE / "results"
    refs = json.loads((out / "reference_fixture_actions.json").read_text())
    states = json.loads((out / "fixture_state_checks.json").read_text())["rows"]
    bad_refs = {x["scenario_id"]: x for x in refs if x["errors"]}
    bad_states = {x["scenario_id"]: x for x in states if x["failures"]}
    assert set(CAUSES) == set(bad_refs)
    rows = []
    for state in states:
        sid = state["scenario_id"]
        rows.append({"scenario_id": sid, "passes_reference_action_legality": sid not in bad_refs, "passes_specified_static_invariants": sid not in bad_states, "passes_both_limited_checks": sid not in bad_refs and sid not in bad_states, "reference_errors": bad_refs.get(sid, {}).get("errors", []), "manually_checked_reference_cause": CAUSES.get(sid), "state_flags": state["failures"], "status": "candidate for independent task adjudication" if sid not in bad_refs and sid not in bad_states else "quarantine pending explicit condition/fixture adjudication"})
    current = runner.ROOT / "python/packages/engine/src/monopoly_engine/engine.py"
    archive = runner.ROOT / "docs/research_raw/paper_draft_2026-10-29/artifacts/historical-claim-audit.zip"
    member = "historical-claim-audit/vendor/monopoly_engine/engine.py"
    with zipfile.ZipFile(archive) as z:
        archived_hash = hashlib.sha256(z.read(member)).hexdigest()
    result = {"scenarios": len(rows), "passes_reference_legality": sum(x["passes_reference_action_legality"] for x in rows), "passes_specified_static_invariants": sum(x["passes_specified_static_invariants"] for x in rows), "passes_both_limited_checks": sum(x["passes_both_limited_checks"] for x in rows), "passing_candidate_ids": [x["scenario_id"] for x in rows if x["passes_both_limited_checks"]], "failing_reference_ids": list(CAUSES), "oracle_claim": "None. The passing subset is not certified strategically optimal, fully reachable, or safe for a capability score.", "additional_probe_requirements": ["Regenerate or validate the complete legal menu against authoritative engine state", "Prove or explicitly declare source-state reachability and any artificial intervention", "Declare an objective endpoint and certify a positive legal witness or supported impossibility bound", "Separate local feasibility from expected utility; use repeated valid continuation policies for value comparisons", "Replace expression/keyword points as capability truth; keep them separate if expression is the target", "Freeze task-family splits and independent labels before fresh model output"], "engine_comparison": {"current_path": str(current.relative_to(runner.ROOT)), "current_sha256": runner.file_digest(current), "archive_path": str(archive.relative_to(runner.ROOT)), "archive_member": member, "archive_member_sha256": archived_hash, "byte_identical": archived_hash == runner.file_digest(current)}, "rows": rows}
    runner.save_json(out / "readiness_summary.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in {"rows", "passing_candidate_ids"}}, sort_keys=True))


if __name__ == "__main__":
    main()
