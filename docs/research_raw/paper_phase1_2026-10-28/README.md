# Paper foundation, phase 1

This folder contains downstream research work on the fixed 20-game October cohort. It does not change game rules, model prompts, response policy or canonical run files. Historical games remain separate references. The paper has no target venue yet.

The research question covers sustained capability, alignment-relevant social conduct, and the design of inspectable long-horizon environments. Economic and social behavior will be analyzed together. The current cohort compares configured agents; it does not establish a trend in alignment as underlying capabilities increase.

## Reproduce the foundation

From the repository root, with the repository Python environment already installed:

```sh
python3 docs/research_raw/paper_phase1_2026-10-28/reproduce_phase1.py --include-peers
```

This runs focused tests, rebuilds economic tables, checks independent reconstructions, verifies canonical source hashes, and prepares the chronological review packets. It makes no provider calls. Outputs and logs stay in this folder. Without `--include-peers`, the command omits Opus's and Fable's independent runs. Regeneration overwrites generated analysis outputs and resets the generated pending-review ledger; future completed review annotations must be stored separately.

Start with `phase1_results.json`. Its economic tables come from Sol's reducer, independently checked against Astra's decision observations and Opus's reconstruction. Each command and its log are recorded. The reports state what each check establishes. Accounting consistency is not evidence that a strategy is optimal or that a social label is correct.

## Research and writing

- `astra/phase1_memo.md`: Astra's independent work, integrated findings and remaining objections.
- `astra/methods_draft.tex`: working methods and framing, with peer revisions incorporated.
- `astra/behavior_review_contract.json`: proposed economic and social review rules, awaiting pilot adjudication.
- `astra/reference_scope.md`: primary-source scope notes for the user's twelve reference anchors.
- `sol/phase1_memo.md`: independent economics, scenario validation, channel inventory and research assessment.
- `opus/opus_phase1_memo.md`: independent settlements, snapshot reconciliation, interface conditions and branching checks.
- `sol_round2/round2_memo.md`: direct peer debate, public-message delivery audit and co-written methods proposals.
- `fable/fable_phase1_memo.md`: independent settlement, bankruptcy, jail-card, management-access and candidate-surrender checks.

Directories prevent concurrent edits from colliding. They do not give researchers exclusive ownership of subjects. All four researchers contribute across framing, evidence, interpretation and writing.

## Next phase: complete behavioral review

`astra/review_packet_manifest.json` lists the chronological packets. They retain all 50,918 events, 6,989 applied decisions, 8,679 attempts and physical response references. Three physical response envelopes differ from their ledger representation and are retained explicitly. Redundant JSON representations point to an equivalent retained value; encrypted fields remain opaque references. Original source files remain authoritative.

`astra/review_unit_ledger.jsonl` is a generated inventory with every semantic-review status still pending. Parsing records or preparing packets does not count as reading and interpreting them. Separate extraction agents will perform the complete first pass. The four researchers will challenge the labels, revisit strong claims and unflagged counterexamples, and jointly write the findings.

Exposure must be traced through actual prompts over time. A logged public utterance need not appear in the shared timeline, and absence from the latest prompt does not erase earlier delivery. Keep original negotiation initiators separate from final-terms authors; separate terminal inheritance from opportunities with follow-up; preserve applied actions when response channels disagree.
