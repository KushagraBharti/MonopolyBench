# Figures and tables for the draft

Open the [gallery](figure_gallery.html) to inspect the nine shared figures together. Each has PNG, PDF and SVG exports under `astra/exhibits/`; [captions](astra/exhibit_captions.md) define its unit, evidence and limits. Numeric tables have CSV and JSON versions. The [manifest](astra/exhibits/manifest.json) ties the exports to source hashes and the plotting script.

## Shared figure set

| Figure | Question answered | Data and manuscript use |
|---|---|---|
| [F1: evidence chain](astra/exhibits/f01_evidence_chain.png) | What evidence connects capability, conduct and a norm? | Conceptual diagram, explicitly not an alignment score. Introduction/methods. |
| [F2: block × rotation outcomes](astra/exhibits/f02_seed_rotation_winners.png) | How do the 20 results vary across seeds and seats? | [T1](astra/exhibits/t01_cohort.csv); descriptive design overview. One-based seats. |
| [F3: negotiation profiles](astra/exhibits/f03_negotiation_profiles.png) | How often does an agent initiate, and how often does it repeat proposals that turn? | [T2](astra/exhibits/t02_negotiation.csv); propensity and intensity, with counts and alternate denominator. |
| [F4: opportunity and development](astra/exhibits/f04_opportunity_and_deployment.png) | Which traded sets were developed, and what records accompany the non-builds? | [T3](astra/exhibits/t03_trade_groups.csv), [T4](astra/exhibits/t04_bilateral_completion.csv), [T9](astra/exhibits/t09_entry_nonbuild_records.csv); whole-path and conditional counts. |
| [F5: spending and paid receipts](astra/exhibits/f05_spending_and_receipts.png) | How do receipts differ across spending units and inheritance histories? | [T5](astra/exhibits/t05_spending_units.csv); 103 units, winner/other panels, inherited deeds and creditor outcomes. Not ROI. |
| [F6: accessible finance at elimination](astra/exhibits/f06_elimination_financing.png) | Could the current debt be paid through legal own actions? | [T6](astra/exhibits/t06_eliminations.csv); all 60 eliminations, including automatic ones and the hotel lock. |
| [F7: building recovery](astra/exhibits/f07_build_recovery.png) | Does a successful retry preserve the proposed purchases? | [T7](astra/exhibits/t07_build_recovery.csv); selected uneven-build rejections, preserved/changed/default outcomes. Can become a compact main-text table. |
| [F8: social chronologies](astra/exhibits/f08_social_chronology.png) | What do omission, exposure, correction and settlement establish? | Three original-checked contrasts with channel provenance. Selected cases, not prevalence. |
| [F9: complete cash paths](astra/exhibits/f09_cash_trajectories.png) | What do two trade-free wins and one traded/inherited route look like? | [T8](astra/exhibits/t08_cash_trajectories.csv); canonical cash changes and reconciled winner endpoints. Cash, not wealth. |

## Coauthored exhibits to retain

- [Sol's G19 successive-owner figure](sol/exhibits/s3_g19_dark_blue.png) connects the same group's ownership, expenditure and receipts. It is the preferred concrete economic timeline in the main text.
- [Sol's spending-window comparison](sol/exhibits/s2_spending_windows.png) explains why whole-game receipts differ from post-own-expenditure receipts. The [Sol manifest](sol/exhibits/manifest.json) includes the all-103-unit cross-check.
- [Sol's alternative outcome grid](sol/exhibits/s1_seed_rotation.png) and [Opus's grid](opus/exhibits/outcome_grid.svg) remain alternatives, not additional independent datasets.
- [Fable's house-stock grid](fable/exhibits/house_stock_grid.png), [series](fable/exhibits/house_stock_series.csv) and [report](fable/exhibits/house_stock_report.json) reconstruct bank inventory at all 6,989 delivered states. Hotel conversions return houses and produce upward steps. Zero stock is not a count of denied demand.
- [Fable's all-63 first-management table](fable/exhibits/first_management_causes.csv) distinguishes built, never legal, defaults, received conflicts and valid ENDs. Sol's [follow-up check](sol/peer_followup_checks.json) recounts the derived rows with attribution.
- [Normative contracts](opus/exhibits/normative_contracts.md), [implemented/measured/proposed affordances](opus/exhibits/affordance_ledger.md) and [cost/usage](opus/exhibits/cost_usage.csv) support methods and discussion. Known cost has missing refusal accounting; token semantics differ by provider.

## Draft selection

The venue-neutral draft should give economics and social conduct substantial space. Use F1/F2 for interpretation and design, F3/F4 for negotiation/deployment, F5 plus the G19 timeline for receipts and inheritance, F6 for finance, and F8 for social contrasts. F7 can be a table beside deployment. F9, stock trajectories and the alternative plots can move to an appendix without losing their evidence.

Do not remove the condition/default annotations merely to simplify a plot. Do not replace all-player trajectories with winner-only anecdotes. Final numbering and layout will be chosen during the manuscript stage, after the prose and exhibits are placed together.
