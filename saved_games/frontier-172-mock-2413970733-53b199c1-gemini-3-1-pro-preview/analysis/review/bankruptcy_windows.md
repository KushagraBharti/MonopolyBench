# Bankruptcy and Elimination Windows

Run: `mock-2413970733-53b199c1`. This review uses canonical events/actions/decisions and declares an immediate bankruptcy avoidable only when the legal menu plus one-step accounting demonstrate a unilateral survival path. A voluntary rescue trade is never treated as available merely because one can imagine it.

## Reconciliation

| Elimination | Turn | Liquidation decision(s) | Creditor | Debt | Realized status | Window semantics |
| --- | ---: | --- | --- | ---: | --- | --- |
| Claude Opus 4.8 | 156 | `mock-2413970733-53b199c1-dec-000582` | Gemini | $550 | deterministic fallback declared bankruptcy | five decisions before `mock-2413970733-53b199c1-dec-000577`–`mock-2413970733-53b199c1-dec-000581`; five after `mock-2413970733-53b199c1-dec-000583`–`mock-2413970733-53b199c1-dec-000587`; eliminated seat means no turn 157 decision |
| OpenAI GPT 5.5 | 163 | `mock-2413970733-53b199c1-dec-000602` | Gemini | $1,100 | model declared bankruptcy | five before `mock-2413970733-53b199c1-dec-000597`–`mock-2413970733-53b199c1-dec-000601`; five after `mock-2413970733-53b199c1-dec-000603`–`mock-2413970733-53b199c1-dec-000607` |
| Grok 4.3 | 171 | `mock-2413970733-53b199c1-dec-000611`–`mock-2413970733-53b199c1-dec-000612` | Gemini | $1,050 | sold both hotels, then declared bankruptcy | five before `mock-2413970733-53b199c1-dec-000607`–`mock-2413970733-53b199c1-dec-000611`; no five-after window exists because `mock-2413970733-53b199c1-dec-000612` is the last decision and `GAME_ENDED` is seq 4072 at synthetic turn index 172 |

There is no dedicated `BANKRUPTCY` event type in this trace. Bankruptcy is represented by a liquidation action, `CASH_CHANGED` rows with `BANKRUPTCY_CASH`/`BANKRUPTCY`, zero-price property acquisitions by the creditor, and turn/game termination. The authoritative elimination evidence is therefore the action plus those emitted events.

## Claude Opus 4.8 — turn 156 fallback-induced avoidable immediate bankruptcy

### Causal buildup

Claude converted its late portfolio into a four-house red monopoly. At the start of turn 156 it had $363 and Kentucky, Indiana, and Illinois with four houses each; it owned no other deeds. That concentration generated a strong rent engine but left its legal liquidity entirely in buildings. The immediately preceding five decisions (`mock-2413970733-53b199c1-dec-000577`–`mock-2413970733-53b199c1-dec-000581`) were GPT’s turn-155 clearance-sale attempts and responses, not Claude actions; the larger causal context is Claude’s earlier sale of mortgaged blockers to GPT for development liquidity and subsequent red build-up.

### Shock and legal menu

Claude rolled 4+2 from Go to Oriental at seq 3818–3819 and owed Gemini $550 hotel rent. Decision `mock-2413970733-53b199c1-dec-000582` exposed:

- cash $363, shortfall $187;
- `sell_houses_or_hotel` and `declare_bankruptcy`;
- sellable buildings on all three red properties;
- no mortgageable property because every deed supported buildings.

The model made two malformed attempts. Both omitted the required `public_message`; the strict retry also failed. The deterministic fallback applied `declare_bankruptcy` (`fallback_reason=malformed_after_retry`). Events seq 3824–3829 transferred $363 and all three red deeds to Gemini.

### Avoidability classification

**`avoidable_unilateral` for the immediate $550 obligation, high confidence.** The engine explicitly offered building sale. Houses on the red group cost $150 and sell for $75 under the rules surface; selling one house from each four-house property respects even-building and raises $225. That exceeds the $187 shortfall, so a demonstrated legal unilateral path could have paid the current rent. This is Tier-0 one-step accounting, not a speculative trade rescue or continuation oracle.

The classification is deliberately narrow. It proves survival of this payment, not eventual victory, long-run survival, or that selling three houses was globally optimal. It also distinguishes the mechanism: the bankruptcy was not a duplicate resume action and not an unavoidable dice shock; it was the deterministic consequence of a structured-output failure after one corrective retry.

### Five decisions after

Decisions `mock-2413970733-53b199c1-dec-000583`–`mock-2413970733-53b199c1-dec-000587` show the game continuing with Claude absent: Grok ended with $15 rather than liquidate its engine; GPT sold Short Line to Gemini for $50 and tried to sell a jail card; Gemini consolidated the rail blocker. Claude had no further actions because elimination removes its seat.

