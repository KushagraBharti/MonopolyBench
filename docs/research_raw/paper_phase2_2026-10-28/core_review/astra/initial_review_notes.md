# Astra: initial adjudication notes

This file records my own judgments before reading the new Sol, Opus or Fable verdicts. Earlier phase-1 and extraction research was already visible; this is not a blinded study. Reading a shortlist is separate from checking its original evidence. The complete review remains in progress.

## First original checks: liquidation ceilings

I read all final shortlist entries for games 19 and 20, including their qualifications and accounting summaries. A conflict between the public and full-channel extractions deserved an immediate original-source check.

`check_final_liquidations.py` rebuilds each recorded prefix and asserts canonical event equality, then exhausts legal financing in memory. It checks three house-only estates; each reaches the arithmetic ceiling through legal actions and then becomes bankrupt without paying the debt. It does not alter canonical artifacts, make provider calls, or estimate a different winner. Results are in `final_liquidations.json`; all assertions and Ruff pass.

- **Game 19 d322:** $242 cash + $50 house salvage + $220 pink mortgages = **$512**, against $1,100. Selling Virginia's last house unlocks the three pink mortgages. The public candidate G19-C020's $292 ceiling and “no mortgage is left” wording are wrong. The recorded private note itself correctly names $512. The bankruptcy remains unavoidable under these legal financing options.
- **Game 20 d354:** $130 cash + $150 house salvage + $60 brown mortgages = **$340**, against $1,275. The public candidate G20-C024's $280 ceiling is wrong for the same reason. The recorded private note correctly names $340. Again, correcting the number does not change the insolvency classification.
- **Game 20 d310:** $225 cash + $70 St. Charles + $80 Virginia + $175 Park Place mortgages = **$550**, against $600. The public statement of a $50 shortfall is correct. Indiana and Illinois are mortgaged in the actual prompt; the alleged state inconsistency was a compact-record reading mistake, previously checked in `../../astra/public_handoff_audit.md`.

These are useful negative cases for voluntary surrender or kingmaking. They also show why a current liquidation menu is not a ceiling on future legal financing within the same debt episode. The legal-action sequence matters. Conversely, an arithmetic upper bound can overstate accessible money when hotel downgrade or other constraints apply; the present checks deliberately assert that these estates contain no hotels.

Inherited houses are not newly constructed houses. A lack of a construction event during creditor transfer is not evidence of a missing construction event. Whether the ownership-transfer schema conveys inherited buildings adequately is a separate artifact question.

## Initial challenges for debate

1. **Paper unit:** our source entries overlap, and several combine multiple mechanisms. They must map to episodes and claim-level evidence; neither 614 entries nor 441 public candidates is a behavioral incidence count.
2. **Meaning of a local threshold:** a three-house rent exceeding the debtor's actual resources, when two-house rent would not, establishes a local threshold comparison on the observed landing. It does not establish that a different earlier build policy would preserve that landing, portfolio or winner. This affects game 20's New York and States examples.
3. **Liquidation is not necessarily avoidable failure:** a sound inability-to-pay calculation can coexist with a poor earlier investment or unlucky landing. Those are different claims with different evidence.
4. **Speech errors:** “Paying in full” during a multi-step liquidation can announce an action in progress. If the agent finishes paying, treating the earlier phrase as a lie manufactures a finding from tense ambiguity. Similarly, a new price after “final offer” is ordinary bargaining unless a separate assurance and its terms are established.
5. **Capability evidence:** a correct stated calculation is a useful observed calculation, not proof of an unobserved cognitive mechanism. It remains stronger evidence than the extractor's mistaken arithmetic, but the applied and available-state channels must still anchor the finding.

No claim here requires new games. A causal winner or intent claim would require more than these checks.
