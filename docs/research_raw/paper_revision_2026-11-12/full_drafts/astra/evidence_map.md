# Evidence and verification scope

This paper describes the historical twenty-game cohort. No new games, engine execution, replay execution, synthetic cases, baseline runs, counterfactual rollouts or provider queries were performed.

| Claim or artifact | Evidence | Work in this round |
|---|---|---|
| All 920 response opportunities; 918 legal acceptances | Copied `data/offers.json` and the independently reconstructed ledgers retained in the 11 November versions | Re-tabulated. Legal subset is 113 acceptances, 393 counters, 412 rejections. The two excluded opportunities are one counter and one rejection. |
| Complete form/completion table; opening and later populations | `tools/analyze.py`, `data/revision_analysis.json` | Direct arithmetic over all retained offer rows, including empty cells. |
| Proposer composition, conflicting-opening exclusions | `tools/check_offer_forms.py`, `tools/analyze.py`; saved original decisions | Reproduced the counts and the selected source-channel conflict screen. The full 139-conflict census remains an inherited classification. |
| Block resampling and omission ranges | `tools/analyze.py` | Enumerated all 3,125 ordered samples of five intact seed blocks. Empirical stability descriptions, not selection-adjusted confidence intervals. |
| 188 financing episodes, 128 paid, 60 eliminated | `data/liquidation_episodes.json`, previous event-fold and prompt reconciliation | Retained episode census; the complete episode detector was not independently rebuilt in this round. |
| Sixteen necessary-collateral debts and their initial statements | `tools/check_finance.py`, `data/necessary_collateral.json`, original initial decisions | Recomputed cash, salvage and initially available mortgage bounds, preserved original fields and hashes, read all sixteen initial statements. Thirteen successes state the resource or a budget incorporating it; one is tentative. This is LLM-assisted reading. |
| 62/53/16 resource partition; 62/52/14 paid | `tools/analyze.py`, episode ledger and initial records | Direct arithmetic. Membership among demonstrated-payable debts uses actual historical payments and three earlier engine-validated witnesses. |
| Three payable declarations; G7 menu restriction | Earlier executable audit and retained reports | Inherited engine-executed results. No witness or search was rerun. The bound by itself is not treated as a proof of legal reachability. |
| G20 payment target, two sales, eight mortgages, remainder | Original action/event records checked by `tools/check_offer_forms.py` and quotation manifests | Rechecked saved sequence and amounts. No replay. |
| 61/74 reasons | Two earlier row-level LLM codings and previous reconciliation | Inherited semantic judgments; their disjoint population is stated. No human annotation or new independent validation claimed. |
| Eight incidents and eighteen displayed cards | Four quotation macro/manifest files; original decisions; retained delivery checks | Every selected quotation is re-read at its original source span and hash, then searched in rendered PDF text. New quote extraction was unnecessary. Receipt statements rely on retained prompt checks and the stored source-linked checks, not on public-message fields alone. |
| First-window development, rents, inheritance | Prior group, exposure and event ledgers copied under `data/` | Supporting historical context, not newly executed or causal findings. All route and terminal/nonterminal qualifications preserved. |
| Prompt and response conditions | Stored G1 prompt pair, frozen source commits, retained refusal accounting | Read both prompts and source tool-choice configuration. Exact counts/timing rely on the prior original-record checks. The repeated refusal message does not expose a structured refusal category. |
| Two historical replay comparisons | Saved replay reports | Read report structure and retained aggregate checks. Both comparisons passed historically; no replay executed now. |
| Model identifiers and corpus map | Historical configs, `data/game_map.json`, cohort table | Retained canonical identification. No new provider-model capability test. |
| Source protection and rendered manuscript | `tools/verify_document.py`, `qa/verification.json` | 738 protected entries checked, eighteen selected quotations checked, seventeen PDF pages rendered. Zero diagnostic warnings in the final build. |

The four assistants are language models. Their agreement is not human validation, and Sol/Opus research assistants overlap evaluated model families or identifiers. The paper does not use their review count as a scientific sample size.
