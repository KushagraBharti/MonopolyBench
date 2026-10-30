# Resolution and recipient-prompt review

The numerical census and the focal exposure labels survive independent reconstruction. One generated metadata field is wrong: every `located_timeline_length` is zero because the script looks up the wrong key. The raw-response evidence excludes this application's streaming accumulator for the detected conflicts. It does not attribute the conflicts to the underlying model rather than its provider or OpenRouter.

The strongest remaining risk is interpretation. `no_detected_name_conflict` is a deliberately narrow parser result. It is not evidence of agreement across all response channels, and its detectability differs sharply across the model configurations.

## Sources and independence

I wrote `initial_position.md` and `initial_findings.md` before seeing any round 1 peer findings. A later repository search surfaced round 1 excerpts. The reconstruction below did not use their case lists, code, or conclusions. I did use the phase 1 manifest to identify the 20 saved runs and the reviewed audit to identify its finite focal case set. I did not import the prior formatter or conflict audit outputs into the independent computation.

The reviewed script snapshot has SHA-256 `e59c1988972f9d69b00f7ce480eb6eb6abbc9c482c607ffede911740540f8c06`. The reviewed JSON snapshot has SHA-256 `e798bce3843cc73e945f3b68249d572d80a58060173309c3fe43fcdb552ca918`. Copies are retained beside this review as `source_snapshot_audit_conditions.py` and `source_snapshot_conditions_audit.json`.

`independent_audit.py` reads all 6,989 resolved decisions and 8,679 attempts. It joins every final action to `actions.jsonl`, verifies that each decision is marked applied, and checks an actual `TURN_ENDED` event for every construction-tool-listed END. It verifies the unique valid final attempt for every nonfallback decision. Its full source paths, decision IDs, JSONL line numbers, request paths, and file hashes are in `independent_results.json`.

For delivery, it executes the historical `PromptMemory` formatter from source revisions `42f85183fa772b2ab3759cc49987e5ed6cc9efcc` and `d6808534a831862682a6940f394c6c87bb2691cb` over the canonical event streams. All 6,989 reconstructed initial timelines equal their saved decision-start prompt timelines. The relevant current `prompting.py`, `decision_resolver.py`, and `openrouter_client.py` files have no differences from either recorded revision. This is a formatter reproduction, not a fresh engine replay.

## Applied END census

The reviewed counts are exact for the declared population.

| Configuration | Decisions listing construction tool | Applied END | Engine default | Selected name conflict | No detected name conflict |
|---|---:|---:|---:|---:|---:|
| Sol | 399 | 236 | 4 | 0 | 232 |
| Gemini | 330 | 144 | 1 | 0 | 143 |
| Opus | 223 | 104 | 61 | 0 | 43 |
| Grok | 273 | 179 | 0 | 24 | 155 |
| Total | 1,225 | 663 | 66 | 24 | 573 |

The denominator is a decision whose initial `prompt_payload.action_state.available_actions` lists `build_houses_or_hotel`. A repeated management decision after another action counts again. This is neither a first-window denominator nor a count of independent opportunities, games, players, or color sets. The script does not establish that a particular nonempty build sequence was executable in every listed decision. Any claim about foregone feasible investment needs the separate legality audit.

The 66 defaults are applied engine actions following unsuccessful resolution. The action-log `decision_meta.valid` is false for those defaults, while the resolved record is marked applied and the matching END event exists. That metadata must not be used to discard defaults from an applied-action denominator.

All 43 nonfallback Opus ENDs came from the originally configured Opus model, but 42 used `same_model_without_private_thought`; only G3 d000134 used `standard`. They cannot all be described as choices under the original prompt condition. The selected-attempt ledger contains no alternate-model success in this cohort. This distinction is about the deployed response policy, not model intent.

## Conflict reconciliation and parser limits

| Content parser and attempt population | Count |
|---|---:|
| Selected attempts, valid JSON with top-level string `name` | 138 |
| Discarded attempts, valid JSON with top-level string `name` | 9 |
| Selected attempt, malformed content with one distinct explicit `name` | 1 |
| Selected inclusive total | 139 |
| All-attempt strict-JSON total | 147 |
| All-attempt inclusive total | 148 |

The nine discarded attempts are all attempt 0 with outcome `illogical`: G1 d000079, G2 d000275, G3 d000448, G3 d000571, G4 d000277, G6 d000084, G8 d000160, G11 d000287, and G17 d000394. They cannot be counted as the selected action for their decisions. The full decision IDs and raw HTTP paths are in `independent_results.json` under `conflicts`.

The malformed selected case is `campaign-8d77f7b822c6458fa9a5be0e884f74ef-6-f542507ff9-dec-000224`, G19 attempt 0. Its content concatenates an argument object with a second object containing `"name": "declare_bankruptcy"`, then extra closing braces. The received tool is `mortgage_property`, and that is the applied action. The explicit textual name is inspectable, but the content is not valid JSON. Calling all 139 cases valid-JSON disagreements would be false.

The reviewed parser accepts only a top-level string `name` in valid JSON. On invalid JSON it extracts one distinct lower-case/underscore name anywhere in the text. It does not require that name to be a top-level function call or check the associated parameters. It ignores unnamed argument objects, free-form explanations, reasoning, and same-name argument conflicts. Its negative category also includes missing content. Eight executable boundary probes document these facts in `parser_probe_results.json`. The synthetic malformed nested-name probe shows why the regex category should stay separate from strict JSON.

The corpus scan found no additional `name`, `action`, `tool_name`, or `function_name` strings nested in valid JSON that the top-level parser omitted. That check is narrower than a semantic audit of all explanations. It is not proof that the 139 selected cases exhaust every kind of response inconsistency.

