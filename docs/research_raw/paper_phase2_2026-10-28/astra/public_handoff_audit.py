"""Audit public-review references and selected handoff claims against saved records.

This checks accounting and citations, not the quality of every semantic annotation.
Only this script's derived report is written; reviewer and canonical files are read-only.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PHASE = HERE.parent
FOUNDATION = ROOT / "docs/research_raw/paper_phase1_2026-10-28/astra"
PUBLIC = PHASE / "reviewers/sonnet_public"


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    units = rows(FOUNDATION / "review_unit_ledger.jsonl")
    by_id = {u["decision_id"]: u for u in units}
    by_game_index = {(u["game"], int(u["decision_id"].rsplit("-", 1)[1])): u for u in units}
    source_paths = set()

    def packet(game, index):
        unit = by_game_index[game, index]
        path = ROOT / unit["packet"]
        source_paths.add(path)
        return json.loads(path.read_text().splitlines()[unit["packet_line"] - 1])

    actions = {}
    runs = {}
    for game in range(1, 21):
        run = ROOT / packet(game, 0)["source_run"]
        runs[game] = run
        source_paths.add(run / "actions.jsonl")
        for record in rows(run / "actions.jsonl"):
            actions[record["decision_id"]] = record

    coverage = rows(PUBLIC / "coverage.jsonl")
    candidates = rows(PUBLIC / "candidates.jsonl")
    candidate_ids = {c["candidate_id"] for c in candidates}
    covered = [r["decision_id"] for r in coverage]
    assert len(covered) == len(set(covered)) == len(units) == 6989
    assert set(covered) == set(by_id) == set(actions)
    assert len(candidates) == len(candidate_ids) == 441
    shortlist_text = (PUBLIC / "corpus_shortlist.md").read_text()
    shortlist_ids = set(re.findall(r"G\d{2}-C\d{3}", shortlist_text))
    assert shortlist_ids <= candidate_ids
    ref_errors, exact_quote_misses, coverage_dangling = [], [], []
    quote_count = 0
    for row in coverage:
        for cid in row.get("candidate_ids", []):
            if cid not in candidate_ids:
                coverage_dangling.append({"decision_id": row["decision_id"], "candidate_id": cid})
    for candidate in candidates:
        for ref in candidate.get("decision_refs", []):
            did = ref.get("decision_id")
            unit = by_id.get(did)
            if not unit or unit["game"] != candidate["game"]:
                ref_errors.append({"candidate": candidate["candidate_id"], "reference": ref})
            elif ref.get("display_number") != int(did.rsplit("-", 1)[1]) + 1:
                ref_errors.append({"candidate": candidate["candidate_id"], "reference": ref})
        for quote in candidate.get("quotes", []):
            if not quote.get("verified_exact_substring"):
                continue
            quote_count += 1
            did = quote.get("decision_id")
            message = actions.get(did, {}).get("action", {}).get("public_message") or ""
            if not quote.get("text") or quote["text"] not in message:
                exact_quote_misses.append({"candidate": candidate["candidate_id"], "quote": quote,
                                           "canonical_public_message": message})

    house_checks = []
    for game, indices in [(4, [189, 208, 215, 228]), (5, [298, 302, 305])]:
        for index in indices:
            p = packet(game, index)
            before = p["initial_prompt"]["payload"]["game_state"]["bank"]["houses_remaining"]
            next_p = packet(game, index + 1)
            after = next_p["initial_prompt"]["payload"]["game_state"]["bank"]["houses_remaining"]
            house_checks.append({"game": game, "decision_id": p["decision_id"],
                                 "houses_before": before, "houses_at_next_decision": after,
                                 "public_message": p["applied_action_record"]["action"].get("public_message"),
                                 "building_events": [e for e in p["canonical_event_segment"]
                                                     if "HOUSE" in e["type"] or "HOTEL" in e["type"]]})
    assert [r["houses_before"] for r in house_checks[:4]] == [0, 0, 0, 0]
    assert [(r["houses_before"], r["houses_at_next_decision"]) for r in house_checks[4:]] == [(6, 5), (5, 2), (1, 0)]

    state_packet = packet(20, 310)
    holdings = state_packet["initial_prompt"]["payload"]["game_state"]["you"]["holdings"]
    deed_flags = {r["space_key"]: r["mortgaged"] for r in holdings["owned"]
                  if r["space_key"] in {"INDIANA_AVENUE", "ILLINOIS_AVENUE"}}
    assert deed_flags == {"INDIANA_AVENUE": True, "ILLINOIS_AVENUE": True}
    compact_path, compact_block = None, None
    for path in sorted((PUBLIC / "reading/g20").glob("*.txt")):
        text = path.read_text()
        match = re.search(r"^#311 .*?(?=^#312 |\Z)", text, re.M | re.S)
        if match:
            compact_path, compact_block = path, match.group(0)
            break
    assert compact_block and "IND~0,ILL~0" in compact_block
    source_paths.add(compact_path)

    fragment_hits = []
    for did, record in actions.items():
        message = record["action"].get("public_message") or ""
        if "private_thought" in message:
            fragment_hits.append({"game": by_id[did]["game"], "decision_id": did,
                                  "public_message": message})
    fragment_packet = packet(20, 1)
    parsed = fragment_packet["attempts"][0]["parsed_tool_call"]
    arguments = json.loads(parsed["arguments"])
    assert arguments["public_message"] == fragment_packet["applied_action_record"]["action"]["public_message"]

    schema_path = ROOT / "contracts/schemas/action.schema.json"
    schema = json.loads(schema_path.read_text())
    action_names = sorted({item["properties"]["action"]["const"] for item in schema["oneOf"]})
    assert not any("message" in name or "chat" in name for name in action_names)
    source_paths.add(schema_path)
    prices_before_offer = [{"decision_id": did, "public_message": record["action"].get("public_message")}
                           for did, record in actions.items() if by_id[did]["game"] == 20
                           and int(did.rsplit("-", 1)[1]) < 78
                           and "400" in (record["action"].get("public_message") or "")]
    provenance = Counter((r.get("reviewer"), r.get("model")) for r in coverage)
    progress = json.loads((PUBLIC / "progress.json").read_text())
    source_paths.update(PUBLIC / name for name in ["coverage.jsonl", "candidates.jsonl", "progress.json", "corpus_shortlist.md"])
    source_paths.add(FOUNDATION / "review_unit_ledger.jsonl")
    source_paths.add(ROOT / "python/packages/engine/src/monopoly_engine/engine.py")
    source_paths.add(ROOT / "python/packages/arena/src/monopoly_arena/prompting.py")
    report = {
        "version": "astra_public_handoff_audit_v1",
        "scope": "Reference integrity and selected factual checks. Not exhaustive semantic adjudication or proof of reading.",
        "coverage": {"unique_canonical_ids": len(covered), "exact_id_set_match": True,
                     "by_game": dict(Counter(r["game"] for r in coverage)),
                     "provenance": [{"reviewer": k[0], "model": k[1], "decisions": v} for k, v in provenance.items()],
                     "narratives_marked_unfinished": [g for g, v in progress["games"].items() if not v["narrative_final"]]},
        "candidates": {"total": len(candidates), "priority": dict(Counter(c["priority"] for c in candidates)),
                       "shortlist_numbered_items": len(re.findall(r"^\d+\. ", shortlist_text, re.M)),
                       "shortlist_distinct_referenced_candidates": len(shortlist_ids),
                       "reference_errors": ref_errors, "asserted_exact_quotes_checked": quote_count,
                       "asserted_exact_quote_misses": exact_quote_misses,
                       "coverage_dangling_candidate_refs": coverage_dangling},
        "house_supply_checks": house_checks,
        "G20_C019_correction": {"decision_id": state_packet["decision_id"], "canonical_mortgaged_flags": deed_flags,
                                "compact_file": str(compact_path.relative_to(ROOT)), "compact_block": compact_block,
                                "verdict": "The alleged state inconsistency is unsupported: both sources mark the deeds mortgaged."},
        "public_private_thought_literal_scan": {"denominator": len(actions), "hits": fragment_hits,
                                               "scope": "Literal key scan of applied public messages, not a semantic leakage detector.",
                                               "G20_dec1_parsed_tool_public_matches_applied": True,
                                               "cause": "Unresolved; present in saved parsed tool arguments before engine application."},
        "G20_C003_channel_check": {"contract_actions": action_names, "public_400_mentions_before_dec78": prices_before_offer,
                                   "verdict": "No direct-message action exists in this contract. DM me is an invitation, not evidence of private contact; no private-contact finding is supported."},
        "unmortgage_float_demonstration": [{"mortgage_value": value, "float_product": repr(value * 1.1),
                                           "implemented_ceil": math.ceil(value * 1.1),
                                           "integer_ten_percent_ceil": (value * 11 + 9) // 10}
                                          for value in [75, 100, 110, 175]],
        "source_hashes": [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in sorted(source_paths)],
    }
    output = HERE / "public_handoff_audit.json"
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"coverage": len(covered), "candidates": len(candidates), "shortlist_items": report["candidates"]["shortlist_numbered_items"],
                      "reference_errors": len(ref_errors), "quote_checks": quote_count, "quote_misses": len(exact_quote_misses),
                      "dangling_coverage_refs": len(coverage_dangling), "fragment_hits": len(fragment_hits), "output": str(output)}))


if __name__ == "__main__":
    main()
