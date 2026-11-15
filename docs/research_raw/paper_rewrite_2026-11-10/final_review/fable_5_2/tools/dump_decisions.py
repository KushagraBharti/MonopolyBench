"""Print compact views of canonical decision records (source read only; no engine).

Usage: python3 -I dump_decisions.py <repo_root> <game> <first> <last> [full]
"""
import json
import sys
from pathlib import Path

repo, g, lo, hi = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
full = len(sys.argv) > 5
pkg = repo / "docs/research_raw/paper_rewrite_2026-11-10"
runs = {r["game"]: r["source_run"] for r in json.loads((pkg / "data/agenda_offers.json").read_bytes())}
LABEL = {"openai/gpt-6.1-sol": "Sol", "google/gemini-4-argon": "Gemini",
         "anthropic/claude-opus-5.5": "Opus", "x-ai/grok-4.7": "Grok"}
recs = [json.loads(x) for x in (repo / runs[g] / "decisions.jsonl").read_bytes().splitlines()]
idx = lambda r: int(r["decision_id"].rsplit("-", 1)[1])
st = {idx(r): r for r in recs if r["phase"] == "decision_started"}
rs = {idx(r): r for r in recs if r["phase"] == "decision_resolved"}
W = 100000 if full else 700
for i in range(lo, hi + 1):
    s, r = st[i], rs[i]
    you = s["prompt_payload"]["game_state"]["you"]
    sc = s["prompt_payload"]["action_state"].get("scenario", {})
    fa = r["final_action"]
    print(f"--- G{g} d{i} turn {s['turn_index']} {s['player_id']} {LABEL[s['openrouter_model_id']]} "
          f"{s['decision_type']} cash={you['cash']} pos={you['position']}")
    avail = [a["action"] if isinstance(a, dict) else a for a in s["prompt_payload"]["action_state"]["available_actions"]]
    print("   avail:", avail)
    keep = {k: v for k, v in sc.items() if k not in ("note", "options")}
    if keep:
        print("   scenario:", json.dumps(keep)[:W])
    if full and sc.get("options"):
        print("   options:", json.dumps(sc["options"])[:W])
    print(f"   APPLIED {fa['action']} {json.dumps(fa.get('args'))[:W]} fallback={r['fallback_used']} "
          f"retry={r['retry_used']} cond={(r.get('sequence_meta') or {}).get('response_condition')}")
    print("   PUBLIC:", fa.get("public_message"))
    for k, a in enumerate(r["attempts"]):
        call = a.get("parsed_tool_call") or {}
        args = call.get("arguments") or call.get("args") or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}
        msg = (((a.get("raw_response") or {}).get("choices") or [{}])[0].get("message") or {})
        reasoning = msg.get("reasoning") or ""
        print(f"   att{k} outcome={a['outcome']} cond={a.get('response_condition')} call={call.get('name')} "
              f"verr={json.dumps(a.get('validation_errors'))[:300]}")
        if a.get("assistant_content"):
            print("      CONTENT:", a["assistant_content"][:W].replace("\n", " "))
        if args.get("private_thought"):
            print("      NOTE:", args["private_thought"][:W])
        if reasoning:
            print("      REASONING:", reasoning[:W].replace("\n", " "))
