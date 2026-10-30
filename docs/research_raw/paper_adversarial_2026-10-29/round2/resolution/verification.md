# Verification record

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_adversarial_2026-10-29/round2/resolution/independent_audit.py
PYTHONDONTWRITEBYTECODE=1 python/.venv/bin/python docs/research_raw/paper_adversarial_2026-10-29/round2/resolution/parser_probes.py
```

Both commands completed with exit code 0. `verification_stdout.log` retains the census output. `independent_results.json` contains exact case IDs, file paths, JSONL lines, response hashes, and event IDs. `parser_probe_results.json` records eight passed parser-boundary probes. The scripts write only inside this review directory.

The independent audit checks:

- All 20 runs in the phase 1 source manifest, 6,989 resolved decisions, and 8,679 attempts.
- All resolved final actions equal their canonical action-log records, all resolved decisions are marked applied, and every nonfallback decision has one valid attempt at the last attempt index.
- All 663 construction-tool-listed applied ENDs have an actual matching-turn `TURN_ENDED` event in the emitted event IDs.
- All 66 fallback decisions have the expected invalid-resolution action metadata while still matching the applied final action. Defaults remain in the applied denominator.
- Construction-listed and END counts exactly equal the reviewed JSON.
- The selected conflict case set exactly equals the reviewed JSON, with the independent all-attempt scan reproducing 138 selected strict-JSON, 9 discarded strict-JSON, and 1 selected malformed explicit-name conflict.
- Every one of the 148 conflict response files has HTTP status 200, one choice, one tool call, no true request stream field, and ordinary JSON raw response text. Its content, name, arguments, and choices match the canonical attempt. The raw body equals saved `response_json`; attempts only add `openrouter_generation` outside choices.
- Historical formatter code at both recorded source revisions reproduces all 6,989 initial timeline lists exactly at their `LLM_DECISION_REQUESTED` events.
- Independent event classification yields 232 self-partner counters, 44 reversed acceptances, and 26 misattributed rejections.
- All 32 focal selected user payloads equal the actual selected request user payload. Their timelines equal the initial timelines.
- All focal defect hits occur only at `$.game_state.memory.public_timeline_last_20[i]`, match the independently reconstructed row, and refer to events earlier than the corresponding request event. The reviewed exact row sets are reproduced.
- A recursive structured-name scan of valid unnamed JSON finds no additional `name`, `action`, `tool_name`, or `function_name` values outside the parser's top-level rule.

The source hashes for all 60 canonical event/action/decision files, the phase 1 manifest, the reviewed output, and the three relevant historical Python files for each revision are in `independent_results.json.source_hashes`. The 148 raw conflict response hashes are stored in their individual records. `source_snapshot_audit_conditions.py` and `source_snapshot_conditions_audit.json` freeze the exact reviewed shared files.

The source revisions checked were `42f85183fa772b2ab3759cc49987e5ed6cc9efcc` and `d6808534a831862682a6940f394c6c87bb2691cb`. `git diff` against each revision showed no current differences in `prompting.py`, `decision_resolver.py`, or `openrouter_client.py`. The formatter imports use the repository's existing Python environment. Bytecode writing is disabled. No external service is called.

Two development-run failures were resolved within the review code: the system Python lacked the existing environment's `httpx`, and dynamically executed historical modules needed registration in `sys.modules` for dataclass annotation handling. An initially overstrong full-object equality check exposed only the known `openrouter_generation` metadata addition; the final audit records that exact difference and checks the response choices and argument bytes. An initially overstrong `decision_meta.valid` assertion was replaced with the explicit fallback check described above. These were verification-script assumptions, not data repairs.

I did not rerun the whole repository verification suite because this review changes no runtime behavior. I did not run a new engine replay, call a model, inspect provider-internal traces, or infer attention and intent. The script's named-content parser is intentionally matched to the reviewed rule for count reproduction; separate probes and channel-shape counts expose its limits. The formatter derivation is independent of the earlier formatter audit's event and exposure lists.
