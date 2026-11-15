# Opus cross-review: initial position

11 November 2026. Written after reading all four frozen complete papers (Astra, Sol, Opus, Fable 5.2), including main text, appendices, generated tables and `\fact{}` values, the main figures, handoffs, initial positions and findings/limits notes. Hash check before reading: all 235 files in `four_draft_hashes.json` match (`data/hash_check_before.json`).

Not yet opened when this was written: root's provisional review in `reviews/astra/` and any other review. I will not read `reviews/fable_5_2/` at all (concurrent peer review). I am Claude Opus 5.5, the same identifier as one evaluated configuration, and the author of one of the four drafts. I am trying not to defend that draft.

## What the four papers claim

| Draft | Central claim | Strongest new evidence | Main weakness |
|---|---|---|---|
| Astra | Strategic attention plus executed local financial reasoning | 188/128/60 liquidation census; 61 multi-action payments; stage-split rejection contrast | Payment success is a scaffolded, low-bar task, so it carries less about strategy than the framing suggests; attention rests mainly on inherited codes and incidents |
| Sol | Bargaining over competitors' future options (construction funds, resale, inheritance); attention is distinct from effectiveness | Resale-network reading of G2; seller/mortgage/stage price cells (11 of 12); prior-rent lead before first estate (15/20) | A carefully hedged descriptive account with no sharp behavioral regularity at its centre; "attention" is soft |
| Opus (mine) | Defensive bargaining over the deed that completes a rival's group; attention is categorical, not graded | Opening rejection 74% vs 64% (author-only vs neither), positive in every block and every standard recipient; concessions accepted 9/58 vs 24/86 | The "neither" baseline mixes offers that do and do not request a deed from the recipient. The "categorical" claim rests on one capacity cut whose smallest cell (6/11) goes the other way. "Opus is not defensive" judges a counter-heavy responder by its rejection rate. |
| Fable | Agents withhold a rival's monopoly until they need the cash; what the cash becomes separates trajectories | Holder-cash split (25% vs 69% rejection); 13/14 within-pair cash declines; strong stated-rule transcripts (G2 d128, G18 d420, G15 d176, G7 d141/d142); 128/131 payable debts paid; G17 payable bankruptcy | The cash split is composition-dependent: Opus rejects almost nothing at any cash level, Gemini rejects 10/11 even under $100, and the within-system pattern is carried by Sol and Grok. The post-sale build/win split (9/14 vs 1/29) is conditioned on already holding a buildable group and on the eventual outcome. The title's "until" generalises past the evidence. |

## My provisional central claim

Across the four papers, the strongest supported discovery joins my draft's defensive pattern with Fable's liquidity evidence and Sol's rival-option reading:

> These LLM agents bargain over the last deed of a rival's colour group as a strategic veto, and the veto has a price in liquidity. Liquid holders mostly refuse or reprice requests that would complete a rival's group. Release is concentrated among cash-constrained holders, or among holders who can turn the proceeds into their own construction. Both sides reason explicitly about the holder's cash and about what the money or the deed would let each player build.

This framing gives more weight to observed choices than to recorded explanations. It covers both kinds of evidence: what the agents say (inherited codes, transcripts with stated release rules) and what they do (population contrasts, within-pair sequences). It also makes the system heterogeneity part of the result instead of a footnote. Gemini holds its veto even when cash-poor. Opus counters instead of refusing and sells cheaply under distress, under a recovery condition we cannot separate from the model. Sol and Grok refuse when liquid and release when not.

It is a claim about attention and the state-dependence of behaviour. It is not a claim about effectiveness, optimal pricing or a causal liquidity effect.

## What I expect to demote or correct

1. **My own "categorical, not graded" claim.** The response is graded in the holder's own cash, even if it is flat in the rival's post-trade building cash. I need to check the rival-capacity cut jointly with holder cash before keeping any version of it. The correct talk-versus-action point may be narrower: agents cite the rival's building cash, but their responses track their own liquidity more clearly than the quantity they cite.
2. **My own "Opus exception" wording.** Opus counters 75% of offers it receives. Its rejection rate is the wrong measure of whether it defends. Its asks do rise for completing buyers (2.00 vs 1.50 unmortgaged). The record supports "Opus does not show the rejection contrast and is the main source of low-price distress sales", not "Opus is not defensive."
3. **Fable's title and abstract.** "Until they need the cash" holds for two of four systems at the offer level. The within-pair evidence has 14 rows, and only about half of those holders are under $100 at the sale. The seller build/win contrast should not appear in an abstract as a trajectory-separating result. Building after a sale requires already owning a buildable group, and several sales by one eventual winner are not independent. A version restricted to sellers who held a buildable group at the sale might survive. I will check whether the records allow that.
4. **Astra's finance framing.** The 128 payments are real positive execution evidence, but the liquidation menu supplies the amount owed, the shortfall and the legal options. Payment is a scaffolded endpoint. Its more informative content is (a) how many payments preserve buildings when mortgages suffice, and (b) the specific error shared by the two standard-condition payable eliminations: their notes omit mortgages that selling buildings would unlock (Fable's reading, to verify). That is a precise multi-step planning failure and deserves more attention than the success count.
5. **Same-deed asks.** The 4/2/1 versus 5/1/1 difference comes from a single row. In G4, Opus asks a completing buyer $450 first, more than the $280 it asks another buyer, and then lowers its asks to $100–175 as its cash falls. The median estimand calls this row lower and the first-ask estimand calls it higher. Both reversals under the median estimand are Opus selling Boardwalk while its cash ran down. The integrated paper should print all seven rows with both estimands and identify no premium.

## Checks I will run (existing-record arithmetic only)

- Opening rejection contrast with the comparison restricted to offers that request at least one deed from the recipient.
- Holder-cash contrast within recipient system and stage, and its interaction with completion (completion requests versus other deed requests) within system.
- Holder cash jointly with the rival's post-trade building capacity.
- Seller build/win split restricted to sellers who held a buildable complete group at the sale, counted by player-game.
- Within-pair sequences: holder cash under $100 at the sale; comparison with unsettled pairs.
- Paid debt episodes: any engine default or Grok content/call conflict among the paying actions.
- Who receives low-cash completion requests, with and without Opus.

No new games, engine runs, replays, synthetic tests, model calls or prompt edits. All outputs stay under `reviews/opus/`.

## Positions I hold going in

- Eight incidents should stay. Fable's G1 (a distress sale at a quarter of list) and its re-centred G7 (a liquidity-timed bid and a construction-financing sale) carry the release mechanism better than G19. I would keep G19 as a short control or the eighth slot, not drop it silently, because it is the clearest case of a recipient separating the terms from the explanation.
- The prompt and provider condition belongs once in the setup, with the exact diff in an appendix. All four drafts now agree on the substance.
- The rent and estate totals, and the first-creditor-wins count, are context. The informative estate result is the five discordant games, especially G17, where a payable bankruptcy handed a developed estate to the poorest player, who then won.
- No draft supports a model ranking, a causal effect of liquidity, or a seller premium.
