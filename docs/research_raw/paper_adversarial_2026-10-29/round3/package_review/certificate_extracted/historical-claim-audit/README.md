# Executable historical-claim audit

This artifact certifies a retrospectively defined census of 60 eliminations and 66 engine-defaulted construction decisions from twenty recorded MonopolyBench games. The case list was frozen from canonical records before this runner executed. Prior research had identified the expected results. This is new executable verification and packaging, not preregistered discovery or blind replication.

## Run outside the repository

Python 3.14.7 was used for verification. The unchanged engine declares Python >=3.10. Exact dependency versions are in `requirements.txt`; only Pydantic and its dependencies are required.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run_audit.py --output reproduced.json
.venv/bin/python test_certificates.py
```

No network, model service, API key, repository checkout, or saved-game directory is needed after installing dependencies. The runner imports the unchanged engine copy in `vendor/` and uses the unchanged `contracts/data/board.json`. `inputs_manifest.json` records input hashes and copied source paths/hashes. `LICENSE` preserves the repository license.

## Inputs and outputs

- `cases.json`: 126 claims, actor, exact decision, attempt fields, original source-line hashes, and prefix event count/digest.
- `inputs/gXX/`: engine settings, original applied actions, and canonical SHA-256 for every original event. Applied public/private fields are retained because they affect emitted events. Provider reasoning transcripts and full prompt payloads are not included.
- `games.json`: original run paths and source-file hashes. The portable runner does not read those paths.
- `results.json`: certificates, construction diagnostics, branch actions/events, source prefix equality, and all twenty historical replay hashes.
- `test_certificates.py`: nine checks, including altered input hashes and historical messages, lost purchases, an illegal hotel sale, a mortgage before its prerequisites, an incomplete payment witness, and a bundled-sale counterexample to atomic search.

All 50,918 original events are re-executed and matched individually. Every audited prefix must match the pending identifier, actor, preceding event count and digest. Changed branches stop at the local endpoint and are never substituted into an asserted historical future.

## Certificate scope

Liquidation permits only the debtor's currently legal sales and mortgages against the existing debt. It excludes assistance, trades, construction and future random moves. Let U be cash plus half-cost salvage for every building level plus the mortgage value of every clear deed. Each sale consumes finite salvage; each mortgage consumes one clear-deed capacity. Neither creates assets or outside income. Ignoring even-selling and stock constraints can only enlarge this resource budget. Thus U < debt proves impossibility under this intervention class, not under possible assistance or future turns.

When U >= debt, a legal route can certify payment. The runner records actions and the emitted payment event and stops immediately. Routes need not be minimal, preferable or unique. The new G12 Sol witness leaves 38 rather than the earlier witness's 8 because it also mortgages Baltic. The new G17 witness leaves 180 rather than 155 because it mortgages Boardwalk instead of Park Place. Both prove the same payment endpoint.

A failed constructive route proves nothing. The runner can certify an exhausted mortgage-only graph, deduplicating estate/cash/bank states, only when no visited decision offers a building-sale action. If a sale is offered, it raises an explicit unresolved error rather than issue an impossibility certificate: the engine can accept bundled sales that cannot be decomposed into legal atomic sales. A cutoff also issues no certificate. The only graph certificate here is G7 d339. No sale is offered; the only financing action is the Oriental mortgage, which triggers elimination at 440 against 750. Its complete one-state graph proves impossibility at that prefix. Earlier management opportunities are outside this claim.

Construction concerns the recorded purchase multiset at the same decision, without extra financing. The runner checks the original encoding, then splits counted operations into single purchases and constructs an order preserving every deed/kind count. Success proves target reachability; the submitted action remains invalid. The constructive ordering is not a general solver. An unsuccessful ordering with adequate cash remains unresolved. In this corpus every well-formed target that fails has cost above current cash. Malformed and absent targets remain separate.

## Verified finite-corpus results

The 60 eliminations have 56 upper-bound impossibility certificates, three payment witnesses and one exhaustive hotel-lock certificate. All 70 well-formed target plans across the 66 defaulted decisions are invalid as encoded. Atomic expansion/reordering executes 63 targets; seven exceed current cash. One further attempted target is malformed and 61 attempts have no parseable construction target. At decision level, 63 of 66 defaults have at least one reachable recorded target. All 66 permit some construction. These claims differ; neither makes a defaulted END a deliberate hold.

This census does not measure evaluator accuracy, latent intent, intrinsic ability, future survival or an alternate winner. Its populations and intervention classes were selected after exploration. It does not reconstruct full prompts or certify the semantic review. It is a bounded behavioral reproduction artifact, not the complete benchmark release.

## Authorship and history

The coordinator implemented and executed this suite after the delegated implementation returned incomplete. That original record remains in `incomplete_delegate_record.md` and receives no validation credit. Existing Sol, Opus and Astra audits informed the targets and engine-interface usage. This revision adds frozen selection, the portable runner, fresh replay, certificate graphs and adversarial tests. No canonical game, original engine or prompt was changed.

A fresh reviewer subsequently found a generic false-negative in the original atomic graph search: a synthetic inventory-conserving estate can pay by a bundled sale even though atomic routes fail. The original runner and executable counterexample are preserved in `round2/certificates/`. The revised runner fails closed on that case, and the ninth regression test verifies both the refusal to certify and the engine-accepted payment. All 126 historical results retain their classifications. This correction narrows the implemented negative-certificate procedure; it is not evidence that atomic search is generally complete.
