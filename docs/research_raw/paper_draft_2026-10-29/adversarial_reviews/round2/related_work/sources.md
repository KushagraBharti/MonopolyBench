# Sources and version audit

Retrieved on 2026-10-29. `sources/fetch_manifest.json` records UTC retrieval times, exact URLs, resolved URLs, byte counts and SHA-256 hashes. The fetched bytes are retained in the same directory. These are primary sources; prior reviewer summaries were treated as leads to verify.

| Citation key | Exact source and inspected sections | Role in the replacement |
|---|---|---|
| `backlund2025vendingbench` | [arXiv 2502.15840v1](https://arxiv.org/abs/2502.15840v1), abstract; submitted 2025-02-20 | Long-running vending operation. |
| `li2026arena` | [arXiv 2608.14825v3](https://arxiv.org/html/2608.14825v3), dated 2026-08-21; abstract, §§2.1, 4.1, 4.3, 5.1, 6; Appendices A, D, F | Corpus, classification/state/reasoning pipeline, follow-through, validation scope. |
| `wu2026agentmonopoly` | [arXiv 2610.29330v2](https://arxiv.org/html/2610.29330v2), dated 2026-10-22; §§3, 4, limitations; Appendices A.1, A.2 | Behavior/persona design, legal choices and invalid records, conduct instruction, bankruptcy trigger, reported cap and session replay. |
| `agentmonopoly2026repo` | [commit 2434f4278bf2970237ba82399db191e0116f3d35](https://github.com/SuELS-Group/Agent_Monopoly/tree/2434f4278bf2970237ba82399db191e0116f3d35); `README.md`; `backend/agent.py` lines 52–93, 210–302; `backend/engine.py` lines 142–162, 536–551, 553–618, 620–693; `backend/run_experiments.py` lines 37, 265–307, 316–380, 511–512; `backend/server.py` lines 36–82, 92–141, 155–193 | Failure diagnostics/retries, pass resolution, inheritance, snapshot path, runner horizon. Read raw files pinned to the bibliography commit, not moving `main`. |
| `hu2026finboardbench` | [arXiv 2605.27896v1](https://arxiv.org/html/2605.27896v1), dated 2026-05-27; abstract, §2.2, Appendix C.3, D, E | Three games, memory records, legal prompts, liquidation and inheritance rules, correction and system-forced fallback. |
| `zhang2026dece` | [arXiv 2610.35773v1 HTML](https://arxiv.org/html/2610.35773v1) and [metadata](https://arxiv.org/abs/2610.35773v1), dated 2026-10-26; abstract, §§3.1–3.2, 4.3; Appendices A.1, D.7, G.1–G.3 | Ten Eurogames, complete configurations, replay/resume, matched comparisons and no dialogue channel. |
| `bianchi2024negotiationarena` | [arXiv 2402.05863v1](https://arxiv.org/html/2402.05863v1), dated 2024-02-08; §2.2, §4 | Explicit serialized-game counterfactual rerunning and bargaining-instruction contrasts. |
| `empty_commitments_v2` | [arXiv 2610.01045v2](https://arxiv.org/html/2610.01045v2), dated 2026-10-08; abstract, introduction, §2 | Runtime feasibility versus enabling action. |

DECE's arXiv metadata title is **A Unified Arena for LLM Agents across Diverse Eurogame**. Its rendered v1 manuscript title ends in **Eurogames**. The existing `references.bib` entry follows the metadata. No bibliography change is proposed.

AgentMonopoly's code inspection supports specific positive implementation facts and the absence of a re-execution entry point in the named runner/server. It is not an exhaustive absence proof about all releases. Its 150-step paper horizon and 600-turn runner default are reported separately; no inference about which code generated the experiments is made. The parser's repair attempt precedes the forced pass, and request/empty-answer retries are different from corrective legal-action feedback.

## Public repository evidence

- [Repository API](https://api.github.com/repos/KushagraBharti/MonopolyBench): public status and license metadata.
- [Remote commit](https://api.github.com/repos/KushagraBharti/MonopolyBench/commits/1133b6b839162ec4929dd80b1a6a2397e2422616): commit identity and root tree.
- [Root tree 286c8e09ad30c708a52cf3eed65b8aaabbfcdcae](https://api.github.com/repos/KushagraBharti/MonopolyBench/git/trees/286c8e09ad30c708a52cf3eed65b8aaabbfcdcae): saved-games tree membership.
- [Saved-games tree 329366d0556335f323cb5052adf25454d90ba97b](https://api.github.com/repos/KushagraBharti/MonopolyBench/git/trees/329366d0556335f323cb5052adf25454d90ba97b): two research cohort trees.

`sources/release_audit.json` records the exact remote/local tree matches and per-game committed blob identities. This uses immutable local Git object enumeration after remote hash matching, not a truncated GitHub recursive listing. It checks file presence, not semantic artifact completeness. The certificate-suite directory is absent from the public commit inspected.

## Local inputs

Read `AGENTS.md`; `paper_draft_2026-10-29/sections/{related_work,introduction,claim_protocol,validation}.tex`; its `references.bib`; round-one `fable_novelty/{review,sources,verification}.md`; and `python/packages/engine/src/monopoly_engine/replay.py`. Paths relative to `docs/research_raw/` unless explicitly repository paths. A small cohort-file read was only used to orient the release audit. All input hashes are in `source_hashes.json`.
