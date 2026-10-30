"""Regenerate the phase-1 economic tables and independent validation.

Run from the repository root after setting up the repository Python environment.
No provider calls or canonical writes. Optional Opus checks are separately attributed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(relative):
    return json.loads((HERE / relative).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-peers", "--include-opus", dest="include_peers", action="store_true",
                        help="Also regenerate Opus's and Fable's independent corpus and validation checks.")
    args = parser.parse_args()
    logs = HERE / "reproduction_logs"
    logs.mkdir(exist_ok=True)
    commands = []

    def run(name, command):
        log = logs / f"{name}.log"
        print(f"Running {name}", flush=True)
        with log.open("w") as stream:
            result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=False)
        commands.append({"name": name, "command": command, "exit_code": result.returncode,
                         "log": str(log.relative_to(ROOT)), "log_sha256": sha(log)})
        if result.returncode:
            raise RuntimeError(f"{name} failed; inspect {log}")

    prefix = str(HERE.relative_to(ROOT))
    python = str(ROOT / "python/.venv/bin/python")
    for directory in ("sol", "astra", "sol_round2"):
        run(f"{directory}_tests", [python, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                                  f"{prefix}/{directory}"])
    for script in ("sol/reproduce.py", "astra/visibility_inventory.py",
                   "astra/checkpoint_audit.py", "astra/memory_audit.py",
                   "astra/prepare_behavior_review.py"):
        run(script.replace("/", "_").removesuffix(".py"), [sys.executable, f"{prefix}/{script}"])
    run("sol_public_delivery", [python, f"{prefix}/sol_round2/public_delivery_audit.py"])
    if args.include_peers:
        run("opus_tests", [python, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"{prefix}/opus"])
        run("fable_tests", [python, "-m", "pytest", "-q", "-p", "no:cacheprovider", f"{prefix}/fable"])
        for script in ("opus_corpus.py", "opus_responses.py", "opus_sandbox_checks.py"):
            run(script.removesuffix(".py"), [python, f"{prefix}/opus/{script}"])
        for script in ("fable_reducer.py", "fable_addendum.py"):
            run(script.removesuffix(".py"), [python, f"{prefix}/fable/{script}"])

    economic = read("sol/results.json")
    visibility = read("astra/visibility_manifest.json")
    checkpoints = read("astra/checkpoint_audit.json")
    memory = read("astra/memory_audit.json")
    packets = read("astra/review_packet_manifest.json")
    delivery = read("sol_round2/public_delivery_summary.json")
    comparisons = []

    def equal(name, left, right):
        comparisons.append({"check": name, "passed": left == right})
        if left != right:
            raise AssertionError(f"{name}: {left!r} != {right!r}")

    for name in ("games", "events", "decisions"):
        equal(f"Sol and Astra {name}", economic[name], visibility["totals"][name])
    equal("Economic observation coverage", economic["decisions"], checkpoints["decisions_checked"])
    equal("Economic observation discrepancies", checkpoints["mismatching_fields"], 0)
    equal("Visibility linkage issues", visibility["issues"], [])
    equal("Private memory provenance issues", memory["issues"], [])
    equal("Private memory coverage", sum(x["decisions"] for x in memory["by_model"].values()), economic["decisions"])
    for key in ("events", "decisions", "attempts"):
        equal(f"Review packet {key} coverage", packets["totals"][key], visibility["totals"][key])
    equal("Public delivery memory coverage", delivery["counts"]["checked_initial_memories"], economic["decisions"])
    equal("Public delivery occurrence coverage", delivery["counts"]["canonical_public_messages"],
          visibility["totals"]["decisions_with_public_events"])
    source_files = read("sol/manifest.json")["sources"]
    for source in source_files:
        equal(f"Source hash {source['path']}", sha(ROOT / source["path"]), source["sha256"])

    peer = {"included": False, "reason": "Use --include-peers to regenerate and compare independent peer outputs."}
    if args.include_peers:
        opus = read("opus/opus_results.json")
        responses = read("opus/opus_response_audit.json")
        branches = read("opus/opus_sandbox_checks.json")
        equal("Sol and Opus game count", economic["games"], opus["n_games"])
        for key in ("events", "decisions", "trade_completion_sides", "first_builder_wins"):
            equal(f"Sol and Opus {key}", economic[key], opus[key])
        equal("Deed acquisition routes", economic["deed_routes"],
              {k: v for k, v in opus["deed_routes"].items() if k != "returned_to_bank"})
        equal("Group completion routes", economic["group_routes"], opus["episode_completion_routes"])
        for model, counts in economic["trade_group_metrics"].items():
            other = opus["trade_group_deployment_by_model"][model]
            for left, right in (("trade_groups", "trade_groups"),
                                ("first_management_built", "built_first_mgmt_turn"),
                                ("entry_eligible", "entry_buildable"),
                                ("entry_eligible_built", "entry_buildable_built"),
                                ("eligible_during_window", "buildable_any_menu_first_turn")):
                equal(f"{model} {left}", counts[left], other[right])
        equal("Snapshot reconciliation", opus["snapshots_matched"], opus["snapshots_total"])
        equal("Opus reducer issues", opus["reducer_issues"], 0)
        equal("Selected-response mismatch count", economic["selected_response_mismatches"]["total"],
              responses["content_tool_mismatch"]["total"])
        equal("Full-memory reconstruction coverage", branches["memory_reconstruction"]["memory_equal"], economic["decisions"])
        fable = read("fable/fable_results.json")
        for key in ("games", "events", "decisions", "first_builder_wins"):
            equal(f"Sol and Fable {key}", economic[key], fable[key])
        equal("Fable route classifier discrepancies", fable["route_disagreements"], [])
        equal("Fable and Sol group routes", fable["episodes"]["by_route"], economic["group_routes"])
        equal("Jail-card observation discrepancies", fable["jail_card_observation_differences"], [])
        equal("Jail-card observation coverage", fable["jail_card_observation_checks"]["match"], economic["decisions"] * 4)
        equal("Fable settlement matches", fable["trade_settlements"]["prediction_matches_events"], opus["trades"])
        peer = {"included": True, "report": "opus/opus_results.json",
                "snapshot_count": opus["snapshots_matched"],
                "terminal_inheritance_episodes": opus["inheritance_episodes_created_by_final_bankruptcy"],
                "branch_checks": branches["branch_summary"], "fable_report": "fable/fable_results.json",
                "jail_card_observation_checks": fable["jail_card_observation_checks"],
                "management_access": fable["turn_access_by_model"]}

    code_paths = sorted(p for p in HERE.rglob("*.py") if "__pycache__" not in p.parts)
    report = {"analysis_version": "phase1_integration_v1", "status": "passed",
              "scope": "Economic accounting and evidence availability. Semantic behavior review is pending.",
              "economic_source": "sol/results.json", "economic_results": economic,
              "independent_observation_check": {"decisions": checkpoints["decisions_checked"],
                                                "differing_fields": checkpoints["mismatching_fields"]},
              "visibility_totals": visibility["totals"], "private_memory_by_model": memory["by_model"],
              "review_preparation": {"packets": len(packets["packets"]), "totals": packets["totals"],
                                     "status": packets["status"]},
              "public_timeline_delivery": {"counts": delivery["counts"], "scope": delivery["scope"]},
              "peer_validation": peer, "checks": comparisons, "commands": commands,
              "analysis_code": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in code_paths],
              "canonical_sources": source_files,
              "interpretation": [
                  "Group route names refer to the last deed completing the group, not homogeneous constituent routes.",
                  "Terminal inheritances cannot measure subsequent deployment.",
                  "Entry-legal menu responsiveness and elapsed access/building delay answer different questions.",
                  "Channel-qualified samples are selected subsets and do not establish comparable behavior prevalence.",
                  "Applied actions remain authoritative; inconsistent response channels do not identify intent."]}
    target = HERE / "phase1_results.json"
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"Passed {len(comparisons)} consistency checks. Wrote {target.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
