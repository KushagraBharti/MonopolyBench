"""Provenance, configuration and source checks. Read-only.

Reads stored run artifacts, replay reports written at run time, and source
files at the two recorded run commits (via `git show`, which reads history
and changes nothing). Executes no engine, replay, game or model call.
Produces data/provenance.json.
"""
from __future__ import annotations

import csv
import re
import subprocess
from collections import Counter
from pathlib import Path

import common as C

out: dict = {}
LABEL = {"anthropic/claude-opus-5.5": "Opus", "openai/gpt-6.1-sol": "Sol",
         "google/gemini-4-argon": "Gemini", "x-ai/grok-4.7": "Grok"}

# ------------------------------------------------------------ cohort map
index = {}
for coll in ("railway-research-12-games-2026-10-25", "railway-research-8-games-2026-10-26"):
    path = C.REPO / "saved_games" / coll / "game-index.csv"
    C.read_bytes(path)
    for row in csv.DictReader(path.open()):
        index[int(row["collection_game"])] = row | {"collection": coll}
cohort = []
totals = Counter()
for g in range(1, 21):
    run = C.REPO / C.runs()[g]
    art = C.read_json(run / "artifact_replay_report.json")
    sta = C.read_json(run / "state_replay_report.json")
    rep = C.read_json(run / "replay_report.json")
    players = C.read_json(run / "players.json")["players"]
    seat = {p["player_id"]: LABEL[p["openrouter_model_id"]] for p in players}
    events = C.read_jsonl(run / "events.jsonl")
    end = events[-1]
    assert end["type"] == "GAME_ENDED"
    win = end["payload"]["winner_player_id"]
    row = {"game": g, "block": C.block_of(g), "rotation": (g - 1) % 4 + 1, "seed": art["run_config_used"]["seed"],
           "turns": int(index[g]["turns"]), "source_commit": index[g]["git_sha"], "run_id": index[g]["run_id"],
           "path": C.runs()[g], "seat_order": [seat[f"p{i}"] for i in range(1, 5)],
           "winner": seat[win], "winner_seat": int(win[1:]), "events": len(events),
           "replay": {"aggregate": rep["status"], "artifact_mode": {"status": art["status"], "scope": art["comparison_scope"],
                                                                     "compared": art["original_compared_event_count"],
                                                                     "excluded_event_types": art["excluded_event_types"],
                                                                     "hash_equal": art["original_canonical_hash"] == art["replay_canonical_hash"]},
                      "state_mode": {"status": sta["status"], "scope": sta["comparison_scope"],
                                     "compared": sta["original_compared_event_count"],
                                     "excluded_event_types": sta["excluded_event_types"],
                                     "hash_equal": sta["original_canonical_hash"] == sta["replay_canonical_hash"]},
                      "report_written": art["finished_at"]}}
    assert row["replay"]["artifact_mode"]["compared"] == len(events) and not art["excluded_event_types"]
    totals["events"] += len(events)
    totals["artifact_compared"] += art["original_compared_event_count"]
    totals["state_compared"] += sta["original_compared_event_count"]
    totals["artifact_passed"] += art["status"] == "passed" and row["replay"]["artifact_mode"]["hash_equal"]
    totals["state_passed"] += sta["status"] == "passed" and row["replay"]["state_mode"]["hash_equal"]
    cohort.append(row)
out["cohort"] = cohort
out["replay_totals"] = dict(totals)
out["replay_definitions"] = {
    "artifact_mode": C.read_json(C.REPO / C.runs()[1] / "artifact_replay_report.json")["canonicalization"],
    "state_mode": C.read_json(C.REPO / C.runs()[1] / "state_replay_report.json")["canonicalization"],
    "canonical_event_lines": "json.dumps(event, sort_keys=True, separators=(',', ':'), ensure_ascii=True) per event "
                             "(python/packages/engine/src/monopoly_engine/replay.py)",
    "clock": "runs use a synthetic event clock (start_ts_ms 0, ts_step_ms 250), so timestamps are reproducible",
}
seeds = []
for r in cohort:
    if r["seed"] not in seeds:
        seeds.append(r["seed"])
