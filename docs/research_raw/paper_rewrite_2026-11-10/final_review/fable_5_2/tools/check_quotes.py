"""Independently match every declared quote card to its original decision-record field.

Source read only. Usage: python3 -I check_quotes.py <repo_root> <out_json>
"""
import json
import re
import sys
from pathlib import Path

repo, out_path = Path(sys.argv[1]), Path(sys.argv[2])
pkg = repo / "docs/research_raw/paper_rewrite_2026-11-10"
sec = pkg / "integrated/sections"
runs = {r["game"]: r["source_run"] for r in json.loads((pkg / "data/agenda_offers.json").read_bytes())}
cache = {}


def resolved(g, d):
    if g not in cache:
        cache[g] = {int(r["decision_id"].rsplit("-", 1)[1]): r
                    for r in map(json.loads, (repo / runs[g] / "decisions.jsonl").read_bytes().splitlines())
                    if r["phase"] == "decision_resolved"}
    return cache[g][d]


def untex(s):
    s = s.replace("\\textnormal{[\\ldots]}", "\x00")
    for a, b in (("\\char34{}", '"'), ("\\textasciitilde{}", "~"), ("\\$", "$"), ("\\_", "_"), ("\\{", "{"),
                 ("\\}", "}"), ("\\%", "%"), ("\\&", "&"), ("\\#", "#"), ("\\par ", ""), ("\\par", "")):
        s = s.replace(a, b)
    return [f.strip() for f in s.split("\x00")]


def parse(path):
    out = []
    for line in path.read_text().splitlines():
        if not line.startswith("\\DeclareTranscriptQuote{"):
            continue
        # three balanced groups
        groups, i = [], len("\\DeclareTranscriptQuote")
        for _ in range(3):
            assert line[i] == "{"
            depth, j = 0, i
            while True:
                c = line[j]
                if c == "\\":
                    j += 2
                    continue
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            groups.append(line[i + 1:j])
            i = j + 1
        out.append(groups)
    return out


def field_of(rec, attempt_index, channel):
    a = rec["attempts"][attempt_index]
    call = a.get("parsed_tool_call") or {}
    args = call.get("arguments") or call.get("args") or {}
    if isinstance(args, str):
        args = json.loads(args)
    msg = (((a.get("raw_response") or {}).get("choices") or [{}])[0].get("message") or {})
    if channel == "public message":
        return [args.get("public_message"), rec["final_action"].get("public_message")]
    if channel == "applied private note":
        return [args.get("private_thought"), rec["final_action"].get("private_thought")]
    if channel == "returned provider explanation":
        cands = [msg.get("reasoning")]
        for d in msg.get("reasoning_details") or []:
            cands += [d.get("text"), d.get("summary")]
        return cands
    if channel.startswith("assistant content"):
        return [a.get("assistant_content")]
    raise ValueError(channel)


used = set(re.findall(r"\\TranscriptQuote\{([^}]+)\}", "".join(p.read_text() for p in sec.glob("*.tex"))))
results = []
for fname in ("transcript_quotes.tex", "opus_quotes.tex", "fable_quotes.tex"):
    for qid, meta, text in parse(sec / fname):
        parts = [p.strip() for p in meta.split("·")]
        speaker, channel, loc, att, kind = parts
        g, d = re.match(r"G(\d+) d(\d+)", loc).groups()
        rec = resolved(int(g), int(d))
        cands = [c for c in field_of(rec, int(att.split()[1]), channel) if c]
        frags = untex(text)
        ok = any(all(f in c for f in frags) for c in cands)
        full = any(c.strip() == frags[0] for c in cands) if len(frags) == 1 else False
        # the field the applied action actually carried, for public messages
        applied_pub = rec["final_action"].get("public_message") if channel == "public message" else None
        results.append({"id": qid, "file": fname, "used_in_paper": qid in used, "speaker": speaker, "channel": channel,
                        "game": int(g), "decision": int(d), "attempt": att, "label": kind, "found": ok,
                        "equals_full_field": full, "label_consistent": (kind == "full field") == full,
                        "n_attempts": len(rec["attempts"]),
                        "attempt_outcome": rec["attempts"][int(att.split()[1])]["outcome"],
                        "speaker_matches_model": {"Sol": "gpt", "Gemini": "gemini", "Opus": "opus", "Grok": "grok"}[speaker]
                        in rec["openrouter_model_id"],
                        "matches_applied_public": (all(f in (applied_pub or "") for f in frags)
                                                   if channel == "public message" else None)})
summary = {"declared": len(results), "used_in_paper": sum(r["used_in_paper"] for r in results),
           "found": sum(r["found"] for r in results),
           "not_found": [r["id"] for r in results if not r["found"]],
           "label_inconsistent": [(r["id"], r["label"], r["equals_full_field"], r["used_in_paper"]) for r in results
                                  if not r["label_consistent"]],
           "speaker_mismatch": [r["id"] for r in results if not r["speaker_matches_model"]],
           "public_not_applied": [r["id"] for r in results if r["matches_applied_public"] is False],
           "declared_unused": [r["id"] for r in results if not r["used_in_paper"]]}
out_path.write_text(json.dumps({"summary": summary, "rows": results}, indent=1) + "\n")
print(json.dumps(summary, indent=1))
