"""Census of response and information conditions from canonical decision records.

Fresh arithmetic on saved records only: prompt text, refusal messages, attempt
outcomes, usage fields and delivered private-note windows.  No model call.
"""
from __future__ import annotations

import collections
import difflib
import hashlib
import json
import statistics
from datetime import datetime, timezone

from corpus import MODELS, load_all, write_json


def h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def main() -> None:
    games = load_all()
    out: dict = {"sources": {n: g.source_hashes() for n, g in games.items()}}

    # ---- system prompts -------------------------------------------------
    std_prompts = collections.Counter()
    std_text = {}
    rec_prompts = collections.Counter()
    rec_text = {}
    other_retry_prompts = collections.Counter()
    cond_counts = collections.Counter()
    for g in games.values():
        for k in range(g.n_decisions):
            st = g.started[k]
            sys_txt = st["prompt_messages"][0]["content"]
            std_prompts[h(sys_txt)] += 1
            std_text[h(sys_txt)] = sys_txt
            for i, a in enumerate(g.resolved[k]["attempts"]):
                cond_counts[(g.model[st["player_id"]], a.get("response_condition"), a.get("outcome"))] += 1
                if a.get("prompt_messages"):
                    t = a["prompt_messages"][0]["content"]
                    if a.get("response_condition") == "same_model_without_private_thought":
                        rec_prompts[h(t)] += 1
                        rec_text[h(t)] = t
                    else:
                        other_retry_prompts[h(t)] += 1
                        rec_text.setdefault(h(t), t)
    assert len(std_prompts) == 1, std_prompts
    assert len(rec_prompts) == 1, rec_prompts
    std = next(iter(std_text[k] for k in std_prompts))
    rec = next(iter(rec_text[k] for k in rec_prompts))
    diff = [
        line
        for line in difflib.unified_diff(std.splitlines(), rec.splitlines(), "standard", "action_only", lineterm="", n=0)
    ]
    out["system_prompt"] = {
        "standard_sha256": h(std),
        "standard_uses": sum(std_prompts.values()),
        "action_only_sha256": h(rec),
        "action_only_uses": sum(rec_prompts.values()),
        "standard_text": std,
        "action_only_text": rec,
        "unified_diff": diff,
        "other_attempt_system_prompts": {k: v for k, v in other_retry_prompts.items()},
        "other_attempt_system_prompt_equals_standard": all(k == h(std) for k in other_retry_prompts),
        "kept_in_action_only": {
            "deception_allowed_sentence": "Deception in public chat is allowed." in rec,
            "bluff_deceive_list": "negotiate, bluff, deceive, cooperate, intimidate" in rec,
            "personality_list": "deceptive" in rec and "manipulative" in rec,
        },
        "removed_in_action_only": {
            "private_thought_field_line": "Private Thoughts: visible only to you" not in rec,
            "true_reasoning_clause": "private thoughts should reflect true reasoning" not in rec,
        },
    }

    # ---- attempt outcomes / refusals ------------------------------------
    out["attempt_conditions"] = {" | ".join(map(str, k)): v for k, v in sorted(cond_counts.items(), key=str)}
    refusal_msgs = collections.Counter()
    finish = collections.Counter()
    per_game = {}
    first_attempt_times = collections.defaultdict(list)  # game -> (ts, refused)
    refused_decisions = 0
    first_refusals = 0
    action_only_attempts = 0
    action_only_refused = 0
    action_only_outcomes = collections.Counter()
    for g in games.values():
        pid = g.pid_of["Opus"]
        n = ref = 0
        for k in range(g.n_decisions):
            r = g.resolved[k]
            if r["player_id"] != pid:
                continue
            n += 1
            any_ref = False
            for i, a in enumerate(r["attempts"]):
                is_ref = a.get("outcome") == "refused"
                if a.get("response_condition") == "same_model_without_private_thought":
                    action_only_attempts += 1
                    action_only_refused += is_ref
                    action_only_outcomes[a.get("outcome")] += 1
                if is_ref:
                    any_ref = True
                    ch = a["raw_response"]["choices"][0]
                    refusal_msgs[ch["message"].get("refusal")] += 1
                    finish[(ch.get("finish_reason"), ch.get("native_finish_reason"))] += 1
                if i == 0:
                    ts = a.get("request_start_ms")
                    first_attempt_times[g.number].append((ts, is_ref))
                    first_refusals += is_ref
                    ref += is_ref
            refused_decisions += any_ref
        per_game[g.number] = {"opus_decisions": n, "first_attempt_refused": ref, "share": round(ref / n, 4)}
    # also check no other model has refusals
    other_ref = collections.Counter()
    for g in games.values():
        for k in range(g.n_decisions):
            r = g.resolved[k]
            for a in r["attempts"]:
                if a.get("outcome") == "refused" and g.model[r["player_id"]] != "Opus":
                    other_ref[g.model[r["player_id"]]] += 1
    timing = {}
    for n in (1, 2, 3, 4):
        rows = sorted(first_attempt_times[n])
        last_ok = max(ts for ts, refd in rows if not refd)
        before = [(ts, refd) for ts, refd in rows if ts <= last_ok]
        after = [(ts, refd) for ts, refd in rows if ts > last_ok]
        timing[n] = {
            "first_request_utc": datetime.fromtimestamp(rows[0][0] / 1000, timezone.utc).isoformat(),
            "last_request_utc": datetime.fromtimestamp(rows[-1][0] / 1000, timezone.utc).isoformat(),
            "last_non_refused_first_attempt_utc": datetime.fromtimestamp(last_ok / 1000, timezone.utc).isoformat(),
            "refused_up_to_last_ok": [sum(r for _, r in before), len(before)],
            "refused_after_last_ok": [sum(r for _, r in after), len(after)],
        }
    # pooled ten-minute bins over G1-G4
    bins = collections.OrderedDict()
    allrows = sorted(x for n in (1, 2, 3, 4) for x in first_attempt_times[n])
    t0 = datetime(2026, 10, 25, 15, 30, tzinfo=timezone.utc).timestamp() * 1000
    for ts, refd in allrows:
        b = int((ts - t0) // (10 * 60 * 1000))
        key = datetime.fromtimestamp((t0 + b * 600000) / 1000, timezone.utc).strftime("%H:%M")
        cur = bins.setdefault(key, [0, 0])
        cur[0] += refd
        cur[1] += 1
    out["opus_refusals"] = {
        "distinct_refusal_messages": len(refusal_msgs),
        "refusal_message": next(iter(refusal_msgs)),
        "refused_attempts": sum(refusal_msgs.values()),
        "finish_reasons": {str(k): v for k, v in finish.items()},
        "decisions_with_any_refusal": refused_decisions,
        "first_attempt_refusals": first_refusals,
        "action_only_attempts": action_only_attempts,
        "action_only_refused": action_only_refused,
        "action_only_outcomes": dict(action_only_outcomes),
        "per_game": per_game,
        "g1_g4_timing": timing,
        "g1_g4_ten_minute_bins_refused_of_first_attempts": bins,
        "refusals_by_other_models": dict(other_ref),
    }

    # ---- final resolution by model --------------------------------------
    res = {m: collections.Counter() for m in MODELS}
    n_attempts = {m: collections.Counter() for m in MODELS}
    final_cond = {m: collections.Counter() for m in MODELS}
    invalid_after_action_only = 0
    for g in games.values():
        for k in range(g.n_decisions):
            r = g.resolved[k]
            m = g.model[r["player_id"]]
            res[m]["decisions"] += 1
            res[m]["retry_used"] += bool(r["retry_used"])
            res[m]["fallback_used"] += bool(r["fallback_used"])
            n_attempts[m][len(r["attempts"])] += 1
            final_cond[m][r["sequence_meta"].get("response_condition")] += 1
            res[m]["has_private_thought_applied"] += bool((r["final_action"] or {}).get("private_thought"))
            if m == "Opus" and r["fallback_used"]:
                conds = [a.get("response_condition") for a in r["attempts"]]
                if "same_model_without_private_thought" in conds:
                    invalid_after_action_only += 1
    out["resolution"] = {
        m: {
            **dict(res[m]),
            "attempt_count_distribution": dict(n_attempts[m]),
            "final_response_condition": dict(final_cond[m]),
        }
        for m in MODELS
    }
    out["resolution"]["Opus"]["engine_default_after_action_only_attempt"] = invalid_after_action_only

    # ---- Opus trade responses under action-only -------------------------
    tr = collections.Counter()
    for g in games.values():
        for k in range(g.n_decisions):
            r = g.resolved[k]
            if r["decision_type"] == "TRADE_RESPONSE_DECISION" and g.model[r["player_id"]] == "Opus":
                tr[r["sequence_meta"].get("response_condition")] += 1
    out["opus_trade_response_conditions"] = dict(tr)

    # ---- delivered private-note windows ---------------------------------
    notes = {m: collections.Counter() for m in MODELS}
    for g in games.values():
        for k in range(g.n_decisions):
            st = g.started[k]
            m = g.model[st["player_id"]]
            mem = st["prompt_payload"]["game_state"]["memory"]
            thoughts = mem["your_private_thoughts_last_10"]
            notes[m]["prompts"] += 1
            if not thoughts:
                notes[m]["empty"] += 1
            texts = [t.get("thought", "") for t in thoughts]
            notes[m]["timeline_entries_total"] += len(mem["public_timeline_last_20"])
            if thoughts and all(("fallback" in t.lower() or "invalid" in t.lower()) for t in texts):
                notes[m]["only_fallback_like"] += 1
    out["private_note_windows"] = {m: dict(notes[m]) for m in MODELS}

    # ---- usage fields ---------------------------------------------------
    usage = {}
    for m in MODELS:
        usage[m] = {
            "attempts": 0,
            "usage_present": 0,
            "reasoning_field_present": 0,
            "reasoning_zero": 0,
            "reasoning_tokens": [],
            "completion_tokens": [],
            "usage_cost_sum": 0.0,
            "upstream_cost_sum": 0.0,
            "byok_true": 0,
            "no_cost_record": 0,
        }
    for g in games.values():
        for k in range(g.n_decisions):
            r = g.resolved[k]
            m = g.model[r["player_id"]]
            for a in r["attempts"]:
                u = usage[m]
                u["attempts"] += 1
                us = (a.get("raw_response") or {}).get("usage")
                if not us:
                    u["no_cost_record"] += 1
                    continue
                u["usage_present"] += 1
                u["completion_tokens"].append(us.get("completion_tokens") or 0)
                det = us.get("completion_tokens_details") or {}
                if "reasoning_tokens" in det and det["reasoning_tokens"] is not None:
                    u["reasoning_field_present"] += 1
                    u["reasoning_tokens"].append(det["reasoning_tokens"])
                    u["reasoning_zero"] += det["reasoning_tokens"] == 0
                u["usage_cost_sum"] += us.get("cost") or 0.0
                u["upstream_cost_sum"] += ((us.get("cost_details") or {}).get("upstream_inference_cost")) or 0.0
                u["byok_true"] += bool(us.get("is_byok"))
    tot_cost = tot_up = 0.0
    for m in MODELS:
        u = usage[m]
        rt, ct = u.pop("reasoning_tokens"), u.pop("completion_tokens")
        u["reasoning_tokens_mean_where_reported"] = round(statistics.fmean(rt), 2) if rt else None
        u["reasoning_tokens_median_where_reported"] = statistics.median(rt) if rt else None
        u["reasoning_tokens_max"] = max(rt) if rt else None
        u["completion_tokens_mean_per_attempt_with_usage"] = round(statistics.fmean(ct), 2) if ct else None
        u["completion_tokens_max"] = max(ct) if ct else None
        tot_cost += u["usage_cost_sum"]
        tot_up += u["upstream_cost_sum"]
        u["usage_cost_sum"] = round(u["usage_cost_sum"], 6)
        u["upstream_cost_sum"] = round(u["upstream_cost_sum"], 6)
    out["usage"] = usage
    out["usage_totals"] = {
        "sum_usage_cost_field": round(tot_cost, 6),
        "sum_upstream_inference_cost_field": round(tot_up, 6),
        "note": "usage.cost is the OpenRouter-billed amount (zero under BYOK); cost_details.upstream_inference_cost is the provider-side charge. "
        "They overlap and must not be added. Neither is an invoice.",
    }

    # ---- channels available on the selected response --------------------
    chan = {m: {"selected": 0, "with_assistant_content": 0, "with_returned_reasoning_text": 0, "note_lengths": []} for m in MODELS}
    for g in games.values():
        for k in range(g.n_decisions):
            r = g.resolved[k]
            m = g.model[r["player_id"]]
            sel = [a for a in r["attempts"] if a.get("outcome") == "valid"]
            if not sel:
                continue
            a = sel[-1]
            c = chan[m]
            c["selected"] += 1
            c["with_assistant_content"] += bool(a.get("assistant_content"))
            msg = ((a.get("raw_response") or {}).get("choices") or [{}])[0].get("message", {})
            c["with_returned_reasoning_text"] += bool(msg.get("reasoning"))
            pt = r["final_action"].get("private_thought") or ""
            if pt and not r["fallback_used"]:
                c["note_lengths"].append(len(pt))
    for m in MODELS:
        nl = chan[m].pop("note_lengths")
        chan[m]["model_written_notes"] = len(nl)
        chan[m]["median_note_characters"] = statistics.median(nl) if nl else None
    out["channels"] = chan

    # ---- request parameters (saved call intents) -------------------------
    import glob
    from corpus import COLLECTIONS
    keys = collections.Counter()
    tool_choice = collections.Counter()
    n_int = 0
    for coll in COLLECTIONS:
        for f in glob.glob(str(coll / "game-*" / "cloud" / "calls" / "*.intent.json")):
            pl = json.loads(open(f).read())["payload"]
            n_int += 1
            keys.update(pl.keys())
            tool_choice[f"{pl.get('model')}|{pl.get('tool_choice')}"] += 1
    out["request_payloads"] = {"files": n_int, "payload_keys": dict(keys), "tool_choice_by_model": dict(tool_choice)}

    # ---- tool descriptions delivered with standard prompts ---------------
    from corpus import game_dirs
    tools = collections.OrderedDict()
    n_tool_files = 0
    for gn, run in game_dirs().items():
        for f in glob.glob(str(run / "prompts" / "*_tools.json")):
            if "_retry" in f:
                continue
            n_tool_files += 1
            for t in json.loads(open(f).read()):
                fn = t["function"]
                d = tools.setdefault(fn["name"], {"descriptions": collections.Counter(), "prompts": 0})
                d["descriptions"][fn["description"]] += 1
                d["prompts"] += 1
    out["tool_descriptions"] = {
        "standard_tool_files": n_tool_files,
        "tools": {k: {"description": next(iter(v["descriptions"])), "distinct_descriptions": len(v["descriptions"]), "prompts": v["prompts"]} for k, v in tools.items()},
    }

    # ---- action-only schema and payload census ---------------------------
    import copy

    def strip_private(tools_):
        t_ = copy.deepcopy(tools_)
        for x in t_:
            par = x["function"]["parameters"]
            par.get("properties", {}).pop("private_thought", None)
            if "required" in par:
                par["required"] = [r_ for r_ in par["required"] if r_ != "private_thought"]
        return t_

    sch = {"action_only_decisions": 0, "schemas_equal_after_dropping_private_thought": 0, "payload_differs_only_by_response_instruction": 0}
    instr = collections.Counter()
    for g in games.values():
        for k in range(g.n_decisions):
            r = g.resolved[k]
            ao = [a for a in r["attempts"] if a.get("response_condition") == "same_model_without_private_thought"]
            if not ao:
                continue
            sch["action_only_decisions"] += 1
            base = g.run / "prompts" / f"decision_{r['decision_id']}"
            std_tools = json.loads(base.with_name(base.name + "_tools.json").read_text())
            rec_tools = json.loads(base.with_name(base.name + "_retry1_tools.json").read_text())
            sch["schemas_equal_after_dropping_private_thought"] += strip_private(std_tools) == rec_tools and std_tools != rec_tools
            pay = dict(ao[0]["prompt_payload"])
            ri = pay.pop("response_instruction", None)
            instr[ri] += 1
            sch["payload_differs_only_by_response_instruction"] += pay == g.started[k]["prompt_payload"] and ri is not None
    sch["distinct_response_instructions"] = len(instr)
    sch["response_instruction"] = next(iter(instr))
    out["action_only_census"] = sch

    # ---- effort and sampling parameters ---------------------------------
    eff = collections.Counter()
    for g in games.values():
        for k in range(g.n_decisions):
            eff[json.dumps(g.started[k]["reasoning"], sort_keys=True)] += 1
    out["recorded_reasoning_setting"] = dict(eff)

    # ---- phase-specific board parameters in prompts ---------------------
    phase = collections.defaultdict(collections.Counter)
    for g in games.values():
        for k in range(g.n_decisions):
            st = g.started[k]
            sc = st["prompt_payload"]["action_state"].get("scenario", {})
            dt = st["decision_type"]
            phase[dt]["prompts"] += 1
            for f in ("price", "house_cost", "rent", "group"):
                phase[dt]["has_" + f] += f in sc
    out["board_fields_by_phase"] = {k: dict(v) for k, v in phase.items()}

    write_json("a1_conditions.json", out)
    brief = {k: v for k, v in out.items() if k not in ("sources",)}
    brief["system_prompt"] = {k: v for k, v in out["system_prompt"].items() if not k.endswith("_text")}
    print(json.dumps(brief, indent=1))


if __name__ == "__main__":
    main()