out["seeds_in_block_order"] = seeds
assert len(seeds) == 5 and all(len({r["seed"] for r in cohort if r["block"] == b}) == 1 for b in range(1, 6))
out["wins_by_system"] = dict(Counter(r["winner"] for r in cohort))
out["wins_by_seat"] = dict(sorted(Counter(r["winner_seat"] for r in cohort).items()))
out["source_commits"] = dict(Counter(r["source_commit"] for r in cohort))

# ------------------------------------------------------------ git: tool choice at both commits
def git_show(commit: str, path: str) -> str:
    return subprocess.run(["git", "-C", str(C.REPO), "show", f"{commit}:{path}"], capture_output=True, text=True,
                          check=True).stdout


tc = {}
for commit in sorted(set(r["source_commit"] for r in cohort)):
    src = git_show(commit, "python/packages/arena/src/monopoly_arena/player_config.py")
    m = re.search(r"def tool_choice_for_model\(model_id: str\) -> str:\n.*?\n    return [^\n]*", src, re.S)
    body = m.group(0)
    pol = git_show(commit, "python/packages/arena/src/monopoly_arena/response_policy.py")
    runner = git_show(commit, "python/packages/arena/src/monopoly_arena/llm_runner.py")
    tc[commit] = {"tool_choice_function": body.strip(),
                  "grok_required": 'return "required" if model_id == "x-ai/grok-4.7" else "auto"' in body,
                  "refusal_policy_version": re.search(r'POLICY_VERSION = "([^"]+)"', pol)[1],
                  "refusal_fallbacks": re.search(r"REFUSAL_FALLBACKS = (\{[^}]*\})", pol)[1],
                  "fallback_policy": re.search(r'"fallback_policy": "([^"]+)"', runner)[1]}
    assert tc[commit]["grok_required"]
out["configuration_at_run_commits"] = tc

# ------------------------------------------------------------ response conditions (recount)
dec = Counter(); att = Counter(); refused_first = Counter(); refused_later = Counter(); recovery = Counter()
conflicts = Counter(); content_named = Counter(); fallback = Counter(); retry = Counter()
for g in range(1, 21):
    for k, rec in C.decisions(g)["decision_resolved"].items():
        m = LABEL[rec["openrouter_model_id"]]
        dec[m] += 1
        atts = rec["attempts"]
        att[m] += len(atts)
        for i, a in enumerate(atts):
            if a.get("outcome") == "refused":
                (refused_first if i == 0 else refused_later)[m] += 1
        if atts and atts[-1].get("response_condition") == "same_model_without_private_thought":
            recovery[m] += 1
        fallback[m] += bool(rec.get("fallback_used"))
        retry[m] += bool(rec.get("retry_used"))
        if m == "Grok":
            a = atts[-1]
            text = a.get("assistant_content")
            if text is None:
                text = ((a.get("raw_response") or {}).get("choices") or [{}])[0].get("message", {}).get("content")
            mm = re.search(r'"name"\s*:\s*"([a-z_]+)"', text or "")
            if mm:
                content_named[m] += 1
                if mm[1] != rec["final_action"]["action"]:
                    conflicts[m] += 1
out["response_conditions"] = {"decisions": dict(dec), "attempts": dict(att), "first_attempt_refusals": dict(refused_first),
                              "later_refusals": dict(refused_later), "decisions_resolved_in_recovery": dict(recovery),
                              "decisions_with_fallback": dict(fallback), "decisions_with_retry": dict(retry),
                              "grok_content_names_action": content_named["Grok"], "grok_content_conflicts": conflicts["Grok"]}

# ------------------------------------------------------------ G18 motive check
g18 = []
alive = None
for k in range(421, 462):
    st = C.decisions(18)["decision_started"].get(k)
    rec = C.decisions(18)["decision_resolved"].get(k)
    if st is None or rec is None:
        continue
    if k == 421:
        gs = st["prompt_payload"]["game_state"]
        alive = {"decision_player": gs["metadata"]["you_player_id"],
                 "others": [{"player_id": o["player_id"], "name": o["name"], "bankrupt": o["bankrupt"], "cash": o["cash"]}
                            for o in gs["others"]]}
    if LABEL[rec["openrouter_model_id"]] != "Opus":
        continue
    a = rec["attempts"][-1]
    msg = ((a.get("raw_response") or {}).get("choices") or [{}])[0].get("message", {}) or {}
    fields = {"public_message": rec["final_action"].get("public_message"), "private_note": rec["final_action"].get("private_thought"),
              "assistant_content": a.get("assistant_content"), "provider_reasoning": msg.get("reasoning")}
    for name, text in fields.items():
        for m in re.finditer(r"inherit|estate|creditor|bankrupt|elimin|\bbust|extend|survive|delay", text or "", re.I):
            g18.append({"decision": k, "field": name, "term": m.group(0),
                        "context": (text or "")[max(0, m.start() - 90): m.end() + 90]})
