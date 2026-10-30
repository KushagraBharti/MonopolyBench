"""Rebuild candidates.jsonl from cand_src/*.txt block files (line-oriented, no JSON escaping).

Block format:
@@ G01-C001
title: ...
priority: high|medium|low
tags: a, b
party: p1 Opus | initiator
lines: 16,17,18        (source lines of game-XX.jsonl; resolved to decision ids + key event ids)
quote: 17 | exact substring of that decision's public message (verified)
fin: numeric evidence line (repeatable)
exposure: 18 > p4        (speaker line > recipient pid; verified against recipient timelines)
endpoint:, observed:, inferred:, support:, contrary:, alt:, followup:, uncertainty:
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

KEY_EVENTS = {"PROPERTY_PURCHASED", "PROPERTY_TRANSFERRED", "TRADE_PROPOSED", "TRADE_COUNTERED", "TRADE_REJECTED",
              "TRADE_ACCEPTED", "RENT_PAID", "HOUSE_BUILT", "HOTEL_BUILT", "HOUSE_SOLD", "HOTEL_SOLD", "PROPERTY_MORTGAGED",
              "PROPERTY_UNMORTGAGED", "AUCTION_STARTED", "AUCTION_ENDED", "GAME_ENDED", "SENT_TO_JAIL"}
cache = {}
def G(g):
    if g not in cache:
        cache[g] = load_game(g)
    return cache[g]

def exposure(g, spk_line, rcp):
    rows = G(g)
    s = rows[spk_line - 1]
    msg = s["applied_action"].get("public_message")
    spid, turn = s["player_id"], s["turn_index"]
    seen = []
    for i in range(spk_line, len(rows)):
        r = rows[i]
        if r["player_id"] != rcp:
            continue
        for t in r["observation"]["memory"]["public_timeline_last_20"]:
            if t.get("player_id") == spid and t.get("turn_index") == turn and t.get("message") == msg:
                seen.append(i + 1)
                break
    nxt = [i + 1 for i in range(spk_line, len(rows)) if rows[i]["player_id"] == rcp][:1]
    return {"speaker_line": spk_line, "speaker": spid, "recipient": rcp, "message_in_recipient_timeline_at_lines": seen[:6],
            "n_recipient_decisions_with_message_visible": len(seen),
            "recipient_next_decision_line": nxt[0] if nxt else None,
            "exposed_at_next_decision": bool(nxt and nxt[0] in seen)}

def parse(path, g_of):
    blocks, cur = [], None
    for raw in open(path):
        raw = raw.rstrip("\n")
        if raw.startswith("@@"):
            cur = {"candidate_id": raw[2:].strip(), "_f": []}
            blocks.append(cur); continue
        if cur is None or not raw.strip() or raw.startswith("#"):
            continue
        m = re.match(r"^(\w+):\s?(.*)$", raw)
        if m:
            cur["_f"].append((m.group(1), m.group(2)))
        elif cur["_f"]:
            cur["_f"][-1] = (cur["_f"][-1][0], cur["_f"][-1][1] + " " + raw.strip())
    return blocks

out, problems = [], []
for path in sorted(glob.glob(OUT + "/cand_src/*.txt")):
    for b in parse(path, None):
        cid = b["candidate_id"]
        g = int(re.match(r"G(\d+)-", cid).group(1))
        rec = {"candidate_id": cid, "game": g, "display_numbering": "display number = 1-based line in public_review/game-XX.jsonl; decision_id suffix is zero-based (#113 = dec-000112)", "label_policy": "public-message/action inconsistencies are observable inconsistencies with cause and intent unresolved", "reviewer": "Sonnet 5.5 (sonnet_public)", "decision_refs": [], "quotes": [],
               "financial_evidence": [], "parties_and_roles": [], "exposure_checks": [], "supporting_evidence": [],
               "contrary_evidence": [], "alternative_interpretations": [], "tags": []}
        lines = []
        for k, v in b["_f"]:
            if k == "title": rec["title"] = v
            elif k == "priority": rec["priority"] = v.strip()
            elif k == "tags": rec["tags"] = [t.strip() for t in v.split(",") if t.strip()]
            elif k == "party": rec["parties_and_roles"].append(v)
            elif k == "lines":
                lines = [int(x) for x in re.findall(r"\d+", v)]
            elif k == "quote":
                ln, _, sub = v.partition("|")
                ln = int(ln.strip()); sub = sub.strip()
                r = G(g)[ln - 1]
                msg = r["applied_action"].get("public_message") or ""
                ok = sub in msg
                if not ok: problems.append("%s quote not found at line %d: %s" % (cid, ln, sub[:50]))
                rec["quotes"].append({"line": ln, "speaker": r["player_id"], "model": MODEL_SHORT.get(r["model"]), "display_number": ln, "decision_id": r["decision_id"], "text": sub, "verified_exact_substring": ok})
            elif k == "fin": rec["financial_evidence"].append(v)
            elif k == "exposure":
                a, _, rc = v.partition(">")
                rec["exposure_checks"].append(exposure(g, int(a.strip()), rc.strip()))
            elif k == "endpoint": rec["endpoint"] = v
            elif k == "observed": rec["observed_conduct"] = v
            elif k == "inferred": rec["inferred_motive_or_interpretation"] = v
            elif k == "support": rec["supporting_evidence"].append(v)
            elif k == "contrary": rec["contrary_evidence"].append(v)
            elif k == "alt": rec["alternative_interpretations"].append(v)
            elif k == "followup": rec["follow_up"] = v
            elif k == "uncertainty": rec["uncertainty"] = v
            else: problems.append("%s unknown field %s" % (cid, k))
        for ln in lines:
            r = G(g)[ln - 1]
            ev = [e["event_id"].split("-evt-")[-1] for e in r["events"] if e["type"] in KEY_EVENTS]
            rec["decision_refs"].append({"line": ln, "display_number": ln, "decision_id_zero_based_suffix": int(r["decision_id"].rsplit("-dec-", 1)[1]), "decision_id": r["decision_id"], "player_id": r["player_id"], "turn_index": r["turn_index"],
                                         "decision_type": r["decision_type"], "action": r["applied_action"]["action"],
                                         "key_event_seqs": ev, "event_seq_range": [r["events"][0]["seq"], r["events"][-1]["seq"]]})
        rec.setdefault("follow_up", "No specific follow-up beyond core-team verification of the cited lines.")
        for need in ("title", "priority", "endpoint", "observed_conduct", "uncertainty"):
            if need not in rec: problems.append("%s missing %s" % (cid, need))
        out.append(rec)
import os as _os
_rv = {}
for _f in sorted(glob.glob(OUT + "/revisions/g*_change_log.jsonl")):
    for _l in open(_f):
        _e = json.loads(_l)
        _t = _e["target"]
        if _t.startswith("G") and "-C" in _t:
            _rv.setdefault(_t.split(" ")[0], []).append({k: _e[k] for k in ("change_id", "field", "reason", "revision_source")})
for r in out:
    r["current_version"] = "v2" if r["candidate_id"] in _rv else "v1"
    r["revision_history"] = _rv.get(r["candidate_id"], [])
ids = [r["candidate_id"] for r in out]
dups = {i for i in ids if ids.count(i) > 1}
for d in dups: problems.append("duplicate id " + d)
with open(OUT + "/candidates.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
by = {}
for r in out: by[r["game"]] = by.get(r["game"], 0) + 1
print("candidates:", len(out), by, "problems:", len(problems))
for p in problems[:25]: print("PROBLEM:", p)
