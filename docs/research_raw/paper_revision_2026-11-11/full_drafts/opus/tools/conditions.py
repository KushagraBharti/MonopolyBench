"""Response conditions, refusal chronology, prompt difference and usage fields.

Reads every attempt in the twenty decision streams (no model calls).
Reports: refusal strings and finish reasons; per-game and per-clock-bin
refusal shares of Opus first attempts; the exact line difference between
the standard and action-only system prompts as stored in attempt records;
Grok received-call versus content conflicts are inherited and not
recomputed; reasoning-token field presence/zeros by configuration; and
the cost fields with an explicit rule (no field addition).
"""
from __future__ import annotations

import difflib
import json
import statistics as st
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import corpus

OUT = Path(__file__).resolve().parents[1] / "data"


def main():
    D = corpus.build_cache()
    res = {}
    refusal_texts = Counter()
    finish = Counter()
    per_game = {}
    bins = defaultdict(lambda: [0, 0])
    last_accepted = {}
    std_sys, alt_sys = None, None
    attempts_by_cond = Counter()
    refused_by_cond = Counter()
    decisions_opus = 0
    first_refused = 0
    chains = Counter()
    memory_empty = Counter()
    tokens = defaultdict(list)
    tok_missing = Counter()
    tok_zero = Counter()
    completion = defaultdict(list)
    cost_usage = defaultdict(float)
    cost_upstream = defaultdict(float)
    cost_rule = defaultdict(float)
    unpriced = Counter()
    for g, game in D["games"].items():
        n_first, n_ref = 0, 0
        for idx, d in game["decisions"].items():
            model = game["pmodel"][d["player"]]
            atts = d["res"]["attempts"]
            for a in atts:
                attempts_by_cond[(model, a["condition"])] += 1
                if a["outcome"] == "refused":
                    refused_by_cond[(model, a["condition"])] += 1
                    refusal_texts[a["refusal"]] += 1
                    finish[(a["finish_reason"], a["native_finish_reason"])] += 1
                u = a["usage"]
                if u is None:
                    unpriced[model] += 1
                else:
                    rt = (u.get("completion_tokens_details") or {}).get("reasoning_tokens")
                    if rt is None:
                        tok_missing[model] += 1
                    else:
                        tokens[model].append(rt)
                        if rt == 0:
                            tok_zero[model] += 1
                    if u.get("completion_tokens") is not None:
                        completion[model].append(u["completion_tokens"])
                    c = u.get("cost")
                    up = (u.get("cost_details") or {}).get("upstream_inference_cost")
                    if c is not None:
                        cost_usage[model] += c
                    if up is not None:
                        cost_upstream[model] += up
                    # rule: BYOK calls report usage.cost 0 and the upstream cost separately;
                    # take upstream_inference_cost when usage.is_byok is true, otherwise usage.cost
                    if u.get("is_byok"):
                        cost_rule[model] += up or 0.0
                    else:
                        cost_rule[model] += c or 0.0
                if a["condition"] == "same_model_without_private_thought" and alt_sys is None and a["system_prompt"]:
                    alt_sys = a["system_prompt"]
            if model == "Opus":
                decisions_opus += 1
                first = atts[0]
                n_first += 1
                ts = datetime.fromtimestamp(first["start_ms"] / 1000, tz=timezone.utc)
                if first["outcome"] == "refused":
                    n_ref += 1
                    first_refused += 1
                else:
                    last_accepted[g] = max(last_accepted.get(g, ts), ts)
                if g <= 4:
                    b = ts.replace(minute=(ts.minute // 10) * 10, second=0, microsecond=0).strftime("%H:%M")
                    bins[b][0] += first["outcome"] == "refused"
                    bins[b][1] += 1
                chains[tuple((a["condition"], a["outcome"]) for a in atts)] += 1
                mem = d["payload"]["game_state"]["memory"]["your_private_thoughts_last_10"]
                texts = [m.get("thought") if isinstance(m, dict) else m for m in mem]
                if not mem:
                    memory_empty["empty"] += 1
                elif all((t or "").strip().lower() == "fallback" for t in texts):
                    memory_empty["fallback_only"] += 1
                else:
                    memory_empty["has_model_note"] += 1
            if std_sys is None and model != "Opus":
                pass
        per_game[g] = {"opus_first_attempts": n_first, "refused": n_ref, "share": round(n_ref / n_first, 3) if n_first else None,
                       "last_accepted_first_attempt_utc": last_accepted.get(g).isoformat() if g in last_accepted else None}
    # standard system prompt from the stored cache of one Opus decision
    any_game = D["games"][5]
    for idx, d in any_game["decisions"].items():
        if any_game["pmodel"][d["player"]] == "Opus":
            break
    rec = json.loads(Path(corpus.REPO / any_game["run"] / "recovery_prompts.json").read_text())
    std_sys = rec[d["player"]]
    diff = list(difflib.unified_diff(std_sys.splitlines(), alt_sys.splitlines(), "standard", "action_only", lineterm="", n=0))
    res["refusal_strings"] = {k: v for k, v in refusal_texts.items()}
    res["finish_reasons"] = {f"{a}/{b}": v for (a, b), v in finish.items()}
    res["opus_decisions"] = decisions_opus
    res["opus_first_attempt_refused"] = first_refused
    res["opus_attempt_chains"] = {" > ".join(f"{c}:{o}" for c, o in k): v for k, v in chains.items()}
    res["opus_private_memory_window"] = dict(memory_empty)
    res["refusals_by_condition"] = {f"{m}|{c}": [refused_by_cond[(m, c)], n] for (m, c), n in attempts_by_cond.items()}
    res["per_game"] = per_game
    res["g1_4_ten_minute_bins_utc"] = {k: v for k, v in sorted(bins.items())}
    res["system_prompt_diff"] = diff
    res["standard_system_prompt"] = std_sys
    res["action_only_system_prompt"] = alt_sys
    res["reasoning_tokens"] = {m: {"records_with_field": len(v), "missing": tok_missing[m], "zero": tok_zero[m],
                                   "mean": round(st.mean(v), 2) if v else None, "median": st.median(v) if v else None,
                                   "max": max(v) if v else None} for m, v in tokens.items()}
    res["completion_tokens"] = {m: {"n": len(v), "mean": round(st.mean(v), 1), "max": max(v)} for m, v in completion.items()}
    res["attempts_without_usage"] = dict(unpriced)
    res["cost_usd"] = {"usage_cost_sum": {m: round(v, 4) for m, v in cost_usage.items()},
                       "upstream_inference_cost_sum": {m: round(v, 4) for m, v in cost_upstream.items()},
                       "byok_aware_rule": {m: round(v, 4) for m, v in cost_rule.items()},
                       "totals": {"usage_cost": round(sum(cost_usage.values()), 4), "upstream": round(sum(cost_upstream.values()), 4),
                                  "byok_aware": round(sum(cost_rule.values()), 4)}}
    (OUT / "conditions.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    r = main()
    for k in ("refusal_strings", "finish_reasons", "opus_decisions", "opus_first_attempt_refused", "opus_attempt_chains",
              "opus_private_memory_window", "refusals_by_condition", "per_game", "g1_4_ten_minute_bins_utc", "reasoning_tokens",
              "completion_tokens", "attempts_without_usage", "cost_usd"):
        print(k, json.dumps(r[k], indent=0)[:1800])
    print("\n".join(r["system_prompt_diff"]))
