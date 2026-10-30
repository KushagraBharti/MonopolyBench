# Negotiation extension adversarial review

## Recommendation and scope

Keep the mechanical census and the completion-by-response table. I independently reproduce every reported headline count and all 920 offer-accounting rows from the original delivered menus, applied actions and events. No mechanical error was found in the tested population. The semantic counts need revision or explicit disagreement reporting before they become substantive prevalence claims. The current source does acknowledge their provisional status.

This review writes only in its own folder. It uses no new games, model calls, engine branches or edits to canonical artifacts. The review does not establish optimal trade values, causal persuasion, stable preferences or human annotation accuracy.

The semantic pass is not fully blinded. An initial schema inspection accidentally exposed the original aggregate counts and first row's codes, plus a fragment of the second row. I recorded this in `coding_protocol.json`, then read all 74 complete applied public messages and private-note fields from `masked_rows.json`, with labels and evidence spans removed. I saved `own_74_row_ledger.json` before comparing labels. All 920 exported public/private fields were subsequently checked against the original applied actions, with zero mismatches. Neither coding pass used provider reasoning summaries for this population.

## Mechanical checks that passed

`independent_census.py` is a separate implementation driven primarily by original decision menus. It does not import the extension reducer. I read that reducer before implementing the check, so this is an independent implementation with known reconciliation targets, not a blinded replication. It checks event authors separately against delivered `current_offer.from_player_id`, rather than using the thread initiator to assign bundle direction.

| Quantity | Independently reproduced |
|---|---:|
| Canonical events / initial decisions | 50,918 / 6,989 |
| Threads / response opportunities / acceptance-legal offers | 526 / 920 / 918 |
| All accepted / countered / rejected responses | 113 / 394 / 413 |
| Legal recipient-completing offers | 221 |
| Their accept / counter / reject partition | 34 / 113 / 74 |
| Legal offers completing both parties | 81 |
| Their accept / counter / reject partition | 10 / 35 / 36 |
| Recipient-completing offers breaking a prior recipient group | 6 |
| Such offers directly rejected | 1 |
| Threads with counters / settlements after counters | 138 / 81 |
| Settlements whose final author differs from initiator | 44 |
| Threads following an earlier thread for the same game/pair | 414 |
| Maximum counters / maximum elapsed global turns | 11 / 0 |
| Response retries / engine defaults | 168 / 0 |
| Opus action-only responses | 162 |

Every completion-table cell and every per-model initiation/response count in `methods_results.tex` matches the second implementation. All 920 computed cash balances, mortgage-transfer fees, new/lost complete groups, resulting holdings, author identities, response actions and acceptance-menu indicators match the extension's rows. For all 113 acceptances, immediate original event deltas and the next original prompt agree with predicted cash, deed ownership, mortgage/development attributes and jail-card transfers. Five deliberate mutations to completion, balance, author, acceptance availability and response are detected by the reviewer's comparator.

The longest exchange is G9, events 1015 through 1069, global turn 59, with eleven counters. It starts with Opus and settles on the other party's authored terms. The zero elapsed-turn result is correct. It should not be interpreted as zero elapsed decisions or evidence of long-horizon relationship learning.

### The two unavailable-acceptance cases

These are offers received without a legal acceptance option, not two illegal acceptances.

* **G4 d219:** the recipient has $156 and is asked to pay $150 for mortgaged Vermont and Connecticut. Transfer interest is $5 + $6. The immediate balance would be $156 - $150 - $11 = -$5. The original menu contains only reject and counter. The applied response rejects and says it needs the cash for yellow development and a buffer. Excluding it prevents an unavailable action from being coded as a rejected feasible opportunity.
* **G12 d228:** the recipient has $50 and is asked to pay $50 for mortgaged Connecticut. Its $6 transfer charge makes the balance -$6. The menu again offers only reject and counter. The applied response counters at $25. The public $66 redemption statement concerns a different charge and does not make acceptance of the current offer legal.

