"""Verify every quote ADDED by the Opus and Fable drafts against canonical
decision records, and check recipient delivery of each public message.

For each generated quote macro this script
  1. parses speaker / channel / game / decision / attempt from the card label,
  2. reloads the resolved decision from saved_games/.../decisions.jsonl,
  3. checks the actor's configured model, the selected attempt index and that
     every span (split on the editorial ellipsis) is a contiguous substring of
     the named applied field,
  4. for public messages, looks for the full applied message in the delivered
     prompt of every other live player's next decision and reports where it
     first appears (trade-thread history or public timeline).

It reads records only. It does not check the 28 baseline quotes (those were
re-verified by Sol, Fable and Astra and are byte-identical across drafts).
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from common import MODEL, PKG, decisions, dump  # noqa: E402

FILES = {
    "opus": os.path.join(PKG, "full_drafts", "opus", "sections", "opus_quotes.tex"),
    "fable_5_2": os.path.join(PKG, "full_drafts", "fable_5_2", "sections", "quotes_supplement.tex"),
}
CARD = re.compile(r"\\DeclareTranscriptQuote\{([^}]*)\}\{([^}]*)\}\{(.*)\}\s*$")
INLINE = re.compile(r"\\DeclareInlineQuote\{([^}]*)\}\{(.*)\}\s*$")
INLINE_SRC = {  # from the Fable draft's temporal section and its supplement manifest
    "fx-g16-plan": ("Grok", "applied private note", 16, 103),
    "fx-g16-note": ("Grok", "applied private note", 16, 159),
    "fx-g16-public": ("Grok", "public message", 16, 159),
}
CHANNEL_FIELD = {"public message": "public_message", "applied private note": "private_thought"}


def untex(s: str) -> list[str]:
    parts = re.split(r"\s*\\textnormal\{\[\\ldots\]\}\s*", s)
    out = []
    for p in parts:
        p = p.replace("\\textasciitilde{}", "~").replace("\\char34{}", '"')
        p = re.sub(r"\\([$%&#_{}])", r"\1", p)
        p = p.replace("\\par ", "").strip()
        out.append(p)
    return out


def selected_attempt(res):
    """Index of the attempt whose parsed action became the applied action."""
    atts = res.get("attempts") or []
    meta = res.get("sequence_meta") or {}
    for key in ("selected_attempt_index", "applied_attempt_index"):
        if key in meta:
            return meta[key]
    return len(atts) - 1 if atts else None


def delivery(game, idx, speaker_pid, message):
    """Where does the applied public message next appear for other players?"""
    decs = decisions(game)
    found = {}
    needle = message.strip()
    for j in range(idx + 1, min(idx + 40, max(decs) + 1)):
        st = decs[j].get("started")
        if not st or st["player_id"] == speaker_pid:
            continue
        pid = st["player_id"]
        if pid in found:
            continue
        raw = st.get("prompt_payload_raw") or json.dumps(st.get("prompt_payload"))
        try:
            payload = json.loads(raw)
        except Exception:
            payload = st.get("prompt_payload")
        text = json.dumps(payload, ensure_ascii=False)
        hit = json.dumps(needle, ensure_ascii=False)[1:-1] in text
        where = None
        if hit:
            mem = json.dumps(payload["game_state"].get("memory", {}), ensure_ascii=False)
            act = json.dumps(payload.get("action_state", {}), ensure_ascii=False)
            enc = json.dumps(needle, ensure_ascii=False)[1:-1]
            where = [w for w, blob in (("public_timeline", mem), ("action_state", act)) if enc in blob]
        found[pid] = {"decision": j, "present": hit, "where": where}
    return found


rows = []
for draft, path in FILES.items():
    for line in open(path):
        m = CARD.match(line.strip())
        mi = INLINE.match(line.strip())
        if m:
            key, label, body = m.groups()
            speaker, channel, gd, att, kind = [x.strip() for x in label.split("·")]
            g, d = re.match(r"G(\d+) d(\d+)", gd).groups()
            g, d = int(g), int(d)
            att = int(att.split()[-1])
        elif mi:
            key, body = mi.groups()
            speaker, channel, g, d = INLINE_SRC[key]
            att, kind = None, "inline"
        else:
            continue
        rec = decisions(g)[d]
        res = rec["resolved"]
        fa = res["final_action"]
        field = CHANNEL_FIELD[channel]
        text = fa.get(field) or ""
        spans = untex(body)
        pos, ok, cursor = [], True, 0
        for sp in spans:
            i = text.find(sp, cursor)
            pos.append(i)
            ok = ok and i >= 0
            cursor = max(i, 0) + len(sp)
        row = {
            "draft": draft,
            "key": key,
            "game": g,
            "decision": d,
            "label_speaker": speaker,
            "actor_model": MODEL[res["openrouter_model_id"]],
            "speaker_matches": MODEL[res["openrouter_model_id"]] == speaker,
            "channel": channel,
            "spans_found_in_applied_field": ok,
            "span_offsets": pos,
            "is_full_field": len(spans) == 1 and spans[0] == text.strip(),
            "label_kind": kind,
            "label_attempt": att,
            "attempt_count": len(res.get("attempts") or []),
            "retry_used": res.get("retry_used"),
            "fallback_used": res.get("fallback_used"),
            "applied_action": fa["action"],
            "turn": res["turn_index"],
            "decision_type": res["decision_type"],
            "line": res["_line"],
        }
        if att is not None:
            # a label saying attempt k must agree with how many attempts exist
            row["attempt_label_consistent"] = att == row["attempt_count"] - 1
        if channel == "public message":
            row["delivery"] = delivery(g, d, res["player_id"], text)
            row["delivered_to_all_checked"] = all(v["present"] for v in row["delivery"].values())
        rows.append(row)

summary = {
    "quotes_checked": len(rows),
    "by_draft": {d: sum(r["draft"] == d for r in rows) for d in FILES},
    "spans_found": sum(r["spans_found_in_applied_field"] for r in rows),
    "speaker_matches": sum(r["speaker_matches"] for r in rows),
    "attempt_label_consistent": sum(r.get("attempt_label_consistent", True) for r in rows),
    "labelled_full_field_but_not_full": [
        r["key"] for r in rows if r["label_kind"] == "full field" and not r["is_full_field"]
    ],
    "labelled_excerpt_but_full": [
        r["key"] for r in rows if r["label_kind"] == "excerpt" and r["is_full_field"]
    ],
    "public_messages": sum(r["channel"] == "public message" for r in rows),
    "public_delivered_to_every_other_player_checked": sum(
        r.get("delivered_to_all_checked", False) for r in rows
    ),
    "failures": [
        r["key"]
        for r in rows
        if not (r["spans_found_in_applied_field"] and r["speaker_matches"] and r.get("attempt_label_consistent", True))
    ],
}
dump("new_quote_checks.json", {"summary": summary, "rows": rows})
print(json.dumps(summary, indent=1))
for r in rows:
    dl = r.get("delivery")
    dls = "" if dl is None else " | " + ", ".join(
        f"{p}@d{v['decision']}:{'Y' if v['present'] else 'N'}{'/' + '+'.join(v['where']) if v['where'] else ''}" for p, v in sorted(dl.items())
    )
    print(
        f"{r['draft']:9s} {r['key']:24s} G{r['game']} d{r['decision']} t{r['turn']} {r['actor_model']:6s} "
        f"{r['channel'][:7]:7s} found={r['spans_found_in_applied_field']} full={r['is_full_field']} "
        f"att={r['label_attempt']}/{r['attempt_count']} {r['applied_action']}{dls}"
    )
