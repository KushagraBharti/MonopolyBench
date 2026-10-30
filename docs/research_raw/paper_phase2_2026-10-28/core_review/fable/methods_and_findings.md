# Methods and findings: economic and social adjudication of 20 MonopolyBench research games

Fable (claude-fable-5-1), core_review coauthor, 2026-10-29. Companion files: `case_reviews.jsonl` (614), `negative_control_reviews.jsonl` (240), `game_assessments.md` (20 games), `claims.md`, `debate.md`, `progress.json`.

## 1. What this is

A per-case adjudication of every phase-1 catalog entry and every common-sample decision against the original artifacts, followed by a synthesis of what the twenty games show about how model players win, lose, negotiate and describe what they are doing. It is not a scored benchmark result, not a human-annotated dataset and not a replication. Nothing here was negotiated into agreement: initial verdicts were recorded before peer input, and corrections are logged in place with the original reasoning preserved.

## 2. Methods

**Evidence hierarchy.** events.jsonl (what happened) > actions.jsonl (what was applied) > decisions.jsonl menus (what was legal) > the delivered prompt payload (what the model saw) > the applied private note and public message > provider reasoning summaries > assistant content that was not applied. Model-authored text is a self-report; it can show intent or a belief, never an outcome.

**Benchmark norm.** The system prompt permits deception in public chat and asks for truthful private thoughts. I therefore separate three objects: public falsehoods (permitted, recorded for description), private falsehoods (the misconduct object), and false rule beliefs (neither, but consequential).

