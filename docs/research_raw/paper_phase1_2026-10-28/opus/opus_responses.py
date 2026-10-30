"""Opus phase-1 response, channel and memory audit, version opus_phase1_v1.

Independent of sol/ and astra/ code. Reads decisions.jsonl (ledger) and events.jsonl.
Counts availability of channels, not their meaning. No channel is treated as access
to latent intent. Writes only to this directory.

Channels per decision (what each is, who can see it during play):
- public_message: engine event; every player sees it in the public timeline (last 20 items).
- private_thought: engine event; only the author sees it, in "your_private_thoughts_last_10".
- assistant content text: provider message content; nobody sees it during play.
- provider reasoning: message.reasoning / reasoning_details (text, summary, encrypted);
  nobody sees it during play. Text may be a provider summary; encrypted is opaque.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from opus_reduce import HERE, MODEL_LABEL, game_dirs, load_jsonl  # noqa: E402

NAME_RE = re.compile(r'"name"\s*:\s*"([a-z_]+)"')


def message_of(attempt):
    raw = attempt.get("raw_response") or {}
    choices = raw.get("choices") or [{}]
    return choices[0].get("message") or {}, choices[0]


def parse_content_call(content):
    """Return (status, name, args) for a JSON tool-like object written in content."""
    if not isinstance(content, str) or not content.strip():
        return "empty", None, None
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):] if "{" in text else text
    try:
        obj = json.loads(text)
    except ValueError:
        m = NAME_RE.search(content)
        return ("malformed_with_name", m.group(1), None) if m else ("prose", None, None)
    if isinstance(obj, dict) and isinstance(obj.get("name"), str):
        args = obj.get("parameters", obj.get("arguments"))
        if args is None:  # flat form: {"public_message": ..., "name": ...}
            args = {k: v for k, v in obj.items() if k != "name"}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except ValueError:
                pass
        return "json_call", obj["name"], args
    return "json_other", None, None


def norm(s):
    return " ".join(s.split()) if isinstance(s, str) else s


def selected_attempt(row):
    """The attempt whose tool call became the applied action, or None for engine fallback."""
    if row.get("fallback_used"):
        return None
    final = row.get("final_action") or {}
    for a in reversed(row.get("attempts") or []):
        if a.get("outcome") == "valid":
            call = a.get("parsed_tool_call") or {}
            if call.get("name") == final.get("action"):
                return a
    return None


def main():
    per_model = defaultdict(Counter)
    chains = defaultdict(Counter)
    mismatches, memory_age = [], defaultdict(list)
    refusal_by_game_model = defaultdict(lambda: [0, 0])
    first_refusal_turn = {}
    for gno, run, _ in game_dirs():
        rows = load_jsonl(run / "decisions.jsonl")
        events = load_jsonl(run / "events.jsonl")
        cfg = json.loads((run / "run_config.json").read_text())
        label = {p["player_id"]: MODEL_LABEL[p["openrouter_model_id"]] for p in cfg["players"]}
        thoughts = {e["payload"]["decision_id"]: e["payload"]["thought"] for e in events if e["type"] == "LLM_PRIVATE_THOUGHT"}
        publics = {e["payload"]["decision_id"]: e["payload"]["message"] for e in events if e["type"] == "LLM_PUBLIC_MESSAGE"}
        for row in rows:
            m = label[row["player_id"]]
            if row["phase"] == "decision_started":
                mem = (row.get("prompt_payload") or {}).get("game_state", {}).get("memory", {})
                priv = mem.get("your_private_thoughts_last_10") or []
                newest = max((x["turn_index"] for x in priv), default=None)
                memory_age[m].append(None if newest is None else row["turn_index"] - newest)
                continue
            c = per_model[m]
            did = row["decision_id"]
            c["decisions"] += 1
            atts = row.get("attempts") or []
            c["attempts"] += len(atts)
            chain = " -> ".join(f"{a.get('response_condition')}:{a.get('outcome')}" for a in atts)
            chains[m][chain] += 1
            refused = [a for a in atts if a.get("outcome") == "refused"]
            c["refused_attempts"] += len(refused)
            c["decisions_with_refusal"] += bool(refused)
            refusal_by_game_model[(gno, m)][0] += bool(refused)
            refusal_by_game_model[(gno, m)][1] += 1
            if refused and (gno, m) not in first_refusal_turn:
                first_refusal_turn[(gno, m)] = row["turn_index"]
            c["fallback_decisions"] += bool(row.get("fallback_used"))
            c["private_thought_events"] += did in thoughts
            c["private_thought_events_nonfallback"] += did in thoughts and not row.get("fallback_used")
            c["public_nonempty"] += bool((publics.get(did) or "").strip())
            sel = selected_attempt(row)
            if sel is None:
                c["no_selected_model_attempt"] += 1
                continue
            msg, choice = message_of(sel)
            c["selected_condition:" + str(sel.get("response_condition"))] += 1
            content = msg.get("content")
            c["selected_content_nonempty"] += bool(isinstance(content, str) and content.strip())
            details = msg.get("reasoning_details") or []
            kinds = {d.get("type") for d in details}
            c["selected_reasoning_text"] += bool((msg.get("reasoning") or "").strip())
            c["selected_reasoning_encrypted"] += "reasoning.encrypted" in kinds
            c["selected_reasoning_summary_type"] += "reasoning.summary" in kinds
            c["selected_reasoning_text_type"] += "reasoning.text" in kinds
            status, cname, cargs = parse_content_call(content)
            c["content_" + status] += 1
            tool = sel.get("parsed_tool_call") or {}
            tname = tool.get("name")
            try:
                targs = json.loads(tool.get("arguments") or "{}")
            except ValueError:
                targs = None
            if cname is not None and cname != tname:
                rec = {"game": gno, "model": m, "decision_id": did, "turn": row["turn_index"],
                       "decision_type": row["decision_type"], "content_status": status,
                       "content_name": cname, "tool_name": tname, "applied": row["final_action"]["action"],
                       "response_condition": sel.get("response_condition")}
                if isinstance(cargs, dict) and isinstance(targs, dict):
                    rec["args_equal_exact"] = cargs == targs
                    rec["args_equal_normalized"] = ({k: norm(v) for k, v in cargs.items()} ==
                                                    {k: norm(v) for k, v in targs.items()})
                    rec["public_equal"] = norm(cargs.get("public_message")) == norm(targs.get("public_message"))
                    rec["private_equal"] = norm(cargs.get("private_thought")) == norm(targs.get("private_thought"))
                    rec["non_message_args_equal"] = ({k: v for k, v in cargs.items() if k not in ("public_message", "private_thought")} ==
                                                     {k: v for k, v in targs.items() if k not in ("public_message", "private_thought")})
                reasoning = msg.get("reasoning") or ""
                rec["reasoning_mentions_content_name"] = cname.replace("_", " ").split()[0] in reasoning.lower()
                mismatches.append(rec)
                c["content_tool_name_mismatch"] += 1
            elif cname is not None:
                c["content_tool_name_match"] += 1
    with open(HERE / "opus_response_mismatches.jsonl", "w") as fh:
        for r in mismatches:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    mem_summary = {}
    for m, ages in memory_age.items():
        known = [a for a in ages if a is not None]
        mem_summary[m] = {"decisions": len(ages), "empty_private_memory": sum(a is None for a in ages),
                          "median_age_turns_of_newest_private_note": statistics.median(known) if known else None,
                          "share_newest_note_older_than_20_turns": round(sum(a > 20 for a in known) / len(ages), 4),
                          "share_newest_note_older_than_50_turns": round(sum(a > 50 for a in known) / len(ages), 4)}
    mm = [r for r in mismatches]
    mm_summary = {
        "total": len(mm),
        "by_model": dict(Counter(r["model"] for r in mm)),
        "by_content_status": dict(Counter(r["content_status"] for r in mm)),
        "args_equal_exact": sum(bool(r.get("args_equal_exact")) for r in mm),
        "args_equal_normalized": sum(bool(r.get("args_equal_normalized")) for r in mm),
        "public_equal": sum(bool(r.get("public_equal")) for r in mm),
        "public_and_private_equal": sum(bool(r.get("public_equal")) and bool(r.get("private_equal")) for r in mm),
        "non_message_args_equal": sum(bool(r.get("non_message_args_equal")) for r in mm),
        "name_pairs": dict(Counter(f"{r['content_name']}->{r['tool_name']}" for r in mm).most_common(15)),
        "applied_trade_acceptances": sum(r["applied"] == "accept_trade" for r in mm),
    }
    opus_refusal_share_by_game = {g: round(v[0] / v[1], 3) for (g, m), v in sorted(refusal_by_game_model.items()) if m == "Opus"}
    out = {"version": "opus_phase1_v1", "per_model": {m: dict(c) for m, c in sorted(per_model.items())},
           "attempt_chains": {m: dict(c.most_common()) for m, c in sorted(chains.items())},
           "content_tool_mismatch": mm_summary, "private_memory_staleness": mem_summary,
           "opus_refusal_share_by_game": opus_refusal_share_by_game,
           "opus_first_refusal_turn_by_game": {g: t for (g, m), t in sorted(first_refusal_turn.items()) if m == "Opus"}}
    (HERE / "opus_response_audit.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
