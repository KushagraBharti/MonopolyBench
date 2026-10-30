# Targeted verification

Executed during phase-2 work on 2026-10-29 UTC. These checks cover downstream reading utilities and targeted case analyses, not completion of the corpus review.

- `python/.venv/bin/python docs/research_raw/paper_phase2_2026-10-28/astra/feasible_liquidation.py`: all three recorded prefixes match; each constructed legal sequence pays the exact debt and leaves its actor non-bankrupt at that endpoint.
- `python3 docs/research_raw/paper_phase2_2026-10-28/astra/liquidation_case_evidence.py`: transfer, payment, cash and unique-utterance assertions pass, including the observed game-17 repayment sequence.
- `python3 docs/research_raw/paper_phase2_2026-10-28/astra/g01_candidate_audit.py`: both mirrored-offer comparisons, cash/holding checks, turn checks and first Opus action check pass.
- `python/.venv/bin/python -m pytest -q -p no:cacheprovider docs/research_raw/paper_phase2_2026-10-28/test_reading_chunks.py`: three focused tests passed. Generated reading copies also assert exact JSON round trips.
- `python/.venv/bin/python -m pytest -q -p no:cacheprovider docs/research_raw/paper_phase2_2026-10-28/test_public_review.py`: two focused tests passed. Full public projection verifies 6,989 decisions across twenty games and preserves all public-message events while excluding private-note events and response channels.
- Ruff passed on the three Astra case scripts, `prepare_public_review.py`, `review_page.py` and `prepare_reading_chunks.py`.

No production engine, prompt, protocol or canonical game changed. No full production suite was rerun for these downstream-only additions. No paid/provider game calls were made.

Additional checks in this phase:

- `astra/trade_memory_audit.py` checks all 113 accepted settlements and all 6,989 initial timeline prompts. Its three hand-specified tests pass.
- `astra/g02_build_fallback_audit.py` verifies five exact replay prefixes and five legal interleaved nine-house builds at the recorded states. Ruff passes on both audits and the direction tests.
- `prepare_game_reading.py` prepares complete source-preserving game copies and a behavioral view retaining all response choices/channels, observations, attempt prompts, actions and event payloads. Both game 7 and game 14 pass exact reconstruction checks. Two focused nested-JSON/text-preservation tests pass. Preparation is not semantic review.
