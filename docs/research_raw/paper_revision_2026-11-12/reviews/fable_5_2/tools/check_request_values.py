#!/usr/bin/env python3
"""What board values does a liquidation request contain?

Reads every stored ``LIQUIDATION_DECISION`` request and reports (a) the
structural fields of the action state, (b) whether any field carries a price,
mortgage value, sale value or the rule that selling buildings releases
mortgages, and (c) for the sixteen necessary-collateral first decisions,
whether each dollar figure the first text states for a released mortgage
occurs anywhere in the request (state, timeline or the agent's own notes).

Stored records only.  No engine, replay or model query.
"""
from __future__ import annotations

import json
import re
from collections import Counter

from ro_corpus import board, load_all, write_json

B = board()["by_key"]


def walk_keys(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{prefix}{k}"
            yield from walk_keys(v, f"{prefix}{k}.")
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_keys(v, prefix + "[].")


SIXTEEN = [(1, 476), (2, 216), (4, 270), (4, 308), (5, 263), (6, 185), (8, 257), (11, 203),
           (12, 190), (13, 195), (17, 234), (17, 254), (18, 309), (18, 313), (20, 291), (20, 327)]


def main():
    games = load_all()
    out = {}
    keys = Counter()
    n = 0
    sys_mentions = Counter()
    timeline_money_mortgage = 0
    timeline_action_kinds = Counter()
    user_text_has_rule = 0
    tool_desc_has_value = 0
    for g in games.values():
        for k in range(g.n):
            st = g.started[k]
            if st["decision_type"] != "LIQUIDATION_DECISION":
                continue
            n += 1
            for kk in set(walk_keys(st["prompt_payload"]["action_state"])):
                keys[kk] += 1
            for kk in set(walk_keys(st["prompt_payload"]["game_state"]["you"])):
                keys["you." + kk] += 1
            sysmsg = [m["content"] for m in st["prompt_messages"] if m["role"] == "system"]
            for word in ("mortgage", "sell", "house", "price", "release", "unlock"):
                if any(word in (s or "").lower() for s in sysmsg):
                    sys_mentions[word] += 1
            for row in st["prompt_payload"]["game_state"]["memory"]["public_timeline_last_20"]:
                act = row.get("action") or ""
                timeline_action_kinds[row.get("event_type")] += 1
                if "mortgag" in act.lower() and "$" in act:
                    timeline_money_mortgage += 1
            user = "".join(m["content"] for m in st["prompt_messages"] if m["role"] == "user" and isinstance(m["content"], str))
            scen_note = st["prompt_payload"]["action_state"]["scenario"].get("note", "")
            if re.search(r"releas|unlock|after (you )?sell|become[s]? mortgageable", scen_note, re.I):
                user_text_has_rule += 1
    out["liquidation_requests"] = n
    out["action_state_and_you_fields"] = dict(sorted(keys.items()))
    out["fields_named_like_values"] = sorted(k for k in keys if re.search(r"price|value|rent|cost|mortgage_value|proceeds", k, re.I))
    out["system_prompt_mentions"] = dict(sys_mentions)
    out["scenario_note_states_release_rule"] = user_text_has_rule
    out["timeline_rows_with_mortgage_and_dollar"] = timeline_money_mortgage
    out["timeline_event_types"] = dict(timeline_action_kinds.most_common())

    # example scenario note and an example timeline mortgage row
    g = games[5]
    out["example_scenario"] = g.started[263]["prompt_payload"]["action_state"]
    ex = None
    for gg in games.values():
        for k in range(gg.n):
            st = gg.started[k]
            for row in st["prompt_payload"]["game_state"]["memory"]["public_timeline_last_20"]:
                if row.get("event_type") and "MORTGAG" in row["event_type"]:
                    ex = row
                    break
            if ex:
                break
        if ex:
            break
    out["example_timeline_mortgage_row"] = ex

    # --- the sixteen: stated released-mortgage figures and where they could come from
    rows = []
    for (gn, k) in SIXTEEN:
        g = games[gn]
        st, rs = g.started[k], g.resolved[k]
        sc = st["prompt_payload"]["action_state"]["scenario"]
        you = st["prompt_payload"]["game_state"]["you"]
        listed = sc["options"]["mortgageable_space_keys"]
        unlisted = [h["space_key"] for h in you["holdings"]["owned"] if not h["mortgaged"] and h["space_key"] not in listed]
        note = rs["final_action"].get("private_thought")
        text = note or g.provider_reasoning(k) or ""
        user = "".join(m["content"] for m in st["prompt_messages"] if m["role"] == "user" and isinstance(m["content"], str))
        mem = st["prompt_payload"]["game_state"]["memory"]
        notes_text = " ".join(t.get("thought") or "" for t in mem.get("your_private_thoughts_last_10", []))
        timeline_text = " ".join((t.get("action") or "") + " " + (t.get("message") or "") for t in mem["public_timeline_last_20"])
        true_vals = {key: B[key]["mortgage"] for key in unlisted}
        total_unlisted = sum(true_vals.values())
        dollars_in_text = [int(x.replace(",", "")) for x in re.findall(r"\$?\b(\d{1,2},\d{3}|\d{2,4})\b", text)]
        # figures that equal a single released mortgage value, or the released total
        hits = sorted({d for d in dollars_in_text if d in set(true_vals.values()) or d == total_unlisted})
        where = {}
        for d in hits:
            pat = re.compile(r"\$" + re.escape(f"{d:,}") + r"\b|\$" + str(d) + r"\b")
            where[d] = {"in_own_notes_in_request": bool(pat.search(notes_text)),
                        "in_timeline_in_request": bool(pat.search(timeline_text))}
        rows.append({
            "game": gn, "decision": k, "model": g.model[st["player_id"]],
            "channel": "applied private note" if note else "provider-returned text",
            "unlisted_true_values": true_vals, "unlisted_total": total_unlisted,
            "text": text.strip(),
            "figures_equal_to_a_released_value_or_total": hits,
            "figure_presence_in_request_memory": where,
            "own_notes_in_request": len(mem.get("your_private_thoughts_last_10", [])),
            "own_notes_mention_mortgage": bool(re.search(r"mortgag", notes_text, re.I)),
        })
    out["sixteen_requests"] = rows
    write_json("check_request_values.json", out)
    brief = {k: v for k, v in out.items() if k not in ("sixteen_requests",)}
    print(json.dumps(brief, indent=1)[:6000])
    for r in rows:
        print(r["game"], r["decision"], r["model"], r["channel"], "| released:", r["unlisted_true_values"],
              "| figures matching:", r["figures_equal_to_a_released_value_or_total"],
              "| in memory:", r["figure_presence_in_request_memory"],
              "| notes mention mortgage:", r["own_notes_mention_mortgage"])


if __name__ == "__main__":
    main()