out["g18_opus_text_hits"] = g18
out["g18_inheritance_terms_found"] = sorted({h["term"].lower() for h in g18 if re.match(r"inherit|estate|creditor", h["term"], re.I)})
out["g18_state_at_d421"] = alive

# ------------------------------------------------------------ necessary-text spans
reading = C.read_json(C.DRAFT / "data/necessary_text_reading.json")
texts = {(t["game"], t["decision"]): t for t in C.read_json(C.DRAFT / "data/necessary_first_texts.json")}
checked = []
for r in reading["rows"]:
    src = texts[(r["game"], r["decision"])][r["field"]] or ""
    # re-read the original record to avoid trusting the cached extract
    rec = C.resolved(r["game"], r["decision"])
    if r["field"] == "applied_private_note":
        orig = rec["final_action"].get("private_thought") or ""
    else:
        a = rec["attempts"][-1]
        orig = (((a.get("raw_response") or {}).get("choices") or [{}])[0].get("message", {}) or {}).get("reasoning") or ""
    assert src == orig and r["span"] in orig, (r["game"], r["decision"])
    checked.append((r["game"], r["decision"], r["category"], r["channel"]))
out["necessary_reading"] = {"rows": len(checked), "spans_verified": len(checked),
                            "by_category": dict(Counter(c for _, _, c, _ in checked)),
                            "paid_by_category": dict(Counter(r["category"] for r in reading["rows"] if r["outcome"] == "paid")),
                            "paid_by_channel": dict(Counter(r["channel"] for r in reading["rows"] if r["outcome"] == "paid"))}

# ------------------------------------------------------------ refusal text and printed prompts
ref_text = Counter(); ref_finish = Counter()
for g in range(1, 21):
    for k, rec in C.decisions(g)["decision_resolved"].items():
        for a in rec["attempts"]:
            if a.get("outcome") == "refused":
                ch = ((a.get("raw_response") or {}).get("choices") or [{}])[0]
                m = ch.get("message") or {}
                ref_text[(m.get("content") or m.get("refusal") or "")] += 1
                ref_finish[f"{ch.get('finish_reason')}/{ch.get('native_finish_reason')}"] += 1
out["refusals"] = {"distinct_texts": len(ref_text), "count": sum(ref_text.values()),
                   "text": next(iter(ref_text)) if len(ref_text) == 1 else None, "finish_reasons": dict(ref_finish)}
std = (C.DRAFT / "data/standard_system_prompt.txt").read_text()
rec_p = (C.DRAFT / "data/recovery_system_prompt.txt").read_text()
found = {"standard": None, "recovery": None}
for k, rec in sorted(C.decisions(1)["decision_resolved"].items()):
    for a in rec["attempts"]:
        for m in a.get("prompt_messages") or []:
            if m.get("role") == "system":
                if m["content"] == std and found["standard"] is None:
                    found["standard"] = k
                if m["content"] == rec_p and found["recovery"] is None:
                    found["recovery"] = k
    if all(found.values()):
        break
out["printed_prompts_match_g1_records"] = found
assert all(v is not None for v in found.values())

out["sources"] = C.sources_snapshot()
C.write_json("provenance.json", out)
print(out["seeds_in_block_order"], out["wins_by_system"], out["wins_by_seat"], out["source_commits"])
print(out["replay_totals"])
print(out["response_conditions"])
print(out["g18_inheritance_terms_found"], out["g18_state_at_d421"])
for h in g18:
    print(h["decision"], h["field"], h["term"], "|", h["context"].replace("\n", " "))
print(out["necessary_reading"])
