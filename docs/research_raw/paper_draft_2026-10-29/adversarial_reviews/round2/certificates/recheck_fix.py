"""Bounded recheck of the coordinator's fail-closed sale-graph guard."""
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import adversarial_checks as checks

live = checks.OUT.parents[1] / "executable_audit"
spec = importlib.util.spec_from_file_location("revised_audit", live / "run_audit.py")
revised = importlib.util.module_from_spec(spec)
spec.loader.exec_module(revised)
old = checks.audit
try:
    checks.audit = revised
    counterexample = checks.synthetic_bundle_counterexample(expect_unresolved=True)
    hotel_lock = checks.hotel_lock_scope()
finally:
    checks.audit = old
with (checks.OUT / "recheck_run.log").open("w") as log, contextlib.redirect_stdout(log):
    fresh = revised.run()
initial = json.loads((checks.OUT / "fresh_results.json").read_text())
assert fresh["summary"] == initial["summary"]
assert fresh["historical_replays"] == initial["historical_replays"]
old_cases = {r["case_id"]: r for r in initial["results"]}
for result in fresh["results"]:
    comparable = json.loads(json.dumps(result))
    if "search" in comparable:
        comparable["search"].pop("graph_scope", None)
    assert comparable == old_cases[result["case_id"]]
record = {"runner_sha256": hashlib.sha256((live / "run_audit.py").read_bytes()).hexdigest(),
          "false_certificate_refused": counterexample["certificate"],
          "bundled_payment_still_accepted": counterexample["cash_after"] == 250,
          "historical_g7_graph": hotel_lock["graph"],
          "all_126_results_unchanged_except_graph_scope": True,
          "summary": fresh["summary"], "historical_replays_unchanged": True}
(checks.OUT / "fix_recheck.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({key: value for key, value in record.items() if key != "historical_g7_graph"}, indent=2))
