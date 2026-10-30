# Integrated manuscript evidence map

Paths below are repository-relative unless marked as local to this draft. This is a source index, not a claim that every retained analysis was rerun during manuscript assembly. The coauthor evidence maps retain exact decision IDs, event sequences, packet hashes and verification scope.

Abbreviations:

- P1: `docs/research_raw/paper_phase1_2026-10-28/`
- P2: `docs/research_raw/paper_phase2_2026-10-28/core_review/`
- P3: `docs/research_raw/paper_phase3_2026-10-29/`

| Manuscript claim or exhibit | Retained evidence | Verification in writing stage |
|---|---|---|
| 20 games; 50,918 events; 6,989 decisions; 8,679 attempts; five seeds/four rotations | P1 `sol/results.json`, `sol/manifest.json`; P3 `astra/exhibits/t01_cohort.json`; P2 `sol/corpus_economics_audit.json` | Sol's new original-event recount; root table invariants and source-copy hashes |
| Frozen rules, prompts, provider configuration, sampling defaults | Engine and arena sources, saved run configurations; `coauthors/fable/evidence_map.md` | Fable original source inspection, with root/Opus precision challenges |
| Source commits and absence of model-facing source differences | P3 `opus/handoff.md`, `opus/debate.md`; inspected `42f85183..d6808534` | Retained diff audit; no inferred behavioral cause |
| Acquisition 475/72/207/397; 209 episodes; terminal 69; bilateral trade 60/43/10 | P1 independent Sol, Opus and Fable reductions; P2 `sol/corpus_economics_audit.json`; P3 T4 | Fresh original-event reconstruction in `coauthors/sol/verification.json` |
| Negotiation propensity and intensity; Figure 1 and Table 2 | P2 `astra/negotiation_units.json`; P3 T1/T2 | Original proposal/menu recount by Sol; root exact-fraction checks |
| 43/63 first-window builds; 34/42 entry builds; eight residuals 3/3/2; Figure 2 | P1 `sol/group_episodes.jsonl`; P3 `fable/exhibits/first_management_causes.json`; P3 T3/T9 | Existing independent reconciliations; root denominator and residual assertions |
| Uneven-build recovery and 61 executable reordered purchase multisets; Table 3 | P2 `sol/build_recovery_audit.json`, `astra/default_build_plans.json` | Retained engine proofs; no new branch execution in draft stage |
| 103 units, 103,450 expenditure, 93,000 whole-game and 92,550 post-spend receipts; Figure 3 | P2 `astra/development_aggregation_check.json`, `sol/corpus_economics_audit.json`; P3 T5 | Fresh original-event recount; root exact sums and all-case figure inputs |
| Winner 58/34/30; 54/60 creditor; 57 developed-color eliminations | P2 `sol/corpus_economics_audit.json`, `astra/development_aggregation_check.json` | Sol recount confirms expenditure/route distinctions; retained trigger audit |
| G15 orange-first and G19 Gemini $2,000 cumulative dark-blue expenditure | Original G15/G19 `events.jsonl`; `coauthors/sol/verification.json`, `final_review/sol/checks.json` | Fresh original reads and reductions; earlier narrative errors explicitly corrected |
| Sixty eliminations: 56 below nominal upper, three payable, one hotel lock; Figure 4/Table 4 | P2 `opus/bankruptcy_bounds.json`, `sol/elimination_upper_bounds.json`, `astra/g07_hotel_lock.json`, `astra/g12_channel_liquidation_check.json`; P3 T6 | Retained legal sequences and exhaustive lock checks; root classification invariants |
| Other local financing and reserve contrasts | P2 Sol/Astra per-game `*_checks.json`; `coauthors/sol/evidence_map.md` | Retained exact-prefix proofs with endpoint/conditional-acceptance scope |
| G13 opening appeal, buyer solvency remark, later omission; G19/G6 corrections with acceptance; G11 echo then reject; G4 prior contingency | P2 `sol/g13_omission_check.json`, `additional_social_channel_checks.json`, `g11_social_channel_checks.json`, `g04_uptake_boundary_check.json`; Astra game audits | Opus writing-stage source/retained-field rereads; root's final `qa/g13_context_check.json` verifies that d250 framing precedes d251 rationale. That rationale precedes only the d252 omission, not all seller framing. |
| G18 standing offer and denial purchase/estate reversal; G20 disclosure | P2 `sol/g18_sample_and_offer_checks.json`, `additional_social_channel_checks.json`; original packets and G18 events | Opus rereads, exact original G18 estate check; selected chronology, not category prevalence |
| 139 received-name conflicts; 15 parsed-equal / five literal-equal | P2 `sol/received_name_conflict_audit.json`; `astra/reconciliation.md` | Retained full-corpus audit; source localization unresolved |
| Trade-summary manifestations 44/113, 26/413, 232/394; union 2,054 prompts | P2 `sol/trade_timeline_audit.json`; `opus/trade_timeline_reversal.log`; `astra/negotiation_units.json` | Retained independent formatter audits; the 44 accepted cases are the same final-author/initiator discrepancy |
| 149 timeline omissions, 6,733 insertions, 6,720 opponent deliveries | P1 `sol_round2/public_delivery_summary.json`, delivery audit and occurrence ledger | Retained source-attributed reconstruction, not a semantic nonexposure claim |
| 10,235 snapshot matches, 113 settlement checks, 27,956 jail-card/player observations | P1 Opus state/settlement reductions; Fable reducer and `fable_phase1_memo.md` | Retained independent source reductions; draft text limits claim to reconstructed economic state |
| Twenty full event replays; 6,989 memory windows; twenty prefix branches; 19/20 builder endings | P2 `sol/build_recovery_audit.json`; P1 `opus/opus_sandbox_checks.json` | Retained tests, no new LLM suffixes; next events versus full prompt and training distinguished |
| Review provenance 614 catalog entries, 240 bundles, twenty trajectories | P2 each coauthor's `progress.json`, `case_reviews.jsonl`, sample ledgers and handoffs | Checked retained review inventories; not human annotation or blind replication |
| Related-work comparisons and 32 cited sources | P3 `literature_review.md`, `reference_registry.json`, each coauthor literature file; `references_source.bib` | Frozen verified-primary-source package plus Fable section mapping; no new broad search claimed |

