"""Copy reviewed research inputs into the manuscript; repository-only step."""

from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "paper_agenda_revision_2026-10-29"
copies = {
    "negotiation/results.json": "data/agenda_negotiation.json",
    "negotiation/offers.json": "data/agenda_offers.json",
    "negotiation/threads.json": "data/agenda_threads.json",
    "negotiation/flows.json": "data/agenda_flows.json",
    "negotiation/rejection_reason_coding.json": "data/agenda_rejection_reasons.json",
    "negotiation/validation.json": "data/agenda_negotiation_validation.json",
    "integration/recurrence_results.json": "data/agenda_recurrence.json",
    "integration/recurrence_rows.jsonl": "data/agenda_recurrence_rows.jsonl",
    "evaluation/results/summary.json": "data/agenda_evaluation.json",
    "evaluation/results/scenario_summary.json": "data/agenda_scenarios.json",
    "evaluation/results/readiness_summary.json": "data/agenda_readiness.json",
    "evaluation/results/verification.json": "data/agenda_evaluation_verification.json",
    "evaluation/protocol.json": "data/agenda_evaluation_protocol.json",
    "evaluation/results/game_summaries.json": "data/agenda_pilot_games.json",
    "evaluation/results/scenario_rows.json": "data/agenda_scenario_rows.json",
    "temporal/results.json": "data/agenda_temporal.json",
    "temporal/sample_fields.json": "data/agenda_sample_fields.json",
    "temporal/row_ledger.jsonl": "data/agenda_temporal_rows.jsonl",
    "temporal/landing_policy_endpoints.json": "data/agenda_landing_endpoints.json",
    "temporal/forecast_endpoints.json": "data/agenda_forecast_endpoints.json",
    "temporal/longitudinal_witnesses.json": "data/agenda_longitudinal_witnesses.json",
    "temporal/validation.json": "data/agenda_temporal_validation.json",
}
manifest = {"sources": {}, "outputs": {}, "transforms": []}
for source, target in copies.items():
    p = SOURCE / source
    out = ROOT / target
    if not p.is_file():
        raise FileNotFoundError(p)
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, out)
    manifest["sources"][source] = hashlib.sha256(p.read_bytes()).hexdigest()
    manifest["outputs"][target] = hashlib.sha256(out.read_bytes()).hexdigest()

for source, target in [
    ("integration/negotiation_adjudicated.tex", "sections/negotiation_extended.tex"),
    ("temporal/temporal_results.tex", "sections/temporal_results.tex"),
    ("temporal/exhibits.tex", "sections/temporal_exhibits.tex"),
]:
    p = SOURCE / source
    out = ROOT / target
    content = p.read_text()
    content = content.replace(
        "states a brown four-house target",
        "states a target of four houses on each brown deed",
    )
    content = content.replace("global turn29 to60", "global turn~29 to~60")
    content = content.replace("event1277", "event~1277").replace(
        "event1279", "event~1279"
    )
    if target == "sections/temporal_exhibits.tex":
        content = content.replace(r"\begin{figure}[p]", r"\begin{figure}[H]")
    out.write_text(content)
    manifest["sources"][source] = hashlib.sha256(p.read_bytes()).hexdigest()
    manifest["outputs"][target] = hashlib.sha256(out.read_bytes()).hexdigest()

p = SOURCE / "evaluation/evaluation_results.tex"
text = p.read_text()
delimiter = "\\subsection{A design for the unanswered experimental questions}"
assert text.count(delimiter) == 1
first, second = text.split(delimiter)
first = first.replace(
    "a small, separately registered local pilot",
    "a small pilot with a locally frozen protocol",
)
second = second.replace(
    "Feedback and memory manipulations change the model-facing condition and therefore require separate, versioned authorization; they are not changes to the historical prompt.",
    "Feedback and memory manipulations define separate, versioned experimental conditions; they are not changes to the historical prompt.",
)
second = second[: second.index("\\paragraph{Cost and execution gate.}")]
second += "The historical workload is not a current cost forecast. No new model query has been made for these arms. Learning, unfamiliar-opponent generalization and the general-to-multi-agent capability relationship remain unmeasured until the corresponding designs are executed.\n"
manifest["sources"]["evaluation/evaluation_results.tex"] = hashlib.sha256(
    p.read_bytes()
).hexdigest()
for target, content in [
    ("sections/reference_readiness.tex", first),
    (
        "sections/prospective_designs.tex",
        "\\section{Experimental designs not executed}\n" + second,
    ),
]:
    out = ROOT / target
    out.write_text(content)
    manifest["outputs"][target] = hashlib.sha256(out.read_bytes()).hexdigest()
manifest["transforms"] = [
    "Separated completed reference-policy diagnostics from unexecuted designs in an appendix.",
    "Clarified the G14 brown construction target as four houses on each deed (4/4).",
    "Restored spacing in turn/event references and kept the three temporal exhibits with their appendix heading.",
    "Used locally frozen protocol instead of separately registered local pilot.",
    "Replaced administrative approval wording with versioned experimental-condition wording.",
    "Kept costing/execution authorization in the research package; manuscript states no model-query arm was run.",
]
(ROOT / "agenda_input_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(
    json.dumps({"copied_inputs": len(copies), "source_files": len(manifest["sources"])})
)
