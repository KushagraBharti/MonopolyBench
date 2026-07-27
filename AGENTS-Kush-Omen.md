# AGENTS.md

This repository is a benchmark, not just an application. A small behavior change can alter the Monopoly rules engine, the LLM decision surface, the replay contract, the UI, or the research artifacts used for analysis. Treat changes as benchmark changes: keep them scoped, documented, replayable, and tested.

## Mission

MonopolyBench has four jobs at once. It is a deterministic Monopoly implementation, an LLM-agent orchestration harness, a real-time render-only UI, and a research artifact pipeline. The project should remain useful for live demos, but the higher standard is reproducible research: every serious run should be inspectable, replayable, and analyzable after the fact.

## Core Invariants

The engine is authoritative. Only the engine mutates game state, validates rules, emits legal actions, and produces events. The UI must render snapshots and events from the server; it must not implement Monopoly rules or infer legality. LLM agents may only choose from explicit legal actions emitted by the engine.

Determinism is mandatory for engine replay. Given the same seed, engine settings, player identities, and applied action sequence, the replayed event stream should match after canonicalization. Wall-clock time, network timing, and provider latency are observational metadata only; they must not affect game progression.

Every state change must emit an event. Events are the canonical replay surface, and actions are the canonical explanation of why those events happened. If a change cannot be reconstructed from events, actions, decisions, snapshots, and prompt/response artifacts, the artifact pipeline is not strong enough.

OpenRouter is the only LLM gateway. Do not add direct vendor API clients unless the project explicitly changes this policy. Do not commit secrets. Use local environment files for keys and treat provider metadata, pricing snapshots, and raw usage fields as research artifacts.

## Protocol Objects

The stable protocol boundary is made of snapshots, events, decisions, and actions. A state snapshot is the authoritative serialized game state. An event is an append-only state transition or major marker with sequence and turn metadata. A decision point is the engine-produced menu of legal choices for one player. An action is the structured selected move for that decision.

If any protocol shape changes, update the whole stack together: JSON schemas, TypeScript contracts, examples, engine/arena/API/frontend/telemetry producers and consumers, and tests. Do not silently change event meaning, action semantics, snapshot fields, or decision payloads.

## Directory Ownership

- `contracts/`: schemas, TypeScript contracts, examples, and board data.
- `python/packages/engine/`: deterministic rules, state, event emission, decision generation.
- `python/packages/arena/`: LLM orchestration, prompt construction, tool calls, validation, retries, fallbacks, OpenRouter client behavior.
- `python/packages/telemetry/`: artifacts, summaries, cost/usage, replay/review files, analysis-facing outputs.
- `python/apps/api/`: FastAPI lifecycle, run management, artifact endpoints, WebSocket streaming. Keep it thin.
- `frontend/`: render-only UI from server-provided snapshots, events, and artifacts.
- `docs/`: durable human documentation, references, raw research outputs, and archived historical plans.

Keep ownership boundaries clean. Rules belong in the engine, not the UI. Model-facing orchestration belongs in arena, not telemetry. Analysis and labels are downstream of model decisions, not part of prompts.

## Prompt And LLM Policy

Prompt behavior is benchmark-critical. Do not change system prompts, user payloads, prompt structure, retry wording, tool schemas, tool choice, memory behavior, public/private message requirements, or model-facing metadata unless the user explicitly asks for a prompt-facing change.

Research metadata, scoring rubrics, review labels, failure taxonomies, and analysis outputs must stay downstream of the decision. They can inspect what happened; they must not leak into what the model sees. If prompt-adjacent files are touched, add or run prompt-preservation checks.

Invalid model outputs should follow the established strict policy: validate against legal actions, perform the configured corrective retry, then apply deterministic fallback if needed. Record validation errors, retries, fallback reasons, attempt metadata, and emitted event ranges.

## Artifact Policy

Run artifacts are part of the benchmark surface. Preserve enough data to debug and replay a run: `events.jsonl`, `actions.jsonl`, `decisions.jsonl`, `state/`, `prompts/`, `summary.json`, usage/cost files, replay reports, manifests, review queues, scorecards, and analysis outputs.

Never overwrite canonical per-turn snapshots. Always include decision IDs and attempt indexes in prompt/response artifacts. Usage and cost accounting should come from provider/OpenRouter data where available, and raw usage semantics should be preserved because providers do not always report reasoning/output tokens the same way.

Saved games should remain self-contained. If generated reports, plots, tables, or zips are produced for a run, keep them with the saved run or in an explicitly named archive. Do not mix raw historical outputs with polished canonical outputs unless the folder structure makes that distinction clear.

## Working Rules

Use `rg` for search. Use `apply_patch` for manual edits. Do not revert user changes or unrelated dirty work. Prefer repo patterns over new abstractions. Add tests for behavior changes, especially engine, replay, protocol, prompt, or artifact changes.

Avoid nondeterministic engine behavior, unordered state iteration that affects outcomes, hidden wall-clock dependencies, UI rule logic, direct vendor clients, secret commits, undocumented house rules, and unversioned schema changes.

For docs, keep canonical files concise and readable. Historical plans, raw model research outputs, and long handoffs should live under `docs/archive/` or `docs/research_raw/` rather than cluttering the root.

## Verification

Before merging meaningful behavioral work, run the strongest practical verification. Preferred full check from repo root:

```powershell
pwsh -File scripts/verify.ps1
```

Focused checks are fine while iterating, but final claims should be backed by the tests that cover the changed surface: contract validation, engine tests, arena tests, telemetry tests, API tests, frontend build, replay verification, saved-artifact checks, and prompt-preservation tests when relevant.

## Debugging Order

When something looks wrong, inspect artifacts in this order: `events.jsonl`, `actions.jsonl`, `decisions.jsonl`, prompt/response files, then state snapshots. Events tell what actually happened. Actions tell what was applied. Decisions explain what the model was allowed to do. Prompts and responses explain model behavior. Snapshots are authoritative state checkpoints.

If anything is ambiguous, choose the strictest interpretation that preserves determinism, legal-action enforcement, replay correctness, contract stability, and artifact completeness.
