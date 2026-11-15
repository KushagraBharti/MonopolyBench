#!/usr/bin/env python3
"""One-pass census of the canonical decision logs (existing records only).

Reads <repo>/saved_games/railway-research-*/game-NN-*/run/decisions.jsonl and writes
data/decision_census.json: per-decision resolution facts and cohort totals. No engine or model call.
"""
import json, glob, pathlib, collections, hashlib
HERE = pathlib.Path(__file__).resolve().parent.parent
REPO = HERE.parents[4]
C = collections.Counter
NAME = {"openai/gpt-6.1-sol": "Sol", "google/gemini-4-argon": "Gemini", "anthropic/claude-opus-5.5": "Opus", "x-ai/grok-4.7": "Grok"}
rows = []; files = {}
for g in range(1, 21):
    cand = glob.glob(str(REPO / "saved_games" / "railway-research-*" / f"game-{g:02d}-*" / "run" / "decisions.jsonl"))
    assert len(cand) == 1, cand
    p = pathlib.Path(cand[0]); files[str(p.relative_to(REPO))] = hashlib.sha256(p.read_bytes()).hexdigest()
    with p.open() as fh:
        for ln, line in enumerate(fh, 1):
            d = json.loads(line)
            if d.get("phase") != "decision_resolved":
                continue
            at = d["attempts"]
            fa = d.get("final_action") or {}
            rows.append({"game": g, "decision": int(d["decision_id"][-6:]), "line": ln, "turn": d["turn_index"], "model": NAME[d["openrouter_model_id"]],
                         "type": d["decision_type"], "n_attempts": len(at), "outcomes": [a.get("outcome") for a in at],
                         "conditions": [a.get("response_condition") for a in at], "fallback": bool(d.get("fallback_used")), "retry": bool(d.get("retry_used")),
                         "action": fa.get("action"), "has_note": bool(fa.get("private_thought")), "has_public": bool(fa.get("public_message"))})
M = ["Sol", "Gemini", "Opus", "Grok"]
out = {"files_sha256": files, "decisions": len(rows), "attempts": sum(r["n_attempts"] for r in rows),
       "by_model": {m: {"decisions": sum(1 for r in rows if r["model"] == m), "attempts": sum(r["n_attempts"] for r in rows if r["model"] == m),
                        "fallbacks": sum(1 for r in rows if r["model"] == m and r["fallback"]),
                        "decisions_with_refusal": sum(1 for r in rows if r["model"] == m and "refused" in r["outcomes"]),
                        "refused_attempts": sum(r["outcomes"].count("refused") for r in rows if r["model"] == m),
                        "first_attempt_refused": sum(1 for r in rows if r["model"] == m and r["outcomes"][0] == "refused"),
                        "decisions_with_retry": sum(1 for r in rows if r["model"] == m and r["n_attempts"] > 1),
                        "applied_without_note": sum(1 for r in rows if r["model"] == m and not r["has_note"]),
                        "outcome_counts": dict(C(o for r in rows if r["model"] == m for o in r["outcomes"]))} for m in M},
       "opus_refusal_by_game": {str(g): {"decisions": sum(1 for r in rows if r["model"] == "Opus" and r["game"] == g),
                                         "with_refusal": sum(1 for r in rows if r["model"] == "Opus" and r["game"] == g and "refused" in r["outcomes"])} for g in range(1, 21)},
       "fallback_by_type": dict(C(r["type"] for r in rows if r["fallback"])), "fallback_by_game": dict(C(r["game"] for r in rows if r["fallback"])),
       "fallback_action": dict(C(r["action"] for r in rows if r["fallback"])),
       "decision_types": dict(C(r["type"] for r in rows)), "actions": dict(C(r["action"] for r in rows)),
       "public_nonempty_applied": sum(1 for r in rows if r["has_public"])}
(HERE / "data" / "decision_census.json").write_text(json.dumps(out, indent=1))
(HERE / "data" / "decision_census_rows.json").write_text(json.dumps(rows))
print(json.dumps({k: v for k, v in out.items() if k != "files_sha256"}, indent=1))
