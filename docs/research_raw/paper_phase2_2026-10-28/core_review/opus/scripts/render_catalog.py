"""Render catalog entries for one game compactly for reading. Drops only per-entry boilerplate that is
identical across public entries (display_numbering, label_policy, reviewer) and compresses decision_refs
to '#line dec-suffix player action ev[a-b] keys'. All other fields are printed in full. Read-only."""
import json, sys
BOIL = {"display_numbering", "label_policy", "reviewer", "decision_refs", "game", "candidate_id"}
g = int(sys.argv[1]); only = sys.argv[2] if len(sys.argv) > 2 else None
for line in open("candidate_catalog.jsonl"):
    r = json.loads(line)
    if (r["game"] or 0) != g or (only and r["source_reviewer"] != only):
        continue
    print("=" * 100)
    print(r["catalog_id"], r["source_reviewer"], r["entry_status"], r["source_file"].split("reviewers/")[-1], f'L{r["source_start_line"]}-{r["source_end_line"]}')
    if "source_entry" in r:
        e = r["source_entry"]
        refs = " | ".join(f'#{d["display_number"]} {d["decision_id"][-6:]} {d["player_id"]} {d["action"]} ev{d.get("event_seq_range")}' for d in e.get("decision_refs", []))
        print("REFS:", refs)
        for k, v in e.items():
            if k in BOIL:
                continue
            if k == "quotes":
                v = [f'#{q["display_number"]} {q["speaker"]}/{q["model"]}: "{q["text"]}" exact={q.get("verified_exact_substring")}' for q in v]
            if k == "exposure_checks":
                v = [f'spk#{x.get("speaker_line")} {x.get("speaker")}->{x.get("recipient")} vis@{x.get("message_in_recipient_timeline_at_lines")} n={x.get("n_recipient_decisions_with_message_visible")} next#{x.get("recipient_next_decision_line")} exposed_next={x.get("exposed_at_next_decision")}' for x in v]
            if k == "revision_history":
                v = [f'{x.get("change_id")}:{x.get("field")}: {x.get("reason")}' for x in v]
            print(f"{k.upper()}:", json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v)
    else:
        print("SECTION:", r.get("section"), "NUM:", r.get("source_number"))
        print(r["raw_markdown"])
