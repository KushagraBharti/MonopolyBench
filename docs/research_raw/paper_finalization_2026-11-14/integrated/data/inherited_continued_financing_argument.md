# Continued financing in the historical payable states

This is an argument from the frozen source and recorded entry holdings. No policy, engine transition, replay, search, or model evaluation was run. Checking the premises consists of arithmetic on saved states. The three historical payment witnesses used to designate payable declarations remain inherited.

All four reviewers independently supported the argument for the sixteen necessary-collateral entries. Fable subsequently extended sufficient conditions to 129 of 131 payable entries. Astra checked those conditions and supplies the final two-state extension below. That extension has not received another coauthor review and must not be described as four-author confirmation or an executed 131/131 baseline.

## Claim and assumptions

For each of the 131 historically demonstrated-payable debt entry states, every uninterrupted continuation consisting of valid, strictly cash-raising mortgage or building-sale actions pays the **current obligation**, provided the player does not choose bankruptcy.

This does not cover invalid actions, zero-length or zero-proceeds plans, call/time limits, provider failure, an external interruption, a different obligation later in the payment queue, or state changes by another actor. It is not a claim that an arbitrary language-model agent succeeds merely by avoiding the bankruptcy tool. It does not measure liquidation cost or strategic value.

The frozen source supplies the following premises:

- `_resolve_pending_payment` pays automatically once cash covers the current amount; otherwise it requests another decision unless no financing option exists.
- An initially available mortgage remains available until used. Financing cannot add development or reverse a mortgage.
- In a completely owned, evenly developed group without hotels, a highest house is sellable while any houses remain.
- A hotel downgrade consumes four bank houses. A house sale returns houses to the bank. The sale validator permits bundles when the final stock and evenness constraints are satisfied.

Relevant source: [payment resolution](/Users/kushagra/CS-Projects/MonopolyBench/python/packages/engine/src/monopoly_engine/engine.py:2386), [mortgages](/Users/kushagra/CS-Projects/MonopolyBench/python/packages/engine/src/monopoly_engine/engine.py:2492), [sale menus](/Users/kushagra/CS-Projects/MonopolyBench/python/packages/engine/src/monopoly_engine/engine.py:2552), [sale validation](/Users/kushagra/CS-Projects/MonopolyBench/python/packages/engine/src/monopoly_engine/engine.py:2814). The source at the collection commits was already checked against the current files in the independent reviews.

Before paying, Q = cash + remaining building salvage + remaining unmortgaged principal is invariant under valid financing. An integer measure—the remaining building levels (hotel = five) plus the number of unmortgaged deeds—strictly decreases under each strictly cash-raising action. Thus a continuing sequence is finite. If it cannot become stuck with inaccessible assets, it must pay: exhausting every resource unpaid would leave cash equal to initial Q, which is at least the debt.

## Coverage of the recorded entries

The entry checks establish complete ownership and evenness for every developed group, and Q at least the debt, in all 131 entries. The following sufficient conditions are applied in order, giving disjoint counts:

| Condition | Entries | Reason |
|---|---:|---|
| No hotels | 108 | A house is sellable until each developed group clears; then its mortgages are available. |
| Initial cash plus initially available mortgages suffice | 12 | Those mortgages persist. Exhausting all available actions would already have raised at least the needed amount. |
| Initial bank houses cover every possible hotel downgrade | 9 | Bank stock cannot obstruct even the worst order of hotel downgrades. House sales only improve stock. |
| At most one hotel per group, with recyclable stock as below | 2 | A hotel-free group or bank stock always supplies the next financing action. |

The first three rows reproduce Fable's 129-entry coverage from an independently assembled entry table. The last row contains G3 d456 and G3 d461.

## The two remaining entries

Both have one hotel in light blue and one in dark blue. Each of these groups becomes hotel-free immediately after its single hotel is downgraded. The other developed group is red, containing houses only.

| Entry | Bank houses B | Houses in groups with no hotel H | B + H |
|---|---:|---:|---:|
| G3 d456 | 0 | 8 | 8 |
| G3 d461 | 6 | 2 | 8 |

Consider R = B + H while hotels remain. A house sale in a hotel-free group moves a unit from H to B, preserving R. Mortgaging leaves R unchanged. Downgrading a group's only hotel moves four bank houses into that now hotel-free group; any houses previously locked alongside the hotel also enter H. Therefore R cannot decrease. Bundling further house sales moves those units to B and does not invalidate the argument.

Initially R = 8 in both entries. While a hotel remains, if B is at least four, that hotel's highest building level is eligible for a downgrade. If B is less than four, H must be positive, so a highest house in a hotel-free group is sellable. Consequently neither entry can reach an unpaid no-option state with a hotel remaining. After the last hotel is removed, the hotel-free argument applies. This closes the two entries without enumerating or executing action sequences.

## What follows for the review

The referee's reactive-policy criticism is substantively stronger than our earlier reply that the policy had not been run. The recorded payable population admits a source-based explanation for why continued valid financing suffices. The historical 128 payments therefore do not establish difficult route planning. The three voluntary declarations, their written assessments, and their channel agreement are more informative.

This does **not** prove that every nominally sufficient state is payable, or that every possible hotel state has the property. G7 remains a recorded counterexample to equating nominal capacity with menu-reachable finance. It is not in the 131 payable entries.

Reproduction of premise arithmetic: [check_continuation_premises.py](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_review_2026-11-14/reviews/astra/check_continuation_premises.py). Recorded rows and input hashes: [continuation_premises.json](/Users/kushagra/CS-Projects/MonopolyBench/docs/research_raw/paper_review_2026-11-14/reviews/astra/continuation_premises.json). Neither file executes the financing process.