The two role errors also check against original holdings. At G15 d106, Grok is buyer p2 with $903 and Mediterranean, not a seller holding Baltic and $8. At G17 d186, Grok is buyer p4 with $545 and Connecticut, not the seller of Oriental and Vermont. Reason text in these rows must remain flagged as role-inconsistent.

### Typed transfers

The original events reproduce 107 trade-cash flows totaling $28,425; 207 traded deeds; 905 paid-rent events totaling $121,154; 59 nonzero estate-cash debits totaling $11,830; and 397 inherited-deed events. Winner receipts reproduce $78,737 paid rent and 372 inherited deeds. Before the last elimination, winners receive 202 of 227 inherited deeds and $7,148 of $7,843 estate cash. The 170 final inherited deeds are a separate terminal partition. Repeated transfer of one deed remains a repeated event, not a distinct title.

The distinction between paid rent and estate cash is preserved. The nonterminal partition is useful, but still conditions recipient identity on the eventual winner. It does not estimate an effect of inheritance on winning.

## Semantic results and disagreements

The two passes agree on all six labels in only 31 of 74 rows. This is chiefly a code-boundary problem. My broad reading of retained assets includes repeated blocking and portfolio-priority statements that the original pass often leaves untagged. My own larger totals are not proposed as corrected ground truth.

| Code | Original positives | Review positives | Both positive | Either positive | Disputed rows |
|---|---:|---:|---:|---:|---:|
| D, rival consequence | 63 | 63 | 61 | 65 | 4 |
| C, own price/liquidity | 42 | 48 | 41 | 49 | 8 |
| R, own holdings/portfolio | 21 | 50 | 19 | 52 | 33 |
| T, timing/reconsideration | 13 | 20 | 13 | 20 | 7 |
| F, contradictory buyer/seller role | 2 | 2 | 2 | 2 | 0 |
| N, no applicable explicit reason | 2 | 3 | 2 | 3 | 1 |

All 43 row disagreements, full text, the original exact spans, and my explanations are preserved in `disagreements.json`. The union and intersection are agreement diagnostics, not confidence intervals or an adjudicated gold standard. Channel availability agrees at 74 public fields and 66 nonempty private notes.

### Four D disagreements, with exact channels

1. **G3 d506, original D, review no D.** The applied private note says it has "no reason to give p2 $400 cash" and then says "Rejecting the trade so I can build hotels and unmortgage my own monopolies on my turn." It names the cash recipient but does not specify a development or survival consequence for that recipient. The explicit stated reason is the buyer's own investment priority. A narrower rival-consequence code should exclude it.
2. **G13 d303, original D, review no D.** The entire available public field is "No thanks. I'm not handing over the dark blues plus $800 for three mortgaged properties." The private field is empty. Rival completion is true mechanically, but this text does not explicitly evaluate the rival's resulting position. The price and surrendered portfolio are stated; a rival-development motive would be inferred. A narrower D should exclude it.
3. **G15 d106, review D, original no D.** The private note explicitly says "$120 is only $60 over cost and leaves Grok able to build immediately." It also discusses a denial buyer. That meets a broad text-only rival-development definition, but the speaker has adopted the wrong seller role. A coherent-rival-assessment count should exclude this row and keep the raw text/F flag separately. It must not be silently deleted from a descriptive text-presence ledger.
4. **G15 d108, review D, original no D.** The private note says "p3 still can't house dark blue on $158" and "Browns don't threaten p4 and p1/p3 likely die elsewhere before hitting them." These are opponent-state and survival forecasts, but the stated consideration is low prospective income from the offered brown set. A narrower question about enabling a rival through the exchange should exclude it. This row demonstrates why general opponent modeling and rival-funding denial need separate labels.

The remaining 61 common D-positive rows form a conservative common set for the narrower trade-linked rival-consequence question. Their agreement does not establish that their factual calculations are correct or that those considerations caused rejection.

### Recommended stricter D codebook

