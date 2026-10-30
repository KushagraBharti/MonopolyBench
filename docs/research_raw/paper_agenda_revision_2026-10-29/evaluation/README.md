# Controlled-evaluation readiness package

This package supplies completed offline readiness diagnostics and a concrete design for new model evaluations. It does not claim that the historical LLMs have been tested for learning, generalization, or a general-to-multi-agent capability relationship.

## Completed work

- `protocol.json` was frozen locally before the primary pilot. This is not an external preregistration.
- `run_offline.py` audited all 130 static scenarios with six existing policies and ran 20 new baseline-only games, plus two exact-repeat checks.
- `verify_offline.py` replayed all 20 games from retained actions and rechecked all 780 baseline and 130 reference choices. Thirteen guard/regression checks passed.
- `check_fixture_states.py` is an explicitly adaptive follow-up after legality failures. Its separate protocol is `fixture_state_checks_protocol.json`.
- `summarize_readiness.py` lists all eleven failed reference IDs with manually checked causes and all 68 candidates passing both limited screens. Those candidates still need complete-menu validation, reachability/intervention declarations, endpoint certificates and independent strategic adjudication.
- `evaluation_results.tex` is finished integration-ready prose with a table and explicit completed/proposed boundaries.

## Results

The primary games produced 19,494 applied decisions and 179,816 events. No live generated action was invalid. Nineteen games were right-censored at 1,000 decisions; one mixed game terminated with builder winning after 494 decisions. No winner is assigned to a censored game. None of the six policies proposed a trade in these games. This is a small reference-policy quality pilot, not a tournament estimate or a result about the historical four LLM configurations.

Static fixtures produced different results: 75 of 780 generated policy actions and 11 of 130 supplied reference actions fail engine legality at the provided pending decision and public state. Many failures reflect ownership/menu inconsistencies in the supplied fixture. All 11 rejected reference cases were inspected in their original JSON. Do not cite this as a live baseline failure rate. Forty-one scenarios produce identical action names and arguments for all six policies. In 128 scenarios, the rubric rewards private-note keywords; the median share is 15.8%, and the maximum is 25.7%. These scores have not been validated as expected-utility or strategic-skill measures.

The follow-up reports 55 scenarios with a standard house-stock conservation discrepancy; some have additional ownership, mortgage, hotel-stock or liquidation-shortfall inconsistencies. A deliberate scarcity intervention may intentionally alter stock, but must declare that condition. A flag is not by itself proof that a synthetic task is useless, and passing these checks is not proof of reachability or optimality.

## Reproduce

From the repository root, using its installed Python environment:

```sh
python/.venv/bin/python docs/research_raw/paper_agenda_revision_2026-10-29/evaluation/run_offline.py --output /tmp/monopoly-offline-reproduction
python/.venv/bin/python docs/research_raw/paper_agenda_revision_2026-10-29/evaluation/verify_offline.py
python/.venv/bin/python docs/research_raw/paper_agenda_revision_2026-10-29/evaluation/check_fixture_states.py
python/.venv/bin/python docs/research_raw/paper_agenda_revision_2026-10-29/evaluation/summarize_readiness.py
```

The first command refuses to overwrite a nonempty destination. The verifier checks this package's retained `results/`; the newly reproduced output can be compared with it. No secret or provider account is read, and the runner does not instantiate a model client. A process audit hook blocks network connection and DNS operations. Enabling a paid/network flag in the protocol is an error, not a way to enable model requests.

The `results/games/` directories contain compressed full decisions, actions and events, initial/final snapshots, configurations and summaries. Repeats are under `results/repeats/`. The repeated-seed checks preserve run identity because the random policy's seed derivation includes that identity. The two mixed-game seeds and seat rotations are descriptive blocks, not independent evidence of a seat effect.

## Source and validation scope

`results/sources_before.json` records 174 unchanged source files. `engine.py` has SHA-256 `122edf5f16db0c4b8e0bd475ded73bf70a2b08065304d0517b8f8e2c98d63e0d`, identical to `historical-claim-audit/vendor/monopoly_engine/engine.py` inside the manuscript's historical audit ZIP. This confirms engine-source identity, not a claim that the entire new pilot condition equals the historical configuration.

The fixture validator reconstructs the provided public board/ownership/cash and pending decision. It checks the generated action against that decision with the unchanged engine. It does not recover hidden decks, future random draws, prior history or scenario reachability. All economic-legality results have this scope. A semantic reference preference is not certified merely because an action is legal.

The same engine replays the pilot, so the repeatability checks are not an independent implementation of the rules. `results/guard_tests.json` records 13 tests, including blocked paid/network configurations, unknown policy, invalid action and unaffordable auction rejection, plus a digest mutation. The single blocked socket connection in the guard test occurs before any operating-system connection; the research pilot made zero network attempts.

`initial_execution/` preserves the first executed runner and its outputs before removal of an unused import. The cleaned runner re-executed the same fixed conditions; this is a reproduction, not twenty additional independent study games. `results/finalization_check.json` records equality of the twenty per-game summaries and fixture results across these executions. No initial result was silently overwritten.

## Paid experiments remain disabled

`protocol.json` defines local skill, adaptation, opponent transfer, cross-family capability and optional framing arms with units, targets, hypotheses, controls, holdouts and prerequisites. No arm has model results. Feedback, memory and message interventions need explicit versioned scope. The user's spending decision is pending. `results/cost_design.json` records saved historical usage as a lower-bound workload reference, not a current pricing quote or a budget guarantee. No canonical fixture, production baseline, engine, prompt or game was changed. No paid call, commit or push was made.