Channel availability prevents a fair comparison of these name-conflict counts as model consistency rates:

| Configuration | Selected attempts | Selected assistant content |
|---|---:|---|
| Sol | 1,957 | All empty |
| Gemini | 1,668 | All empty |
| Opus | 1,635 | 1,284 empty; 351 unparsed by the name rule |
| Grok | 1,663 | 1,045 strict named JSON; 23 malformed explicit names; 385 unnamed JSON; 195 other unparsed; 15 empty |

Of Grok's 155 ENDs without a detected name conflict, 129 have a parsed matching top-level name, 15 have unnamed JSON, and 11 have other unparsed content. Sol's 232 and Gemini's 143 are entirely empty-content cases. Opus's 43 divide into 28 empty and 15 unparsed. These are heterogeneous observations, so a label such as "confirmed voluntary END" would overstate the evidence.

For any reported rate, retain the unit: 139 of 1,663 selected Grok attempts, or 148 of 1,698 Grok attempts including discarded ones. The name-observable subsets are different again. None of these pooled counts gives an independent-trial probability or a measure of latent intention.

## Transport attribution

I checked all 148 detected conflict files, including the nine discarded attempts. Every saved request omits `stream`; every saved response is one ordinary JSON completion with one choice and one tool call, HTTP status 200, and the expected requested and returned Grok model. The entire parsed raw body equals the saved `response_json`. Its `choices`, assistant content, tool name, and tool arguments equal the canonical attempt. The only added top-level field in the attempt's `raw_response` is `openrouter_generation`.

At `openrouter_client.py` lines 80–108, this client's streaming path requires a stream callback, sets `stream: true`, and calls the separate accumulator path. Lines 113–164 preserve `response.text` and parse that same nonstreamed response. Those facts exclude this application's streaming assembly as the source of the recorded conflicts. The claim applies to these saved requests, not every possible transport path or every response inconsistency in the corpus.

The artifact is a saved HTTP response text, not an independently captured provider-internal trace. The upstream provider and OpenRouter may transform or route model output. The audit therefore supports "inconsistent names already present in the received nonstreamed response" and does not support "the model intended the content action," "the provider changed the action," or "OpenRouter corrupted the tool call."

## Focal recipient-prompt exposure

The independent event-derived defect counts are 232 self-partner counter summaries, 44 reversed accepted summaries, and 26 misattributed rejected summaries. I reconstructed the exact row including turn, player, event type, action string, and attached message. Every focal equality hit lies in `$.game_state.memory.public_timeline_last_20[i]`; none lies in structured trade history or another field. Each source event precedes the corresponding decision request.

All 32 focal selected request bodies have a user payload equal to the payload inspected by the audit. Their selected timelines equal their initial timelines, including the Opus retries. For the 30 requested focal cases in G4/G6/G11/G13/G18/G19 the actual timeline length is 20. The two G20 extras have lengths 1 and 4.

Here, `dNNNNNN` is the decision suffix. The complete identifiers, canonical paths and lines, request-event sequences, response-file paths, and exact matching JSON paths are in `independent_results.json` under `focal_records`.

| Game and decision suffix | Known formatter rows in selected prompt, by event sequence |
|---|---|
| G4 d000148 | 957, 966, 971, 1013, 1018, 1028, 1038, 1043 |
| G4 d000149–d000150 | Those eight plus 1057 |
| G4 d000151–d000152 | Those nine plus 1067 |
| G6 d000019–d000021 | None |
| G11 d000255–d000258 | None |
| G13 d000218, d000243, d000244, d000250, d000251, d000311 | None |
| G13 d000252–d000253 | 1799 |
| G18 d000083, d000360, d000419, d000441, d000442 | None |
| G18 d000335 | 2232 |
| G18 d000431 | 2948 |
| G18 d000460 | 3183, 3192, 3196 |
| G19 d000135–d000136 | None |

In G4, event 971 and 1043 are reversed acceptances; event 1018 misattributes a rejected offer; the other listed rows name the countering player as their own partner. G13 event 1799 and G18 events 2232, 2948, 3183, and 3192 are self-partner counters. G18 event 3196 is a rejected-offer misattribution.

This supports the reviewed positive exposure annotations and the narrower negative label "no occurrence of these known formatter defects in this prompt." It does not establish that a recipient attended to or believed a row, that a settlement followed because of it, or that a prompt without those rows was otherwise accurate. A sender's false public proposition is also distinct from a formatter attribution defect.

## Required correction and finite limits

Correct `audit_conditions.py` line 111 to read `memory.get("public_timeline_last_20", [])`, or validate the explicit full path for this cohort. Record the path in the output and, preferably, constrain the equality match to that timeline. The current recursive search is broader than the claim in principle, but it produces the correct focal matches in this corpus. Regenerate `conditions_audit.json` so the timeline lengths are true. This is a metadata correction and does not require withdrawing the exposure results.

The reviewed counts need no numerical correction. Preserve the attempt-selection and malformed-content distinctions, the construction-tool-listed denominator, the response condition of Opus ENDs, and the channel-availability limitation when using them in prose or tables.

I could not independently check provider-internal generation, OpenRouter-internal transformations, model attention or intent, or causal persuasion. These records do not contain those quantities. I did not perform a new engine replay or verify all 1,225 advertised construction opportunities as executable sequences. Those are separate claims from this resolution and delivery review. I also did not semantically relabel every reasoning and message field. No model calls were made, and no canonical artifacts, prompts, engine files, manuscript, or shared audit scripts were changed.