Use a stated trade-consequence code with four recorded components: the named rival, the offered change, the claimed future consequence, and the source span. Include a row only when the text explicitly connects the exchange to a rival's group completion, development, activation, survival, delay of bankruptcy or changed creditor inheritance. An explicit denial statement such as "Keeping Vermont Avenue ensures p4 has zero monopolies" qualifies. Merely naming transferred cash, declining a bundle, listing rival wealth or forecasting who might land on the buyer's new property does not. Keep general opponent forecasts in a separate descriptive code. Keep role contradictions as an independent flag; report them separately from coherent assessments. Do not use later events to turn a prior terse refusal into an inferred motive.

For C/R/T, specify whether relative barter value counts as price, whether retaining a blocking deed counts as portfolio retention, whether generic future planning is part of the rejection reason, and whether a standing price available "later" qualifies as timing. Give paired positive/negative examples before another coding pass. In particular, G20 d278 says only "New York stays with me. Orange isn't for sale." It is R under an inclusive retention definition and N under a definition excluding bare retention refusals. Neither choice can be resolved by arithmetic or by calling one reviewer correct.

## Manuscript findings and precise fixes

**N1, medium, lines 84-100.** Replace the single-pass semantic totals, or print the two-pass disagreement table in the supplement. The current warning is honest but a main-text list of 63/42/21/13 invites later reuse as settled prevalence. Suggested prose:

> We read both applied fields for all 74 rejections and retained separate model-assisted judgments. Both passes identify explicit rival-consequence considerations in 61 records; four further records receive that label in only one pass. Broader price, retention and timing counts depend more strongly on category boundaries and are reported with disagreements in the annotation supplement. These are stated considerations, not verified calculations or causal explanations. All 74 records have public text and 66 have a private note. Two notes adopt the wrong buyer/seller role.

If using 61 in this form, retain the common-positive list and state that it is agreement between two non-blind model-assisted passes. It is not a newly validated 61/74 human prevalence estimate.

**N2, low, lines 43-51 and 75-82.** Make the action level visible before readers infer choice or rationality. Replace "34 are accepted, 113 are countered and 74 are rejected" with "the applied responses comprise 34 acceptances, 113 counters and 74 rejections." Then use: "Thus own-set completion alone does not predict immediate acceptance in these configured systems." The later caveat that a valid call can disagree with content is correct and should remain. The original sufficient-condition claim is mechanically true; this edit clarifies its psychological limits.

**N3, low, lines 146-153.** Add: "Removing the final estate avoids the forced last-player transfer, but the nonterminal statistic still classifies recipients by an eventual outcome." The existing no-causation sentence is sound. Do not call this winner-adjusted evidence or a measure of the skill of extracting inheritance.

**N4, low, lines 30-38.** Retain the exact repeated-pair definition. A fresh proposal after a terminal rejection is a new engine thread, even in the same global turn. The 414 figure counts threads with any earlier same-game/pair thread, not 414 independent repeated relationships, and not 414 retries. No correction to the number is needed.

**N5, passed interpretation checks.** Lines 109-132 correctly distinguish counter-associated settlement from a causal effect of countering. Completing both parties' sets does not imply fairness or positive joint surplus. Lines 155-163 correctly refuse to label network concentration as collusion. Rejected own completion is not evidence of irrationality, and the explicit caveats preserve that boundary. The extension answers descriptive components of the strategic, negotiation and collective-dynamics questions. It does not complete causal negotiation effectiveness or economic optimality.

## Verification limits

This review independently recomputed the 920 mechanical offer rows, original applied text, 113 accepted transitions, thread statistics, model counts and typed-flow aggregates. It counted all 6,989 decisions but did not independently reconstruct every nontrade state or every concentration time-series value. The original author's all-6,989 state-reconstruction claim remains a separately executed producer check. I did not rerun the author's eight-mutation validator because its main routine writes in the shared source folder; five different comparator mutations were performed in this review's folder. No source rendering or full-paper build was required for this bounded data review. I did not reread all provider reasoning, re-query any model, execute an engine branch or assess an optimal continuation policy. I did not audit external literature in this local evidence check.
