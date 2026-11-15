# Evidence map (Opus finalization draft)

Status labels:

- **Recomputed.** This draft's scripts derived the value from original saved records, board data or git blobs.
- **Re-tabulated.** The classification is inherited from an earlier package; this draft redid the counts.
- **Inherited.** Read from an earlier package or audit, not rerun.
- **Coded.** The author's model-assisted reading (Claude Opus 5.5). It is not human annotation.

No game, engine execution, replay, policy rollout, search, synthetic state or model or provider call was made.

## Claims in the main text

| Claim | Location | Evidence | Status |
|---|---|---|---|
| 50,918 events, 6,989 decisions, 8,679 attempts; decisions per model | §2.1, Table 1 | `tools/provenance.py` over all 20 `events.jsonl` and `decisions.jsonl` | Recomputed |
| Liquidation prompts carry deed keys only, with no prices, values or group labels | §2.1 | `tools/conditions.py`: in all 338 liquidation payloads, the holdings carry only `space_key`, `houses`, `hotel` and `mortgaged`; the menu carries only key lists; no value or group field appears in the action state or own state. Timeline and notes can contain values. | Recomputed |
| Four channels and their provenance (`reasoning.summary` or `reasoning.text`) | §2.1 | `data/focal_channels.json` detail types; `tools/conditions.py` | Recomputed |
| 1,604 Opus first-attempt refusals, all first attempts from G5 on | §2.1 | `data/response_conditions.json` | Recomputed. The claim that all share one provider message is inherited. |
| Grok uses required tool choice | §2.1 | `player_config.py`, byte-identical at both run commits | Source read; settings in saved requests are inherited |
| The fallback mortgages or sells before it declares; no paid episode used it | §2.1 | `decision_resolver.py` `_fallback_action`; `finance_census.json` | Source read and recomputed |
| Rule differences (Table 2) | §2.2, App. B | Rulebook PDF text extracted locally (SHA-256 `64efc743…e94a`); `engine.py` functions named in App. B | Read directly this round |
| U0 and U* for all 188 entries; 0 mismatches with the retained ledger | §2.3 | `tools/finance.py` | Recomputed |
| Payable set = 128 paid plus three witnessed declarations | §2.3 | Earlier engine-executed audit witnesses | Inherited, not rerun |
| Proposition 1 and its four classes (108/12/9/2) | §2.3, App. C | `data/continuation_premises.json`, built from original entry prompts; argument checked against engine source | Recomputed premises. The two-entry extension was first argued by Astra and the 129-entry coverage by Fable; both are re-derived here. The result is a source argument, not an executed baseline. |
| G7: $1,310 nominal, $440 reachable | §2.3 | Earlier restricted menu search | Inherited |
| 128 paid, 60 eliminated, 180 mortgages, 89 sales, $51,997; 67 one-action payments | §3.1 | `finance_census.json` | Recomputed. Episode boundaries are inherited. |
| 62/53/16 partition with 62/52/14 paid | §3.1 | `finance_census.json` | Recomputed |
| Middle class supported by 47 routes, the G12 d249 witness and 5 constructive routes | §3.1, App. D | Applied mortgages compared with entry menus; holdings and bank stock | Recomputed. The witness is inherited. The five routes are derived from source, not executed. |
| First-menu declarations by region and model (Table 3) | §3.1 | `finance_census.json` | Recomputed |
| 28 of 30 owners paid without selling; excess $2–$94, median $38, across 47 payments | §3.1 | `finance_census.json` `mortgage_first` | Recomputed (new in this draft) |
| Sixteen: values, totals = U0 or U*, remainders (Table 4) | §3.2 | `sixteen_rubric.json` with `sixteen_numeric_checks.json`: 18 of 19 stated totals checked by arithmetic, and one route total that has no reference value | Coded, with arithmetic recomputed |
| Rubric counts 5/3/5/1/2 | §3.2 | `sixteen_rubric.json` | Coded |
| G20 exact valuation; Gemini's creditor estimate; final $14 | Incident 1 | Quotes verified; route amounts recomputed | Recomputed |
| G13 selective plan, leaving $28 | §3.2 | Quotes verified; route recomputed | Recomputed |
| Errors inside successes (G2 $430, G20 d291 accounting, G17 d254 belief, G13 provider $44) | §3.2 | Full fields in `focal_channels.json` | Coded and recomputed |
| Second channel: 7 of 9 provider fields in successful note cases include released collateral | §3.2 | `focal_channels.json` | Coded |
| Two false budgets equal U0; omitted $340 and $375 | §3.3 | `finance_census.json`; quotes verified | Recomputed |
| Witness remainders of $38 and $180 | §3.3 | Earlier audit | Inherited |
| Carried $130 and $30 notes; reserve figures before successes; Opus successes without notes | §3.3 | `focal_channels.json` `carried_notes` | Recomputed |
| Nine departures (Table 5); six Grok conflicts; G18 d344 fee motive | §3.4 | `focal_channels.json`; quotes verified | Recomputed |
| Named-action scan: 9 conflicts in 338 decisions, all Grok; Grok content names an action in 27 of 56 decisions | §3.4, App. D | `named_action_scan.json` | Recomputed (independent re-implementation; agrees with Fable's earlier count) |
| 526 threads; 113/394/413; responses by recipient | §4.1 | `bargaining_census.json` | Re-tabulated |
| 79 of 111 counters keep the non-cash exchange | §4.1 | `bargaining_census.json` | Re-tabulated |
| Opening swap contrast 95/116 vs 37/72; no-Grok 16.7; Grok composition 36/72, 15/17, 13/15 | §4.1 | `bargaining_census.json`; `conflicting_openings.json` | Re-tabulated. The conflict classification of openings is inherited. |
| Block gaps and resampling ranges | §4.1, App. G | `revision_analysis.json` from the integrated package | Inherited |
| Cash-bid contrast −5.0 pooled; −0.2 to +8.5 within recipients | §4.1 | `bargaining_census.json` | Re-tabulated |
| 61 of 74 rival-consequence reading | §4.2 | Earlier two-reader GPT-6 Astra coding | Inherited |
| Grok's rival-liquidity note (G18, turn 78) | §4.2 | Carried note, verified | Recomputed |
| Incidents 2–5: quoted text | §4.2 | `quote_manifest.json` | Verified verbatim |
| Incidents 2–5: continuations (G15 blockers to Gemini after 18 turns; G7 builds four orange houses; G13 $16 interest; Opus's earlier $130 counter reasoning) | §4.2 | Earlier incident traces | Inherited. Spot-checked here: G15 Grok cash $333, the turn-33 Ventnor note, and Opus's $200 acceptance in G13. |
| Incidents 6–8 | App. H | Quotes verified; continuations from earlier traces | Verified quotes; continuations inherited |
| Cohort seeds, rotations, seats, winners, commits | App. A | `provenance.json` from run summaries and `cloud/execution_manifest.json` | Recomputed |
| Rule sources byte-identical at both run commits and head | App. A | `git show` blob hashes | Recomputed |
| Replay reports pass | not claimed in the main text | Saved replay reports | Inherited; not rerun |

## Literature access in this round

"Direct" means this draft's author retrieved and read the primary text in this session. Locally extracted PDFs and HTML went to the scratchpad and were searched with Ghostscript or Python; no code from them was executed. "Prior Opus" means my earlier 14 November review read it, through a summarizing fetch. "Peer" means another author's review recorded a primary-source read, which is inherited here.

| Source | Use in the paper | Access |
|---|---|---|
| Hasbro rulebook PDF | Table 2, App. B quotes | Direct: full text extracted locally; selling, mortgage and bankruptcy sections read |
| FinBoardBench v1 HTML | Fund-raising with mortgage and sale; bankruptcy "when recovery is impossible"; settlement follows the rulebook | Direct: HTML text extracted locally; passages read |
| Guhe and Lascarides 2014 | Embargo recipients always comply | Direct: PDF extracted locally; Section VI read |
| Co and Konuganti, ICML 2026 workshop | Identifying an unsafe action and taking it | Direct: workshop page and abstract |
| ACPBench, ACPBench Hard | Action reachability; single-turn; validators | Metadata direct; prior Opus HTML read; peers |
| Valmeekam et al. 2024 (o1) | 11.5% false impossibility | Metadata direct; prior Opus; peers read Table 3 |
| PlanBench | Planning and reasoning about change | Peers: abstract, plus Fable's local PDF read |
| AutoPlanBench (ICAPS 2025 extended) | Whole-plan versus interactive action choice | Metadata direct; peers |
| The Menu Is an Execution Prior (EMNLP 2026) | Same-candidate reordering changes success | ACL BibTeX direct; Table 6 per Astra and Fable (Fable read the PDF locally) |
| LLM-Modulo (ICML 2024) | External verification | Metadata direct; prior Opus abstract; Sol sections |
| Reasoning or Reciting (NAACL 2024) | Counterfactual rule variants | Metadata direct; prior Opus abstract; Sol sections 1–2 |
| ReAct; Zero-Shot Planners | Interaction; knowledge versus admissible action | Metadata direct; Sol abstracts |
| Embodied Agent Interface | Diagnostic decomposition | Metadata direct; Astra repository and method excerpts |
| Xiong et al. (ACL 2026) | Error propagation from stored experience | ACL page and BibTeX direct; Sol sections 3.1–3.4 |
| MafiaScope v3 | Saved-state branching and repeated probes | Metadata direct; Astra and Sol read v3 |
| Oota et al. | Declared versus executed plan structure | Metadata direct; prior Opus project page |
| Turpin; Lanham | Explanation faithfulness | Retained bibliography from the integrated package |
| AgentMonopoly v2 | Negative-cash elimination; no debt rescue | Metadata direct; prior Opus HTML and code read; peers |
| Vending-Bench; Vending-Bench 2; Epoch review | Repeated runs; calculated reference; audit findings | Metadata direct (v1); prior Opus page summaries; peers |
| AutoVend v2 | Rule-based reference policy | Metadata direct; prior Opus HTML methods; peers |
| Li et al. (Arena communication) | Complete-population coding with cross-family judges | Metadata direct; prior Opus HTML methods; peers |
| Lewis 2017; He 2018; NegotiationArena | Negotiation evaluation | Abstracts (integrated package; Sol) |
| Jehiel, Moldovanu and Stacchetti 1996 | Identity-dependent externalities | Sol read the opening of the author-hosted article; prior use |

Sources mentioned in the feedback but not cited (TravelPlanner, Cattle Trade, DECE, Robotouille, LexiCon, Planning in the Dark, PokerBench, MemTrial and the anchoring paper) are left out because none of them changes a claim in this draft. This is not a claim that they are irrelevant. No novelty claim rests on the absence of prior work.
