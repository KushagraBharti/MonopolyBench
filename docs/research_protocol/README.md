# MonopolyBench Research Protocol

This directory defines the experimental program that follows the eight-game
exploratory corpus. It is an experiment and analysis contract, not manuscript text.

The benchmark remains unchanged:

- the engine remains authoritative;
- model-facing prompts and tools remain unchanged;
- research labels and scoring remain downstream;
- all planned cells, including failures and capped games, remain visible;
- the existing eight saved games remain exploratory and are never pooled into the
  confirmatory campaign.

Canonical protocol files:

- `scientific_protocol_v2.md`: questions, estimands, hypotheses, experimental layers,
  randomness, inclusion, exclusion, and generalization.
- `downstream_bridge_contracts.md`: trajectory extraction, exact-history prompt replay,
  repeated-query, one-step branch, and provenance contracts.
- `campaign_control_audit.md`: current execution/routing/sampling/time controls and
  the gates that must close before paid runs.
- `social_evidence_codebook.md`: communication episode eligibility, labels, blinding,
  coding, adjudication, and publication thresholds.
- `llm_judge_social_evidence_protocol.md`: exhaustive three-turn chronological
  coverage, specialist judge passes, evidence challenges, human candidate
  verification, and judge-negative audits.
- `preregistration_freeze_contract.md`: completed-evidence, endpoint-window, clean
  commit, canonical tree, and immutable freeze requirements.

Generated evidence is stored outside this directory:

- `analysis/research_protocol/architecture_proof/`: zero-provider-call prompt
  reconstruction proof, canonical v2 exact-history fixtures, and the preserved v1
  serialization-failure record.
- `analysis/research_protocol/pilot/`: pilot outputs after execution.
- `analysis/research_protocol/preregistration/`: frozen preregistration package after
  pilot-based design lock.
- `analysis/research_protocol/readiness_audit.{json,md}`: machine-readable proof of
  which requirements are complete, externally blocked, or still empirical.

E1 billing is explicit and fail-closed: OpenAI must return from provider `OpenAI`
with `usage.is_byok=true`; Anthropic, Google, and xAI are treated as
OpenRouter-credit routes. A separate forced-tool preflight verifies all four routes
without changing any game prompt.

The post-E1 gate is deliberately fail-closed:

1. `scripts/research/validate_e1_pilot.py` requires all eight planned cells in the
   ledger, complete cyclic seat coverage, decision/action bijection, complete core
   artifacts, and passing state and artifact replay.
2. `scripts/research/build_e1_analysis_matrix.py` chooses \(H_c\) and \(H\) using the
   label-blind frozen quantile rules and emits only blinded actor codes.
3. `scripts/research/simulate_e1_design.py` calibrates the joint primary family under
   low, central, and high variance/attrition scenarios and cannot write
   `design_lock.json` without both scientific gate passage and an explicit approved
   campaign-cost ceiling.
4. The social review freezes an exhaustive Codex/Claude Code judge workflow before
   E2. It reads local artifacts through agentic research tasks and makes no OpenRouter
   or external model API call. Humans later validate high-risk machine candidates and
   a probability sample of judge-negative windows; that validation gates social
   claims, not ecological campaign execution.
   `scripts/research/analyze_communication_calibration.py` remains the downstream
   agreement/adjudication validator and never mutates the packet manifest.
5. `scripts/research/audit_protocol_readiness.py` rechecks the complete goal rather
   than treating preparatory files as empirical completion.

No paper drafting begins from these files until the ecological campaign and diagnostic
gates in `scientific_protocol_v2.md` are complete.

The canonical exact-history collection is `fixtures_v2/`; `fixtures/` is retained
only to document the key-order persistence defect caught by the independent execution
precheck. See `analysis/research_protocol/architecture_proof/fixture_format_migration.md`.
