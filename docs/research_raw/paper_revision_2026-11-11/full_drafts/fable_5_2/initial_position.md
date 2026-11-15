# Fable 5.2: initial position

11 November 2026. Written before any new tabulation for this revision and before reading any other author's revision draft. It records what I believe going in, which claims I intend to test, and what would change my mind. Results are in `findings_and_limits.md`.

## What I had read when I wrote this

- `revision_contract.md`, in full.
- Both critique attachments (the 53-page-version critique and the 33-page-version critique).
- `user_review.md` and `assessment.md`, plus all four core assessments (`astra.md`, `sol.md`, `opus.md`, and my own earlier `fable_5_2.md`).
- Every source file of the previous integrated manuscript, its evidence map and its integration decisions.
- The transcription of the eight research questions and A to C.

I had not yet opened any ledger or raw game file for this revision, and I had not read `full_drafts/astra/` or `full_drafts/sol/`.

## Where I think the last paper went wrong

The last paper organised twenty games as a pipeline: bargain, build, collect rent, inherit. The pipeline is how Monopoly works. Three of its abstract numbers (rent share of early-built groups, winners' share of estates, debts above the asset bound) describe the game more than the players. Both outside reviewers said this, and I agree.

The paper also buried its most behavioural material. The offers, counters, refusals and stated reasons are what the agents chose. The rent and estate totals are what the rules then did with those choices.

## The claim I expect to defend

My working thesis has two halves.

1. **Attention.** These agents treat a deed as a claim on somebody's future monopoly. They name the rival's gain when they refuse, when they set a price, and when they decide whether to keep a failing opponent alive. This shows up in populations (refusals of one's own completion, asks to completing buyers) and in the incidents.
2. **Effectiveness.** That attention does not become a stable price or a reliable plan. Same-deed asks are mixed. Counters reprice completing and ordinary bundles alike. The stated arithmetic is sometimes wrong. I suspect the thing that moves a blocking deed is the seller's cash, more than any valuation of the buyer's gain.

So the candidate headline is: *strategic attention is pervasive; strategic pricing is inconsistent; liquidity decides when blockers move.* The third clause is a hypothesis. I have not tested it on the full offer population, only seen it among settled deals, where it is confounded with Opus's response condition.

## Alternatives I will examine before committing

| Candidate central claim | What would support it | What would sink it |
|---|---|---|
| A seller premium for completing buyers | Higher asks within seller, deed, mortgage status and stage | Mixed same-deed comparisons; effect carried by one seller or by stage |
| Liquidity releases blockers | Acceptance and ask levels move with seller cash across all offers, in more than one configuration | Pattern confined to Opus under action-only recovery, or to settled deals only |
| Refusing one's own completion to deny a rival | Recipient-only refusals with stated rival consequences across configurations and games | Concentration in two games; no difference from ordinary refusals |
| Development gap as a planning finding | Timing and exposure show similar opportunities but different building | Gap explained by mortgages at acquisition, late completion, or response handling |
| First estate decides games | First creditor not already ahead before the estate | First creditor already leads on cash, development and rent |
| Debt handling as competence | Most payable debts paid across all debt episodes | Many payable debts ending in bankruptcy |

I will report whichever of these the records support, including null or mixed results. I have no stake in a positive effect.

## Comparisons I plan to run on existing records

1. Asking and bidding prices by seller, deed, mortgage status and stage, with every same-seller same-deed pair listed.
2. Responses by recipient, stage and completion category in one joint table, and the same table by the responder's cash.
3. For every trade-completed group: completion turn, first build, ownership end, opponent landings and rent, so that receipts can be read against exposure.
4. Every debt episode from first debt menu to payment or bankruptcy, so that the three payable eliminations get a denominator.
5. Each game's position just before its first estate: cash, deeds, buildings and rent so far, for the creditor and the other players.

Uncertainty will be stated at the level of games and seed blocks. I will not attach offer-level significance tests to dependent offers.

## Conditions I will check at the source

- The exact stored standard prompt and recovery prompt, diffed, with the tool schemas. My earlier assessment said the recovery prompt keeps the permission to deceive and drops only the private-thought request. I will re-read the files before repeating that.
- The refusal message, its counts and its time course.
- Which cost and token fields mean what.

## Positions I hold going in

- Opus did not refuse to deceive. I expect the stored prompts to confirm it. I will not write "no memory" or "no reasoning" for any system.
- Authorised bluffing is conduct under the task's rules. I will not call it misalignment.
- A stated reason is a recorded explanation. I will not treat it as the cause of the action or as a readout of internal computation.
- No decision in this corpus can be scored as strategically good or bad. Arithmetic, legality and current-debt feasibility can be checked. I will keep those levels apart.
- Twenty games in five seed blocks and one cyclic seating order cannot rank four systems.
- The eight incidents stay if each one carries an inference the tables cannot. I will drop or swap an incident that does not.

## Objections to the contract, recorded before the work

1. **The word target and the eight incidents pull against each other.** Eight incidents with context, outcome and interpretation cost roughly 2,000 to 2,500 words of prose outside the quotations. That leaves about 4,500 for everything else. I will try to meet both and say where I could not.
2. **"Prioritise fundamentals over bookkeeping" can tempt overreach.** The records support claims about what agents said and did. They do not support claims about general cognition. I will keep the headline behavioural and concrete.
3. **Existing-record comparisons cannot replace a controlled contrast.** A within-seller, within-deed table is sharper than a pooled median. It is still seven pairs. I will present such tables as descriptions and say so once.

## What would change my mind

- If the liquidity pattern vanishes outside Opus, I drop the third clause and lead with attention against pricing.
- If the same-deed pairs and the stage cuts both favour a premium once I have listed them all, I will say the seller premium is better supported than I now think.
- If first creditors turn out not to be prior leaders, the estate result earns more prominence than I currently plan to give it.