The draft's `tools/build_exhibits.py` uses only copied JSON exports. `tools/verify_draft.py` checks exact figures, source-copy identity, protected files, citations and PDF geometry. It does not test behavioral hypotheses or repeat the whole engine suite. The repository's engine, harness, prompt and canonical saved-game files were not edited.

## Adversarial revision: current evidence

The table above records first-draft provenance, including its historical 32-citation scope. The revised manuscript cites 18 selected sources and adds the following evidence. `A` below denotes `docs/research_raw/paper_adversarial_2026-10-29/` in the original repository. `adversarial_reviews/` contains copies of the nine review reports; report source paths retain their original repository meaning.

| Current claim | Evidence | Verification and boundary |
|---|---|---|
| 60 elimination and 66 default-decision cases | `artifacts/historical-claim-audit.zip`, `data/certificate_results.json` | New unchanged-engine executions at all prefixes; 50,918 events replay. Round 2 and 3 reviewers independently reran them and checked census/attempt transcription against originals. Frozen selection is not re-derived by the small package. |
| 56 upper-bound negatives, three payment witnesses, one exact hotel lock | Same artifact; `adversarial_reviews/round2/certificates/` | Guarded search refuses a negative certificate when building sales are offered. The synthetic bundled-sale regression invalidated the old generic claim; finite results survived. Plot shows upper bounds, not 59 alleged exact accessible maxima. |
| 663 END records: 66 defaults, 24 conflicts, 573 residual | `data/resolution_conditions.json`; `A/audit_conditions.py` | Fresh original-record audit; separate resolution reviewer reconstructed every initial timeline and checked source requests/responses. Residual is not chosen restraint. |
| 139 selected versus 147 strict all-attempt conflicts; 148 including malformed name | Same audit and `adversarial_reviews/round2/resolution/` | Identity-level reconciliation; raw received JSON is nonstreamed. Local stream assembly excluded for checked cases; provider/gateway origin unresolved. |
| All 63 trade-completion windows and 80 game/configuration cells | `data/first_management_windows.json`, `data/opportunity_ledger.json` | Retained Fable windows, explicit reaggregation with zero cells, independently checked in final package review. No new raw event reduction claimed. |
| G13 omitted route, refusal-posture ambiguity and actual financing opportunity | `adversarial_reviews/round3/social_review/` | Fresh complete focal sources and 1,801-event prefix; acceptance plus mortgage reaches 295 before another roll. No hypothetical actual rent, latent belief or $70 causal effect inferred. |
| G4 ownership versus buildability; G6/G19 correction with acceptance; G11 transient echo; G18 assurance; G20 disclosure | Same finite social review; original maps above | Forty focal assertions checked, including selected retry prompts. Not an all-corpus semantic reread or a rate. |
| Closest work and public release status | `adversarial_reviews/round2/related_work/`, `data/public_release_check.json` | Fresh primary sources credit competitor retries, failure records, counterfactual reruns and Arena validation. Raw public commit is separate from new local research outputs. |
| Final tables, copyable commands, PDFs and package | `verification.json`, `qa/verifier_regression.json`, `qa/final_render_review.md` | Row/digest consistency, corrupted-copy rejection, rendered inspection and exact archive extraction. Distinct from behavioral proof or external scientific replication. |

The certificate suite's new first-payment routes sometimes stop with different cash than earlier maximum-finance analyses because they mortgage different collateral or stop earlier. G12 Sol retains 38 and G17 Gemini 180 in the new witnesses; prior 8/155 routes were different legal sequences. No incompatible endpoint is silently equated.
