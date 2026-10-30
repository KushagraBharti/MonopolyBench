"""Link reviewed source entries without treating a graph component as an episode.

The manually authored episode_linkage remains authoritative as a proposal.
Shared cited decisions identify overlap, not identical semantic claims.
"""

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from check_additional_economics import units

HERE = Path(__file__).resolve().parent


def main():
    catalog = [json.loads(line) for line in (HERE.parent / "candidate_catalog.jsonl").read_text().splitlines()]
    reviewed = {r["catalog_id"]: r for r in map(json.loads, (HERE / "case_reviews.jsonl").read_text().splitlines())}
    sample = {(r["game"], r["decision_id"]): r for r in
              map(json.loads, (HERE / "negative_control_reviews.jsonl").read_text().splitlines())}
    source_units = {g: units(g) for g in range(1, 21)}
    anchors = {}
    unresolved = {}
    inferred_games = {}
    for entry in catalog:
        ident = entry["catalog_id"]
        assert ident in reviewed and reviewed[ident]["episode_linkage"]
        cited = set()
        misses = []
        game = entry["game"]
        if "source_entry" in entry:
            for row in entry["source_entry"].get("decision_refs", []):
                suffix = int(row["decision_id_zero_based_suffix"])
                assert source_units[game][suffix][0]["decision_id"] == row["decision_id"]
                cited.add((game, suffix))
        else:
            text = entry["raw_markdown"]
            if game is None:
                found = re.search(r"\bgame\s+(\d+)\b", text, re.I)
                game = int(found.group(1)) if found else None
                inferred_games[ident] = game
            if game is not None:
                # Only explicit d/decision anchors, never currency, events,
                # page numbers or packet-part numbers.
                pattern = r"\b(?:d|decisions?\s+)(\d{1,6})(?:[–−-](\d{1,6}))?"
                for match in re.finditer(pattern, text, re.I):
                    start = int(match.group(1))
                    stop = int(match.group(2) or start)
                    if stop < start or stop - start > 1000:
                        misses.append(match.group(0))
                        continue
                    for suffix in range(start, stop + 1):
                        if suffix in source_units[game]:
                            cited.add((game, suffix))
                        else:
                            misses.append(f"G{game}d{suffix}")
        anchors[ident] = cited
        unresolved[ident] = misses

    reverse = defaultdict(set)
    for ident, cited in anchors.items():
        for anchor in cited:
            reverse[anchor].add(ident)
    links = []
    for entry in catalog:
        ident = entry["catalog_id"]
        overlapping = defaultdict(list)
        original_anchors = []
        samples = []
        for game, suffix in sorted(anchors[ident]):
            unit, ref = source_units[game][suffix]
            original_anchors.append({"game": game, "decision_id": unit["decision_id"], "source": ref})
            for other in reverse[game, suffix] - {ident}:
                overlapping[other].append(unit["decision_id"])
            if (game, unit["decision_id"]) in sample:
                samples.append(unit["decision_id"])
        links.append({"catalog_id": ident, "manual_episode_linkage_proposal": reviewed[ident]["episode_linkage"],
                      "initial_verdict": reviewed[ident]["initial_verdict"], "entry_status": entry["entry_status"],
                      "source_cited_original_decisions": original_anchors,
                      "shared_decision_source_entries": dict(sorted(overlapping.items())),
                      "complete_common_originals_in_source_citations": samples,
                      "unresolved_source_citation_tokens": unresolved[ident],
                      "game_inferred_from_explicit_source_wording": inferred_games.get(ident),
                      "limits": "A citation link confirms which original exists, not that its full provider bundle was read or that the extractor's proposition is true. Shared decisions can support different or opposed claims. No connected-component episode count or prevalence is inferred."})
    assert len(links) == len(reviewed) == 614
    (HERE / "source_overlap_links.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in links))
    summary = {"reviewed_source_entries_linked": len(links), "public_entries": sum("source_entry" in e for e in catalog),
               "historical_entries": sum(e["entry_status"] == "historical" for e in catalog),
               "entries_with_explicit_valid_citations": sum(bool(r["source_cited_original_decisions"]) for r in links),
               "entries_with_shared_decision_citations": sum(bool(r["shared_decision_source_entries"]) for r in links),
               "unresolved_citation_tokens": {r["catalog_id"]: r["unresolved_source_citation_tokens"] for r in links if r["unresolved_source_citation_tokens"]},
               "method": "Conservative citation graph joined to all manually proposed episode linkages. Full-channel d-ranges are source quotations, not new adjudicated episodes. Exact original evidence anchors and duplicate sources are retained, and historical entries remain marked. No distinct episode count reported.",
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE / "source_overlap_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