## OpenAI GPT 5.5 — turn 163 forced bankruptcy after complete asset liquidation

### Causal buildup and five-before window

By `mock-2413970733-53b199c1-dec-000597`–`mock-2413970733-53b199c1-dec-000601`, GPT had already sold every deed and was liquidating its last jail card. It paid $200 railroad rent to Grok on turn 162, then sold the card to Gemini for $1 (`trade-0133`, seq 3953–3958) and ended with $117 and no assets. Earlier sales—especially Boardwalk, Ventnor, and Short Line to Gemini—provided temporary cash while concentrating board control in Gemini. Those realized transfers are facts; whether retaining any one asset would have improved GPT’s survival requires a branch oracle and is not asserted.

### Shock and legal menu

At turn 163 GPT landed on Gemini’s Illinois hotel and owed $1,100. Decision `mock-2413970733-53b199c1-dec-000602` showed a $983 shortfall, no mortgageable assets, no sellable buildings, and only `declare_bankruptcy` as legal. GPT selected it validly on the first attempt. Seq 3973–3975 transferred the remaining $117 to Gemini and eliminated GPT.

### Avoidability classification

**`unavoidable_under_evaluated_action_set` at the liquidation decision, high confidence.** There was no unilateral action other than bankruptcy. A hypothetical rescue trade is not counted: GPT had nothing left to transfer and no evidence that an opponent would donate $983. The causal buildup includes voluntary liquidation and high-frequency trading, but no supported counterfactual proves a prior legal choice would have prevented this realized landing.

### Five decisions after

Decisions `mock-2413970733-53b199c1-dec-000603`–`mock-2413970733-53b199c1-dec-000607` cover the two-player transition. Gemini retained liquidity and existing lethal hotels; Grok preserved its brown/rail engine; after Grok paid another $550 light-blue hotel rent, Gemini used `mock-2413970733-53b199c1-dec-000607` to add two houses to each orange, deliberately increasing the next-board-segment hazard.

## Grok 4.3 — turn 171 terminal unavoidable bankruptcy

### Causal buildup and five-before window

The five-decision lead-in (`mock-2413970733-53b199c1-dec-000607`–`mock-2413970733-53b199c1-dec-000611`) starts with Gemini’s six-house orange build on turn 168, followed by end turns from both finalists. Grok entered turn 171 with $315, brown hotels, and three unmortgaged railroads. It landed on Gemini’s Kentucky hotel and owed $1,050.

### Liquidation sequence

At `mock-2413970733-53b199c1-dec-000611`, legal actions included mortgaging Reading/Pennsylvania/B. & O., selling the two brown hotels, or declaring bankruptcy. Grok first sold both hotels. Events seq 4056–4058 raised only $50 total and converted the hotels to four houses on each brown property; `run/state/turn_0171_decision_0002.json` confirms $365 and eight brown houses.

At `mock-2413970733-53b199c1-dec-000612`, $685 remained due. The same three railroads and eight houses remained legally liquidatable, but the maximum one-step proceeds were $300 from the three $100 railroad mortgages plus $200 from eight $25 house sales, only $500. That is below the $685 shortfall. Grok declared bankruptcy validly; seq 4063–4070 transferred cash and five deeds to Gemini, and seq 4072 ended the game.

### Avoidability classification

**`unavoidable_under_evaluated_action_set`, high confidence.** Unlike Claude’s window, exhaustive immediate unilateral liquidation could not cover the debt. Negotiated rescue is also not a plausible realized route in a two-player game where the sole counterparty is the creditor, but the label does not depend on that inference.

### No after-window

The requested five-after window is structurally censored. `mock-2413970733-53b199c1-dec-000612` is canonical decision 613/613. `GAME_ENDED` uses turn index 172 although playable turns are indexed 0–171; reports therefore call this a 172-turn game while the terminal marker sits at the next synthetic index.

## Cross-window mechanism findings

- Gemini directly received all three bankruptcy payments and asset transfers. This is realized creditor concentration, not proof that any prior deal “caused” the final result.
- The three collapse mechanisms differ: structured-output fallback despite a legal sale path (Claude), no remaining liquidation assets (GPT), and insufficient maximum legal liquidation value (Grok).
- Only Claude’s immediate bankruptcy is labeled avoidable, and only at the demonstrated one-payment horizon.
- The decisive reliability anomaly is unusually consequential: `mock-2413970733-53b199c1-dec-000582` turned two missing-public-message errors into elimination. GPT and Grok’s terminal decisions were first-pass valid.
- Archived pre-resume recovery evidence has no role in any bankruptcy classification; all three windows occur in canonical post-resume evidence.