**Protocol per catalog entry.** Read the entry; locate every cited decision in the original bundle (menu, each attempt's content, tool call, provider reasoning, applied action, emitted events); recompute every figure (cash, rent, bound, price); check the referent of every quote; record a verdict (supported / qualified / contradicted / historical-superseded) with the checks run, the overstated claims, alternatives and counterexamples. Per sample decision: read the bundle, classify as ordinary, catalog-covered or newly noticed.

**Scripts (reading aids, no classification).** `traj.py` (compact trace), `mv.py` (multi-decision bundle viewer), `liq.py` (upper bound of raisable cash from buildings and mortgages under the building lock), `mismatch_scan.py` (heuristic content/tool disagreement finder), `fb_opus.py` (plan shape of the 61 Opus fallbacks), event-level recounts for eliminations, creditors, trades and bank stock. All run with `python3 -I` on untrusted artifacts.

**Negative cases.** Every game assessment carries an "alternatives and counterexamples" paragraph; the sample serves as the negative control against catalog selection; 219/240 sample decisions were ordinary play.

## 3. Shape of the corpus

6,989 decisions (Sol 1,961; Opus 1,696; Argon 1,669; Grok 1,663). Wins: Sol 8, Argon 7, Opus 3, Grok 2. 60 eliminations (56 declared, 4 automatic). 113 accepted trades. 66 fallbacks (Opus 61, Sol 4, Argon 1). Opus was refused by the provider on 1,605 of 1,696 standard attempts and played action-only on the retry.

## 4. Findings

### 4.1 How games were won
Games were won by the first developed set that opponents had to cross, financed early, and then by inheritance: the creditor was the eventual winner in 54 of 60 eliminations, and bankrupt estates moved whole developed or developable sets to the player already ahead (G18 pinks to Opus, reds and dark blues to Sol; G19 reds, eight deeds and eleven deeds to Argon; G20 nineteen deeds to Argon). The decisive set was usually completed by one trade timed to the board: G19 d54 (Connecticut, hotels the same turn, 2,350 collected from the light blues) and G20 d168-176 (Argon's private names the two opponents heading into green; 2,940 of paid developed rent followed). Two winners traded nothing (G14 Sol, G15 Argon).

### 4.2 Liquidity and insolvency
The upper bound of raisable cash, computed with the building lock, was below the debt in 53 of 56 declared bankruptcies. The three premature declarations (G12 d190, G12 d249, G17 d234) all omitted mortgages that house sales would have unlocked. The same omission appears in catalog bounds (G18 C020, G20 C024) and in models' own arithmetic (G20 d322 Argon's 1,098 for a rival who then raised 1,414). The positive cases are as instructive: G18 d463 (Sol computes 679 including unlocked mortgages and declares correctly), G20 d327-336 (sells everything, pays 1,400, keeps 14).

### 4.3 Building: the validator and the refusal
The engine checks evenness after every plan entry, so a plan written as "count 3 on each" fails even when the end state is even and affordable. Three models repaired this on the corrective attempt in 48 of 53 decisions; Opus repaired it in 0 of 61 because the provider refusal had consumed the corrective attempt. "Repaired" means some build was applied: Sol's G2 d243 check and my G19 reads show the repaired plan often differs from the one asked for (fewer houses that decision, hotels added, a layer deferred), and once (G19 d231) the corrective was malformed and nothing was built. The 61 Opus plans were all affordable and all pass when interleaved (Opus and Astra replays), so the loss is attributable to the response condition, not to the plans.

### 4.4 Negotiation
Price ladders with "final" labels were followed by acceptance (G19 d154-155) and by further movement in both directions (G20 d80-83, d90-92). Standing offers were repeated without price change (G19 C007) and withdrawn when the counterparty collapsed (G18 d421-443, with the summary "accepting the $250 just extends their life briefly"). Public framing of a set-completing deed as worthless ("dead red", "dead singleton") was refused on the merits by counterparties who named the monopoly (G19 d70, G20 d101). Recipients did not adopt proposers' false premises in any case I could find; the closest, G4 d148-152, has the recipient rejecting the premise in its own summary while conceding publicly for positional reasons.

### 4.5 Social conduct
No pact, immunity or kingmaking appears in any of the twenty games. Public appeals against funding a leader (G20 d96) were followed by their author and independently by one other player, while a third kept offering the leader cash. Anti-leader bidding was explicit in private notes (G20 d222: bid to drain the rival's cash). The private-channel misconduct I found is small and specific: a false private rationale for a lateral swap (G15 Grok), a private recording a rejection of an offer that was never sent (G18 d245), and a private that said "do not send it" attached to a proposal that was sent (G19 d135), which is a channel limit rather than deceit.

### 4.6 Channel integrity
Three harness-side issues shape what the models saw or what the record says they said: the trade-timeline reversal (44 of 113 accepted trades rendered with giver and receiver swapped), a liquidation prompt that reports one creditor of a pay-each-player card (G19 d263), and an unsanitised public message carrying a private note (G20 d1). One model-side issue shapes what was applied: Grok's assistant content and tool call disagree often enough that ownership changed hands on the tool side against the content side (G18 d83, G19 d135, G20 d6) and once left the model at $7 after it wrote that $7 would be fatal (G20 d98).

### 4.7 Rule beliefs
Four instances of the jail-doubles bonus-roll belief, two of transfer fee or interest on bankruptcy, one fabricated restriction (G6 C021) against two genuine locks (G7 d338, G15 d215), and a "must liquidate before declaring" belief (G19 d224). These are consequential when they drive liquidation order or jail choices, and they are the same across models.

## 5. Negative cases and counterexamples (selected)
G1 d426 Sol: feasible build declined, correctly computed (Sol's check). G18 d463 Sol: full bound computed and bankruptcy correct. G19 d313 / G20 d327-336: survival by full liquidation. G19 c-06: stated house-supply denial with no restriction ever binding. G20 d71: a "DM me" invitation that led nowhere; the "unseen $400" was a split, not a channel. G20 d129/d156: the player accused of organising a boycott was offered cash by another player twice. Twelve catalog entries contradicted on the originals, five of them quotes read against the wrong referent.

## 6. Errors I made and corrected
Three early "Terra concordance" verdicts reversed by Sol's event checks (G3 C017, G3 C021, G4 C005). A viewer bug hid every provider's reasoning field; my claim that Gemini had none was wrong (Sol). G2 d129 summarised from the last attempt only (Opus). G13 extractor errors confirmed only after Astra pointed to them. G19 c-09 counted file lines as decisions (77, not 154). One peer message mislogged as Opus's when it was Astra's relay of Sol's check. All are preserved in `debate.md` and the amended entries carry `amended: true`.

## 7. Unresolved items and dissent
No open dissent on verdicts. Open methodological items: whether "recovered" tables should report quantity-preserving repairs separately (Sol, Astra and I say yes; count not yet done); whether development-return totals should be windowed after the first own build (Astra's 92,550 vs 93,000); a full denominator for Grok's content/tool splits; corpus-wide incidence of the multi-creditor liquidation prompt.

## 8. What would strengthen or overturn
A non-refusing Opus condition would test whether the 61 fallbacks and the action-only play explain Opus's 3 wins; a fixed trade formatter would test whether the G12/G14 confusions recur; a coded pass over every false public claim would turn 4.5's case list into rates. None of these is run in this stage.
