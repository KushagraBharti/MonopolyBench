"""Read canonical decisions.jsonl records for response-handling conditions (source read only).

Usage: python3 -I check_response_conditions.py <repo_root> <out_json>
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

repo, out_path = Path(sys.argv[1]), Path(sys.argv[2])
pkg = repo / "docs/research_raw/paper_rewrite_2026-11-10"
offers = json.loads((pkg / "data/agenda_offers.json").read_bytes())
runs = {r["game"]: r["source_run"] for r in offers}
LABEL = {"openai/gpt-6.1-sol": "Sol", "google/gemini-4-argon": "Gemini",
         "anthropic/claude-opus-5.5": "Opus", "x-ai/grok-4.7": "Grok"}
out = {"sources": {}, "per_model": {}, "opus": {}}
dec, att = Counter(), Counter()
opus = Counter()
opus_by_span = Counter()
stages_seen, policies = Counter(), Counter()
first_refusal, any_refusal, returned, fallback_model = Counter(), Counter(), Counter(), Counter()
attempt_counts = Counter()
refusal_texts = Counter()
attempt_conditions = Counter()
second_attempt_outcomes = Counter()
events_total = 0
for g in sorted(runs):
    path = repo / runs[g] / "decisions.jsonl"
    raw = path.read_bytes()
    out["sources"][str(path.relative_to(repo))] = hashlib.sha256(raw).hexdigest()
    ev = repo / runs[g] / "events.jsonl"
    events_total += sum(1 for _ in ev.open("rb"))
    for line in raw.splitlines():
        r = json.loads(line)
        if r["phase"] != "decision_resolved":
            continue
        m = LABEL[r["openrouter_model_id"]]
        dec[m] += 1
        att[m] += len(r["attempts"])
        attempt_counts[(m, len(r["attempts"]))] += 1
        sm = r.get("sequence_meta") or {}
        if m != "Opus":
            continue
        pol = sm.get("response_policy") or {}
        policies[json.dumps({k: pol.get(k) for k in ("version", "trigger", "max_resolver_calls", "fallback_models")},
                            sort_keys=True)] += 1
        stages_seen[json.dumps(pol.get("stages"), sort_keys=True)] += 1
        opus[sm.get("response_condition")] += 1
        returned[sm.get("returned_model")] += 1
        fallback_model[str(sm.get("model_fallback_used"))] += 1
        outs = [a["outcome"] for a in r["attempts"]]
        span = "G1-4" if g <= 4 else "G5-20"
        if outs and outs[0] == "refused":
            first_refusal[span] += 1
        if "refused" in outs:
            any_refusal[span] += 1
        opus_by_span[span] += 1
        for i, a in enumerate(r["attempts"]):
            attempt_conditions[(i, a.get("response_condition"), a.get("requested_model"), a["outcome"])] += 1
            if a["outcome"] == "refused":
                msg = (((a.get("raw_response") or {}).get("choices") or [{}])[0].get("message") or {})
                txt = msg.get("refusal") or msg.get("content") or ""
                refusal_texts[txt[:400]] += 1
        if len(outs) > 1 and outs[0] == "refused":
            second_attempt_outcomes[(outs[1], str(r["fallback_used"]))] += 1
out["events_total"] = events_total
out["per_model"] = {m: {"decisions": dec[m], "attempts": att[m]} for m in dec}
out["attempt_counts"] = {f"{k[0]}/{k[1]}": v for k, v in sorted(attempt_counts.items())}
out["opus"] = {
    "decisions_by_span": dict(opus_by_span), "first_attempt_refused_by_span": dict(first_refusal),
    "any_refusal_by_span": dict(any_refusal), "sequence_response_condition": dict(opus),
    "returned_model": dict(returned), "model_fallback_used": dict(fallback_model),
    "policies": dict(policies), "stages": dict(stages_seen),
    "attempt_conditions": {"/".join(map(str, k)): v for k, v in sorted(attempt_conditions.items(), key=str)},
    "second_attempt_after_first_refusal": {"/".join(k): v for k, v in second_attempt_outcomes.items()},
    "distinct_refusal_texts": len(refusal_texts),
    "refusal_texts": [(t, n) for t, n in refusal_texts.most_common(5)]}
out_path.write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "sources"}, indent=1))
