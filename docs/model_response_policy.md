# Model response policy

New cloud jobs use `execution_policy_v3` and `claude_refusal_recovery_v1`.
Initial prompts, legal actions, ordinary corrective retries, and Monopoly rules
remain unchanged. Grok 4.7 uses `tool_choice: required`; other models use `auto`.
Opus 5.5 does not support forced tool use.

## Claude refusal recovery

The fixed map is `anthropic/claude-opus-5.5` to `anthropic/claude-opus-4.8`.
For an explicit refusal on the first Opus 5.5 response:

1. Discard all refused output, including any apparently valid partial tool call.
2. Retry Opus 5.5 with the same game state, existing memory, reasoning effort,
   and legal actions. Remove the request for private reasoning from the system
   prompt and remove `private_thought` from tool arguments and payload requirements.
   Require the legal action and `public_message`. No private note is synthesized.
3. If that retry is explicitly refused, send the same action-only condition to
   Opus 4.8. Retain reasoning effort and pin the Anthropic provider.
4. If recovery is exhausted or produces an invalid action, use the existing
   deterministic game fallback. Refused partial actions are never applied.

There are at most three resolver calls. Ordinary malformed or illegal responses
retain the existing two-call corrective policy; a refusal appearing only on that
ordinary corrective retry does not start a new recovery chain. A malformed
response to the action-only retry also does not switch models. Billing errors,
transport failures, wrong routes, and outages retain their existing operational
pause behavior. Transport retries are separate from resolver stages.

Every request still goes through OpenRouter. Both Claude models use the account's
Anthropic BYOK integration; actual billing is established by returned usage,
not assumed from the model name. Account-level credit fallback settings are not
changed. Missing usage/BYOK evidence stays unknown.

## Attribution and reproducibility

The participant is labeled "claude-opus-5.5 with claude-opus-4.8 fallback".
This is a separate benchmark treatment, not a pure Opus 5.5 score. Preserve the
execution policy, treatment fingerprint, configured map, source hashes, prompts,
tools, requested/returned models, response condition, request IDs, and costs.
Per-attempt cost and failure attribution use the actual model. The original
participant identity remains available on the enclosing decision and run.
Usage reports (`usage_accounting_v3`) keep the fallback under the participant's
umbrella: `by_model["anthropic/claude-opus-5.5"]` totals the whole seat, and
`fallback_models["anthropic/claude-opus-4.8"]` breaks out the fallback's calls,
cost, decision IDs and the trigger `explicit_provider_refusal_after_same_model_retry`.

`fallback_used` continues to mean the deterministic engine fallback.
`sequence_meta.model_fallback_used` identifies an attempted substitute model;
check the final action and `fallback_used` to determine whether its move was used.
Each attempt records `requested_model` and `response_condition`; raw responses
preserve returned model/provider and refusal metadata. Prompt artifacts retain
that attempt's tools, not the first request's tools. Durable recovery reuses all
saved stages without repeating paid calls.

Existing private notes remain in memory. Successful action-only recovery adds no
new private note, so it changes future memory compared with a normal response.
Private notes are emitted text used for game memory and research review, not
access to hidden internal reasoning. Engine scoring uses game state and actions.

Preflight exercises all four participants with the resolver policy and separately
qualifies Opus 4.8 using the action-only condition. Manifests include fallback
endpoint metadata. Old policy artifacts remain readable; jobs frozen under a
different execution policy cannot resume under this runner. Deploy only at an
idle boundary, preserving completed games and exports.

## Validation and sources

Tests cover flagged partial responses, streamed refusals, all recovery stages,
ordinary retry prompt preservation, durable response reuse, actual-model cost
attribution, preflight, and complete mocked games through replay and export.

Live diagnostics repeated the five previously refused decision states under the
action-only condition on both Claude models. All ten returned legal, schema-valid
actions, all reported Anthropic BYOK, and all charged zero OpenRouter credits.
This is a small diagnostic sample, not a guarantee against future refusals or a
randomized comparison. Grok's six saved-decision required-tool probes also passed.

References:

- [Anthropic refusals and fallback](https://platform.claude.com/docs/en/build-with-claude/refusals-and-fallback)
- [Anthropic tool choice restrictions](https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools#forcing-tool-use)
- [OpenRouter model fallback behavior](https://openrouter.ai/docs/guides/routing/model-fallbacks)
- [xAI function calling](https://docs.x.ai/developers/tools/function-calling)
